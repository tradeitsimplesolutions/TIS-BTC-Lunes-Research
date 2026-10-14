"""La ficha de la estrategia (guia/btc-lunes-ficha.html). Importa las piezas comunes de comun.py."""
from comun import *

CSS_FICHA = CSS_BADGES + """
.strip{display:grid;grid-template-columns:1fr 1fr 1.3fr 1.4fr;gap:10px;margin:22px 0 0}
.chart{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px;margin:26px 0 8px}
.chart .tog{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;align-items:center}
.chart .tog button{font:inherit;font-size:13px;font-weight:700;padding:6px 12px;border-radius:999px;border:2px solid var(--c);background:var(--c);color:#fff;cursor:pointer}
.chart .tog button.off{background:#fff;color:var(--c);opacity:.7}
.chart canvas{width:100%;height:auto;display:block}.chart .tip{font-size:13px;color:var(--sub);min-height:20px;margin-top:6px;font-variant-numeric:tabular-nums}
.chart .print{display:none}@media print{.chart canvas,.chart .tog,.chart .tip{display:none}.chart .print{display:block}}
.libro{display:grid;grid-template-columns:78px 1fr;gap:14px;align-items:start;background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:10px}
.libro b{display:block;font-size:15.5px}.libro span{font-size:14px;color:var(--muted)}
.aporte{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px 20px 12px 22px;margin-bottom:14px;position:relative;overflow:hidden}.aporte::before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px}.aporte.si::before{background:#0e9c58}.aporte.no::before{background:#c8512f}
.aporte .cab{display:flex;align-items:center;gap:10px;margin-bottom:6px}.aporte .cab h4{margin:0;font-size:17px}.aporte .ico{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:900;font-size:18px;flex:0 0 30px;line-height:1}.aporte.si .ico{background:#0e9c58}.aporte.no .ico{background:#c8512f}
.aporte .intro{margin:0 0 10px;color:var(--sub);font-size:14px}.aporte ol,.aporte ul{margin:0;padding:0;list-style:none;counter-reset:n}.aporte li{display:grid;grid-template-columns:28px 1fr;gap:2px 10px;padding:9px 0;border-top:1px solid var(--line);font-size:14px;align-items:start}
.aporte ol li::before{counter-increment:n;content:counter(n);width:24px;height:24px;border-radius:50%;background:#e6f4ec;color:#0e9c58;font-weight:800;font-size:12px;display:grid;place-items:center;grid-row:span 2}.aporte ul li::before{content:"—";width:24px;height:24px;border-radius:50%;background:#fbe9e3;color:#c8512f;font-weight:800;display:grid;place-items:center;grid-row:span 2}
.aporte li b{grid-column:2;color:var(--ink)}.aporte li span{grid-column:2;color:var(--sub);font-size:13.5px}
.portada{width:78px;height:112px;flex:0 0 78px;border-radius:4px 8px 8px 4px;box-shadow:3px 3px 0 #0003,inset 6px 0 0 #0002;padding:9px 7px;color:#fff;font-weight:800;font-size:9px;line-height:1.15;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;word-break:break-word}
.portada span{color:#fff;opacity:1;text-shadow:0 1px 2px #0006}.portada small{color:#fff;font-weight:600;opacity:.9;font-size:8px}.portada.p1{background:linear-gradient(160deg,#1d3f6b,#0f2440)}.portada.p2{background:linear-gradient(160deg,#0e9c58,#0b3d24)}.portada.p3{background:linear-gradient(160deg,#63756b,#3a4b44)}.portada.p4{background:linear-gradient(160deg,#7a4fb8,#3a2560)}
.strip div{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px 14px;font-size:14px}
.strip b{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:2px}
.strip span{font-weight:800;color:var(--brand-ink);font-size:16px}.strip a{font-weight:800}
.oos-head{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin:38px 0 12px}
.oos-head h3{margin:0;font-size:22px}.oos-head span{color:var(--muted);font-size:14.5px}
.kpis6{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}.kpis6 .kpi .v{font-size:28px}
.regla-big{background:#fff;border:1px solid var(--line);border-radius:18px;padding:0;overflow:hidden;display:grid;grid-template-columns:185px 1fr}
.regla-big .lab{padding:22px 18px;color:#fff;display:flex;flex-direction:column;justify-content:center}
.regla-big .lab .k{font-size:11px;letter-spacing:.16em;opacity:.85;font-weight:800}.regla-big .lab .t{font-size:17px;font-weight:900;line-height:1.1;margin-top:6px;letter-spacing:-.01em;overflow-wrap:normal;hyphens:manual}
.regla-big .cont{padding:18px 22px}.regla-big .cont h4{margin:0 0 6px;font-size:20px}.regla-big .cont p{margin:0 0 12px;color:var(--sub);font-size:15px}
.regla-big pre{border-radius:10px;font-size:13.5px;padding:12px 14px;max-height:none}
.rb-f .lab{background:var(--azul)}.rb-c .lab{background:#7a4fb8}.rb-e .lab{background:var(--brand)}.rb-s .lab{background:var(--neg)}.rb-n .lab{background:#63756b}
.reglas-big{display:grid;gap:14px;margin-top:22px}
.specs{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}
.spec{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 16px 12px;border-top:5px solid var(--line);min-width:0}
.spec pre,.regla-big pre{white-space:pre-wrap;word-break:break-word}
.spec .k{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:800}.spec .t{font-size:22px;font-weight:900;margin:4px 0 6px}
.spec p{margin:0 0 10px;font-size:13.5px;color:var(--sub)}.spec pre{border-radius:8px;font-size:12.5px;padding:9px 12px}
.spec.s1{border-top-color:#9a5a15}.spec.s2{border-top-color:#1d3f6b}.spec.s3{border-top-color:#4c2a73}.spec.s4{border-top-color:#0f4c4c}
.niveles{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:22px}
.nivel{background:#fff;border:1px solid var(--line);border-radius:18px;padding:20px 22px;border-top:7px solid var(--line)}
.nivel.n1{border-top-color:var(--azul)}.nivel.n2{border-top-color:var(--brand)}.nivel.n3{border-top-color:#f0a860}.nivel.n4{border-top-color:var(--neg)}
.nivel{display:flex;flex-direction:column}.nivel .ico{font-size:28px;height:34px}.nivel h4{margin:6px 0 0;font-size:20px;height:26px}.nivel .sub{color:var(--muted);font-size:13px;margin:2px 0 12px;height:3.4em;overflow:hidden}
.nivel .big{font-size:34px;font-weight:900;letter-spacing:-.02em;line-height:1;height:36px}.nivel .bl{font-size:12.5px;color:var(--muted);margin-bottom:12px;height:1.4em}
.nivel .fila{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:baseline;font-size:12.5px;padding:7px 0;border-top:1px solid var(--line);min-height:2.4em;white-space:nowrap}.nivel .fila span{color:var(--sub)}.nivel .fila b{font-variant-numeric:tabular-nums;white-space:nowrap;text-align:right}
.nivel.n1 .big{color:var(--azul)}.nivel.n2 .big{color:var(--brand)}.nivel.n3 .big{color:#c97d1e}.nivel.n4 .big{color:var(--neg)}
.atr{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}
.atr div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px}.atr .n{font-size:12px;font-weight:800;color:var(--muted);letter-spacing:.1em}
.atr .f{font-family:var(--mono);font-size:13.5px;color:var(--brand-ink);margin:6px 0;background:var(--panel2);padding:6px 8px;border-radius:6px}
.atr .r{font-size:22px;font-weight:900}.atr p{margin:6px 0 0;font-size:13px;color:var(--sub)}
.flujo{display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin-top:22px;align-items:stretch}
.flujo > div{background:#fff;border:1px solid var(--line);padding:16px 14px;position:relative;text-align:center}
.flujo > div:first-child{border-radius:14px 0 0 14px}.flujo > div:last-child{border-radius:0 14px 14px 0}
.flujo .ic{font-size:26px}.flujo b{display:block;font-size:14.5px;margin:6px 0 2px}.flujo span{font-size:12.5px;color:var(--muted)}
.flujo > div:not(:last-child)::after{content:"›";position:absolute;right:-9px;top:50%;transform:translateY(-50%);width:18px;height:18px;border-radius:50%;background:var(--brand);color:#fff;font-weight:900;font-size:14px;line-height:18px;z-index:2}
.vias{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}
.via{border-radius:18px;padding:22px;border:1px solid var(--line);background:#fff;border-top:7px solid var(--line)}
.via.v1{border-top-color:var(--brand)}.via.v2{border-top-color:var(--azul)}.via.v3{border-top-color:#9a5a15}
.via .ico{font-size:34px}.via h4{margin:8px 0 4px;font-size:19px}.via .tag{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:3px 8px;border-radius:999px;background:var(--panel2);color:var(--sub);margin-bottom:8px}
.via ul{margin:0;padding-left:18px;font-size:14.5px;color:var(--sub)}.via li{margin:4px 0}
.rec-big{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}
.recb{border-radius:18px;overflow:hidden;border:1px solid var(--line);background:#fff}
.recb .head{padding:22px;color:#fff}.recb .head .ico{font-size:34px}.recb .head h4{margin:8px 0 0;font-size:19px}.recb .head span{font-size:13px;opacity:.9}
.recb .cuerpo{padding:16px 22px 20px}.recb .cuerpo p{margin:0 0 12px;font-size:14.5px;color:var(--sub)}
.recb.r1 .head{background:linear-gradient(135deg,#0d3d24,#0e9c58)}.recb.r2 .head{background:linear-gradient(135deg,#1d3f6b,#2b6cb0)}.recb.r3 .head{background:linear-gradient(135deg,#3a2560,#7a4fb8)}
.historia .hito h4{font-size:18px}.historia .hito p{font-size:15px}
.cuatro{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:18px}
@media(max-width:1000px){.niveles{grid-template-columns:1fr 1fr}}
@media(max-width:860px){.strip,.kpis6,.specs,.niveles,.atr,.vias,.rec-big,.cuatro{grid-template-columns:1fr 1fr}.flujo{grid-template-columns:1fr}.flujo > div{border-radius:0}.flujo > div:not(:last-child)::after{display:none}.regla-big{grid-template-columns:110px 1fr}}
@media(max-width:560px){.strip,.kpis6,.specs,.niveles,.atr,.vias,.rec-big,.cuatro{grid-template-columns:1fr}.regla-big{grid-template-columns:1fr}.regla-big .lab{padding:14px 18px}}
"""


