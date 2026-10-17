"""Cálculo de los tres casos aplicados (lo usan la página 5 y el panel principal)."""
import pandas as pd

from utils.financial_math import (
    TASA_EA, TASA_NOM_V, TASA_PER_V, PERIODICIDADES, a_efectiva_anual, desde_efectiva_anual, ea_neta, tasa_combinada,
    tabla_cuota_fija, tabla_abono_constante, factor_vf_serie,
    flujos_gradiente_aritmetico, flujos_gradiente_geometrico, vf_flujos,
)

# Datos de ofertas reales consultadas el 17 de octubre de 2026 (fuente y fecha en cada caso).
DEFAULTS = {
    # Caso 1: CDT Bancolombia a 360 días (9.40 % EA, retención 4 %) frente a la cuenta de ahorros
    # Davivienda (0.10 % EA con cuota de manejo de $16.500 al mes, $198.000 en 12 meses).
    "c1": dict(cap=50_000_000.0, meses=12, cdt_tipo=TASA_EA, cdt_val=9.40, cdt_per="Mensual",
               ah_ea=0.10, ah_costo=16_500.0, ret=4.0, infl=5.5, pts=3.0,
               fuente="CDT: simulador de CDT de Bancolombia, plazo 360 días (bancolombia.com). "
                      "Cuenta de ahorros: simulador de Davivienda "
                      "(davivienda.com/simuladores/simulador-cuenta-de-ahorros). "
                      "Inflación + puntos: escenario de referencia.",
               fecha="17 de octubre de 2026"),
    # Caso 2: crédito de libre inversión Bancolombia, tasa fija desde 1.30 % MV (16.77 % EA)
    # frente a tasa variable IBR + puntos desde 15.36 % EA. Tasas vigentes desde el 1 de octubre de 2026.
    "c2": dict(cap=60_000_000.0, anios=5.0,
               a_nombre="Tasa fija", a_tipo=TASA_PER_V, a_val=1.30, a_per="Mensual",
               b_nombre="Tasa variable IBR", b_tipo=TASA_EA, b_val=15.36, b_per="Mensual",
               fuente="Bancolombia, crédito de libre inversión, tasas vigentes desde el 1 de octubre de 2026 "
                      "(bancolombia.com/personas/creditos/consumo/credito-libre-inversion).",
               fecha="17 de octubre de 2026"),
    # Caso 3: Cajitas de ahorro de Nu, hasta 8.25 % EA, disponibles siempre, desde $50.000.
    "c3": dict(meta=30_000_000.0, meses=36, ea=8.25, grad="Aritmético", g_arit=10_000.0, g_geom=1.0,
               fuente="Nu Colombia, Cajitas de ahorro: hasta 8.25 % E.A. (nu.com.co/cuenta).",
               fecha="17 de octubre de 2026"),
}


def calcular_caso1(p):
    """Compara tres destinos para el mismo capital y plazo.

    Los costos (cuota de manejo de la cuenta de ahorros) se restan del rendimiento neto, como
    hace el VTUP del simulador de Davivienda. La EA neta se despeja del valor final:
    EA_neta = (VF_neto / C)^(1/t) − 1, y puede ser negativa si los costos superan los intereses.
    """
    t = p["meses"] / 12
    m = PERIODICIDADES[p["cdt_per"]]
    ea_cdt = a_efectiva_anual(p["cdt_tipo"], p["cdt_val"] / 100, m)
    ret = p["ret"] / 100
    opciones = [
        ("CDT Bancolombia", ea_cdt, 0.0),
        ("Cuenta de ahorros Davivienda", p["ah_ea"] / 100, p.get("ah_costo", 0.0)),
        ("Inversión inflación + puntos", tasa_combinada(p["infl"] / 100, p["pts"] / 100), 0.0),
    ]
    prods = []
    for nombre, ea, costo_mes in opciones:
        bruto = p["cap"] * ((1 + ea) ** t - 1)
        costos = costo_mes * p["meses"]
        neto = bruto * (1 - ret) - costos
        vf = p["cap"] + neto
        prods.append(dict(nombre=nombre, ea=ea, ea_neta=(vf / p["cap"]) ** (1 / t) - 1, bruto=bruto,
                          retencion=bruto * ret, costo_mes=costo_mes, costos=costos, neto=neto, vf=vf))
    mejor = max(prods, key=lambda x: x["neto"])
    nominal_cdt = desde_efectiva_anual(ea_cdt, m)["nominal_vencida"]
    vf_simple = p["cap"] * (1 + nominal_cdt * t)
    vf_comp = p["cap"] * (1 + ea_cdt) ** t
    return dict(prods=prods, mejor=mejor, vf_simple=vf_simple, vf_comp=vf_comp, nominal_cdt=nominal_cdt)


