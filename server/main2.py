import os
import re
from typing import List, Dict
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Store in environment variable
genai.configure(api_key=GEMINI_API_KEY)

class CodeAnalyzer:
    @staticmethod
    def generate_function_summary(function_code: str) -> str:
        """
        Use Gemini to generate a summary of a function
        """
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""Analyze this C function and provide:
            1. A clear, concise description of what the function does
            2. Brief explanation of parameters
            3. What the function returns
            4. Any notable implementation details

            Function code:
            ```c
            {function_code}
            ```
            
            Provide the summary in a structured, easy-to-read format."""

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate summary: {str(e)}"

class CodeMapParser:
    @staticmethod
    def parse_c_file(file_path: str) -> Dict:
        """
        Parse C language file and extract key structural information
        """
        with open(file_path, 'r') as file:
            content = file.read()

        # Extract function definitions with full function body
        functions = CodeMapParser._extract_functions_with_body(content)
        
        # Generate summaries for functions
        for func in functions:
            func['summary'] = CodeAnalyzer.generate_function_summary(func['full_code'])

        return {
            'imports': CodeMapParser._extract_imports(content),
            'functions': functions,
            'global_variables': CodeMapParser._extract_global_variables(content),
            'structs': CodeMapParser._extract_structs(content)
        }

    @staticmethod
    def _extract_functions_with_body(content: str) -> List[Dict]:
        """
        Extract function definitions with full body and context
        """
        function_pattern = re.compile(
            r'^(\w+\s*(?:\*+\s*)?)\s*(\w+)\s*\((.*?)\)\s*{(.*?)}', 
            re.MULTILINE | re.DOTALL
        )
        
        functions = []
        for match in function_pattern.finditer(content):
            return_type, name, params, body = match.groups()
            functions.append({
                'return_type': return_type.strip(),
                'name': name.strip(),
                'parameters': [p.strip() for p in params.split(',') if p.strip()],
                'full_code': f"{return_type} {name}({params}) {{{body}}}",
                'body': body.strip()
            })
        return functions

    @staticmethod
    def _extract_imports(content: str) -> List[str]:
        """Extract #include statements from C code"""
        import_pattern = re.compile(r'#include\s*[<"]([^>"]+)[>"]')
        imports = import_pattern.findall(content)
        return imports

    @staticmethod
    def _extract_global_variables(content: str) -> List[Dict]:
        """Extract global variable declarations"""
        # Look for variable declarations outside of functions
        var_pattern = re.compile(
            r'^((?:const\s+)?(?:unsigned\s+)?(?:int|char|float|double|void)\s*\*?\s*)'
            r'(\w+)\s*(?:=\s*[^;]+)?;', 
            re.MULTILINE
        )
        
        variables = []
        for match in var_pattern.finditer(content):
            variables.append({
                'type': match.group(1).strip(),
                'name': match.group(2).strip()
            })
        return variables

    @staticmethod
    def _extract_structs(content: str) -> List[Dict]:
        """Extract struct definitions"""
        struct_pattern = re.compile(
            r'typedef\s+struct\s*(?:\w+)?\s*{(.*?)}(?:\s*(\w+))?\s*;', 
            re.MULTILINE | re.DOTALL
        )
        
        structs = []
        for match in struct_pattern.finditer(content):
            body, typedef_name = match.groups()
            members = [
                {'type': m.split()[0].strip(), 'name': m.split()[1].strip().rstrip(';')} 
                for m in body.split(';') if m.strip()
            ]
            structs.append({
                'name': typedef_name or 'Anonymous',
                'members': members
            })
        return structs

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse/c")
async def parse_c_file(file: UploadFile = File(...)):
    """
    Endpoint to parse uploaded C file with Gemini-powered analysis
    """
    # Save uploaded file temporarily
    with open(file.filename, 'wb') as buffer:
        buffer.write(await file.read())
    
    try:
        # Parse the file
        result = CodeMapParser.parse_c_file(file.filename)
        
        # Clean up temporary file
        os.remove(file.filename)
        
        return result
    except Exception as e:
        # Clean up file in case of error
        if os.path.exists(file.filename):
            os.remove(file.filename)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)