"""
Reconciliación del Pine v3 (codigo/TIS_BTC_Lunes_v3.pine) con el motor, sobre el Strategy Tester de TradingView.

TradingView: BINANCE:BTCUSDT 1H, 16 ago 2017 → 12 oct 2026 (Deep Backtesting), 40 % del equity, comisión 0,14 % por lado.
Las horas del export están en la zona del gráfico: America/New_York (UTC−5 en invierno, UTC−4 en verano).
Motor: resultados/trades.csv (v3, velas de Binance, 14 bps por lado). Se emparejan las operaciones por lunes.

Uso: python motor/reconciliar_tv_v3.py [export.csv]  → resultados/reconciliacion_tradingview_v3.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
EXPORT = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "resultados" / "tradingview_export_v3_BINANCE_2026-10-12.csv"
ZONA = "America/New_York"                                # zona horaria del gráfico al exportar


def main():
    t = pd.read_csv(EXPORT, encoding="utf-8-sig")
    e = t[t["Tipo"].str.startswith("Entrada")].copy(); s = t[t["Tipo"].str.startswith("Salida")].copy()
    a_utc = lambda c: pd.to_datetime(c).dt.tz_localize(ZONA, ambiguous="NaT", nonexistent="shift_forward").dt.tz_convert("UTC").dt.tz_localize(None)
    e["utc"] = a_utc(e["Fecha y hora"]); s["utc"] = a_utc(s["Fecha y hora"])
    tv = e[["Número de operación", "utc", "Precio USDT", "Rentabilidad %"]].merge(s[["Número de operación", "utc", "Precio USDT"]], on="Número de operación", suffixes=("_in", "_out"))
    tv["ret"] = tv["Rentabilidad %"] / 100
    tv["lunes"] = (tv.utc_in + pd.Timedelta(hours=1)).dt.normalize()     # la orden se llena al cierre de la vela del domingo 23:00 UTC = lunes 00:00
    m = pd.read_csv(RAIZ / "resultados" / "trades.csv", parse_dates=["entrada"]); m["lunes"] = m.entrada.dt.normalize()
    j = m.merge(tv, on="lunes", how="outer", indicator=True); b = j[j._merge == "both"]
    pf = lambda r: float(r[r > 0].sum() / -r[r <= 0].sum())
    px_bin = b.px_ent / 1.0014
    out = dict(fichero=EXPORT.name, plataforma="TradingView Strategy Tester · BINANCE:BTCUSDT 1H · comisión 0,14 % por lado · 40 % equity", script="TIS_BTC_Lunes_v3.pine",
               desde=str(tv.lunes.min().date()), hasta=str(tv.lunes.max().date()),
               horas_entrada_utc=sorted(set(tv.utc_in.dt.hour)), dias_entrada_utc=sorted(set(tv.utc_in.dt.dayofweek)),
               tv=dict(n=int(len(tv)), pf=pf(tv.ret.to_numpy()), win=float((tv.ret > 0).mean())),
               motor=dict(n=int(len(m)), pf=pf(m.ret.to_numpy()), win=float((m.ret > 0).mean())),
               emparejadas=int(len(b)), solo_tv=[str(x.date()) for x in j[j._merge == "right_only"].lunes], solo_motor=[str(x.date()) for x in j[j._merge == "left_only"].lunes],
               dif_precio_entrada_pct=dict(mediana=float(((b["Precio USDT_in"] / px_bin - 1).abs() * 100).median()), max=float(((b["Precio USDT_in"] / px_bin - 1).abs() * 100).max())),
               dif_retorno_pp=dict(mediana=float(((b.ret_y - b.ret_x).abs() * 100).median()) if "ret_y" in b else None, max=float(((b.ret_y - b.ret_x).abs() * 100).max()) if "ret_y" in b else None,
                                   correlacion=float(np.corrcoef(b.ret_x, b.ret_y)[0, 1]) if "ret_y" in b else None),
               signo_distinto=[str(x.date()) for x, a, c in zip(b.lunes, b.ret_x, b.ret_y) if np.sign(a) != np.sign(c)],
               nota="TradingView entra al cierre de la vela del domingo 23:00 UTC y el motor a la apertura del lunes 00:00 UTC: es casi el mismo precio.")
    (RAIZ / "resultados" / "reconciliacion_tradingview_v3.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"TradingView {out['tv']['n']} ops (PF {out['tv']['pf']:.3f}) · motor {out['motor']['n']} (PF {out['motor']['pf']:.3f}) · emparejadas {out['emparejadas']} · "
          f"solo TV {out['solo_tv']} · solo motor {out['solo_motor']} · precio entrada mediana {out['dif_precio_entrada_pct']['mediana']:.4f} % · "
          f"retorno mediana {out['dif_retorno_pp']['mediana']:.4f} pp · corr {out['dif_retorno_pp']['correlacion']:.5f} · signo distinto {out['signo_distinto']}")


if __name__ == "__main__":
    main()
