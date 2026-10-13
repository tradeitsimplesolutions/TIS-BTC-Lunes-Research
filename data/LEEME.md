# Datos

Los dos ficheros de velas horarias no se versionan (son grandes y se regeneran en un minuto):

```
python descargar_datos.py                 # Binance (BTC/USDT) y Coinbase (BTC/USD), 1 hora, desde agosto de 2017
python descargar_datos.py --solo binance  # solo uno
```

- `BTCUSDT_binance_H1.csv` — la fuente de todas las cifras y gráficos de la guía.
- `BTCUSD_coinbase_H1.csv` — el contraste: otro exchange, otra moneda de cotización (USD), otras comisiones.

Ambos vienen de la API pública de cada exchange a través de `ccxt`; no hace falta cuenta ni clave.
Columnas: `Date` (apertura de la vela, UTC), `Open`, `High`, `Low`, `Close`, `Volume`.
El motor acepta cualquier CSV horario con esas columnas: `python motor/btc_lunes_motor.py --csv mi_fichero.csv --etiqueta otro`.
