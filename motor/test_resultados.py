"""
Pruebas de coherencia de resultados/ ANTES de construir el HTML.

Comprueba que el motor dejó todo lo que las páginas necesitan y que las cifras son coherentes entre sí.
Si algo falla, construir_html.py no arranca. Uso: python motor/test_resultados.py (también lo llama construir_html.py).
Sale con código 0 si todo está OK, 1 si hay fallos. Los avisos no bloquean.
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RES, G = RAIZ / "resultados", RAIZ / "resultados" / "graficos"
GRAFICOS = ["01_equity", "02_operaciones_ano", "03_versiones", "04_grid", "05_montecarlo", "06_monkey", "07_pf_anual", "08_underwater", "09_walkforward", "10_riesgo",
            "11_robustez_4d", "11_params_mapas", "11b_params_barras", "11c_vecinos", "11d_dia_regla", "01b_backtest", "21b_dias", "29_sma", "13_aed_semana", "13b_dias_eras", "14_aed_eras", "15_aed_quintiles", "16_operacion_ejemplo",
            "17_atr", "18_aed_colas", "19_meses", "20_dd_bins", "21_horas", "22_duracion", "23_tp_sl", "24_mae_mfe", "25_exchanges", "26_vigilancia", "27_filtros", "28_sizing_atr"]
fallos, avisos = [], []


def ok(cond, msg):
    if not cond: fallos.append(msg)


def aviso(cond, msg):
    if not cond: avisos.append(msg)


def num(x):
    return isinstance(x, (int, float)) and x == x


# ------------------------------------------------------------------ ficheros
for f in ["metricas.json", "equity_semanal.json", "trades.csv", "equity_diaria.csv", "metricas_coinbase.json", "reconciliacion_tradingview.json"]:
    ok((RES / f).exists(), f"falta resultados/{f}")
for g in GRAFICOS:
    p = G / f"{g}.png"; ok(p.exists() and p.stat().st_size > 5000, f"falta o está vacío el gráfico {g}.png")
if fallos:
    print("FALLOS:\n- " + "\n- ".join(fallos)); sys.exit(1)

M = json.loads((RES / "metricas.json").read_text(encoding="utf-8")); SEM = json.loads((RES / "equity_semanal.json").read_text(encoding="utf-8"))
CB = json.loads((RES / "metricas_coinbase.json").read_text(encoding="utf-8")); REC = json.loads((RES / "reconciliacion_tradingview.json").read_text(encoding="utf-8"))

# ------------------------------------------------------------------ meta
meta = M["meta"]
for k in ["activo", "exchange", "fuente", "desde", "hasta", "velas", "atr_len", "pct_min", "robot", "is_desde", "is_hasta", "oos_desde", "oos_hasta", "live_desde", "generado"]:
    ok(k in meta and meta[k] not in (None, ""), f"meta.{k} vacío")
ok(meta["is_hasta"] <= meta["oos_desde"] < meta["live_desde"], "las fechas construcción ≤ validación < real no están en orden")
ok(meta["velas"] > 50000, f"muy pocas velas ({meta['velas']})"); ok(meta["exchange"] == "binance" and "Binance" in meta["fuente"], "la fuente principal debe ser Binance")
ok(abs(meta["coste_lado_bps"] - 14.0) < 1e-6, f"coste por lado de Binance ≠ 14 bps ({meta['coste_lado_bps']})")

# ------------------------------------------------------------------ fase 1
f1 = M["fase1"]; I, O, T = f1["IS"], f1["OOS"], f1["TODO"]; Ir, Or, Tr = f1["IS_robot"], f1["OOS_robot"], f1["TODO_robot"]
for nombre, m in [("IS", I), ("OOS", O), ("TODO", T), ("IS_robot", Ir), ("OOS_robot", Or), ("TODO_robot", Tr), ("OOS_p20", f1["OOS_p20"]), ("OOS_x2", f1["OOS_x2"]), ("TODO_x2", f1["TODO_x2"]), ("OOS_atr", f1["OOS_atr"]), ("TODO_atr", f1["TODO_atr"]), ("OOS_vt", f1["OOS_vt"]), ("TODO_vt", f1["TODO_vt"])]:
    for k in ["n", "pf", "pfnb", "mdd", "wr", "expectancy", "ret_total", "cagr", "mdd_diario"]:
        ok(k in m and num(m[k]), f"fase1.{nombre}.{k} falta o no es número")
    ok(m["pfnb"] <= m["pf"] + 1e-9, f"fase1.{nombre}: PF sin mejor trade > PF"); ok(0 <= m["wr"] <= 1, f"fase1.{nombre}: win rate fuera de [0,1]")
ok(abs(I["n"] + O["n"] - T["n"]) <= 1, f"IS ({I['n']}) + OOS ({O['n']}) ≠ total ({T['n']})")
ok(abs(I["pf"] - Ir["pf"]) < 1e-6 and abs(O["pf"] - Or["pf"]) < 1e-6, "el PF no debería depender del tamaño")
crit = f1["criterios"]
ok(crit["pf"] == (Or["pf"] >= 1.3) and crit["n"] == (Or["n"] >= 30) and crit["mdd"] == (Or["mdd"] > -0.20) and crit["pfnb"] == ((Or["pfnb"] or 0) > 1.0), "criterios de la Fase 1 mal evaluados")
ok(f1["pasa"] == all(crit.values()), "fase1.pasa no coincide con sus criterios")
ok(f1["TODO_p20"]["mdd_diario"] >= Tr["mdd_diario"] - 1e-9 >= T["mdd_diario"] - 1e-9 >= f1["TODO_x2"]["mdd_diario"] - 1e-9, "los drawdowns por tamaño no están ordenados (20 % ≤ 40 % ≤ 100 % ≤ 1:2)")

# ------------------------------------------------------------------ versiones
V = M["versiones"]
for v in ["base", "pine", "v3"]:
    for k in ["TODO", "OOS", "REAL", "TODO_robot", "OOS_robot", "REAL_robot"]:
        ok(num(V[v][k]["pf"]) and V[v][k]["n"] > 0, f"versiones.{v}.{k} incompleto")
ok(V["v3"]["OOS"]["n"] == O["n"] and abs(V["v3"]["OOS"]["pf"] - O["pf"]) < 1e-6, "versiones.v3 no coincide con la Fase 1")
ok(V["base"]["TODO"]["n"] > V["pine"]["TODO"]["n"] > 0 and V["base"]["TODO"]["n"] > V["v3"]["TODO"]["n"], "la base debe tener más operaciones que las versiones filtradas")

# ------------------------------------------------------------------ fase 2
f2 = M["fase2"]
ok(len(f2["ventanas"]) >= 5, f"walk-forward con pocas ventanas ({len(f2['ventanas'])})")
ok(num(f2.get("eficiencia")) and num(f2["pct_positivas"]) and num(f2["peor_mdd"]), "walk-forward sin eficiencia / % positivas / peor mdd")
ok(f2["pasa"] == (f2["eficiencia"] >= 0.5 and f2["pct_positivas"] >= 0.6 and f2["peor_mdd"] > -0.20), "fase2.pasa no coincide con sus criterios")
anos = [v["ano"] for v in f2["ventanas"]]; ok(anos == sorted(anos) and len(set(anos)) == len(anos), "ventanas del walk-forward desordenadas o repetidas")

# ------------------------------------------------------------------ fase 3 y robustez
f3 = M["fase3"]; pf = f3["pf"]; nn = f3["n"]; ia = ib = f3["off_in"].index(0)
ok(all(num(v) and v > 0 for fila in pf for v in fila), "hay celdas vacías en la rejilla de horas")
ok(abs(pf[ia][ib] - f3["centro"]) < 1e-3, "fase3.centro no coincide con la celda central")
ok(abs(pf[ia][ib] - I["pf"]) < 0.02, f"el PF de la celda que opera ({pf[ia][ib]:.3f}) no coincide con el PF IS de la Fase 1 ({I['pf']:.3f})")
vec = [pf[a][b] for a in range(ia - 1, ia + 2) for b in range(ib - 1, ib + 2)]; caida = max(1 - v / f3["centro"] for v in vec) * 100
ok(abs(caida - f3["peor_caida_vecino_pct"]) < 0.5 and f3["anticliff"] == (caida <= 30), "fase3: anti-cliff mal evaluado")
ok(f3["vecinos_dentro_20"] == all(v >= f3["centro"] * 0.8 for v in vec), "fase3.vecinos_dentro_20 mal evaluado")
ok(f3["pasa"] == (f3["vecinos_dentro_20"] and f3["anticliff"] and all(v > 1 for fila in pf for v in fila) and f3["n_minimo_ok"]), "fase3.pasa no coincide con sus criterios")
r4 = M["robustez_4d"]
ok(r4["n_combos"] == 25 * len(r4["filtros"]) * len(r4["costes"]), "robustez_4d: n_combos no cuadra")
for k in r4["cubos"]: ok(k in r4["cubos_mdd"] and k in r4["cubos_n"] and all(num(v) for fila in r4["cubos"][k] for v in fila), f"robustez_4d: cubo '{k}' incompleto")
ok(abs(r4["pf_vigente"] - pf[ia][ib]) < 1e-3, "robustez_4d.pf_vigente no coincide con la celda que opera")
ok(r4["por_coste"][r4["costes"][0]] >= r4["por_coste"][r4["costes"][1]], "robustez_4d: con más coste el PF medio debería bajar")

# ------------------------------------------------------------------ fase 4 y tamaño
for nombre in ["fase4", "fase4_100"]:
    f4 = M[nombre]
    ok(f4["n_sim"] >= 5000, f"{nombre}: menos de 5.000 simulaciones"); ok(f4["p5_ret"] <= f4["p50_ret"] <= f4["p95_ret"], f"{nombre}: percentiles de retorno desordenados")
    ok(f4["mdd_p5"] <= f4["mdd_p50"] <= f4["mdd_p95"] <= 0 and f4["mdd_peor"] <= f4["mdd_p5"], f"{nombre}: percentiles de drawdown desordenados")
    ok(f4["pasa_estricto"] == (f4["p5_ret"] > 0 and f4["mdd_p5"] > -0.25 and f4["prob_ruina"] < 0.05), f"{nombre}.pasa_estricto no coincide con sus criterios")
    ok(f4["pasa"] == (f4["p5_ret"] > 0 and f4["mdd_p5"] > -(0.25 + f4["tolerancia_dd"]) and f4["prob_ruina"] < 0.05), f"{nombre}.pasa no coincide con sus criterios (con el margen de {f4['tolerancia_dd']*100:.0f} punto)")
ok(M["fase4"]["sizing"] == "robot" and M["fase4"]["mdd_p5"] >= M["fase4_100"]["mdd_p5"], "el Monte Carlo del robot debe tener menos drawdown que el del 100 %")
mt = M["mc_tamano"]; ok(len(mt["filas"]) >= 6 and all(mt["filas"][i]["mdd_p95"] >= mt["filas"][i + 1]["mdd_p95"] - 1e-9 for i in range(len(mt["filas"]) - 1)), "mc_tamano: el drawdown debe crecer con el tamaño")
aviso(M["fase4"]["pasa_estricto"], f"Fase 4 al {int(meta['robot']*100)} % superada solo con el margen de 1 punto aceptado (p95 DD {M['fase4']['mdd_p5']*100:.1f} %); sin margen el tope es el {mt['tope']}")

# ------------------------------------------------------------------ fase 5
f5 = M["fase5"]
ok(f5["costes_x2"]["n"] == O["n"] and f5["costes_x2"]["pf"] <= O["pf"] + 1e-9, "estrés costes×2: operaciones o PF incoherentes")
ok(len(f5["sin_2_mejores_anos"]["anos"]) == 2 and f5["sin_2_mejores_anos"]["n"] < O["n"], "estrés sin 2 mejores años mal construido")
ok(f5["pasa_protocolo"] == (f5["costes_x2"]["pasa"] and f5["sin_2_mejores_anos"]["pasa"] and f5["regimen_malo_2018_2022"]["pasa"]), "fase5.pasa_protocolo no coincide")
ok(f5["excepcion"]["aprobada"] is True and f5["excepcion"]["fecha"], "la excepción de la Fase 5 tiene que estar documentada")
aviso(f5["pasa_protocolo"], "Fase 5: el escenario 2018+2022 no supera el criterio; se publica con la excepción documentada")

# ------------------------------------------------------------------ mono, AED, desgaste, vigilancia, drawdowns, mensual, revisión, exchanges, reconciliación
mk = M["monkey"]; ok(mk["n_sim"] >= 1000 and 0 <= mk["pct_pf"] <= 1 and abs(mk["pf_real"] - T["pf"]) < 1e-6, "monkey test incompleto o PF real distinto del total")
ae = M["aed"]; ok(len(ae["eras"]) == 3 and all(len(ae["semana"][e]) == 7 and len(ae["semana"][e][0]) == 24 for e in ae["eras"]), "AED: mapa de la semana incompleto")
ok(all(e in ae["lunes_por_era"] and e in ae["dias"] for e in ae["eras"]) and "ATR% en percentil del año" in ae["quintiles"], "AED: eras o quintiles incompletos")
ok(0 < ae["distribucion"]["top10_pct_beneficio"] < 1 and num(ae["distribucion"]["curtosis"]), "AED: distribución incompleta")
ed = M["edge_decay"]; ok(len(ed["anual"]) >= 8 and len(ed["movil"]) > 30 and num(ed["ultimos_3"]["pf"]), "edge decay incompleto")
vg = M["vigilancia"]; ok(num(vg["mu0"]) and num(vg["sigma0"]) and vg["n_ref"] > 50 and vg["n_live"] >= 20 and vg["estado"] in ("verde", "amarillo", "rojo"), "vigilancia incompleta")
for k in ["drawdowns", "drawdowns_robot"]:
    dd = M[k]; ok(dd["n"] > 5 and len(dd["bins"]) == 5 and sum(b["n"] for b in dd["bins"]) == dd["n"], f"{k}: episodios o tramos no cuadran")
ok(abs(M["drawdowns"]["peores"][0]["prof"] - T["mdd_diario"]) < 1e-6, "la peor caída al 100 % no coincide con el drawdown día a día del total")
ok(abs(M["drawdowns_robot"]["peores"][0]["prof"] - Tr["mdd_diario"]) < 1e-6, "la peor caída al 40 % no coincide con el drawdown día a día del robot")
me = M["mensual"]; ok(len(me["anos"]) == len(me["filas"]) == len(me["matriz"]) and all(len(f) == 12 for f in me["matriz"]), "mensual: matriz mal formada")
rv = M["revision"]; ok(len(rv["horas"]) == 49 and len(rv["duracion"]) >= 10 and all(k in rv["tp_sl"] for k in ["construccion", "validacion", "real"]) and len(rv["filtros"]) >= 8, "revisión incompleta")
ok(rv["filtros"][0]["filtro"].startswith("sin filtro") and abs(rv["filtros"][0]["validacion"]["n"] - V["base"]["OOS"]["n"]) <= 1, "revisión: la fila base no coincide con la versión base")
ex = M["exchanges"]; ok({"binance", "coinbase", "quantfury"} <= set(ex) and ex["binance"]["OOS"]["n"] == O["n"], "exchanges incompletos")
ok(ex["quantfury"]["OOS"]["pf"] >= ex["binance"]["OOS"]["pf"] >= ex["coinbase"]["OOS"]["pf"], "exchanges: más coste debería dar menos PF")
ok(CB["meta"]["exchange"] == "coinbase" and num(CB["fase1"]["OOS_robot"]["pf"]), "metricas_coinbase incompleto")
ok(REC["emparejadas"] == REC["tv"]["n"] and REC["dif_precio_entrada_pct"]["mediana"] < 0.05, "reconciliación con TradingView: no cuadran las operaciones")
ok("real" in REC and REC["real"]["n"] >= 20 and num(REC["real"]["pf"]) and num(REC["real"]["z_hoy"]), "reconciliación: falta el bloque de operaciones reales (desde 2025-02)")

# ------------------------------------------------------------------ curvas y veredicto
ok(all(k in SEM for k in ["fechas", "oos", "live", "capital", "fijo", "robot", "p20", "x2", "atr", "vt", "desnudo", "v1"]) and len({len(SEM[k]) for k in ["fechas", "capital", "fijo", "robot", "p20", "x2", "atr", "vt", "desnudo", "v1"]}) == 1, "equity_semanal.json incompleto")
ok(abs(SEM["robot"][-1] - (1 + Tr["ret_total"])) < 0.05, "la curva semanal del robot no termina donde dice el retorno total")
ok(all(k in M for k in ["drawdowns_p20", "drawdowns_atr", "drawdowns_vt", "robustez_params", "sma", "btc"]) and "exposicion_media_vt" in M["sizing"], "faltan drawdowns_vt, robustez_params, sma, btc o la exposición media del vol targeting")
rp_ = M["robustez_params"]; ok(rp_["pasa"] and rp_["vecinos_min"] >= rp_["centro"] * 0.8 and len(rp_["vecinos"]) == 8, "la rejilla de parámetros (ATR × percentil) no cumple la meseta de 8 vecinos")
vg_ = M["vigilancia"]; ok(len(vg_["todo"]) == T["n"] and len(vg_["permiso"]) > 100 and vg_["cuota_ref"] is not None, "la vigilancia no trae z en todo el histórico o la cuota de permiso")
ok(all("btc_dd" in e for e in M["drawdowns_robot"]["peores"]), "las peores caídas no llevan la caída de BTC en el mismo tramo")
ok("ret_anual_p50" in M["fase4"] and M["fase4"]["ret_anual_p50"] > 0, "el Monte Carlo no trae el retorno anualizado")
ok(SEM["robot"][-1] > SEM["desnudo"][-1] and SEM["robot"][-1] > SEM["v1"][-1], "la v3 no termina por encima del lunes desnudo y de la v1")
v = M["veredicto"]
ok(v["fase1"] == f1["pasa"] and v["fase2"] == f2["pasa"] and v["fase3"] == f3["pasa"] and v["fase4"] == M["fase4"]["pasa"] and v["fase5"] == f5["pasa"], "veredicto no coincide con las fases")
aviso(all(v[k] for k in ["fase1", "fase2", "fase3", "fase4", "fase5"]), "hay fases NO superadas: " + ", ".join(k for k in ["fase1", "fase2", "fase3", "fase4", "fase5"] if not v[k]) + " (revisar antes de publicar)")

print(f"Pruebas de resultados · {meta['activo']} · {meta['fuente']} · {meta['desde']} → {meta['hasta']} · generado {meta['generado']}")
print(f"  IS {I['n']} / OOS {O['n']} / total {T['n']} · PF OOS {O['pf']:.2f} · F3 centro {f3['centro']:.2f} · MC {M['fase4']['n_sim']} · veredicto {v}")
if avisos: print("AVISOS:\n- " + "\n- ".join(avisos))
if fallos:
    print("FALLOS:\n- " + "\n- ".join(fallos)); sys.exit(1)
print(f"OK · {len(GRAFICOS)} gráficos · 0 fallos · {len(avisos)} avisos")
