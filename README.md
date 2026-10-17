# Tablero de Ingeniería Financiera

Taller final de Ingeniería Financiera, Universidad Pontificia Bolivariana (docente: Adriana Arango L.).
Tablero interactivo en Python + Streamlit que sintetiza interés simple y compuesto, rentabilidad y
equivalencia de tasas, series uniformes, gradientes y tablas de amortización, y los aplica a tres casos
con productos financieros.

**Entrega y presentación:** jueves 29 de octubre de 2026, en el horario de clase.

## Equipo

| Integrante | Módulos a cargo |
|---|---|
| Mariana Arbeláez | Interés simple y compuesto, rentabilidad y equivalencia de tasas |
| Evelyn Jiménez | Series uniformes y gradientes |
| María Lucía Cadavid | Tablas de amortización, panel principal y consolidación de casos |

## Estructura del proyecto

```
final-ingenieria-financiera/
├── app.py                          # Panel principal: navegación, equipo y resumen de casos
├── requirements.txt                # Librerías necesarias
├── .streamlit/
│   └── config.toml                 # Tema de color del tablero
├── utils/
│   ├── __init__.py
│   ├── financial_math.py           # Todas las fórmulas del curso (sin Streamlit)
│   ├── casos.py                    # Cálculo de los tres casos aplicados y sus valores iniciales
│   └── ui.py                       # Estilos y componentes visuales compartidos
└── pages/                          # Un archivo por módulo; Streamlit los muestra en el menú
    ├── 1_Interes_Simple_y_Compuesto.py
    ├── 2_Rentabilidad_y_Tasas.py
    ├── 3_Series_y_Gradientes.py
    ├── 4_Tablas_de_Amortizacion.py
    └── 5_Casos_Aplicados.py
```

### Qué va en cada carpeta

- **`utils/financial_math.py`:** las fórmulas. Si una fórmula se usa en más de una página, va aquí.
  Las tasas siempre entran como decimal (0.025 = 2.5 %).
- **`utils/casos.py`:** la lógica de los casos. Lo comparten `pages/5_Casos_Aplicados.py` y el panel
  principal, para que ambos muestren los mismos números.
- **`utils/ui.py`:** el diseño. Cada página empieza con `setup_page(...)` y `page_header(...)`, y usa
  `kpi`, `callout`, `section`, `style_fig`, `show_plot`, `show_table` y `verification_table`.
- **`pages/`:** solo pantalla (campos de entrada, gráficos y textos). No se escriben fórmulas aquí;
  se importan de `utils/`. El número del nombre define el orden en el menú.

## Cómo ejecutarlo

```bash
python -m venv venv
source venv/bin/activate          # En Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Casos aplicados

Los datos de `utils/casos.py` son ofertas reales consultadas el 17 de octubre de 2026:

| Caso | Fuente | Datos |
|---|---|---|
| 1. Inversión | Simulador de CDT de Bancolombia; simulador de cuenta de ahorros de Davivienda | CDT a 360 días, 9.40 % EA, retención 4 %; cuenta de ahorros 0.10 % EA con cuota de manejo de $16.500 al mes |
| 2. Crédito | Bancolombia, crédito de libre inversión | Tasa fija desde 1.30 % MV (16.77 % EA); tasa variable IBR + puntos desde 15.36 % EA |
| 3. Plan de ahorro | Nu Colombia, Cajitas de ahorro | Hasta 8.25 % EA |

La alternativa "inflación + puntos" del caso 1 es un escenario de referencia, no una oferta consultada.

## Trabajo en equipo con Git

Repositorio: https://github.com/MariArbe/final-ingenieria-financiera

1. Antes de empezar a trabajar: `git pull`
2. Edita solo los archivos de tu módulo. Si necesitas tocar `financial_math.py`, `ui.py` o `app.py`,
   avisa al grupo, porque son compartidos y es donde se generan conflictos.
3. Prueba en tu computador con `streamlit run app.py`.
4. Sube tus cambios:

```bash
git add .
git commit -m "Mensaje corto de lo que cambiaste"
git pull
git push
```

Si `git pull` muestra un conflicto, no borres nada: abre el archivo, conserva ambos cambios y avisa al grupo.

## Despliegue

La app se publica en Streamlit Community Cloud desde la rama `main` con `app.py` como archivo
principal. Cada `git push` a `main` actualiza la app publicada, así que **prueba localmente antes de subir**.