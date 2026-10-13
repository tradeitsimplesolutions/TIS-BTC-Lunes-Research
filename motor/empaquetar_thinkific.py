"""
Empaqueta la ficha y el manual avanzado para Thinkific (lección multimedia: un .zip con index.html por página).

Dentro de Thinkific cada página se muestra incrustada (iframe) y vive en su propia lección, así que:
  · los enlaces entre la ficha y el manual pasan a ser URLs absolutas (las de las lecciones o las de GitHub Pages),
  · los enlaces externos (GitHub, TradingView, papers, exchanges) se abren en una pestaña nueva:
    GitHub y TradingView no se dejan mostrar dentro de un iframe,
  · las anclas internas (#reglas, #donde…) siguen igual,
  · la librería de la superficie 3D (Plotly) va dentro del zip en lugar de cargarse de internet.

Uso:
  python motor/empaquetar_thinkific.py
  python motor/empaquetar_thinkific.py --ficha-url URL_LECCION_FICHA --manual-url URL_LECCION_MANUAL
Salida: dist/thinkific/btc-lunes-ficha.zip y dist/thinkific/btc-lunes-validacion.zip
"""
import argparse, re, zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GUIA, DIST = RAIZ / "guia", RAIZ / "dist" / "thinkific"
PAGES = "https://tradeitsimplesolutions.github.io/TIS-BTC-Lunes-Research/guia/"


def adaptar(html, urls):
    def cambiar(m):
        tag = m.group(0); href = m.group(1)
        if href.startswith("#") or href.startswith("data:") or href.startswith("javascript:"):
            return tag
        page, sep, anchor = href.partition("#")
        if page in urls:                                           # enlace a la otra página de la guía
            nuevo = urls[page] + (sep + anchor if anchor else "")
            tag = tag.replace(f'href="{href}"', f'href="{nuevo}"')
        if "target=" not in tag:                                    # todo lo que sale de la página, en pestaña nueva
            tag = tag[:-1] + ' target="_blank" rel="noopener">'
        return tag
    return re.sub(r'<a\b[^>]*\bhref="([^"]+)"[^>]*>', cambiar, html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ficha-url", default=PAGES + "btc-lunes-ficha.html")
    ap.add_argument("--manual-url", default=PAGES + "btc-lunes-validacion.html")
    a = ap.parse_args()
    urls = {"btc-lunes-ficha.html": a.ficha_url, "btc-lunes-validacion.html": a.manual_url}
    DIST.mkdir(parents=True, exist_ok=True)
    for nombre in ["btc-lunes-ficha.html", "btc-lunes-validacion.html"]:
        html = adaptar((GUIA / nombre).read_text(encoding="utf-8"), urls)
        extra = {}
        cdn = re.search(r'<script[^>]*src="https://cdn\.plot\.ly/[^"]+"[^>]*>', html)
        if cdn:                                                     # Plotly local, junto al index.html
            import plotly
            js = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"
            html = html.replace(cdn.group(0), '<script charset="utf-8" src="plotly.min.js">'); extra["plotly.min.js"] = js.read_bytes()
        z = DIST / nombre.replace(".html", ".zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            f.writestr("index.html", html)
            for k, v in extra.items(): f.writestr(k, v)
        print(f"{z.relative_to(RAIZ)} · index.html {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
