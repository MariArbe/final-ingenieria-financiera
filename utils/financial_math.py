"""Fórmulas financieras centralizadas del curso.

Convención: todas las tasas entran como decimal (0.025 = 2.5 %).
"""
import math

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constantes compartidas por las páginas
# ---------------------------------------------------------------------------
TASA_EA = "Efectiva anual (EA)"
TASA_NOM_V = "Nominal vencida"
TASA_NOM_A = "Nominal anticipada"
TASA_PER_V = "Periódica vencida"
TASA_PER_A = "Periódica anticipada"
TIPOS_TASA = [TASA_EA, TASA_NOM_V, TASA_NOM_A, TASA_PER_V, TASA_PER_A]

# Periodos por año
PERIODICIDADES = {
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Cuatrimestral": 3,
    "Semestral": 2,
    "Anual": 1,
}

# ---------------------------------------------------------------------------
# INTERÉS SIMPLE Y COMPUESTO
# (si ya tenías estas cuatro, conserva las tuyas; deben devolver lo mismo)
# ---------------------------------------------------------------------------
def interes_simple(capital, tasa, n, convencion="30/360"):
    """VF = C(1 + i·n). Devuelve (valor_futuro, interes).
    `convencion` queda registrada en los supuestos; con tasa periódica y
    periodos enteros no altera el resultado."""
    interes = capital * tasa * n
    return capital + interes, interes


def interes_compuesto(capital, tasa, n):
    """VF = C(1 + i)^n. Devuelve (valor_futuro, interes)."""
    vf = capital * (1 + tasa) ** n
    return vf, vf - capital


def despejar_tasa_compuesto(capital, vf, n):
    return (vf / capital) ** (1 / n) - 1


def despejar_plazo_compuesto(capital, vf, tasa):
    return math.log(vf / capital) / math.log(1 + tasa)


# ---------------------------------------------------------------------------
# NUEVAS: simple y compuesto
# ---------------------------------------------------------------------------
def valor_presente_simple(vf, tasa, n):
    return vf / (1 + tasa * n)


def valor_presente_compuesto(vf, tasa, n):
    return vf / (1 + tasa) ** n


def despejar_tasa_simple(capital, vf, n):
    return (vf / capital - 1) / n


def despejar_plazo_simple(capital, vf, tasa):
    return (vf / capital - 1) / tasa


# ---------------------------------------------------------------------------
# NUEVAS: equivalencia de tasas
# ---------------------------------------------------------------------------
def anticipada_a_vencida(ia):
    """i_v = i_a / (1 − i_a)  (misma periodicidad)."""
    if ia >= 1:
        raise ValueError("La tasa anticipada periódica debe ser menor a 100 %.")
    return ia / (1 - ia)


def vencida_a_anticipada(iv):
    """i_a = i_v / (1 + i_v)  (misma periodicidad)."""
    return iv / (1 + iv)


def a_efectiva_anual(tipo, valor, m):
    """Convierte cualquier tipo de tasa a EA. `m` = periodos por año."""
    if tipo == TASA_EA:
        return valor
    if tipo == TASA_NOM_V:
        return (1 + valor / m) ** m - 1
    if tipo == TASA_PER_V:
        return (1 + valor) ** m - 1
    if tipo == TASA_NOM_A:
        return (1 + anticipada_a_vencida(valor / m)) ** m - 1
    if tipo == TASA_PER_A:
        return (1 + anticipada_a_vencida(valor)) ** m - 1
    raise ValueError(f"Tipo de tasa desconocido: {tipo}")


def desde_efectiva_anual(ea, m):
    """Devuelve las tasas equivalentes a una EA para m periodos por año."""
    iv = (1 + ea) ** (1 / m) - 1
    ia = vencida_a_anticipada(iv)
    return {
        "periodica_vencida": iv,
        "nominal_vencida": iv * m,
        "periodica_anticipada": ia,
        "nominal_anticipada": ia * m,
    }


def tasa_combinada(inflacion, puntos):
    """(1 + inflación)(1 + puntos) − 1."""
    return (1 + inflacion) * (1 + puntos) - 1


def inflacion_de_equilibrio(tasa_fija, puntos):
    """Inflación a la que 'inflación + puntos' iguala a una tasa fija."""
    return (1 + tasa_fija) / (1 + puntos) - 1


def ea_neta(ea, retencion, anios=1.0):
    """EA neta cuando la retención se aplica sobre los intereses al vencimiento.
    VF_neto/C = 1 + ((1+EA)^t − 1)(1 − ret);  EA_neta = (VF_neto/C)^(1/t) − 1."""
    factor = 1 + ((1 + ea) ** anios - 1) * (1 - retencion)
    return factor ** (1 / anios) - 1


