"""
BTC · Efecto Lunes (v3) — motor de backtest y validación (Trade It Simple).

La regla (hora UTC, velas de 1 hora de Binance):
  Entrada : compra a la apertura de las 00:00 UTC del lunes (la orden se decide al cierre de la vela de las 23:00 del domingo)
  Salida  : venta a la apertura de las 00:00 UTC del martes (24 velas después). Sin stop, sin take profit.
  Permiso : solo si el ATR%(48) de la vela de señal está por encima del percentil 30 de las últimas 8.760 velas (un año):
            el lunes paga cuando BTC se mueve; en calma no cubre los costes.
  Calendario: no se opera el primer lunes del mes (día 1 a 7).
  Costes  : por lado, spread/2 + slippage + comisión del exchange (Binance spot 14 bps/lado = 0,28 % ida y vuelta).

Tres versiones, mismas operaciones de base (todos los lunes):
  "base"  → sin filtros                           "pine" → la versión original de 2025 (ATR% fijo 0,40–1,20 y |ret 24h| ≤ 4 %)
  "v3"    → la validada (percentil de ATR + sin primer lunes del mes)

Tamaños (mismas señales): "capital" 100 % · "robot" 40 % (el que opera: tope del Monte Carlo) · "p20" 20 % · "x2" 200 % · "fijo" 10.000 $ sin reinvertir.

Uso:
  python motor/btc_lunes_motor.py                                  # Binance (data/BTCUSDT_binance_H1.csv)
  python motor/btc_lunes_motor.py --csv data/BTCUSD_coinbase_H1.csv --etiqueta coinbase --exchange coinbase --solo-metricas
Salidas en resultados/: metricas.json, trades.csv, equity_diaria.csv, equity_semanal.json y graficos/*.png
"""
import argparse, itertools, json
from pathlib import Path
import numpy as np, pandas as pd

ATR_LEN, PCT_MIN, VENTANA_PCT, IS_FRAC = 48, 0.30, 8760, 0.70
ROBOT, P20, X2 = 0.40, 0.20, 2.0
RIESGO_ATR, K_ATR = 0.01, 2.0                      # sizing por ATR (comparación): 1 % de riesgo con stop virtual a 2 ATR diarios
VOL_OBJ = 0.015                                    # vol targeting (comparación): objetivo de 1,5 % de volatilidad diaria, tope 100 %
ATR_LENS, PCTS = [24, 30, 36, 42, 48, 56, 64, 72, 84, 96], [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]   # rejilla de parámetros (Fase 3): longitud del ATR × suelo del percentil
ATR_LENS_GRUESO, PCTS_GRUESO = [24, 36, 48, 72, 96], [0.10, 0.20, 0.30, 0.40, 0.50]                              # subconjunto para el gráfico de barras
PINE_ATR_MIN, PINE_ATR_MAX, PINE_RET24 = 0.40, 1.20, 4.0
LIVE_DESDE = pd.Timestamp("2025-02-01")           # la regla original opera en real desde febrero de 2025
ERAS = [("retail · 2017-19", None, "2020-01-01"), ("institucional · 2020-23", "2020-01-01", "2024-01-01"), ("ETF · 2024-26", "2024-01-01", None)]
# Costes por lado en puntos básicos: mitad del spread + slippage (supuesto, 3 bps) + comisión taker. Tarifas públicas base, leídas el 2026-10-02.
EXCHANGES = {
    "binance":   dict(nombre="Binance spot",   spread_bps=2.0, slippage_bps=3.0, comision_bps=10.0, nota="taker 0,10 % (0,075 % pagando con BNB)"),
    "coinbase":  dict(nombre="Coinbase Advanced", spread_bps=2.0, slippage_bps=3.0, comision_bps=60.0, nota="taker 0,60 % en el tramo base (< 10.000 $ al mes); 0,40 % con orden límite"),
    "quantfury": dict(nombre="Quantfury",      spread_bps=2.0, slippage_bps=3.0, comision_bps=0.0,  nota="sin comisión; cobra el spread real del exchange"),
    # CFD en MetaTrader 5 (BTCUSDz, cuenta Exness). Especificación del símbolo leída el 2026-10-12 con BTC ≈ 83.200 $:
    # spread flotante (≈ 2 bps ida y vuelta medido en el Strategy Tester), comisión 4,375 $ por lote solo en la entrada (≈ 0,26 bps por lado),
    # swap largo −1.863,7 puntos = −18,64 $ por BTC y noche (≈ 2,24 bps; la operación cruza una noche, la del lunes, coeficiente 1).
    # El swap se reparte mitad y mitad entre los dos lados. Reconciliación del EA: resultados/reconciliacion_mt5.json.
    "exness":    dict(nombre="Exness (CFD MT5)", spread_bps=2.0, slippage_bps=3.0, comision_bps=0.26, swap_bps=2.24, nota="CFD BTCUSDz: spread flotante, comisión 4,375 $/lote en la entrada y swap largo de una noche"),
}
RAIZ = Path(__file__).resolve().parent.parent
OUT = RAIZ / "resultados"
rng = np.random.default_rng(42)


def coste_lado(exchange="binance", factor=1.0):
    e = EXCHANGES[exchange]; return (e["spread_bps"] / 2 + e["slippage_bps"] + e["comision_bps"] + e.get("swap_bps", 0.0) / 2) / 1e4 * factor


# ----------------------------------------------------------------- datos e indicadores
def cargar(csv):
    df = pd.read_csv(csv, parse_dates=["Date"]).set_index("Date").sort_index()
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    return df[~df.index.duplicated(keep="last")]


def preparar(raw, atr_len=ATR_LEN):
    df = raw.copy(); c = df["Close"]
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - c.shift()).abs(), (df["Low"] - c.shift()).abs()], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1 / atr_len, min_periods=atr_len, adjust=False).mean()
    df["atr_pct"] = df["atr"] / c * 100
    df["pct"] = df["atr_pct"].rolling(VENTANA_PCT, min_periods=500).rank(pct=True)
    df["ret24"] = (c / c.shift(24) - 1) * 100
    df["sma50"] = c.rolling(50 * 24).mean(); df["sma200"] = c.rolling(200 * 24).mean()   # medias de 50 y 200 días sobre velas horarias
    return df


def lunes_de(df):
    idx = df.index
    return idx[(idx.dayofweek == 0) & (idx.hour == 0) & (idx.minute == 0)]


# ----------------------------------------------------------------- backtest
def backtest(df, version="v3", coste=None, off_in=0, off_out=0, pct_min=PCT_MIN, saltar_primer=True, hold=24, lunes=None, estricto=False):
    """Una operación por lunes. version: 'v3' | 'pine' | 'base'. off_in/off_out en horas respecto a lunes 00:00 / martes 00:00.
    Devuelve lista de trades (dict) ordenada por fecha. estricto=True exige que las 24 velas de la posición existan."""
    coste = coste_lado() if coste is None else coste
    o, h, l, c = df["Open"].values, df["High"].values, df["Low"].values, df["Close"].values
    pct, atrp, r24 = df["pct"].values, df["atr_pct"].values, df["ret24"].values
    s50 = df["sma50"].values if "sma50" in df else np.full(len(df), np.nan); s200 = df["sma200"].values if "sma200" in df else np.full(len(df), np.nan)
    base = lunes_de(df) if lunes is None else lunes
    t_in = base + pd.Timedelta(hours=off_in); t_out = t_in + pd.Timedelta(hours=hold + off_out - off_in)
    pi, po = df.index.get_indexer(t_in), df.index.get_indexer(t_out)
    trades = []
    for k in range(len(base)):
        i, j = pi[k], po[k]
        if i <= 0 or j <= i or (estricto and j - i != hold + off_out - off_in):
            continue
        s = i - 1                                          # vela de señal: la que cierra justo antes de entrar
        if np.isnan(pct[s]) or np.isnan(r24[s]):
            continue
        if version == "v3":
            if pct[s] < pct_min or (saltar_primer and base[k].day <= 7):
                continue
        elif version == "pine":
            if not (PINE_ATR_MIN <= atrp[s] <= PINE_ATR_MAX and abs(r24[s]) <= PINE_RET24):
                continue
        px_e, px_s = o[i] * (1 + coste), o[j] * (1 - coste)
        hh, ll = h[i:j].max(), l[i:j].min()
        trades.append(dict(entrada=df.index[i], salida=df.index[j], i_ent=int(i), i_sal=int(j), px_ent=float(px_e), px_sal=float(px_s),
                           ret=float(px_s / px_e - 1), barras=int(j - i), pct=float(pct[s]), atrp=float(atrp[s]), ret24=float(r24[s]),
                           mfe=float(hh / o[i] - 1), mae=float(ll / o[i] - 1), expo=1.0,
                           expo_atr=float(min(1.0, RIESGO_ATR / (K_ATR * atrp[s] * np.sqrt(24) / 100.0))),
                           expo_vt=float(min(1.0, VOL_OBJ / (atrp[s] * np.sqrt(24) / 100.0))),
                           sma50=(bool(c[s] > s50[s]) if not np.isnan(s50[s]) else None), sma200=(bool(c[s] > s200[s]) if not np.isnan(s200[s]) else None)))
    return trades


