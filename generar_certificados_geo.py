#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de certificados de PARTICIPACIÓN — Geografía (A4 vertical).
Marca de agua: globos terráqueos con meridianos y paralelos, rosa de los
vientos, cadenas montañosas, pin de mapa y textura de coordenadas.
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


# --------------------------------------------------------------------------
# Fuentes
# --------------------------------------------------------------------------
def registrar_fuentes() -> dict[str, str]:
    """Usa DejaVu (tildes/ñ garantizadas) si está disponible; si no, Times/Helvetica."""
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
            for nombre, f in archivos.items():
                pdfmetrics.registerFont(TTFont(nombre, str(carpeta / f)))
            return {k: k for k in archivos}
    print("Aviso: no se encontró DejaVu; se usan fuentes estándar (Times/Helvetica).",
          file=sys.stderr)
    return {
        "Serif": "Times-Roman",
        "Serif-Bold": "Times-Bold",
        "Serif-Italic": "Times-Italic",
        "Sans": "Helvetica",
        "Sans-Bold": "Helvetica-Bold",
    }


# --------------------------------------------------------------------------
# Lectura del CSV
# --------------------------------------------------------------------------
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def _limpiar(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def leer_csv(ruta: Path) -> list[tuple[str, str]]:
    """Devuelve [(nombre, centro)] ignorando filas vacías."""
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

    if not tiene_cabecera:  # sin cabecera: 1.ª columna = nombre, 2.ª = centro (opcional)
        return [
            (_limpiar(f[0]), _limpiar(f[1]) if len(f) > 1 else "")
            for f in filas if _limpiar(f[0])
        ]

    def indice(claves):
        return next((i for i, h in enumerate(cabecera) if h in claves), None)

    i_nom, i_ape, i_cen = indice(CLAVES_NOMBRE), indice(CLAVES_APELLIDO), indice(CLAVES_CENTRO)
    if i_nom is None:
        sys.exit("El CSV necesita una columna 'nombre'.")

    def celda(fila, i):
        return _limpiar(fila[i]) if i is not None and i < len(fila) else ""

    resultado = []
    for f in filas[1:]:
        nombre = _limpiar(f"{celda(f, i_nom)} {celda(f, i_ape)}")
        if nombre:
            resultado.append((nombre, celda(f, i_cen)))
    return resultado


# --------------------------------------------------------------------------
# Utilidades de dibujo
# --------------------------------------------------------------------------
def fecha_es(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def formatear_fecha(valor: str | None) -> str:
    if not valor:
        return fecha_es(date.today())
    try:
        return fecha_es(date.fromisoformat(valor))
    except ValueError:
        return valor  # texto libre


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:60] or "participante"


def centrado(c, texto, y, fuente, tam, color=INK, espacio=0.0, x=None):
    x = W / 2 if x is None else x
    ancho = pdfmetrics.stringWidth(texto, fuente, tam) + espacio * max(len(texto) - 1, 0)
    c.setFillColor(color)
    t = c.beginText(x - ancho / 2, y)
    t.setFont(fuente, tam)
    t.setCharSpace(espacio)
    t.textOut(texto)
    c.drawText(t)


def parrafo(c, texto, y, fuente, tam, color, ancho, interlineado=1.45):
    """Dibuja un párrafo centrado; devuelve la línea base siguiente."""
    for ln in simpleSplit(texto, fuente, tam, ancho):
        centrado(c, ln, y, fuente, tam, color)
        y -= tam * interlineado
    return y


def rombo(c, x, y, lado=8):
    c.saveState()
    c.translate(x, y)
    c.rotate(45)
    c.setFillColor(GOLD)
    c.rect(-lado / 2, -lado / 2, lado, lado, stroke=0, fill=1)
    c.restoreState()


def marco(c):
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.rect(30, 30, W - 60, H - 60)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.rect(40, 40, W - 80, H - 80)
    for x, y in ((40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)):
        rombo(c, x, y, 9)


def ornamento(c, y):
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(W / 2 - 110, y, W / 2 - 12, y)
    c.line(W / 2 + 12, y, W / 2 + 110, y)
    rombo(c, W / 2, y, 7)


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
    """Una línea reduciendo el tamaño; si no cabe, dos líneas equilibradas."""
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


MAX_FIRMAS = 6
ALTO_IMG_FIRMA = 44


def lista_firmas(cfg):
    """[(nombre, cargo, imagen|None)]; vacío si --sin-firmas."""
    if cfg.sin_firmas:
        return []
    return cfg.firmas_parsed or [("", "Comité Organizador", None)]


def distribuir_firmas(n):
    """Cantidad de firmas por fila: hasta 3 en una fila; de 4 a 6, dos filas."""
    if n <= 3:
        return [n]
    primera = (n + 1) // 2
    return [primera, n - primera]


def geometria_firmas(cfg):
    """Devuelve (y de la línea de la fila superior, hay_imagen_en_fila_superior)."""
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
# Marca de agua alegórica a GEOGRAFÍA
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
    """Pasa la imagen a gris claro conservando su transparencia."""
    im = Image.open(ruta).convert("RGBA")
    r, g, b, a = im.split()
    gris = Image.merge("RGB", (r, g, b)).convert("L")
    gris = gris.point(lambda v: int(255 - (255 - v) * opacidad))
    return ImageReader(Image.merge("RGBA", (gris, gris, gris, a)))


def preparar_firma(ruta):
    """Si la imagen no tiene transparencia (foto/escaneo), vuelve transparente el fondo blanco."""
    im = Image.open(ruta)
    tiene_alfa = im.mode in ("RGBA", "LA") or "transparency" in im.info
    rgba = im.convert("RGBA")
    if not tiene_alfa:
        gris = rgba.convert("L")
        alfa = gris.point(lambda v: max(0, min(255, int((245 - v) * 255 / 55))))
        rgba.putalpha(alfa)
    return ImageReader(rgba)


def textura_coordenadas(c, F):
    """Coordenadas latitud/longitud repetidas muy tenues como textura de fondo."""
    rng = random.Random(51)
    c.setFillColor(GRIS_TEXTURA)
    tam = 9
    y = 52
    while y < H - 52:
        t = c.beginText(50, y)
        t.setFont(F["Sans"], tam)
        partes = []
        for _ in range(7):
            lat = f"{rng.randint(0, 89)}°{rng.randint(0, 59)}'{rng.choice('NS')}"
            lon = f"{rng.randint(0, 179)}°{rng.randint(0, 59)}'{rng.choice('EW')}"
            partes.append(f"{lat} {lon}")
        t.textOut("   ".join(partes))
        c.drawText(t)
        y += 15


def globo(c, cx, cy, r, color):
    """Globo terráqueo con meridianos, paralelos y eje."""
    c.setStrokeColor(color)
    c.setLineWidth(2)
    c.circle(cx, cy, r, stroke=1, fill=0)
    # meridianos (elipses con distinto semieje horizontal)
    for k in (0.4, 0.75):
        c.ellipse(cx - r * k, cy - r, cx + r * k, cy + r, stroke=1, fill=0)
    # paralelos (líneas horizontales)
    for dy in (-0.55, 0, 0.55):
        c.line(cx - r, cy + dy * r, cx + r, cy + dy * r)
    # eje vertical
    c.line(cx, cy - r * 1.15, cx, cy + r * 1.15)


def rosa_vientos(c, cx, cy, r, color):
    """Rosa de los vientos de 4 puntas con rombos."""
    c.setStrokeColor(color)
    c.setLineWidth(1.8)
    for k in range(4):
        a = math.radians(90 * k)
        x1 = cx + r * math.cos(a)
        y1 = cy + r * math.sin(a)
        x2 = cx - r * 0.35 * math.cos(a)
        y2 = cy - r * 0.35 * math.sin(a)
        # vértice lateral (perpendicular)
        b = a + math.radians(90)
        px = cx + r * 0.18 * math.cos(b)
        py = cy + r * 0.18 * math.sin(b)
        p = c.beginPath()
        p.moveTo(x1, y1)
        p.lineTo(px, py)
        p.lineTo(x2, y2)
        p.lineTo(cx - px + cx, cy - py + cy)
        p.close()
        c.drawPath(p, stroke=1, fill=0)


def montanas(c, x0, y0, ancho, alto, color):
    """Cadena montañosa estilizada."""
    c.setStrokeColor(color)
    c.setLineWidth(2)
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.lineTo(x0 + ancho * 0.20, y0 + alto)
    p.lineTo(x0 + ancho * 0.35, y0 + alto * 0.45)
    p.lineTo(x0 + ancho * 0.55, y0 + alto * 1.0)
    p.lineTo(x0 + ancho * 0.80, y0 + alto * 0.35)
    p.lineTo(x0 + ancho, y0)
    c.drawPath(p, stroke=1, fill=0)


def pin(c, cx, cy, r, color):
    """Pin de mapa (marcador de ubicación)."""
    c.setStrokeColor(color)
    c.setLineWidth(2)
    p = c.beginPath()
    p.moveTo(cx, cy - r * 1.6)
    p.curveTo(cx - r * 1.05, cy + r * 0.1, cx - r * 0.65, cy + r * 0.95,
              cx, cy + r * 0.95)
    p.curveTo(cx + r * 0.65, cy + r * 0.95, cx + r * 1.05, cy + r * 0.1,
              cx, cy - r * 1.6)
    c.drawPath(p, stroke=1, fill=0)
    c.setFillColor(color)
    c.circle(cx, cy + r * 0.15, r * 0.32, stroke=0, fill=1)


def marca_agua(c, cfg):
    if cfg.sin_marca_agua:
        return
    F = cfg.fuentes
    c.saveState()
    clip = c.beginPath()
    clip.rect(41, 41, W - 82, H - 82)
    c.clipPath(clip, stroke=0, fill=0)
    if cfg.marcas_img:                      # imágenes propias
        n = len(cfg.marcas_img)
        if n in POSICIONES_MARCA:
            pos = POSICIONES_MARCA[n]
        else:
            filas = (n + 1) // 2
            pos = [(0.30 if i % 2 == 0 else 0.70, 1 - (i // 2 + 0.5) / filas * 0.8 - 0.1, 170)
                   for i in range(n)]
        for img, (fx, fy, lado) in zip(cfg.marcas_img, pos):
            iw, ih = img.getSize()
            esc = lado / max(iw, ih)
            c.drawImage(img, fx * W - iw * esc / 2, fy * H - ih * esc / 2, iw * esc, ih * esc,
                        mask="auto")
    else:                                   # dibujos integrados de GEOGRAFÍA
        c.saveState()
        c.setFillAlpha(0.55)
        textura_coordenadas(c, F)
        c.restoreState()

        c.saveState()
        c.setFillAlpha(0.72)
        c.setStrokeAlpha(0.72)
        globo(c, 110, 700, 60, GRIS_A)
        globo(c, W - 105, 280, 48, GRIS_B)
        rosa_vientos(c, W - 110, 600, 40, GRIS_A)
        rosa_vientos(c, 110, 240, 30, GRIS_C)
        montanas(c, W - 220, 130, 200, 70, GRIS_A)
        montanas(c, 60, 420, 180, 60, GRIS_C)
        pin(c, 110, 480, 20, GRIS_B)
        c.restoreState()
    c.restoreState()


# --------------------------------------------------------------------------
# Certificado
# --------------------------------------------------------------------------
def dibujar_certificado(c, nombre, centro, cfg, folio):
    F = cfg.fuentes
    ancho_texto = 425
    marca_agua(c, cfg)
    marco(c)

    y = H - 100
    if cfg.logos:
        y_top = H - 66
        y = y_top - dibujar_logos(c, cfg.logos, y_top) - 30
    if cfg.encabezado:
        centrado(c, cfg.encabezado.upper(), y, F["Sans-Bold"], 10.5, MUTED, 2.5)
        y -= 62

    centrado(c, cfg.titulo, y, F["Serif-Bold"], 44, NAVY, 5)
    y -= 34
    centrado(c, cfg.subtitulo, y, F["Serif"], 18, GOLD, 4.5)
    y -= 30
    ornamento(c, y)
    y -= 50

    centrado(c, "Se otorga a", y, F["Serif-Italic"], 15, MUTED)
    y -= 48

    lineas, tam = ajustar_nombre(nombre, F["Serif-Bold"], W - 130)
    for ln in lineas:
        centrado(c, ln, y, F["Serif-Bold"], tam, NAVY)
        y -= tam * 1.25
    y_sub = y + tam * 1.25 - 10
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(W / 2 - 210, y_sub, W / 2 + 210, y_sub)
    y = y_sub - 34

    if centro:
        centrado(c, "en representación de", y, F["Serif-Italic"], 12, MUTED)
        y -= 22
        y = parrafo(c, centro, y, F["Serif-Bold"], 15, NAVY, ancho_texto, 1.3)
        y -= 14

    y -= 10
    y = parrafo(c, cfg.texto_rol, y, F["Serif"], 14, INK, ancho_texto, 1.6)
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

    if folio:
        centrado(c, folio, 56, F["Sans"], 8, MUTED, 1)


# --------------------------------------------------------------------------
# Programa principal
# --------------------------------------------------------------------------
def parsear_argumentos():
    p = argparse.ArgumentParser(
        description="Genera certificados de participación en Geografía (A4 vertical).")
    p.add_argument("csv", type=Path, help="Archivo CSV con los participantes")
    p.add_argument("-o", "--salida", type=Path, default=Path("certificados_geo"),
                   help="Carpeta de salida (por defecto: certificados_geo)")
    p.add_argument("--evento", default="Concurso Provincial de Geografía")
    # p.add_argument("--modalidad", default="Resolución de Problemas de Geografía")
    p.add_argument("--lugar", default="Matanzas")
    p.add_argument("--fecha", default=None,
                   help="AAAA-MM-DD o texto libre (por defecto: hoy)")
    p.add_argument("--encabezado", default="",
                   help="Línea superior (vacío para omitirla)")
    p.add_argument("--titulo", default="CERTIFICADO")
    p.add_argument("--subtitulo", default="DE PARTICIPACIÓN")
    p.add_argument("--texto-rol", dest="texto_rol",
                   default="por su participación como concursante en el")
    p.add_argument("--firma", action="append", default=[], metavar="'Nombre|Cargo|imagen'",
                   help=f"Pie de firma; repetir la opción (hasta {MAX_FIRMAS}). La imagen de la "
                        "firma es opcional (PNG/JPG); sin '|' se toma como cargo")
    p.add_argument("--sin-firmas", action="store_true", help="No dibujar pies de firma")
    p.add_argument("--logo", action="append", default=[], type=Path,
                   help="Hasta 3 logos (PNG/JPG) en la parte superior; repetir la opción")
    p.add_argument("--marca-agua", action="append", default=[], type=Path, metavar="IMAGEN",
                   help="Imágenes propias para la marca de agua (se pasan a gris claro); "
                        "sustituyen a los dibujos integrados")
    p.add_argument("--opacidad-marca", type=float, default=0.16,
                   help="Intensidad de tus imágenes de marca de agua, 0.05-0.5 (def. 0.16)")
    p.add_argument("--sin-marca-agua", action="store_true",
                   help="Fondo blanco, sin marca de agua")
    p.add_argument("--sin-folio", action="store_true",
                   help="No numerar los certificados")
    args = p.parse_args()

    if len(args.firma) > MAX_FIRMAS:
        p.error(f"Máximo {MAX_FIRMAS} firmas.")
    if len(args.logo) > 3:
        p.error("Máximo 3 logos.")
    for r in args.logo + args.marca_agua:
        if not r.exists():
            p.error(f"No existe la imagen: {r}")
    if not args.csv.exists():
        p.error(f"No existe el CSV: {args.csv}")

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


def main():
    cfg = parsear_argumentos()
    cfg.fuentes = registrar_fuentes()

    participantes = leer_csv(cfg.csv)
    if not participantes:
        sys.exit("El CSV no contiene participantes.")

    cfg.salida.mkdir(parents=True, exist_ok=True)

    def folio(i):
        return None if cfg.sin_folio else f"N.º {i:03d}"

    # Un PDF por participante
    for i, (nombre, centro) in enumerate(participantes, 1):
        ruta = cfg.salida / f"{i:03d}_{slug(nombre)}.pdf"
        c = canvas.Canvas(str(ruta), pagesize=A4)
        c.setTitle(f"Certificado Geografía - {nombre}")
        c.setAuthor(cfg.evento)
        dibujar_certificado(c, nombre, centro, cfg, folio(i))
        c.showPage()
        c.save()

    # PDF combinado (una página por participante)
    ruta_todos = cfg.salida / "todos_los_certificados_geo.pdf"
    c = canvas.Canvas(str(ruta_todos), pagesize=A4)
    c.setTitle(f"Certificados Geografía - {cfg.evento}")
    c.setAuthor(cfg.evento)
    for i, (nombre, centro) in enumerate(participantes, 1):
        dibujar_certificado(c, nombre, centro, cfg, folio(i))
        c.showPage()
    c.save()

    print(f"Listo: {len(participantes)} certificados de Geografía en '{cfg.salida}/' "
          f"(más {ruta_todos.name}).")


if __name__ == "__main__":
    main()