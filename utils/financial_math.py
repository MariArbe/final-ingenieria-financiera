import numpy as np

# --- MÓDULO 2 Y 3: INTERÉS SIMPLE Y COMPUESTO ---
def interes_simple(C, i, n):
    vf = C * (1 + i * n)
    interes = vf - C
    return vf, interes

def interes_compuesto(C, i, n):
    vf = C * ((1 + i) ** n)
    interes = vf - C
    return vf, interes

def despejar_tasa_compuesto(C, vf, n):
    if C <= 0 or n <= 0:
        return 0
    return ((vf / C) ** (1 / n)) - 1

def despejar_plazo_compuesto(C, vf, i):
    if C <= 0 or i <= 0:
        return 0
    return np.log(vf / C) / np.log(1 + i)


# --- MÓDULO 4: RENTABILIDAD Y EQUIVALENCIA DE TASAS ---
def nominal_a_efectiva(j, m, n_per=1):
    ef = (1 + j / m) ** m - 1
    return ef

def efectiva_a_nominal(ef, m, freq=1):
    j = m * ((1 + ef) ** (1 / m) - 1)
    return j

def vencida_a_anticipada(i_v):
    return i_v / (1 + i_v)

def anticipada_a_vencida(i_a):
    return i_a / (1 - i_a)

def tasa_combinada(inflacion, puntos):
    return (1 + inflacion) * (1 + puntos) - 1

def rentabilidad_neta(tea, retencion):
    return tea * (1 - retencion)
