# -*- coding: utf-8 -*-
import os
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

_USER     = "postgres"
_PASSWORD = "admin123"
_HOST     = "localhost"
_PORT     = "5432"
_DBNAME   = "dw_instagram"

DATABASE_URL = f"postgresql+psycopg2://{_USER}:{_PASSWORD}@{_HOST}:{_PORT}/{_DBNAME}"


def _connect_args():
    return {
        "user":     _USER,
        "password": _PASSWORD,
        "host":     _HOST,
        "port":     _PORT,
        "dbname":   _DBNAME,
        "options":  "-c client_encoding=utf8",
    }


def get_engine():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"options": "-c client_encoding=utf8"},
    )


def test_connection() -> bool:
    try:
        conn = psycopg2.connect(**_connect_args())
        conn.close()
        return True
    except Exception:
        return False


def init_db():
    try:
        conn = psycopg2.connect(**_connect_args())
        conn.close()
    except Exception:
        pass


def list_tables() -> list[str]:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
            )
            return [row[0] for row in result]
    except Exception:
        return []