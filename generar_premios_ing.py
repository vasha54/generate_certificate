#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de certificados de MEDALLAS (Oro/Plata/Bronce) — Inglés (A4 vertical).
Variante B: sin trofeo de marca de agua; medalla circular centrada sobre el nombre.
Marca de agua: bloques ABC, bocadillo con "Hello!", signos de interrogación
y exclamación, comillas inglesas " ", letras "Aa" gigantes y textura de
alfabeto con puntuación (? ! . , ; : ' ").

CSV esperado:
    nombre,centro,grado,medalla
    Ana Pérez,IPVCE "Carlos Marx",10,oro
    Juan Gómez,IPVCE "Carlos Marx",11,plata
    Luis Díaz,IPVCE "Carlos Marx",12,bronce
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = A4  # 595.27 x 841.89 pt (vertical)

NAVY = HexColor("#1F3A5F")
GOLD = HexColor("#B08D3C")
INK = HexColor("#2B2B2B")
MUTED = HexColor("#6B6B6B")

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

CLAVES_NOMBRE   = {"nombre", "nombres", "nombre completo", "name", "estudiante", "participante"}
CLAVES_APELLIDO = {"apellido", "apellidos"}
CLAVES_CENTRO   = {"centro", "escuela", "institucion", "centro de estudio",
                   "centro de estudios", "school"}
CLAVES_GRADO    = {"grado", "grade", "nivel", "año", "ano", "curso"}
CLAVES_MEDALLA  = {"medalla", "medal", "premio", "distincion", "distinción"}

# Colores por medalla
MEDALLA_COLORES = {
    "oro":    {"base": HexColor("#8B6914"), "cuerpo": HexColor("#D4AF37"), "brillo": HexColor("#F5E6A8")},
    "plata":  {"base": HexColor("#606060"), "cuerpo": HexColor("#A8A8A8"), "brillo": HexColor("#E8E8E8")},
    "bronce": {"base": HexColor("#6B3A1A"), "cuerpo": HexColor("#B87333"), "brillo": HexColor("#E0A878")},
}
MEDALLA_NOMBRE = {"oro": "ORO", "plata": "PLATA", "bronce": "BRONCE"}

GRADOS_NOMBRE = {
    "10": "décimo", "decimo": "décimo", "décimo": "décimo", "diez": "décimo",
    "11": "onceno", "onceno": "onceno", "once": "onceno", "undecimo": "onceno", "undécimo": "onceno",
    "12": "duodécimo", "duodecimo": "duodécimo", "duodécimo": "duodécimo", "doce": "duodécimo",
}
GRADO_A_NUM = {
    "décimo": "10", "decimo": "10", "10": "10",
    "onceno": "11", "once": "11", "undecimo": "11", "undécimo": "11", "11": "11",
    "duodécimo": "12", "duodecimo": "12", "doce": "12", "12": "12",
}


# --------------------------------------------------------------------------
# Fuentes
# --------------------------------------------------------------------------
def registrar_fuentes() -> dict[str, str]:
    aqui = Path(__file__).resolve().parent
    carpetas = [
        aqui / "fuentes",
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/dejavu"),
        Path("C:/Windows/Fonts"),
        Path.home() / "Library/Fonts",
    ]
    archivos = {
        "Serif": "DejaVuSerif.ttf",
        "Serif-Bold": "DejaVuSerif-Bold.ttf",
        "Serif-Italic": "DejaVuSerif-Italic.ttf",
        "Sans": "DejaVuSans.ttf",
        "Sans-Bold": "DejaVuSans-Bold.ttf",
    }
    for carpeta in carpetas:
        if all((carpeta / f).exists() for f in archivos.values()):
            for n, f in archivos.items():
                pdfmetrics.registerFont(TTFont(n, str(carpeta / f)))
            return {k: k for k in archivos}
    print("Aviso: no se encontró DejaVu; se usan fuentes estándar (Times/Helvetica).",
          file=sys.stderr)
    return {
        "Serif": "Times-Roman", "Serif-Bold": "Times-Bold",
        "Serif-Italic": "Times-Italic", "Sans": "Helvetica", "Sans-Bold": "Helvetica-Bold",
    }


# --------------------------------------------------------------------------
# Lectura del CSV
# --------------------------------------------------------------------------
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def _limpiar(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def normalizar_grado(v: str) -> str:
    return GRADOS_NOMBRE.get(_norm(v), _limpiar(v))


def normalizar_medalla(v: str) -> str:
    n = _norm(v)
    mapa = {
        "oro": "oro", "gold": "oro", "dorada": "oro", "dorado": "oro",
        "1": "oro", "primero": "oro", "primer lugar": "oro",
        "plata": "plata", "silver": "plata", "plateada": "plata", "plateado": "plata",
        "2": "plata", "segundo": "plata", "segundo lugar": "plata",
        "bronce": "bronce", "bronze": "bronce",
        "3": "bronce", "tercero": "bronce", "tercer lugar": "bronce",
    }
    return mapa.get(n, n)


def leer_csv(ruta: Path) -> list[tuple[str, str, str, str]]:
    crudo = ruta.read_bytes()
    texto = None
    for enc in ("utf-8-sig", "cp1252"):
        try:
            texto = crudo.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if texto is None:
        sys.exit("No se pudo leer el CSV (codificación desconocida).")

    try:
        dialecto = csv.Sniffer().sniff(texto[:4096], delimiters=",;\t")
    except csv.Error:
        dialecto = csv.excel
    filas = [f for f in csv.reader(texto.splitlines(), dialecto) if any(c.strip() for c in f)]
    if not filas:
        return []

    cabecera = [_norm(h) for h in filas[0]]
    tiene_cabecera = any(h in CLAVES_NOMBRE | CLAVES_APELLIDO for h in cabecera)

    if not tiene_cabecera:
        out = []
        for f in filas:
            nombre = _limpiar(f[0]) if f else ""
            if not nombre:
                continue
            centro = _limpiar(f[1]) if len(f) > 1 else ""
            grado = normalizar_grado(f[2]) if len(f) > 2 else ""
            medalla = normalizar_medalla(f[3]) if len(f) > 3 else "oro"
            out.append((nombre, centro, grado, medalla))
        return out

    def indice(claves):
        return next((i for i, h in enumerate(cabecera) if h in claves), None)

    i_nom, i_ape = indice(CLAVES_NOMBRE), indice(CLAVES_APELLIDO)
    i_cen, i_grado, i_medalla = indice(CLAVES_CENTRO), indice(CLAVES_GRADO), indice(CLAVES_MEDALLA)
    if i_nom is None and i_ape is None:
        sys.exit("El CSV necesita una columna 'nombre' (o 'nombres' + 'apellidos').")

    def celda(f, i):
        return _limpiar(f[i]) if i is not None and i < len(f) else ""

    out = []
    for f in filas[1:]:
        nombre = _limpiar(" ".join(p for p in [celda(f, i_nom), celda(f, i_ape)] if p))
        if not nombre:
            continue
        gr = celda(f, i_grado)
        grado = normalizar_grado(gr) if gr else ""
        mr = celda(f, i_medalla)
        medalla = "oro"
        if mr:
            medalla = normalizar_medalla(mr)
            if medalla not in MEDALLA_COLORES:
                print(f"Aviso: medalla desconocida '{mr}' en '{nombre}'; se usa oro.",
                      file=sys.stderr)
                medalla = "oro"
        out.append((nombre, celda(f, i_cen), grado, medalla))
    return out


# --------------------------------------------------------------------------
# Utilidades de dibujo
# --------------------------------------------------------------------------
def fecha_es(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def formatear_fecha(v: str | None) -> str:
    if not v:
        return fecha_es(date.today())
    try:
        return fecha_es(date.fromisoformat(v))
    except ValueError:
        return v


def slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:60] or "participante"


def grado_numero(g: str) -> str:
    return GRADO_A_NUM.get(_norm(g), slug(g) or "grado")


def centrado(c, texto, y, fuente, tam, color=INK, espacio=0.0, x=None):
    x = W / 2 if x is None else x
    ancho = pdfmetrics.stringWidth(texto, fuente, tam) + espacio * max(len(texto) - 1, 0)
    c.setFillColor(color)
    t = c.beginText(x - ancho / 2, y)
    t.setFont(fuente, tam)
    t.setCharSpace(espacio)
    t.textOut(texto)
    c.drawText(t)


def parrafo(c, texto, y, fuente, tam, color, ancho, inter=1.45):
    for ln in simpleSplit(texto, fuente, tam, ancho):
        centrado(c, ln, y, fuente, tam, color)
        y -= tam * inter
    return y


def rombo(c, x, y, lado=8, color=None):
    color = GOLD if color is None else color
    c.saveState()
    c.translate(x, y)
    c.rotate(45)
    c.setFillColor(color)
    c.rect(-lado / 2, -lado / 2, lado, lado, stroke=0, fill=1)
    c.restoreState()


def marco(c, color_medalla):
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.rect(30, 30, W - 60, H - 60)
    c.setStrokeColor(color_medalla)
    c.setLineWidth(1)
    c.rect(40, 40, W - 80, H - 80)
    for x, y in ((40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)):
        rombo(c, x, y, 9, color_medalla)


def ornamento(c, y, color=None):
    color = GOLD if color is None else color
    c.setStrokeColor(color)
    c.setLineWidth(1)
    c.line(W / 2 - 110, y, W / 2 - 12, y)
    c.line(W / 2 + 12, y, W / 2 + 110, y)
    rombo(c, W / 2, y, 7, color)


def dibujar_logos(c, rutas, y_top, alto_max=62, ancho_max=120):
    n = len(rutas)
    for i, r in enumerate(rutas):
        img = ImageReader(str(r))
        iw, ih = img.getSize()
        esc = min(alto_max / ih, ancho_max / iw)
        w, h = iw * esc, ih * esc
        x = W * (i + 1) / (n + 1)
        c.drawImage(img, x - w / 2, y_top - alto_max / 2 - h / 2, w, h,
                    mask="auto", preserveAspectRatio=True)
    return alto_max


def ajustar_nombre(nombre, fuente, ancho_max, tam_max=32, tam_min=18):
    sw = pdfmetrics.stringWidth
    tam = tam_max
    while tam > tam_min and sw(nombre, fuente, tam) > ancho_max:
        tam -= 1
    if sw(nombre, fuente, tam) <= ancho_max:
        return [nombre], tam

    palabras = nombre.split()
    if len(palabras) < 2:
        return [nombre], tam_min
    mejor = min(
        (max(sw(" ".join(palabras[:i]), fuente, 1), sw(" ".join(palabras[i:]), fuente, 1)),
         " ".join(palabras[:i]), " ".join(palabras[i:]))
        for i in range(1, len(palabras))
    )
    _, a, b = mejor
    tam = 28
    while tam > 14 and max(sw(a, fuente, tam), sw(b, fuente, tam)) > ancho_max:
        tam -= 1
    return [a, b], tam


# --------------------------------------------------------------------------
# Firmas
# --------------------------------------------------------------------------
MAX_FIRMAS = 6
ALTO_IMG_FIRMA = 44


def lista_firmas(cfg):
    if cfg.sin_firmas:
        return []
    return cfg.firmas_parsed or [("", "Comité Organizador", None)]


def distribuir_firmas(n):
    if n <= 3:
        return [n]
    p = (n + 1) // 2
    return [p, n - p]


def geometria_firmas(cfg):
    lista = lista_firmas(cfg)
    if not lista:
        return 0, False
    filas = distribuir_firmas(len(lista))
    y0 = 165 if len(filas) == 1 else 135
    y_sup = y0 + 100 * (len(filas) - 1)
    return y_sup, any(img is not None for _, _, img in lista[:filas[0]])


def firmas(c, cfg, F):
    lista = lista_firmas(cfg)
    if not lista:
        return
    filas = distribuir_firmas(len(lista))
    y0 = 165 if len(filas) == 1 else 135
    i = 0
    for r, k in enumerate(filas):
        y_linea = y0 + 100 * (len(filas) - 1 - r)
        sep = (W - 120) / k
        ancho = min(190, sep - 20)
        for j in range(k):
            nombre, cargo, img = lista[i]
            i += 1
            x = 60 + sep * (j + 0.5)
            if img is not None:
                iw, ih = img.getSize()
                esc = min(ancho / iw, ALTO_IMG_FIRMA / ih)
                c.drawImage(img, x - iw * esc / 2, y_linea + 2, iw * esc, ih * esc, mask="auto")
            c.setStrokeColor(INK)
            c.setLineWidth(0.8)
            c.line(x - ancho / 2, y_linea, x + ancho / 2, y_linea)
            y = y_linea - 15
            if nombre:
                centrado(c, nombre, y, F["Sans-Bold"], 10.5, INK, x=x)
                y -= 14
            for ln in simpleSplit(cargo, F["Serif-Italic"], 9.5, ancho + 20)[:3]:
                centrado(c, ln, y, F["Serif-Italic"], 9.5, MUTED, x=x)
                y -= 12


# --------------------------------------------------------------------------
# Medalla centrada
# --------------------------------------------------------------------------
def dibujar_medalla(c, cx, cy, r, colores):
    """Medalla circular con cintas y estrella, en los colores de la medalla."""
    base, cuerpo, brillo = colores["base"], colores["cuerpo"], colores["brillo"]

    # Cintas detrás del disco
    c.setFillColor(base)
    p = c.beginPath()
    p.moveTo(cx - r * 0.55, cy + r * 0.80)
    p.lineTo(cx - r * 1.00, cy + r * 1.90)
    p.lineTo(cx - r * 0.20, cy + r * 1.90)
    p.lineTo(cx + r * 0.15, cy + r * 0.80)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    p = c.beginPath()
    p.moveTo(cx + r * 0.55, cy + r * 0.80)
    p.lineTo(cx + r * 1.00, cy + r * 1.90)
    p.lineTo(cx + r * 0.20, cy + r * 1.90)
    p.lineTo(cx - r * 0.15, cy + r * 0.80)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    # Aro exterior
    c.setFillColor(base)
    c.circle(cx, cy, r, stroke=0, fill=1)
    # Disco interior
    c.setFillColor(cuerpo)
    c.circle(cx, cy, r * 0.85, stroke=0, fill=1)
    # Brillo
    c.setFillColor(brillo)
    c.circle(cx - r * 0.30, cy + r * 0.35, r * 0.22, stroke=0, fill=1)

    # Estrella de 5 puntas
    c.setFillColor(base)
    p = c.beginPath()
    for i in range(10):
        ang = math.radians(90 + i * 36)
        rad = r * 0.55 if i % 2 == 0 else r * 0.22
        x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


# --------------------------------------------------------------------------
# Marca de agua alegórica a INGLÉS
# --------------------------------------------------------------------------
GRIS_A = HexColor("#DFDFDF")
GRIS_B = HexColor("#E8E8E8")
GRIS_C = HexColor("#EEEEEE")
GRIS_TEXTURA = HexColor("#F0F0F0")
BRILLO = HexColor("#F8F8F8")

POSICIONES_MARCA = {
    1: [(0.50, 0.50, 380)],
    2: [(0.32, 0.64, 250), (0.68, 0.36, 250)],
    3: [(0.30, 0.70, 220), (0.70, 0.50, 220), (0.34, 0.30, 220)],
}


def preparar_marca(ruta, opacidad):
    im = Image.open(ruta).convert("RGBA")
    r, g, b, a = im.split()
    gris = Image.merge("RGB", (r, g, b)).convert("L")
    gris = gris.point(lambda v: int(255 - (255 - v) * opacidad))
    return ImageReader(Image.merge("RGBA", (gris, gris, gris, a)))


def preparar_firma(ruta):
    im = Image.open(ruta)
    tiene_alfa = im.mode in ("RGBA", "LA") or "transparency" in im.info
    rgba = im.convert("RGBA")
    if not tiene_alfa:
        g = rgba.convert("L")
        a = g.point(lambda v: max(0, min(255, int((245 - v) * 255 / 55))))
        rgba.putalpha(a)
    return ImageReader(rgba)


def textura_alfabeto(c, F):
    rng = random.Random(81)
    alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    puntuacion = "? ! . , ; : ' \" "
    c.setFillColor(GRIS_TEXTURA)
    tam = 9
    y = 52
    while y < H - 52:
        t = c.beginText(50, y)
        t.setFont(F["Sans"], tam)
        piezas = []
        for _ in range(60):
            piezas.append(rng.choice(alfabeto))
            if rng.random() < 0.10:
                piezas.append(rng.choice(puntuacion.strip()))
        t.textOut(" ".join(piezas))
        c.drawText(t)
        y += 14


def bloque_abc(c, cx, cy, lado, letra, color, F):
    """Bloque cúbico tipo ABC con una letra grande en su cara."""
    c.setStrokeColor(color)
    c.setLineWidth(2)
    c.rect(cx - lado / 2, cy - lado / 2, lado, lado, stroke=1, fill=0)
    c.line(cx - lado / 2, cy + lado / 2, cx - lado / 2 + lado * 0.18, cy + lado / 2 + lado * 0.18)
    c.line(cx + lado / 2, cy + lado / 2, cx + lado / 2 + lado * 0.18, cy + lado / 2 + lado * 0.18)
    c.line(cx - lado / 2 + lado * 0.18, cy + lado / 2 + lado * 0.18,
           cx + lado / 2 + lado * 0.18, cy + lado / 2 + lado * 0.18)
    centrado(c, letra, cy - lado * 0.15, F["Serif-Bold"], lado * 0.55, color, x=cx)


def bocadillo_hello(c, cx, cy, ancho, alto, color, F):
    """Bocadillo de diálogo con 'Hello!'."""
    c.setStrokeColor(color)
    c.setLineWidth(2)
    c.roundRect(cx - ancho / 2, cy - alto / 2, ancho, alto, 10, stroke=1, fill=0)
    p = c.beginPath()
    p.moveTo(cx - ancho * 0.15, cy - alto / 2)
    p.lineTo(cx - ancho * 0.05, cy - alto * 0.85)
    p.lineTo(cx + ancho * 0.10, cy - alto / 2)
    c.drawPath(p, stroke=1, fill=0)
    centrado(c, "Hello!", cy - 6, F["Serif-Bold"], min(alto * 0.45, 22), color, x=cx)


def signo_pregunta(c, cx, cy, tam, color, F):
    centrado(c, "?", cy, F["Serif-Bold"], tam, color, x=cx)


def signo_exclamacion(c, cx, cy, tam, color, F):
    centrado(c, "!", cy, F["Serif-Bold"], tam, color, x=cx)


def comillas_inglesas(c, cx, cy, tam, color, F):
    centrado(c, '"  "', cy, F["Serif-Bold"], tam, color, x=cx)


def letras_aa(c, cx, cy, tam, color, F):
    centrado(c, "Aa", cy, F["Serif-Bold"], tam, color, x=cx)


def marca_agua(c, cfg, medalla=None):
    """Sin trofeo: textura de alfabeto + bloques ABC + imágenes propias."""
    if cfg.sin_marca_agua:
        return
    F = cfg.fuentes
    c.saveState()
    clip = c.beginPath()
    clip.rect(41, 41, W - 82, H - 82)
    c.clipPath(clip, stroke=0, fill=0)
    if cfg.marcas_img:
        n = len(cfg.marcas_img)
        pos = POSICIONES_MARCA.get(n)
        if pos is None:
            filas = (n + 1) // 2
            pos = [(0.30 if i % 2 == 0 else 0.70,
                    1 - (i // 2 + 0.5) / filas * 0.8 - 0.1, 170) for i in range(n)]
        for img, (fx, fy, lado) in zip(cfg.marcas_img, pos):
            iw, ih = img.getSize()
            esc = lado / max(iw, ih)
            c.drawImage(img, fx * W - iw * esc / 2, fy * H - ih * esc / 2,
                        iw * esc, ih * esc, mask="auto")
    else:
        c.saveState()
        c.setFillAlpha(0.55)
        textura_alfabeto(c, F)
        c.restoreState()

        c.saveState()
        c.setFillAlpha(0.72)
        c.setStrokeAlpha(0.72)
        bloque_abc(c, 110, 700, 62, "A", GRIS_A, F)
        bloque_abc(c, 180, 660, 46, "B", GRIS_B, F)
        bloque_abc(c, W - 120, 260, 56, "C", GRIS_C, F)
        bocadillo_hello(c, W - 120, 620, 130, 62, GRIS_A, F)
        signo_pregunta(c, 110, 260, 90, GRIS_C, F)
        signo_exclamacion(c, W - 110, 460, 90, GRIS_B, F)
        comillas_inglesas(c, 110, 470, 60, GRIS_A, F)
        letras_aa(c, W / 2, 200, 70, GRIS_C, F)
        c.restoreState()
    c.restoreState()


# --------------------------------------------------------------------------
# Certificado
# --------------------------------------------------------------------------
def dibujar_certificado(c, nombre, centro, grado, medalla, cfg, folio):
    F = cfg.fuentes
    colores = MEDALLA_COLORES[medalla]
    ancho_texto = 425

    subtitulo = cfg.subtitulo or f"MEDALLA DE {MEDALLA_NOMBRE[medalla]}"
    texto_rol = cfg.texto_rol or f"por haber obtenido la medalla de {medalla} en el"

    marca_agua(c, cfg, medalla)
    marco(c, colores["cuerpo"])

    y = H - 100
    if cfg.logos:
        y_top = H - 66
        y = y_top - dibujar_logos(c, cfg.logos, y_top) - 30
    if cfg.encabezado:
        centrado(c, cfg.encabezado.upper(), y, F["Sans-Bold"], 10.5, MUTED, 2.5)
        y -= 62

    centrado(c, cfg.titulo, y, F["Serif-Bold"], 44, NAVY, 5)
    y -= 34
    centrado(c, subtitulo, y, F["Serif-Bold"], 18, colores["base"], 4.5)
    y -= 30
    ornamento(c, y, colores["cuerpo"])
    y -= 8

    # ---- Medalla centrada (más grande, entre el rombo y "Se otorga a") ----
    medal_r = 32
    medal_cy = y - medal_r * 1.90
    dibujar_medalla(c, W / 2, medal_cy, medal_r, colores)
    y = medal_cy - medal_r - 10
    # ----------------------------------------------------------------------

    centrado(c, "Se otorga a", y, F["Serif-Italic"], 15, MUTED)
    y -= 48

    lineas, tam = ajustar_nombre(nombre, F["Serif-Bold"], W - 130)
    for ln in lineas:
        centrado(c, ln, y, F["Serif-Bold"], tam, NAVY)
        y -= tam * 1.25

    y_sub = y + tam * 1.25 - 10
    c.setStrokeColor(colores["cuerpo"])
    c.setLineWidth(1)
    c.line(W / 2 - 210, y_sub, W / 2 + 210, y_sub)
    y = y_sub - 34

    if grado:
        centrado(c, f"Estudiante del grado {grado}", y, F["Serif-Bold"], 14, NAVY)
        y -= 26

    if centro:
        centrado(c, "en representación de", y, F["Serif-Italic"], 12, MUTED)
        y -= 22
        y = parrafo(c, centro, y, F["Serif-Bold"], 15, NAVY, ancho_texto, 1.3)
        y -= 14

    y -= 10
    y = parrafo(c, texto_rol, y, F["Serif"], 14, INK, ancho_texto, 1.6)
    y -= 6
    y = parrafo(c, cfg.evento, y, F["Serif-Bold"], 19, NAVY, ancho_texto, 1.35)
    y -= 6
    if hasattr(cfg,'modalidad'):
        y = parrafo(c, f"en la modalidad de {cfg.modalidad},", y, F["Serif"], 14, INK,
                    ancho_texto, 1.6)
    y = parrafo(c, f"celebrado en {cfg.lugar} el {cfg.fecha_txt}.", y, F["Serif"], 14, INK,
                ancho_texto, 1.6)

    y_sup, con_img = geometria_firmas(cfg)
    if y_sup and y < y_sup + (ALTO_IMG_FIRMA + 20 if con_img else 30):
        print(f"Aviso: el texto de '{nombre}' queda muy cerca de las firmas.", file=sys.stderr)

    firmas(c, cfg, F)


# --------------------------------------------------------------------------
# Argumentos
# --------------------------------------------------------------------------
def parsear_argumentos():
    p = argparse.ArgumentParser(
        description="Certificados de medallas de Inglés (A4 vertical)."
    )
    p.add_argument("csv", type=Path, help="CSV con los ganadores")
    p.add_argument("-o", "--salida", type=Path, default=Path("premios_ing"))
    p.add_argument("--evento", default="Concurso Provincial de Inglés")
    # p.add_argument("--modalidad", default="English Language Competition")
    p.add_argument("--lugar", default="Matanzas")
    p.add_argument("--fecha", default=None,
                   help="AAAA-MM-DD o texto libre (por defecto: hoy)")
    p.add_argument("--encabezado", default="")
    p.add_argument("--titulo", default="CERTIFICADO")
    p.add_argument("--subtitulo", default=None,
                   help="Por defecto: 'MEDALLA DE ORO/PLATA/BRONCE'")
    p.add_argument("--texto-rol", dest="texto_rol", default=None,
                   help="Por defecto: 'por haber obtenido la medalla de <medalla> en el'")
    p.add_argument("--medalla", choices=["oro", "plata", "bronce", "todas"], default="todas")
    p.add_argument("--agrupar-por-medalla", action="store_true")
    p.add_argument("--firma", action="append", default=[], metavar="'Nombre|Cargo|img'",
                   help=f"Pie de firma (hasta {MAX_FIRMAS}); imagen opcional")
    p.add_argument("--sin-firmas", action="store_true")
    p.add_argument("--logo", action="append", default=[], type=Path,
                   help="Hasta 3 logos; repetir la opción")
    p.add_argument("--marca-agua", action="append", default=[], type=Path,
                   help="Imágenes propias de marca de agua (en gris claro)")
    p.add_argument("--opacidad-marca", type=float, default=0.16,
                   help="Intensidad de las imágenes propias, 0.05-0.5 (def. 0.16)")
    p.add_argument("--sin-marca-agua", action="store_true")
    p.add_argument("--sin-folio", action="store_true")
    args = p.parse_args()

    if len(args.firma) > MAX_FIRMAS:
        p.error(f"Máximo {MAX_FIRMAS} firmas.")
    if len(args.logo) > 3:
        p.error("Máximo 3 logos.")
    for r in args.logo + args.marca_agua:
        if not r.exists():
            p.error(f"No existe: {r}")
    if not args.csv.exists():
        p.error(f"No existe: {args.csv}")

    args.firmas_parsed = []
    for f in args.firma:
        partes = [x.strip() for x in f.split("|")]
        if len(partes) == 1:
            nombre, cargo, img = "", partes[0], ""
        else:
            nombre, cargo, img = partes[0], partes[1], (partes[2] if len(partes) > 2 else "")
        if img and not Path(img).exists():
            p.error(f"No existe la imagen de firma: {img}")
        args.firmas_parsed.append((nombre, cargo, preparar_firma(img) if img else None))
    args.logos = args.logo
    args.marcas_img = [preparar_marca(r, min(max(args.opacidad_marca, 0.05), 0.5))
                       for r in args.marca_agua]
    args.fecha_txt = formatear_fecha(args.fecha)
    return args


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    cfg = parsear_argumentos()
    cfg.fuentes = registrar_fuentes()

    participantes = leer_csv(cfg.csv)
    if not participantes:
        sys.exit("El CSV no contiene ganadores.")

    if cfg.medalla != "todas":
        participantes = [p for p in participantes if p[3] == cfg.medalla]
        if not participantes:
            sys.exit(f"No hay participantes con medalla de {cfg.medalla}.")

    cfg.salida.mkdir(parents=True, exist_ok=True)

    def folio(i):
        return None if cfg.sin_folio else f"N.º {i:03d}"

    # Un PDF por participante
    for i, (nombre, centro, grado, medalla) in enumerate(participantes, 1):
        carpeta = cfg.salida
        if cfg.agrupar_por_medalla:
            carpeta = cfg.salida / medalla.capitalize()
            carpeta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta / f"{i:03d}_{medalla.capitalize()}_Grado{grado_numero(grado)}_{slug(nombre)}.pdf"
        c = canvas.Canvas(str(ruta), pagesize=A4)
        c.setTitle(f"Medalla {MEDALLA_NOMBRE[medalla].title()} Inglés - {nombre}")
        c.setAuthor(cfg.evento)
        dibujar_certificado(c, nombre, centro, grado, medalla, cfg, folio(i))
        c.showPage()
        c.save()

    # PDF combinado
    ruta_todos = cfg.salida / "todos_los_certificados_ing.pdf"
    c = canvas.Canvas(str(ruta_todos), pagesize=A4)
    c.setTitle(f"Medallas Inglés - {cfg.evento}")
    c.setAuthor(cfg.evento)
    for i, (nombre, centro, grado, medalla) in enumerate(participantes, 1):
        dibujar_certificado(c, nombre, centro, grado, medalla, cfg, folio(i))
        c.showPage()
    c.save()

    por_medalla = {}
    for _, _, _, m in participantes:
        por_medalla[m] = por_medalla.get(m, 0) + 1
    resumen = ", ".join(f"{n} {m}" for m, n in sorted(por_medalla.items()))
    print(f"Listo: {len(participantes)} certificados de Inglés ({resumen}) en "
          f"'{cfg.salida}/' (más {ruta_todos.name}).")


if __name__ == "__main__":
    main()