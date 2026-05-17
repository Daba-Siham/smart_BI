# -*- coding: utf-8 -*-
import os
os.environ["PYTHONUTF8"] = "1"

import re
import io
import pandas as pd
import streamlit as st
from sqlalchemy import text

from database.connection import (
    DATABASE_URL, get_engine, init_db, list_tables, test_connection
)
from etl.loader import load_csv_to_postgres
from llm.groq_client import (
    analyze_table, chat_with_data, explain_chart, explain_table_info
)
from utils.charts import bar_chart, correlation_heatmap, histogram, line_chart

st.set_page_config(
    page_title="Smart BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.main { background: #0f172a; }
div[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
}
button[data-baseweb="tab"] { font-weight: 600; font-size: 14px; }
div[data-testid="stAlert"] { border-radius: 8px; }
code { font-family: 'JetBrains Mono', monospace; font-size: 13px; }
details > summary { font-weight: 600; color: #94a3b8; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

init_db()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# SIDEBAR
with st.sidebar:
    st.markdown("## Smart BI")
    st.markdown("---")

    db_ok = test_connection()
    if db_ok:
        st.success("Base de donnees PostgreSQL connectee")
    else:
        st.error("Base de donnees PostgreSQL inaccessible")
        st.info("Verifiez les parametres de connexion PostgreSQL")
        st.stop()

    st.markdown("---")
    st.markdown("### Ajouter et stocker des donnees")
    uploaded_files = st.file_uploader(
        "Importer vos fichiers CSV dans PostgreSQL",
        type=["csv"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for file in uploaded_files:
            table_name = re.sub(r"[^a-zA-Z0-9_]", "_", file.name.split(".")[0].lower())
            buffer = io.StringIO(file.getvalue().decode("utf-8"))
            with st.spinner(f"Ajout et stockage de {table_name} dans PostgreSQL..."):
                success, msg = load_csv_to_postgres(buffer, table_name, DATABASE_URL)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown("---")
    st.caption("Powered by Groq API")

tables = list_tables()

tab_dashboard, tab_chat = st.tabs(["Dashboard", "Chat IA"])

# TAB 1 - DASHBOARD
with tab_dashboard:
    st.header("Dashboard analytique")

    if not tables:
        st.info("Aucune table. Importez un CSV depuis la barre laterale.")
        st.stop()

    col_sel, col_rows = st.columns([3, 1])
    with col_sel:
        table = st.selectbox("Table a analyser", tables)
    with col_rows:
        row_limit = st.number_input("Lignes max", min_value=50, max_value=5000, value=500, step=50)

    engine = get_engine()
    df = pd.read_sql(f'SELECT * FROM "{table}" LIMIT {row_limit}', engine)

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # KPIs
    st.markdown("### Indicateurs cles")
    n_kpi = min(4, max(2, len(num_cols) + 2))
    kpi_cols = st.columns(n_kpi)
    kpi_cols[0].metric("Lignes", f"{df.shape[0]:,}")
    kpi_cols[1].metric("Colonnes", df.shape[1])
    if num_cols and n_kpi > 2:
        kpi_cols[2].metric(f"Total {num_cols[0]}", f"{df[num_cols[0]].sum():,.2f}")
    if len(num_cols) > 1 and n_kpi > 3:
        kpi_cols[3].metric(f"Moyenne {num_cols[1]}", f"{df[num_cols[1]].mean():,.2f}")

    st.markdown("---")

    # Explication de la table
    st.markdown("### Informations sur la table")
    with st.expander("Que represente cette table ? (explication IA)", expanded=True):
        with st.spinner("Analyse de la structure..."):
            try:
                table_explanation = explain_table_info(df)
                st.markdown(table_explanation)
            except Exception as e:
                st.error(f"Erreur IA : {e}")

    # Apercu
    with st.expander("Apercu des donnees brutes", expanded=False):
        st.dataframe(df, use_container_width=True)
        st.caption(f"Affichage de {len(df):,} lignes.")

    # Statistiques
    with st.expander("Statistiques descriptives", expanded=False):
        st.dataframe(df.describe(include="all").T, use_container_width=True)
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            st.warning(f"Valeurs manquantes dans : {', '.join(missing.index.tolist())}")
        else:
            st.success("Aucune valeur manquante detectee.")

    st.markdown("---")

    # Graphiques
    st.markdown("### Visualisations")

    if not num_cols:
        st.info("Aucune colonne numerique - graphiques indisponibles.")
    else:
        for col in num_cols[:3]:
            g_col, e_col = st.columns([2, 1])
            with g_col:
                fig = line_chart(df, col)
                st.plotly_chart(fig, use_container_width=True)
            with e_col:
                st.markdown(f"#### Analyse - `{col}`")
                with st.spinner("Generation de l'explication..."):
                    try:
                        explanation = explain_chart(df, col, "line")
                        st.markdown(explanation)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        st.markdown("#### Distribution")
        hist_col = st.selectbox("Colonne pour l'histogramme", num_cols, key="hist_sel")
        g2, e2 = st.columns([2, 1])
        with g2:
            fig2 = histogram(df, hist_col)
            st.plotly_chart(fig2, use_container_width=True)
        with e2:
            st.markdown("#### Lecture du graphique")
            st.markdown(
                "Un histogramme montre la **distribution de frequence** des valeurs. "
                "Les barres les plus hautes = valeurs les plus frequentes. "
                "Un pic central = distribution normale. "
                "Plusieurs pics = plusieurs groupes dans vos donnees."
            )

        corr_fig = correlation_heatmap(df)
        if corr_fig:
            st.markdown("#### Correlations entre variables numeriques")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.plotly_chart(corr_fig, use_container_width=True)
            with c2:
                st.markdown("#### Comment lire cette carte ?")
                st.markdown(
                    "**+1 (bleu)** : les deux variables augmentent ensemble.\n\n"
                    "**-1 (rouge)** : quand l'une monte, l'autre descend.\n\n"
                    "**0 (blanc)** : pas de relation lineaire.\n\n"
                    "Correlations > 0.7 ou < -0.7 meritent attention."
                )

    st.markdown("---")

    st.markdown("### Analyse intelligente")
    if st.button("Lancer l'analyse complete", type="primary"):
        with st.spinner("Groq analyse vos donnees..."):
            try:
                analysis = analyze_table(df)
                st.markdown(analysis)
            except Exception as e:
                st.error(f"Erreur IA : {e}")

# TAB 2 - CHAT IA
with tab_chat:
    st.header("Assistant BI intelligent")

    if not tables:
        st.info("Aucune table disponible.")
        st.stop()

    chat_table = st.selectbox("Table pour la conversation", tables, key="chat_table")
    engine2 = get_engine()
    df_chat = pd.read_sql(f'SELECT * FROM "{chat_table}"', engine2)

    with st.expander("Infos sur la table selectionnee", expanded=False):
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Lignes", f"{df_chat.shape[0]:,}")
        cc2.metric("Colonnes", df_chat.shape[1])
        cc3.metric("Colonnes numeriques", len(df_chat.select_dtypes(include="number").columns))
        st.dataframe(df_chat.head(5), use_container_width=True)

    st.markdown("---")

    st.markdown("#### Questions suggerees")
    suggestions = [
        "Total de chaque colonne numerique ?",
        "Y a-t-il des valeurs aberrantes ?",
        "Quelle est la tendance generale ?",
        "Quelles colonnes sont correlees ?",
        "Resume les donnees en 5 points.",
    ]
    sugg_cols = st.columns(len(suggestions))
    for i, sugg in enumerate(suggestions):
        if sugg_cols[i].button(sugg, key=f"sugg_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": sugg})
            with st.spinner("Groq genere une reponse..."):
                try:
                    reply = chat_with_data(sugg, df_chat, st.session_state.chat_history)
                except Exception as e:
                    reply = f"Erreur : {e}"
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    st.markdown("---")

    for msg in st.session_state.chat_history:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if question := st.chat_input("Posez votre question sur les donnees..."):
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(question)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Groq analyse les donnees..."):
                try:
                    reply = chat_with_data(question, df_chat, st.session_state.chat_history)
                except Exception as e:
                    reply = f"Erreur : {e}"
            st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    if st.session_state.chat_history:
        if st.button("Effacer la conversation", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()