def _oferta(cap, anios, tipo, val, per):
    m = PERIODICIDADES[per]
    ea = a_efectiva_anual(tipo, val / 100, m)
    i = (1 + ea) ** (1 / m) - 1
    n = max(1, int(round(anios * m)))
    t = tabla_cuota_fija(cap, i, n)
    return dict(ea=ea, i=i, m=m, n=n, tabla=t, cuota=t["Cuota"].iloc[0],
                intereses=t["Intereses"].sum(), total=t["Cuota"].sum())


def nombres_ofertas(nombre_a, nombre_b):
    """Nombres no vacíos y distintos (con nombres iguales las tablas perderían una columna)."""
    na = (nombre_a or "").strip() or "Oferta A"
    nb = (nombre_b or "").strip() or "Oferta B"
    if na == nb:
        na, nb = f"{na} (A)", f"{nb} (B)"
    return na, nb


def calcular_caso2(p):
    """Compara dos créditos por su costo real.

    Criterio: la oferta con MENOR tasa efectiva anual es la más barata. Sumar las cuotas
    ("total pagado") no sirve para decidir, porque suma pesos de fechas distintas: dos
    ofertas con la misma EA pero distinta periodicidad tienen totales distintos y cuestan
    lo mismo. La diferencia en pesos se mide en valor presente: las cuotas de la oferta cara
    descontadas a la tasa de la barata, menos el capital.
    """
    a = _oferta(p["cap"], p["anios"], p["a_tipo"], p["a_val"], p["a_per"])
    b = _oferta(p["cap"], p["anios"], p["b_tipo"], p["b_val"], p["b_per"])
    a["nombre"], b["nombre"] = nombres_ofertas(p["a_nombre"], p["b_nombre"])
    iguales = abs(a["ea"] - b["ea"]) < 1e-9
    mejor = a if a["ea"] <= b["ea"] else b
    peor = b if mejor is a else a
    # Tasa de la oferta barata expresada en la periodicidad de pago de la cara
    i_desc = (1 + mejor["ea"]) ** (1 / peor["m"]) - 1
    t = peor["tabla"]
    vp_peor = float(sum(c / (1 + i_desc) ** k for k, c in zip(t["Periodo"], t["Cuota"])))
    ahorro_vp = 0.0 if iguales else vp_peor - p["cap"]
    ac = tabla_abono_constante(p["cap"], mejor["i"], mejor["n"])
    return dict(a=a, b=b, mejor=mejor, peor=peor, iguales=iguales, ahorro_vp=ahorro_vp,
                dif_total=peor["total"] - mejor["total"],
                int_abono_constante=ac["Intereses"].sum(), primera_cuota_ac=ac["Cuota"].iloc[0])


def calcular_caso3(p):
    i = (1 + p["ea"] / 100) ** (1 / 12) - 1
    n = int(p["meses"])
    f_unif = factor_vf_serie(i, n)
    if p["grad"] == "Aritmético":
        g = p["g_arit"]
        a1 = (p["meta"] - vf_flujos(flujos_gradiente_aritmetico(0, g, n), i)) / f_unif
        flujos = flujos_gradiente_aritmetico(a1, g, n)
    else:
        g = p["g_geom"] / 100
        a1 = p["meta"] / vf_flujos(flujos_gradiente_geometrico(1, g, n), i)
        flujos = flujos_gradiente_geometrico(a1, g, n)
    cuota_unif = p["meta"] / f_unif
    return dict(i=i, n=n, a1=a1, flujos=flujos, ultima=flujos[-1], total=flujos.sum(),
                intereses=p["meta"] - flujos.sum(), cuota_unif=cuota_unif, total_unif=cuota_unif * n)


