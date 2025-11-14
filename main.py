from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from openai import OpenAI

# ------------------ Load OpenAI API Key ------------------
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Check your .env file!")

client = OpenAI(api_key=api_key)

# ------------------ FastAPI Setup ------------------
app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# ------------------ In-memory storage ------------------
patients = []
appointments = []
bills = []

# ------------------ ROUTES ------------------

# Home
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat
@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/chat", response_class=HTMLResponse)
def chat_submit(request: Request, message: str = Form(...)):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{"role": "user", "content": message}]
        )
        ai_reply = response.output_text
    except Exception as e:
        ai_reply = f"Error: {e}"
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "user_message": message, "ai_reply": ai_reply}
    )

# Patients
@app.get("/patients", response_class=HTMLResponse)
def patients_page(request: Request):
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})

@app.post("/patients", response_class=HTMLResponse)
def add_patient(request: Request, name: str = Form(...), age: str = Form(...), gender: str = Form(...)):
    patients.append({"name": name, "age": age, "gender": gender})
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})

# Appointments
@app.get("/appointments", response_class=HTMLResponse)
def appointments_page(request: Request):
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointments})

@app.post("/appointments", response_class=HTMLResponse)
def book_appointment(request: Request, patient_name: str = Form(...), doctor_name: str = Form(...), date: str = Form(...)):
    appointments.append({"patient_name": patient_name, "doctor_name": doctor_name, "date": date})
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointments})

# Billing
@app.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request):
    return templates.TemplateResponse("billing.html", {"request": request, "bills": bills})

@app.post("/billing", response_class=HTMLResponse)
def add_bill(request: Request, patient_name: str = Form(...), amount: str = Form(...)):
    bills.append({"patient_name": patient_name, "amount": amount})
    return templates.TemplateResponse("billing.html", {"request": request, "bills": bills})
