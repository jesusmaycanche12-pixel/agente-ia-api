import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

# ====== PERSONALIZACIÓN: cambia estos textos a tu gusto ======
NOMBRE = "Jesús May"
TITULO = "Asistente de IA"
SUBTITULO = "Vas a platicar con el asistente de Jesús May, puedes preguntarle lo que quieras"
SALUDO = "¡Qué onda! ¿Qué quieres saber?"
# =============================================================

app = FastAPI(title="Agente IA API", version="1.4.0")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    f"Eres el asistente virtual de {NOMBRE}, consultor de automatización con IA en México. "
    "Respondes en español, con un tono amigable, cercano y con buen humor. "
    "Tus respuestas son claras y breves. "
    "Ayudas con dudas sobre inteligencia artificial, automatización y negocios. "
    "Si te piden un chiste o algo divertido, lo haces con gusto, con humor sano y sin groserías. "
    f"Si te preguntan por servicios o precios, di que {NOMBRE} puede dar una cotización personalizada."
)


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
    return {"estado": "activo", "version": "1.4.0"}


@app.post("/chat")
def chat(entrada: MensajeEntrada):
    respuesta = llamar_groq([
        {"role": "system", "content": SYSTEM_PROMPT},
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


PAGINA_CHAT = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITULO__ · __NOMBRE__</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; height: 100vh; display: flex; flex-direction: column;
    font-family: "Segoe UI", Arial, sans-serif; color: #e6edf3;
    background:
      repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 40px),
      repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 40px),
      radial-gradient(circle at 15% 0%, #1c2431 0%, #0a0d12 50%, #030406 100%);
    background-attachment: fixed;
  }
  header {
    padding: 16px 20px;
    background: linear-gradient(180deg, #141a24, #0b0f16);
    border-bottom: 2px solid #00e5ff;
    box-shadow: 0 2px 18px rgba(0,229,255,0.35);
  }
  header h1 {
    margin: 0; font-family: "Orbitron", "Segoe UI", sans-serif; font-size: 20px;
    text-transform: uppercase; letter-spacing: 3px; color: #00e5ff;
    text-shadow: 0 0 10px rgba(0,229,255,0.6);
  }
  header p { margin: 6px 0 0; font-size: 13px; color: #9fb0c3; }
  #chat { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
  .msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; line-height: 1.4; white-space: pre-wrap; }
  .user {
    align-self: flex-end; color: #fff;
    background: linear-gradient(135deg, #8b0f0f, #c41e1e);
    border: 1px solid #ff3b3b; box-shadow: 0 0 10px rgba(255,45,45,0.3);
  }
  .bot {
    align-self: flex-start; background: #121923;
    border: 1px solid #1f3a4a; border-left: 3px solid #00e5ff;
    box-shadow: 0 0 10px rgba(0,229,255,0.12);
  }
  #sugerencias { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 16px 10px; }
  .chip {
    padding: 8px 12px; border-radius: 20px; border: 1px solid #00e5ff;
    background: transparent; color: #00e5ff; font-size: 14px; cursor: pointer;
  }
  .chip:hover { background: rgba(0,229,255,0.15); }
  form { display: flex; gap: 8px; padding: 12px 16px; background: #0b0f16; border-top: 1px solid #1f2a37; }
  input {
    flex: 1; padding: 12px; border-radius: 10px; font-size: 16px;
    background: #0f1520; color: #e6edf3; border: 1px solid #26405a; outline: none;
  }
  input:focus { border-color: #00e5ff; box-shadow: 0 0 8px rgba(0,229,255,0.4); }
  button.enviar {
    padding: 12px 18px; border-radius: 10px; font-size: 15px; font-weight: bold; cursor: pointer;
    text-transform: uppercase; letter-spacing: 1px; color: #fff;
    background: linear-gradient(135deg, #a82c2c, #7d2222); border: 1px solid #c75a5a;
  }
  button:disabled { opacity: 0.5; }
  footer { text-align: center; font-size: 12px; color: #6b7c90; padding: 6px 0 10px; background: #0b0f16; }
</style>
</head>
<body>
<header>
  <h1>🤖 __TITULO__</h1>
  <p>__SUBTITULO__</p>
</header>
<div id="chat"><div class="msg bot">__SALUDO__</div></div>
<div id="sugerencias">
  <button class="chip" type="button">Cuéntame un chiste de robots 🤖</button>
  <button class="chip" type="button">¿Qué pasaría si un robot fuera mi jefe por un día? 😄</button>
  <button class="chip" type="button">Explícame qué es la IA como si tuviera 5 años 🧸</button>
</div>
<form id="form">
  <input id="texto" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" required>
  <button class="enviar" id="enviar" type="submit">Enviar</button>
</form>
<footer>Creado por __NOMBRE__ · Powered by Groq</footer>
<script>
  const chat = document.getElementById("chat");
  const form = document.getElementById("form");
  const texto = document.getElementById("texto");
  const boton = document.getElementById("enviar");
  const sugerencias = document.getElementById("sugerencias");

  function agregar(clase, contenido) {
    const div = document.createElement("div");
    div.className = "msg " + clase;
    div.textContent = contenido;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
  }

  async function enviar(pregunta) {
    if (!pregunta || boton.disabled) return;
    sugerencias.style.display = "none";
    agregar("user", pregunta);
    boton.disabled = true;
    const espera = agregar("bot", "Pensando... (si el servicio estaba dormido, la primera respuesta puede tardar un minuto)");
    try {
      const r = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensaje: pregunta })
      });
      const datos = await r.json();
      if (r.ok) {
        espera.textContent = datos.respuesta;
      } else {
        espera.textContent = "Error " + r.status + ": " + (typeof datos.detail === "string" ? datos.detail : "petición inválida");
      }
    } catch (err) {
      espera.textContent = "No se pudo conectar con el servidor.";
    }
    boton.disabled = false;
    texto.focus();
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const pregunta = texto.value.trim();
    texto.value = "";
    enviar(pregunta);
  });

  document.querySelectorAll(".chip").forEach((b) => {
    b.addEventListener("click", () => enviar(b.textContent));
  });
</script>
</body>
</html>"""


@app.get("/app", response_class=HTMLResponse)
def pagina_chat():
    return (
        PAGINA_CHAT
        .replace("__NOMBRE__", NOMBRE)
        .replace("__TITULO__", TITULO)
        .replace("__SUBTITULO__", SUBTITULO)
        .replace("__SALUDO__", SALUDO)
    )