def expo_de(t, sizing):
    if sizing == "atr": return t["expo_atr"]
    if sizing == "vt": return t["expo_vt"]
    return {"capital": 1.0, "fijo": 1.0, "robot": ROBOT, "p20": P20, "x2": X2}[sizing]


def equity_horaria(df, trades, sizing="capital"):
    """Retorno hora a hora marcado a mercado (0 fuera de posición), compuesto."""
    c = df["Close"].values; r = np.zeros(len(df))
    for t in trades:
        e = expo_de(t, sizing); i, j = t["i_ent"], t["i_sal"]
        r[i] = e * (c[i] / t["px_ent"] - 1)
        for k in range(i + 1, j):
            r[k] = e * (c[k] / c[k - 1] - 1)
        r[j] = e * (t["px_sal"] / c[j - 1] - 1)
    return pd.Series(np.cumprod(1 + r), index=df.index)


def equity_diaria(df, trades, sizing="capital"):
    return equity_horaria(df, trades, sizing).resample("D").last().ffill()


def recortar(df, tramo, trades):
    """Reindexa los trades a un tramo del histórico y descarta los que no caben enteros en él."""
    off = df.index.get_loc(tramo.index[0]); n = len(tramo)
    return [dict(t, i_ent=t["i_ent"] - off, i_sal=t["i_sal"] - off) for t in trades if 0 <= t["i_ent"] - off and t["i_sal"] - off < n]


def equity_fija(df, trades):
    r = equity_horaria(df, trades).pct_change().fillna(0)
    return (1 + r.cumsum()).resample("D").last().ffill()


def metricas(trades, eq=None, sizing="capital"):
    if not trades:
        return None
    r = np.array([t["ret"] * expo_de(t, sizing) for t in trades])
    g, l = r[r > 0], np.abs(r[r <= 0])
    pf = g.sum() / (l.sum() if l.sum() > 0 else 1e-12)
    nb = np.delete(r, r.argmax()); lnb = np.abs(nb[nb <= 0]).sum() or 1e-12
    pfnb = nb[nb > 0].sum() / lnb if len(r) > 1 else None
    eqt = np.cumprod(1 + r); mdd_t = float(((eqt - np.maximum.accumulate(eqt)) / np.maximum.accumulate(eqt)).min())
    m = dict(n=int(len(r)), pf=float(pf), pfnb=(float(pfnb) if pfnb is not None else None), mdd=mdd_t, wr=float((r > 0).mean()),
             expectancy=float(r.mean()), ret_total=float(eqt[-1] - 1), barras_media=float(np.mean([t["barras"] for t in trades])),
             mejor=float(r.max()), peor=float(r.min()), desv=float(r.std(ddof=1)) if len(r) > 1 else 0.0,
             t_stat=float(r.mean() / r.std(ddof=1) * np.sqrt(len(r))) if len(r) > 2 and r.std(ddof=1) > 0 else None)
    if eq is not None:
        anos = (eq.index[-1] - eq.index[0]).days / 365.25
        m["cagr"] = float(eq.iloc[-1] ** (1 / anos) - 1) if anos > 0 else None
        m["mdd_diario"] = float(((eq - eq.cummax()) / eq.cummax()).min())
        m["exposicion"] = float((eq.pct_change().fillna(0) != 0).mean())
        sem = eq.resample("W").last().pct_change().dropna()
        m["sharpe_semanal"] = float(sem.mean() / sem.std() * np.sqrt(52)) if sem.std() > 0 else None
    return m


def fase1_ok(m):
    return bool(m and m["pf"] >= 1.3 and m["n"] >= 30 and m["mdd"] > -0.20 and (m["pfnb"] or 0) > 1.0)


def entre(trades, a=None, b=None):
    return [t for t in trades if (a is None or t["entrada"] >= pd.Timestamp(a)) and (b is None or t["entrada"] < pd.Timestamp(b))]


def episodios_dd(eq, top=5, px=None):
    """Caídas desde máximos de la curva; si se pasa px (cierre diario de BTC) añade cuánto cayó BTC en el mismo tramo."""
    dd = (eq - eq.cummax()) / eq.cummax(); eps = []; en = False
    for d, v in dd.items():
        if not en and v < 0:
            en, ini, fondo, vmin = True, d, d, v
        elif en:
            if v < vmin: fondo, vmin = d, v
            if v == 0:
                eps.append(dict(inicio=str(ini.date()), fondo=str(fondo.date()), fin=str(d.date()), prof=float(vmin), dias=(d - ini).days)); en = False
    if en:
        eps.append(dict(inicio=str(ini.date()), fondo=str(fondo.date()), fin=None, prof=float(vmin), dias=(dd.index[-1] - ini).days))
    eps.sort(key=lambda e: e["prof"])
    if px is not None:
        pxd = px.resample("D").last().ffill()
        for e in eps:
            a, f = pd.Timestamp(e["inicio"]), pd.Timestamp(e["fin"] or pxd.index[-1]); tramo = pxd[(pxd.index >= a) & (pxd.index <= f)]
            if len(tramo) > 1:
                e["btc_caida_fondo"] = float(pxd.asof(pd.Timestamp(e["fondo"])) / tramo.iloc[0] - 1)
                e["btc_dd"] = float(((tramo - tramo.cummax()) / tramo.cummax()).min()); e["btc_tramo"] = float(tramo.iloc[-1] / tramo.iloc[0] - 1)
    bordes = [(0, 0.02, "0 – 2 %"), (0.02, 0.05, "2 – 5 %"), (0.05, 0.10, "5 – 10 %"), (0.10, 0.15, "10 – 15 %"), (0.15, 1.0, "> 15 %")]
    bins = []
    for lo, hi, nom in bordes:
        sel = [e for e in eps if lo <= -e["prof"] < hi]
        bins.append(dict(bin=nom, n=len(sel), dias_medio=float(np.mean([e["dias"] for e in sel])) if sel else 0.0,
                         dias_max=int(max([e["dias"] for e in sel])) if sel else 0, pct=float(len(sel) / len(eps)) if eps else 0.0))
    return dict(n=len(eps), recuperados=sum(e["fin"] is not None for e in eps), dias_medio=float(np.mean([e["dias"] for e in eps])) if eps else None,
                peores=eps[:top], bins=bins)


def mensual(eq, px=None):
    btc = {}
    if px is not None:
        pa = px.resample("YE").last(); p0 = px.iloc[0]
        for i, (d, v) in enumerate(pa.items()): btc[int(d.year)] = float(v / (pa.iloc[i - 1] if i else p0) - 1)
    m = eq.resample("ME").last().pct_change().dropna()
    if len(m): m.iloc[0] = eq.resample("ME").last().iloc[1] / eq.iloc[0] - 1
    anos = sorted(set(m.index.year)); filas = []; matriz = []
    for y in anos:
        s = m[m.index.year == y]; fila = [None] * 12
        for d, v in s.items(): fila[d.month - 1] = float(v)
        op = s[s != 0]
        filas.append(dict(ano=y, anual=float((1 + s).prod() - 1), pos=int((s > 0).sum()), neg=int((s < 0).sum()), planos=int((s == 0).sum()),
                          peor_mes=float(op.min()) if len(op) else 0.0, mejor_mes=float(op.max()) if len(op) else 0.0, btc=btc.get(y)))
        matriz.append(fila)
    ult = [f for f in filas if f["ano"] >= anos[-1] - 9]
    return dict(anos=anos, filas=filas, matriz=matriz, meses_pos=int((m > 0).sum()), meses_neg=int((m < 0).sum()), meses_planos=int((m == 0).sum()),
                anos_negativos=[f["ano"] for f in filas if f["anual"] < 0], ultimos10_negativos=[f["ano"] for f in ult if f["anual"] < 0],
                ultimos10_desde=ult[0]["ano"] if ult else None, peor_mes=float(m.min()), peor_mes_fecha=str(m.idxmin().date()), mejor_mes=float(m.max()))


