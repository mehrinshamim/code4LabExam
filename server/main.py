from fastapi import FastAPI #, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import google.generativeai as genai
#import re
import os
from dotenv import load_dotenv
from services.gemini_os_doc import generate_documentation_with_ai

# Load environment variables
load_dotenv()

# Initialize Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentationRequest(BaseModel):
    question: str
    code: Optional[str] = None
    options: Dict[str, bool]

@app.post("/generate-documentation")
async def generate_documentation(request: DocumentationRequest):
    """Generate documentation based on question and code."""
    return generate_documentation_with_ai(
        question=request.question,
        code=request.code,
        options=request.options
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)