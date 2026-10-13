"""
Piezas comunes de las páginas (configuración, utilidades, CSS, plantilla). Importado por construir_html.py y pagina_ficha.py.

Construye las dos páginas de la guía a partir de resultados/metricas.json y resultados/graficos/*.png:
  guia/btc-lunes-ficha.html        → la estrategia explicada de principio a fin (para el alumno)
  guia/btc-lunes-validacion.html   → la validación completa, fase a fase

Todo autocontenido (imágenes incrustadas), sin dependencias externas. Uso: python motor/construir_html.py
"""
import base64, html, io, json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RES, G, GUIA = RAIZ / "resultados", RAIZ / "resultados" / "graficos", RAIZ / "guia"

# ------------------------------------------------------------------ configuración editable
REPO_URL = "https://github.com/tradeitsimplesolutions/TIS-BTC-Lunes-Research"
PINE_URL = "https://es.tradingview.com/script/crKuDZ77/"   # script v3 publicado en TradingView
INSTAGRAM = "https://instagram.com/mariellangsaez"
# Bibliografía real (comprobada el 2026-10-02)
PAPERS = [
    dict(autores="Caporale, G. M. y Plastun, A.", ano=2019, titulo="The day of the week effect in the cryptocurrency market", revista="Finance Research Letters, 31, 258–269",
         url="https://doi.org/10.1016/j.frl.2018.11.012", nota="Con datos de 2013–2017, Bitcoin es la única cripto con un efecto día de la semana: los lunes rinden significativamente más que el resto. El punto de partida."),
    dict(autores="Aharon, D. Y. y Qadan, M.", ano=2019, titulo="Bitcoin and the day-of-the-week effect", revista="Finance Research Letters, 31, 415–424",
         url="https://www.researchgate.net/publication/329516639_Bitcoin_and_the_Day-of-the-Week_Effect", nota="2010–2017: los lunes tienen más retorno y más volatilidad que los demás días."),
    dict(autores="Baur, D. G., Cahill, D., Godfrey, K. y Liu, Z. F.", ano=2019, titulo="Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume", revista="Finance Research Letters, 31, 78–92",
         url="https://www.researchgate.net/publication/332404798_Bitcoin_Time-of-Day_Day-of-Week_and_Month-of-Year_Effects_in_Returns_and_Trading_Volume", nota="Efectos de hora y de día en un mercado que no cierra nunca: la actividad sigue el horario de las bolsas tradicionales."),
    dict(autores="Kinateder, H. y Papavassiliou, V. G.", ano=2021, titulo="Calendar effects in Bitcoin returns and volatility", revista="Finance Research Letters, 38, 101420",
         url="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3517291", nota="2013–2019: el efecto día de la semana clásico ya no aparece en los retornos, solo en la volatilidad (menor el fin de semana, mayor al empezar la semana). El primer aviso de desgaste."),
]
EXCH_URLS = dict(binance="https://www.binance.com/en/fee/schedule", coinbase="https://www.coinbase.com/advanced-fees", quantfury="https://quantfury.com", exness="https://www.exness.com/")
FECHA_TARIFAS = "2026-10-02"

M = json.loads((RES / "metricas.json").read_text(encoding="utf-8"))
SEM = json.loads((RES / "equity_semanal.json").read_text(encoding="utf-8")) if (RES / "equity_semanal.json").exists() else None
CB = json.loads((RES / "metricas_coinbase.json").read_text(encoding="utf-8")) if (RES / "metricas_coinbase.json").exists() else None
REC = json.loads((RES / "reconciliacion_tradingview.json").read_text(encoding="utf-8")) if (RES / "reconciliacion_tradingview.json").exists() else None
REC_V3 = json.loads((RES / "reconciliacion_tradingview_v3.json").read_text(encoding="utf-8")) if (RES / "reconciliacion_tradingview_v3.json").exists() else None
REC_MT5 = json.loads((RES / "reconciliacion_mt5.json").read_text(encoding="utf-8")) if (RES / "reconciliacion_mt5.json").exists() else None
PINE_V3 = (RAIZ / "codigo" / "TIS_BTC_Lunes_v3.pine").read_text(encoding="utf-8", errors="ignore") if (RAIZ / "codigo" / "TIS_BTC_Lunes_v3.pine").exists() else ""
EA_MT5 = (RAIZ / "codigo" / "TIS_BTC_Lunes_v3.mq5").read_text(encoding="utf-8", errors="ignore") if (RAIZ / "codigo" / "TIS_BTC_Lunes_v3.mq5").exists() else ""
PINE_V1 = (RAIZ / "codigo" / "TIS_BTC_Lunes_v1_original.pine").read_text(encoding="utf-8", errors="ignore") if (RAIZ / "codigo" / "TIS_BTC_Lunes_v1_original.pine").exists() else ""
EX = M["meta"]["exchanges"]; ROBOT = M["meta"]["robot"]


