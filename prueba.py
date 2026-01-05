import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io

densidades_base = {
    "Agua": 1.00,
    "Aceite": 0.92,
    "Miel": 1.42,
    "Alcohol": 0.79
}

liquidos = st.multiselect("Selecciona líquidos a mezclar", list(densidades_base.keys()), default=["Agua","Aceite","Miel"])
vols = {}
for liq in liquidos:
    vols[liq] = st.slider(f"Volumen de {liq} (ml)", 0, 500, 100)

masa_total = sum(densidades_base[liq] * vols[liq] for liq in liquidos)
vol_total = sum(vols.values())
densidad_mezcla = masa_total / vol_total if vol_total > 0 else 0