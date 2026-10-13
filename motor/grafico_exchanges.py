"""
Gráfico 25 (lo que cambia el exchange) con los cuatro perfiles de coste, sin volver a bajar las velas.
Curvas reconstruidas con perfil_sin_velas.curva() a partir de trades.csv y equity_diaria.csv (el método reproduce el
Profit Factor del motor exacto y el CAGR y el drawdown a centésimas). Misma estética que motor/graficos.py.

Uso: python motor/grafico_exchanges.py   → resultados/graficos/25_exchanges.png
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
RAIZ = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(RAIZ / "motor"))
from btc_lunes_motor import coste_lado
from perfil_sin_velas import curva, M, SP, EQ
from graficos import VERDE, VERDE2, ROJO, NARANJA, MORADO, OUT


def main():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": "#c2d0c8", "axes.labelcolor": "#3a4b44", "xtick.color": "#3a4b44",
                         "ytick.color": "#3a4b44", "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e2ede8",
                         "grid.linewidth": 0.6, "figure.facecolor": "white", "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left"})
    ex = M["exchanges"]; LIVE = pd.Timestamp(M["meta"]["live_desde"]); i0, i1 = EQ.index[0], EQ.index[-1]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    for k, col in [("quantfury", VERDE2), ("exness", MORADO), ("binance", VERDE), ("coinbase", ROJO)]:
        if k not in ex: continue
        _, e = curva(coste_lado(k))
        ax.plot(e.index, e.values, color=col, lw=2 if k == "binance" else 1.5, label=f"{ex[k]['nombre']} · {ex[k]['ida_vuelta_pct']:.2f} % por ida y vuelta · PF validación {ex[k]['OOS']['pf']:.2f}")
        ax.text(e.index[-1], e.iloc[-1] + {"quantfury": 0.05, "exness": -0.05}.get(k, 0), f"  {e.iloc[-1]:.2f}×", color=col, fontweight="bold", va="center", fontsize=9.5)
    cb = OUT / "equity_semanal_coinbase.json"
    if cb.exists():
        s_ = json.loads(cb.read_text(encoding="utf-8")); ax.plot(pd.to_datetime(s_["fechas"]), s_["robot"], color=NARANJA, lw=1.2, ls="--", label="Datos de Coinbase (BTC/USD) con costes de Coinbase")
    top, lo = 3, 0.5
    ax.set_ylim(max(0, lo * 0.9), top * 1.08); paso = 0.5
    ticks = np.arange(np.floor(lo * 4) / 4, top * 1.08 + paso, paso); ax.set_yticks(ticks); ax.set_yticklabels([f"{t:g}×" for t in ticks])
    ax.axvspan(SP, i1, color="#eef6f1", zorder=0); ax.axvline(LIVE, color=ROJO, ls=":", lw=1.2)
    l_, h_ = ax.get_ylim(); ax.text(SP, h_, "  fuera de muestra →", va="top", color="#3a4b44", fontsize=9.5); ax.text(LIVE, h_ - (h_ - l_) * 0.08, "  en real →", va="top", color=ROJO, fontsize=9.5)
    ax.set_xlim(i0, i1 + pd.Timedelta(days=330)); ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.set_ylabel("Capital (40 %, escala log)")
    ax.set_title("Misma regla, mismas velas: lo que cambia el exchange\nCon Coinbase al 0,60 % por lado el lunes no cubre el coste", fontsize=11.5)
    fig.savefig(OUT / "graficos" / "25_exchanges.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    print("resultados/graficos/25_exchanges.png con", [k for k in ["quantfury", "exness", "binance", "coinbase"] if k in ex])


if __name__ == "__main__":
    main()
