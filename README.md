# 📜 README — Generador de Certificados de Concursos

Sistema de generación automática de **certificados de participación** y **certificados de medallas (Oro/Plata/Bronce)** para los concursos provinciales de las siguientes asignaturas:

- Informática (`_inf`)
- Matemática (`_mat`)
- Física (`_fis`)
- Química (`_qui`)
- Biología (`_bio`)
- Geografía (`_geo`)
- Español (`_esp`)
- Historia (`_his`)
- Inglés (`_ing`)

Todos los certificados se generan en **PDF A4 vertical**, con marco decorativo, marca de agua alegórica a la asignatura, medallas vectoriales (en el caso de premios), logos institucionales opcionales y pies de firma personalizables.

---

## 📑 Índice

1. [Requisitos e instalación](#1-requisitos-e-instalación)
2. [Estructura de archivos](#2-estructura-de-archivos)
3. [Inicio rápido (5 minutos)](#3-inicio-rápido-5-minutos)
4. [Formato del CSV](#4-formato-del-csv)
5. [Scripts de participación](#5-scripts-de-participación)
6. [Scripts de medallas](#6-scripts-de-medallas)
7. [Opciones de línea de comandos](#7-opciones-de-línea-de-comandos)
8. [Logos institucionales](#8-logos-institucionales)
9. [Pies de firma](#9-pies-de-firma)
10. [Marca de agua](#10-marca-de-agua)
11. [Ejemplos completos por asignatura](#11-ejemplos-completos-por-asignatura)
12. [Automatización y lotes](#12-automatización-y-lotes)
13. [Solución de problemas](#13-solución-de-problemas)
14. [Preguntas frecuentes](#14-preguntas-frecuentes)

---

## 1. Requisitos e instalación

### 1.1. Software necesario

| Componente | Versión mínima | Notas |
|---|---|---|
| Python | 3.10+ | Se usa sintaxis `str \| None`, `from __future__ import annotations` |
| pip | cualquiera reciente | Para instalar dependencias |
| Sistema operativo | Windows, Linux o macOS | Probado en los tres |

### 1.2. Dependencias de Python

```bash
pip install reportlab pillow
```

- **`reportlab`**: motor de generación de PDF.
- **`Pillow`**: procesamiento de imágenes (logos, firmas, marcas de agua).

### 1.3. Fuentes (muy recomendable)

Los scripts usan **DejaVu Sans / DejaVu Serif** para garantizar tildes, ñ y símbolos (`π`, `√`, `⇌`, `«»`). Buscan en este orden:

1. `./fuentes/` (junto al script)
2. `/usr/share/fonts/truetype/dejavu` (Linux)
3. `C:/Windows/Fonts` (Windows)
4. `~/Library/Fonts` (macOS)

**Si no se encuentran**, el script avisa y usa `Times`/`Helvetica`, que no cubren todos los símbolos. Para evitarlo:

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt install fonts-dejavu
  ```
- **Windows:** ya vienen instaladas (`DejaVu` no, pero puede descargarlas de [dejavu-fonts.github.io](https://dejavu-fonts.github.io/) y copiarlas a `C:\Windows\Fonts` o a la carpeta `fuentes/`).
- **macOS:** `brew install --cask font-dejavu`

Alternativa rápida (cualquier SO): crear una carpeta `fuentes/` junto a los scripts y copiar dentro:

```
fuentes/
├── DejaVuSerif.ttf
├── DejaVuSerif-Bold.ttf
├── DejaVuSerif-Italic.ttf
├── DejaVuSans.ttf
└── DejaVuSans-Bold.ttf
```

---

## 2. Estructura de archivos

Estructura recomendada del proyecto:

```
mi-concurso/
├── generar_certificados_inf.py      ← script participación (Informática)
├── generar_premios_inf.py           ← script medallas     (Informática)
├── generar_certificados_mat.py      ← Matemática
├── generar_premios_mat.py
├── generar_certificados_fis.py
├── generar_premios_fis.py
├── generar_certificados_qui.py
├── generar_premios_qui.py
├── generar_certificados_bio.py
├── generar_premios_bio.py
├── generar_certificados_geo.py
├── generar_premios_geo.py
├── generar_certificados_esp.py
├── generar_premios_esp.py
├── generar_certificados_his.py
├── generar_premios_his.py
├── generar_certificados_ing.py
├── generar_premios_ing.py
│
├── fuentes/                         ← (opcional) TTFs DejaVu
│
├── logos/                           ← logos institucionales
│   ├── mined.png
│   ├── comite.png
│   └── ...
│
├── firmas/                          ← imágenes de firmas (opcional)
│   ├── presidente.png
│   ├── director.png
│   └── ...
│
├── datos/                           ← CSVs de entrada
│   ├── participantes_inf.csv
│   ├── ganadores_inf.csv
│   ├── participantes_mat.csv
│   ├── ganadores_mat.csv
│   └── ...
│
└── salida/                          ← PDFs generados (se crea sola)
    ├── certificados_inf/
    ├── premios_inf/
    └── ...
```

---

## 3. Inicio rápido (5 minutos)

### Paso 1 — Instalar dependencias

```bash
pip install reportlab pillow
```

### Paso 2 — Descargar los 16 scripts

Coloca todos los archivos `.py` en una misma carpeta.

### Paso 3 — Crear el CSV de participantes

Archivo `datos/participantes_fis.csv`:

```csv
nombre,centro
Ana María Pérez Gómez,IPVCE "Carlos Marx"
Juan Carlos Díaz López,IPUEC "Mártires de Girón"
Laura Fernández Ruiz,IPVCE "Carlos Marx"
```

### Paso 4 — Ejecutar el script

```bash
python generar_certificados_fis.py datos/participantes_fis.csv
```

### Paso 5 — Resultado

Se genera la carpeta `certificados_fis/` con:

```
certificados_fis/
├── 001_Ana_Maria_Perez_Gomez.pdf
├── 002_Juan_Carlos_Diaz_Lopez.pdf
├── 003_Laura_Fernandez_Ruiz.pdf
└── todos_los_certificados_fis.pdf   ← todos en un solo PDF
```

¡Listo! 🎉

---

## 4. Formato del CSV

Los scripts aceptan **dos formatos de CSV**:

### 4.1. Participación (sin medalla)

**Con cabecera:**

```csv
nombre,centro
Ana Pérez,IPVCE "Carlos Marx"
Juan Gómez,IPUEC "Mártires de Girón"
```

**También acepta `nombres` + `apellidos` por separado:**

```csv
nombres,apellidos,centro
Ana María,Pérez Gómez,IPVCE "Carlos Marx"
Juan Carlos,Díaz López,IPUEC "Mártires de Girón"
```

**Sin cabecera** (solo datos, 2 columnas: nombre y centro):

```csv
Ana Pérez,IPVCE "Carlos Marx"
Juan Gómez,IPUEC "Mártires de Girón"
```

### 4.2. Medallas (con grado y medalla)

**Con cabecera:**

```csv
nombre,centro,grado,medalla
Ana Pérez,IPVCE "Carlos Marx",10,oro
Juan Gómez,IPVCE "Carlos Marx",11,plata
Luis Díaz,IPVCE "Carlos Marx",12,bronce
```

**Sin cabecera** (4 columnas fijas: nombre, centro, grado, medalla):

```csv
Ana Pérez,IPVCE "Carlos Marx",10,oro
Juan Gómez,IPVCE "Carlos Marx",11,plata
```

### 4.3. Codificación y separadores

| Aspecto | Valores aceptados |
|---|---|
| Codificación | `UTF-8` (con o sin BOM) y `Windows-1252` |
| Separador | `,` · `;` · `TAB` (autodetectado) |
| Columnas nombre | `nombre`, `nombres`, `nombre completo`, `name`, `estudiante`, `participante` |
| Columnas apellido | `apellido`, `apellidos` |
| Columnas centro | `centro`, `escuela`, `institucion`, `centro de estudio(s)`, `school` |
| Columnas grado | `grado`, `grade`, `nivel`, `año`, `ano`, `curso` |
| Columnas medalla | `medalla`, `medal`, `premio`, `distincion`, `distinción` |

### 4.4. Valores normalizados

**Grados:**

| Valor en CSV | Se muestra como |
|---|---|
| `10`, `decimo`, `décimo`, `diez` | `décimo` |
| `11`, `onceno`, `once`, `undecimo`, `undécimo` | `onceno` |
| `12`, `duodecimo`, `duodécimo`, `doce` | `duodécimo` |

**Medallas:**

| Valor en CSV | Se muestra como |
|---|---|
| `oro`, `gold`, `dorada`, `dorado`, `1`, `primero`, `primer lugar` | **ORO** |
| `plata`, `silver`, `plateada`, `plateado`, `2`, `segundo`, `segundo lugar` | **PLATA** |
| `bronce`, `bronze`, `3`, `tercero`, `tercer lugar` | **BRONCE** |

Valores desconocidos → se usa `oro` y se muestra un aviso por `stderr`.

---

## 5. Scripts de participación

### 5.1. Lista de scripts

| Asignatura | Script | Carpeta salida por defecto |
|---|---|---|
| Informática | `generar_certificados_inf.py` | `certificados_inf/` |
| Matemática | `generar_certificados_mat.py` | `certificados_mat/` |
| Física | `generar_certificados_fis.py` | `certificados_fis/` |
| Química | `generar_certificados_qui.py` | `certificados_qui/` |
| Biología | `generar_certificados_bio.py` | `certificados_bio/` |
| Geografía | `generar_certificados_geo.py` | `certificados_geo/` |
| Español | `generar_certificados_esp.py` | `certificados_esp/` |
| Historia | `generar_certificados_his.py` | `certificados_his/` |
| Inglés | `generar_certificados_ing.py` | `certificados_ing/` |

### 5.2. Sintaxis mínima

```bash
python generar_certificados_<sufijo>.py <csv> [opciones]
```

### 5.3. Textos por defecto (personalizables)

| Parámetro | Informática | Física | Química |
|---|---|---|---|
| `--evento` | Concurso Provincial de Informática | Concurso Provincial de Física | Concurso Provincial de Química |
| `--modalidad` | Programación Competitiva | Resolución de Problemas de Física | Resolución de Problemas de Química |

La estructura visible en el certificado es:

```
        [logos opcionales]
        [encabezado opcional]
        CERTIFICADO
        DE PARTICIPACIÓN
        ─────◆─────
        Se otorga a
        NOMBRE DEL PARTICIPANTE
        ────────────────
        en representación de
        NOMBRE DEL CENTRO

        por su participación como concursante en el
        CONCURSO PROVINCIAL DE <ASIGNATURA>
        en la modalidad de <modalidad>,
        celebrado en <lugar> el <fecha>.

        [firmas]
        N.º 001
```

---

## 6. Scripts de medallas

### 6.1. Lista de scripts

| Asignatura | Script | Carpeta salida por defecto |
|---|---|---|
| Informática | `generar_premios_inf.py` | `premios_inf/` |
| Matemática | `generar_premios_mat.py` | `premios_mat/` |
| Física | `generar_premios_fis.py` | `premios_fis/` |
| Química | `generar_premios_qui.py` | `premios_qui/` |
| Biología | `generar_premios_bio.py` | `premios_bio/` |
| Geografía | `generar_premios_geo.py` | `premios_geo/` |
| Español | `generar_premios_esp.py` | `premios_esp/` |
| Historia | `generar_premios_his.py` | `premios_his/` |
| Inglés | `generar_premios_ing.py` | `premios_ing/` |

### 6.2. Sintaxis mínima

```bash
python generar_premios_<sufijo>.py <csv> [opciones]
```

### 6.3. Estructura del certificado de medalla

```
        [logos opcionales]
        CERTIFICADO
        MEDALLA DE ORO                 ← en color de la medalla
        ─────◆─────
             🏅                        ← medalla vectorial centrada
        Se otorga a
        NOMBRE DEL PARTICIPANTE
        ────────────────
        Estudiante del grado onceno
        en representación de
        NOMBRE DEL CENTRO

        por haber obtenido la medalla de oro en el
        CONCURSO PROVINCIAL DE <ASIGNATURA>
        en la modalidad de <modalidad>,
        celebrado en <lugar> el <fecha>.
```

### 6.4. Agrupación por medalla

Si quieres que los PDFs se organicen en subcarpetas `Oro/`, `Plata/` y `Bronce/`:

```bash
python generar_premios_fis.py ganadores_fis.csv --agrupar-por-medalla
```

Resultado:

```
premios_fis/
├── Oro/
│   ├── 001_Oro_Grado10_Ana_Perez.pdf
│   └── 002_Oro_Grado11_Pedro_Ruiz.pdf
├── Plata/
│   └── 003_Plata_Grado11_Juan_Gomez.pdf
├── Bronce/
│   └── 004_Bronce_Grado12_Luis_Diaz.pdf
└── todos_los_certificados_fis.pdf
```

### 6.5. Filtrar por tipo de medalla

```bash
# Solo los de oro
python generar_premios_fis.py ganadores_fis.csv --medalla oro

# Solo los de plata
python generar_premios_fis.py ganadores_fis.csv --medalla plata

# Solo los de bronce
python generar_premios_fis.py ganadores_fis.csv --medalla bronce

# Todos (por defecto)
python generar_premios_fis.py ganadores_fis.csv
```

---

## 7. Opciones de línea de comandos

### 7.1. Opciones comunes (participación y medallas)

| Opción | Valor | Descripción |
|---|---|---|
| `csv` (posicional) | ruta | **Obligatorio.** CSV con los datos |
| `-o`, `--salida` | carpeta | Carpeta de salida (se crea si no existe) |
| `--evento` | texto | Nombre del concurso |
| `--modalidad` | texto | Modalidad (p. ej. "Programación Competitiva") |
| `--lugar` | texto | Ciudad/provincia (def. `Matanzas`) |
| `--fecha` | `AAAA-MM-DD` o texto | Fecha (def. hoy, formateada en español) |
| `--encabezado` | texto | Línea superior en mayúsculas (def. vacío) |
| `--titulo` | texto | Título grande (def. `CERTIFICADO`) |
| `--subtitulo` | texto | Subtítulo (def. `DE PARTICIPACIÓN` o `MEDALLA DE …`) |
| `--texto-rol` | texto | Frase antes del nombre del evento |
| `--firma` | `"Nombre\|Cargo\|img.png"` | Pie de firma (repetible, hasta 6) |
| `--sin-firmas` | flag | No dibujar firmas |
| `--logo` | `ruta.png` | Logo superior (repetible, hasta 3) |
| `--marca-agua` | `ruta.png` | Marca de agua propia (repetible) |
| `--opacidad-marca` | `0.05`–`0.5` | Intensidad de las marcas propias (def. `0.16`) |
| `--sin-marca-agua` | flag | Fondo blanco, sin marca de agua |
| `--sin-folio` | flag | No numerar los certificados |

### 7.2. Opciones exclusivas de medallas

| Opción | Valor | Descripción |
|---|---|---|
| `--medalla` | `oro`·`plata`·`bronce`·`todas` | Filtro (def. `todas`) |
| `--agrupar-por-medalla` | flag | Subcarpetas por medalla |

### 7.3. Textos por defecto de `--texto-rol`

| Script | Texto por defecto |
|---|---|
| Participación | `por su participación como concursante en el` |
| Medallas | `por haber obtenido la medalla de <medalla> en el` |

### 7.4. Ejemplos de personalización

```bash
# Cambiar el título y el subtítulo
python generar_certificados_fis.py datos.csv \
    --titulo "RECONOCIMIENTO" \
    --subtitulo "DE EXCELENCIA ACADÉMICA"

# Cambiar la fecha a formato libre
python generar_certificados_fis.py datos.csv \
    --fecha "12 de abril de 2026"

# Añadir un encabezado
python generar_certificados_fis.py datos.csv \
    --encabezado "Ministerio de Educación de Cuba"

# Añadir lugar y modalidad
python generar_certificados_fis.py datos.csv \
    --lugar "Cárdenas" \
    --modalidad "Física Experimental"
```

---

## 8. Logos institucionales

### 8.1. Cómo añadirlos

Usa `--logo` una vez por cada logo (máximo **3**):

```bash
python generar_certificados_fis.py datos.csv \
    --logo logos/mined.png \
    --logo logos/universidad.png \
    --logo logos/comite.png
```

Se colocan **centrados horizontalmente**, repartidos de forma equidistante:

- 1 logo → centrado.
- 2 logos → izquierda y derecha.
- 3 logos → izquierda, centro y derecha.

### 8.2. Recomendaciones

| Aspecto | Recomendación |
|---|---|
| Formato | PNG (preferible) o JPG |
| Transparencia | **PNG con fondo transparente** para mejor acabado |
| Resolución | 300–600 px de ancho |
| Proporción | Horizontal (escudos y logos suelen quedar bien) |
| Tamaño máximo en el PDF | 120 × 62 pt (~4.2 × 2.2 cm) |

Si el logo no respeta su proporción, el script lo escala automáticamente sin deformarlo.

---

## 9. Pies de firma

### 9.1. Estructura

Cada `--firma` sigue el formato:

```
"Nombre Completo|Cargo|ruta/imagen.png"
```

- **Nombre:** se muestra en negrita.
- **Cargo:** se muestra en cursiva debajo del nombre.
- **Imagen:** opcional (firma escaneada). Si se omite, solo se dibuja la línea.

### 9.2. Ejemplos

```bash
# Firma completa con imagen
python generar_certificados_fis.py datos.csv \
    --firma "Dra. Ana Rodríguez|Presidenta del Comité Organizador|firmas/presidenta.png"

# Firma solo con cargo (sin nombre, sin imagen)
python generar_certificados_fis.py datos.csv \
    --firma "Comité Organizador"

# Firma con nombre y cargo, sin imagen
python generar_certificados_fis.py datos.csv \
    --firma "Lic. Pedro Martínez|Director Provincial de Educación"

# Varias firmas
python generar_certificados_fis.py datos.csv \
    --firma "Dra. Ana Rodríguez|Presidenta del Comité|firmas/presidenta.png" \
    --firma "Lic. Pedro Martínez|Director Provincial de Educación|firmas/director.png" \
    --firma "MSc. Laura González|Secretaria Docente"
```

### 9.3. Distribución automática

| N.º de firmas | Distribución |
|---|---|
| 1 | 1 fila, centrada |
| 2 | 1 fila |
| 3 | 1 fila |
| 4 | 2 filas (2 + 2) |
| 5 | 2 filas (3 + 2) |
| 6 | 2 filas (3 + 3) |

**Máximo:** 6 firmas. Más de 6 → error del parser.

### 9.4. Consejos para imágenes de firma

- **PNG con fondo transparente** es lo ideal.
- Si usas un escaneo con **fondo blanco**, el script lo vuelve transparente automáticamente (detecta píxeles claros y los hace transparentes).
- Si la firma es muy grande, se escala para no superar 190 pt de ancho ni 44 pt de alto.
- Formato recomendado: PNG, ~600 × 200 px.

### 9.5. Sin firmas

```bash
python generar_certificados_fis.py datos.csv --sin-firmas
```

---

## 10. Marca de agua

Cada asignatura tiene **una marca de agua vectorial propia** que se dibuja en gris muy claro:

| Asignatura | Textura de fondo | Dibujos grandes |
|---|---|---|
| Informática | Dígitos `0 1` | Globos, portátil con `</>`, `{ }` |
| Matemática | Números y operadores `π √ ∑ ∞ ≠` | π gigante, √, ∑, onda seno, círculo, triángulo |
| Física | Fórmulas `E=mc² F=ma v=d/t λ Ω` | Átomos, rayo, onda, péndulo |
| Química | Fórmulas `H₂O CO₂ NaCl CH₄ NH₃ pH ⇌` | Hexágonos moleculares, matraces con burbujas |
| Biología | Secuencias `A T C G U` | Doble hélice de ADN, hojas, células, flores |
| Geografía | Coordenadas `23°08'N 82°22'W` | Globos terráqueos, rosa de los vientos, cordilleras, pins |
| Español | Alfabeto con `Ñ á é í ó ú` | Libro abierto, pluma, bocadillo, comillas `« »` |
| Historia | Fechas y siglos `1492 a.C. s. XV` | Columnas griegas, relojes de arena, pergaminos, laurel |
| Inglés | Alfabeto y puntuación `? ! . , ' "` | Bloques ABC, "Hello!", `?`, `!`, comillas, `Aa` |

### 10.1. Quitar la marca de agua

```bash
python generar_certificados_fis.py datos.csv --sin-marca-agua
```

### 10.2. Usar tus propias imágenes como marca de agua

```bash
python generar_certificados_fis.py datos.csv \
    --marca-agua imagenes/atomo_grande.png
```

Puedes pasar hasta **N imágenes** (se reparten según una cuadrícula automática). Se convierten a gris claro con la opacidad indicada.

```bash
python generar_certificados_fis.py datos.csv \
    --marca-agua img1.png \
    --marca-agua img2.png \
    --opacidad-marca 0.10
```

| N.º de imágenes | Posición |
|---|---|
| 1 | Centro, grande |
| 2 | Diagonal (arriba-izq / abajo-der) |
| 3 | Triangular (arriba, centro, abajo) |
| 4+ | Cuadrícula automática |

### 10.3. Opacidad

| Valor | Efecto |
|---|---|
| `0.05` | Muy tenue (casi invisible) |
| `0.16` | **Por defecto** |
| `0.30` | Visible, pero discreta |
| `0.50` | Muy marcada (no recomendado) |

---

## 11. Ejemplos completos por asignatura

### 11.1. Informática

```bash
# Participación
python generar_certificados_inf.py datos/participantes_inf.csv -o salida/certificados_inf \
    --fecha 2026-04-18 \
    --logo logos/mined.png --logo logos/uci.png \
    --firma "Dra. Ana Rodríguez|Presidenta del Comité|firmas/presidenta.png" \
    --firma "Lic. Pedro Martínez|Director Provincial de Educación"

# Medallas
python generar_premios_inf.py datos/ganadores_inf.csv -o salida/premios_inf \
    --agrupar-por-medalla --fecha 2026-04-18
```

### 11.2. Matemática

```bash
python generar_certificados_mat.py datos/participantes_mat.csv -o salida/certificados_mat \
    --fecha 2026-04-18

python generar_premios_mat.py datos/ganadores_mat.csv -o salida/premios_mat \
    --agrupar-por-medalla --fecha 2026-04-18
```

### 11.3. Física

```bash
python generar_certificados_fis.py datos/participantes_fis.csv -o salida/certificados_fis \
    --fecha 2026-04-18

python generar_premios_fis.py datos/ganadores_fis.csv -o salida/premios_fis \
    --agrupar-por-medalla --fecha 2026-04-18
```

### 11.4. Química

```bash
python generar_certificados_qui.py datos/participantes_qui.csv -o salida/certificados_qui
python generar_premios_qui.py datos/ganadores_qui.csv -o salida/premios_qui --agrupar-por-medalla
```

### 11.5. Biología

```bash
python generar_certificados_bio.py datos/participantes_bio.csv -o salida/certificados_bio
python generar_premios_bio.py datos/ganadores_bio.csv -o salida/premios_bio --agrupar-por-medalla
```

### 11.6. Geografía

```bash
python generar_certificados_geo.py datos/participantes_geo.csv -o salida/certificados_geo
python generar_premios_geo.py datos/ganadores_geo.csv -o salida/premios_geo --agrupar-por-medalla
```

### 11.7. Español

```bash
python generar_certificados_esp.py datos/participantes_esp.csv -o salida/certificados_esp
python generar_premios_esp.py datos/ganadores_esp.csv -o salida/premios_esp --agrupar-por-medalla
```

### 11.8. Historia

```bash
python generar_certificados_his.py datos/participantes_his.csv -o salida/certificados_his
python generar_premios_his.py datos/ganadores_his.csv -o salida/premios_his --agrupar-por-medalla
```

### 11.9. Inglés

```bash
python generar_certificados_ing.py datos/participantes_ing.csv -o salida/certificados_ing \
    --modalidad "English Language Competition"

python generar_premios_ing.py datos/ganadores_ing.csv -o salida/premios_ing \
    --modalidad "English Language Competition" --agrupar-por-medalla
```

---

## 12. Automatización y lotes

### 12.1. Script Bash (Linux / macOS)

`generar_todo.sh`:

```bash
#!/usr/bin/env bash
set -e

FECHA="2026-04-18"
OUT="salida"
DATOS="datos"

declare -A ASIG=(
    [inf]="Informática"
    [mat]="Matemática"
    [fis]="Física"
    [qui]="Química"
    [bio]="Biología"
    [geo]="Geografía"
    [esp]="Español"
    [his]="Historia"
    [ing]="Inglés"
)

for suf in "${!ASIG[@]}"; do
    echo "▶ Procesando ${ASIG[$suf]}..."
    
    # Participación
    python "generar_certificados_${suf}.py" \
        "${DATOS}/participantes_${suf}.csv" \
        -o "${OUT}/certificados_${suf}" \
        --fecha "${FECHA}"
    
    # Medallas
    python "generar_premios_${suf}.py" \
        "${DATOS}/ganadores_${suf}.csv" \
        -o "${OUT}/premios_${suf}" \
        --fecha "${FECHA}" \
        --agrupar-por-medalla
done

echo "✅ Todo listo en '${OUT}/'"
```

```bash
chmod +x generar_todo.sh
./generar_todo.sh
```

### 12.2. Script Python maestro

`generar_todo.py`:

```python
#!/usr/bin/env python3
"""Genera todos los certificados en un solo paso."""
import subprocess
from pathlib import Path

FECHA = "2026-04-18"
DATOS = Path("datos")
OUT = Path("salida")

ASIGNATURAS = {
    "inf": "Informática",
    "mat": "Matemática",
    "fis": "Física",
    "qui": "Química",
    "bio": "Biología",
    "geo": "Geografía",
    "esp": "Español",
    "his": "Historia",
    "ing": "Inglés",
}

def run(cmd):
    print("▶", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)

for suf, nombre in ASIGNATURAS.items():
    print(f"\n=== {nombre} ===")
    
    csv_part = DATOS / f"participantes_{suf}.csv"
    if csv_part.exists():
        run(["python", f"generar_certificados_{suf}.py", csv_part,
             "-o", OUT / f"certificados_{suf}", "--fecha", FECHA])
    else:
        print(f"  (sin CSV de participación: {csv_part})")
    
    csv_med = DATOS / f"ganadores_{suf}.csv"
    if csv_med.exists():
        run(["python", f"generar_premios_{suf}.py", csv_med,
             "-o", OUT / f"premios_{suf}", "--fecha", FECHA,
             "--agrupar-por-medalla"])
    else:
        print(f"  (sin CSV de medallas: {csv_med})")

print("\n✅ Todo generado en 'salida/'")
```

### 12.3. `Makefile` (opcional)

```makefile
FECHA := 2026-04-18
DATOS := datos
OUT   := salida

SUFIJOS := inf mat fis qui bio geo esp his ing

.PHONY: todo $(SUFIJOS) limpiar

todo: $(SUFIJOS)

$(SUFIJOS):
	@echo "▶ $@"
	python generar_certificados_$@.py $(DATOS)/participantes_$@.csv -o $(OUT)/certificados_$@ --fecha $(FECHA)
	python generar_premios_$@.py      $(DATOS)/ganadores_$@.csv      -o $(OUT)/premios_$@      --fecha $(FECHA) --agrupar-por-medalla

limpiar:
	rm -rf $(OUT)
```

```bash
make          # genera todo
make fis      # solo Física
make limpiar  # borra salida
```

### 12.4. Concatenar PDFs (opcional)

Si quieres un **único PDF con todos los certificados de todas las asignaturas**, usa `pdfunite` (Poppler):

```bash
pdfunite salida/premios_*/todos_los_certificados_*.pdf premios_todos.pdf
pdfunite salida/certificados_*/todos_los_certificados_*.pdf certificados_todos.pdf
```

O con `pypdf`:

```python
from pypdf import PdfMerger
from pathlib import Path

def unir(patron, salida):
    merger = PdfMerger()
    for pdf in sorted(Path("salida").glob(patron)):
        merger.append(pdf)
    merger.write(salida)
    merger.close()

unir("premios_*/todos_los_certificados_*.pdf", "premios_todos.pdf")
unir("certificados_*/todos_los_certificados_*.pdf", "certificados_todos.pdf")
```

---

## 13. Solución de problemas

### ❌ "No se encontró DejaVu; se usan fuentes estándar"

**Causa:** faltan las fuentes DejaVu.

**Solución:**
1. Instalar el paquete del sistema (`fonts-dejavu` en Linux).
2. O copiar los `.ttf` a una carpeta `fuentes/` junto a los scripts.
3. Consecuencia si no se resuelve: caracteres especiales (`π`, `√`, `∑`, `⇌`, `«»`) pueden mostrarse como cuadrados.

---

### ❌ "No existe el CSV: datos/participantes.csv"

**Causa:** la ruta al CSV no existe.

**Solución:**
1. Verifica la ruta con `ls datos/` (Linux) o `dir datos\` (Windows).
2. Si el archivo está en la misma carpeta que el script, usa solo el nombre: `participantes.csv`.

---

### ❌ "El CSV necesita una columna 'nombre'"

**Causa:** la cabecera del CSV no tiene ninguna columna reconocible.

**Solución:** comprueba que la primera fila tenga al menos una de estas columnas: `nombre`, `nombres`, `nombre completo`, `name`, `estudiante`, `participante`.

Si el CSV **no** tiene cabecera, elimina también la primera fila de datos o asegúrate de que la primera columna sea el nombre.

---

### ❌ "No existe la imagen: logos/mined.png"

**Causa:** ruta a un logo o firma incorrecta.

**Solución:** verifica con `ls logos/` y usa rutas relativas correctas. Recuerda que `--logo` acepta varias rutas; revisa que **todas** existan.

---

### ❌ Acentos aparecen como `Ã¡`, `Ã©` o `?`

**Causa:** el CSV está guardado en una codificación no soportada o mixta.

**Solución:**
- Guardar el CSV como **UTF-8** (sin BOM es lo ideal, con BOM también se acepta).
- O guardarlo como **Windows-1252** (Excel "CSV (delimitado por comas)" por defecto).
- Evitar codificaciones exóticas como UTF-16.

En Excel/LibreOffice: `Archivo → Guardar como → CSV UTF-8`.

---

### ❌ "Máximo 3 logos" / "Máximo 6 firmas"

**Causa:** se superó el límite.

**Solución:** reduce el número de `--logo` o `--firma`.

---

### ❌ Los logos se ven pixelados

**Causa:** resolución baja.

**Solución:** usa PNG de al menos 300 px de ancho. Evita capturas de pantalla; usa los logos originales.

---

### ❌ Los textos se solapan con las firmas

**Causa:** nombres muy largos + muchos textos antes del evento.

**Solución:**
- El script emite un aviso por `stderr`: `Aviso: el texto de '...' queda muy cerca de las firmas.`
- Opciones:
  - Acortar `--evento` o `--modalidad`.
  - Usar `--sin-firmas` si no son necesarias.
  - Reducir a ≤3 firmas (una sola fila).

---

### ❌ "Permission denied" al ejecutar el script (Linux/macOS)

**Solución:**

```bash
chmod +x generar_certificados_fis.py
./generar_certificados_fis.py datos.csv
```

O ejecutar con `python3`:

```bash
python3 generar_certificados_fis.py datos.csv
```

---

### ❌ "UnicodeDecodeError" al leer el CSV

**Causa:** el CSV está en UTF-16, Shift-JIS o una codificación similar.

**Solución:** abrir el CSV en un editor de texto, guardarlo como **UTF-8** y volver a ejecutar.

---

## 14. Preguntas frecuentes

### ¿Puedo generar solo algunas asignaturas?

Sí, ejecuta solo los scripts que necesites:

```bash
python generar_certificados_fis.py participantes_fis.csv
python generar_premios_fis.py ganadores_fis.csv --agrupar-por-medalla
```

---

### ¿Puedo cambiar el diseño del marco?

Sí. Abre el script correspondiente y edita las funciones `marco()`, `ornamento()` y `rombo()`. Cada asignatura comparte esas funciones, así que los cambios son consistentes dentro de un mismo archivo.

---

### ¿Puedo cambiar la marca de agua por asignatura?

Sí. Cada script tiene una sección claramente marcada:

```python
# --------------------------------------------------------------------------
# Marca de agua alegórica a <ASIGNATURA>
# --------------------------------------------------------------------------
```

Dentro encontrarás `marca_agua()` y todos sus helpers. Puedes editar libremente para añadir o quitar dibujos.

---

### ¿Puedo usar las mismas firmas para todas las asignaturas?

Sí. Basta con repetir el bloque `--firma …` en cada ejecución, o crear un script de automatización (ver sección 12).

---

### ¿Cómo imprimo correctamente los PDFs?

- **Tamaño de papel:** A4 vertical.
- **Escala:** 100% (no "ajustar al área").
- **Márgenes:** ninguno o mínimo.
- **Doble cara:** activado si imprimes varios certificados.
- **Papel:** mate de 200–250 g/m² da mejor acabado, sobre todo con medallas.

---

### ¿Los certificados son imprimibles en blanco y negro?

Sí, aunque el marco y la medalla se ven menos vistosos. La marca de agua es gris muy claro, así que no interfiere con el texto.

---

### ¿Cómo genero un único PDF con todos los certificados de una asignatura?

Por defecto **ya se genera** un archivo `todos_los_certificados_<sufijo>.pdf` en cada carpeta de salida.

Para combinar **varias asignaturas**, ver sección 12.4 (concatenar PDFs).

---

### ¿Puedo usar esto para otras asignaturas?

Sí. La forma más rápida es copiar un script existente y cambiar la sección de marca de agua. Los scripts están estructurados de forma idéntica para facilitar esta tarea.

---

### ¿Cómo actualizo un solo certificado sin regenerar todos?

No hay generación selectiva por nombre, pero puedes:

1. Copiar el CSV completo a uno temporal con solo la fila del participante que quieres actualizar.
2. Ejecutar el script con ese CSV y `-o carpeta_individual/`.
3. Copiar el PDF generado al lugar correspondiente.

---

### ¿Cómo puedo borrar todos los PDFs generados?

```bash
# Linux / macOS
rm -rf salida/

# Windows PowerShell
Remove-Item -Recurse -Force salida\
```

O con `make limpiar` si usaste el `Makefile` de la sección 12.3.

---

## 📌 Resumen de buenas prácticas

1. ✅ Guarda los CSV en **UTF-8**.
2. ✅ Verifica **rutas relativas** de logos y firmas antes de ejecutar.
3. ✅ Usa **PNG con transparencia** para logos y firmas.
4. ✅ Mantén los nombres de archivo **sin espacios** (usa `_`).
5. ✅ Versiona los CSV junto con los PDFs de cada edición.
6. ✅ Automatiza con `generar_todo.sh` / `generar_todo.py` / `Makefile`.
7. ✅ Revisa el primer PDF de cada lote antes de imprimir todo.
8. ✅ Conserva los PDFs originales; imprime copias.

---

## 🧭 Estructura de un certificado (resumen visual)

```
┌─────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────┐  │
│  │                                               │  │
│  │         [LOGOS INSTITUCIONALES]               │  │
│  │                                               │  │
│  │           [ENCABEZADO OPCIONAL]               │  │
│  │                                               │  │
│  │              CERTIFICADO                      │  │
│  │           MEDALLA DE ORO                      │  │
│  │              ───◆───                          │  │
│  │                                               │  │
│  │              [MEDALLA]                        │  │
│  │                                               │  │
│  │            Se otorga a                        │  │
│  │      NOMBRE DEL PARTICIPANTE                  │  │
│  │      ─────────────────────                    │  │
│  │      Estudiante del grado onceno              │  │
│  │        en representación de                   │  │
│  │      NOMBRE DEL CENTRO                        │  │
│  │                                               │  │
│  │   por haber obtenido la medalla de oro en el  │  │
│  │      CONCURSO PROVINCIAL DE ...               │  │
│  │      en la modalidad de ...,                  │  │
│  │      celebrado en Matanzas el ...             │  │
│  │                                               │  │
│  │   ───────    ───────    ───────               │  │
│  │    Firma      Firma      Firma                │  │
│  │    Cargo      Cargo      Cargo                │  │
│  │                                               │  │
│  │                   N.º 001                     │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
        ↑ marca de agua alusiva a la asignatura
```

---

**Fin del README** — ¡buena suerte con los certificados! 🎓