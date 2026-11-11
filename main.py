import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Agente IA API", version="1.0.0")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "openai/gpt-oss-20b"


def llamar_groq(mensajes):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Falta GROQ_API_KEY en el servidor")
    headers = {
        "Authorization": "Bearer " + GROQ_API_KEY,
        "Content-Type": "application/json",
    }
    body = {"model": MODELO, "messages": mensajes, "temperature": 0.7}
    try:
        r = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        raise HTTPException(status_code=502, detail="Error al consultar el modelo")


class MensajeEntrada(BaseModel):
    mensaje: str


class ProspectoEntrada(BaseModel):
    nombre: str
    sector: str
    problema: str


@app.get("/")
def inicio():
    return {"estado": "activo", "version": "1.0.0"}


@app.post("/chat")
def chat(entrada: MensajeEntrada):
    respuesta = llamar_groq([
        {"role": "system", "content": "Eres un asistente de negocios especializado en automatización IA."},
        {"role": "user", "content": entrada.mensaje},
    ])
    return {"respuesta": respuesta, "modelo": MODELO}


@app.post("/analizar-prospecto")
def analizar_prospecto(p: ProspectoEntrada):
    prompt = f"""Analiza este prospecto en 3 puntos concisos:
Empresa: {p.nombre}
Sector: {p.sector}
Problema: {p.problema}

1. Por qué necesitan IA
2. Servicio específico a ofrecer
3. Mensaje de WhatsApp para contactarlos"""
    respuesta = llamar_groq([{"role": "user", "content": prompt}])
    return {"analisis": respuesta}