"""
Reconciliación del motor con el Strategy Tester de TradingView (la paridad con la plataforma real).

TradingView: la versión original (v1 de 2025) sobre MEXC:BTCUSDT 1H, comisión 0, 100 % del equity, export del 30/09/2026
(resultados/tradingview_export_MEXC_2026-09-30.xlsx; las fechas del export están en hora de Nueva York).
Motor: la misma regla ("pine") sobre las velas de Binance, con costes a cero. Se emparejan las operaciones por lunes.

Uso: python motor/reconciliar_tv.py  → resultados/reconciliacion_tradingview.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

RAIZ = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(RAIZ / "motor"))
from btc_lunes_motor import cargar, preparar, backtest

EXPORT = RAIZ / "resultados" / "tradingview_export_MEXC_2026-09-30.xlsx"


def main():
    t = pd.read_excel(EXPORT, sheet_name="Trades"); e = t[t["Type"] == "Entry long"].copy(); e["dt"] = pd.to_datetime(e["Date and time"])
    ny = e.dt.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward")
    e["lunes"] = (ny.dt.tz_convert("UTC").dt.tz_localize(None) + pd.Timedelta(hours=1)).dt.normalize()
    df = preparar(cargar(RAIZ / "data" / "BTCUSDT_binance_H1.csv"))
    tr = [x for x in backtest(df, "pine", coste=0.0) if x["entrada"] >= e.lunes.min()]
    mot = pd.DataFrame(dict(lunes=[x["entrada"].normalize() for x in tr], px_in=[x["px_ent"] for x in tr], ret=[x["ret"] * 100 for x in tr]))
    j = e[["lunes", "Price USDT", "Return %"]].merge(mot, on="lunes", how="outer", indicator=True); both = j[j._merge == "both"]
    pf = lambda r: float(r[r > 0].sum() / -r[r <= 0].sum())
    # tramo en REAL: desde el 1 de febrero de 2025 todo lo que hay en TradingView son operaciones reales (alertas de TradingView → exchange)
    # Desde el 2026-10-02: a las operaciones reales se les mete la comisión de Binance spot (14 bps por lado = 0,28 % por ida y vuelta).
    from btc_lunes_motor import coste_lado
    LIVE = pd.Timestamp("2025-02-01"); coste_rt = coste_lado("binance") * 2 * 100
    real = e[e.lunes >= LIVE].copy(); bruto = real["Return %"].to_numpy(); rr = bruto - coste_rt
    ref = np.array([x["ret"] * 100 for x in backtest(df, "pine", coste=coste_lado("binance")) if x["entrada"] < LIVE])   # lo que esperaba la regla original, con costes, antes del live
    mu0, s0 = float(ref.mean()), float(ref.std(ddof=1)); med20 = pd.Series(rr).rolling(20).mean(); z = (med20 - mu0) / (s0 / np.sqrt(20))
    eq = np.cumprod(1 + rr / 100); mdd = float(((eq - np.maximum.accumulate(eq)) / np.maximum.accumulate(eq)).min())
    real_out = dict(desde=str(real.dt.min().date()), hasta=str(real.dt.max().date()), n=int(len(real)), coste_ida_vuelta_pct=float(coste_rt),
                    pf=pf(rr), suma_pct=float(rr.sum()), ret_total_pct=float((eq[-1] - 1) * 100), win=float((rr > 0).mean()), media_pct=float(rr.mean()), mdd_pct=mdd * 100,
                    mejor_pct=float(rr.max()), peor_pct=float(rr.min()), bruto=dict(pf=pf(bruto), suma_pct=float(bruto.sum()), ret_total_pct=float((np.cumprod(1 + bruto / 100)[-1] - 1) * 100), win=float((bruto > 0).mean())),
                    referencia=dict(n=int(len(ref)), mu0_pct=mu0, sigma0_pct=s0), z_hoy=(float(z.iloc[-1]) if not np.isnan(z.iloc[-1]) else None),
                    serie=[dict(fecha=str(d.date()), ret=float(x), z=(float(zz) if not np.isnan(zz) else None)) for d, x, zz in zip(real.lunes, rr, z)],
                    nota="Retornos de precio del Strategy Tester (comisión 0, 100 % del equity) menos el coste de Binance spot por ida y vuelta.")
    out = dict(fichero=EXPORT.name, plataforma="TradingView Strategy Tester · MEXC:BTCUSDT 1H · comisión 0 · 100 % equity", regla="v1 original (ATR% 0,40–1,20 y |ret 24h| ≤ 4 %)", real=real_out,
               desde=str(e.dt.min().date()), hasta=str(e.dt.max().date()), tv=dict(n=int(len(e)), pf=pf(e["Return %"].to_numpy()), suma_pct=float(e["Return %"].sum()), net_profit_pct=194.47),
               motor=dict(n=int(len(tr)), pf=pf(mot.ret.to_numpy()), suma_pct=float(mot.ret.sum())),
               emparejadas=int(len(both)), solo_tv=[str(x.date()) for x in j[j._merge == "left_only"].lunes], solo_motor=[str(x.date()) for x in j[j._merge == "right_only"].lunes],
               dif_precio_entrada_pct=dict(mediana=float(((both["Price USDT"] / both.px_in - 1).abs() * 100).median()), max=float(((both["Price USDT"] / both.px_in - 1).abs() * 100).max())),
               dif_retorno_pp=dict(mediana=float((both["Return %"] - both.ret).abs().median()), max=float((both["Return %"] - both.ret).abs().max())),
               nota="Las operaciones extra del motor son lunes en los que el filtro queda en el límite con velas de Binance frente a MEXC.")
    (RAIZ / "resultados" / "reconciliacion_tradingview.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"TradingView {out['tv']['n']} ops · motor {out['motor']['n']} · emparejadas {out['emparejadas']} · precio entrada mediana {out['dif_precio_entrada_pct']['mediana']:.3f} % · retorno mediana {out['dif_retorno_pp']['mediana']:.3f} pp")


if __name__ == "__main__":
    main()
