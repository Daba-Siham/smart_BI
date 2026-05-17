# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY introuvable dans le fichier .env")

        _client = Groq(api_key=api_key)

    return _client


def _df_summary(df: pd.DataFrame, max_rows: int = 5) -> str:
    shape = f"{df.shape[0]} lignes x {df.shape[1]} colonnes"
    cols = ", ".join(df.columns.tolist())
    stats = df.describe(include="all").to_string()
    sample = df.head(max_rows).to_string(index=False)
    return (
        f"Dimensions : {shape}\n"
        f"Colonnes : {cols}\n\n"
        f"Statistiques :\n{stats}\n\n"
        f"Apercu ({max_rows} lignes) :\n{sample}"
    )


def _call_groq(prompt: str, max_tokens: int = 800) -> str:
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur Groq : {e}"


def _call_groq_with_system(system: str, messages: list, max_tokens: int = 800) -> str:
    try:
        client = _get_client()
        all_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=max_tokens,
            messages=all_messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur Groq : {e}"


def analyze_table(df: pd.DataFrame) -> str:
    summary = _df_summary(df)
    prompt = (
        "Tu es un expert en Data Analysis et Business Intelligence.\n"
        "Analyse ce dataset et fournis une reponse structuree en markdown avec :\n"
        "1. **Resume general** - decris les donnees en 2-3 phrases.\n"
        "2. **Points cles** - 3 a 5 insights importants.\n"
        "3. **Qualite des donnees** - valeurs manquantes, anomalies.\n"
        "4. **Recommandations** - actions suggeres.\n\n"
        f"Donnees :\n{summary}"
    )
    return _call_groq(prompt)


def explain_chart(df: pd.DataFrame, column: str, chart_type: str = "line") -> str:
    series = df[column].dropna()
    stats = {
        "min": float(series.min()),
        "max": float(series.max()),
        "mean": round(float(series.mean()), 2),
        "std": round(float(series.std()), 2),
    }
    prompt = (
        f"Tu es un analyste BI. Explique en 3-4 phrases ce que montre ce graphique {chart_type} "
        f"pour la colonne {column}.\n"
        f"Statistiques : {json.dumps(stats)}\n"
        f"Premieres valeurs : {series.head(10).tolist()}\n"
        "Reponds en francais, de facon concise et professionnelle."
    )
    return _call_groq(prompt, max_tokens=300)


def explain_table_info(df: pd.DataFrame) -> str:
    cols_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = int(df[col].isnull().sum())
        uniq = int(df[col].nunique())
        cols_info.append(f"- {col} ({dtype}) : {uniq} valeurs uniques, {nulls} valeurs manquantes")

    cols_text = "\n".join(cols_info)
    prompt = (
        "Tu es un expert en donnees. Explique en francais ce que represente cette table "
        "de facon claire et accessible pour un manager non-technique.\n\n"
        f"Structure ({df.shape[0]} lignes, {df.shape[1]} colonnes) :\n{cols_text}\n\n"
        "Donne une description globale puis explique chaque colonne brievement. "
        "Max 200 mots. Utilise le markdown."
    )
    return _call_groq(prompt, max_tokens=500)


def chat_with_data(question: str, df: pd.DataFrame, history: list = None) -> str:
    summary = _df_summary(df, max_rows=8)
    system = (
        "Tu es un assistant BI expert. Tu reponds aux questions sur des donnees en francais.\n"
        "Tu as acces au resume d'un dataset. Effectue les calculs demandes quand possible.\n"
        "Reponds de facon structuree en markdown avec des chiffres precis.\n\n"
        f"Contexte du dataset :\n{summary}"
    )

    messages = []
    if history:
        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})

    messages.append({"role": "user", "content": question})
    return _call_groq_with_system(system, messages)