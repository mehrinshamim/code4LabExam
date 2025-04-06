from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

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

class CParser:
    @staticmethod
    def extract_includes(code: str) -> List[str]:
        """Extract included libraries from C code."""
        include_pattern = r'#include\s*<([^>]+)>'
        return re.findall(include_pattern, code)
    
    @staticmethod
    def extract_functions(code: str) -> List[Dict]:
        """Extract function definitions from C code."""
        # Basic function pattern (simplified)
        function_pattern = r'(\w+\s+\w+\s*\([^)]*\)\s*\{[^}]*\})'
        functions = re.findall(function_pattern, code, re.DOTALL)
        
        result = []
        for func in functions:
            # Extract function signature
            signature_match = re.match(r'(\w+\s+\w+\s*\([^)]*\))', func)
            if signature_match:
                signature = signature_match.group(1).strip()
                # Extract function name
                name_match = re.search(r'\s(\w+)\s*\(', signature)
                if name_match:
                    name = name_match.group(1)
                    result.append({
                        "name": name,
                        "signature": signature,
                        "body": func
                    })
        
        return result
    
    @staticmethod
    def extract_variables(code: str) -> List[Dict]:
        """Extract variable declarations from C code."""
        # This is a simplified version
        var_pattern = r'(int|float|double|char|void)\s+(\w+)(?:\s*=\s*([^;]+))?;'
        variables = re.findall(var_pattern, code)
        
        result = []
        for var_type, var_name, initial_value in variables:
            result.append({
                "type": var_type,
                "name": var_name,
                "initial_value": initial_value.strip() if initial_value else None
            })
        
        return result

def generate_documentation_with_ai(question: str, code: Optional[str], options: Dict[str, bool]):
    """Generate documentation sections using Gemini AI."""
    
    # Parse code if provided
    parsed_code = None
    if code:
        parsed_code = {
            "includes": CParser.extract_includes(code),
            "functions": CParser.extract_functions(code),
            "variables": CParser.extract_variables(code)
        }
    
    # Build the prompt based on selected options
    prompt = f"""
    You are an expert in Operating Systems and computer programming. 
    
    QUESTION:
    {question}
    
    {'CODE PROVIDED BY USER:' + code if code else 'No code provided. Please generate appropriate code.'}
    
    Please generate the following documentation sections:
    """
    
    for option, selected in options.items():
        if selected:
            prompt += f"- {option}\n"
    
    if parsed_code:
        prompt += f"""
        Based on my analysis, the code has:
        - Includes: {', '.join(parsed_code['includes']) if parsed_code['includes'] else 'None'}
        - Functions: {', '.join([f['name'] for f in parsed_code['functions']]) if parsed_code['functions'] else 'None'}
        - Variables: {', '.join([f"{v['type']} {v['name']}" for v in parsed_code['variables']]) if parsed_code['variables'] else 'None'}
        
        Please use this information in your documentation.
        """
        
    prompt += """
    Important: Format your response as JSON with the following structure:
    {
        "overview": "overview text if requested",
        "shortAlgorithm": "short algorithm if requested",
        "detailedAlgorithm": "detailed algorithm if requested",
        "code": "code solution if requested",
        "requiredModules": "required modules if requested",
        "variablesAndConstants": "variables and constants if requested",
        "functions": "functions if requested",
        "explanation": "code explanation if requested"
    }
    
    For sections that weren't requested, leave those fields empty.
    Make each section comprehensive and educational for a student preparing for an OS lab exam.
    """
    
    # Set temperature to 0 for more deterministic results
    generation_config = {
        "temperature": 0,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 8192,
    }
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # The response should be JSON formatted
        response_text = response.text
        
        # Handle the response
        import json
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # If Gemini doesn't return valid JSON, extract sections manually
            sections = {}
            
            # Check for each section in the response
            for section in ["overview", "shortAlgorithm", "detailedAlgorithm", "code", 
                           "requiredModules", "variablesAndConstants", "functions", "explanation"]:
                # Simple extraction (could be improved)
                section_match = re.search(rf'"{section}"\s*:\s*"(.*?)"', response_text, re.DOTALL)
                if section_match:
                    sections[section] = section_match.group(1)
                else:
                    sections[section] = ""
            
            return sections
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating documentation: {str(e)}")

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