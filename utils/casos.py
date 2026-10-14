"""Cálculo de los tres casos aplicados (lo usan la página 5 y el panel principal)."""
import pandas as pd

from utils.financial_math import (
    TASA_NOM_V, PERIODICIDADES, a_efectiva_anual, desde_efectiva_anual, ea_neta, tasa_combinada,
    tabla_cuota_fija, tabla_abono_constante, factor_vf_serie,
    flujos_gradiente_aritmetico, flujos_gradiente_geometrico, vf_flujos,
)

# Valores iniciales verosímiles: reemplázalos por los datos reales de cada entidad,
# con su fuente y fecha de consulta.
DEFAULTS = {
    "c1": dict(cap=20_000_000.0, meses=12, cdt_tipo=TASA_NOM_V, cdt_val=9.5, cdt_per="Mensual",
               ah_ea=6.0, ret=4.0, infl=5.5, pts=3.0,
               fuente="COMPLETAR: entidades, productos y enlaces", fecha="COMPLETAR: fecha de consulta"),
    "c2": dict(cap=60_000_000.0, anios=5.0,
               a_nombre="Oferta A", a_tipo=TASA_NOM_V, a_val=17.5, a_per="Mensual",
               b_nombre="Oferta B", b_tipo="Nominal anticipada", b_val=16.5, b_per="Mensual",
               fuente="COMPLETAR: entidades, simuladores y enlaces", fecha="COMPLETAR: fecha de consulta"),
    "c3": dict(meta=30_000_000.0, meses=36, ea=8.0, grad="Aritmético", g_arit=10_000.0, g_geom=1.0,
               fuente="COMPLETAR: entidad y producto de ahorro", fecha="COMPLETAR: fecha de consulta"),
}


def calcular_caso1(p):
    t = p["meses"] / 12
    m = PERIODICIDADES[p["cdt_per"]]
    ea_cdt = a_efectiva_anual(p["cdt_tipo"], p["cdt_val"] / 100, m)
    ret = p["ret"] / 100
    opciones = [
        ("CDT", ea_cdt),
        ("Cuenta de ahorros", p["ah_ea"] / 100),
        ("Inversión inflación + puntos", tasa_combinada(p["infl"] / 100, p["pts"] / 100)),
    ]
    prods = []
    for nombre, ea in opciones:
        bruto = p["cap"] * ((1 + ea) ** t - 1)
        prods.append(dict(nombre=nombre, ea=ea, ea_neta=ea_neta(ea, ret, t), bruto=bruto,
                          retencion=bruto * ret, neto=bruto * (1 - ret), vf=p["cap"] + bruto * (1 - ret)))
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
    return dict(ea=ea, i=i, n=n, tabla=t, cuota=t["Cuota"].iloc[0],
                intereses=t["Intereses"].sum(), total=t["Cuota"].sum())


def calcular_caso2(p):
    a = _oferta(p["cap"], p["anios"], p["a_tipo"], p["a_val"], p["a_per"])
    b = _oferta(p["cap"], p["anios"], p["b_tipo"], p["b_val"], p["b_per"])
    a["nombre"], b["nombre"] = p["a_nombre"], p["b_nombre"]
    mejor = a if a["total"] <= b["total"] else b
    peor = b if mejor is a else a
    ac = tabla_abono_constante(p["cap"], mejor["i"], mejor["n"])
    return dict(a=a, b=b, mejor=mejor, peor=peor, ahorro=peor["total"] - mejor["total"],
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
         "Decisión recomendada": f"Tomar {m2['nombre']}: ahorra ${r2['ahorro']:,.0f} frente a la otra oferta."},
        {"Caso": "3. Plan de ahorro", "Producto o inversión": f"Ahorro con gradiente {params['c3']['grad'].lower()}",
         "Tasa efectiva anual": f"{params['c3']['ea']:.2f}%",
         "Valor total recibido / pagado": f"${r3['total']:,.0f} aportados",
         "Decisión recomendada": f"Empezar con ${r3['a1']:,.0f} frente a ${r3['cuota_unif']:,.0f} de la cuota uniforme."},
    ])