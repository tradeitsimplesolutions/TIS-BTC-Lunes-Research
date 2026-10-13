# BTC · Efecto Lunes — Trade It Simple

Estrategia **#2** del material de trading sistemático de [Trade It Simple](https://instagram.com/mariellangsaez):
un sesgo estacional en Bitcoin —el lunes— que empezó siendo el "efecto fin de semana" de los papers, se desgastó,
y volvió con otra forma cuando BTC cambió de dueños. Aquí está **todo**: cómo descubrimos el edge, el AED, las reglas,
la validación con las cinco fases, la revisión completa (horas, duración, salidas, filtros), los tres exchanges con
sus costes reales, el robot y el motor que generó cada cifra y cada gráfico. Sin cajas negras.

> La estrategia no es el premio. El premio es aprender a **construir, validar y confiar** en la tuya.

---

## 📘 Empieza por aquí

Abre en el navegador (son autocontenidas; solo la superficie 3D del manual carga una librería de internet):

- **[`guia/btc-lunes-ficha.html`](guia/btc-lunes-ficha.html)** — la estrategia de principio a fin: reglas, resultado,
  cómo descubrimos el edge, origen, riesgo y tamaño, dónde operarla (Binance, Coinbase, Quantfury) y el código.
- **[`guia/btc-lunes-validacion.html`](guia/btc-lunes-validacion.html)** — el manual avanzado: AED por eras, las cinco
  fases, test del mono, la revisión completa (horas, duración, take profit y stop, MAE/MFE, filtros), Monte Carlo por
  tamaño, drawdowns, desgaste y la vigilancia del edge en real.

## 🚀 Reprodúcelo tú

```bash
pip install -r requirements.txt
python descargar_datos.py             # Binance (BTC/USDT) y Coinbase (BTC/USD), velas de 1 hora desde 2017, API pública
python motor/btc_lunes_motor.py       # las 5 fases + AED + revisión + exchanges → resultados/ (JSON, trades, 29 gráficos)
python motor/btc_lunes_motor.py --csv data/BTCUSD_coinbase_H1.csv --etiqueta coinbase --exchange coinbase --solo-metricas
python motor/reconciliar_tv.py        # v1 original: empareja el export del Strategy Tester de TradingView con el motor
python motor/reconciliar_tv_v3.py     # v3: export del Strategy Tester de TradingView (BINANCE:BTCUSDT) ↔ motor
python motor/reconciliar_mt5.py       # v3: informe del Strategy Tester de MetaTrader 5 (Exness) ↔ motor, y costes del CFD
python motor/perfil_sin_velas.py      # métricas de otro perfil de costes a partir de trades.csv, sin volver a bajar velas
python motor/construir_html.py        # comprueba los resultados (motor/test_resultados.py) y construye las dos páginas
```

## 📐 La regla (la misma en el motor y en el robot)

| | |
|---|---|
| **Entrada** | Compra a la apertura de las 00:00 UTC del lunes (la orden se decide al cierre de la vela de las 23:00 del domingo) |
| **Salida** | Venta a la apertura de las 00:00 UTC del martes: 24 velas. Sin stop, sin take profit |
| **Permiso** | Solo si el ATR%(48) de la vela de señal está por encima del percentil 30 de las últimas 8.760 velas (un año) |
| **Calendario** | No se opera el primer lunes del mes (día 1 a 7) |
| **Tamaño** | 40 % del capital por operación, sin apalancar (el tope que admite el Monte Carlo) |
| **Costes** | Por lado: mitad del spread + 3 bps de slippage + comisión del exchange (+ la mitad del swap en un CFD). Binance spot: 14 bps por lado (0,28 % ida y vuelta) |

## 🗂️ Estructura

```
├── guia/                          Las dos páginas HTML (empieza aquí) + logo
├── motor/
│   ├── btc_lunes_motor.py         Backtest, 5 fases, Monte Carlo por tamaño, estrés, mono, desgaste, AED, revisión, exchanges, vigilancia
│   ├── graficos.py                Los 29 gráficos
│   ├── reconciliar_tv.py          Paridad de la v1 con el Strategy Tester de TradingView
│   ├── reconciliar_tv_v3.py       Paridad de la v3 con el Strategy Tester de TradingView (183/183)
│   ├── reconciliar_mt5.py         Paridad del EA con el Strategy Tester de MetaTrader 5 (Exness) y costes del CFD
│   ├── perfil_sin_velas.py        Métricas de un perfil de costes nuevo sin regenerar las velas
│   ├── test_resultados.py         Pruebas de coherencia (las lanza construir_html.py)
│   ├── comun.py · pagina_ficha.py · pagina_manual.py · construir_html.py
├── codigo/
│   ├── TIS_BTC_Lunes_v3.pine      Pine Script v6 de la versión validada (alertas para Make)
│   ├── TIS_BTC_Lunes_v3.mq5       El robot para MetaTrader 5 (v1.1; se compila en MetaEditor con F7)
│   └── TIS_BTC_Lunes_v1_original.pine   La versión original de 2025, la que opera en real desde febrero de 2025
├── resultados/
│   ├── metricas.json              Todas las cifras (Binance)
│   ├── metricas_coinbase.json     Mismas reglas sobre los datos de Coinbase con costes de Coinbase
│   ├── reconciliacion_tradingview.json + tradingview_export_MEXC_2026-09-30.xlsx        (v1)
│   ├── reconciliacion_tradingview_v3.json + tradingview_export_v3_BINANCE_2026-10-12.csv (v3)
│   ├── reconciliacion_mt5.json + mt5_report_Exness_BTCUSDz_2026-10-12.html + log del agente
│   ├── perfil_exness.json         La v3 con los costes del CFD de Exness
│   ├── trades.csv · equity_diaria.csv · equity_semanal.json
│   └── graficos/
├── data/                          Se regenera con descargar_datos.py (ver data/LEEME.md)
├── descargar_datos.py
└── requirements.txt
```

## ⚠️ Lo que conviene saber

- La versión que opera en real desde febrero de 2025 es la **original** (filtros fijos). La **v3** es la validada; las dos están en `codigo/`.
- **Paridad cerrada en las tres plataformas** (octubre de 2026): v1 en TradingView 156/156; v3 en TradingView 183/183 (BINANCE:BTCUSDT, 0,14 % por lado, mismo precio de entrada); EA en MetaTrader 5 (Exness) 97/103 el mismo lunes, con las diferencias explicadas en `reconciliacion_mt5.json` (historial del CFD desde 2021 y lunes en el límite del p30).
- **Exness (CFD en MT5)**: spread flotante (≈ 2 bps ida y vuelta medido en el tester), comisión 4,375 $/lote en la entrada y swap largo −1.863,7 puntos por noche (≈ 2,2 bps con BTC a 83.000 $). En el EA, `ModoHorario` = desfase fijo y `OffsetFijoUTC` = 0: el servidor de Exness va en GMT+0.
- Las cifras de "en real" de la guía son las que el motor habría dado con las velas de Binance; la lista de operaciones reales se añadirá cuando esté.
- La Fase 5 se publica con una **excepción documentada**: el escenario 2018 + 2022 da PF 0,79 por un solo año (2022, 13 operaciones).
- La Fase 4 con bloques de 5 operaciones (conserva las rachas) deja el p95 del drawdown al 40 % en el límite del 25 %; al 30 % cumple. Está dicho en el manual.

Material educativo. No es asesoría financiera. Los resultados pasados no garantizan resultados futuros.