def corto(t, n=42):
    out = ""
    for w in t.split():
        if len(out) + len(w) + 1 > n: return out.strip() + "…"
        out += w + " "
    return out.strip()

def portada(cl, titulo, sub):
    return f'<div class="portada {cl}"><span>{titulo}</span><small>{sub}</small></div>'


SERIES_HERO = [("robot", "v3 · 40 % del capital (el robot)", "#0e9c58", True), ("desnudo", "Lunes desnudo, sin filtros · 40 %", "#95a29b", True), ("v1", "v1 original (2025) · 40 %", "#2b6cb0", True),
               ("fijo", "v3 · 10.000 $ fijos (sin reinvertir)", "#0f4c4c", False), ("capital", "v3 · 100 % del capital", "#c97d1e", False), ("p20", "v3 · 20 %", "#7a4fb8", False),
               ("atr", "v3 · sizing por ATR (1 % riesgo)", "#9a5a15", False), ("vt", "v3 · vol targeting 1,5 %", "#b8860b", False), ("x2", "v3 · apalancado 1:2", "#c8512f", False)]
SERIES_NIVELES = [("p20", "Conservador · 20 % del capital", "#2b6cb0", True), ("robot", "El robot · 40 %", "#0e9c58", True), ("capital", "Decidido · 100 %", "#c97d1e", True),
                  ("x2", "Arriesgado · 1:2 (200 %)", "#c8512f", False), ("atr", "Sizing por ATR · 1 % de riesgo", "#9a5a15", False), ("vt", "Vol targeting · 1,5 % diario", "#b8860b", False)]
CAPTION_HERO = "Curva de capital desde {y0}, costes de Binance incluidos. En gris, el lunes desnudo (todos los lunes, sin filtro); en azul, la v1 original; en verde, la v3. Pulsa cada botón para encender o apagar una curva y el último para cambiar entre escala lineal (en % sobre el capital inicial) y logarítmica; pasa el ratón para ver los valores. La zona sombreada es el periodo fuera de muestra y la línea roja marca desde cuándo opera en real."
CAPTION_NIVELES = "La misma señal, las mismas operaciones, cuatro tamaños. Enciende el 1:2 para ver lo que hace el apalancamiento (y pasa a escala logarítmica para que no aplaste a las demás). Pasa el ratón para leer el capital de cada nivel en cualquier fecha."


def grafico_interactivo(id_="eqchart", series=None, caption=None, print_img="01_equity.png"):
    """Curva de capital con botones para encender/apagar cada serie (canvas + JS, sin librerías)."""
    if not SEM:
        return fig(print_img, "Curva de capital.")
    series = series or SERIES_HERO; caption = (caption or CAPTION_HERO).format(y0=SEM["fechas"][0][:4])
    datos = json.dumps(dict(fechas=SEM["fechas"], oos=SEM["oos"], live=SEM["live"], series=[dict(k=k, n=n, c=c, on=on, v=SEM[k]) for k, n, c, on in series]))
    botones = "".join(f'<button data-k="{k}" style="--c:{c}" class="{"" if on else "off"}">{n}</button>' for k, n, c, on in series) + '<button data-escala="1" style="--c:#132620;margin-left:auto">Escala: lineal ⇄ log</button>'
    js = """
(function(){const D=%s;const el=document.getElementById('__ID__');const cv=el.querySelector('canvas');const tip=el.querySelector('.tip');const on={};D.series.forEach(s=>on[s.k]=s.on);let LOG=false;const be=el.querySelector('[data-escala]');
const W=1100,H=440,L=62,R=16,T=18,B=34;cv.width=W;cv.height=H;const ctx=cv.getContext('2d');
const xs=D.fechas.map(f=>new Date(f).getTime());const x0=xs[0],x1=xs[xs.length-1];const X=t=>L+(t-x0)/(x1-x0)*(W-L-R);
function lims(){let lo=1e9,hi=-1e9;D.series.forEach(s=>{if(!on[s.k])return;s.v.forEach(v=>{if(v<lo)lo=v;if(v>hi)hi=v;});});if(hi<0)hi=1;lo=Math.min(lo,0.9);return[lo*0.97,hi*1.08];}
function draw(hover){const[lo,hi]=lims();const Y=v=>LOG?T+(Math.log(hi)-Math.log(Math.max(v,0.05)))/(Math.log(hi)-Math.log(lo))*(H-T-B):T+(hi-v)/(hi-lo)*(H-T-B);ctx.clearRect(0,0,W,H);be.textContent='Escala: '+(LOG?'logarítmica (pulsa para lineal)':'lineal (pulsa para log)');
ctx.fillStyle='#eef6f1';const xo=X(new Date(D.oos).getTime());ctx.fillRect(xo,T,W-R-xo,H-T-B);ctx.fillStyle='#3a4b44';ctx.font='12px system-ui';ctx.fillText('fuera de muestra →',xo+6,T+14);
const xl=X(new Date(D.live).getTime());ctx.strokeStyle='#c8512f';ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(xl,T);ctx.lineTo(xl,H-B);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle='#c8512f';ctx.fillText('en real →',xl+6,T+30);
ctx.strokeStyle='#e2ede8';ctx.lineWidth=1;ctx.fillStyle='#3a4b44';const paso=(hi-lo)>3?1:(hi-lo)>1.5?0.5:0.25;const marcas=[];for(let v=Math.ceil(lo/paso)*paso;v<=hi;v+=paso)marcas.push(Math.round(v*100)/100);marcas.forEach(v=>{ctx.beginPath();ctx.moveTo(L,Y(v));ctx.lineTo(W-R,Y(v));ctx.stroke();ctx.fillText(v+'× ('+Math.round((v-1)*100)+'%%)',4,Y(v)+4);});
for(let y=new Date(x0).getFullYear()+1;y<=new Date(x1).getFullYear();y+=1){const tx=X(new Date(y,0,1).getTime());ctx.beginPath();ctx.moveTo(tx,T);ctx.lineTo(tx,H-B);ctx.stroke();ctx.fillText(y,tx-14,H-10);}
const labs=[];D.series.forEach(s=>{if(!on[s.k])return;ctx.strokeStyle=s.c;ctx.lineWidth=2;ctx.beginPath();s.v.forEach((v,i)=>{const x=X(xs[i]),y=Y(v);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();labs.push({y:Y(s.v[s.v.length-1])-4,t:s.v[s.v.length-1].toFixed(2)+'×',c:s.c});});
labs.sort((a,b)=>a.y-b.y);for(let i=1;i<labs.length;i++){if(labs[i].y-labs[i-1].y<13)labs[i].y=labs[i-1].y+13;}
ctx.font='bold 12px system-ui';labs.forEach(l=>{ctx.fillStyle=l.c;ctx.fillText(l.t,W-R-44,l.y);});
if(hover!=null){const i=hover;ctx.strokeStyle='#132620';ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(X(xs[i]),T);ctx.lineTo(X(xs[i]),H-B);ctx.stroke();ctx.setLineDash([]);
let s=D.fechas[i]+' · ';D.series.forEach(q=>{if(on[q.k])s+=q.n.split(' (')[0].split(' ·')[0]+': '+q.v[i].toFixed(2)+'× · ';});tip.textContent=s.slice(0,-3);
D.series.forEach(q=>{if(!on[q.k])return;ctx.fillStyle=q.c;ctx.beginPath();ctx.arc(X(xs[i]),Y(q.v[i]),4,0,7);ctx.fill();});}}
el.querySelectorAll('.tog button[data-k]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.k;on[k]=!on[k];b.classList.toggle('off',!on[k]);draw(null);}));be.addEventListener('click',()=>{LOG=!LOG;draw(null);});
cv.addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect();const x=(e.clientX-r.left)*W/r.width;const t=x0+(x-L)/(W-L-R)*(x1-x0);let i=0;while(i<xs.length-1&&xs[i]<t)i++;draw(i);});
cv.addEventListener('mouseleave',()=>{draw(null);tip.textContent='';});draw(null);})();""".replace("__ID__", id_) % datos
    return f"""<div class="chart" id="{id_}"><div class="tog">{botones}</div><canvas></canvas><div class="tip"></div>
<img class="print" src="{img(print_img)}" alt="Curva de capital">
<figcaption style="padding:8px 4px 0">{caption}</figcaption>
<script>{js}</script></div>"""


