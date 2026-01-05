import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Densidades en g/cm³
densidades_base = {
    "Agua": 1.00,
    "Aceite": 0.92,
    "Miel": 1.42,
    "Alcohol": 0.79
}

colores = {
    "Agua": "blue",
    "Aceite": "orange",
    "Miel": "brown",
    "Alcohol": "green"
}

# Relaciones de miscibilidad (simplificadas)
miscibilidad = {
    ("Agua", "Alcohol"): "miscibles",
    ("Agua", "Aceite"): "no miscibles",
    ("Agua", "Miel"): "miscibles",
    ("Aceite", "Alcohol"): "no miscibles",
    ("Aceite", "Miel"): "no miscibles",
    ("Alcohol", "Miel"): "miscibles"
}

st.title("Simulador de densidad y estratificación de líquidos")

# Selección de líquidos base
liquidos = st.multiselect("Selecciona líquidos a mezclar", list(densidades_base.keys()), default=["Agua","Aceite","Miel"])

vols = {}
for liq in liquidos:
    vols[liq] = st.slider(f"Volumen de {liq} (ml)", 0, 500, 100)

# Opción para agregar líquido personalizado
st.subheader("Agregar líquido personalizado")
nombre_liq = st.text_input("Nombre del líquido")
dens_liq = st.number_input("Densidad (g/cm³)", min_value=0.1, max_value=5.0, step=0.01)
vol_liq = st.slider("Volumen del líquido personalizado (ml)", 0, 500, 0)

if nombre_liq and vol_liq > 0:
    densidades_base[nombre_liq] = dens_liq
    colores[nombre_liq] = "purple"
    liquidos.append(nombre_liq)
    vols[nombre_liq] = vol_liq

# Cálculo de densidad mezcla
masa_total = sum(densidades_base[liq] * vols[liq] for liq in liquidos)
vol_total = sum(vols.values())
densidad_mezcla = masa_total / vol_total if vol_total > 0 else 0

st.metric("Densidad resultante (g/cm³)", f"{densidad_mezcla:.3f}")

# Gráfica comparativa de densidades
fig1 = go.Figure()
for liq in liquidos:
    fig1.add_trace(go.Bar(x=[liq], y=[densidades_base[liq]], name=liq, marker_color=colores.get(liq,"gray")))
fig1.add_trace(go.Bar(x=["Mezcla"], y=[densidad_mezcla], name="Mezcla", marker_color="red"))
fig1.update_layout(title="Comparación de densidades", yaxis_title="g/cm³")
st.plotly_chart(fig1, use_container_width=True)

# Estratificación en capas
st.subheader("Visualización de estratificación (torre de líquidos)")
capas = sorted([(liq, densidades_base[liq], vols[liq]) for liq in liquidos], key=lambda x: x[1], reverse=True)

fig2 = go.Figure()
altura_total = sum(v for _,_,v in capas)
y_base = 0
for liq, dens, vol in capas:
    altura = vol
    fig2.add_shape(
        type="rect",
        x0=0, x1=1,
        y0=y_base, y1=y_base+altura,
        fillcolor=colores.get(liq,"gray"),
        line=dict(color="black")
    )
    fig2.add_annotation(
        x=0.5, y=y_base+altura/2,
        text=f"{liq} ({dens:.2f} g/cm³)",
        showarrow=False, font=dict(color="white")
    )
    y_base += altura

fig2.update_yaxes(range=[0, altura_total], title="Altura proporcional al volumen (ml)")
fig2.update_xaxes(visible=False)
fig2.update_layout(title="Estratificación de líquidos (más densos abajo)")
st.plotly_chart(fig2, use_container_width=True)

# Simulación de miscibilidad
st.subheader("Simulación de miscibilidad")
pairs = [(liquidos[i], liquidos[j]) for i in range(len(liquidos)) for j in range(i+1,len(liquidos))]
for p in pairs:
    estado = miscibilidad.get(p) or miscibilidad.get((p[1],p[0])) or "desconocido"
    st.write(f"{p[0]} + {p[1]} → {estado}")

# Exportar resultados
st.subheader("Exportar resultados")
df_export = pd.DataFrame({
    "Liquido": [liq for liq in liquidos],
    "Volumen_ml": [vols[liq] for liq in liquidos],
    "Densidad_gcm3": [densidades_base[liq] for liq in liquidos]
})
df_export.loc[len(df_export)] = ["Mezcla", vol_total, densidad_mezcla]

buf = io.BytesIO()
df_export.to_csv(buf, index=False)
buf.seek(0)
st.download_button("Descargar CSV", data=buf, file_name="mezcla_liquidos.csv", mime="text/csv")
