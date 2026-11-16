# Diagnóstico visual — por que a V3.1 ainda parecia parada

A reclamação estava correta. A revisão anterior reforçou a trilha e o zoom, mas manteve essencialmente uma composição por beat. Os dez beats duram cerca de 6–9 segundos; em quatro blocos de mapa, o desenho era composto uma vez e permanecia congelado. Nas páginas, cada objeto entrava e ficava no quadro até o corte seguinte. O resultado era uma montagem de slides e uma alternância previsível entre página e mapa.

A causa técnica é estrutural: `L(..., pop, ...)` só controla a entrada e não a saída das camadas; os `MAP_BLOCKS` anteriores devolviam uma única composição por bloco. O movimento de câmera contínuo não criava novos acontecimentos visuais. Aumentar música, zoom ou flash não resolveria isso.

## Meta desta revisão

A V3.2 mantém a voz, o roteiro, os beats, a mixagem e os elementos de marca, mas troca a composição durante a própria fala: 41 estados visuais em dez beats, ancorados a palavras pronunciadas, em média cerca de 1,9 s por estado. O mapa passa a ser um recorte ilustrativo pontual dentro de uma página, em vez de uma tela recorrente em sequência. As demais cenas variam entre retratos impressos, manchetes, citações, desenhos editoriais, papéis rasgados, carimbos e diagramas que evoluem.

O renderer é local a esta pasta; não altera `engine.py`, `engine_ritmo.py` de outras edições, o vídeo original, a V3 ou a V3.1. A densidade exata ainda precisa ser avaliada em reprodução contínua, não apenas em quadros estáticos.