def primera_cuota_requerida(p, ea_pct):
    """Primera cuota necesaria para la meta con otra tasa (para el análisis de sensibilidad)."""
    q = dict(p, ea=ea_pct)
    return calcular_caso3(q)["a1"]


def decision_caso2(r2):
    m, q = r2["mejor"], r2["peor"]
    if r2["iguales"]:
        return (f"Las dos ofertas cuestan lo mismo (EA {m['ea'] * 100:.2f}%): elige según la cuota "
                "que se ajuste a tu flujo de caja.")
    return (f"Elegir «{m['nombre']}»: EA de {m['ea'] * 100:.2f}% frente a {q['ea'] * 100:.2f}%; "
            f"ahorra ${r2['ahorro_vp']:,.0f} en valor presente.")


def decision_caso3(r3):
    if r3["a1"] <= 0:
        return "Revisar el gradiente: la primera cuota resulta negativa."
    dif = r3["cuota_unif"] - r3["a1"]
    if abs(dif) < 0.005:
        return f"Aportar ${r3['a1']:,.0f} al mes: sin gradiente, igual a la cuota uniforme."
    if dif > 0:
        return f"Empezar con ${r3['a1']:,.0f}, ${dif:,.0f} menos que la cuota uniforme de ${r3['cuota_unif']:,.0f}."
    return (f"Empezar con ${r3['a1']:,.0f}, ${-dif:,.0f} más que la cuota uniforme de "
            f"${r3['cuota_unif']:,.0f}, e ir bajando.")


def vf_gradiente_formula(a1, g, n, i, tipo):
    """VF de un gradiente vencido por fórmula cerrada (para la verificación)."""
    s = factor_vf_serie(i, n)
    if tipo == "Aritmético":
        return a1 * s + (g / i) * (s - n)
    if abs(i - g) < 1e-12:
        return n * a1 * (1 + i) ** (n - 1)
    return a1 * ((1 + i) ** n - (1 + g) ** n) / (i - g)


# Qué tema del curso usa cada caso (para la matriz de cobertura del resumen)
TEMAS_POR_CASO = [
    ("Interés simple", (True, False, False), "Caso 1: valor final del CDT si se liquidara a interés simple."),
    ("Interés compuesto", (True, False, True), "Caso 1: crecimiento del capital; caso 3: capitalización de los aportes."),
    ("Rentabilidad y equivalencia de tasas", (True, True, True),
     "Caso 1: EA neta, retención e inflación + puntos; caso 2: nominal vencida y anticipada a EA; "
     "caso 3: EA a tasa mensual."),
    ("Series uniformes", (False, True, True), "Caso 2: la cuota fija es una serie uniforme; caso 3: cuota uniforme de referencia."),
    ("Gradientes", (False, False, True), "Caso 3: aportes con gradiente aritmético o geométrico."),
    ("Tablas de amortización", (False, True, False), "Caso 2: cuota fija frente a abono constante a capital."),
]


def calcular_casos(params):
    """Tabla resumen para el panel principal."""
    r1, r2, r3 = calcular_caso1(params["c1"]), calcular_caso2(params["c2"]), calcular_caso3(params["c3"])
    m1, m2 = r1["mejor"], r2["mejor"]
    return pd.DataFrame([
        {"Caso": "1. Inversión", "Producto o inversión": m1["nombre"],
         "Tasa efectiva anual": f"{m1['ea'] * 100:.2f}% (neta {m1['ea_neta'] * 100:.2f}%)",
         "Valor total recibido / pagado": f"${m1['vf']:,.0f} recibidos",
         "Decisión recomendada": f"Invertir en {m1['nombre']}: mayores intereses netos a {params['c1']['meses']} meses."},
        {"Caso": "2. Crédito", "Producto o inversión": m2["nombre"],
         "Tasa efectiva anual": f"{m2['ea'] * 100:.2f}%",
         "Valor total recibido / pagado": f"${m2['total']:,.0f} pagados",
         "Decisión recomendada": decision_caso2(r2)},
        {"Caso": "3. Plan de ahorro", "Producto o inversión": f"Ahorro con gradiente {params['c3']['grad'].lower()}",
         "Tasa efectiva anual": f"{params['c3']['ea']:.2f}%",
         "Valor total recibido / pagado": f"${r3['total']:,.0f} aportados",
         "Decisión recomendada": decision_caso3(r3)},
    ])