# ---------------------------------------------------------------------------
# SERIES UNIFORMES (vencidas y anticipadas)
# ---------------------------------------------------------------------------
def factor_vp_serie(i, n):
    """a(n,i) = (1 − (1+i)^−n) / i   (serie vencida)."""
    return n if i == 0 else (1 - (1 + i) ** -n) / i


def factor_vf_serie(i, n):
    """s(n,i) = ((1+i)^n − 1) / i   (serie vencida)."""
    return n if i == 0 else ((1 + i) ** n - 1) / i


def vp_serie(cuota, i, n, anticipada=False):
    vp = cuota * factor_vp_serie(i, n)
    return vp * (1 + i) if anticipada else vp


def vf_serie(cuota, i, n, anticipada=False):
    vf = cuota * factor_vf_serie(i, n)
    return vf * (1 + i) if anticipada else vf


def cuota_desde_vp(vp, i, n, anticipada=False):
    cuota = vp / factor_vp_serie(i, n)
    return cuota / (1 + i) if anticipada else cuota


def cuota_desde_vf(vf, i, n, anticipada=False):
    cuota = vf / factor_vf_serie(i, n)
    return cuota / (1 + i) if anticipada else cuota


# ---------------------------------------------------------------------------
# GRADIENTES (flujos vencidos: la primera cuota cae al final del periodo 1)
# ---------------------------------------------------------------------------
def flujos_gradiente_aritmetico(a1, g, n):
    """A_k = A1 + (k−1)·G"""
    return np.array([a1 + g * k for k in range(int(n))], dtype=float)


def flujos_gradiente_geometrico(a1, g, n):
    """A_k = A1·(1+g)^(k−1)"""
    return np.array([a1 * (1 + g) ** k for k in range(int(n))], dtype=float)


def vp_flujos(flujos, i):
    return float(sum(f / (1 + i) ** (k + 1) for k, f in enumerate(flujos)))


def vf_flujos(flujos, i):
    n = len(flujos)
    return float(sum(f * (1 + i) ** (n - k - 1) for k, f in enumerate(flujos)))


def vp_gradiente_aritmetico_formula(a1, g, n, i):
    a = factor_vp_serie(i, n)
    return a1 * a + (g / i) * (a - n / (1 + i) ** n)


def vp_gradiente_geometrico_formula(a1, g, n, i):
    if abs(i - g) < 1e-12:
        return n * a1 / (1 + i)
    return a1 * (1 - ((1 + g) / (1 + i)) ** n) / (i - g)


# ---------------------------------------------------------------------------
# AMORTIZACIÓN
# ---------------------------------------------------------------------------
def cuota_fija(capital, i, n):
    return capital / factor_vp_serie(i, n)


def tabla_cuota_fija(capital, i, n):
    cuota = cuota_fija(capital, i, n)
    saldo, filas = capital, []
    for k in range(1, int(n) + 1):
        interes = saldo * i
        abono = cuota - interes
        saldo -= abono
        filas.append((k, cuota, interes, abono, saldo))
    return pd.DataFrame(filas, columns=["Periodo", "Cuota", "Intereses", "Abono a capital", "Saldo"])


def tabla_abono_constante(capital, i, n):
    abono = capital / n
    saldo, filas = capital, []
    for k in range(1, int(n) + 1):
        interes = saldo * i
        saldo -= abono
        filas.append((k, abono + interes, interes, abono, saldo))
    return pd.DataFrame(filas, columns=["Periodo", "Cuota", "Intereses", "Abono a capital", "Saldo"])

# ---------------------------------------------------------------------------
# AMORTIZACIÓN CON ABONOS EXTRAORDINARIOS Y REFINANCIACIÓN
# ---------------------------------------------------------------------------
SIS_CUOTA_FIJA = "Cuota fija"
SIS_ABONO_CONSTANTE = "Abono constante a capital"
SISTEMAS_AMORTIZACION = [SIS_CUOTA_FIJA, SIS_ABONO_CONSTANTE]

ABONO_REDUCE_PLAZO = "Reducir plazo"
ABONO_REDUCE_CUOTA = "Reducir cuota"

COLUMNAS_TABLA = ["Periodo", "Tasa periódica", "Cuota", "Intereses", "Abono a capital",
                  "Abono extra", "Pago total", "Saldo"]


