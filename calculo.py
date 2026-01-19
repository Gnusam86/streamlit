import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)

# =============================
# CONFIGURACIÓN GENERAL
# =============================
st.set_page_config(
    page_title="Cálculo Visual con Python",
    layout="wide",
    page_icon="📘"
)

st.markdown(
    "<h1 style='text-align:center;'>📘 Simulador Visual Para el Aprendizaje de Cálculo</h1>"
    "<p style='text-align:center;'>Explora Funciones, Derivadas e Integrales de forma interactiva</p>",
    unsafe_allow_html=True
)

# =============================
# PARSER ROBUSTO
# =============================
X = sp.Symbol("x")

TRANSFORMATIONS = (
    standard_transformations +
    (implicit_multiplication_application, convert_xor)
)

SAFE_FUNCTIONS = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "exp": sp.exp, "ln": sp.log, "log": sp.log,
    "sqrt": sp.sqrt, "abs": sp.Abs, "pi": sp.pi, "e": sp.E
}

def limpiar_entrada(expr: str) -> str:
    expr = expr.lower().strip()
    reemplazos = {"sen": "sin", "π": "pi", "^": "**", "|x|": "abs(x)"}
    for k, v in reemplazos.items():
        expr = expr.replace(k, v)
    return expr

def parsear_funcion(expr_str: str):
    try:
        expr = parse_expr(
            expr_str,
            local_dict=SAFE_FUNCTIONS | {"x": X},
            transformations=TRANSFORMATIONS,
            evaluate=True
        )
        if not expr.has(X) and not expr.is_number:
            raise ValueError("La función debe depender de x")
        return expr, None
    except Exception as e:
        return None, str(e)

def lambdify_seguro(expr):
    try:
        f = sp.lambdify(X, expr, modules=["numpy"])
        def wrapper(x):
            try:
                y = f(x)
                y = np.array(y, dtype=float)
                if y.shape == (): y = np.full_like(x, y) # Manejar funciones constantes
                y[~np.isfinite(y)] = np.nan
                return y
            except:
                return np.full_like(x, np.nan)
        return wrapper
    except:
        return None

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.header("⚙ Configuración")

    raw_input = st.text_input(
        "Ingresa f(x):",
        value="x^2 - 4",
        help="Ejemplos: x^2, sin(x), exp(x), ln(x)"
    )

    col_x1, col_x2 = st.columns(2)
    xmin = col_x1.number_input("x min", value=-6.0)
    xmax = col_x2.number_input("x max", value=6.0)

    st.markdown("---")
    show_f = st.checkbox("Mostrar f(x)", True)
    show_d = st.checkbox("Mostrar derivada f'(x)", True)
    show_area = st.checkbox("Visualizar Área Bajo la Curva", False)

    if show_area:
        st.subheader("Rango de Integración")
        a_b = st.slider("Intervalo [a, b]", float(xmin), float(xmax), (0.0, 3.0))
        a_int, b_int = a_b

    st.markdown("---")
    x0 = st.slider("Punto x₀ (Tangente)", float(xmin), float(xmax), float((xmin + xmax) / 4))

resolution = 1000
# =============================
# PROCESAMIENTO MATEMÁTICO
# =============================
expr_limpia = limpiar_entrada(raw_input)
f_sym, error = parsear_funcion(expr_limpia)

if error:
    st.error(f"❌ Error: {error}")
    st.stop()

f = lambdify_seguro(f_sym)
xs = np.linspace(xmin, xmax, resolution)
ys = f(xs)

# Derivada
try:
    d_sym = sp.diff(f_sym, X)
    df = lambdify_seguro(d_sym)
except:
    d_sym, df = None, None

# =============================
# CONSTRUCCIÓN DE GRÁFICA (PLOTLY)
# =============================
fig = go.Figure()

# 1. Área bajo la curva (se dibuja primero para quedar al fondo)
if show_area:
    x_fill = np.linspace(a_int, b_int, 400)
    y_fill = f(x_fill)
    fig.add_trace(go.Scatter(
        x=x_fill, y=y_fill,
        fill='tozeroy',
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(0, 150, 255, 0.3)',
        name='Área Definida',
        hoverinfo='skip'
    ))

# 2. Función principal
if show_f:
    fig.add_trace(go.Scatter(x=xs, y=ys, name="f(x)", line=dict(width=4, color='#1f77b4')))

# 3. Derivada
if show_d and df:
    fig.add_trace(go.Scatter(x=xs, y=df(xs), name="f'(x)", line=dict(color="red", dash="dash", width=2)))

# 4. Línea de Tangente en x0
if df:
    y0 = f(np.array([x0]))[0]
    slope = df(np.array([x0]))[0]
    # Dibujar una línea corta de tangente
    t_range = (xmax - xmin) * 0.1
    xt = np.linspace(x0 - t_range, x0 + t_range, 100)
    yt = slope * (xt - x0) + y0
    fig.add_trace(go.Scatter(x=xt, y=yt, name="Tangente", line=dict(color="orange", width=3)))
    fig.add_trace(go.Scatter(x=[x0], y=[y0], mode="markers", marker=dict(size=12, color="orange"), name="Punto x₀"))

# Estética de la gráfica
fig.update_layout(
    height=600,
    template="plotly_white",
    hovermode="x unified",
    xaxis=dict(title="Eje X", zeroline=True, zerolinewidth=2, zerolinecolor='black'),
    yaxis=dict(title="Eje Y", zeroline=True, zerolinewidth=2, zerolinecolor='black'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# PANEL DE RESULTADOS
# =============================
col_math, col_res = st.columns([1, 1])

with col_math:
    with st.expander("📐 Análisis Simbólico", expanded=True):
        st.latex(r"f(x) = " + sp.latex(f_sym))
        if d_sym:
            st.latex(r"f'(x) = " + sp.latex(d_sym))

with col_res:
    if show_area:
        with st.expander("🧮 Cálculo de Integral", expanded=True):
            try:
                area_val = sp.integrate(f_sym, (X, a_int, b_int))
                st.latex(r"\int_{" + f"{a_int:.2f}" + r"}^{" + f"{b_int:.2f}" + r"} f(x) dx")
                st.metric("Resultado del Área", f"{float(area_val):.4f}")
            except:
                st.warning("No se pudo calcular la integral exacta.")