# main.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='multiprocessing.resource_tracker')

from fastapi import FastAPI
from pydantic import BaseModel
from charles import DarwinChatbot
from fastapi.middleware.cors import CORSMiddleware

# Initialize chatbot once
chatbot = DarwinChatbot()

# Create FastAPI app
app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body format
class QuestionRequest(BaseModel):
    question: str

# POST endpoint to receive questions
@app.post("/ask")
def ask_question(data: QuestionRequest):
    answer = chatbot.ask(data.question)
    return {"answer": answer}