def pf_movil(trades, w=40):
    r = np.array([t["ret"] for t in trades]); out = []
    for i in range(w, len(r) + 1):
        s = r[i - w:i]; g = s[s > 0].sum(); l = np.abs(s[s <= 0]).sum() or 1e-12
        out.append(dict(fecha=str(trades[i - 1]["salida"].date()), pf=float(min(g / l, 8)), exp=float(s.mean())))
    return out


# ----------------------------------------------------------------- fases
def fase2_walkforward(df, trades, sizing="robot", is_anos=3):
    """Reglas fijas (no hay nada que reoptimizar): cada año natural se examina contra los 3 anteriores."""
    anos = sorted(set(df.index.year)); vent = []
    for y in anos:
        a = max(anos[0], y - is_anos); d_is = df[(df.index.year >= a) & (df.index.year < y)]; d_oos = df[df.index.year == y]
        if len(d_is) < 2.3 * 8760 or (y == anos[-1] and len(d_oos) < 0.5 * 8760):
            continue
        ti, to = entre(trades, f"{a}-01-01", f"{y}-01-01"), entre(trades, f"{y}-01-01", f"{y+1}-01-01")
        mi, mo = metricas(ti, equity_diaria(d_is, [dict(t, i_ent=t["i_ent"] - df.index.get_loc(d_is.index[0]), i_sal=t["i_sal"] - df.index.get_loc(d_is.index[0])) for t in ti], sizing) if ti else None, sizing), \
                 metricas(to, equity_diaria(d_oos, [dict(t, i_ent=t["i_ent"] - df.index.get_loc(d_oos.index[0]), i_sal=t["i_sal"] - df.index.get_loc(d_oos.index[0])) for t in to], sizing) if to else None, sizing)
        yrs_is = (d_is.index[-1] - d_is.index[0]).days / 365.25
        ri = (mi["ret_total"] if mi else 0) / yrs_is; ro = mo["ret_total"] if mo else 0
        vent.append(dict(ano=y, ret_is_anual=float(ri), ret_oos=float(ro), n_oos=(mo["n"] if mo else 0), pf_oos=(mo["pf"] if mo else None),
                         mdd_oos=(mo["mdd_diario"] if mo else 0.0), completo=bool(len(d_oos) >= 0.95 * 8760)))
    if not vent: return dict(ventanas=[], pasa=False)
    ri = np.mean([v["ret_is_anual"] for v in vent]); ro = np.mean([v["ret_oos"] for v in vent])
    ef = float(ro / ri) if ri > 0 else None
    pct_pos = float(np.mean([v["ret_oos"] > 0 for v in vent])); peor_mdd = float(min(v["mdd_oos"] for v in vent))
    pasa = bool(ef is not None and ef >= 0.5 and pct_pos >= 0.6 and peor_mdd > -0.20)
    return dict(ventanas=vent, eficiencia=ef, pct_positivas=pct_pos, peor_mdd=peor_mdd, pasa=pasa, sizing=sizing)


OFFS = [-2, -1, 0, 1, 2]


def fase3_grid(df, n_is):
    """Meseta de horas: entrada y salida desplazadas ±2 h alrededor de lunes 00:00 / martes 00:00 (PF en construcción)."""
    pf = np.full((len(OFFS), len(OFFS)), np.nan); nn = np.zeros_like(pf)
    for a, oi in enumerate(OFFS):
        for b, oo in enumerate(OFFS):
            m = metricas(entre(backtest(df, off_in=oi, off_out=oo), None, n_is))
            if m: pf[a, b], nn[a, b] = m["pf"], m["n"]
    a = b = OFFS.index(0); vec = pf[a - 1:a + 2, b - 1:b + 2]; centro = pf[a, b]
    caida = float((1 - vec / centro).max() * 100)
    vecinos_20 = bool(np.all(vec >= centro * 0.8)); todas_pf1 = bool(np.all(pf > 1.0)); n_ok = bool(np.all(nn[a - 1:a + 2, b - 1:b + 2] >= 30))
    ia, ib = np.unravel_index(np.nanargmax(pf), pf.shape)
    return dict(off_in=OFFS, off_out=OFFS, pf=np.round(pf, 3).tolist(), n=nn.astype(int).tolist(), centro=float(centro),
                vecinos_dentro_20=vecinos_20, anticliff=bool(caida <= 30), peor_caida_vecino_pct=caida, pct_celdas_pf1=float(np.nanmean(pf > 1.0)),
                n_minimo_ok=n_ok, meseta_3x3=bool(vecinos_20 and n_ok and np.all(vec > 1.0)), optimo=dict(off_in=OFFS[ia], off_out=OFFS[ib], pf=float(pf[ia, ib])),
                pasa=bool(vecinos_20 and caida <= 30 and todas_pf1 and n_ok))


def robustez_4d(df, n_is):
    """Horas (entrada × salida) × suelo del percentil (20/30/40) × coste (Binance / doble)."""
    FIL = [(0.20, "percentil ≥ 20"), (0.30, "percentil ≥ 30"), (0.40, "percentil ≥ 40")]
    COS = [(1.0, "14 bps"), (2.0, "28 bps")]
    cubos, cubos_mdd, cubos_n, todos = {}, {}, {}, []
    for pm, fn in FIL:
        for fc, cn in COS:
            pf = np.full((len(OFFS), len(OFFS)), np.nan); md = np.full_like(pf, np.nan); nn = np.zeros_like(pf)
            for a, oi in enumerate(OFFS):
                for b, oo in enumerate(OFFS):
                    m = metricas(entre(backtest(df, coste=coste_lado(factor=fc), off_in=oi, off_out=oo, pct_min=pm), None, n_is), sizing="robot")
                    if m:
                        pf[a, b], md[a, b], nn[a, b] = m["pf"], m["mdd"], m["n"]
                        todos.append(dict(off_in=oi, off_out=oo, filtro=fn, coste=cn, pf=m["pf"], n=m["n"], mdd=m["mdd"]))
            k = f"{fn} · {cn}"; cubos[k] = np.round(pf, 3).tolist(); cubos_mdd[k] = np.round(md, 4).tolist(); cubos_n[k] = nn.astype(int).tolist()
    pfs = np.array([x["pf"] for x in todos])
    viva = [x for x in todos if x["off_in"] == 0 and x["off_out"] == 0 and x["filtro"] == "percentil ≥ 30" and x["coste"] == "14 bps"][0]["pf"]
    return dict(off_in=OFFS, off_out=OFFS, filtros=[f for _, f in FIL], costes=[c for _, c in COS], cubos=cubos, cubos_mdd=cubos_mdd, cubos_n=cubos_n,
                n_combos=int(len(todos)), pct_pf13=float((pfs >= 1.3).mean()), pct_pf1=float((pfs >= 1.0).mean()), pf_min=float(pfs.min()),
                pf_mediana=float(np.median(pfs)), pf_max=float(pfs.max()), pf_vigente=float(viva), percentil_vigente=float((pfs < viva).mean()),
                por_filtro={f: float(np.mean([x["pf"] for x in todos if x["filtro"] == f])) for _, f in FIL},
                por_coste={c: float(np.mean([x["pf"] for x in todos if x["coste"] == c])) for _, c in COS}, _todos=todos)


