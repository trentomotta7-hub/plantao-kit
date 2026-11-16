#!/usr/bin/env python3
"""Prova V5: trecho 31.10–37.74s em estilo fotográfico e sincronizado por palavra."""
from pathlib import Path
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = Path(__file__).resolve().parent
V32 = HERE.parent / "revisao_v3_cortes_visuais"
FRAMES = HERE / "work" / "frames"
OUTDIR = HERE / "out"
OUT = OUTDIR / "proof_moraes_sync_6s.mp4"
FRAMES.mkdir(parents=True, exist_ok=True); OUTDIR.mkdir(parents=True, exist_ok=True)
os.environ["PLANTAO_WORK"] = str(V32 / "work")
os.environ["PLANTAO_OUT"] = str(V32 / "work" / "frames_out")
os.environ["PLANTAO_BEATS"] = str(V32 / "beats.json")
os.environ["PLANTAO_EDICAO"] = "3"
os.environ["PLANTAO_NOME"] = "MAPA SUJO"
os.environ["PLANTAO_DATA"] = "DOMINGO, 15 DE NOVEMBRO DE 2026"
os.environ["PLANTAO_TICKER"] = "CASO BANCO MASTER  •  MENSAGEM ATRIBUÍDA  •  RELATÓRIO EM REVISÃO  •  "
sys.path.insert(0, str(V32))
import engine_ritmo as E  # noqa: E402
import conteudo_ed003 as BASE  # noqa: E402

W, H, FPS = 1080, 1920, 30
START = 31.10
END = 37.74
DURATION = END - START
beats = json.loads((V32 / "beats.json").read_text())
words = beats["words"][4]
SPEECH_START = float(beats["starts"][4])
VOICE_OFFSET = SPEECH_START - START

def word_start(term):
    for item in words:
        token = item["w"].strip(".,!?\"'“”").lower()
        if token == term.lower():
            return float(item["t"])
    raise ValueError(f"Palavra {term!r} não encontrada na transcrição")

# Os tempos das palavras são relativos ao início da fala (beats.starts), não ao corte.
# Cada gatilho entra 0,10s antes da palavra, preservando o lead visual do projeto.
def visual_trigger(term):
    return VOICE_OFFSET + word_start(term) - 0.10

T_INTERESSE = visual_trigger("interesse")
T_NAO = visual_trigger("não")
T_MORAES = visual_trigger("Moraes")
T_ANTECIPOU = visual_trigger("antecipou")
T_COMBINOU = visual_trigger("combinou")
T_VORCARO = visual_trigger("Vorcaro")

NAVY = (10, 20, 32)
INK = (16, 22, 28)
WHITE = (245, 242, 233)
RED = (202, 42, 43)
YELLOW = (246, 194, 55)


def clamp(x): return max(0.0, min(1.0, x))
def smooth(x):
    x = clamp(x)
    return x*x*(3-2*x)
def lerp(a,b,p): return a+(b-a)*p

def cover(im, size, cx=0.5, cy=0.42):
    tw, th = size
    s=max(tw/im.width,th/im.height)
    im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS)
    left=round((im.width-tw)*cx); top=round((im.height-th)*cy)
    left=max(0,min(im.width-tw,left)); top=max(0,min(im.height-th,top))
    return im.crop((left,top,left+tw,top+th)).convert("RGBA")

