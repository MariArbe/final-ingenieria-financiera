"""Resumen de cada módulo para el panel principal.

Calcula el resultado clave de cada página con sus valores iniciales (EJEMPLOS). La verificación
global (utils/verificacion.py) usa estos mismos valores. Si cambias los valores iniciales de una
página, cámbialos también aquí.
"""
from utils.casos import calcular_caso1, calcular_caso2, calcular_caso3
from utils.financial_math import (
    TASA_NOM_V, PERIODICIDADES, a_efectiva_anual, desde_efectiva_anual, ea_neta,
    interes_simple, interes_compuesto, vp_serie, vf_serie, cuota_desde_vp,
    flujos_gradiente_aritmetico, vp_flujos, tabla_amortizacion, SIS_CUOTA_FIJA, SIS_ABONO_CONSTANTE,
)

# Valores iniciales de cada página (los mismos que trae cada formulario)
EJEMPLOS = {
    "interes": dict(capital=1_000_000.0, tasa=0.025, n=12),                       # mensual
    "tasas": dict(ea=0.12, m=12, infl=0.055, pts=0.04,
                  cap_ret=20_000_000.0, ea_ret=0.10, ret=0.04, meses=12),
    "series": dict(cuota=500_000.0, i=0.015, n=24, a1=300_000.0, g=20_000.0, ig=0.015, ng=24),
    "amort": dict(capital=50_000_000.0, tasa_nmv=0.18, m=12, anios=5, infl=0.05),
}


def resumen_interes():
    e = EJEMPLOS["interes"]
    per = list(range(e["n"] + 1))
    vf_s, int_s = interes_simple(e["capital"], e["tasa"], e["n"])
    vf_c, int_c = interes_compuesto(e["capital"], e["tasa"], e["n"])
    return dict(ej=e, vf_simple=vf_s, vf_comp=vf_c, ventaja=vf_c - vf_s, extra_pct=(int_c / int_s - 1),
                periodos=per,
                simple=[interes_simple(e["capital"], e["tasa"], p)[0] for p in per],
                comp=[interes_compuesto(e["capital"], e["tasa"], p)[0] for p in per])


def resumen_tasas():
    e = EJEMPLOS["tasas"]
    eq = desde_efectiva_anual(e["ea"], e["m"])
    nominales = [(nombre, desde_efectiva_anual(e["ea"], mm)["nominal_vencida"])
                 for nombre, mm in PERIODICIDADES.items()]
    return dict(ej=e, nominal_mensual=eq["nominal_vencida"], periodica_mensual=eq["periodica_vencida"],
                ea_neta=ea_neta(e["ea_ret"], e["ret"], e["meses"] / 12), nominales=nominales)


def resumen_series():
    e = EJEMPLOS["series"]
    vp, vf = vp_serie(e["cuota"], e["i"], e["n"]), vf_serie(e["cuota"], e["i"], e["n"])
    flujos = flujos_gradiente_aritmetico(e["a1"], e["g"], e["ng"])
    vp_g = vp_flujos(flujos, e["ig"])
    return dict(ej=e, vp=vp, vf=vf, flujos=list(flujos), cuota_eq=cuota_desde_vp(vp_g, e["ig"], e["ng"]),
                vp_gradiente=vp_g)


def resumen_amortizacion():
    e = EJEMPLOS["amort"]
    ea = a_efectiva_anual(TASA_NOM_V, e["tasa_nmv"], e["m"])
    i = (1 + ea) ** (1 / e["m"]) - 1
    n = int(round(e["anios"] * e["m"]))
    cf = tabla_amortizacion(e["capital"], i, n, SIS_CUOTA_FIJA)
    ac = tabla_amortizacion(e["capital"], i, n, SIS_ABONO_CONSTANTE)
    return dict(ej=e, ea=ea, i=i, n=n, cuota=cf["Cuota"].iloc[0], intereses_cf=cf["Intereses"].sum(),
                intereses_ac=ac["Intereses"].sum(), primera_ac=ac["Cuota"].iloc[0],
                periodos=[0] + cf["Periodo"].tolist(),
                saldo_cf=[e["capital"]] + cf["Saldo"].tolist(), saldo_ac=[e["capital"]] + ac["Saldo"].tolist())


def resumen_casos(params):
    r1, r2, r3 = calcular_caso1(params["c1"]), calcular_caso2(params["c2"]), calcular_caso3(params["c3"])
    return dict(r1=r1, r2=r2, r3=r3)
