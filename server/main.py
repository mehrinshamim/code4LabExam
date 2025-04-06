import os
import re
from typing import List, Dict
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

class CodeMapParser:
    @staticmethod
    def parse_c_file(file_path: str) -> Dict:
        """
        Parse C language file and extract key structural information
        """
        with open(file_path, 'r') as file:
            content = file.read()

        return {
            'imports': CodeMapParser._extract_imports(content),
            'functions': CodeMapParser._extract_functions(content),
            'global_variables': CodeMapParser._extract_global_variables(content),
            'structs': CodeMapParser._extract_structs(content)
        }

    @staticmethod
    def _extract_imports(content: str) -> List[str]:
        """Extract #include statements"""
        import_pattern = r'#\s*include\s*[<"](.+?)[>"]'
        return re.findall(import_pattern, content)

    @staticmethod
    def _extract_functions(content: str) -> List[Dict]:
        """Extract function definitions with details"""
        # Improved regex for function detection
        function_pattern = re.compile(
            r'^(\w+\s*(?:\*+\s*)?)\s*(\w+)\s*\((.*?)\)\s*{', 
            re.MULTILINE | re.DOTALL
        )
        
        functions = []
        for match in function_pattern.finditer(content):
            return_type, name, params = match.groups()
            functions.append({
                'return_type': return_type.strip(),
                'name': name.strip(),
                'parameters': [p.strip() for p in params.split(',') if p.strip()]
            })
        return functions

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

# CORS middleware to allow frontend connections
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
    Endpoint to parse uploaded C file
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