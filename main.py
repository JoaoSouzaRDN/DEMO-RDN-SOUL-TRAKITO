from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    sql: str

class EmailRequest(BaseModel):
    para: str
    assunto: str
    html: str

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

API_TOKEN = os.getenv("API_TOKEN")

@app.post("/executar-sql")
def executar_sql(
    request: QueryRequest,
    x_api_key: str = Header(None)
):

    if x_api_key != API_TOKEN:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

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

                resultado.append(
                    dict(zip(columns, row))
                )

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

                    returning.append(
                        dict(zip(columns, row))
                    )

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

@app.post("/enviar-email")
def enviar_email(
    request: EmailRequest,
    x_api_key: str = Header(None)
):

    if x_api_key != API_TOKEN:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    try:

        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": os.getenv("BREVO_API_KEY"),
            "content-type": "application/json"
        }

        payload = {
            "sender": {
                "name": os.getenv("BREVO_REMETENTE_NOME"),
                "email": os.getenv("BREVO_REMETENTE_EMAIL")
            },
            "to": [
                {
                    "email": request.para
                }
            ],
            "subject": request.assunto,
            "htmlContent": request.html
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        return {
            "success": response.status_code in [200, 201, 202],
            "status_code": response.status_code,
            "response": response.json()
        }

    except Exception as e:

        return {
            "success": False,
            "erro": str(e)
        }

@app.get("/")
def home():

    return {
        "success": True,
        "message": "API TRAKITO ONLINE"
    }