def cuotas_pendientes(saldo, i, sistema, cuota=None, abono=None):
    """Número de cuotas que faltan para extinguir `saldo` con la cuota (cuota fija)
    o el abono a capital (abono constante) vigentes."""
    if saldo <= 0:
        return 0
    if sistema == SIS_ABONO_CONSTANTE:
        return math.ceil(saldo / abono - 1e-9)
    if i == 0:
        return math.ceil(saldo / cuota - 1e-9)
    # n = −ln(1 − S·i/A) / ln(1 + i)
    return math.ceil(-math.log(1 - saldo * i / cuota) / math.log(1 + i) - 1e-9)


def tabla_amortizacion(capital, i, n, sistema=SIS_CUOTA_FIJA, abonos_extra=None,
                       modo_abono=ABONO_REDUCE_PLAZO, refinanciacion=None):
    """Tabla de amortización con abonos extraordinarios y una refinanciación opcional.

    - `abonos_extra`: {periodo: monto}. Se paga al final del periodo, junto con la cuota,
      y va completo a capital (si supera el saldo, se limita al saldo).
    - `modo_abono`: tras un abono extra, "Reducir plazo" mantiene la cuota (cuota fija) o el
      abono a capital (abono constante) y el crédito termina antes; "Reducir cuota" mantiene
      el plazo y recalcula la cuota sobre el nuevo saldo.
    - `refinanciacion`: {"periodo": k, "tasa": i_nueva, "cuotas": r}. Después de pagar la
      cuota k (y su abono extra), el saldo se reprograma a la nueva tasa periódica en r
      cuotas. Si `cuotas` es None se conservan las cuotas que faltaban.
    """
    abonos_extra = {int(k): float(v) for k, v in (abonos_extra or {}).items() if v and v > 0}
    eps = 1e-9 * max(abs(capital), 1.0)

    saldo, tasa, n_plan = float(capital), float(i), int(n)
    cuota = cuota_fija(saldo, tasa, n_plan)
    abono_k = saldo / n_plan
    filas, k = [], 0

    while saldo > eps and k < n_plan:
        k += 1
        interes = saldo * tasa
        abono = (cuota - interes) if sistema == SIS_CUOTA_FIJA else abono_k
        abono = min(abono, saldo)          # la última cuota solo paga lo que se debe
        saldo -= abono
        extra = min(abonos_extra.get(k, 0.0), saldo)
        saldo -= extra
        filas.append((k, tasa, interes + abono, interes, abono, extra, interes + abono + extra, saldo))

        if saldo <= eps:
            break
        if extra > 0 and modo_abono == ABONO_REDUCE_CUOTA:
            restantes = n_plan - k
            cuota = cuota_fija(saldo, tasa, restantes)
            abono_k = saldo / restantes
        if refinanciacion and k == int(refinanciacion["periodo"]):
            r = refinanciacion.get("cuotas")
            if not r:
                r = cuotas_pendientes(saldo, tasa, sistema, cuota, abono_k)
            r = int(r)
            tasa = float(refinanciacion["tasa"])
            n_plan = k + r
            cuota = cuota_fija(saldo, tasa, r)
            abono_k = saldo / r

    return pd.DataFrame(filas, columns=COLUMNAS_TABLA)


def vp_pagos_tabla(df, columna="Pago total"):
    """VP de los pagos de una tabla descontando con la tasa de cada periodo
    (sirve aunque la tasa cambie por una refinanciación)."""
    factores = np.cumprod(1 + df["Tasa periódica"].to_numpy())
    return float((df[columna].to_numpy() / factores).sum())


# ---------------------------------------------------------------------------
# INFLACIÓN: PESOS CONSTANTES Y TASA REAL
# ---------------------------------------------------------------------------
def tasa_real(i_nominal, inflacion):
    """Fisher: (1 + i) = (1 + r)(1 + π)  →  r = (1 + i)/(1 + π) − 1 (misma periodicidad)."""
    return (1 + i_nominal) / (1 + inflacion) - 1


def deflactar_tabla(df, inflacion_periodica):
    """Expresa los pagos y el saldo de una tabla en pesos de hoy (periodo 0)."""
    factor = (1 + inflacion_periodica) ** df["Periodo"].to_numpy()
    return pd.DataFrame({
        "Periodo": df["Periodo"],
        "Pago nominal": df["Pago total"],
        "Pago en pesos de hoy": df["Pago total"] / factor,
        "Saldo nominal": df["Saldo"],
        "Saldo en pesos de hoy": df["Saldo"] / factor,
    })
