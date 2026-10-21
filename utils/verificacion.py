"""Verificación global del tablero (la usa el panel principal).

Repite, con los valores iniciales de cada página, las mismas comprobaciones de su pestaña
"Supuestos y verificación". Casos aplicados se verifica con los datos que estén en uso.
Si cambias los valores iniciales de una página, cámbialos también aquí.
"""
from utils.casos import calcular_caso1, calcular_caso2, calcular_caso3, vf_gradiente_formula
from utils.financial_math import (
    TASA_NOM_V, PERIODICIDADES, a_efectiva_anual, desde_efectiva_anual, tasa_combinada, ea_neta,
    interes_simple, interes_compuesto, despejar_tasa_compuesto, despejar_plazo_compuesto,
    vp_serie, vf_serie, cuota_desde_vp, factor_vp_serie, factor_vf_serie,
    flujos_gradiente_aritmetico, vp_flujos, vf_flujos, vp_gradiente_aritmetico_formula,
    cuota_fija, tabla_cuota_fija, tabla_abono_constante, tabla_amortizacion, vp_pagos_tabla,
    deflactar_tabla, tasa_real, SIS_CUOTA_FIJA, SIS_ABONO_CONSTANTE,
)

TOL = 1e-6


def coincide(modelo, manual, escala=0.0, tol=TOL):
    """Misma regla que la tabla de verificación de cada página."""
    return abs(modelo - manual) <= tol * max(1.0, abs(manual), abs(escala))


def _interes():
    capital, tasa, n = 1_000_000.0, 0.025, 12
    vf_s, _ = interes_simple(capital, tasa, n)
    vf_c, int_c = interes_compuesto(capital, tasa, n)
    return [
        ("VF compuesto = C·(1+i)ⁿ", vf_c, capital * (1 + tasa) ** n),
        ("VF simple = C·(1+i·n)", vf_s, capital * (1 + tasa * n)),
        ("Intereses compuestos = VF − C", int_c, vf_c - capital),
        ("Despeje de tasa (ida y vuelta)", despejar_tasa_compuesto(capital, vf_c, n), tasa),
        ("Despeje de plazo (ida y vuelta)", despejar_plazo_compuesto(capital, vf_c, tasa), float(n)),
    ]


def _tasas():
    m = 12
    ea_in = 0.12
    eq = desde_efectiva_anual(ea_in, m)
    iv, ia = eq["periodica_vencida"], eq["periodica_anticipada"]
    infl, pts = 0.055, 0.04
    ea_comb = tasa_combinada(infl, pts)
    cap, t, ea, ret = 20_000_000.0, 1.0, 0.10, 0.04
    bruto = cap * ((1 + ea) ** t - 1)
    neto = bruto * (1 - ret)
    return [
        ("EA → periódica → EA", (1 + iv) ** m - 1, ea_in),
        ("Anticipada → vencida", ia / (1 - ia), iv),
        ("Nominal capitalizada m veces rinde la EA", (1 + eq["nominal_vencida"] / m) ** m - 1, ea_in),
        ("Tasa combinada (1+π)(1+r)−1", ea_comb, (1 + infl) * (1 + pts) - 1),
        ("Fisher: (1+EA comb)/(1+π)−1 = puntos", (1 + ea_comb) / (1 + infl) - 1, pts),
        ("EA neta", (1 + ea_neta(ea, ret, t)) ** t, 1 + neto / cap),
    ]


def _series():
    cuota, i, n = 500_000.0, 0.015, 24
    vp, vf = vp_serie(cuota, i, n), vf_serie(cuota, i, n)
    a1, g, ig, ng = 300_000.0, 20_000.0, 0.015, 24
    flujos = flujos_gradiente_aritmetico(a1, g, ng)
    vp_g, vf_g = vp_flujos(flujos, ig), vf_flujos(flujos, ig)
    cuota_eq = cuota_desde_vp(vp_g, ig, ng)
    return [
        ("Serie: VP = Σ cuota/(1+i)^k", vp, sum(cuota / (1 + i) ** k for k in range(1, n + 1))),
        ("Serie: VF = Σ cuota·(1+i)^(n−k)", vf, sum(cuota * (1 + i) ** (n - k) for k in range(1, n + 1))),
        ("Serie: cuota ida y vuelta", cuota_desde_vp(vp, i, n), cuota),
        ("Serie anticipada = vencida · (1+i)", vp_serie(cuota, i, n, True), vp * (1 + i)),
        ("Gradiente: VP flujo a flujo = fórmula", vp_g, vp_gradiente_aritmetico_formula(a1, g, ng, ig)),
        ("Gradiente: cuota equivalente · a(n,i) = VP", cuota_eq * factor_vp_serie(ig, ng), vp_g),
        ("Gradiente: VF = VP · (1+i)^n", vf_g, vp_g * (1 + ig) ** ng),
    ]


