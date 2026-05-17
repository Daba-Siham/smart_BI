# -*- coding: utf-8 -*-
# etl/loader.py
import pandas as pd
from sqlalchemy import create_engine
from typing import Tuple


def load_csv_to_postgres(buffer, table_name: str, database_url: str) -> Tuple[bool, str]:
    """
    Load a CSV buffer into a PostgreSQL table.
    Returns (success: bool, message: str).
    """
    try:
        df = pd.read_csv(buffer)

        # Clean column names: lowercase, spaces → underscores
        df.columns = [
            col.strip().lower().replace(" ", "_").replace("-", "_")
            for col in df.columns
        ]

        engine = create_engine(database_url)
        df.to_sql(table_name, engine, if_exists="replace", index=False)

        return True, f"✅ Table **{table_name}** chargée ({len(df):,} lignes, {len(df.columns)} colonnes)"
    except Exception as e:
        return False, f"❌ Erreur lors du chargement : {e}"
