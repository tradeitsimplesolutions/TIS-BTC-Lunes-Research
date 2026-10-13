"""
Reconciliación del EA (codigo/TIS_BTC_Lunes_v3.mq5, v1.1) con el motor, sobre el Strategy Tester de MetaTrader 5.

MT5: Exness, símbolo BTCUSDz, H1, ModoHorario = desfase fijo 0 (el servidor de Exness va en GMT+0), 40 % del equity.
Motor: resultados/trades.csv (v3 sobre las velas de Binance). Se emparejan las operaciones por lunes.
Además mide los costes reales del CFD (spread, comisión, swap) para el perfil "exness" de btc_lunes_motor.py.

Uso: python motor/reconciliar_mt5.py [informe.html]  → resultados/reconciliacion_mt5.json
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
INFORME = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "resultados" / "mt5_report_Exness_BTCUSDz_2026-10-12.html"
COSTE_MOTOR = 0.0014                                     # coste por lado con el que se generó trades.csv (Binance)


def leer_mt5(path):
    t = pd.read_html(path)[1]; t.columns = range(t.shape[1])
    hdr = t.index[t[0].astype(str).str.contains("Fecha/Hora") & t[1].astype(str).str.contains("Transacc")][0]
    d = t.loc[hdr + 1:].copy(); d.columns = ["fecha", "deal", "sym", "tipo", "dir", "vol", "precio", "orden", "com", "swap", "ben", "bal", "coment"]
    d = d[d.dir.isin(["in", "out"])].copy()
    for c in ["vol", "precio", "com", "swap", "ben"]:
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(" ", "").str.replace("\xa0", ""), errors="coerce")
    d["fecha"] = pd.to_datetime(d.fecha, format="%Y.%m.%d %H:%M:%S")
    i, o = d[d.dir == "in"].reset_index(drop=True), d[d.dir == "out"].reset_index(drop=True)
    tr = pd.DataFrame(dict(entrada=i.fecha, salida=o.fecha, p_in=i.precio, p_out=o.precio, vol=i.vol,
                           com=i.com.values + o.com.values, swap=i.swap.values + o.swap.values, ben=o.ben.values))
    tr["nocional"] = tr.vol * tr.p_in; tr["ret_px"] = tr.p_out / tr.p_in - 1
    tr["neto"] = (tr.ben + tr.com + tr.swap) / tr.nocional
    return tr


def main():
    tr = leer_mt5(INFORME); tr["lunes"] = tr.entrada.dt.normalize()
    m = pd.read_csv(RAIZ / "resultados" / "trades.csv", parse_dates=["entrada"]); m["lunes"] = m.entrada.dt.normalize()
    m = m[m.lunes >= tr.lunes.min()]
    j = m.merge(tr, on="lunes", how="outer", suffixes=("_m", "_t"), indicator=True); b = j[j._merge == "both"]
    px_in_bin = b.px_ent / (1 + COSTE_MOTOR); px_out_bin = b.px_sal / (1 - COSTE_MOTOR); bruto_bin = px_out_bin / px_in_bin - 1
    pf = lambda r: float(r[r > 0].sum() / -r[r <= 0].sum())
    spread_rt = float(-(b.ret_px - bruto_bin).mean() * 1e4); com_lado = float((-tr.com / 2 / tr.nocional).mean() * 1e4); swap = float((-tr.swap / tr.nocional).mean() * 1e4)
    out = dict(fichero=INFORME.name, plataforma="MetaTrader 5 Strategy Tester · Exness · BTCUSDz H1 · desfase fijo 0 · 40 % equity",
               ea="TIS_BTC_Lunes_v3.mq5 v1.1", desde=str(tr.entrada.min().date()), hasta=str(tr.entrada.max().date()),
               horas_entrada_servidor=sorted(set(tr.entrada.dt.hour.tolist())), dias_entrada=sorted(set(tr.entrada.dt.dayofweek.tolist())),
               mt5=dict(n=int(len(tr)), pf_neto=pf(tr.neto.to_numpy()), win=float((tr.neto > 0).mean())),
               motor=dict(n=int(len(m)), pf=pf(m.ret.to_numpy()), win=float((m.ret > 0).mean())),
               emparejadas=int(len(b)), solo_mt5=[str(x.date()) for x in j[j._merge == "right_only"].lunes], solo_motor=[str(x.date()) for x in j[j._merge == "left_only"].lunes],
               dif_precio_entrada_pct=dict(mediana=float(((b.p_in / px_in_bin - 1).abs() * 100).median()), max=float(((b.p_in / px_in_bin - 1).abs() * 100).max())),
               dif_retorno_bruto_pp=dict(mediana=float(((b.ret_px - bruto_bin).abs() * 100).median()), max=float(((b.ret_px - bruto_bin).abs() * 100).max()), correlacion=float(np.corrcoef(b.ret_px, bruto_bin)[0, 1])),
               costes_medidos_bps=dict(spread_ida_vuelta=spread_rt, comision_por_lado=com_lado, swap_por_operacion=swap,
                                       swap_por_ano={int(k): float(v) for k, v in (-tr.swap / tr.nocional * 1e4).groupby(tr.entrada.dt.year).mean().items()}),
               nota="El historial de BTCUSDz en el tester empieza a finales de 2020: en 2021 la ventana del percentil es más corta que el año del motor. "
                    "Las demás diferencias son lunes en el límite del p30 con las velas del CFD frente a las de Binance.")
    # percentiles que el EA escribió en el log del agente para los lunes que no coinciden (2.ª prueba, ModoHorario = desfase fijo 0)
    out["diferencias_explicadas"] = dict(
        log="mt5_agente_Exness_BTCUSDz_2026-10-12.log", historial_mt5_desde="2021-01-01",
        solo_motor={"2021-05-10": dict(pct_mt5=20.7, pct_motor=60.0, atr_mt5=1.123, atr_motor=1.138),
                    "2021-08-16": dict(pct_mt5=14.7, pct_motor=33.8, atr_mt5=0.977, atr_motor=0.979),
                    "2022-01-31": dict(pct_mt5=23.0, pct_motor=32.3, atr_mt5=0.941, atr_motor=0.997)},
        solo_mt5={"2021-11-29": 30.4, "2023-04-24": 30.8, "2023-05-08": 31.4, "2023-08-21": 32.2, "2024-01-22": 36.8, "2024-05-27": 33.1},
        atr_pct_dif_relativa_mediana_pct=3.2, percentil_dif_mediana_puntos=1.7,
        conclusion="Las 3 del motor: mismo ATR%, pero en MT5 la ventana del percentil empieza en enero de 2021 (2021 muy volátil) y el lunes queda por debajo del p30. "
                   "Las 6 de MT5: percentil entre 30,4 y 36,8, justo por encima del umbral; con las velas de Binance quedan por debajo. Ninguna es un error del EA.")
    (RAIZ / "resultados" / "reconciliacion_mt5.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"MT5 {out['mt5']['n']} ops · motor {out['motor']['n']} · emparejadas {out['emparejadas']} · precio entrada mediana {out['dif_precio_entrada_pct']['mediana']:.3f} % · "
          f"retorno mediana {out['dif_retorno_bruto_pp']['mediana']:.3f} pp · spread {spread_rt:.1f} bps i/v · comisión {com_lado:.2f} bps/lado · swap {swap:.1f} bps/op")


if __name__ == "__main__":
    main()
