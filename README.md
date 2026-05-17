# 🚀 Smart BI – Business Intelligence avec Groq AI

Application Streamlit professionnelle d'analyse de données alimentée par **Groq API**.

## Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 📂 Import CSV | Glissez vos fichiers → chargés automatiquement en PostgreSQL |
| 🗃️ Explication de table | LLM explique la structure et le contenu de vos données |
| 📊 Graphiques interactifs | Lignes, histogrammes, corrélations (Plotly) |
| 💡 Explication des graphes | Chaque graphique est accompagné d'une analyse IA |
| 🧠 Analyse complète | Rapport IA complet sur vos données |
| 💬 Chat IA | Posez des questions en langage naturel, obtenez des réponses précises |
| 🔄 Historique de conversation | Le chat garde le contexte des échanges précédents |

## Installation

### 1. Cloner et configurer

```bash
git clone <repo>
cd smart_bi
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditez .env et renseignez GROQ_API_KEY et DATABASE_URL
```

### 3. Démarrer PostgreSQL

```bash
# Avec Docker (recommandé)
docker run -d \
  --name smartbi-pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=smartbi \
  -p 5432:5432 \
  postgres:16
```

### 4. Lancer l'application

```bash
streamlit run app.py
```

## Structure du projet

```
smart_bi/
├── app.py                  # Point d'entrée Streamlit
├── requirements.txt        # Dépendances Python
├── .env.example            # Template de configuration
├── database/
│   ├── __init__.py
│   └── connection.py       # Connexion SQLAlchemy / PostgreSQL
├── etl/
│   ├── __init__.py
│   └── loader.py           # Chargement CSV → PostgreSQL
├── llm/
│   ├── __init__.py
│   └── groq_client.py    # Client Anthropic groq API
└── utils/
    ├── __init__.py
    └── charts.py           # Graphiques Plotly stylisés
```

## Obtenir une clé API Groq

1. Créez un compte sur [console.groq.com](https://console.groq.com)
2. Allez dans **API Keys** → **Create Key**
3. Copiez la clé dans votre `.env`

## Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `GROQ_API_KEY` | Clé API Groq **(obligatoire)** | — |
| `DATABASE_URL` | URL PostgreSQL | `postgresql://postgres:postgres@localhost:5432/smartbi` |
