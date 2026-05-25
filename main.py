from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    sql: str

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

ALLOWED_COMMANDS = (
    "select",
    "insert",
    "update"
)

BLOCKED_TERMS = (
    "drop ",
    "truncate ",
    "delete ",
    "alter ",
    "create ",
    "grant ",
    "revoke "
)

@app.post("/executar-sql")
def executar_sql(request: QueryRequest):

    sql_original = request.sql.strip()

    sql_lower = sql_original.lower()

    # =========================
    # VALIDACAO COMANDO
    # =========================

    if not sql_lower.startswith(ALLOWED_COMMANDS):
        return {
            "erro": "Comando SQL nao permitido"
        }

    # =========================
    # BLOQUEIO SEGURANCA
    # =========================

    for termo in BLOCKED_TERMS:
        if termo in sql_lower:
            return {
                "erro": f"Termo bloqueado detectado: {termo}"
            }

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        options="-c search_path=demo_rdn_soul_agents_trackito"
    )

    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    try:

        cur.execute(sql_original)

        # =========================
        # SELECT
        # =========================

        if sql_lower.startswith("select"):

            rows = cur.fetchall()

            return {
                "success": True,
                "rows": rows
            }

        # =========================
        # INSERT / UPDATE
        # =========================

        conn.commit()

        resultado = {
            "success": True,
            "rows_affected": cur.rowcount
        }

        # =========================
        # RETURNING
        # =========================

        try:

            returning_rows = cur.fetchall()

            resultado["returning"] = returning_rows

        except:
            pass

        return resultado

    except Exception as e:

        conn.rollback()

        return {
            "success": False,
            "erro": str(e)
        }

    finally:

        cur.close()
        conn.close()