# ------------------------------------------------------------------ utilidades
def pct(x, d=1, signo=False):
    if x is None: return "—"
    s = f"{x*100:+.{d}f}" if signo else f"{x*100:.{d}f}"
    return s.replace(".", ",").replace("-", "−") + " %"


def num(x, d=2):
    if x is None: return "—"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def fecha(s):
    if not s: return "—"
    y, m, d = s.split("-"); meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{int(d)} {meses[int(m)-1]} {y}"


def img(nombre):
    from PIL import Image
    im = Image.open(G / nombre).convert("RGB"); buf = io.BytesIO(); im.save(buf, "WEBP", quality=82)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def logo():
    p = RAIZ / "guia" / "logo_tis.png"
    if not p.exists(): return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def fig(nombre, caption):
    return f'<figure><img src="{img(nombre)}" alt="{html.escape(caption)}"><figcaption>{caption}</figcaption></figure>'


def superficie_4d(rp):
    """Superficie 3D interactiva (Plotly) sobre los dos parámetros de la regla: longitud del ATR × suelo del percentil.
    Altura y color = Profit Factor al 40 %. Botones: construcción 14 bps · construcción 28 bps · validación (cada una con su eje). Necesita internet para plotly.js (CDN)."""
    import plotly.graph_objects as go
    LS, PS = rp["atr_lens"], rp["pcts"]; iL, iP = LS.index(M["meta"]["atr_len"]), PS.index(M["meta"]["pct_min"]); xs = [int(round(p_ * 100)) for p_ in PS]
    vistas = [("pf_is_14", "Construcción · 14 bps"), ("pf_is_28", "Construcción · doble coste"), ("pf_oos_14", "Validación · 14 bps")]
    # Escala de color: por debajo de 1 rojo, 1–1,3 naranja/amarillo, 1,3 verde claro, 2 o más verde intenso
    escala = [[0, "#c8512f"], [0.167, "#f4805e"], [0.333, "#f5d76e"], [0.417, "#9ee3b8"], [0.667, "#2fbf71"], [1, "#0b6e3e"]]
    fig = go.Figure(); rangos = []
    for i_, (k, nom) in enumerate(vistas):
        Z = [[(v if v is not None else None) for v in fila] for fila in rp[k]]; N = rp["n_is"]; C = rp["mdd_is"]
        vals = [v for fila in Z for v in fila if v is not None]; rangos.append([0, max(vals) * 1.08])   # el eje empieza en 0 y un plano marca el empate (PF 1): así el relieve se ve a su escala real
        txt = [[f"ATR {LS[a]} · percentil {xs[b]}<br><b>Profit Factor {Z[a][b]:.2f}</b>" + (f"<br>Drawdown máx. {abs(C[a][b])*100:.1f} % · {N[a][b]} operaciones" if k != "pf_oos_14" and C[a][b] is not None else "<br>(validación: solo comprobación)") for b in range(len(PS))] for a in range(len(LS))]
        fig.add_trace(go.Surface(x=xs, y=LS, z=Z, cmin=0.8, cmax=2.0, colorscale=escala,
                                 colorbar=dict(title="Profit<br>Factor", thickness=14, len=0.6, tickvals=[0.8, 1, 1.3, 1.6, 2], ticktext=["0,8", "1", "1,3", "1,6", "≥ 2"]), text=txt, hoverinfo="text", name=nom, visible=(i_ == 0), opacity=0.97,
                                 contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="#132620", project_z=True, width=2)), lighting=dict(ambient=0.75, diffuse=0.7, specular=0.15, roughness=0.6)))
        fig.add_trace(go.Surface(x=[xs[0], xs[-1]], y=[LS[0], LS[-1]], z=[[1, 1], [1, 1]], showscale=False, opacity=0.35, colorscale=[[0, "#c8512f"], [1, "#c8512f"]], hoverinfo="skip", name="empate", visible=(i_ == 0), showlegend=False))
        fig.add_trace(go.Scatter3d(x=[xs[iP]], y=[LS[iL]], z=[Z[iL][iP] + 0.03], mode="markers+text", text=["la regla"], textposition="top center",
                                   textfont=dict(color="#132620", size=13, family="system-ui"), marker=dict(size=8, color="#132620", line=dict(color="white", width=2)), hoverinfo="text",
                                   hovertext=f"La regla · ATR {LS[iL]} · percentil {xs[iP]} · PF {Z[iL][iP]:.2f}", name="la regla", visible=(i_ == 0), showlegend=False))
    botones = [dict(label=nom, method="update", args=[{"visible": [j_ // 3 == i_ for j_ in range(3 * len(vistas))]}, {"scene.zaxis.range": rangos[i_]}]) for i_, (k, nom) in enumerate(vistas)]
    fig.update_layout(height=680, margin=dict(l=0, r=0, t=56, b=0), paper_bgcolor="white", font=dict(family="system-ui, Segoe UI, Roboto, sans-serif", color="#132620"),
                      scene=dict(xaxis=dict(title="suelo del percentil", tickvals=xs, ticktext=[f"p{x}" for x in xs], backgroundcolor="#f5fbf8", gridcolor="#e2ede8"),
                                 yaxis=dict(title="longitud del ATR (velas)", tickvals=LS, backgroundcolor="#f5fbf8", gridcolor="#e2ede8"),
                                 zaxis=dict(title="Profit Factor (40 %)", range=rangos[0], backgroundcolor="#ffffff", gridcolor="#e2ede8"),
                                 camera=dict(eye=dict(x=1.45, y=1.55, z=0.8), center=dict(x=0, y=0, z=-0.15)), aspectratio=dict(x=1.2, y=1, z=0.6), domain=dict(y=[0, 1])),
                      updatemenus=[dict(type="buttons", direction="right", x=0, y=1.0, xanchor="left", yanchor="bottom", showactive=True, buttons=botones, bgcolor="#eef6f1", bordercolor="#e2ede8", font=dict(size=11), pad=dict(r=4, t=0, b=0))], modebar=dict(orientation="v"))
    div = fig.to_html(include_plotlyjs="cdn", full_html=False, div_id="sup4d", config=dict(displayModeBar=True, responsive=True, displaylogo=False, locale="es"))
    return f'<div class="chart" id="sup4d-wrap">{div}<img class="print" src="{img("11_robustez_4d.png")}" alt="Superficie de parámetros"><figcaption style="padding:8px 4px 0">El eje vertical empieza en 0 y el plano rojo translúcido es el empate (Profit Factor 1): toda la superficie flota por encima de él, y el relieve se ve a su escala real. Gírala con el ratón y pasa el cursor por cada punto para ver sus parámetros, su Profit Factor, su drawdown y sus operaciones. Los dos ejes son los dos parámetros de la regla: cuántas velas mide el ATR y qué suelo del percentil se exige ({len(LS)} × {len(PS)} = {len(LS) * len(PS)} combinaciones). La altura y el color son el Profit Factor: por debajo de 1,3 amarillo o rojo; 1,3 verde; 2 o más, verde intenso. Lo que buscamos es que el punto negro (la regla) esté en una zona llana y rentable, rodeado de vecinos parecidos, no en un pico aislado. Los botones cambian a doble coste y a la validación, cada una con su propio eje.</figcaption></div>'


def kpi(valor, label, sub="", tono=""):
    return f'<div class="kpi {tono}"><div class="v">{valor}</div><div class="l">{label}</div>{f"<div class=s>{sub}</div>" if sub else ""}</div>'


def check(ok, texto, detalle=""):
    ic = "✓" if ok else ("✕" if ok is False else "·")
    cl = "ok" if ok else ("ko" if ok is False else "na")
    return f'<li class="chk {cl}"><span class="ic">{ic}</span><div><b>{texto}</b>{f"<br><span class=d>{detalle}</span>" if detalle else ""}</div></li>'


import re as _re
_RE_PF = _re.compile(r"^(?:<b>)?PF\s+(−?\d+,\d+)"); _RE_NUM = _re.compile(r"^(?:<b>)?([+−])(\d+,\d+) %"); _RE_SOLO = _re.compile(r"^(?:<b>)?(\d+,\d+)(?:</b>)?$")


def _clase_celda(c, col_pf):
    """Verde/rojo tenue según el contenido: 'PF 1,32' (>1 verde, <1 rojo), '+0,51 %' / '−0,20 %', y un número solo en una columna de PF."""
    if not isinstance(c, str): return ""
    m = _RE_PF.match(c)
    if m: return "tpos" if float(m.group(1).replace(",", ".").replace("−", "-")) > 1 else "tneg"
    m = _RE_NUM.match(c)
    if m: return "tpos" if m.group(1) == "+" else "tneg"
    if col_pf:
        m = _RE_SOLO.match(c)
        if m: return "tpos" if float(m.group(1).replace(",", ".")) > 1 else "tneg"
    return ""


def tabla(cab, filas, clase="", color=True):
    th = "".join(f"<th>{c}</th>" for c in cab); pfcols = [("profit factor" in str(c).lower() or str(c).strip().upper().startswith("PF")) for c in cab]
    def td(j, c):
        cl = _clase_celda(c, pfcols[j] if j < len(pfcols) else False) if color else ""
        return f'<td class="{cl}">{c}</td>' if cl else f"<td>{c}</td>"
    tr = "".join(f'<tr class="{f[-1]}">' + "".join(td(j, c) for j, c in enumerate(f[:-1])) + "</tr>" if (isinstance(f, list) and f and isinstance(f[-1], str) and f[-1].startswith("fila-")) else "<tr>" + "".join(td(j, c) for j, c in enumerate(f)) + "</tr>" for f in filas)
    return f'<div class="tw"><table class="{clase}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def gauge(nombre, valor, umbral, fmt, mejor="alto", maximo=None, ok=None):
    """Criterio visual: barra con el valor y la marca del umbral. mejor='alto' (PF ≥ x) o 'bajo' (drawdown < x, se pasan valores positivos)."""
    v, u = float(valor), float(umbral); top = maximo or max(v, u) * 1.35
    ok = (v >= u if mejor == "alto" else v <= u) if ok is None else ok; wv, wu = min(100, v / top * 100), min(100, u / top * 100)
    return f'<div class="gauge {"ok" if ok else "ko"}"><div class="gl"><span class="gi">{"✓" if ok else "✕"}</span><b>{nombre}</b><span class="gv">{fmt(valor)}</span></div><div class="gb"><div class="gf" style="width:{wv:.1f}%"></div><div class="gu" style="left:{wu:.1f}%"><i style="{'left:0' if wu < 10 else ''}">criterio {fmt(umbral)}</i></div></div></div>'


def explica(titulo, puntos):
    return f'<div class="explica"><div class="k">📖 {titulo}</div><ul>{"".join(f"<li>{p_}</li>" for p_ in puntos)}</ul></div>'


def ecg(id_, series, bandas, caption, umbrales=((-1, "#9a5a15"), (-2, "#c8512f")), ylim=(-4, 4), ylabel="z", print_img=None, marcas=None):
    """Gráfico interactivo tipo electrocardiograma (canvas): una o varias series en el tiempo con bandas de salud y hover.
    series: [(clave, nombre, color, [(fecha, valor), ...])]; bandas: [(y0, y1, color, etiqueta)]; marcas: [(fecha, etiqueta, color)]."""
    datos = json.dumps(dict(series=[dict(k=k, n=n, c=c, p=[[f, v] for f, v in pts if v is not None]) for k, n, c, pts in series], bandas=bandas, umbrales=list(umbrales), ylim=list(ylim), ylabel=ylabel, marcas=marcas or []))
    js = """
(function(){const D=%s;const el=document.getElementById('__ID__');const cv=el.querySelector('canvas');const tip=el.querySelector('.tip');const on={};D.series.forEach(s=>on[s.k]=true);
const W=1100,H=360,L=44,R=16,T=16,B=34;cv.width=W;cv.height=H;const ctx=cv.getContext('2d');
const xs=[];D.series.forEach(s=>s.p.forEach(q=>xs.push(new Date(q[0]).getTime())));const x0=Math.min(...xs),x1=Math.max(...xs);const X=t=>L+(t-x0)/(x1-x0)*(W-L-R);const[lo,hi]=D.ylim;const Y=v=>T+(hi-Math.max(lo,Math.min(hi,v)))/(hi-lo)*(H-T-B);
function draw(hx){ctx.clearRect(0,0,W,H);D.bandas.forEach(b=>{ctx.fillStyle=b[2];ctx.fillRect(L,Y(b[1]),W-L-R,Y(b[0])-Y(b[1]));ctx.fillStyle='#3a4b44';ctx.font='bold 11px system-ui';ctx.fillText(b[3],L+6,Y(b[1])+14);});
ctx.strokeStyle='#e2ede8';ctx.lineWidth=1;ctx.fillStyle='#3a4b44';ctx.font='11px system-ui';for(let v=Math.ceil(lo);v<=hi;v++){ctx.beginPath();ctx.moveTo(L,Y(v));ctx.lineTo(W-R,Y(v));ctx.stroke();ctx.fillText((v>0?'+':'')+v,8,Y(v)+4);}
for(let y=new Date(x0).getFullYear()+1;y<=new Date(x1).getFullYear();y++){const tx=X(new Date(y,0,1).getTime());ctx.beginPath();ctx.moveTo(tx,T);ctx.lineTo(tx,H-B);ctx.stroke();ctx.fillText(y,tx-14,H-10);}
D.umbrales.forEach(u=>{ctx.strokeStyle=u[1];ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(L,Y(u[0]));ctx.lineTo(W-R,Y(u[0]));ctx.stroke();ctx.setLineDash([]);});ctx.strokeStyle='#95a29b';ctx.setLineDash([2,3]);ctx.beginPath();ctx.moveTo(L,Y(0));ctx.lineTo(W-R,Y(0));ctx.stroke();ctx.setLineDash([]);
D.marcas.forEach(m=>{const tx=X(new Date(m[0]).getTime());ctx.strokeStyle=m[2];ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(tx,T);ctx.lineTo(tx,H-B);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=m[2];ctx.font='11px system-ui';ctx.fillText(m[1],tx+4,T+12);});
D.series.forEach(s=>{if(!on[s.k])return;ctx.strokeStyle=s.c;ctx.lineWidth=2;ctx.beginPath();s.p.forEach((q,i)=>{const x=X(new Date(q[0]).getTime()),y=Y(q[1]);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();});
if(hx!=null){let best=null;D.series.forEach(s=>{if(!on[s.k])return;s.p.forEach(q=>{const x=X(new Date(q[0]).getTime());if(best==null||Math.abs(x-hx)<Math.abs(best.x-hx))best={x:x,q:q,s:s};});});
if(best){ctx.strokeStyle='#132620';ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(best.x,T);ctx.lineTo(best.x,H-B);ctx.stroke();ctx.setLineDash([]);let t='';D.series.forEach(s=>{if(!on[s.k])return;let q=null;s.p.forEach(p=>{if(q==null||Math.abs(new Date(p[0]).getTime()-new Date(best.q[0]).getTime())<Math.abs(new Date(q[0]).getTime()-new Date(best.q[0]).getTime()))q=p;});if(q){ctx.fillStyle=s.c;ctx.beginPath();ctx.arc(X(new Date(q[0]).getTime()),Y(q[1]),4.5,0,7);ctx.fill();const v=q[1];t+=s.n+': '+(v>0?'+':'')+v.toFixed(2)+(v<=-2?' 🔴':(v<=-1?' 🟡':' 🟢'))+' · ';}});tip.textContent=best.q[0]+' · '+t.slice(0,-3);}}}
el.querySelectorAll('.tog button').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.k;on[k]=!on[k];b.classList.toggle('off',!on[k]);draw(null);}));
cv.addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect();draw((e.clientX-r.left)*W/r.width);});cv.addEventListener('mouseleave',()=>{draw(null);tip.textContent='';});draw(null);})();""".replace("__ID__", id_) % datos
    botones = "".join(f'<button data-k="{k}" style="--c:{c}">{n}</button>' for k, n, c, _ in series)
    pr = f'<img class="print" src="{img(print_img)}" alt="{html.escape(caption)}">' if print_img else ""
    return f'<div class="chart ecg" id="{id_}"><div class="tog">{botones}</div><canvas></canvas><div class="tip"></div>{pr}<figcaption style="padding:8px 4px 0">{caption}</figcaption><script>{js}</script></div>'


def sec(id_, kicker, titulo, lead, cuerpo, clase=""):
    return f'<section id="{id_}" class="{clase}"><div class="wrap"><div class="kicker">{kicker}</div><h2>{titulo}</h2>' \
           f'{f"<p class=lead>{lead}</p>" if lead else ""}{cuerpo}</div></section>'


# ------------------------------------------------------------------ CSS común
CSS = """
:root{--bg:#fff;--panel:#f5fbf8;--panel2:#eef6f1;--line:#e2ede8;--ink:#132620;--sub:#3a4b44;--muted:#6b7a72;--faint:#95a29b;
--brand:#0e9c58;--brand2:#26d97e;--brand-soft:#e6faef;--brand-ink:#0d3d24;--neg:#c8512f;--neg-soft:#fdeee9;--warn:#9a5a15;--warn-soft:#fff5e9;--warn-line:#f0d3ab;
--azul:#2b6cb0;--azul-soft:#e8f0fa;--sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;--mono:"SF Mono",ui-monospace,Consolas,"Roboto Mono",monospace}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;font-family:var(--sans);color:var(--ink);background:var(--bg);line-height:1.55;font-size:17px}
a{color:var(--brand);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
nav.top{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav.top .wrap{display:flex;align-items:center;gap:18px;height:56px}
nav.top img{height:32px;background:var(--brand-ink);padding:5px 9px;border-radius:7px}nav.top .brand{font-weight:800;letter-spacing:.2px;font-size:15px;color:var(--brand-ink);white-space:nowrap}
nav.top .links{display:flex;gap:4px;margin-left:auto;overflow-x:auto;scrollbar-width:none}
nav.top .links a{font-size:13.5px;font-weight:600;color:var(--sub);padding:6px 10px;border-radius:8px;white-space:nowrap}
nav.top .links a:hover{background:var(--panel2);text-decoration:none;color:var(--brand-ink)}
nav.top .links a.cta{background:var(--brand);color:#fff}
header.hero{background:radial-gradient(1200px 500px at 15% -10%,#dcf6e4 0,transparent 60%),radial-gradient(900px 400px at 95% 10%,#e8f0fa 0,transparent 55%),var(--bg);padding:54px 0 34px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--brand)}
h1{font-size:clamp(40px,7vw,68px);line-height:1;margin:8px 0 10px;letter-spacing:-.02em}
h1 small{display:block;font-size:clamp(18px,2.6vw,26px);font-weight:600;color:var(--sub);letter-spacing:0;margin-top:8px}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}
.badge{font-size:13px;font-weight:700;padding:6px 12px;border-radius:999px;background:var(--panel2);color:var(--brand-ink);border:1px solid var(--line)}
.badge.b{background:var(--brand);color:#fff;border-color:var(--brand)}
.hero-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:28px;align-items:end}
.hero .hint{font-size:15px;color:var(--muted);margin-top:14px}
.hero-kpis{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;box-shadow:0 1px 0 rgba(19,38,32,.03)}
.kpi .v{font-size:30px;font-weight:800;letter-spacing:-.02em;color:var(--brand-ink);line-height:1.05}
.kpi.ok .v{color:var(--brand)}.kpi.neg .v{color:var(--neg)}.kpi.azul .v{color:var(--azul)}
.kpi .l{font-size:13px;font-weight:700;color:var(--sub);margin-top:6px}.kpi .s{font-size:12.5px;color:var(--muted);margin-top:2px}
section{padding:54px 0;border-bottom:1px solid var(--line)}section.alt{background:var(--panel)}
.kicker{font-size:12.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--brand)}
h2{font-size:clamp(28px,4vw,38px);line-height:1.1;margin:6px 0 10px;letter-spacing:-.015em}
h3{font-size:20px;margin:26px 0 8px}
p.lead{font-size:19px;color:var(--sub);max-width:820px;margin:0 0 22px}
.hipo{background:linear-gradient(135deg,#0d3d24,#0e9c58);color:#fff;border-radius:20px;padding:34px 36px;margin:10px 0 0;box-shadow:0 12px 40px rgba(14,156,88,.25)}
.hipo .k{font-size:12.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;opacity:.85}
.hipo .t{font-size:clamp(24px,3.4vw,34px);font-weight:800;line-height:1.2;margin:8px 0 12px;letter-spacing:-.01em}
.hipo .w{font-size:17px;opacity:.95;max-width:760px}
.tres{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}
.card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px 22px}
.card h4{margin:0 0 6px;font-size:16px}.card p{margin:0;font-size:15px;color:var(--sub)}
.card .n{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--brand);color:#fff;font-weight:800;font-size:14px;margin-bottom:10px}
.reglas{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:22px}
.regla{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px;border-top:5px solid var(--brand)}
.regla.sal{border-top-color:var(--neg)}.regla.fil{border-top-color:var(--azul)}.regla.no{border-top-color:var(--faint)}
.regla .k{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.regla .t{font-size:22px;font-weight:800;margin:6px 0 6px;letter-spacing:-.01em}.regla p{margin:0;font-size:14.5px;color:var(--sub)}
.params{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:16px}
.param{background:var(--panel2);border-radius:12px;padding:12px 14px}.param .v{font-weight:800;font-size:20px}.param .l{font-size:12.5px;color:var(--muted)}
figure{margin:26px 0 8px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px;overflow:hidden}
figure img{width:100%;height:auto;display:block;border-radius:8px}figcaption{font-size:13.5px;color:var(--muted);padding:10px 4px 2px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:20px}
ul.checks{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:8px}
li.chk{display:flex;gap:12px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-size:15px}
li.chk .ic{flex:0 0 26px;height:26px;border-radius:50%;display:grid;place-items:center;font-weight:900;color:#fff;background:var(--brand)}
li.chk.ko .ic{background:var(--neg)}li.chk.na .ic{background:var(--faint)}li.chk .d{color:var(--muted);font-size:14px}
.nota{background:var(--warn-soft);border:1px solid var(--warn-line);color:var(--warn);border-radius:12px;padding:14px 16px;font-size:15px;margin:18px 0 0}
.nota b{color:inherit}.info{background:var(--azul-soft);border:1px solid #cfdff3;color:#1d3f6b;border-radius:12px;padding:14px 16px;font-size:15px;margin:18px 0 0}
.dos{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px}
.riesgo{border-radius:18px;padding:22px 24px;border:1px solid var(--line);background:#fff}
.riesgo.bajo{border-top:6px solid var(--azul)}.riesgo.medio{border-top:6px solid var(--brand)}
.riesgo h4{margin:0;font-size:20px}.riesgo .sub{color:var(--muted);font-size:14px;margin:2px 0 14px}
.riesgo ul{margin:0 0 14px;padding-left:18px;font-size:15px;color:var(--sub)}.riesgo .mini{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.mini .kpi .v{font-size:22px}
.tw{overflow-x:auto;margin-top:16px}table{border-collapse:collapse;width:100%;font-size:14.5px;background:#fff;border-radius:12px;overflow:hidden}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:var(--panel2);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--sub)}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}tr:last-child td{border-bottom:0}
.chart{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px;margin:26px 0 8px}
.chart .tog{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;align-items:center}
.chart .tog button{font:inherit;font-size:13px;font-weight:700;padding:6px 12px;border-radius:999px;border:2px solid var(--c);background:var(--c);color:#fff;cursor:pointer}
.chart .tog button.off{background:#fff;color:var(--c);opacity:.7}
.chart canvas{width:100%;height:auto;display:block}.chart .tip{font-size:13px;color:var(--sub);min-height:20px;margin-top:6px;font-variant-numeric:tabular-nums}
.chart .print{display:none}
@media print{.chart canvas,.chart .tog,.chart .tip{display:none}.chart .print{display:block;width:100%}}
.ok{color:var(--brand);font-weight:700}.ko{color:var(--neg);font-weight:700}
td.tpos{background:#eaf7ef;color:#0b6e3e;font-weight:600}td.tneg{background:#fcebe6;color:#9c3a21;font-weight:600}tr.fila-neg td{background:#fdf1ee}tr.fila-pos td{background:#f3faf6}tr.fila-regla td{font-weight:800;background:#e6f4ec}
.gauge{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px 14px;margin-top:10px}.gauge .gl{display:flex;align-items:center;gap:10px;font-size:15px}.gauge .gl b{flex:1}.gauge .gv{white-space:nowrap}.gauge .gi{flex:0 0 26px;height:26px;border-radius:50%;display:grid;place-items:center;font-weight:900;color:#fff;background:var(--brand)}
.gauge.ko .gi{background:var(--neg)}.gauge .gv{margin-left:auto;font-weight:900;font-size:19px;color:var(--brand-ink)}.gauge.ko .gv{color:var(--neg)}.gauge .gb{position:relative;height:12px;background:var(--panel2);border-radius:999px;margin-top:12px}
.gauge .gf{height:100%;border-radius:999px;background:var(--brand)}.gauge.ko .gf{background:var(--neg)}.gauge .gu{position:absolute;top:-5px;width:3px;height:22px;background:#132620;border-radius:2px}.gauge .gu i{position:absolute;top:24px;left:-40px;width:120px;font-style:normal;font-size:11px;color:var(--muted);white-space:nowrap}
.gauges{display:grid;grid-template-columns:1fr 1fr;gap:10px 14px;margin-top:18px;padding-bottom:16px}
.explica{background:#fffbf2;border:1px solid #f0d3ab;border-radius:12px;padding:12px 16px;margin:16px 0 0;font-size:14.5px;color:#5a3d12}.explica .k{font-weight:800;margin-bottom:4px;color:#9a5a15}.explica ul{margin:0;padding-left:18px}.explica li{margin:3px 0}
.ecg .tog button.off{opacity:.45}
.pasos{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:22px}
.paso{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 16px 14px;position:relative}
.paso .n{font-size:12px;font-weight:800;color:var(--brand);letter-spacing:.1em}.paso h4{margin:4px 0 6px;font-size:15.5px}.paso p{margin:0;font-size:13.5px;color:var(--sub)}
.paso .aqui{position:absolute;top:12px;right:12px;font-size:11px;font-weight:800;background:var(--brand);color:#fff;border-radius:999px;padding:3px 8px}
.fases{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:18px}
.fase{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;text-align:center}
.fase .n{font-size:12px;font-weight:800;color:var(--muted)}.fase .t{font-weight:800;font-size:15px;margin:2px 0 6px}
.fase .r{display:inline-block;font-size:12.5px;font-weight:800;border-radius:999px;padding:3px 10px;background:var(--brand-soft);color:var(--brand-ink)}
.fase.ko .r{background:var(--neg-soft);color:var(--neg)}
.camino{position:relative;margin:24px 0 0;padding-left:34px;border-left:3px solid var(--line)}
.hito{position:relative;margin-bottom:18px}.hito::before{content:"";position:absolute;left:-43px;top:6px;width:16px;height:16px;border-radius:50%;background:var(--brand);border:3px solid #fff;box-shadow:0 0 0 2px var(--brand)}
.hito .f{font-size:12.5px;font-weight:800;letter-spacing:.08em;color:var(--muted);text-transform:uppercase}.hito h4{margin:2px 0 4px;font-size:17px}.hito p{margin:0;font-size:15px;color:var(--sub)}
details.code{background:#fff;border:1px solid var(--line);border-radius:14px;margin-top:14px;overflow:hidden}
details.code summary{cursor:pointer;padding:16px 18px;font-weight:800;list-style:none;display:flex;align-items:center;gap:12px}
details.code summary::-webkit-details-marker{display:none}details.code summary .tag{font-size:12px;font-weight:800;padding:3px 9px;border-radius:999px;background:var(--panel2);color:var(--sub)}
details.code summary .arrow{margin-left:auto;transition:.2s;color:var(--muted)}details[open].code summary .arrow{transform:rotate(180deg)}
details.code .body{border-top:1px solid var(--line)}details.code .meta{padding:12px 18px;font-size:14px;color:var(--sub);background:var(--panel)}
pre{margin:0;padding:18px;background:#0f1a15;color:#dbe8df;font-family:var(--mono);font-size:12.5px;line-height:1.5;overflow:auto;max-height:520px}
.copiar{float:right;font-size:12px;font-weight:700;padding:5px 10px;border-radius:8px;border:1px solid var(--line);background:#fff;cursor:pointer;color:var(--sub)}
.recursos{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:20px}
.rec{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px 20px}.rec h4{margin:0 0 4px;font-size:16px}.rec p{margin:0 0 10px;font-size:14px;color:var(--sub)}
.btn{display:inline-block;font-weight:800;font-size:14px;padding:9px 14px;border-radius:10px;background:var(--brand);color:#fff}.btn.sec{background:var(--panel2);color:var(--brand-ink)}.btn.off{background:var(--panel2);color:var(--faint);pointer-events:none}
.glos{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}.glos div{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-size:14.5px}.glos b{color:var(--brand-ink)}
footer{padding:36px 0 60px;color:var(--muted);font-size:13.5px}footer .wrap{display:grid;gap:8px}
.cta-final{background:linear-gradient(135deg,#0d3d24,#0e9c58);color:#fff;border-radius:20px;padding:30px 34px;display:flex;align-items:center;gap:24px;justify-content:space-between;flex-wrap:wrap}
.cta-final h3{margin:0 0 4px;font-size:24px}.cta-final p{margin:0;opacity:.9}.cta-final .btn{background:#fff;color:var(--brand-ink)}
.origen{display:grid;grid-template-columns:1.2fr 1fr;gap:20px;margin-top:20px}
.libro{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:10px}.libro b{display:block;font-size:15.5px}.libro span{font-size:14px;color:var(--muted)}
@media(max-width:860px){.hero-grid,.tres,.reglas,.params,.kpis,.dos,.pasos,.fases,.recursos,.glos,.origen,.riesgo .mini,.gauges{grid-template-columns:1fr 1fr}.hero-grid,.gauges{grid-template-columns:1fr}}
@media(max-width:560px){.tres,.reglas,.params,.kpis,.dos,.pasos,.fases,.recursos,.glos,.origen,.riesgo .mini,.hero-kpis{grid-template-columns:1fr}body{font-size:16px}section{padding:40px 0}.hipo{padding:26px 22px}}
@media print{nav.top{position:static}details.code{display:none}section{page-break-inside:avoid}}
"""

CSS_BADGES = """
.badge.c1{background:#e6faef;color:#0d3d24;border-color:#b9efd1}.badge.c2{background:#e8f0fa;color:#1d3f6b;border-color:#c5d8f2}
.badge.c3{background:#fff5e9;color:#9a5a15;border-color:#f0d3ab}.badge.c4{background:#f3e8fa;color:#4c2a73;border-color:#dcc6ee}
.badge.c5{background:#e6f7f7;color:#0f4c4c;border-color:#b8e3e3}.badge.c6{background:#132620;color:#fff;border-color:#132620}
"""

JS = """
document.querySelectorAll('.copiar').forEach(b=>b.addEventListener('click',()=>{const t=b.closest('.body').querySelector('pre').innerText;navigator.clipboard.writeText(t).then(()=>{b.textContent='Copiado ✓';setTimeout(()=>b.textContent='Copiar',1500)})}));
"""


def pagina(titulo, desc, nav_links, cuerpo, otra, css_extra=""):
    lg = logo()
    links = "".join(f'<a href="#{i}">{t}</a>' for i, t in nav_links) + f'<a class="cta" href="{otra[0]}">{otra[1]}</a>'
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title><meta name="description" content="{html.escape(desc)}"><style>{CSS}{css_extra}</style></head><body>
<nav class="top"><div class="wrap">{f'<img src="{lg}" alt="Trade It Simple">' if lg else ''}<span class="brand">Trade It Simple</span><div class="links">{links}</div></div></nav>
{cuerpo}
<footer><div class="wrap"><div>Material educativo de <a href="{INSTAGRAM}">Trade It Simple</a>. No es asesoría financiera. Los resultados pasados no garantizan resultados futuros. Bitcoin es un activo muy volátil; operar con apalancamiento puede hacerte perder más de lo invertido.</div>
<div>Cifras generadas el {fecha(M['meta']['generado'])} con el motor abierto del repositorio <a href="{REPO_URL}">TIS-BTC-Lunes-Research</a> · velas horarias de BTC: {M['meta']['fuente']} · contraste con datos de Coinbase y cuatro perfiles de coste (tres exchanges y un CFD en MetaTrader 5) · {M['meta']['desde'][:4]}–{M['meta']['hasta'][:4]}.</div></div></footer>
<script>{JS}</script></body></html>"""


