# Transparencia Presupuestaria – Provincia de Santa Cruz (MVP)

Web app gratuita para mostrar la ejecución presupuestaria acumulada,
orientada a la ciudadanía.

## Características
- Métrica por defecto: Devengado Consumido
- Ejecución acumulada (sin vista mensual)
- Gráfico de árbol (Treemap) con bajada hasta SAF
- Ranking y detalle descargables
- Compatible con PC y celular (iPhone / Android)

## Archivos necesarios
- transparencia_sc_app_v2.py
- requirements_transparencia_sc_v2.txt
- cr_30_12_25_1_12.xlsx (o el Excel actualizado)

## Ejecución local
```bash
pip install -r requirements_transparencia_sc_v2.txt
streamlit run transparencia_sc_app_v2.py
```

## Publicación sin costo
Recomendado: Streamlit Community Cloud
https://streamlit.io/cloud
