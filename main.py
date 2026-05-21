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

    sql = request.sql.strip().lower()

    if not sql.startswith("select"):
        return {"erro": "Apenas SELECT permitido"}

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        options="-c search_path=demo_rdn_soul_agents_trackito"
    )

    cur = conn.cursor()

    cur.execute(request.sql)

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    resultado = []

    for row in rows:
        resultado.append(dict(zip(columns, row)))

    cur.close()
    conn.close()

    return {
        "rows": resultado
    }