def _amortizacion():
    capital, m, n = 50_000_000.0, 12, 60
    ea = a_efectiva_anual(TASA_NOM_V, 0.18, m)
    i = (1 + ea) ** (1 / m) - 1
    t_cf = tabla_amortizacion(capital, i, n, SIS_CUOTA_FIJA)
    t_ac = tabla_amortizacion(capital, i, n, SIS_ABONO_CONSTANTE)
    pi_p = 1.05 ** (1 / m) - 1
    dfl = deflactar_tabla(t_cf, pi_p)
    r_p = tasa_real(i, pi_p)
    reales = tasa_real(t_cf["Tasa periódica"].to_numpy(), pi_p)
    vp_real = float((dfl["Pago en pesos de hoy"].to_numpy() / (1 + reales).cumprod()).sum())
    return [
        ("Cuota fija: coincide con la tabla original",
         float((t_cf["Saldo"] - tabla_cuota_fija(capital, i, n)["Saldo"]).abs().max()), 0.0, capital),
        ("Cuota fija: cuota = P·i/(1−(1+i)^−n)", t_cf["Cuota"].iloc[0], capital * i / (1 - (1 + i) ** -n)),
        ("Cuota fija: ajuste de la última cuota", t_cf["Cuota"].iloc[-1], cuota_fija(capital, i, n), capital),
        ("Cuota fija: suma de abonos = capital", t_cf["Abono a capital"].sum(), capital),
        ("Cuota fija: saldo final = 0", t_cf["Saldo"].iloc[-1], 0.0, capital),
        ("Cuota fija: VP de las cuotas = capital", vp_pagos_tabla(t_cf), capital),
        ("Abono constante: coincide con la tabla original",
         float((t_ac["Saldo"] - tabla_abono_constante(capital, i, n)["Saldo"]).abs().max()), 0.0, capital),
        ("Abono constante: suma de abonos = capital", t_ac["Abono a capital"].sum(), capital),
        ("Abono constante: saldo final = 0", t_ac["Saldo"].iloc[-1], 0.0, capital),
        ("Abono constante: VP de las cuotas = capital", vp_pagos_tabla(t_ac), capital),
        ("Total pagado = capital + intereses", t_cf["Pago total"].sum(), capital + t_cf["Intereses"].sum()),
        ("Fisher: (1 + r)(1 + π) = 1 + i", (1 + r_p) * (1 + pi_p), 1 + i),
        ("Pagos en pesos de hoy a la tasa real = capital", vp_real, capital),
    ]


def _casos(params):
    p1, p2, p3 = params["c1"], params["c2"], params["c3"]
    r1, r2, r3 = calcular_caso1(p1), calcular_caso2(p2), calcular_caso3(p3)
    t1 = p1["meses"] / 12
    filas = [(f"Caso 1 · {pr['nombre']}: EA neta", p1["cap"] * (1 + pr["ea_neta"]) ** t1, pr["vf"])
             for pr in r1["prods"]]
    cdt, ah = r1["prods"][0], r1["prods"][1]
    filas += [
        ("Caso 1 · CDT: intereses brutos", cdt["bruto"], p1["cap"] * ((1 + cdt["ea"]) ** t1 - 1)),
        ("Caso 1 · Cuenta de ahorros: ganancia neta", ah["neto"],
         ah["bruto"] * (1 - p1["ret"] / 100) - p1.get("ah_costo", 0.0) * p1["meses"]),
        ("Caso 1 · CDT: retención", cdt["retencion"], cdt["bruto"] * p1["ret"] / 100),
        ("Caso 1 · Inflación + puntos", r1["prods"][2]["ea"],
         (1 + p1["infl"] / 100) * (1 + p1["pts"] / 100) - 1),
    ]
    if (abs(p1["cap"] - 50_000_000) < 0.5 and p1["meses"] == 12 and p1["cdt_tipo"] == "Efectiva anual (EA)"
            and abs(p1["cdt_val"] - 9.40) < 1e-9 and abs(p1["ret"] - 4.0) < 1e-9):
        filas += [("Caso 1 · CDT = simulador de Bancolombia (ganancia)", cdt["neto"], 4_512_000.00),
                  ("Caso 1 · CDT = simulador de Bancolombia (retención)", cdt["retencion"], 188_000.00)]
    for of in (r2["a"], r2["b"]):
        t = of["tabla"]
        filas += [
            (f"Caso 2 · {of['nombre']}: cuota", of["cuota"], cuota_fija(p2["cap"], of["i"], of["n"])),
            (f"Caso 2 · {of['nombre']}: saldo final = 0", float(t["Saldo"].iloc[-1]), 0.0, p2["cap"]),
            (f"Caso 2 · {of['nombre']}: VP de las cuotas = crédito",
             float(sum(c / (1 + of["i"]) ** k for k, c in zip(t["Periodo"], t["Cuota"]))), p2["cap"]),
        ]
    filas += [
        ("Caso 3 · VF de los aportes = meta", vf_flujos(r3["flujos"], r3["i"]), p3["meta"]),
        ("Caso 3 · cuota uniforme = meta", r3["cuota_unif"] * factor_vf_serie(r3["i"], r3["n"]), p3["meta"]),
    ]
    if r3["i"] > 0:
        g = p3["g_arit"] if p3["grad"] == "Aritmético" else p3["g_geom"] / 100
        filas.append(("Caso 3 · VF del gradiente por fórmula = meta",
                      vf_gradiente_formula(r3["a1"], g, r3["n"], r3["i"], p3["grad"]), p3["meta"]))
    return filas


MODULOS = [
    ("Interés simple y compuesto", _interes),
    ("Rentabilidad y tasas", _tasas),
    ("Series y gradientes", _series),
    ("Tablas de amortización", _amortizacion),
]


def verificar_todo(params_casos):
    """Lista de módulos con cuántas pruebas pasan: [{'Módulo', 'Pruebas', 'Coinciden', 'fallas'}]."""
    resultado = []
    for nombre, fn in MODULOS + [("Casos aplicados", lambda: _casos(params_casos))]:
        filas = fn()
        fallas = [f[0] for f in filas if not coincide(f[1], f[2], f[3] if len(f) > 3 else 0.0)]
        resultado.append({"Módulo": nombre, "Pruebas": len(filas), "Coinciden": len(filas) - len(fallas),
                          "fallas": fallas})
    return resultado
