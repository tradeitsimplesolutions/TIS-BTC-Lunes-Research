"""Los gráficos de la guía (PNG en resultados/graficos/). Los llama btc_lunes_motor.py; cada uno dice en el título qué demuestra."""
import json
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path(__file__).resolve().parent.parent / "resultados"
VERDE, VERDE2, GRIS, ROJO, TINTA, AZUL, NARANJA, MORADO = "#0e9c58", "#26d97e", "#95a29b", "#c8512f", "#132620", "#2b6cb0", "#c97d1e", "#7a4fb8"
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
PER = [("construccion", "construcción (hasta el corte)", GRIS), ("validacion", "validación (fuera de muestra)", AZUL), ("real", "en real (desde feb-2025)", VERDE)]


def graficos(df, ta, tb, tp, sp_date, res, raw):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.ticker
    import matplotlib.pyplot as plt, matplotlib.dates as mdates
    from scipy.stats import gaussian_kde, norm as _norm
    G = OUT / "graficos"; G.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": "#c2d0c8", "axes.labelcolor": "#3a4b44", "xtick.color": "#3a4b44",
                         "ytick.color": "#3a4b44", "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e2ede8",
                         "grid.linewidth": 0.6, "figure.facecolor": "white", "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left"})
    LIVE = pd.Timestamp(res["meta"]["live_desde"]); eq = res["_eq"]; eq_cap, eq_rob, eq_fijo, eq_p20, eq_x2 = eq["capital"], eq["robot"], eq["fijo"], eq["p20"], eq["x2"]

    def guardar(fig, nombre):
        fig.savefig(G / nombre, dpi=150, bbox_inches="tight"); plt.close(fig)

    def eje_log(ax, top, lo=0.5):
        """Escala lineal con marcas en × (el log aplasta curvas que van de 0,8× a 5×); el nombre se mantiene por compatibilidad."""
        ax.set_ylim(max(0, lo * 0.9), top * 1.08); paso = 0.25 if top < 2.2 else (0.5 if top < 4 else 1.0)
        ticks = np.arange(np.floor(lo * 4) / 4, top * 1.08 + paso, paso); ax.set_yticks(ticks); ax.set_yticklabels([f"{t:g}×" for t in ticks])
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines

    def sombras(ax):
        ax.axvspan(sp_date, df.index[-1], color="#eef6f1", zorder=0); ax.axvline(LIVE, color=ROJO, ls=":", lw=1.2)
        lo, hi = ax.get_ylim(); y2 = hi - (hi - lo) * 0.08
        ax.text(sp_date, hi, "  fuera de muestra →", va="top", color="#3a4b44", fontsize=9.5)
        ax.text(LIVE, y2, "  en real →", va="top", color=ROJO, fontsize=9.5)

    # 01 equity: robot 40 % · 100 % · 10.000 $ fijos + drawdown del robot
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.8), height_ratios=[3, 1.2], sharex=True)
    l1, = a1.plot(eq_rob.index, eq_rob.values, color=VERDE, lw=2); l2, = a1.plot(eq_cap.index, eq_cap.values, color=NARANJA, lw=1.4); l3, = a1.plot(eq_fijo.index, eq_fijo.values, color=AZUL, lw=1.4)
    eje_log(a1, max(eq_cap.max(), eq_rob.max()), min(0.5, eq_cap.min())); sombras(a1); a1.set_ylabel("Capital (1 = inicial)")
    for e, col, nom in [(eq_rob, VERDE, "40 % · el robot"), (eq_cap, NARANJA, "100 % del capital"), (eq_fijo, AZUL, "10.000 $ fijos")]:
        a1.text(e.index[-1], e.iloc[-1], f"  {nom} · {e.iloc[-1]:.2f}×", color=col, va="center", fontweight="bold", fontsize=10)
    a1.legend([l1, l2, l3], ["40 % del capital por operación (lo que opera el robot, reinvirtiendo)", "100 % del capital (referencia)", "10.000 $ fijos por operación (sin reinvertir)"], loc="upper left", frameon=False, fontsize=9.5)
    a1.set_title("BTC · Efecto Lunes v3 — curva de capital con tres tamaños de posición"); a1.set_xlim(eq_cap.index[0], eq_cap.index[-1] + pd.Timedelta(days=520))
    dd = (eq_rob - eq_rob.cummax()) / eq_rob.cummax() * 100
    a2.fill_between(dd.index, dd.values, 0, color=ROJO, alpha=0.25, lw=0); a2.plot(dd.index, dd.values, color=ROJO, lw=1); a2.set_ylabel("Drawdown % (40 %)"); a2.xaxis.set_major_locator(mdates.YearLocator(1))
    guardar(fig, "01_equity.png")

    # 01b Fase 1: la curva al 40 % con construcción / validación / real sombreados y cada operación como barra
    f1 = res["fase1"]; o_, oo_ = f1["IS_robot"], f1["OOS_robot"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 7.4), height_ratios=[2.6, 1.1], sharex=True)
    a1.axvspan(df.index[0], sp_date, color="#f1f3f2", zorder=0); a1.axvspan(sp_date, df.index[-1], color="#eef6f1", zorder=0); a1.axvline(LIVE, color=ROJO, ls=":", lw=1.2)
    a1.plot(eq_rob.index, eq_rob.values, color=VERDE, lw=2.2); eje_log(a1, eq_rob.max(), min(0.8, eq_rob.min())); a1.set_ylabel("Capital (40 %, 1 = inicial)")
    hi_ = a1.get_ylim()[1]
    a1.text(df.index[0] + pd.Timedelta(days=20), hi_ * 0.985, f"CONSTRUCCIÓN · 70 % de las velas\n{o_['n']} operaciones · PF {o_['pf']:.2f} · caída máx. {o_['mdd']*100:.1f} %", va="top", fontsize=9.5, color="#3a4b44", fontweight="bold")
    a1.text(sp_date + pd.Timedelta(days=20), hi_ * 0.985, f"VALIDACIÓN · 30 % final, sin mirar\n{oo_['n']} operaciones · PF {oo_['pf']:.2f} · caída máx. {oo_['mdd']*100:.1f} %", va="top", fontsize=9.5, color=VERDE, fontweight="bold")
    a1.text(LIVE + pd.Timedelta(days=10), hi_ * 0.86, "en real →", color=ROJO, fontsize=9.5)
    a1.set_title("Fase 1 · El backtest: la misma regla, primero en construcción y después en los datos guardados (40 % del capital, costes de Binance)", fontsize=11.5)
    rr = [t["ret"] * 100 for t in ta]; ff = [t["entrada"] for t in ta]
    a2.bar(ff, rr, width=6, color=[VERDE if v > 0 else ROJO for v in rr]); a2.axhline(0, color=TINTA, lw=0.8); a2.axvspan(sp_date, df.index[-1], color="#eef6f1", zorder=0)
    a2.set_ylabel("cada operación (%, al 100 %)"); a2.set_title("Las operaciones una a una: verde gana, rojo pierde", fontsize=10); a2.xaxis.set_major_locator(mdates.YearLocator(1))
    fig.tight_layout(); guardar(fig, "01b_backtest.png")

    # 02 operaciones de un año sobre velas diarias, con flechas estilo MetaTrader y las entradas filtradas rotuladas
    y = pd.Timestamp.today().year - 1; dh = raw[(raw.index >= f"{y}-01-01") & (raw.index <= f"{y}-12-31")]
    dd1 = dh.resample("D").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna()
    tr_y = [t for t in ta if t["entrada"].year == y]; filtrados = [t for t in tb if t["entrada"].year == y and t["entrada"] not in {x["entrada"] for x in tr_y}]
    fig, ax = plt.subplots(figsize=(13, 6.2))
    for dt, row in dd1.iterrows():
        col = "#8fbf9f" if row["Close"] >= row["Open"] else "#e4a393"; x = mdates.date2num(dt)
        ax.plot([dt, dt], [row["Low"], row["High"]], color=col, lw=0.8); ax.add_patch(plt.Rectangle((x - 0.35, min(row["Open"], row["Close"])), 0.7, abs(row["Close"] - row["Open"]) or 1, color=col))
    for t in tr_y:
        ax.annotate("", xy=(t["entrada"], t["px_ent"]), xytext=(t["entrada"], t["px_ent"] * 0.955), arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=2.2, mutation_scale=18))
        ax.annotate("", xy=(t["salida"], t["px_sal"]), xytext=(t["salida"], t["px_sal"] * 1.045), arrowprops=dict(arrowstyle="-|>", color=ROJO, lw=2.2, mutation_scale=18))
        ax.plot([t["entrada"], t["salida"]], [t["px_ent"], t["px_sal"]], color=VERDE if t["ret"] > 0 else ROJO, lw=1.6, ls=":", alpha=0.9)
    for t in filtrados:
        ax.plot([t["entrada"]], [t["px_ent"] * 0.955], marker="x", ms=7, color=GRIS, mew=1.8)
    if filtrados:
        ents = [x["entrada"] for x in tr_y]
        f0 = max(filtrados, key=lambda t: min([abs((t["entrada"] - e).days) for e in ents] or [0]))
        ax.annotate("entrada filtrada" + chr(10) + "(sin permiso o primer lunes)", xy=(f0["entrada"], f0["px_ent"] * 0.955), xytext=(28, -52), textcoords="offset points", ha="left", fontsize=8.5, color="#3a4b44", arrowprops=dict(arrowstyle="->", color=GRIS))
    ax.legend([mlines.Line2D([], [], color=AZUL, marker="^", ls="", ms=10), mlines.Line2D([], [], color=ROJO, marker="v", ls="", ms=10), mlines.Line2D([], [], color=GRIS, marker="x", ls="", ms=8, mew=1.8), mlines.Line2D([], [], color=VERDE, ls=":"), mlines.Line2D([], [], color=ROJO, ls=":")],
              ["Compra · lunes 00:00 UTC", "Venta · martes 00:00 UTC", "Entrada filtrada: lunes sin permiso", "Operación ganadora", "Operación perdedora"], frameon=False, loc="upper left", fontsize=9.5)
    ax.set_title(f"Así se ven las operaciones — BTC en {y}, velas diarias: {len(tr_y)} lunes operados, {len(filtrados)} filtrados"); ax.set_ylabel("BTC/USDT"); ax.xaxis.set_major_locator(mdates.MonthLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    guardar(fig, "02_operaciones_ano.png")

    # 03 versiones: base · Pine 2025 · v3 (todas al 40 %)
    eb, ep = res["_eq_base"], res["_eq_pine"]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    l1, = ax.plot(eq_rob.index, eq_rob.values, color=VERDE, lw=2.2); l2, = ax.plot(ep.index, ep.values, color=AZUL, lw=1.6); l3, = ax.plot(eb.index, eb.values, color=GRIS, lw=1.4)
    eje_log(ax, max(eq_rob.max(), ep.max(), eb.max()), min(0.5, eb.min())); sombras(ax)
    etiquetas = sorted([(e.iloc[-1], col, nom, e) for e, col, nom in [(eq_rob, VERDE, "v3"), (ep, AZUL, "v1 original"), (eb, GRIS, "lunes desnudo")]], key=lambda x: x[0])
    ys = [x[0] for x in etiquetas]
    for i in range(1, len(ys)):                                   # separa las etiquetas que caen casi en el mismo sitio
        if ys[i] - ys[i - 1] < 0.07: ys[i] = ys[i - 1] + 0.07
    for (val, col, nom, e), y in zip(etiquetas, ys):
        ax.text(e.index[-1], y, f"  {nom} · {val:.2f}×", color=col, fontweight="bold", va="center", fontsize=10)
    ax.legend([l3, l2, l1], ["Lunes desnudo: todos los lunes, sin filtro", "v1 original (2025): ATR% 0,40–1,20 y |ret 24h| ≤ 4 %, la que opera en real", "v3 validada: ATR% sobre el percentil 30 de su año, sin el primer lunes del mes"], frameon=False, loc="upper left", fontsize=9.5)
    ax.set_title("Lunes desnudo, v1 y v3: las mismas velas, los mismos costes y el mismo tamaño (40 %)"); ax.set_xlim(eq_rob.index[0], eq_rob.index[-1] + pd.Timedelta(days=430)); ax.set_ylabel("Capital (1 = inicial)")
    guardar(fig, "03_versiones.png")

    # 04 grid de horas
    g = res["fase3"]; pf = np.array(g["pf"]); nn = np.array(g["n"]); OF = g["off_in"]
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    im = ax.imshow(pf, cmap="RdYlGn", vmin=0.8, vmax=max(1.6, np.nanmax(pf)), aspect="auto")
    ax.set_xticks(range(5)); ax.set_xticklabels([f"salida {o:+d} h" for o in OF]); ax.set_yticks(range(5)); ax.set_yticklabels([f"entrada {o:+d} h" for o in OF]); ax.grid(False)
    for a in range(5):
        for b in range(5): ax.text(b, a, f"{pf[a,b]:.2f}\nN={int(nn[a,b])}", ha="center", va="center", fontsize=9, color=TINTA)
    ax.add_patch(plt.Rectangle((1.5, 1.5), 1, 1, fill=False, ec=TINTA, lw=3))
    ax.set_title("Zonas robustas — Profit Factor en construcción al mover la hora de entrada y de salida\n(0 h = lunes 00:00 → martes 00:00 UTC; recuadro = la que opera)", fontsize=11.5)
    fig.colorbar(im, ax=ax, label="Profit Factor (construcción)", shrink=0.8); guardar(fig, "04_grid.png")

    # 05 Monte Carlo (40 %)
    mc = res["fase4"]; n_tr = mc["_caminos"].shape[1]; xi = np.arange(1, n_tr + 1)
    fig = plt.figure(figsize=(13, 9)); gs = fig.add_gridspec(2, 2, height_ratios=[1.6, 1]); a0 = fig.add_subplot(gs[0, :]); a1 = fig.add_subplot(gs[1, 0]); a2 = fig.add_subplot(gs[1, 1])
    for cam in mc["_caminos"]: a0.plot(xi, cam, color=GRIS, lw=0.4, alpha=0.25)
    b = mc["_bandas"]; a0.fill_between(xi, b[0], b[4], color=VERDE, alpha=0.12, lw=0); a0.fill_between(xi, b[1], b[3], color=VERDE, alpha=0.18, lw=0)
    a0.plot(xi, b[2], color=VERDE, lw=1.6, ls="--"); a0.plot(xi, mc["_real"], color=TINTA, lw=2.2); a0.plot(xi, mc["_peor"], color=ROJO, lw=1.6)
    eje_log(a0, max(mc["_real"].max(), b[4].max()), 0.5); arriba = mc["_real"][-1] >= b[2][-1]
    a0.text(n_tr, mc["_real"][-1], f"  real · {mc['_real'][-1]:.2f}×", color=TINTA, fontweight="bold", va="bottom" if arriba else "top")
    a0.text(n_tr, b[2][-1], f"  mediana · {b[2][-1]:.2f}×", color=VERDE, fontweight="bold", va="top" if arriba else "bottom")
    a0.text(n_tr, mc["_peor"][-1], f"  peor drawdown · {mc['mdd_peor']*100:.0f} %", color=ROJO, fontweight="bold", va="center")
    a0.set_xlim(1, n_tr * 1.14); a0.set_xlabel("Número de operación"); a0.set_ylabel("Capital (escala log)")
    a0.set_title(f"{mc['n_sim']:,} reordenaciones de las {n_tr} operaciones reales, al 40 % · 400 dibujadas · bandas 5–95 % y 25–75 %".replace(",", "."))
    a0.legend([plt.Line2D([], [], color=GRIS, lw=1), plt.Line2D([], [], color=VERDE, lw=1.6, ls="--"), plt.Line2D([], [], color=TINTA, lw=2.2), plt.Line2D([], [], color=ROJO, lw=1.6)],
              ["Un camino posible", "Mediana de todos", "El camino real", "El camino con el peor drawdown"], loc="upper left", frameon=False, fontsize=9.5)
    a1.hist(mc["_rets"] * 100, bins=60, color=VERDE2, alpha=0.8, ec="white"); a1.axvline(mc["p5_ret"] * 100, color=TINTA, ls="--")
    a1.text(mc["p5_ret"] * 100, a1.get_ylim()[1] * 0.9, f" 5 % peor: {mc['p5_ret']*100:+.0f} %", color=TINTA, fontsize=9); a1.set_title("Retorno total de cada camino", fontsize=11); a1.set_xlabel("Retorno total (%)")
    a2.hist(mc["_mdds"] * 100, bins=60, color="#f0a860", alpha=0.85, ec="white"); a2.axvline(-25, color=ROJO, ls="--"); a2.text(-25, a2.get_ylim()[1] * 0.9, " límite −25 % ", color=ROJO, ha="right", fontsize=9)
    a2.axvline(mc["mdd_p5"] * 100, color=TINTA, ls="--"); a2.text(mc["mdd_p5"] * 100, a2.get_ylim()[1] * 0.72, f" 5 % peor: {mc['mdd_p5']*100:.1f} %", color=TINTA, fontsize=9)
    a2.axvline(mc["mdd_peor"] * 100, color=ROJO, lw=2); a2.text(mc["mdd_peor"] * 100, a2.get_ylim()[1] * 0.5, f" el peor: {mc['mdd_peor']*100:.1f} %", color=ROJO, fontsize=9)
    a2.set_title("Drawdown máximo de cada camino", fontsize=11); a2.set_xlabel("Drawdown máximo (%)"); fig.tight_layout(); guardar(fig, "05_montecarlo.png")

    # 06 mono
    mk = res["monkey"]; nm = mk["_curvas"].shape[1]; xm = np.arange(1, nm + 1)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.35, 1]))
    for cv in mk["_curvas"]: a1.plot(xm, cv, color=GRIS, lw=0.5, alpha=0.35)
    med = np.median(mk["_curvas"], axis=0); a1.plot(xm, med, color=MORADO, lw=1.8, ls="--"); a1.plot(xm, mk["_real"], color=VERDE, lw=2.4)
    eje_log(a1, max(mk["_real"].max(), mk["_curvas"].max()), 0.5)
    a1.text(nm, mk["_real"][-1], f"  estrategia · {mk['_real'][-1]:.2f}×", color=VERDE, fontweight="bold", va="center"); a1.text(nm, med[-1], f"  mono mediano · {med[-1]:.2f}×", color=MORADO, fontweight="bold", va="center")
    a1.set_xlim(1, nm * 1.22); a1.set_xlabel("Número de operación"); a1.set_ylabel("Capital (escala log, 100 %)"); a1.set_title("250 monos comprando 24 h un día cualquiera (gris) frente a la estrategia (verde)", fontsize=11)
    cnt, edges, _ = a2.hist(mk["_pfs"], bins=45, color="#c2d0c8", ec="white")
    xs = np.linspace(mk["_pfs"].min(), max(mk["_pfs"].max(), mk["pf_real"] * 1.05), 300); a2.plot(xs, gaussian_kde(mk["_pfs"])(xs) * len(mk["_pfs"]) * (edges[1] - edges[0]), color=MORADO, lw=2)
    a2.axvline(mk["pf_mono_mediana"], color=MORADO, ls="--"); a2.axvline(mk["pf_real"], color=VERDE, lw=3)
    a2.text(mk["pf_real"], a2.get_ylim()[1] * 0.9, f" estrategia · PF {mk['pf_real']:.2f}\n supera al {mk['pct_pf']*100:.1f} %", color=VERDE, fontweight="bold", fontsize=9.5, ha="right")
    a2.text(mk["pf_mono_mediana"], a2.get_ylim()[1] * 0.55, f" mono mediano · {mk['pf_mono_mediana']:.2f}", color=MORADO, fontsize=9.5)
    a2.set_title(f"Profit Factor de los {mk['n_sim']:,} monos".replace(",", "."), fontsize=11); a2.set_xlabel("Profit Factor"); a2.set_ylabel("Monos"); fig.tight_layout(); guardar(fig, "06_monkey.png")

    # 07 desgaste: el PF móvil como electrocardiograma con bandas de salud
    ed = res["edge_decay"]["anual"]; mv = res["edge_decay"]["movil"]; fx = pd.to_datetime([m["fecha"] for m in mv]); fy = np.array([m["pf"] for m in mv])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 7), height_ratios=[2.4, 1], sharex=True); top = min(5, fy.max() * 1.1)
    a1.axhspan(1.3, top, color=VERDE, alpha=0.08, lw=0); a1.axhspan(1.0, 1.3, color="#f0a860", alpha=0.18, lw=0); a1.axhspan(0, 1.0, color=ROJO, alpha=0.12, lw=0)
    a1.plot(fx, fy, color=TINTA, lw=2.2); a1.axhline(1, color=ROJO, lw=1); a1.axhline(1.3, color="#9a5a15", lw=1, ls="--"); a1.axvline(sp_date, color=TINTA, ls=":", lw=1); a1.axvline(LIVE, color=ROJO, ls=":", lw=1.2)
    a1.text(fx[0], top * 0.96, " SANO · PF > 1,3: gana con margen", color=VERDE, fontsize=9.5, va="top", fontweight="bold"); a1.text(fx[0], 1.15, " VIGILAR · entre 1 y 1,3: gana poco", color="#9a5a15", fontsize=9.5, fontweight="bold"); a1.text(fx[0], 0.45, " PERDIENDO · PF < 1", color=ROJO, fontsize=9.5, fontweight="bold")
    a1.text(sp_date, top * 0.75, " validación →", fontsize=9, color="#3a4b44"); a1.text(LIVE, top * 0.66, " en real →", fontsize=9, color=ROJO)
    a1.set_ylim(0, top); a1.set_ylabel("Profit Factor de las últimas 40 operaciones"); a1.set_title("El electrocardiograma del edge: Profit Factor de las últimas 40 operaciones, con sus bandas de salud", fontsize=11.5)
    a2.bar([pd.Timestamp(f"{f['ano']}-07-01") for f in ed], [f["n"] for f in ed], width=250, color=[VERDE if f["pf"] >= 1 else ROJO for f in ed])
    for f in ed: a2.text(pd.Timestamp(f"{f['ano']}-07-01"), f["n"] + 0.4, f"{f['n']}\nPF {f['pf']:.2f}", ha="center", fontsize=8, color="#3a4b44")
    a2.set_ylim(0, max(f["n"] for f in ed) * 1.45); a2.set_ylabel("Operaciones por año"); a2.set_title("Cuántas veces opera cada año (verde: año ganador, rojo: perdedor). 2017 es corto: el percentil necesita un año de datos", fontsize=10); a2.xaxis.set_major_locator(mdates.YearLocator(1))
    fig.tight_layout(); guardar(fig, "07_pf_anual.png")

    # 08 underwater (robot)
    fig, ax = plt.subplots(figsize=(11, 3.8)); ax.fill_between(dd.index, dd.values, 0, color=ROJO, alpha=0.25, lw=0); ax.plot(dd.index, dd.values, color=ROJO, lw=1)
    ax.axvline(sp_date, color=TINTA, ls=":", lw=1); ax.axvline(LIVE, color=ROJO, ls=":", lw=1); ax.set_ylabel("Caída desde el máximo (%)"); ax.set_title("Curva submarina — cuánto tiempo pasa la cuenta por debajo de su máximo (40 % del capital)"); guardar(fig, "08_underwater.png")

    # 09 walk-forward
    wf = res["fase2"]["ventanas"]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    bars = ax.bar([v["ano"] for v in wf], [v["ret_oos"] * 100 for v in wf], color=[VERDE if v["ret_oos"] > 0 else ROJO for v in wf], width=0.7)
    l, = ax.plot([v["ano"] for v in wf], [v["ret_is_anual"] * 100 for v in wf], color=TINTA, lw=1.5, marker="o", ms=4); ax.axhline(0, color=TINTA, lw=1); ax.set_ylabel("Retorno del año (%, al 40 %)")
    ax.legend([bars, l], ["Año examinado (reglas fijas)", "Media anual de los 3 años previos"], frameon=False); ax.set_title("Walk-forward con reglas fijas — cada año examinado contra los tres anteriores"); guardar(fig, "09_walkforward.png")

    # 10 cuatro niveles: solo la caída desde máximos (la curva de capital es interactiva en la ficha)
    fig, a2 = plt.subplots(figsize=(11, 4.6))
    for e, col, nom in [(eq_x2, ROJO, "Arriesgado · 1:2"), (eq_cap, NARANJA, "Decidido · 100 %"), (eq_rob, VERDE, "Robot · 40 %"), (eq_p20, AZUL, "Conservador · 20 %")]:
        d_ = (e - e.cummax()) / e.cummax() * 100; a2.fill_between(d_.index, d_.values, 0, color=col, alpha=0.16, lw=0); a2.plot(d_.index, d_.values, color=col, lw=1.2, label=f"{nom} · peor {d_.min():.0f} %")
    sombras(a2); a2.legend(loc="lower left", frameon=False, fontsize=9.5); a2.set_ylabel("Caída desde máximos (%)"); a2.set_title("Lo que se ve en la cuenta: la caída desde máximos de cada tamaño")
    a2.xaxis.set_major_locator(mdates.YearLocator(1)); a2.set_xlim(eq_cap.index[0], eq_cap.index[-1] + pd.Timedelta(days=60)); guardar(fig, "10_riesgo.png")

    # 11 robustez: los dos parámetros de la regla (longitud del ATR × suelo del percentil) y sus vecinos
    rp = res["robustez_params"]; LS, PS = rp["atr_lens"], rp["pcts"]; iL, iP = LS.index(res["meta"]["atr_len"]), PS.index(res["meta"]["pct_min"])
    et_p = [f"{int(p_*100)}" for p_ in PS]
    fig, axs = plt.subplots(1, 3, figsize=(16, 7.2), sharey=True)
    for ax, (k, tit) in zip(axs, [("pf_is_14", "Construcción · 14 bps"), ("pf_is_28", "Construcción · doble coste"), ("pf_oos_14", "Validación (comprobación)")]):
        Z = np.array([[v if v is not None else np.nan for v in fila] for fila in rp[k]], float); im = ax.imshow(Z, cmap="RdYlGn", vmin=0.8, vmax=max(1.8, np.nanmax(Z)), aspect="auto"); ax.grid(False)
        for a in range(len(LS)):
            for b_ in range(len(PS)):
                if not np.isnan(Z[a, b_]): ax.text(b_, a, f"{Z[a,b_]:.2f}", ha="center", va="center", fontsize=6.5, color=TINTA, fontweight="bold" if (a, b_) == (iL, iP) else "normal")
        ax.add_patch(plt.Rectangle((iP - 1.5, iL - 1.5), 3, 3, fill=False, ec=TINTA, lw=1.2, ls="--")); ax.add_patch(plt.Rectangle((iP - 0.5, iL - 0.5), 1, 1, fill=False, ec=TINTA, lw=2.8))
        ax.set_xticks(range(len(PS))); ax.set_xticklabels([f"p{e}" for e in et_p], fontsize=8); ax.set_yticks(range(len(LS))); ax.set_yticklabels([f"ATR {L}" for L in LS], fontsize=8); ax.set_xlabel("suelo del percentil", fontsize=9); ax.set_title(tit, fontsize=10.5, loc="center")
    axs[0].set_ylabel("longitud del ATR (velas de 1 h)")
    fig.suptitle(f"Fase 3 · Los parámetros de la regla y sus vecinos (Profit Factor al 40 %). Recuadro grueso = la regla (ATR {LS[iL]} · p{et_p[iP]}); punteado = sus 8 vecinos. p30 = operar salvo el 30 % de días más tranquilos", fontweight="bold", x=0.01, ha="left", fontsize=10.5)
    fig.colorbar(im, ax=axs, shrink=0.75, pad=0.02, label="Profit Factor"); guardar(fig, "11_params_mapas.png")
    Z = np.array([[v if v is not None else np.nan for v in fila] for fila in rp["pf_is_14"]], float); C = np.array([[abs(v) if v is not None else np.nan for v in fila] for fila in rp["mdd_is"]], float)
    fig = plt.figure(figsize=(10, 7.5)); ax3 = fig.add_subplot(1, 1, 1, projection="3d"); Xg, Yg = np.meshgrid(range(len(PS)), range(len(LS))); norm = plt.Normalize(np.nanmin(C), np.nanmax(C)); cmap = plt.get_cmap("YlOrRd")
    ax3.plot_surface(Xg, Yg, Z, facecolors=cmap(norm(C)), rstride=1, cstride=1, linewidth=0.4, edgecolor="#ffffff", alpha=0.95, shade=False)
    ax3.set_xticks(range(len(PS))); ax3.set_xticklabels([f"p{e}" for e in et_p], fontsize=8); ax3.set_yticks(range(len(LS))); ax3.set_yticklabels([str(L) for L in LS], fontsize=8)
    ax3.set_xlabel("suelo del percentil", fontsize=9, labelpad=6); ax3.set_ylabel("longitud del ATR", fontsize=9, labelpad=6); ax3.set_zlabel("Profit Factor (construcción)", fontsize=9, labelpad=4)
    ax3.scatter([iP], [iL], [Z[iL, iP] + 0.03], color=TINTA, s=60, depthshade=False); ax3.text(iP, iL, Z[iL, iP] + 0.18, "la regla", fontsize=9, fontweight="bold", color=TINTA)
    ax3.view_init(elev=30, azim=-125); ax3.set_box_aspect((1.25, 1, 0.75)); ax3.set_zlim(np.nanmin(Z) * 0.9, np.nanmax(Z) * 1.05)
    ax3.set_title("Superficie de parámetros: altura = Profit Factor · color = drawdown máximo (versión fija para imprimir)", fontsize=10.5, loc="left")
    m_ = plt.cm.ScalarMappable(cmap=cmap, norm=norm); m_.set_array([]); cb = fig.colorbar(m_, ax=ax3, shrink=0.55, pad=0.08); cb.set_label("drawdown máx. (construcción, 40 %), fracción", fontsize=8.5); guardar(fig, "11_robustez_4d.png")
    from btc_lunes_motor import ATR_LENS_GRUESO, PCTS_GRUESO
    grueso = [x for x in rp["todos"] if x["atr_len"] in ATR_LENS_GRUESO and any(abs(x["pct"] - p_) < 1e-9 for p_ in PCTS_GRUESO)]
    orden = sorted(grueso, key=lambda x: -(x["pf_is"] or 0)); et = [f"ATR {x['atr_len']} · p{int(round(x['pct']*100))}" for x in orden]
    fig, ax4 = plt.subplots(figsize=(13, 5.6)); cols = [TINTA if (x["atr_len"] == LS[iL] and abs(x["pct"] - PS[iP]) < 1e-9) else VERDE2 for x in orden]
    ax4.bar(range(len(orden)), [x["pf_is"] or 0 for x in orden], color=cols, width=0.75); ax4.plot(range(len(orden)), [x["pf_28"] or 0 for x in orden], color=NARANJA, lw=2, marker="o", ms=3.5)
    ax4.scatter(range(len(orden)), [x["pf_oos"] or 0 for x in orden], color=AZUL, s=22, zorder=5, marker="D")
    ax4.axhline(1.0, color=ROJO, ls="--", lw=1); ax4.text(len(orden) - 0.5, 1.02, "PF 1 = empate", color=ROJO, ha="right", fontsize=9)
    ax4.set_xticks(range(len(orden))); ax4.set_xticklabels(et, rotation=90, fontsize=8); ax4.set_xlabel("las 25 combinaciones de parámetros, de mejor a peor en construcción", fontsize=9)
    ax4.set_ylabel("Profit Factor"); ax4.set_title("Las 25 combinaciones ordenadas: barras = construcción con 14 bps · línea naranja = con el doble de coste · rombos azules = validación", fontsize=11)
    ax4.legend([plt.Rectangle((0, 0), 1, 1, color=VERDE2), plt.Line2D([], [], color=NARANJA, lw=2, marker="o"), plt.Line2D([], [], color=AZUL, ls="", marker="D"), plt.Rectangle((0, 0), 1, 1, color=TINTA)], ["construcción · 14 bps", "construcción · 28 bps", "validación · 14 bps", "la regla (ATR 48 · p30)"], frameon=False, fontsize=9.5)
    ax4.set_title("25 de las combinaciones (la rejilla gruesa), ordenadas: barras = construcción con 14 bps · línea naranja = doble coste · rombos azules = validación", fontsize=11)
    fig.tight_layout(); guardar(fig, "11b_params_barras.png")
    # 11c la regla y sus 8 vecinos, uno a uno
    vec = [(LS[a], PS[b], Z[a, b]) for a in range(len(LS)) for b in range(len(PS)) if max(abs(a - iL), abs(b - iP)) == 1]
    fig, ax = plt.subplots(figsize=(11, 4.2)); nombres = ["la regla"] + [f"ATR {L} · p{int(round(p_*100))}" for L, p_, _ in vec]; vals = [rp["centro"]] + [v for _, _, v in vec]
    ax.bar(range(len(vals)), vals, color=[TINTA] + [VERDE2 if v >= rp["centro"] * 0.8 else ROJO for v in vals[1:]], width=0.7)
    ax.axhline(rp["centro"], color=TINTA, ls=":", lw=1); ax.axhspan(rp["centro"] * 0.8, rp["centro"] * 1.2, color=VERDE, alpha=0.08, lw=0); ax.axhline(rp["centro"] * 0.7, color=ROJO, ls="--", lw=1)
    ax.text(len(vals) - 0.5, rp["centro"] * 0.7 + 0.01, "acantilado: −30 % respecto a la regla", color=ROJO, ha="right", fontsize=9); ax.text(-0.4, max(vals) * 1.22, "banda verde: hasta un 20 % por debajo de la regla (por encima no es un problema)", color=VERDE, ha="left", fontsize=9)
    for i, v in enumerate(vals): ax.text(i, v + 0.015, f"{v:.2f}", ha="center", fontsize=9, color=TINTA, fontweight="bold" if i == 0 else "normal")
    ax.set_xticks(range(len(vals))); ax.set_xticklabels(nombres, fontsize=9); ax.set_ylabel("Profit Factor (construcción)"); ax.set_ylim(0, max(vals) * 1.3)
    ax.set_title("La regla y sus 8 vecinos: si ninguno cae más de un 20 % respecto a la regla, estamos en una meseta y no en un pico", fontsize=11); fig.tight_layout(); guardar(fig, "11c_vecinos.png")

    # 11d el día: la misma regla con los mismos filtros, cada día de la semana
    rd = res["robustez_dia"]; fig, ax = plt.subplots(figsize=(11, 4.6)); w = 0.38; xx = np.arange(7)
    v_is = [d["pf_is"] or 0 for d in rd]; v_oos = [d["pf_oos"] or 0 for d in rd]
    ax.bar(xx - w / 2, v_is, width=w, color=[TINTA if i == 0 else GRIS for i in range(7)], label="construcción"); ax.bar(xx + w / 2, v_oos, width=w, color=[VERDE if i == 0 else AZUL for i in range(7)], label="validación")
    for i, d in enumerate(rd):
        ax.text(i - w / 2, v_is[i] + 0.04, f"{v_is[i]:.2f}\nn {d['n_is']}", ha="center", fontsize=7.5, color="#3a4b44"); ax.text(i + w / 2, v_oos[i] + 0.04, f"{v_oos[i]:.2f}\nn {d['n_oos']}", ha="center", fontsize=7.5, color="#3a4b44")
    ax.axhline(1, color=ROJO, ls="--", lw=1); ax.text(6.6, 1.03, "PF 1 = empate", color=ROJO, ha="right", fontsize=9); ax.axvspan(-0.5, 0.5, color=VERDE, alpha=0.08, lw=0)
    ax.set_xticks(xx); ax.set_xticklabels([d["dia"] for d in rd]); ax.set_ylabel("Profit Factor (40 %)"); ax.set_ylim(0, max(v_is + v_oos) * 1.25); ax.legend(frameon=False, fontsize=9.5)
    ax.set_title("La tercera palanca: el día. La misma regla, con los mismos filtros, aplicada a cada día de la semana", fontsize=11.5); fig.tight_layout(); guardar(fig, "11d_dia_regla.png")

    # 13 AED: la semana de BTC hora a hora (era ETF) + por día de la semana en las tres eras
    ae = res["aed"]; eras = ae["eras"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw=dict(width_ratios=[1.6, 1]))
    Z = np.array(ae["semana"][eras[-1]]); vmax = np.nanmax(np.abs(Z)); im = a1.imshow(Z, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto"); a1.grid(False)
    a1.set_yticks(range(7)); a1.set_yticklabels(DIAS); a1.set_xticks(range(0, 24, 2)); a1.set_xticklabels([f"{h:02d}" for h in range(0, 24, 2)]); a1.set_xlabel("hora UTC")
    a1.add_patch(plt.Rectangle((-0.5, -0.5), 24, 1, fill=False, ec=TINTA, lw=2.5)); a1.axvspan(13.5, 20, color=TINTA, alpha=0.06, lw=0); a1.text(16.7, 6.35, "bolsa de EE. UU.", fontsize=8, color=TINTA, ha="center", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
    a1.set_title(f"La semana de BTC hora a hora ({eras[-1]}): retorno bruto medio por hora en puntos básicos\nLa fila recuadrada es la estrategia", fontsize=11); fig.colorbar(im, ax=a1, shrink=0.8, label="pb por hora")
    w = 0.26
    for k, (era, col) in enumerate(zip(eras, [GRIS, AZUL, VERDE])):
        v = [ae["dias"][era][d]["media"] for d in range(7)]; a2.bar(np.arange(7) + (k - 1) * w, v, width=w, color=col, label=era)
    a2.axhline(0, color=TINTA, lw=1); a2.set_xticks(range(7)); a2.set_xticklabels(DIAS); a2.set_ylabel("% bruto por día"); a2.legend(frameon=False, fontsize=9)
    a2.set_title("Retorno bruto medio por día de la semana, en las tres eras\nLunes y miércoles suben, martes y jueves bajan: un ciclo semanal", fontsize=11); fig.tight_layout(); guardar(fig, "13_aed_semana.png")
    # 13b (ficha): antes subía el fin de semana, ahora sube el lunes — solo dos eras, en claro
    fig, ax = plt.subplots(figsize=(11, 4.6)); w = 0.38
    for k, (era, col, nom) in enumerate([(eras[0], GRIS, f"era retail · {eras[0].split('·')[-1].strip()}"), (eras[-1], VERDE, f"era ETF · {eras[-1].split('·')[-1].strip()}")]):
        v = [ae["dias"][era][d]["media"] for d in range(7)]; ax.bar(np.arange(7) + (k - 0.5) * w, v, width=w, color=col, label=nom)
        for d, vv in enumerate(v): ax.text(d + (k - 0.5) * w, vv + (0.02 if vv >= 0 else -0.06), f"{vv:+.2f}", ha="center", fontsize=8.5, color="#3a4b44")
    ax.axhline(0, color=TINTA, lw=1); ax.set_xticks(range(7)); ax.set_xticklabels(DIAS, fontsize=11); ax.set_ylabel("% bruto medio por día"); ax.legend(frameon=False, fontsize=10, loc="upper right")
    ax.set_title("Antes subía el fin de semana; ahora sube el lunes. Retorno medio de cada día, era retail frente a era ETF", fontsize=11.5); fig.tight_layout(); guardar(fig, "13b_dias_eras.png")

    # 14 lunes desnudo frente a lunes con filtro (v3), año a año, con eras
    anos = sorted({t["entrada"].year for t in tb}); dr = {a_: [t["ret"] * 100 for t in tb if t["entrada"].year == a_] for a_ in anos}; fr = {a_: [t["ret"] * 100 for t in ta if t["entrada"].year == a_] for a_ in anos}
    fig, ax = plt.subplots(figsize=(12.5, 5.2)); w = 0.38; xs_ = np.arange(len(anos))
    v_d = [np.mean(dr[a_]) if dr[a_] else 0 for a_ in anos]; v_f = [np.mean(fr[a_]) if fr[a_] else 0 for a_ in anos]
    ax.bar(xs_ - w / 2, v_d, width=w, color=GRIS, label="Lunes desnudo: todos los lunes, sin filtro")
    ax.bar(xs_ + w / 2, v_f, width=w, color=VERDE, label="Lunes con filtro (v3): ATR% sobre el percentil 30 de su año, sin el primer lunes del mes")
    for x_, (vd, vf, a_) in enumerate(zip(v_d, v_f, anos)):
        ax.text(x_ - w / 2, vd + (0.05 if vd >= 0 else -0.05), f"{vd:+.2f}\nn {len(dr[a_])}", ha="center", va="bottom" if vd >= 0 else "top", fontsize=7.5, color="#3a4b44")
        ax.text(x_ + w / 2, vf + (0.05 if vf >= 0 else -0.05), f"{vf:+.2f}\nn {len(fr[a_])}", ha="center", va="bottom" if vf >= 0 else "top", fontsize=7.5, color=VERDE)
    ax.axhline(0, color=TINTA, lw=1); ax.set_xticks(xs_); ax.set_xticklabels([str(a_) for a_ in anos])
    i20, i24 = anos.index(2020), anos.index(2024); ax.axvspan(-0.5, i20 - 0.5, color=GRIS, alpha=0.08, lw=0); ax.axvspan(i24 - 0.5, len(anos) - 0.5, color=VERDE, alpha=0.08, lw=0)
    lo_, hi_ = ax.get_ylim(); ax.set_ylim(lo_ - (hi_ - lo_) * 0.14, hi_ * 1.15); yb = ax.get_ylim()[0] + (hi_ - lo_) * 0.03
    ax.text(i20 / 2 - 0.5, yb, "era retail", fontsize=9, color="#3a4b44", ha="center"); ax.text((i20 + i24) / 2 - 0.5, yb, "era institucional", fontsize=9, color="#3a4b44", ha="center"); ax.text((i24 + len(anos)) / 2 - 0.5, yb, "era ETF", fontsize=9, color=VERDE, ha="center", fontweight="bold")
    ax.set_ylabel("% neto medio por lunes"); ax.legend(frameon=False, fontsize=9.5, loc="upper right")
    ax.set_title("El lunes desnudo frente al lunes con filtro, año a año (neto de costes)\nEl filtro no se eligió por el mejor año: se eligió porque mejora en todas las eras, a pesar de cómo ha cambiado Bitcoin", fontsize=11); fig.tight_layout(); guardar(fig, "14_aed_eras.png")

    # 15 AED: quintiles del ATR percentil por periodo
    q = ae["quintiles"]["ATR% en percentil del año"]
    fig, ax = plt.subplots(figsize=(11, 4.8)); w = 0.26
    for k, (pk, pn, col) in enumerate(PER):
        if pk not in q: continue
        v = q[pk]["medias"]; ax.bar(np.arange(5) + (k - 1) * w, v, width=w, color=col, label=f"{pn} · ρ {q[pk]['rho']:+.2f} (t {q[pk]['t']:+.1f})")
        for i, (vv, n) in enumerate(zip(v, q[pk]["n"])): ax.text(i + (k - 1) * w, vv + (0.03 if vv >= 0 else -0.12), f"n{n}", ha="center", fontsize=7.5, color="#3a4b44")
    ax.axhline(0, color=ROJO, ls=":"); ax.set_xticks(range(5)); ax.set_xticklabels(["Q1 · calma", "Q2", "Q3", "Q4", "Q5 · movimiento"]); ax.set_ylabel("% neto medio por lunes"); ax.legend(frameon=False, fontsize=9)
    ax.set_title("¿Qué variable tiene información? El lunes por quintil de volatilidad (ATR% en percentil de su año)\nLa información está en los quintiles altos: cuando BTC se mueve, el lunes paga; en calma, no cubre el coste", fontsize=11); fig.tight_layout(); guardar(fig, "15_aed_quintiles.png")

    # 16 dos operaciones en velas horarias con el panel del permiso (ATR% frente a su percentil 30 del año)
    oos_tr = [t for t in ta if t["entrada"] >= sp_date]; gan = max(oos_tr[-40:], key=lambda t: t["ret"]); per = min(oos_tr[-40:], key=lambda t: t["ret"])
    DIAS_ES = {0: "lun", 1: "mar", 2: "mié", 3: "jue", 4: "vie", 5: "sáb", 6: "dom"}
    fmt_es = matplotlib.ticker.FuncFormatter(lambda x, pos: (lambda d: f"{DIAS_ES[d.weekday()]} {d.strftime('%H:%M')}")(mdates.num2date(x)))
    umbral = df["atr_pct"].rolling(8760, min_periods=500).quantile(0.30)

    def velas(ax, d, t, titulo):
        for dt, row in d.iterrows():
            col = VERDE if row["Close"] >= row["Open"] else ROJO; x = mdates.date2num(dt)
            ax.plot([dt, dt], [row["Low"], row["High"]], color=col, lw=0.9); ax.add_patch(plt.Rectangle((x - 0.016, min(row["Open"], row["Close"])), 0.032, abs(row["Close"] - row["Open"]) or 1, color=col))
        sig = d.index[d.index.get_loc(t["entrada"]) - 1]; ax.axvspan(mdates.date2num(sig) - 0.02, mdates.date2num(sig) + 0.02, color="#fff5e9", zorder=0)
        ax.axvspan(mdates.date2num(t["entrada"]), mdates.date2num(t["salida"]), color="#eef6f1", zorder=0)
        bb = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)
        ax.annotate(f"compra {t['px_ent']:,.0f}", (t["entrada"], t["px_ent"]), xytext=(-70, -40), textcoords="offset points", fontsize=9, color=VERDE, fontweight="bold", bbox=bb, arrowprops=dict(arrowstyle="->", color=VERDE))
        ax.annotate(f"venta {t['px_sal']:,.0f}\n{t['ret']*100:+.2f} %", (t["salida"], t["px_sal"]), xytext=(14, -48), textcoords="offset points", fontsize=9, color=ROJO if t["ret"] < 0 else VERDE, fontweight="bold", bbox=bb, arrowprops=dict(arrowstyle="->", color=ROJO if t["ret"] < 0 else VERDE))
        ax.set_title(titulo, fontsize=9.5, loc="left"); ax.xaxis.set_major_formatter(fmt_es); ax.grid(axis="x", visible=False); ax.margins(y=0.15); ax.set_ylabel("BTC/USDT", fontsize=9); ax.tick_params(labelbottom=False)

    def panel(ax, d, t):
        sig = d.index[d.index.get_loc(t["entrada"]) - 1]
        ax.plot(d.index, df.loc[d.index, "atr_pct"], color=MORADO, lw=1.6); ax.plot(d.index, umbral.loc[d.index], color=VERDE, lw=1.2, ls="--")
        ax.fill_between(d.index, umbral.loc[d.index], df.loc[d.index, "atr_pct"].max() * 1.1, color="#e6faef", zorder=0)
        ax.scatter([sig], [df.loc[sig, "atr_pct"]], color="#9a5a15", s=40, zorder=5)
        ax.text(0.01, 0.95, "zona verde = con permiso (ATR% sobre el percentil 30 del año)", transform=ax.transAxes, fontsize=8, color=VERDE, va="top", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
        ax.set_ylabel("ATR%(48)", fontsize=9); ax.tick_params(labelsize=8); ax.xaxis.set_major_formatter(fmt_es); ax.grid(axis="x", visible=False)

    def tit(nombre, t):
        return (f"{nombre} · lunes {t['entrada'].strftime('%d %b %Y')} · 24 velas · precio {t['ret']*100:+.2f} %\n"
                f"sobre el capital: 100 % → {t['ret']*100:+.2f} % · robot 40 % → {t['ret']*40:+.2f} %\n"
                f"vela de señal: ATR% {t['atrp']:.2f} % = percentil {t['pct']*100:.0f} del año")
    fig, axs = plt.subplots(2, 2, figsize=(13, 7.4), height_ratios=[3, 1.1], sharex="col")
    for j, (t, nombre) in enumerate([(gan, "GANADORA"), (per, "PERDEDORA")]):
        d = df.iloc[max(0, t["i_ent"] - 14):t["i_sal"] + 7]; velas(axs[0, j], d, t, tit(nombre, t)); panel(axs[1, j], d, t)
    fig.suptitle("Así se ve una operación, vela a vela: la vela de señal (domingo 23:00 UTC, en naranja), la compra a las 00:00 del lunes,\nel día entero (en verde) y la venta a las 00:00 del martes", fontweight="bold", x=0.01, ha="left", y=1.02, fontsize=11)
    fig.tight_layout(); guardar(fig, "16_operacion_ejemplo.png")

    # 17 qué calcula el permiso: (1) el ATR, (2) el año ordenado de menor a mayor y dónde cae hoy
    j = ta[-1]["i_ent"] - 1; d = df.iloc[j - 47:j + 1]; c_prev = df["Close"].iloc[j - 48:j].values
    tr = np.maximum.reduce([d["High"].values - d["Low"].values, np.abs(d["High"].values - c_prev), np.abs(d["Low"].values - c_prev)])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw=dict(width_ratios=[1, 1.25]))
    a1.bar(range(48), tr, color="#f0a860"); a1.axhline(d["atr"].iloc[-1], color=TINTA, lw=2)
    a1.text(0.02, 0.95, f"ATR(48) = {d['atr'].iloc[-1]:,.0f} $ por vela\n= {d['atr_pct'].iloc[-1]:.2f} % del precio", transform=a1.transAxes, va="top", fontsize=10, fontweight="bold", color=TINTA, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#e2ede8"))
    a1.set_xlabel("las 48 velas horarias (dos días) anteriores a la última señal"); a1.set_ylabel("cuánto se movió cada vela ($)"); a1.set_title("Paso 1 · ¿Cuánto se mueve BTC cada hora?\nLa media de las últimas 48 velas es el ATR (línea negra)", fontsize=10.5)
    ano = np.sort(df["atr_pct"].iloc[j - 8759:j + 1].dropna().values); n = len(ano); hoy = float(df["atr_pct"].iloc[j]); u30 = float(np.percentile(ano, 30)); pos = float((ano < hoy).mean() * 100)
    a2.fill_between(np.arange(n) / n * 100, ano, color="#e6faef", lw=0, where=np.arange(n) / n * 100 >= 30); a2.plot(np.arange(n) / n * 100, ano, color=MORADO, lw=2)
    a2.axvline(30, color=VERDE, lw=2, ls="--"); a2.axhline(u30, color=VERDE, lw=1, ls=":"); a2.scatter([pos], [hoy], color="#9a5a15", s=70, zorder=5)
    a2.text(31, ano.max() * 0.95, f"a partir del 30 % hay permiso\n(ATR% ≥ {u30:.2f} % en este año)", fontsize=9.5, color=VERDE, va="top")
    a2.text(pos, hoy, f"  hoy: {hoy:.2f} % → percentil {pos:.0f}" + ("  ✓ permiso" if pos >= 30 else "  ✗ sin permiso"), fontsize=9.5, color="#9a5a15", fontweight="bold", va="bottom")
    a2.text(2, ano.min() * 1.05, "días tranquilos", fontsize=9, color="#3a4b44"); a2.text(80, ano.max() * 0.6, "días movidos", fontsize=9, color="#3a4b44", ha="center")
    a2.set_xlabel("los 365 días del último año, de más tranquilo (0 %) a más movido (100 %)"); a2.set_ylabel("ATR% de cada vela del año")
    a2.set_title("Paso 2 · ¿Dónde está el de hoy entre los de su último año?\nSi queda en el 70 % más movido, hay permiso para operar el lunes", fontsize=10.5)
    fig.tight_layout(); guardar(fig, "17_atr.png")

    # 18 AED: distribución de los lunes (colas) y dependencia de los mejores
    r = np.array([t["ret"] * 100 for t in tb]); mu, sd = r.mean(), r.std(); di = ae["distribucion"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.4, 1]))
    cnt, edges, _ = a1.hist(r, bins=60, color="#c2d0c8", ec="white", label="Retorno neto de cada lunes (todos, sin filtro)")
    xs = np.linspace(r.min(), r.max(), 400); a1.plot(xs, _norm.pdf(xs, mu, sd) * len(r) * (edges[1] - edges[0]), color=AZUL, lw=2, label="Campana normal con la misma media y desviación")
    a1.axvline(r.min(), color=ROJO, ls="--"); a1.axvline(r.max(), color=VERDE, ls="--"); a1.text(r.min(), cnt.max() * 0.5, f" peor lunes {r.min():+.1f} %", color=ROJO, fontsize=9, rotation=90, va="bottom"); a1.text(r.max(), cnt.max() * 0.5, f"mejor lunes {r.max():+.1f} % ", color=VERDE, fontsize=9, rotation=90, va="bottom", ha="right")
    a1.set_xlabel("Retorno del lunes (%)"); a1.set_ylabel("Lunes"); a1.legend(frameon=False, fontsize=9); a1.set_title(f"Colas gordas: mediana {di['mediana']:+.2f} %, media {di['media']:+.2f} %, curtosis {di['curtosis']:.1f}\nEl lunes gana por unos pocos días grandes", fontsize=11)
    s = pd.Series(r).sort_values(ascending=False).to_numpy(); dec = np.array_split(s, 10); gan_tot = s[s > 0].sum(); aport = [d.sum() / gan_tot * 100 for d in dec]
    a2.bar(range(10), aport, color=[VERDE if v > 0 else ROJO for v in aport], width=0.7)
    for i, v in enumerate(aport): a2.text(i, v + (1.5 if v >= 0 else -4), f"{v:+.0f} %", ha="center", fontsize=8.5, color=TINTA)
    a2.axhline(0, color=TINTA, lw=0.8); a2.set_xticks(range(10)); a2.set_xticklabels(["mejor\n10 %", "2º", "3º", "4º", "5º", "6º", "7º", "8º", "9º", "peor\n10 %"], fontsize=8.5)
    a2.set_ylabel("% del beneficio bruto que aporta"); a2.set_title(f"Los lunes en 10 grupos, de mejor a peor: el mejor 10 % aporta el {di['top10_pct_beneficio']*100:.0f} %\nPor eso no se corta un lunes bueno a medias (ni take profit ni stop)", fontsize=10.5)
    fig.tight_layout(); guardar(fig, "18_aed_colas.png")

    # 19 meses (robot)
    me = res["mensual"]; Mz = np.array([[np.nan if (v is None or abs(v) < 1e-9) else v * 100 for v in fila] for fila in me["matriz"]])
    fig, ax = plt.subplots(figsize=(13, 0.34 * len(me["anos"]) + 1.6)); vmax = np.nanmax(np.abs(Mz)); im = ax.imshow(Mz, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
    for i in range(Mz.shape[0]):
        for jj in range(12):
            if not np.isnan(Mz[i, jj]): ax.text(jj, i, f"{Mz[i,jj]:+.1f}", ha="center", va="center", fontsize=7.5, color=TINTA if abs(Mz[i, jj]) < vmax * 0.6 else "white")
        f = me["filas"][i]; ax.text(12.1, i, f"{f['anual']*100:+.1f} %", va="center", fontsize=8.5, fontweight="bold", color=VERDE if f["anual"] >= 0 else ROJO); ax.text(13.4, i, f"{f['pos']}↑ {f['neg']}↓", va="center", fontsize=8, color="#3a4b44")
    ax.set_xticks(range(12)); ax.set_xticklabels(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]); ax.set_yticks(range(len(me["anos"]))); ax.set_yticklabels(me["anos"], fontsize=8.5); ax.set_xlim(-0.5, 14.2); ax.grid(False)
    ax.text(12.1, -0.9, "año", fontsize=8.5, fontweight="bold"); ax.text(13.4, -0.9, "meses ↑↓", fontsize=8.5, fontweight="bold")
    ax.set_title(f"Retorno mes a mes con el 40 % del capital · {me['meses_pos']} meses positivos, {me['meses_neg']} negativos, {me['meses_planos']} sin operar (en blanco)", fontsize=11, loc="left", pad=18); fig.tight_layout(); guardar(fig, "19_meses.png")

    # 20 drawdowns por profundidad (robot): cuántas y cuánto tardan
    bins = res["drawdowns_robot"]["bins"]; cols = ["#b9efd1", "#5eeba4", "#f0a860", "#f4805e", ROJO]
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(13, 4.6))
    b1.bar(range(len(bins)), [b_["n"] for b_ in bins], color=cols, width=0.65)
    for i, b_ in enumerate(bins): b1.text(i, b_["n"] + 0.5, f"{b_['n']}\n({b_['pct']*100:.0f} %)", ha="center", fontsize=9, color="#3a4b44")
    b1.set_xticks(range(len(bins))); b1.set_xticklabels([b_["bin"] for b_ in bins]); b1.set_xlabel("profundidad de la caída"); b1.set_ylabel("número de caídas"); b1.set_ylim(0, max(b_["n"] for b_ in bins) * 1.3); b1.set_title("Cuántas caídas de cada tamaño (40 %)", fontsize=11)
    w = 0.36; b2.bar(np.arange(len(bins)) - w / 2, [b_["dias_medio"] for b_ in bins], width=w, color="#9fb5aa", label="recuperación media"); b2.bar(np.arange(len(bins)) + w / 2, [b_["dias_max"] for b_ in bins], width=w, color=TINTA, label="la más larga")
    for i, b_ in enumerate(bins):
        if b_["n"]: b2.text(i - w / 2, b_["dias_medio"] + 8, f"{b_['dias_medio']:.0f}", ha="center", fontsize=8, color="#3a4b44"); b2.text(i + w / 2, b_["dias_max"] + 8, f"{b_['dias_max']}", ha="center", fontsize=8, color=TINTA)
    b2.set_xticks(range(len(bins))); b2.set_xticklabels([b_["bin"] for b_ in bins]); b2.set_xlabel("profundidad de la caída"); b2.set_ylabel("días hasta recuperar el máximo"); b2.legend(frameon=False, fontsize=9); b2.set_title("Cuánto tardan en recuperarse", fontsize=11)
    fig.suptitle(f"Las {res['drawdowns_robot']['n']} caídas desde máximos, agrupadas por profundidad", fontweight="bold", x=0.01, ha="left", fontsize=11.5); fig.tight_layout(); guardar(fig, "20_dd_bins.png")

    # 21 horas: tres paneles (uno por periodo), barras verdes/rojas, con la zona que aguanta
    rv = res["revision"]; offs = [h["off"] for h in rv["horas"]]
    fig, axs = plt.subplots(3, 1, figsize=(12, 8.6), sharex=True)
    for ax, (pk, pn, col) in zip(axs, PER):
        v = np.array([(h[pk]["media"] if h[pk]["media"] is not None else np.nan) for h in rv["horas"]], float)
        ax.bar(offs, v, color=[VERDE if x > 0 else ROJO for x in v], width=0.8, alpha=0.9); ax.axhline(0, color=TINTA, lw=0.8); ax.axvspan(-9.5, 0.5, color=VERDE, alpha=0.07, lw=0); ax.axvline(0, color=TINTA, ls=":", lw=1)
        ax.bar([0], [v[offs.index(0)]], color=TINTA, width=0.8); ax.set_ylabel("% neto por operación"); ax.set_title(pn, fontsize=10.5, color=col)
        ax.text(-24, ax.get_ylim()[1] * 0.95, "zona verde: de 9 h antes a la hora en punto, aguanta", fontsize=8.5, color=VERDE, va="top", bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    axs[-1].set_xlabel("hora de entrada respecto al lunes 00:00 UTC (negativo = antes, el domingo; positivo = después) · siempre 24 h en posición · barra negra = la regla")
    fig.suptitle("¿Cuántas horas antes o después aguanta el efecto? Cada barra = media neta por operación entrando a esa hora", fontweight="bold", x=0.01, ha="left", fontsize=11.5); fig.tight_layout(); guardar(fig, "21_horas.png")

    # 21b los otros días y el fin de semana: Profit Factor en barras por periodo
    ds = rv["dias_semana"]; fd = rv["finde"]; filas_ = list(ds.items()) + list(fd.items()); nom = [k for k, _ in filas_]
    fig, ax = plt.subplots(figsize=(13.5, 5.6)); w = 0.26; xx = np.arange(len(filas_))
    for k, (pk, pn, col) in enumerate(PER):
        v = [(d[pk]["pf"] if d[pk]["pf"] is not None else 0) for _, d in filas_]; ax.bar(xx + (k - 1) * w, v, width=w, color=col, label=pn)
        for i, vv in enumerate(v): ax.text(i + (k - 1) * w, vv + 0.02, f"{vv:.2f}", ha="center", fontsize=7, color="#3a4b44", rotation=90)
    ax.axhline(1, color=ROJO, ls="--", lw=1); ax.text(len(filas_) - 0.5, 1.03, "PF 1 = empate", color=ROJO, ha="right", fontsize=9); ax.axvspan(-0.5, 0.5, color=VERDE, alpha=0.08, lw=0)
    ax.set_xticks(xx); ax.set_xticklabels([{"viernes 21:00 → lunes 00:00 (bolsa cerrada)": "fin de semana\n(vie 21h → lun 00h)", "viernes 21:00 → martes 00:00 (finde + lunes)": "finde + lunes\n(vie 21h → mar 00h)", "lunes + martes (48 h)": "lunes + martes\n(48 h)"}.get(n, n) for n in nom], fontsize=8.5); ax.set_ylabel("Profit Factor"); ax.legend(frameon=False, fontsize=9.5); ax.set_ylim(0, 2.2)
    ax.set_title("Comprar 24 h desde las 00:00 UTC de cada día, y el fin de semana entero: solo el lunes (y algo el miércoles) gana en los tres periodos", fontsize=11); fig.tight_layout(); guardar(fig, "21b_dias.png")

    # 22 duración: barras agrupadas
    hd = [h["hold"] for h in rv["duracion"]]; fig, ax = plt.subplots(figsize=(11, 4.8)); w = 0.26; xx = np.arange(len(hd))
    for k, (pk, pn, col) in enumerate(PER):
        v = [(h[pk]["media"] if h[pk]["media"] is not None else 0) for h in rv["duracion"]]; ax.bar(xx + (k - 1) * w, v, width=w, color=col, label=pn)
    ax.axhline(0, color=TINTA, lw=0.8); ax.axvspan(hd.index(24) - 0.5, hd.index(24) + 0.5, color=VERDE, alpha=0.1, lw=0); ax.text(hd.index(24), ax.get_ylim()[1] * 0.92, "la regla\n24 h", ha="center", fontsize=9, color=VERDE, fontweight="bold")
    ax.set_xticks(xx); ax.set_xticklabels([f"{h} h" for h in hd]); ax.set_xlabel("horas en posición desde el lunes 00:00 UTC (salir antes = time stop; más de 24 h = aguantar el martes)"); ax.set_ylabel("% neto medio por operación"); ax.legend(frameon=False, fontsize=9.5)
    ax.set_title("¿Menos horas? ¿Más? Las primeras 12–15 h no pagan el coste; el dinero está entre las 15 h y las 24 h; aguantar más lo devuelve", fontsize=11); fig.tight_layout(); guardar(fig, "22_duracion.png")

    # 23 take profit × stop
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.4))
    for ax, (pk, pn, _) in zip(axs, PER[:2]):
        t_ = rv["tp_sl"][pk]; Z = np.array([[v if v is not None else np.nan for v in fila] for fila in t_["pf"]])
        im = ax.imshow(Z, cmap="RdYlGn", vmin=0.3, vmax=max(1.6, np.nanmax(Z)), aspect="auto"); ax.grid(False)
        ax.set_xticks(range(len(t_["sl"]))); ax.set_xticklabels([f"{s}" if isinstance(s, str) else f"SL {s:g} %" for s in t_["sl"]], rotation=45, fontsize=8); ax.set_yticks(range(len(t_["tp"]))); ax.set_yticklabels([f"{s}" if isinstance(s, str) else f"TP {s:g} %" for s in t_["tp"]], fontsize=8)
        for a in range(Z.shape[0]):
            for b_ in range(Z.shape[1]):
                if not np.isnan(Z[a, b_]): ax.text(b_, a, f"{Z[a,b_]:.2f}", ha="center", va="center", fontsize=7.5, color=TINTA)
        ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, 1, fill=False, ec=TINTA, lw=2.5)); ax.set_title(pn, fontsize=10.5, loc="center", pad=8)
    fig.suptitle("Salidas por porcentaje: Profit Factor con cada take profit (filas) × stop (columnas). El recuadro es la regla, sin ninguno de los dos", fontweight="bold", x=0.01, ha="left", fontsize=11, y=0.99)
    fig.subplots_adjust(top=0.86, wspace=0.28); fig.colorbar(im, ax=axs, shrink=0.7, label="Profit Factor"); guardar(fig, "23_tp_sl.png")

    # 24 MAE / MFE
    mm = rv["mae_mfe"]; ret = np.array(mm["ret"]); mfe = np.array(mm["mfe"]); mae = np.array(mm["mae"]); fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(-mae[ret > 0], mfe[ret > 0], s=16, color=VERDE, alpha=0.6, label="lunes ganador"); ax.scatter(-mae[ret <= 0], mfe[ret <= 0], s=16, color=ROJO, alpha=0.6, marker="x", label="lunes perdedor")
    ax.axhline(1, color=TINTA, ls=":"); ax.axvline(2, color=TINTA, ls=":"); ax.set_xlabel("MAE: cuánto fue en contra en el peor momento (%)"); ax.set_ylabel("MFE: cuánto fue a favor en el mejor momento (%)"); ax.legend(frameon=False)
    rs = mm["resumen"]; ax.set_title(f"MAE y MFE de cada lunes: las ganadoras pasan por −{abs(rs['mae_gan'])*100:.1f} % de media antes de subir;\nlas perdedoras solo llegan a +{rs['mfe_per']*100:.1f} %. No hay take profit que rescate perdedoras sin cortar ganadoras", fontsize=10.5); ax.set_xlim(0, min(25, (-mae).max() * 1.05)); ax.set_ylim(0, min(25, mfe.max() * 1.05))
    fig.tight_layout(); guardar(fig, "24_mae_mfe.png")

    # 25 exchanges
    if "exchanges" in res:
        ex = res["exchanges"]; fig, ax = plt.subplots(figsize=(11, 5.4))
        for k, col in [("quantfury", VERDE2), ("binance", VERDE), ("coinbase", ROJO)]:
            e = ex[k]["_eq"]; ax.plot(e.index, e.values, color=col, lw=2 if k == "binance" else 1.5, label=f"{ex[k]['nombre']} · {ex[k]['ida_vuelta_pct']:.2f} % por ida y vuelta · PF validación {ex[k]['OOS']['pf']:.2f}")
            ax.text(e.index[-1], e.iloc[-1], f"  {e.iloc[-1]:.2f}×", color=col, fontweight="bold", va="center", fontsize=9.5)
        cb = OUT / "equity_semanal_coinbase.json"
        if cb.exists():
            s_ = json.loads(cb.read_text(encoding="utf-8")); ax.plot(pd.to_datetime(s_["fechas"]), s_["robot"], color=NARANJA, lw=1.2, ls="--", label="Datos de Coinbase (BTC/USD) con costes de Coinbase")
        eje_log(ax, 3, 0.5); sombras(ax); ax.set_xlim(df.index[0], df.index[-1] + pd.Timedelta(days=330)); ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.set_ylabel("Capital (40 %, escala log)")
        ax.set_title("Misma regla, mismas velas: lo que cambia el exchange\nCon Coinbase al 0,60 % por lado el lunes no cubre el coste", fontsize=11.5); guardar(fig, "25_exchanges.png")

    # 28 sizing: fracción fija · sizing por ATR · vol targeting
    eq_atr, eq_vt = eq["atr"], eq["vt"]; sz = res["sizing"]
    expo_a = pd.Series([t["expo_atr"] for t in ta], index=[t["entrada"] for t in ta]); expo_v = pd.Series([t["expo_vt"] for t in ta], index=[t["entrada"] for t in ta])
    fig, axs = plt.subplots(3, 1, figsize=(12, 9.6), height_ratios=[2.4, 1.1, 1.2], sharex=True)
    for e_, col, nom in [(eq_rob, VERDE, f"Fracción fija: 40 % del capital cada lunes · {eq_rob.iloc[-1]:.2f}×"), (eq_atr, MORADO, f"Sizing por ATR: 1 % de riesgo, stop virtual a 2 ATR diarios (tamaño medio {sz['exposicion_media_atr']*100:.0f} %) · {eq_atr.iloc[-1]:.2f}×"), (eq_vt, NARANJA, f"Vol targeting: objetivo 1,5 % de vol diaria, tope 100 % (tamaño medio {sz['exposicion_media_vt']*100:.0f} %) · {eq_vt.iloc[-1]:.2f}×")]:
        axs[0].plot(e_.index, e_.values, color=col, lw=2, label=nom)
    eje_log(axs[0], max(eq_rob.max(), eq_atr.max(), eq_vt.max()), min(eq_rob.min(), eq_atr.min(), eq_vt.min())); sombras(axs[0]); axs[0].legend(frameon=False, loc="upper left", fontsize=9.5); axs[0].set_ylabel("Capital (1 = inicial)")
    axs[0].set_title("Tres formas de poner el tamaño: aquí la volatilidad alta es la señal, no el riesgo\nUn tamaño inverso a la volatilidad pone poco justo en los lunes que pagan", fontsize=11.5)
    for e_, col in [(eq_rob, VERDE), (eq_atr, MORADO), (eq_vt, NARANJA)]:
        d_ = (e_ - e_.cummax()) / e_.cummax() * 100; axs[1].fill_between(d_.index, d_.values, 0, color=col, alpha=0.18, lw=0); axs[1].plot(d_.index, d_.values, color=col, lw=0.9)
    axs[1].set_ylabel("Drawdown %")
    axs[2].bar(expo_v.index, expo_v.values * 100, width=5, color=NARANJA, alpha=0.6, label="vol targeting"); axs[2].bar(expo_a.index, expo_a.values * 100, width=5, color=MORADO, alpha=0.9, label="sizing por ATR"); axs[2].axhline(40, color=VERDE, lw=1.5, ls="--")
    axs[2].text(expo_a.index[0], 38.5, " 40 % fijo (el robot)", color=VERDE, fontsize=9, va="top"); axs[2].set_ylabel("tamaño por lunes (%)"); axs[2].legend(frameon=False, fontsize=9, loc="upper right")
    axs[2].set_title("Tamaño que habría puesto cada método en cada lunes: pequeño cuando BTC se mueve, grande cuando está en calma", fontsize=10); axs[2].xaxis.set_major_locator(mdates.YearLocator(1))
    fig.tight_layout(); guardar(fig, "28_sizing_atr.png")

    # 29 ¿ayuda una media móvil? la v3 sola frente a la v3 solo con BTC por encima de su media
    sm = res["sma"]; fig, ax = plt.subplots(figsize=(11, 5))
    for e_, col, nom in [(eq_rob, VERDE, f"v3 tal cual · {eq_rob.iloc[-1]:.2f}×"), (sm["sma50"]["_eq"], AZUL, f"v3 solo con BTC > media de 50 días (quita {sm['sma50']['n_quita']} lunes) · {sm['sma50']['_eq'].iloc[-1]:.2f}×"), (sm["sma200"]["_eq"], NARANJA, f"v3 solo con BTC > media de 200 días (quita {sm['sma200']['n_quita']} lunes) · {sm['sma200']['_eq'].iloc[-1]:.2f}×")]:
        ax.plot(e_.index, e_.values, color=col, lw=2 if col == VERDE else 1.6, label=nom)
    eje_log(ax, max(eq_rob.max(), sm["sma50"]["_eq"].max(), sm["sma200"]["_eq"].max()), 0.8); sombras(ax); ax.legend(frameon=False, loc="upper left", fontsize=9.5); ax.set_ylabel("Capital (40 %, 1 = inicial)")
    ax.set_title("¿Ayuda un filtro de tendencia? La v3 con y sin exigir que BTC esté por encima de su media móvil", fontsize=11.5); ax.set_xlim(df.index[0], df.index[-1] + pd.Timedelta(days=60)); guardar(fig, "29_sma.png")

    # 26 vigilancia: z en todo el histórico (electrocardiograma), z del lunes desnudo (régimen) y cuota de permiso
    vg = res["vigilancia"]
    def serie_z(lst):
        f_ = pd.to_datetime([x["fecha"] for x in lst]); v_ = np.array([x["z"] if x["z"] is not None else np.nan for x in lst], float); return f_, v_
    fz, zv = serie_z(vg["todo"]); fb, zb = serie_z(vg["desnudo"]) if vg["desnudo"] else (fz, np.full(len(fz), np.nan))
    fp = pd.to_datetime([x["fecha"] for x in vg["permiso"]]); cp = np.array([x["cuota"] for x in vg["permiso"]]) * 100
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), height_ratios=[2.2, 1.4, 1.1], sharex=True)
    for ax, (f_, v_, tit, col) in zip(axs[:2], [(fz, zv, "z de la v3 (la que se vigila): media de los últimos 20 lunes operados frente a lo que esperaba el backtest", TINTA), (fb, zb, "z del lunes desnudo (todos los lunes, sin filtro): el termómetro del régimen", GRIS)]):
        ax.axhspan(-1, 4, color=VERDE, alpha=0.07, lw=0); ax.axhspan(-2, -1, color="#f0a860", alpha=0.2, lw=0); ax.axhspan(-4, -2, color=ROJO, alpha=0.14, lw=0)
        ok_ = ~np.isnan(v_); ax.plot(f_[ok_], v_[ok_], color=col, lw=1.8); ax.axhline(0, color=GRIS, ls=":"); ax.axhline(-1, color="#9a5a15", ls="--", lw=1); ax.axhline(-2, color=ROJO, ls="--", lw=1)
        ax.axvline(sp_date, color=TINTA, ls=":", lw=1); ax.axvline(LIVE, color=ROJO, ls=":", lw=1.2); ax.set_ylim(-4, 4); ax.set_ylabel("z"); ax.set_title(tit, fontsize=10.5)
        ax.text(f_[0], 3.6, " VERDE · como en el backtest", fontsize=9, color=VERDE, fontweight="bold"); ax.text(f_[0], -1.5, " AMARILLO · anotar y seguir", fontsize=9, color="#9a5a15", va="center", fontweight="bold"); ax.text(f_[0], -3, " ROJO · tamaño a la mitad y revisión", fontsize=9, color=ROJO, va="center", fontweight="bold")
    axs[0].text(LIVE, 3.1, " en real →", color=ROJO, fontsize=9); axs[0].text(sp_date, 2.6, " validación →", color="#3a4b44", fontsize=9)
    if len(fp):
        axs[2].fill_between(fp, cp, 0, color=AZUL, alpha=0.18, lw=0); axs[2].plot(fp, cp, color=AZUL, lw=1.6); axs[2].axhline(vg["cuota_ref"] * 100, color=TINTA, ls="--", lw=1); axs[2].text(fp[0], vg["cuota_ref"] * 100 + 2, f" referencia del backtest: opera el {vg['cuota_ref']*100:.0f} % de los lunes", fontsize=9, color=TINTA)
    axs[2].set_ylim(0, 100); axs[2].set_ylabel("% de lunes con permiso"); axs[2].set_title("Cuota de permiso en las últimas 26 semanas: si baja, es que BTC está en calma (no opera), no que el edge falle", fontsize=10.5); axs[2].xaxis.set_major_locator(mdates.YearLocator(1))
    fig.suptitle(f"Protocolo de desgaste del edge · z = (media de los últimos 20 lunes − {vg['mu0']*100:+.2f} %) ÷ ({vg['sigma0']*100:.2f} % ÷ √20) · hoy z = {vg['z_hoy']:+.2f}" if vg["z_hoy"] is not None else "Protocolo de desgaste del edge", fontweight="bold", x=0.01, ha="left", fontsize=11.5)
    fig.tight_layout(); guardar(fig, "26_vigilancia.png")

    # 27 filtros: PF por periodo
    fl = rv["filtros"]; fig, ax = plt.subplots(figsize=(12, 0.5 * len(fl) + 1.8)); yy = np.arange(len(fl)); h = 0.26
    for k, (pk, pn, col) in enumerate(PER):
        vals = [min(f[pk]["pf"], 5.0) if f[pk]["pf"] is not None else 0 for f in fl]; ax.barh(yy + (k - 1) * h, vals, height=h, color=col, label=pn)
        for y_, f in zip(yy, fl):
            if f[pk]["pf"] is None: ax.text(0.05, y_ + (k - 1) * h, f"{f[pk]['n']} lunes: pocos para medir", va="center", fontsize=7, color=col)
            elif f[pk]["pf"] > 5: ax.text(5.02, y_ + (k - 1) * h, f"> 5 ({f[pk]['pf']:.0f}, n {f[pk]['n']})", va="center", fontsize=7, color=col)
    ax.axvline(1, color=ROJO, ls="--"); ax.set_xlim(0, 5.6); ax.set_yticks(yy); ax.set_yticklabels([f["filtro"] for f in fl], fontsize=9); ax.invert_yaxis(); ax.set_xlabel("Profit Factor (eje recortado en 5)"); ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.set_title("Los filtros, uno a uno: se eligen con la construcción; validación y real comprueban que la mejora se mantiene\nEl tope de la v1 hunde la construcción; el suelo del percentil mejora en las tres columnas", fontsize=11); fig.tight_layout(); guardar(fig, "27_filtros.png")
