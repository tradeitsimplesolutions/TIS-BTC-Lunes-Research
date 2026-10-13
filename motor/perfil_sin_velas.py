"""
Métricas de la v3 con OTRO perfil de costes sin volver a bajar las velas: se parte de resultados/trades.csv (precios de
apertura de Binance con 14 bps por lado) y de resultados/equity_diaria.csv (curva del robot al 40 %), se quitan los
costes de Binance de cada operación y se ponen los del perfil. Se comprueba contra los perfiles que ya calculó el motor.

Uso: python motor/perfil_sin_velas.py            → imprime la comprobación y resultados/perfil_exness.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
RAIZ = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(RAIZ / "motor"))
from btc_lunes_motor import EXCHANGES, ROBOT, coste_lado, metricas

C_BIN = 0.0014
T = pd.read_csv(RAIZ / "resultados" / "trades.csv", parse_dates=["entrada", "salida"])
EQ = pd.read_csv(RAIZ / "resultados" / "equity_diaria.csv", index_col=0, parse_dates=True)["robot_40"]
M = json.loads((RAIZ / "resultados" / "metricas.json").read_text(encoding="utf-8")); SP = pd.Timestamp(M["meta"]["oos_desde"])


def curva(c):
    """Retornos por operación y curva diaria del robot (40 %) con un coste por lado c."""
    o_in, o_out = T.px_ent / (1 + C_BIN), T.px_sal / (1 - C_BIN)
    r = (o_out * (1 - c)) / (o_in * (1 + c)) - 1
    # curva diaria: la del robot con Binance, corregida en la fecha de salida de cada operación por la diferencia de coste
    f = pd.Series((1 + ROBOT * r.values) / (1 + ROBOT * T.ret.values), index=T.salida.dt.normalize()).groupby(level=0).prod()
    return r, EQ * f.reindex(EQ.index).fillna(1.0).cumprod()


def perfil(c):
    r, eq = curva(c)
    trs = [dict(ret=float(x), barras=int(b), entrada=e) for x, b, e in zip(r, T.barras, T.entrada)]
    tod = metricas(trs, eq, "robot")
    eo = eq[eq.index >= SP]; eo = eo / eo.iloc[0]
    oos = metricas([t for t in trs if t["entrada"] > SP], eo, "robot")       # el corte del motor cae dentro del 8 ene 2024: ese lunes es construcción
    return tod, oos


def main():
    print("comprobación contra el motor (PF validación · CAGR · drawdown diario · PF todo):")
    for k in ["binance", "quantfury", "coinbase"]:
        tod, oos = perfil(coste_lado(k)); ref = M["exchanges"][k]
        print(f"  {k:9s} mío {oos['pf']:.3f} · {oos['cagr']*100:.2f} % · {oos['mdd_diario']*100:.2f} % · {tod['pf']:.3f}   "
              f"motor {ref['OOS']['pf']:.3f} · {ref['OOS']['cagr']*100:.2f} % · {ref['OOS']['mdd_diario']*100:.2f} % · {ref['TODO']['pf']:.3f}")
    c = coste_lado("exness"); tod, oos = perfil(c); e = EXCHANGES["exness"]
    out = dict(nombre=e["nombre"], coste_lado_bps=c * 1e4, ida_vuelta_pct=c * 2 * 100, nota=e["nota"], TODO=tod, OOS=oos,
               metodo="perfil_sin_velas.py: trades.csv + equity_diaria.csv con los costes del perfil (sin regenerar velas)")
    (RAIZ / "resultados" / "perfil_exness.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  exness    {oos['pf']:.3f} · {oos['cagr']*100:.2f} % · {oos['mdd_diario']*100:.2f} % · {tod['pf']:.3f}   ({c*1e4:.2f} bps por lado)")


if __name__ == "__main__":
    main()