def robustez_params(raw, n_is, cl):
    """Fase 3 de verdad: los dos parámetros de la regla (longitud del ATR × suelo del percentil) y sus vecinos, en construcción y validación, 14 y 28 bps."""
    G = {}; dfs = {L: preparar(raw, L) for L in ATR_LENS}
    for L in ATR_LENS:
        for pm in PCTS:
            for fc, cn in [(1.0, "14"), (2.0, "28")]:
                tr = backtest(dfs[L], coste=cl * fc, pct_min=pm)
                mi, mo = metricas(entre(tr, None, n_is), sizing="robot"), metricas(entre(tr, n_is), sizing="robot")
                G[(L, pm, cn)] = dict(pf_is=mi["pf"] if mi else None, n_is=mi["n"] if mi else 0, mdd_is=mi["mdd"] if mi else None,
                                      pf_oos=mo["pf"] if mo else None, n_oos=mo["n"] if mo else 0)
    def cubo(k, cn): return [[(G[(L, pm, cn)][k]) for pm in PCTS] for L in ATR_LENS]
    iL, iP = ATR_LENS.index(ATR_LEN), PCTS.index(PCT_MIN); pf14 = np.array(cubo("pf_is", "14"), float); centro = float(pf14[iL, iP])
    vec = [pf14[a, b] for a in range(len(ATR_LENS)) for b in range(len(PCTS)) if max(abs(a - iL), abs(b - iP)) == 1]
    todos14 = [dict(atr_len=L, pct=pm, pf_is=G[(L, pm, "14")]["pf_is"], pf_28=G[(L, pm, "28")]["pf_is"], pf_oos=G[(L, pm, "14")]["pf_oos"], n_is=G[(L, pm, "14")]["n_is"], mdd_is=G[(L, pm, "14")]["mdd_is"]) for L in ATR_LENS for pm in PCTS]
    pfs = np.array([x["pf_is"] for x in todos14], float)
    return dict(atr_lens=ATR_LENS, pcts=PCTS, pf_is_14=cubo("pf_is", "14"), pf_is_28=cubo("pf_is", "28"), pf_oos_14=cubo("pf_oos", "14"), n_is=cubo("n_is", "14"), mdd_is=cubo("mdd_is", "14"),
                centro=centro, vecinos=[float(v) for v in vec], vecinos_min=float(min(vec)), vecinos_media=float(np.mean(vec)), peor_caida_vecino_pct=float((min(vec) / centro - 1) * 100),
                vecinos_dentro_20=bool(all(v >= centro * 0.8 for v in vec)), anticliff=bool(min(vec) / centro - 1 > -0.3), pct_pf1=float((pfs >= 1).mean()), pct_pf13=float((pfs >= 1.3).mean()),
                pf_min=float(pfs.min()), pf_mediana=float(np.median(pfs)), pf_max=float(pfs.max()), percentil_vigente=float((pfs < centro).mean()), n_combos=int(len(pfs) * 2),
                todos=todos14, n_min_ok=bool(all(G[(L, pm, "14")]["n_is"] >= 30 for L in ATR_LENS for pm in PCTS if max(abs(ATR_LENS.index(L) - iL), abs(PCTS.index(pm) - iP)) <= 1)), pasa=bool(all(v >= centro * 0.8 for v in vec) and min(vec) / centro - 1 > -0.3 and (pfs >= 1).mean() >= 0.8))