def make_plate(text, size, bg, fg, width=880, padding=(28,20), font="Oswald.ttf", weight=800):
    txt=E.TB(text if isinstance(text,list) else [text],size,fg,font,weight,maxw=width)
    pad_x,pad_y=padding
    layer=Image.new("RGBA",(txt.width+pad_x*2,txt.height+pad_y*2),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    d.rounded_rectangle((0,0,layer.width-1,layer.height-1),radius=9,fill=bg)
    layer.alpha_composite(txt,(pad_x,pad_y))
    return layer

def place(canvas, layer, x, y, scale=1.0, angle=0.0, opacity=1.0):
    w=max(1,int(layer.width*scale)); h=max(1,int(layer.height*scale))
    im=layer.resize((w,h),Image.Resampling.LANCZOS)
    if abs(angle)>0.05: im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    if opacity<0.999:
        im.putalpha(im.getchannel("A").point(lambda a:int(a*clamp(opacity))))
    canvas.alpha_composite(im,(int(x-im.width/2),int(y-im.height/2)))

def photo_panel(im, label, credit, size, crop=(0.5,0.42)):
    pic=cover(im,size,*crop)
    panel=Image.new("RGBA",(size[0]+12,size[1]+115),(0,0,0,0))
    d=ImageDraw.Draw(panel)
    d.rounded_rectangle((0,0,panel.width-1,panel.height-1),radius=16,fill=(244,242,235,255))
    panel.alpha_composite(pic,(6,6))
    d=ImageDraw.Draw(panel)
    d.rounded_rectangle((6,size[1]-68,panel.width-6,size[1]+6),radius=6,fill=(12,20,29,245))
    f=E.C.fnt("Oswald.ttf",34,700)
    tw=d.textlength(label,font=f)
    d.text(((panel.width-tw)/2,size[1]-59),label,font=f,fill=(255,255,255,255))
    cf=E.C.fnt("Oswald.ttf",19,500)
    d.text((18,size[1]+34),credit,font=cf,fill=(35,40,45,255))
    return panel

# Brand assets are restrained: masthead, red/yellow accent and ticker, not a paper-craft layout.
MORAES_IMG=Image.open(BASE.MORAES).convert("RGB")
DANIEL_IMG=Image.open(BASE.DANIEL).convert("RGB")
MORAES_PANEL=photo_panel(MORAES_IMG,"ALEXANDRE DE MORAES","Victor Piemonte/STF · domínio público",(880,1100),(0.5,0.40))
DANIEL_PANEL=photo_panel(DANIEL_IMG,"DANIEL VORCARO","Arquivo · Claudio Gatti/Divulgação",(960,610),(0.5,0.38))
TITLE_CONTEXT=make_plate(["INTERESSE", "ECONÔMICO"],78,YELLOW,INK,840,(34,25),"Anton.ttf",800)
TITLE_NOT_PROOF=make_plate("NÃO PROVA",48,RED,WHITE,480,(26,18),"Anton.ttf",800)
TITLE_QUESTION=make_plate(["ANTECIPOU O VOTO?"],49,(245,242,233,247),INK,850,(24,18),"Anton.ttf",800)
TITLE_COMBO=make_plate(["OU COMBINOU ALGO?"],45,(245,242,233,247),INK,850,(24,18),"Anton.ttf",800)
SOURCE=make_plate("UOL · reportagem de 13/11/2026",20,(245,242,233,230),INK,530,(12,8),"Oswald.ttf",500)


def render(t):
    # t é relativo ao início da fala deste beat; zero corresponde a 31,10s do episódio.
    bg=Image.new("RGBA",(W,H),NAVY+(255,))
    # Planos de cor limpos e discretos, não ilustram fatos nem criam evidência.
    d=ImageDraw.Draw(bg)
    d.rectangle((0,0,W,214),fill=(8,15,24,255))
    d.rectangle((0,208,W,214),fill=RED+(255,))
    # Gradiente fotográfico controlado e textura mínima.
    for y in range(174,H-90):
        a=int(16*(y/(H-90)))
        d.line((0,y,W,y),fill=(NAVY[0]+a,NAVY[1]+a,NAVY[2]+a,255))
    mast=E.C.fnt("Playfair.ttf",124,900)
    mast_w=d.textlength("MAPA SUJO",font=mast)
    d.text(((W-mast_w)/2,14),"MAPA SUJO",font=mast,fill=WHITE+(255,))
    small=E.C.fnt("Oswald.ttf",24,600)
    small_text="EDIÇÃO 003  ·  CONTEXTO E INFERÊNCIA"
    small_w=d.textlength(small_text,font=small)
    d.text(((W-small_w)/2,172),small_text,font=small,fill=(185,195,202,255))

    # Antes do nome, mostrar somente a ideia falada: nenhum rosto de Moraes antecipado.
    pre_alpha=1-smooth((t-(T_MORAES-0.12))/0.14)
    cap=make_plate("ESSE CONTEXTO",54,(245,242,233,235),INK,760,(24,16),"Oswald.ttf",700)
    place(bg,cap,540,480,1,0,pre_alpha)
    if t>=T_INTERESSE:
        p=smooth((t-T_INTERESSE)/0.22)
        place(bg,TITLE_CONTEXT,540,790,lerp(.88,1,p),lerp(1.8,0,p),p*pre_alpha)
    if t>=T_NAO:
        p=smooth((t-T_NAO)/0.18)
        place(bg,TITLE_NOT_PROOF,540,1100,lerp(.82,1,p),lerp(-3,0,p),p*pre_alpha)

    # Moraes entra 0,10s antes do nome, não no começo do beat.
    if t>=T_MORAES:
        p=smooth((t-T_MORAES)/0.20)
        photo_exit=smooth((t-T_VORCARO)/0.18)
        x=lerp(1240,540,p)
        y=lerp(1240,995,p)
        scale=lerp(.74,1.0,p)*(1+.012*smooth((t-T_MORAES)/2.0))*(1-.24*photo_exit)
        place(bg,MORAES_PANEL,x,y,scale,lerp(2.5,0,p),p*(1-photo_exit))
        if t>=T_ANTECIPOU:
            trigger=T_COMBINOU if t>=T_COMBINOU else T_ANTECIPOU
            question=TITLE_COMBO if t>=T_COMBINOU else TITLE_QUESTION
            qp=smooth((t-trigger)/0.16)
            place(bg,question,540,1640,lerp(.88,1,qp),0,qp)

    # Vorcaro só surge no próprio nome. Não há linha/efeito que una os retratos.
    if t>=T_VORCARO:
        p=smooth((t-T_VORCARO)/0.20)
        x=lerp(1320,540,p)
        y=lerp(1120,1035,p)+3*math.sin(t*2.2)
        place(bg,DANIEL_PANEL,x,y,lerp(.82,1,p),lerp(-2,0,p),p)
        np=smooth((t-T_VORCARO-0.35)/0.18)
        if np>0:
            caution=make_plate("PERGUNTA · NÃO COMPROVADO",28,RED,WHITE,610,(17,10),"Oswald.ttf",700)
            place(bg,caution,540,1510,1,0,np)

    # Créditos/fontes fixos, sem encobrir imagem ou ticker.
    place(bg,SOURCE,540,1740,1,0,1)
    tick=E.C.ticker_strip(YELLOW)
    x=-int((START+t)*235%tick.width)
    bg.alpha_composite(tick,(x,H-tick.height))
    bg.alpha_composite(tick,(x+tick.width,H-tick.height))
    return bg.convert("RGB")


def main():
    for f in FRAMES.glob("f_*.jpg"): f.unlink()
    nframes=math.ceil(DURATION*FPS)
    for n in range(nframes):
        t=min(DURATION-1/FPS,n/FPS)
        render(t).save(FRAMES/f"f_{n:04d}.jpg",quality=92,subsampling=0)
    audio=V32/"mix_ln.wav"
    subprocess.run([
        "ffmpeg","-y","-hide_banner","-loglevel","warning",
        "-framerate",str(FPS),"-i",str(FRAMES/"f_%04d.jpg"),
        "-ss",str(START),"-t",str(DURATION),"-i",str(audio),
        "-map","0:v:0","-map","1:a:0","-vf","hqdn3d=1:1:4:4",
        "-c:v","libx264","-preset","slow","-crf","24","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(OUT)
    ],check=True)
    print(f"Prova: {OUT}\nEntrada Moraes: {START+T_MORAES:.2f}s; palavra Moraes: {SPEECH_START+word_start('Moraes'):.2f}s")
    print(f"Entrada Vorcaro: {START+T_VORCARO:.2f}s; palavra Vorcaro: {SPEECH_START+word_start('Vorcaro'):.2f}s")

if __name__=="__main__": main()
