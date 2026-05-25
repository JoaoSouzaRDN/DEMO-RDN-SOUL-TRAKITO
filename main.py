from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
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

@app.post("/executar-sql")
def executar_sql(request: QueryRequest):

    conn = None
    cur = None

    try:

        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            options="-c search_path=demo_rdn_soul_agents_trackito"
        )

        cur = conn.cursor()

        sql_lower = request.sql.strip().lower()

        cur.execute(request.sql)

        if sql_lower.startswith("select"):

            rows = cur.fetchall()

            columns = [desc[0] for desc in cur.description]

            resultado = []

            for row in rows:
                resultado.append(dict(zip(columns, row)))

            return {
                "success": True,
                "rows": resultado
            }

        else:

            conn.commit()

            returning = []

            if cur.description:
                columns = [desc[0] for desc in cur.description]

                for row in cur.fetchall():
                    returning.append(dict(zip(columns, row)))

            return {
                "success": True,
                "rows_affected": cur.rowcount,
                "returning": returning
            }

    except Exception as e:

        if conn:
            conn.rollback()

        return {
            "success": False,
            "erro": str(e)
        }

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()