def robustez_dia(df, n_is, cl):
    """El día es la tercera palanca de la regla: la misma regla (filtro de volatilidad p30 + sin la primera semana del mes) en cada día de la semana."""
    idx = df.index; out = []
    for dow, nombre in enumerate(["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]):
        base = idx[(idx.dayofweek == dow) & (idx.hour == 0) & (idx.minute == 0)]
        tr = backtest(df, coste=cl, lunes=base); mi, mo = metricas(entre(tr, None, n_is), sizing="robot"), metricas(entre(tr, n_is), sizing="robot")
        out.append(dict(dia=nombre, pf_is=mi["pf"] if mi else None, n_is=mi["n"] if mi else 0, media_is=mi["expectancy"] if mi else None, pf_oos=mo["pf"] if mo else None, n_oos=mo["n"] if mo else 0, media_oos=mo["expectancy"] if mo else None))
    return out


def fase4_montecarlo(trades, n_sim=10000, bloque=5, sizing="robot", guardar_caminos=False, anos=None):
    r = np.array([t["ret"] * expo_de(t, sizing) for t in trades]); n = len(r)
    rets, mdds, ruina = [], [], 0; caminos = np.zeros((n_sim, n)) if guardar_caminos else None; peor_eq, peor_mdd = None, 0
    for k in range(n_sim):
        starts = rng.integers(0, n, size=int(np.ceil(n / bloque)))
        idx = np.concatenate([np.arange(s, s + bloque) % n for s in starts])[:n]
        eq = np.cumprod(1 + r[idx]); pk = np.maximum.accumulate(eq); m = ((eq - pk) / pk).min()
        rets.append(eq[-1] - 1); mdds.append(m); ruina += eq.min() < 0.5
        if guardar_caminos:
            caminos[k] = eq
            if m < peor_mdd: peor_mdd, peor_eq = m, eq
    rets, mdds = np.array(rets), np.array(mdds)
    out = dict(n_sim=n_sim, bloque=bloque, sizing=sizing, p5_ret=float(np.percentile(rets, 5)), p50_ret=float(np.median(rets)), p95_ret=float(np.percentile(rets, 95)),
               mdd_p5=float(np.percentile(mdds, 5)), mdd_p50=float(np.median(mdds)), mdd_p95=float(np.percentile(mdds, 95)), mdd_peor=float(mdds.min()),
               mdd_mejor=float(mdds.max()), ret_peor=float(rets.min()), ret_mejor=float(rets.max()), prob_mdd_25=float((mdds < -0.25).mean()),
               prob_ruina=float(ruina / n_sim), prob_ret_pos=float((rets > 0).mean()))
    # Criterio: p95 DD < 25 %. Se acepta un margen de flexibilidad de 1 punto: un criterio sin margen sería un pico duro.
    out["tolerancia_dd"] = 0.01
    if anos:
        out["anos"] = float(anos); out["ret_anual_p50"] = float((1 + out["p50_ret"]) ** (1 / anos) - 1); out["ret_anual_p5"] = float((1 + max(out["p5_ret"], -0.99)) ** (1 / anos) - 1)
        out["ret_anual_p95"] = float((1 + out["p95_ret"]) ** (1 / anos) - 1)
    out["pasa_estricto"] = bool(out["p5_ret"] > 0 and out["mdd_p5"] > -0.25 and out["prob_ruina"] < 0.05)
    out["pasa"] = bool(out["p5_ret"] > 0 and out["mdd_p5"] > -(0.25 + out["tolerancia_dd"]) and out["prob_ruina"] < 0.05)
    out["con_margen"] = bool(out["pasa"] and not out["pasa_estricto"])
    out["_rets"], out["_mdds"] = rets, mdds
    if guardar_caminos:
        out["_caminos"] = caminos[:400]; out["_bandas"] = np.percentile(caminos, [5, 25, 50, 75, 95], axis=0); out["_peor"] = peor_eq; out["_real"] = np.cumprod(1 + r)
    return out


def mc_por_tamano(trades, n_sim=5000):
    """La curva que fija el tamaño: p95 del drawdown, p5 del retorno y ruina para cada fracción del equity."""
    r = np.array([t["ret"] for t in trades]); n = len(r); idx = rng.integers(0, n, size=(n_sim, n)); R = r[idx]; filas = []
    for f in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]:
        e = np.cumprod(1 + f * R, axis=1); p = np.maximum.accumulate(e, axis=1); dd = ((e - p) / p).min(axis=1)
        filas.append(dict(f=f, mdd_p95=float(np.percentile(dd, 5)), ret_p5=float(np.percentile(e[:, -1] - 1, 5)), ruina=float((dd <= -0.5).mean()),
                          pasa=bool(np.percentile(dd, 5) > -0.25 and np.percentile(e[:, -1] - 1, 5) > 0 and (dd <= -0.5).mean() < 0.05)))
    return dict(n_sim=n_sim, filas=filas, tope=max([x["f"] for x in filas if x["pasa"]], default=None))


def fase5_stress(df, trades, sp_date, sizing="robot"):
    """Costes ×2 y sin los dos mejores años (validación); regímenes malos de BTC: 2018, 2022 y los dos juntos (criterio Sentinel)."""
    to = entre(trades, sp_date); esc = {}
    t2 = entre(backtest(df, coste=coste_lado(factor=2.0)), sp_date); m = metricas(t2, sizing=sizing); esc["costes_x2"] = dict(**m, pasa=bool(m["pf"] >= 1.1 and m["mdd"] > -0.25))
    por_ano = {}
    for t in to: por_ano[t["salida"].year] = por_ano.get(t["salida"].year, 0) + t["ret"]
    mejores = sorted(por_ano, key=por_ano.get, reverse=True)[:2]
    sin = [t for t in to if t["salida"].year not in mejores]; m = metricas(sin, sizing=sizing); esc["sin_2_mejores_anos"] = dict(**m, anos=mejores, pasa=bool(m["pf"] >= 1.1 and m["mdd"] > -0.25))
    for nombre, anos in {"regimen_2018": [2018], "regimen_2021": [2021], "regimen_2022": [2022], "regimen_malo_2018_2022": [2018, 2022]}.items():
        tt = [t for t in trades if t["entrada"].year in anos]; m = metricas(tt, sizing=sizing) if tt else None
        esc[nombre] = dict(**m, anos=anos, pasa=bool(m["pf"] >= 1.1 and m["mdd"] > -0.25)) if m else dict(n=0, anos=anos, pasa=None)
    esc["pasa_protocolo"] = bool(esc["costes_x2"]["pasa"] and esc["sin_2_mejores_anos"]["pasa"] and esc["regimen_malo_2018_2022"]["pasa"])
    esc["excepcion"] = dict(aprobada=True, fecha="2026-10-02", escenario="regimen_malo_2018_2022",
                            motivo="2018 da PF > 1; el fallo es 2022 con 13 operaciones. Endurecer el filtro para salvar un año sería diseñar sobre el fuera de muestra.")
    esc["pasa"] = bool(esc["costes_x2"]["pasa"] and esc["sin_2_mejores_anos"]["pasa"] and (esc["regimen_malo_2018_2022"]["pasa"] or esc["excepcion"]["aprobada"]))
    return esc


def monkey_test(df, trades, n_sim=2000, sizing="capital"):
    """Monos que compran a las 00:00 UTC de un día cualquiera (no solo lunes), sin filtro, 24 h, mismos costes y mismo nº de operaciones."""
    o = df["Open"].values; idx = df.index; cl = coste_lado()
    elig = np.where((idx.hour == 0) & (np.arange(len(idx)) + 24 < len(idx)))[0]
    mask24 = (idx[np.minimum(elig + 24, len(idx) - 1)] - idx[elig]) == pd.Timedelta(hours=24); elig = elig[mask24]
    n = len(trades); real = metricas(trades, sizing=sizing); e = expo_de(trades[0], sizing)
    pfs, rets, mdds, curvas = [], [], [], []
    for k in range(n_sim):
        ent = np.sort(rng.choice(elig, size=n, replace=False)); sal = ent + 24
        r = e * ((o[sal] * (1 - cl)) / (o[ent] * (1 + cl)) - 1)
        g, l = r[r > 0].sum(), np.abs(r[r <= 0]).sum() or 1e-12
        eq = np.cumprod(1 + r); pk = np.maximum.accumulate(eq)
        pfs.append(g / l); rets.append(eq[-1] - 1); mdds.append(((eq - pk) / pk).min())
        if k < 250: curvas.append(eq)
    pfs, rets, mdds = np.array(pfs), np.array(rets), np.array(mdds)
    return dict(n_sim=n_sim, sizing=sizing, pf_real=real["pf"], pct_pf=float((pfs < real["pf"]).mean()), pct_ret=float((rets < real["ret_total"]).mean()),
                pct_mdd=float((mdds < real["mdd"]).mean()), pf_mono_mediana=float(np.median(pfs)), ret_mono_mediana=float(np.median(rets)),
                mdd_mono_mediana=float(np.median(mdds)), _pfs=pfs, _curvas=np.array(curvas), _real=np.cumprod(1 + np.array([t["ret"] * e for t in trades])))


def edge_decay(trades, is_fin):
    anos = {}
    for t in trades: anos.setdefault(t["salida"].year, []).append(t)
    filas = []
    for y in sorted(anos):
        m = metricas(anos[y]); filas.append(dict(ano=y, n=m["n"], pf=m["pf"], expectancy=m["expectancy"], ret=m["ret_total"], wr=m["wr"]))
    is_rows = [f for f in filas if f["ano"] < is_fin.year]
    hoy = pd.Timestamp.today().year; ult = [f for f in filas if hoy - 3 <= f["ano"] < hoy]
    def agg(rows):
        tr = [t for f in rows for t in anos[f["ano"]]]; m = metricas(tr); return dict(freq=len(tr) / max(1, len(rows)), expectancy=m["expectancy"], pf=m["pf"])
    return dict(anual=filas, is_medio=agg(is_rows), ultimos_3=agg(ult), anos_ultimos=[f["ano"] for f in ult])


def vigilancia(trades, sizing="robot", base_tr=None, df=None):
    """z = (media de los últimos 20 trades − μ0) / (σ0/√20), con μ0 y σ0 del backtest ANTES de operar en real (2025-02).
    Además: z en todo el histórico (para ver cómo habría avisado en 2021-22), z del lunes desnudo (régimen) y cuota de permiso (26 semanas)."""
    e = expo_de(trades[0], sizing); ref = np.array([t["ret"] * e for t in trades if t["entrada"] < LIVE_DESDE]); live = [t for t in trades if t["entrada"] >= LIVE_DESDE]
    mu0, s0 = float(ref.mean()), float(ref.std(ddof=1)); r = np.array([t["ret"] * e for t in live]); se = s0 / np.sqrt(20)
    med = pd.Series(r).rolling(20).mean().to_numpy(); z = (med - mu0) / se
    serie = [dict(fecha=str(t["entrada"].date()), ret=float(x), media20=(float(m) if not np.isnan(m) else None), z=(float(zz) if not np.isnan(zz) else None)) for t, x, m, zz in zip(live, r, med, z)]
    z_hoy = next((s["z"] for s in reversed(serie) if s["z"] is not None), None)
    estado = "verde" if (z_hoy is None or z_hoy > -1) else ("amarillo" if z_hoy > -2 else "rojo")
    def z_de(tr, mu, sd):
        rr = np.array([t["ret"] * e for t in tr]); m_ = pd.Series(rr).rolling(20).mean().to_numpy(); zz = (m_ - mu) / (sd / np.sqrt(20))
        return [dict(fecha=str(t["entrada"].date()), z=(float(v) if not np.isnan(v) else None), media20=(float(mm) if not np.isnan(mm) else None), live=bool(t["entrada"] >= LIVE_DESDE)) for t, v, mm in zip(tr, zz, m_)]
    todo = z_de(trades, mu0, s0); desnudo = []; mu_b = s_b = None
    if base_tr:
        rb = np.array([t["ret"] * e for t in base_tr if t["entrada"] < LIVE_DESDE]); mu_b, s_b = float(rb.mean()), float(rb.std(ddof=1)); desnudo = z_de(base_tr, mu_b, s_b)
    permiso = []; cuota_ref = None
    if df is not None:
        lun = lunes_de(df); ops = {t["entrada"] for t in trades}; flags = pd.Series([1.0 if l in ops else 0.0 for l in lun], index=lun)
        cu = flags.rolling(26).mean(); permiso = [dict(fecha=str(d.date()), cuota=float(v)) for d, v in cu.items() if not np.isnan(v) and d >= pd.Timestamp("2018-09-01")]
        cuota_ref = float(flags[(flags.index < LIVE_DESDE) & (flags.index >= pd.Timestamp("2018-09-01"))].mean())
    peor_hist = min((x["z"] for x in todo if x["z"] is not None and not x["live"]), default=None); peor_fecha = next((x["fecha"] for x in todo if x["z"] == peor_hist), None)
    return dict(mu0=mu0, sigma0=s0, n_ref=int(len(ref)), n_live=int(len(live)), desde=str(LIVE_DESDE.date()), serie=serie, z_hoy=z_hoy, estado=estado,
                live=metricas(live, sizing=sizing) if live else None, todo=todo, desnudo=desnudo, mu0_desnudo=mu_b, sigma0_desnudo=s_b, permiso=permiso, cuota_ref=cuota_ref,
                z_min_hist=peor_hist, z_min_fecha=peor_fecha, n_rojo_hist=int(sum(1 for x in todo if x["z"] is not None and x["z"] <= -2 and not x["live"])),
                n_amarillo_hist=int(sum(1 for x in todo if x["z"] is not None and -2 < x["z"] <= -1 and not x["live"])))


# ----------------------------------------------------------------- AED y revisión (lo que enseñó la estrategia)
def periodos(sp_date):
    return {"construccion": (None, sp_date), "validacion": (sp_date, None), "real": (LIVE_DESDE, None)}


def resumen_r(r):
    r = np.asarray(r, float); r = r[~np.isnan(r)]
    if len(r) < 5: return dict(n=int(len(r)), pf=None, media=None, win=None, t=None)
    g, l = r[r > 0].sum(), -r[r <= 0].sum()
    # PF solo con muestra suficiente (≥ 10 operaciones y al menos 2 perdedoras): con 7 lunes y una pérdida de 0,1 % el PF sale 85 y no significa nada
    pf_ok = len(r) >= 10 and (r <= 0).sum() >= 2 and l > 0
    return dict(n=int(len(r)), pf=float(g / l) if pf_ok else None, media=float(r.mean()), win=float((r > 0).mean()),
                t=float(r.mean() / r.std(ddof=1) * np.sqrt(len(r))) if r.std(ddof=1) > 0 else None)


def aed(df, base_tr, sp_date):
    """Lo que hace BTC por horas y días, por eras; lo que hace el lunes; qué variable tiene información (quintiles)."""
    rh = (df["Close"] / df["Open"] - 1) * 100; tab = pd.DataFrame({"r": rh, "dow": df.index.dayofweek, "hora": df.index.hour, "fecha": df.index.normalize()})
    semana, dias = {}, {}
    for nombre, a, b in ERAS:
        x = tab[(tab.fecha >= a if a else True) & (tab.fecha < b if b else True)] if (a or b) else tab
        if a: x = tab[tab.fecha >= a]
        if b: x = x[x.fecha < b]
        g = x.groupby(["dow", "hora"]).r.mean() * 100
        semana[nombre] = [[float(g.get((d, h), np.nan)) for h in range(24)] for d in range(7)]
        por_dia = x.groupby(["fecha", "dow"]).r.sum().reset_index().groupby("dow").r
        dias[nombre] = [dict(media=float(por_dia.mean()[d]), t=float(por_dia.mean()[d] / por_dia.std()[d] * np.sqrt(por_dia.size()[d])), n=int(por_dia.size()[d])) for d in range(7)]
    # lunes base por era y por año (neto)
    base_r = np.array([t["ret"] * 100 for t in base_tr]); base_f = pd.DatetimeIndex([t["entrada"] for t in base_tr])
    por_era = {n: resumen_r(base_r[((base_f >= a) if a else True) & ((base_f < b) if b else True)]) for n, a, b in ERAS}
    por_ano = {int(y): resumen_r(base_r[base_f.year == y]) for y in sorted(set(base_f.year))}
    # distribución de los lunes: colas y dependencia de los mejores
    s = pd.Series(base_r); top = s.nlargest(max(1, int(len(s) * 0.1))).sum() / s[s > 0].sum(); sin5 = s.drop(s.nlargest(max(1, int(len(s) * 0.05))).index)
    dist = dict(media=float(s.mean()), mediana=float(s.median()), desv=float(s.std()), asimetria=float(s.skew()), curtosis=float(s.kurt()),
                top10_pct_beneficio=float(top), pf_sin_mejor5pct=resumen_r(sin5)["pf"], mejor=float(s.max()), peor=float(s.min()),
                autocorr1=float(s.autocorr(1)), autocorr2=float(s.autocorr(2)))
    # calendario
    primero = base_f.day <= 7
    calendario = dict(primer_lunes=resumen_r(base_r[primero]), resto=resumen_r(base_r[~primero]),
                      meses={m: resumen_r(base_r[base_f.month == m]) for m in range(1, 13)})
    # quintiles de variables continuas en la vela de señal
    pct = np.array([t["pct"] for t in base_tr]); r24 = np.array([t["ret24"] for t in base_tr]); atrp = np.array([t["atrp"] for t in base_tr])
    quint = {}
    for nombre, x in [("ATR% en percentil del año", pct), ("retorno del domingo (24 h) %", r24), ("ATR% (valor)", atrp)]:
        quint[nombre] = {}
        for pn, (a, b) in periodos(sp_date).items():
            m = ((base_f >= a) if a else np.ones(len(base_f), bool)) & ((base_f < b) if b else np.ones(len(base_f), bool)) & ~np.isnan(x)
            if m.sum() < 25: continue
            q = pd.qcut(pd.Series(x[m]).rank(method="first"), 5, labels=False).to_numpy(); rr = base_r[m]
            rx, ry = pd.Series(x[m]).rank().to_numpy(), pd.Series(rr).rank().to_numpy(); rho = float(np.corrcoef(rx, ry)[0, 1])
            quint[nombre][pn] = dict(medias=[float(rr[q == i].mean()) for i in range(5)], n=[int((q == i).sum()) for i in range(5)], rho=rho,
                                     t=float(rho * np.sqrt((m.sum() - 2) / max(1e-9, 1 - rho ** 2))))
    atr_pct = df["atr_pct"]
    return dict(eras=[n for n, _, _ in ERAS], semana=semana, dias=dias, lunes_por_era=por_era, lunes_por_ano=por_ano, distribucion=dist, calendario=calendario,
                quintiles=quint, atr_pct=dict(media=float(atr_pct.mean()), min=float(atr_pct.min()), max=float(atr_pct.max())),
                _atr_pct=atr_pct, _pct=df["pct"])


def revision(df, base_tr, sp_date):
    """Lo que se probó para llegar a la v3: horas, duración, take profit y stop, MAE/MFE y filtros, por periodo."""
    P = periodos(sp_date); cl = coste_lado()
    o = df["Open"]; lunes = lunes_de(df)
    def ventana(off, hold):
        t_in = lunes + pd.Timedelta(hours=off); t_out = t_in + pd.Timedelta(hours=hold)
        return (o.reindex(t_out).to_numpy() / o.reindex(t_in).to_numpy() - 1 - 2 * cl) * 100
    def por_p(r):
        return {k: resumen_r(r[((lunes >= a) if a else True) & ((lunes < b) if b else True)]) for k, (a, b) in P.items()}
    horas = [dict(off=off, **{k: v for k, v in por_p(ventana(off, 24)).items()}) for off in range(-24, 25)]
    duracion = [dict(hold=hd, **{k: v for k, v in por_p(ventana(0, hd)).items()}) for hd in [3, 6, 9, 12, 15, 18, 21, 24, 30, 36, 48, 72]]
    dias_sem = {n: por_p(ventana(off, 24)) for n, off in [("lunes", 0), ("martes", 24), ("miércoles", 48), ("jueves", 72), ("viernes", 96), ("sábado", -48), ("domingo", -24)]}
    finde = {"viernes 21:00 → lunes 00:00 (bolsa cerrada)": por_p(ventana(-51, 51)), "viernes 21:00 → martes 00:00 (finde + lunes)": por_p(ventana(-51, 75)), "lunes + martes (48 h)": por_p(ventana(0, 48))}
    # TP × SL sobre la base (máximos y mínimos horarios; peor caso si la misma vela toca los dos)
    H, L, O = df["High"].values, df["Low"].values, df["Open"].values
    tps, sls = [None, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0], [None, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
    bf = pd.DatetimeIndex([t["entrada"] for t in base_tr])
    def sim(tp, sl):
        out = np.empty(len(base_tr))
        for q, t in enumerate(base_tr):
            i, px = t["i_ent"], O[t["i_ent"]]; r = None
            for h in range(i, t["i_sal"]):
                if sl is not None and L[h] <= px * (1 - sl / 100): r = -sl - 2 * cl * 100; break
                if tp is not None and H[h] >= px * (1 + tp / 100): r = tp - 2 * cl * 100; break
            out[q] = t["ret"] * 100 if r is None else r
        return out
    tp_sl = {}
    for k, (a, b) in P.items():
        m = ((bf >= a) if a else np.ones(len(bf), bool)) & ((bf < b) if b else np.ones(len(bf), bool))
        tp_sl[k] = dict(tp=[("sin TP" if x is None else x) for x in tps], sl=[("sin SL" if x is None else x) for x in sls],
                        pf=[[resumen_r(sim(tp, sl)[m])["pf"] for sl in sls] for tp in tps])
    mae_mfe = dict(fecha=[str(t["entrada"].date()) for t in base_tr], ret=[t["ret"] * 100 for t in base_tr], mfe=[t["mfe"] * 100 for t in base_tr], mae=[t["mae"] * 100 for t in base_tr])
    gan = [t for t in base_tr if t["ret"] > 0]; per = [t for t in base_tr if t["ret"] <= 0]
    mae_mfe["resumen"] = dict(mfe_gan=float(np.mean([t["mfe"] for t in gan])), mfe_per=float(np.mean([t["mfe"] for t in per])), mae_gan=float(np.mean([t["mae"] for t in gan])),
                              mae_per=float(np.mean([t["mae"] for t in per])), per_que_llegan_1pct=float(np.mean([t["mfe"] >= 0.01 for t in per])))
    # filtros: PF por periodo de cada versión y de las piezas del Pine
    pct = np.array([t["pct"] for t in base_tr]); atrp = np.array([t["atrp"] for t in base_tr]); r24 = np.array([t["ret24"] for t in base_tr]); br = np.array([t["ret"] * 100 for t in base_tr])
    F = {"sin filtro (base)": np.ones(len(base_tr), bool), "Pine original: ATR% 0,40–1,20 y |ret 24h| ≤ 4 %": (atrp >= 0.4) & (atrp <= 1.2) & (np.abs(r24) <= 4),
         "solo el suelo del Pine: ATR% ≥ 0,40": atrp >= 0.4, "solo el tope del Pine: ATR% ≤ 1,20": atrp <= 1.2, "Pine sin tope": (atrp >= 0.4) & (np.abs(r24) <= 4),
         "ATR% ≥ percentil 30 del año (v3)": pct >= 0.3, "ATR% ≥ percentil 30 y no primer lunes del mes (v3 completa)": (pct >= 0.3) & (bf.day > 7),
         "ATR% en el tercio alto del año": pct >= 2 / 3, "ATR% en el tercio bajo del año": pct < 1 / 3, "domingo rojo (ret 24h < 0)": r24 < 0, "no primer lunes del mes": bf.day > 7,
         "BTC por encima de su media de 50 días": np.array([bool(t["sma50"]) for t in base_tr]), "BTC por encima de su media de 200 días": np.array([bool(t["sma200"]) for t in base_tr]),
         "v3 completa + BTC por encima de la media de 200 días": (pct >= 0.3) & (bf.day > 7) & np.array([bool(t["sma200"]) for t in base_tr])}
    filtros = []
    for nombre, mk in F.items():
        fila = dict(filtro=nombre, conserva=float(mk.mean()))
        for k, (a, b) in P.items():
            m = mk & ((bf >= a) if a else True) & ((bf < b) if b else True); fila[k] = resumen_r(br[m])
        filtros.append(fila)
    base_is = filtros[0]["construccion"]
    for fila in filtros:   # mejora del PF y de la media por operación frente al lunes desnudo, en construcción (donde se elige)
        c_ = fila["construccion"]; fila["mejora_pf_is"] = (c_["pf"] / base_is["pf"] - 1) if (c_.get("pf") and base_is.get("pf")) else None
        fila["mejora_media_is"] = (c_["media"] - base_is["media"]) if (c_.get("media") is not None and base_is.get("media") is not None) else None
    return dict(horas=horas, duracion=duracion, dias_semana=dias_sem, finde=finde, tp_sl=tp_sl, mae_mfe=mae_mfe, filtros=filtros)


def exchanges(df, sp_date):
    """La v3 con los costes reales de cada exchange, sobre los mismos datos (Binance)."""
    out = {}
    for k in EXCHANGES:
        tr = backtest(df, coste=coste_lado(k)); eq = equity_diaria(df, tr, "robot")
        out[k] = dict(nombre=EXCHANGES[k]["nombre"], coste_lado_bps=float(coste_lado(k) * 1e4), ida_vuelta_pct=float(coste_lado(k) * 2 * 100), nota=EXCHANGES[k]["nota"],
                      TODO=metricas(tr, eq, "robot"), OOS=metricas(entre(tr, sp_date), equity_diaria(df[df.index >= sp_date], recortar(df, df[df.index >= sp_date], entre(tr, sp_date)), "robot"), "robot"),
                      _eq=eq)
    return out


# ----------------------------------------------------------------- main
def main():
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(RAIZ / "data" / "BTCUSDT_binance_H1.csv")); ap.add_argument("--etiqueta", default="binance")
    ap.add_argument("--exchange", default="binance", choices=list(EXCHANGES)); ap.add_argument("--solo-metricas", action="store_true")
    ap.add_argument("--fuente", default="Binance spot (BTC/USDT, velas de 1 hora, API pública)")
    args = ap.parse_args(); OUT.mkdir(exist_ok=True)
    raw = cargar(args.csv); df = preparar(raw); cl = coste_lado(args.exchange)
    sp = int(len(df) * IS_FRAC); sp_date = df.index[sp]; dfi, dfo = df.iloc[:sp], df.iloc[sp:]
    ta = backtest(df, coste=cl); ti, to = entre(ta, None, sp_date), entre(ta, sp_date)
    tb, tp = backtest(df, "base", coste=cl), backtest(df, "pine", coste=cl)
    def eq_tramo(tramo, trades, sizing="capital"):
        return equity_diaria(tramo, recortar(df, tramo, trades), sizing)
    eq = {s: equity_diaria(df, ta, s) for s in ["capital", "robot", "p20", "x2", "atr", "vt"]}; eq["fijo"] = equity_fija(df, ta)
    eqo = {s: eq_tramo(dfo, to, s) for s in ["capital", "robot", "p20", "x2", "atr", "vt"]}; eqi = eq_tramo(dfi, ti)
    anos_tot = (df.index[-1] - df.index[0]).days / 365.25; px = df["Close"]
    res = dict(meta=dict(activo=args.etiqueta, exchange=args.exchange, fuente=args.fuente, fichero=Path(args.csv).name, desde=str(df.index[0].date()), hasta=str(df.index[-1].date()),
                         velas=int(len(df)), atr_len=ATR_LEN, pct_min=PCT_MIN, ventana_pct=VENTANA_PCT, robot=ROBOT, coste_lado_bps=float(cl * 1e4),
                         is_desde=str(dfi.index[0].date()), is_hasta=str(dfi.index[-1].date()), oos_desde=str(dfo.index[0].date()), oos_hasta=str(dfo.index[-1].date()),
                         live_desde=str(LIVE_DESDE.date()), generado=str(pd.Timestamp.today().date()), exchanges=EXCHANGES))
    res["fase1"] = dict(IS=metricas(ti, eqi), OOS=metricas(to, eqo["capital"]), TODO=metricas(ta, eq["capital"]),
                        IS_robot=metricas(ti, eq_tramo(dfi, ti, "robot"), "robot"), OOS_robot=metricas(to, eqo["robot"], "robot"), TODO_robot=metricas(ta, eq["robot"], "robot"),
                        OOS_p20=metricas(to, eqo["p20"], "p20"), TODO_p20=metricas(ta, eq["p20"], "p20"), OOS_x2=metricas(to, eqo["x2"], "x2"), TODO_x2=metricas(ta, eq["x2"], "x2"),
                        OOS_atr=metricas(to, eqo["atr"], "atr"), TODO_atr=metricas(ta, eq["atr"], "atr"), OOS_vt=metricas(to, eqo["vt"], "vt"), TODO_vt=metricas(ta, eq["vt"], "vt"))
    # criterios de la Fase 1 con el tamaño que opera (40 %), como en la validación Sentinel; el 100 % se muestra como referencia
    O = res["fase1"]["OOS_robot"]
    res["fase1"]["criterios"] = dict(pf=O["pf"] >= 1.3, n=O["n"] >= 30, mdd=O["mdd"] > -0.20, pfnb=(O["pfnb"] or 0) > 1.0); res["fase1"]["pasa"] = all(res["fase1"]["criterios"].values())
    res["fase1"]["criterios_100"] = dict(pf=res["fase1"]["OOS"]["pf"] >= 1.3, n=res["fase1"]["OOS"]["n"] >= 30, mdd=res["fase1"]["OOS"]["mdd"] > -0.20, pfnb=(res["fase1"]["OOS"]["pfnb"] or 0) > 1.0)
    res["fijo"] = dict(final=float(eq["fijo"].iloc[-1]), ganancia_total_por_10k=float((eq["fijo"].iloc[-1] - 1) * 10000), mdd=float(((eq["fijo"] - eq["fijo"].cummax()) / eq["fijo"].cummax()).min()))
    res["_eq"] = eq; res["_eqo"] = eqo
    eq_desnudo, eq_v1 = equity_diaria(df, tb, "robot"), equity_diaria(df, tp, "robot")
    sem = pd.DataFrame({**{k: eq[k] for k in ["capital", "fijo", "robot", "p20", "x2", "atr", "vt"]}, "desnudo": eq_desnudo, "v1": eq_v1}).resample("W-SUN").last().dropna()
    (OUT / ("equity_semanal.json" if args.etiqueta == "binance" else f"equity_semanal_{args.etiqueta}.json")).write_text(json.dumps(dict(
        fechas=[d.strftime("%Y-%m-%d") for d in sem.index], oos=str(sp_date.date()), live=str(LIVE_DESDE.date()), **{k: [round(float(v), 4) for v in sem[k]] for k in sem.columns})), encoding="utf-8")
    # versiones: base, pine, v3 — periodo completo, validación y real, con el tamaño del robot y al 100 %
    def bloque(tr):
        er = equity_diaria(df, tr, "robot"); ya = er.resample("YE").last(); ya = (ya / ya.shift(1).fillna(er.iloc[0]) - 1)
        return dict(TODO=metricas(tr, equity_diaria(df, tr)), OOS=metricas(entre(tr, sp_date), eq_tramo(dfo, entre(tr, sp_date))), REAL=metricas(entre(tr, LIVE_DESDE)),
                    TODO_robot=metricas(tr, er, "robot"), OOS_robot=metricas(entre(tr, sp_date), eq_tramo(dfo, entre(tr, sp_date), "robot"), "robot"),
                    REAL_robot=metricas(entre(tr, LIVE_DESDE), sizing="robot"), peor_ano=int(ya.idxmin().year), peor_ano_ret=float(ya.min()), mejor_ano=int(ya.idxmax().year), mejor_ano_ret=float(ya.max()),
                    anos_positivos=int((ya > 0).sum()), anos_total=int(len(ya)))
    res["versiones"] = dict(base=bloque(tb), pine=bloque(tp), v3=bloque(ta)); res["_eq_base"], res["_eq_pine"] = equity_diaria(df, tb, "robot"), equity_diaria(df, tp, "robot")
    res["sizing"] = dict(robot=ROBOT, p20=P20, x2=X2, riesgo_atr=RIESGO_ATR, k_atr=K_ATR, vol_obj=VOL_OBJ, exposicion_media_atr=float(np.mean([t["expo_atr"] for t in ta])), exposicion_media_vt=float(np.mean([t["expo_vt"] for t in ta])), ejemplo=dict(precio=float(ta[-1]["px_ent"]), atr=float(df["atr"].iloc[ta[-1]["i_ent"] - 1]), atr_pct=float(ta[-1]["atrp"]), pct=float(ta[-1]["pct"]), fecha=str(ta[-1]["entrada"].date())))
    res["aed"] = aed(df, tb, sp_date)
    res["fase2"] = fase2_walkforward(df, ta)
    res["fase3"] = fase3_grid(df, sp_date)
    res["robustez_4d"] = robustez_4d(df, sp_date)
    res["robustez_params"] = robustez_params(raw, sp_date, cl); res["robustez_dia"] = robustez_dia(df, sp_date, cl)
    res["fase3"]["pasa"] = bool(res["fase3"]["pasa"] and res["robustez_params"]["pasa"])
    res["fase4"] = fase4_montecarlo(ta, sizing="robot", guardar_caminos=True, anos=anos_tot)
    res["fase4_100"] = {k: v for k, v in fase4_montecarlo(ta, sizing="capital", anos=anos_tot).items() if not k.startswith("_")}
    res["mc_tamano"] = mc_por_tamano(ta)
    res["fase5"] = fase5_stress(df, ta, sp_date)
    res["monkey"] = monkey_test(df, ta)
    res["edge_decay"] = edge_decay(ta, sp_date); res["edge_decay"]["movil"] = pf_movil(ta, 40)
    res["vigilancia"] = vigilancia(ta, base_tr=tb, df=df)
    res["drawdowns"] = episodios_dd(eq["capital"], px=px); res["drawdowns_robot"] = episodios_dd(eq["robot"], top=5, px=px); res["drawdowns_x2"] = episodios_dd(eq["x2"], top=3)
    res["drawdowns_p20"] = episodios_dd(eq["p20"], top=3); res["drawdowns_atr"] = episodios_dd(eq["atr"], top=3); res["drawdowns_vt"] = episodios_dd(eq["vt"], top=3)
    res["mensual"] = mensual(eq["robot"], px=px)
    btc_d = px.resample("D").last().ffill(); res["btc"] = dict(ret_total=float(btc_d.iloc[-1] / btc_d.iloc[0] - 1), mdd=float(((btc_d - btc_d.cummax()) / btc_d.cummax()).min()),
                                                             cagr=float((btc_d.iloc[-1] / btc_d.iloc[0]) ** (1 / anos_tot) - 1), vol_anual=float(btc_d.pct_change().std() * np.sqrt(365)))
    # ¿ayuda una media móvil? la v3 solo con BTC por encima de su media de 50 / 200 días (al 40 %)
    sma = {}
    for k in ["sma50", "sma200"]:
        tr_ = [t for t in ta if t.get(k)]; e_ = equity_diaria(df, tr_, "robot")
        sma[k] = dict(TODO=metricas(tr_, e_, "robot"), OOS=metricas(entre(tr_, sp_date), eq_tramo(dfo, entre(tr_, sp_date), "robot"), "robot"), n_quita=int(len(ta) - len(tr_)), _eq=e_)
    res["sma"] = sma
    res["revision"] = revision(df, tb, sp_date)
    if args.etiqueta == "binance":
        res["exchanges"] = exchanges(df, sp_date)
    res["veredicto"] = dict(fase1=res["fase1"]["pasa"], fase2=res["fase2"]["pasa"], fase3=res["fase3"]["pasa"], fase4=res["fase4"]["pasa"], fase5=res["fase5"]["pasa"],
                            fase5_protocolo=res["fase5"]["pasa_protocolo"])
    if not args.solo_metricas:
        from graficos import graficos
        graficos(df, ta, tb, tp, sp_date, res, raw)
        pd.DataFrame([{k: (str(v) if isinstance(v, pd.Timestamp) else v) for k, v in t.items() if not k.startswith("i_")} for t in ta]).round(5).to_csv(OUT / "trades.csv", index=False)
        pd.DataFrame({"capital_100": eq["capital"], "fijo_10k": eq["fijo"], "robot_40": eq["robot"], "p20": eq["p20"], "x2": eq["x2"], "riesgo_1pct_atr": eq["atr"], "vol_targeting_1.5": eq["vt"], "desnudo_40": eq_desnudo, "v1_40": eq_v1}).round(5).to_csv(OUT / "equity_diaria.csv")
    limpio = {k: v for k, v in res.items() if not k.startswith("_")}
    for f in ("fase4", "monkey", "robustez_4d", "aed"): limpio[f] = {k: v for k, v in limpio[f].items() if not k.startswith("_")}
    limpio["sma"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in limpio["sma"].items()}
    if "exchanges" in limpio: limpio["exchanges"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in limpio["exchanges"].items()}
    (OUT / ("metricas.json" if args.etiqueta == "binance" else f"metricas_{args.etiqueta}.json")).write_text(json.dumps(limpio, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    f1 = res["fase1"]; o = f1["OOS_robot"]
    print(f"{args.etiqueta}: {res['meta']['desde']} → {res['meta']['hasta']} · IS {f1['IS']['n']} / OOS {o['n']} trades · coste {cl*1e4:.0f} bps/lado")
    print(f"  OOS (40 %) PF {o['pf']:.2f} PFnb {o['pfnb']:.2f} MaxDD {o['mdd']*100:.1f}% (diario {o['mdd_diario']*100:.1f}%) CAGR {o['cagr']*100:.1f}% WR {o['wr']*100:.0f}%")
    print(f"  Fases: {res['veredicto']} · WF ef {res['fase2'].get('eficiencia')} pos {res['fase2'].get('pct_positivas')} · F3 centro {res['fase3']['centro']:.2f} celdas>1 {res['fase3']['pct_celdas_pf1']:.2f}")
    print(f"  MC(40%) p5ret {res['fase4']['p5_ret']:.2f} mddp5 {res['fase4']['mdd_p5']:.3f} ruina {res['fase4']['prob_ruina']} · tope {res['mc_tamano']['tope']} · mono {res['monkey']['pct_pf']:.3f} · z {res['vigilancia']['z_hoy']}")


if __name__ == "__main__":
    main()
