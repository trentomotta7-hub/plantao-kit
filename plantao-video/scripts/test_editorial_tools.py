import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = load("check_hook", "check_hook.py")
brief = load("validate_brief", "validate_brief.py")
metrics = load("analyze_metrics", "analyze_metrics.py")


class EditorialToolsTests(unittest.TestCase):
    def test_hook_empty_fails(self):
        self.assertEqual(hook.inspect([""])[0][0], "FAIL")

    def test_hook_timing_threshold(self):
        beats = {"starts": [0.1], "words": [[{"t": 0.25}]]}
        self.assertTrue(any(level == "FAIL" for level, _ in hook.inspect(["A manchete"], beats)))

    def test_brief_missing_topic_fails(self):
        errors, _ = brief.validate({})
        self.assertTrue(any("topic" in e for e in errors))

    def test_claim_references_must_exist(self):
        data = {
            "topic": "Pauta", "duration_preset": "standard", "target_duration_seconds": 65,
            "selected_hook_id": "h1",
            "hooks": [{"id": f"h{i}", "spoken": "fala", "on_screen": "texto", "first_frame": "quadro", "claim_id": "c1"} for i in range(1, 4)],
            "source_records": [{"id": "s1", "publisher": "Jornal", "title": "Matéria", "published_at": "2026-01-01", "url": "https://example.com/fonte"}],
            "claim_ledger": [{"id": "c1", "text": "Fato", "classification": "confirmed", "source_ids": ["missing"]}],
        }
        errors, _ = brief.validate(data)
        self.assertTrue(any("inexistente" in e for e in errors))

    def test_metrics_zero_views_does_not_divide(self):
        row = {"duration_seconds": "60", "views": "0", "avg_watch_seconds": "30", "completed_views": "0", "shares": "0"}
        normalized, _ = metrics.analyze([row])
        self.assertIsNone(normalized[0]["completion_pct"])
        self.assertIsNone(normalized[0]["shares_per_1k"])
        self.assertEqual(normalized[0]["avg_watch_pct"], 50)


if __name__ == "__main__":
    unittest.main()
