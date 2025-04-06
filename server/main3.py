import os
import re
from typing import List, Dict
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=GEMINI_API_KEY)

class FunctionAnalyzer:
    @staticmethod
    def extract_functions(file_path: str) -> List[Dict]:
        """
        Extract complete functions from C file
        """
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Enhanced regex to capture full function bodies
        function_pattern = re.compile(
            r'((?:static\s+)?[\w\*\s]+)\s+(\w+)\s*\(([^)]*)\)\s*{([^}]*(?:{[^}]*}[^}]*)*)}', 
            re.MULTILINE | re.DOTALL
        )
        
        functions = []
        for match in function_pattern.finditer(content):
            return_type, name, params, body = match.groups()
            
            # Clean up function details
            full_function = f"{return_type} {name}({params}) {{\n{body}\n}}"
            
            # Generate summary using Gemini
            summary = FunctionAnalyzer.generate_function_summary(full_function)
            
            functions.append({
                'name': name.strip(),
                'return_type': return_type.strip(),
                'parameters': [p.strip() for p in params.split(',') if p.strip()],
                'body': body.strip(),
                'full_code': full_function,
                'summary': summary
            })
        
        return functions

    @staticmethod
    def generate_function_summary(function_code: str) -> str:
        """
        Use Gemini to generate a comprehensive function summary
        """
        try:
            # Use Gemini Pro for text generation
            model = genai.GenerativeModel('gemini-pro')
            
            # Detailed prompt for function analysis
            prompt = f"""Analyze this C function and provide a comprehensive summary:

Function Code:
```c
{function_code}
```

For the summary, include:
1. Primary purpose of the function
2. Key input parameters and their roles
3. Return value and its significance
4. Any notable algorithmic approaches or implementation details
5. Potential use cases or context
6. Any potential side effects or important observations

Provide a clear, concise, and informative summary that helps developers quickly understand the function's behavior and purpose."""

            # Generate summary
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze/c")
async def analyze_c_file(file: UploadFile = File(...)):
    """
    Endpoint to analyze C file and extract function details with Gemini summaries
    """
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, 'wb') as buffer:
        buffer.write(await file.read())
    
    try:
        # Extract and analyze functions
        functions = FunctionAnalyzer.extract_functions(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {
            "filename": file.filename,
            "functions": functions
        }
    except Exception as e:
        # Clean up file in case of error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)