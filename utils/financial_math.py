"""Fórmulas financieras centralizadas del curso.

Convención: todas las tasas entran como decimal (0.025 = 2.5 %).
"""
import math

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