def ficha():
    f1 = M["fase1"]; o, t, oos = f1["IS"], f1["TODO"], f1["OOS"]; orb, trb, o20, t20, ox, tx = f1["OOS_robot"], f1["TODO_robot"], f1["OOS_p20"], f1["TODO_p20"], f1["OOS_x2"], f1["TODO_x2"]
    meta = M["meta"]; mk = M["monkey"]; ed = M["edge_decay"]; sz = M["sizing"]; V = M["versiones"]; ae = M["aed"]; ex = M["exchanges"]; vg = M["vigilancia"]; f5 = M["fase5"]; mt = M["mc_tamano"]
    anos = int(meta["hasta"][:4]) - int(meta["desde"][:4]); rob = int(ROBOT * 100)
    anos_oos = (pd_anios := (lambda a, b: (int(b[:4]) - int(a[:4])) + (int(b[5:7]) - int(a[5:7])) / 12)(meta["oos_desde"], meta["oos_hasta"]))
    b, p, v3 = V["base"], V["pine"], V["v3"]
    eras = ae["eras"]; lpe = ae["lunes_por_era"]; dias = ae["dias"]

    # ------------------------------------------------------------- hero
    hero = f"""<header class="hero"><div class="wrap">
<div class="eyebrow">Estrategia #2 · Estacional · Bitcoin</div>
<h1>BTC · Efecto Lunes<small>Compra el lunes de Bitcoin, el día en que vuelve el dinero. Solo cuando hay movimiento. Y déjalo correr el día entero.</small></h1>
<div class="badges"><span class="badge c1">Estacional · ciclo semanal</span><span class="badge c2">Bitcoin · BTC/USDT</span><span class="badge c3">Velas de 1 hora · 24 h en posición</span><span class="badge c4">Solo largos</span><span class="badge c5">Automatizada · MetaTrader 5 y TradingView</span><span class="badge c6">{anos} años de datos · en real desde {fecha(meta['live_desde'])[-8:]}</span></div>
<div class="strip"><div><b>Motor usado</b><span>Sentinel</span></div><div><b>Método</b><span>TIS</span></div><div><b>Fuente de datos</b><span>Binance + Coinbase</span></div><div><b>Replícalo tú</b><a href="{REPO_URL}">Repositorio abierto: datos, motor y código →</a></div></div>
<div class="oos-head"><h3>Números fuera de muestra</h3><span>{fecha(meta['oos_desde'])} → {fecha(meta['oos_hasta'])} · datos que la regla nunca vio · {rob} % del capital por operación (el robot) · costes de Binance incluidos</span></div>
<div class="kpis6">
{kpi(num(orb['pf']), 'Profit Factor', 'ganado ÷ perdido', 'ok')}
{kpi(pct(orb['cagr']), 'Retorno anual', f'CAGR al {rob} %')}
{kpi(pct(orb['mdd_diario']), 'Peor caída', 'drawdown hora a hora', 'neg')}
{kpi(pct(orb['wr'],0), 'Aciertos', 'lunes ganadores')}
{kpi(orb['n'], 'Operaciones', f"{num(orb['n']/anos_oos,0)} al año · {t['n']} en {anos} años")}
{kpi(pct(orb['expectancy'],2,True), 'Por operación', 'retorno medio neto')}
</div>
{grafico_interactivo()}
{(lambda r: f'<div class="info" style="margin-top:14px"><b>En real desde {fecha(r["desde"])}</b> (la regla original, operando con dinero con alertas de TradingView conectadas al exchange; estas son las operaciones reales, no el motor): <b>{r["n"]} operaciones · Profit Factor {num(r["pf"])} · {pct(r["ret_total_pct"]/100, 0, True)} con el 100 % del capital · {pct(r["win"], 0)} de aciertos · peor caída {pct(r["mdd_pct"]/100)}</b>, ya descontado el coste de Binance spot ({num(r["coste_ida_vuelta_pct"],2)} % por ida y vuelta). Vigilancia: z = {num(r["z_hoy"])} ({"🟢 verde" if (r["z_hoy"] or 0) > -1 else ("🟡 amarillo" if (r["z_hoy"] or 0) > -2 else "🔴 rojo")}).</div>')(REC["real"]) if REC and REC.get("real") else ""}
</div></header>"""

    # ------------------------------------------------------------- 1 · ficha técnica
    def regla(cl, k, t_, h, p_, code):
        return f'<div class="regla-big {cl}"><div class="lab"><div class="k">{k}</div><div class="t">{t_}</div></div><div class="cont"><h4>{h}</h4><p>{p_}</p><pre><code>{html.escape(code)}</code></pre></div></div>'

    def spec(cl, k, t_, p_, code):
        return f'<div class="spec {cl}"><div class="k">{k}</div><div class="t">{t_}</div><p>{p_}</p><pre><code>{html.escape(code)}</code></pre></div>'
    eb = EX["binance"]
    ficha_tec = sec("reglas", "1 · Ficha técnica", "Las reglas, sin letra pequeña",
                    "Un filtro de volatilidad, un filtro de calendario, una entrada, una salida y ningún stop. Todo se decide al cierre de la vela de las 23:00 UTC del domingo y se ejecuta en la apertura siguiente: es lo que hace un robot, o tú con una alarma.",
                    '<div class="reglas-big">'
                    + regla("rb-f", "Regla 1 · filtro", "FILTRO DE VOLATILIDAD", "Solo operamos si Bitcoin se está moviendo más que en el 30 % de los días más tranquilos de su último año", "Medimos cuánto se mueve BTC por hora con el ATR de 48 velas (dos días), en porcentaje del precio. Lo comparamos con los 365 días anteriores: si el valor de hoy está entre el 70 % más alto del año, hay permiso. Si está entre el 30 % más bajo (calma), no se opera: en calma el lunes no cubre el 0,28 % de costes. Es un filtro relativo: vale igual con el Bitcoin de 2018 que con el de 2026.",
                            "atr_pct  = ATR(48 velas) / precio × 100          # cuánto se mueve BTC por hora, en %\nsuelo    = percentil 30 de atr_pct en las ultimas 8760 velas (un año)\nFILTRO 1 = atr_pct >= suelo                      # hay movimiento → se puede operar")
                    + regla("rb-c", "Regla 2 · filtro", "FILTRO DE CALENDARIO", "Nunca el primer lunes del mes", "En el análisis exploratorio, los lunes del día 1 al 7 pierden en las tres eras de Bitcoin (retail, institucional y ETF) mientras el resto de lunes gana. Los flujos de cierre y apertura de mes rompen el patrón. Se dejan pasar.",
                            "FILTRO 2 = dia_del_mes(lunes) > 7                 # el primer lunes del mes no se opera")
                    + regla("rb-e", "Regla 3", "ENTRADA", "Compra a las 00:00 UTC del lunes", "Si los dos filtros dan permiso, la orden se lanza al cierre de la vela de las 23:00 del domingo y se ejecuta a mercado en la apertura de la vela de las 00:00 del lunes.",
                            "si FILTRO 1 y FILTRO 2:\n    comprar en apertura[lunes 00:00 UTC]")
                    + regla("rb-s", "Regla 4", "SALIDA", "Venta a las 00:00 UTC del martes", "24 velas después, pase lo que pase. Salida por tiempo: el efecto es la deriva del día entero, no un objetivo de precio.",
                            "vender en apertura[martes 00:00 UTC]           # 24 velas en posición")
                    + regla("rb-n", "Regla 5", "SIN STOP", "Ni stop ni take profit", f"Probamos 64 combinaciones de take profit y stop en los tres periodos: ninguna mejora la regla. Las ganadoras pasan por un −{abs(M['revision']['mae_mfe']['resumen']['mae_gan'])*100:.1f} % de media antes de subir y las perdedoras solo llegan a +{M['revision']['mae_mfe']['resumen']['mfe_per']*100:.1f} %. La gestión del riesgo es el tamaño (sección 5).",
                            "stop_loss = ninguno\ntake_profit = ninguno                            # el tamaño de posición es la gestión del riesgo")
                    + "</div>"
                    + '<div class="specs">'
                    + spec("s1", "Timeframe", "1 hora", "Se mira una vez a la semana: el domingo a las 23:00 UTC (la 01:00 en España en invierno, las 00:00 en verano).", "velas = 1 hora (UTC)\nevaluar_en = domingo 23:00\nejecutar_en = lunes 00:00")
                    + spec("s2", "Activo", "Bitcoin", "BTC/USDT en Binance (datos y costes de referencia). Contrastado con BTC/USD en Coinbase.", f"activo = 'BTC/USDT'\ndatos = Binance H1 ({meta['desde'][:4]}–{meta['hasta'][:4]})")
                    + spec("s3", "Dirección", "Solo largos", "El lunes sube; el martes y el jueves bajan (sección 3), pero el corto no es el espejo del largo y no está validado.", "direccion = LONG\nposiciones_simultaneas = 1")
                    + spec("s4", "Costes", f"{num(ex['binance']['ida_vuelta_pct'],2)} %", f"Por ida y vuelta en Binance spot: comisión {num(eb['comision_bps']/100,2)} % por lado, spread {num(eb['spread_bps'],0)} bps y {num(eb['slippage_bps'],0)} bps de slippage por lado. Tarifas públicas base, leídas el {fecha(FECHA_TARIFAS)}.", f"precio_compra = apertura × (1 + 0,0014)\nprecio_venta  = apertura × (1 − 0,0014)")
                    + "</div>"
                    + fig("02_operaciones_ano.png", "Las operaciones de un año completo sobre las velas diarias de Bitcoin, como en MetaTrader: flecha azul hacia arriba = compra a las 00:00 UTC del lunes; flecha roja hacia abajo = venta a las 00:00 del martes; línea punteada verde o roja = operación ganadora o perdedora. Las aspas grises son las entradas filtradas: lunes en los que el filtro de volatilidad o el de calendario no dieron permiso.")
                    + fig("16_operacion_ejemplo.png", "Dos operaciones reales del periodo fuera de muestra, vela a vela, con el panel del permiso debajo: la línea morada es el ATR%(48) y la verde discontinua el percentil 30 de su último año. La vela sombreada en naranja es la de señal (domingo 23:00 UTC). Se compra en la apertura siguiente, se aguanta el lunes entero y se vende a las 00:00 del martes. En el título, el movimiento del precio traducido a lo que supone para el capital con cada tamaño.")
                    + "<h3>El lunes desnudo, la v1 y la v3</h3><p class=\"lead\" style=\"font-size:16px\">Tres curvas con las mismas velas, los mismos costes y el mismo tamaño. <b>Lunes desnudo</b>: comprar todos los lunes, sin filtro. <b>v1</b>: la versión original de 2025, la que opera en real, con un ATR% fijo entre 0,40 y 1,20 y un |retorno de 24 h| ≤ 4 %. <b>v3</b>: la validada, que traduce esos umbrales a su época (percentil del ATR, sin tope) y añade el filtro de calendario. Cómo pasamos de una a otra está contado en la sección 3, <a href=\"#descubrimiento\">Cómo descubrimos el edge</a>: un efecto de fin de semana documentado que se desgastó, un activo que cambió de dueños, un AED por eras y una búsqueda de filtros que tenían que aguantar en todas las épocas.</p>"
                    + fig("03_versiones.png", f"Capital acumulado al {rob} % durante los {anos} años, en escala lineal. Gris: el lunes desnudo. Azul: la v1 original. Verde: la v3.")
                    + tabla(["", "Lunes desnudo (sin filtros)", "v1 · original 2025", "v3 · validada"], [
                        ["Filtro de volatilidad", "ninguno", "ATR% fijo entre 0,40 y 1,20 · |ret 24 h| ≤ 4 %", "ATR% ≥ percentil 30 de su año"], ["Filtro de calendario", "—", "—", "sin el primer lunes del mes"],
                        [f"Operaciones · periodo completo ({meta['desde'][:4]}–{meta['hasta'][:4]})", num(b["TODO"]["n"], 0), num(p["TODO"]["n"], 0), f"<b>{num(v3['TODO']['n'], 0)}</b>"],
                        [f"Operaciones · fuera de muestra ({meta['oos_desde'][:4]}–{meta['oos_hasta'][:4]})", num(b["OOS"]["n"], 0), num(p["OOS"]["n"], 0), f"<b>{num(v3['OOS']['n'], 0)}</b>"],
                        ["Profit Factor · periodo completo", num(b["TODO"]["pf"]), num(p["TODO"]["pf"]), f"<b>{num(v3['TODO']['pf'])}</b>"], ["Profit Factor · fuera de muestra", num(b["OOS"]["pf"]), num(p["OOS"]["pf"]), f"<b>{num(v3['OOS']['pf'])}</b>"],
                        [f"Profit Factor · en real (desde {fecha(meta['live_desde'])})", num(b["REAL"]["pf"]), num(p["REAL"]["pf"]), f"<b>{num(v3['REAL']['pf'])}</b>"],
                        [f"Retorno anual (CAGR, {rob} %) · periodo completo", pct(b["TODO_robot"]["cagr"]), pct(p["TODO_robot"]["cagr"]), f"<b>{pct(v3['TODO_robot']['cagr'])}</b>"],
                        [f"Peor caída ({rob} %) · periodo completo", pct(b["TODO_robot"]["mdd_diario"]), pct(p["TODO_robot"]["mdd_diario"]), f"<b>{pct(v3['TODO_robot']['mdd_diario'])}</b>"],
                        [f"Capital final ({rob} %) · periodo completo", num(1 + b["TODO_robot"]["ret_total"], 2) + "×", num(1 + p["TODO_robot"]["ret_total"], 2) + "×", f"<b>{num(1 + v3['TODO_robot']['ret_total'], 2)}×</b>"]])
                    + f'<div class="nota"><b>Lectura honesta:</b> la v1 ya funcionaba en el tramo reciente (es lo que se veía en TradingView, que solo enseña desde 2022). Lo que no aguantaba era 2018–2021: su tope de 1,20 % recortaba justo los lunes con movimiento, que son los que pagan. En real, desde {fecha(meta["live_desde"])}, las dos versiones ganan; la v3 lo hace con {num(v3["REAL"]["n"],0)} operaciones en vez de {num(p["REAL"]["n"],0)}. El lunes desnudo gana poco con costes: el edge está en elegir qué lunes.</div>', "alt")

    # ------------------------------------------------------------- 2 · hipótesis
    hipo = sec("hipotesis", "2 · La hipótesis", "Por qué debería funcionar",
               "Antes de tocar un dato hay que saber por qué una idea debería ganar. Si no sabes por qué gana, tampoco sabrás cuándo dejará de hacerlo.",
               f"""<div class="hipo"><div class="k">Hipótesis</div>
<div class="t">Bitcoin cotiza siete días, pero el dinero que lo mueve trabaja cinco. El fin de semana es un mercado huérfano de flujo profesional; el lunes vuelve, y vuelve comprando. Si además hay volatilidad, el movimiento es grande y paga.</div>
<div class="w">No miramos un indicador de precio: miramos el calendario y la volatilidad. El permiso de volatilidad separa los lunes en los que el movimiento cubre los costes de los que no. Compramos el día entero y lo dejamos correr, porque la ganancia está en la cola: unos pocos lunes grandes hacen el año.</div></div>
<div class="tres">
<div class="card"><span class="n">1</span><h4>Qué explota</h4><p>Un ciclo semanal del precio de Bitcoin: el lunes y el miércoles suben de media, el martes y el jueves bajan. En las tres eras del activo (sección 3).</p></div>
<div class="card"><span class="n">2</span><h4>Por qué existe</h4><p>Bitcoin es hoy un activo <i>risk-on</i> en manos de gestores, ETF y mesas que operan de lunes a viernes. El fin de semana toma los golpes sin ellos; el lunes se reposiciona todo.</p></div>
<div class="card"><span class="n">3</span><h4>Cuándo falla</h4><p>En calma extrema (no cubre el 0,28 %), en el primer lunes del mes y en años de mercado roto como 2022. Por eso hay permiso de volatilidad, calendario y tamaño moderado.</p></div>
</div>""")

    # ------------------------------------------------------------- 3 · cómo descubrimos el edge
    def era(n): return lpe[n]
    e0, e1, e2 = eras
    d_lun = {n: dias[n][0] for n in eras}; d_vie = {n: dias[n][4] for n in eras}; d_sab = {n: dias[n][5] for n in eras}
    descubrimiento = sec("descubrimiento", "3 · Cómo descubrimos el edge", "Un efecto que se desgastó y volvió con otra forma",
                         "Esta es la parte más importante de la hipótesis. No encontramos el lunes en un libro: lo encontramos siguiendo la pista de un efecto que había dejado de funcionar.",
                         f"""<div class="camino historia">
<div class="hito"><div class="f">Lo documentado</div><h4>Antes había un sesgo de fin de semana</h4><p>Los papers de 2019 encontraban en Bitcoin un efecto día de la semana: lunes con más retorno y más volatilidad (Caporale y Plastun; Aharon y Qadan), y una actividad que seguía el reloj de las bolsas aunque el mercado no cerrara. En nuestros datos de la era retail, el viernes y el sábado también subían: {pct(d_vie[e0]['media']/100, 2, True)} y {pct(d_sab[e0]['media']/100, 2, True)} brutos por día.</p></div>
<div class="hito"><div class="f">El desgaste</div><h4>Eso fue cambiando, y los papers lo recogen</h4><p>Kinateder y Papavassiliou (2021) ya no encuentran el efecto en los retornos, solo en la volatilidad. En nuestros datos, el sábado pasa de {pct(d_sab[e0]['media']/100, 2, True)} a {pct(d_sab[e2]['media']/100, 2, True)} y el viernes de {pct(d_vie[e0]['media']/100, 2, True)} a {pct(d_vie[e2]['media']/100, 2, True)}. El fin de semana de los papers murió. Todos los efectos de calendario publicados sufren <i>edge decay</i>: cuando se publican, se operan; cuando se operan, desaparecen.</p></div>
<div class="hito"><div class="f">La pregunta</div><h4>¿A qué responde Bitcoin si ya no es una acción de retail?</h4><p>Bitcoin dejó de ser un activo de fin de semana para ser un activo <i>risk-on</i>: toma los golpes del fin de semana sin el dinero profesional, y el lunes ese dinero vuelve. Si la tesis es cierta, el efecto no debería estar en el fin de semana sino en el lunes, y debería crecer con la institucionalización.</p></div>
<div class="hito"><div class="f">El AED</div><h4>Miramos cómo evolucionaron los efectos estacionales, era a era</h4><p>Partimos la historia en tres eras: retail (2017–19), institucional (2020–23) y ETF (desde 2024). El lunes bruto pasa de {pct(d_lun[e0]['media']/100, 2, True)} por día (t de Student {num(d_lun[e0]['t'],1)}: no distinguible de cero) a {pct(d_lun[e2]['media']/100, 2, True)} (t {num(d_lun[e2]['t'],1)}): el mejor día de la semana. Y aparece un ciclo completo: lunes y miércoles suben, martes y jueves bajan.</p></div>
<div class="hito"><div class="f">La búsqueda del filtro</div><h4>Qué variable tiene información de verdad</h4><p>Probamos por quintiles diez variables en la vela de señal, era a era. Solo una repite el signo en todas: la volatilidad, y su información está en la zona alta, no es lineal. El retorno del domingo, la distancia a las medias, el volumen o el fin de semana previo no tienen patrón que se repita. De ahí el permiso de volatilidad relativo a su año, y del calendario, el primer lunes del mes.</p></div>
<div class="hito"><div class="f">La validación</div><h4>Cinco fases, cuatro perfiles de coste, y pum: un edge joven</h4><p>{num(mk['n_sim'],0)} monos comprando un día cualquiera, {anos} años de datos, walk-forward año a año, 25 horas de entrada y salida, {num(M['fase4']['n_sim'],0)} caminos de Monte Carlo y estrés. Lo que queda es un edge <b>joven</b>: potente desde 2024, presente en 2020, inexistente antes. Se opera con tamaño moderado y con una vigilancia de una sola fórmula (manual avanzado).</p></div>
</div>
{fig('13b_dias_eras.png', 'Retorno medio de cada día de la semana en la era retail (gris) y en la era ETF (verde). Antes subían el viernes y el sábado; ahora sube el lunes, y el martes y el jueves bajan. El efecto no murió: cambió de día.')}
{fig('14_aed_eras.png', 'Año a año: el lunes desnudo (todos los lunes, gris) frente al lunes con filtro (la v3, verde), neto de costes. Esto es lo que buscábamos al elegir el filtro: no el año más bonito, sino que mejorara en todas las eras, a pesar de cómo ha cambiado Bitcoin.')}
<div class="info"><b>Cómo se eligió el filtro, y cómo no.</b> No buscamos el filtro que más ganaba: con nueve años de datos siempre hay uno que gana por casualidad. Buscamos el <b>mecanismo</b>: el lunes paga cuando Bitcoin se mueve, y eso se ve ya en el periodo de construcción (2017–2023), donde el filtro de volatilidad relativo a su año es el único que mejora el lunes desnudo de forma clara. Lo que se le exigió no fue ganar todos los años, sino que <b>la mejora se mantuviera en las tres eras del activo</b> (retail, institucional y ETF), es decir, que aguantara la evolución de Bitcoin. Probamos sesenta filtros: los fijos de la v1, los de retorno previo, el ADX, las medias, el volumen… mejoran en una era y empeoran en otra. Solo el de volatilidad relativo a su año y el de calendario aguantan. Las operaciones reales desde 2025 <b>no se usaron para elegir nada</b>: sirven para comprobar que lo que opera coincide con lo que dice la regla. La tabla completa está en el manual avanzado.</div>
<div class="cuatro">{kpi(pct(era(e0)['media']/100, 2, True), 'Lunes · era retail', f"PF {num(era(e0)['pf'])} · {era(e0)['n']} lunes · neto", 'neg' if era(e0)['media'] < 0 else '')}{kpi(pct(era(e1)['media']/100, 2, True), 'Lunes · era institucional', f"PF {num(era(e1)['pf'])} · {era(e1)['n']} lunes · neto")}{kpi(pct(era(e2)['media']/100, 2, True), 'Lunes · era ETF', f"PF {num(era(e2)['pf'])} · {era(e2)['n']} lunes · neto", 'ok')}{kpi(num(d_lun[e2]['t'],1), 't de Student · era ETF', 'por encima de 2 se toma en serio', 'ok')}</div>""", "alt")

    # ------------------------------------------------------------- 4 · origen
    libros = "".join(f'<div class="libro">{portada(f"p{i+1}", corto(p_["titulo"]), f"{p_['autores'].split(',')[0].split(' y ')[0]} · {p_['ano']}")}<div><b>{html.escape(p_["titulo"])} ({p_["ano"]})</b><span>{html.escape(p_["autores"])}. {html.escape(p_["revista"])}. {p_["nota"]} → <a href="{p_["url"]}">Ver el paper</a></span></div></div>' for i, p_ in enumerate(PAPERS))
    origen = sec("origen", "4 · El origen", "De dónde viene la idea",
                 "Lo que documentó la literatura, con sus fechas. Nuestra aportación es seguir la pista del desgaste hasta el lunes de hoy.",
                 f"""<div class="origen"><div>{libros}</div><div>
<div class="aporte si"><div class="cab"><span class="ico">+</span><h4>Lo que cambiamos nosotros</h4></div><p class="intro">Los papers miden días enteros con datos de 2010–2019: encuentran el lunes y después dejan de encontrarlo.</p>
<ol><li><b>Partimos la historia en eras</b><span>y vimos que el efecto no muere: cambia de sitio.</span></li>
<li><b>Lo hicimos ejecutable</b><span>hora de entrada y de salida en UTC, una vela de señal, una orden.</span></li>
<li><b>Filtro relativo a su época</b><span>permiso de volatilidad por percentil del último año, en vez de umbrales fijos.</span></li>
<li><b>Costes reales y dinero real</b><span>tres exchanges y un CFD con sus tarifas, operación en real desde {fecha(meta['live_desde'])}.</span></li></ol></div>
<div class="aporte no"><div class="cab"><span class="ico">×</span><h4>Lo que no hicimos</h4></div>
<ul><li><b>Optimizar la hora</b><span>es la del día UTC; la meseta de horas la confirma, no la elige.</span></li>
<li><b>Stop ni take profit</b><span>las 64 combinaciones probadas empeoran la regla.</span></li>
<li><b>Elegir el pico de un mapa</b><span>la configuración que opera está en el centro de la meseta.</span></li></ul></div>
</div></div>""")

    # ------------------------------------------------------------- 5 · camino
    camino = sec("camino", "5 · El camino", "De un paper olvidado a un robot operando",
                 "Cómo llegó esta estrategia hasta aquí. Cada parada tiene su prueba en el manual avanzado.",
                 f"""<div class="camino">
<div class="hito"><div class="f">2019–2021</div><h4>La literatura documenta el lunes de Bitcoin y después su desgaste</h4><p>Cuatro papers en Finance Research Letters. El último ya no lo encuentra en los retornos.</p></div>
<div class="hito"><div class="f">2025</div><h4>Versión original: el lunes con dos filtros fijos, operando en real desde {fecha(meta['live_desde'])}</h4><p>Un script de TradingView, sus alertas y un exchange. Reconciliado trade a trade con el motor: {REC['emparejadas'] if REC else '—'} de {REC['tv']['n'] if REC else '—'} operaciones coinciden.</p></div>
<div class="hito"><div class="f">Septiembre 2026</div><h4>{anos} años de velas horarias de Binance, con costes, partidos en construcción y validación</h4><p>{o['n']} operaciones para construir · {oos['n']} para validar en datos nunca vistos · {v3['REAL']['n']} ya en real.</p></div>
<div class="hito"><div class="f">Revisión</div><h4>Horas, duración, salidas, 60 filtros, AED por eras, cuatro perfiles de coste</h4><p>De ahí sale la v3: los filtros fijos pasan a relativos a su año, el tope desaparece, entra el calendario. Todo en el <a href="btc-lunes-validacion.html">manual avanzado</a>.</p></div>
<div class="hito"><div class="f">Validación · método TIS</div><h4>Walk-forward, meseta de horas, Monte Carlo, estrés y test del mono</h4><p>Supera al {pct(mk['pct_pf'],0)} de {num(mk['n_sim'],0)} entradas al azar. El Monte Carlo fija el tamaño; la vigilancia en real es una fórmula.</p></div>
<div class="hito"><div class="f">Hoy</div><h4>En real con alertas de TradingView, vigilancia semanal</h4><p>{(lambda r: f"En real desde {fecha(r['desde'])} con la regla original: {r['n']} operaciones reales, Profit Factor {num(r['pf'])}, {pct(r['ret_total_pct']/100, 0, True)} con el 100 % del capital, peor caída {pct(r['mdd_pct']/100)}. Vigilancia a {fecha(meta['generado'])}: z = {num(r['z_hoy'])} → {'verde' if (r['z_hoy'] or 0) > -1 else ('amarillo' if (r['z_hoy'] or 0) > -2 else 'rojo')}. ")(REC["real"]) if REC and REC.get("real") else ""}La v3 es la versión validada; el cambio del robot a la v3 y el tamaño ({rob} % o 30 %) son la siguiente decisión.</p></div>
</div>""", "alt")

    # ------------------------------------------------------------- 6 · riesgo y tamaño
    ej = sz["ejemplo"]; cap = 10000.0; posicion = cap * ROBOT; unidades = posicion / ej["precio"]
    def nivel(cl, ico, nombre, sub, big, bl, filas):
        fs = "".join(f'<div class="fila"><span>{a}</span><b>{b_}</b></div>' for a, b_ in filas)
        return f'<div class="nivel {cl}"><div class="ico">{ico}</div><h4>{nombre}</h4><div class="sub">{sub}</div><div class="big">{big}</div><div class="bl">{bl}</div>{fs}</div>'
    tope = mt["tope"]
    riesgo_sec = sec("riesgo", "6 · Riesgo y tamaño", "La misma señal, cuatro formas de apostar",
                     "La señal es una. Lo que cambia es cuánto capital pones en cada lunes. Aquí no hay stop: el tamaño ES la gestión del riesgo, y lo fija el Monte Carlo, no el apetito.",
                     '<div class="niveles">'
                     + nivel("n1", "🛡️", "Conservador", "20 % del capital por operación", pct(o20["cagr"]), "retorno anual fuera de muestra",
                             [("Peor caída · validación", pct(o20["mdd_diario"])), (f"Peor caída · {anos} años", pct(t20["mdd_diario"])), (f"Capital final · {anos} años", num(1 + t20["ret_total"], 2) + "×"), ("En juego", "20 %"), ("Monte Carlo 5 % peor", pct(next(x["mdd_p95"] for x in mt["filas"] if abs(x["f"] - 0.2) < 1e-9)))])
                     + nivel("n2", "🤖", "El robot", f"{rob} % del capital por operación", pct(orb["cagr"]), "retorno anual fuera de muestra",
                             [("Peor caída · validación", pct(orb["mdd_diario"])), (f"Peor caída · {anos} años", pct(trb["mdd_diario"])), (f"Capital final · {anos} años", num(1 + trb["ret_total"], 2) + "×"), ("En juego", f"{rob} %"), ("Monte Carlo 5 % peor", pct(M["fase4"]["mdd_p5"]))])
                     + nivel("n3", "🔥", "Decidido", "100 % del capital en cada operación", pct(oos["cagr"]), "retorno anual fuera de muestra",
                             [("Peor caída · validación", pct(oos["mdd_diario"])), (f"Peor caída · {anos} años", pct(t["mdd_diario"])), (f"Capital final · {anos} años", num(1 + t["ret_total"], 2) + "×"), ("En juego", "100 %"), ("Monte Carlo 5 % peor", pct(M["fase4_100"]["mdd_p5"]))])
                     + nivel("n4", "⚡", "Arriesgado", "apalancamiento 1:2 · 200 % del capital", pct(ox["cagr"]), "retorno anual fuera de muestra",
                             [("Peor caída · validación", pct(ox["mdd_diario"])), (f"Peor caída · {anos} años", pct(tx["mdd_diario"])), (f"Capital final · {anos} años", num(1 + tx["ret_total"], 2) + "×"), ("En juego", "200 % · futuros"), ("Monte Carlo 5 % peor", "ruina posible")])
                     + "</div>"
                     + f'<div class="nota"><b>Lo que dice el Monte Carlo sobre el tamaño:</b> reordenando las {t["n"]} operaciones {num(M["fase4"]["n_sim"],0)} veces en bloques de {M["fase4"]["bloque"]} (para conservar las rachas), el drawdown del 5 % peor de caminos queda en {pct(M["fase4"]["mdd_p5"])} con el {rob} % y en {pct(next(x["mdd_p95"] for x in mt["filas"] if abs(x["f"] - 0.3) < 1e-9))} con el 30 %. El criterio es 25 % con un margen de flexibilidad de 1 punto (un umbral sin margen sería un pico duro): el {rob} % lo cumple dentro del margen y el 30 % sin necesitarlo. Con el 100 % el 5 % peor llega a {pct(M["fase4_100"]["mdd_p5"])}. El apalancamiento solo es posible en futuros o CFD, y duplica también la peor caída.</div>'
                     + f'<div class="info"><b>Dos cifras de "peor caída" en cada tarjeta, y las dos importan.</b> "Validación" es la caída en los datos que la regla nunca vio (2024–2026): es la que corresponde a los números de la cabecera. "{anos} años" es la caída en todo el histórico, y la mayor está en 2022, antes de la era ETF. Con el 100 % del capital, la caída de 2022 fue del {pct(t["mdd_diario"])}: eso es lo que tienes que estar dispuesto a aguantar si eliges "Decidido".</div>'
                     + grafico_interactivo("nivchart", SERIES_NIVELES, CAPTION_NIVELES, "10_riesgo.png")
                     + fig("10_riesgo.png", "La caída desde máximos de cada nivel, en el mismo eje de tiempo: lo que habrías visto en la cuenta en cada momento. La de 2022 es la que hay que mirar antes de elegir.")
                     + f"""<h3>Qué calcula el filtro de volatilidad, en dos pasos</h3>
<p class="lead" style="font-size:16px"><b>Paso 1 · ¿Cuánto se mueve Bitcoin cada hora?</b> Para cada vela medimos su rango verdadero: lo más grande de su altura (máximo − mínimo) o de la distancia al cierre anterior. La media de los últimos 48 rangos (dos días) es el ATR. Lo dividimos por el precio para tenerlo en porcentaje: "BTC se mueve un 0,5 % por hora".<br><b>Paso 2 · ¿Eso es mucho o poco <i>para el Bitcoin de ahora</i>?</b> Cogemos los 365 días anteriores y los ordenamos de más tranquilo a más movido. Si el valor de hoy queda entre el 70 % más movido, hay permiso. Si queda entre el 30 % más tranquilo, no. No hay un número fijo: el listón se mueve con el activo.</p>
{fig('17_atr.png', 'Izquierda (paso 1): las 48 velas anteriores a la última señal y cuánto se movió cada una; la línea negra es la media, el ATR. Derecha (paso 2): los 365 días del último año ordenados de más tranquilo a más movido; a partir del 30 % (línea verde) hay permiso, y el punto marrón es dónde cae el de hoy.')}
<h3>Cómo se aplica (lo que hace el robot cada domingo a las 23:00 UTC)</h3>
<p class="lead" style="font-size:16px">Ejemplo con la última operación del backtest ({fecha(ej['fecha'])}) y 10.000 $ de capital:</p>
<div class="atr">
<div><div class="n">PASO 1 · ATR%</div><div class="f">ATR(48) ÷ precio</div><div class="r">{num(ej['atr_pct'],2)} %</div><p>{num(ej['atr'],0)} $ de rango medio sobre un precio de {num(ej['precio'],0)} $.</p></div>
<div><div class="n">PASO 2 · PERMISO</div><div class="f">percentil en el último año</div><div class="r">{num(ej['pct']*100,0)}</div><p>{"Por encima de 30: hay permiso." if ej['pct'] >= 0.3 else "Por debajo de 30: no se opera."} Y no es el primer lunes del mes.</p></div>
<div><div class="n">PASO 3 · TAMAÑO</div><div class="f">10.000 $ × {rob} %</div><div class="r">{num(posicion,0)} $</div><p>Siempre la misma fracción del capital actual. Sin apalancar.</p></div>
<div><div class="n">PASO 4 · UNIDADES</div><div class="f">{num(posicion,0)} $ ÷ {num(ej['precio'],0)} $</div><div class="r">{num(unidades,4)} BTC</div><p>Orden a mercado a las 00:00 UTC del lunes; venta a las 00:00 del martes.</p></div>
</div>
<h3>Fracción fija frente a sizing por ATR y vol targeting</h3>
<p class="lead" style="font-size:16px">En el RSI 2 el robot dimensiona con el ATR: 1 % de riesgo con un stop virtual a 2 ATR, menos tamaño cuanto más se mueve el activo. El vol targeting hace algo parecido buscando una volatilidad diaria fija. Aquí probamos los dos y son lo contrario de lo que conviene.</p>
{fig('28_sizing_atr.png', f'Arriba: la v3 con fracción fija del {rob} % (verde) frente al sizing por ATR (morado) y al vol targeting de 1,5 % diario (naranja). En medio, la caída desde máximos de cada una. Abajo, el tamaño que cada método habría puesto cada lunes: pequeño cuando BTC se mueve, grande cuando está en calma.')}
{tabla(["", f"Fracción fija · {rob} %", "Sizing por ATR · 1 % de riesgo", "Vol targeting · 1,5 % diario"], [["Tamaño medio por operación", f"{rob} %", pct(sz["exposicion_media_atr"], 0), pct(sz["exposicion_media_vt"], 0)], ["Retorno anual (CAGR) · periodo completo", pct(trb["cagr"]), pct(f1["TODO_atr"]["cagr"]), pct(f1["TODO_vt"]["cagr"])], ["Peor caída · periodo completo", pct(trb["mdd_diario"]), pct(f1["TODO_atr"]["mdd_diario"]), pct(f1["TODO_vt"]["mdd_diario"])], ["Capital final · periodo completo", num(1 + trb["ret_total"], 2) + "×", num(1 + f1["TODO_atr"]["ret_total"], 2) + "×", num(1 + f1["TODO_vt"]["ret_total"], 2) + "×"], ["Retorno anual · validación", pct(orb["cagr"]), pct(f1["OOS_atr"]["cagr"]), pct(f1["OOS_vt"]["cagr"])], ["Profit Factor (no depende del tamaño)", num(trb["pf"]), num(f1["TODO_atr"]["pf"]), num(f1["TODO_vt"]["pf"])]])}
<div class="info">¿Por qué aquí no se dimensiona con el ATR? Porque en esta estrategia el ATR alto es la <b>señal</b>, no el riesgo: cuanto más se mueve Bitcoin, mejor paga el lunes (sección 3 y AED del manual). Un tamaño inverso a la volatilidad pone poco justo en los lunes que pagan y mucho en los que no. Por eso el tamaño es una fracción fija del capital y la fija el Monte Carlo.</div>""", "alt")

    # ------------------------------------------------------------- 7 · dónde operarla
    filas_ex = [[ex[k]["nombre"], f"{num(ex[k]['coste_lado_bps']/100,2)} %", f"{num(ex[k]['ida_vuelta_pct'],2)} %", num(ex[k]["OOS"]["pf"]), pct(ex[k]["OOS"]["cagr"]), pct(ex[k]["OOS"]["mdd_diario"]), f"<a href=\"{EXCH_URLS[k]}\">tarifas</a> · {ex[k]['nota']}"] for k in ["binance", "quantfury", "exness", "coinbase"] if k in ex]
    cb_txt = ""
    if CB:
        c1 = CB["fase1"]["OOS_robot"]
        cb_txt = f'<div class="info"><b>Comprobado con los datos del otro exchange:</b> mismo motor, misma regla, sobre las velas de Coinbase (BTC/USD) con los costes de Coinbase: {c1["n"]} operaciones fuera de muestra, Profit Factor {num(c1["pf"])}, retorno anual {pct(c1["cagr"])}. Las velas apenas difieren (precio de entrada ±{num(REC["dif_precio_entrada_pct"]["mediana"],3) if REC else "—"} % frente a MEXC en la reconciliación); lo que cambia el resultado es la comisión.</div>'
    rec_txt = f'<div class="info"><b>El robot hace lo que dice esta página:</b> el Strategy Tester de TradingView (regla original, MEXC:BTCUSDT, {fecha(REC["desde"])} → {fecha(REC["hasta"])}) coincide con el motor en {REC["emparejadas"]} de {REC["tv"]["n"]} operaciones, con una diferencia mediana de {num(REC["dif_precio_entrada_pct"]["mediana"],3)} % en el precio de entrada y de {num(REC["dif_retorno_pp"]["mediana"],3)} puntos en el retorno por operación. El motor tiene {len(REC["solo_motor"])} operaciones más: lunes en los que el filtro queda en el límite con velas de Binance frente a MEXC.</div>' if REC else ""
    rec_v3_txt = (f'<div class="info"><b>La v3 en TradingView es la misma que la del motor:</b> el Strategy Tester (BINANCE:BTCUSDT 1H, {fecha(REC_V3["desde"])} → {fecha(REC_V3["hasta"])}, 0,14 % por lado, {rob} % del equity) '
                  f'coincide con el motor en {REC_V3["emparejadas"]} de {REC_V3["motor"]["n"]} operaciones, mismo lunes y mismo precio de entrada (diferencia mediana {num(REC_V3["dif_precio_entrada_pct"]["mediana"],3)} %), '
                  f'con Profit Factor {num(REC_V3["tv"]["pf"])} frente a {num(REC_V3["motor"]["pf"])} del motor.</div>') if REC_V3 else ""
    mt5_rec = (f'Reconciliado con el Strategy Tester de MetaTrader 5 (Exness, {fecha(REC_MT5["desde"])} → {fecha(REC_MT5["hasta"])}): {REC_MT5["emparejadas"]} de {REC_MT5["mt5"]["n"]} operaciones el mismo lunes; antes de operarlo en otra cuenta, repite la prueba en su tester.'
               if REC_MT5 else 'Antes de operarlo en una cuenta, se reconcilia con su Strategy Tester.')
    rec_mt5_txt = (f'<div class="info"><b>Y el robot de MetaTrader 5 también:</b> en el Strategy Tester de Exness (BTCUSDz, historial desde enero de 2021) el EA compra todos los lunes a las 00:00 UTC y cierra 24 horas después; '
                   f'{REC_MT5["emparejadas"]} de {REC_MT5["mt5"]["n"]} operaciones coinciden con el motor, con una diferencia mediana de {num(REC_MT5["dif_precio_entrada_pct"]["mediana"],3)} % en el precio de entrada y una correlación de {num(REC_MT5["dif_retorno_bruto_pp"]["correlacion"],2)} en el retorno. '
                   f'Las {len(REC_MT5["solo_mt5"]) + len(REC_MT5["solo_motor"])} restantes son lunes con el percentil justo en el límite del 30 o de 2021, cuando la ventana del CFD aún no tenía un año de historia.</div>') if REC_MT5 else ""
    donde = sec("donde", "7 · Dónde operarla", "Qué necesitas, cuánto cuesta en cada sitio y cómo es un lunes",
                "Pensada para Bitcoin en velas de 1 hora UTC. Vale como CFD en MetaTrader 5 (Exness, Axi u otro bróker con BTCUSD) o al contado en un exchange (Binance, Quantfury); lo que cambia, y mucho, es la comisión. Tres formas de hacerlo, de más a menos automática, y las tres reconciliadas con el motor.",
                f"""<div class="vias">
<div class="via v1"><div class="ico">🤖</div><span class="tag">Recomendada</span><h4>Con el robot en MetaTrader 5</h4><ul><li>El EA (MQL5, en la sección 8) corre en un gráfico H1 de BTCUSD en un servidor 24/7: calcula el filtro de volatilidad, el calendario, compra a las 00:00 UTC del lunes y cierra a las 00:00 del martes.</li><li>Tamaño: {rob} % del equity, sin apalancar. Si el {rob} % no llega al lote mínimo, no opera.</li><li>Un parámetro elige el horario del servidor: GMT+2/+3 con el verano de EE. UU. (Axi, IC Markets…) o un desfase fijo (Exness = 0). En cuenta real comprueba solo que coincide con el servidor.</li><li>Lo hace todo solo. {mt5_rec}</li></ul></div>
<div class="via v2"><div class="ico">🔔</div><span class="tag">Con alertas</span><h4>TradingView</h4><ul><li>El script de Pine (v3) calcula el permiso y lanza una alerta al cierre de la vela del domingo 23:00 UTC: compra, venta o "este lunes no se opera" con el motivo.</li><li>Puedes ejecutar la orden tú en tu exchange (Binance, Quantfury u otro) o conectar la alerta a tu propia automatización; el martes, la alerta de venta.</li><li>Nuestra referencia: así opera la v1 en real desde {fecha(meta['live_desde'])}.</li></ul></div>
<div class="via v3"><div class="ico">✍️</div><span class="tag">Manual</span><h4>A mano, con la alerta o con el motor</h4><ul><li>El script de Pine te avisa en el móvil ("LONG" o "sin permiso"), o corres el motor del repositorio el domingo por la noche.</li><li>Compras a las 00:00 UTC y vendes 24 h después. Dos acciones a la semana.</li><li><b>Solo recomendable si estás aprendiendo</b>: el objetivo es escalar y despegarte de la pantalla.</li></ul></div>
</div>
<h3>Un lunes en la vida de la estrategia</h3>
<div class="flujo">
<div><div class="ic">🕚</div><b>Domingo 23:00 UTC</b><span>cierra la vela de señal (01:00 en España en invierno)</span></div>
<div><div class="ic">📏</div><b>¿ATR% sobre el percentil 30?</b><span>si no, no hay nada que hacer</span></div>
<div><div class="ic">📅</div><b>¿Es el primer lunes del mes?</b><span>si sí, se deja pasar</span></div>
<div><div class="ic">🛒</div><b>Compra a las 00:00 UTC</b><span>{rob} % del capital, a mercado (el EA lo hace solo)</span></div>
<div><div class="ic">🏁</div><b>Venta martes 00:00 UTC</b><span>24 velas · sin mirar en medio</span></div>
</div>
<h3>Lo que cambia el exchange: mismas velas, misma regla, cuatro perfiles de coste</h3>
{tabla(["Exchange", "Coste por lado", "Ida y vuelta", "PF · validación", "Retorno anual · validación", "Peor caída · validación", "Tarifa (leída el " + fecha(FECHA_TARIFAS) + ")"], filas_ex)}
{fig('25_exchanges.png', 'La v3 al 40 % con las velas de Binance y los costes de cada exchange; en naranja discontinuo, además, con las velas del propio Coinbase. Con 0,60 % por lado el lunes no cubre el coste: antes de elegir dónde operar, mira la comisión. En morado, Exness (CFD en MetaTrader 5): spread, comisión y el swap de una noche.')}
<div class="cfd">
<div><h5>💱 Spot (Binance, Coinbase)</h5><ul><li>Compras Bitcoin de verdad; sin swap ni funding.</li><li>Pagas comisión por lado: de 0,10 % a 0,60 % según el exchange y tu volumen. Es la variable que decide la estrategia.</li><li>Sin apalancamiento: el nivel "Decidido" es el máximo.</li></ul></div>
<div><h5>📈 Futuros perpetuos o CFD (Binance Futures, Quantfury)</h5><ul><li>Comisión más baja o cero; a cambio, funding cada 8 h o spread algo mayor.</li><li>Permiten apalancar: no lo hagas por encima del nivel que elegiste.</li><li>Quantfury cotiza al precio spot del exchange sin comisión: es el coste más bajo de los cuatro.</li><li>En un CFD de MetaTrader 5 (Exness) pagas spread, una comisión pequeña y el swap de la noche del lunes: la operación cruza siempre un cierre diario.</li></ul></div>
</div>{cb_txt}{rec_txt}{rec_v3_txt}{rec_mt5_txt}""")

    # ------------------------------------------------------------- 8 · recursos
    pine_btn = f'<a class="btn" href="{PINE_URL}">Abrir en TradingView →</a>' if PINE_URL else '<a class="btn off">Publicación en TradingView pendiente</a>'
    recursos = sec("recursos", "8 · Recursos", "El código, completo y a la vista",
                   "El robot para MetaTrader 5, el script para TradingView, la v1 que opera en real, el motor de backtest en Python y los resultados reproducibles.",
                   f"""<div class="rec-big">
<div class="recb r1"><div class="head"><div class="ico">🤖</div><h4>Robot para MetaTrader 5</h4><span>MQL5 · v3 · v1.1 · reconciliado con el Strategy Tester</span></div><div class="cuerpo"><p>EA completo: filtro de volatilidad por percentil, calendario, compra lunes 00:00 UTC, cierre martes 00:00 UTC, {rob} % del equity. Despliégalo abajo o descárgalo {"(.mq5 y .ex5)" if (RAIZ / "codigo" / "TIS_BTC_Lunes_v3.ex5").exists() else "(.mq5; compílalo en MetaEditor con F7)"}.</p><a class="btn sec" href="{REPO_URL}/blob/HEAD/codigo/TIS_BTC_Lunes_v3.mq5">Descargar del repositorio</a></div></div>
<div class="recb r2"><div class="head"><div class="ico">🔔</div><h4>Script para TradingView</h4><span>Pine Script v6 · v3 · señales y alertas · y la v1 original</span></div><div class="cuerpo"><p>La misma regla, con las señales en el gráfico y alertas de entrada y salida. Junto a ella, la v1 de 2025 tal cual, para que se vea de dónde viene la v3.</p><a class="btn sec" href="{REPO_URL}/blob/HEAD/codigo/TIS_BTC_Lunes_v3.pine">Descargar del repositorio</a> {pine_btn}</div></div>
<div class="recb r3"><div class="head"><div class="ico">🐍</div><h4>Motor de backtest</h4><span>Python · Sentinel · reproducible</span></div><div class="cuerpo"><p>Descarga las velas de Binance y Coinbase, reproduce el backtest y revisa las cinco fases, el AED y la revisión con el mismo motor.</p><a class="btn sec" href="{REPO_URL}">Ir al repositorio</a></div></div>
</div>
<details class="code"><summary><span class="tag">MQL5</span> TIS_BTC_Lunes_v3.mq5 · robot para MetaTrader 5 <span class="arrow">▼</span></summary><div class="body">
<div class="meta">Parámetros de la validación (ATR 48 · percentil 30 sobre 8.760 velas · sin primer lunes del mes · {rob} % del equity). Cárgalo en un gráfico H1 de BTCUSD con al menos un año de historia (Máx. barras en el gráfico ≥ 10.000) y elige en ModoHorario el horario de tu servidor: GMT+2/+3 con el verano de EE. UU. (Axi, IC Markets, Pepperstone…) o desfase fijo con OffsetFijoUTC (Exness = 0). <button class="copiar">Copiar</button></div>
<pre><code>{html.escape(EA_MT5)}</code></pre></div></details>
<details class="code"><summary><span class="tag">Pine v6</span> TIS_BTC_Lunes_v3.pine · el script para TradingView <span class="arrow">▼</span></summary><div class="body">
<div class="meta">Parámetros de la validación (ATR 48 · percentil 30 sobre 8.760 velas · sin primer lunes del mes · 40 %). Alertas de texto en la entrada, en la salida y los domingos sin entrada (con el motivo). Cárgalo en un gráfico de 1 hora de BINANCE:BTCUSDT: el script lee las horas en UTC sea cual sea la zona del gráfico. Comisión 0,14 % por lado, el coste del motor. <button class="copiar">Copiar</button></div>
<pre><code>{html.escape(PINE_V3)}</code></pre></div></details>
<details class="code"><summary><span class="tag">Pine v6</span> TIS_BTC_Lunes_v1_original.pine · la v1 de 2025 que opera en real <span class="arrow">▼</span></summary><div class="body">
<div class="meta">Filtros fijos: ATR% entre 0,40 y 1,20 y |retorno 24 h| ≤ 4 %. Comisión 0 en el Tester (la guía la añade). <button class="copiar">Copiar</button></div>
<pre><code>{html.escape(PINE_V1)}</code></pre></div></details>
<details class="code"><summary><span class="tag">Python</span> La señal en 15 líneas · lo que hace el motor por dentro <span class="arrow">▼</span></summary><div class="body">
<div class="meta">Extracto del motor. Señal en la vela de las 23:00 UTC del domingo, ejecución en la apertura de las 00:00 del lunes, salida en la apertura del martes, 14 puntos básicos de coste por lado. <button class="copiar">Copiar</button></div>
<pre><code>{html.escape('''atr_pct = ATR(df, 48) / close * 100                       # rango medio de 48 velas, en % del precio
pct     = atr_pct.rolling(8760, min_periods=500).rank(pct=True)   # dónde está dentro de su último año (0–1)

for lunes in lunes_00h_utc:                                 # cada lunes a las 00:00 UTC
    s = lunes - 1h                                          # la vela de señal: domingo 23:00
    if pct[s] < 0.30:        continue                       # sin permiso: calma
    if lunes.day <= 7:       continue                       # primer lunes del mes
    precio_entrada = open[lunes] * (1 + 0.0014)             # compra a mercado, con coste
    precio_salida  = open[lunes + 24h] * (1 - 0.0014)       # venta 24 velas después
    retorno = precio_salida / precio_entrada - 1
    capital *= 1 + 0.40 * retorno                           # 40 % del capital por operación''')}</code></pre></div></details>
<div class="cta-final" style="margin-top:32px"><div><h3>Manual avanzado: cómo la validamos</h3><p>El AED por eras, las cinco fases con sus números, la revisión completa (horas, duración, salidas, filtros), el test del mono, el Monte Carlo por tamaño, los drawdowns y la vigilancia en real. Mismos datos, mismo motor.</p></div><a class="btn" href="btc-lunes-validacion.html">Abrir el manual avanzado →</a></div>""", "alt")

    cuerpo = hero + ficha_tec + hipo + descubrimiento + origen + camino + riesgo_sec + donde + recursos
    nav = [("reglas", "Reglas"), ("hipotesis", "Hipótesis"), ("descubrimiento", "El edge"), ("origen", "Origen"), ("camino", "Camino"), ("riesgo", "Riesgo"), ("donde", "Dónde"), ("recursos", "Código")]
    return pagina("BTC · Efecto Lunes — Trade It Simple", "Estrategia estacional sobre Bitcoin: el lunes con permiso de volatilidad. Reglas, resultado, cómo descubrimos el edge, origen, riesgo, dónde operarla y código.", nav, cuerpo, ("btc-lunes-validacion.html", "Manual avanzado →"), CSS_FICHA)
