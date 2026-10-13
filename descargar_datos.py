"""
Descarga el histórico HORARIO de Bitcoin desde dos exchanges y lo guarda en data/:

  data/BTCUSDT_binance_H1.csv   Binance spot, par BTC/USDT, velas de 1 hora desde agosto de 2017 (la fuente principal de la guía)
  data/BTCUSD_coinbase_H1.csv   Coinbase, par BTC/USD, velas de 1 hora (el contraste: otro exchange, otra moneda de cotización)

Las dos descargas usan la API pública de cada exchange a través de ccxt; no hace falta cuenta ni clave.
Cada fila: Date (apertura de la vela, UTC), Open, High, Low, Close, Volume.

Uso:  python descargar_datos.py                 # las dos
      python descargar_datos.py --solo binance  # una
"""
import argparse, time
from pathlib import Path

import ccxt, pandas as pd

DATA = Path(__file__).resolve().parent / "data"
FUENTES = {
    "binance": dict(clase=ccxt.binance, simbolo="BTC/USDT", desde="2017-08-17T00:00:00Z", fichero="BTCUSDT_binance_H1.csv", limite=1000),
    "coinbase": dict(clase=ccxt.coinbase, simbolo="BTC/USD", desde="2017-08-17T00:00:00Z", fichero="BTCUSD_coinbase_H1.csv", limite=300),
}


def descargar(nombre):
    f = FUENTES[nombre]; ex = f["clase"]({"enableRateLimit": True})
    desde = ex.parse8601(f["desde"]); fin = ex.milliseconds(); filas = []
    print(f"{nombre}: descargando {f['simbolo']} 1h desde {f['desde'][:10]} …", flush=True)
    while desde < fin:
        try:
            lote = ex.fetch_ohlcv(f["simbolo"], timeframe="1h", since=desde, limit=f["limite"])
        except Exception as e:                       # red o límite de peticiones: espera y reintenta
            print(f"  reintento ({e.__class__.__name__})"); time.sleep(5); continue
        if not lote:
            desde += f["limite"] * 3600_000; continue    # hueco en el histórico: salta hacia delante
        filas.extend(lote); desde = lote[-1][0] + 3600_000
        if len(filas) % 20000 < f["limite"]:
            print(f"  {len(filas):,} velas · {pd.Timestamp(lote[-1][0], unit='ms').date()}", flush=True)
    d = pd.DataFrame(filas, columns=["ts", "Open", "High", "Low", "Close", "Volume"]).drop_duplicates("ts")
    d["Date"] = pd.to_datetime(d.ts, unit="ms", utc=True).dt.tz_localize(None)
    d = d.drop(columns="ts").set_index("Date").sort_index()
    d = d[(d.High >= d.Low) & (d.Close > 0)]
    DATA.mkdir(exist_ok=True); d.round(2).to_csv(DATA / f["fichero"])
    print(f"{nombre}: {len(d):,} velas horarias · {d.index[0]} → {d.index[-1]} · guardado en {DATA / f['fichero']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--solo", choices=list(FUENTES)); a = ap.parse_args()
    for n in ([a.solo] if a.solo else FUENTES):
        descargar(n)
