import os
import re
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import GenerativeModel

load_dotenv()
model = GenerativeModel('gemini-pro')

# Initialize Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')


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
    """Generate documentation sections using Gemini AI with an enhanced prompt."""

    # --- Input Processing ---
    parsed_code_info = ""
    if code:
        try:
            includes = CParser.extract_includes(code)
            functions = CParser.extract_functions(code)
            variables = CParser.extract_variables(code) # Assuming basic extraction is sufficient

            parsed_code_info = f"""
        CODE ANALYSIS:
        Based on static analysis, the provided C code appears to contain:
        - Includes: {', '.join(includes) if includes else 'None detected'}
        - Functions: {', '.join([f['name'] for f in functions]) if functions else 'None detected'}
        - Key Variables/Structs: {', '.join([f"{v['type']} {v['name']}" for v in variables]) if variables else 'None detected'}
        Use this analysis to inform your documentation, ensuring consistency. If the analysis seems incorrect based on the code's logic, prioritize documenting the actual code's behavior.
        """
        except Exception as e:
            print(f"Warning: Code parsing failed - {e}") # Log or handle appropriately
            parsed_code_info = "\n        CODE ANALYSIS: Could not perform static analysis on the provided code.\n"

    # --- Build the Prompt ---
    requested_sections = [option for option, selected in options.items() if selected]
    options_list = "\n".join([f"- {section}" for section in requested_sections])

    # Determine code handling instruction
    code_instruction = ""
    if code:
        code_instruction = f"""
    CODE PROVIDED BY USER:
    ```c
    {code}
    ```
    {parsed_code_info}
    Focus your documentation (especially 'code', 'variablesAndConstants', 'functions', 'explanation') on THIS specific code. If generating sections like 'detailedAlgorithm' or 'shortAlgorithm', ensure they accurately reflect the logic in the provided code.
    """
    else:
        code_instruction = """
    CODE PROVIDED BY USER: None
    Please generate a standard, correct, and well-commented C implementation for the given question as part of the 'code' section if requested. Base other relevant sections (algorithm, explanation, etc.) on this generated code.
    """

    # Fixed version: Use raw string for the JSON template part
    json_template = r'''
    ```json
    {
        "overview": "{'overview text if requested' or ''}",
        "shortAlgorithm": "{'short algorithm text if requested, formatted as a numbered list with \\n between items' or ''}",
        "detailedAlgorithm": "{'detailed algorithm text if requested, formatted as a numbered list with \\n between items' or ''}",
        "code": "{'C code solution (potentially formatted with \\n and \\t) if requested' or ''}",
        "requiredModules": "{'required modules explanation if requested, potentially with \\n between items' or ''}",
        "variablesAndConstants": "{'variables and constants explanation if requested, potentially with \\n between items' or ''}",
        "functions": "{'functions explanation if requested, potentially with \\n between items' or ''}",
        "explanation": "{'holistic code explanation if requested' or ''}"
    }
    ```
    '''

    prompt = f"""
    **ROLE AND GOAL:**
    You are an expert C programmer and Operating Systems Teaching Assistant. Your goal is to help a university student prepare for their OS Lab Exam by generating clear, accurate, and educational documentation for a given problem.

    **CONTEXT:**
    The student needs to understand both the underlying OS concepts and how they are implemented in C. The output should be suitable for studying and revising for a practical lab examination. Assume the student has basic C programming knowledge but needs detailed explanations for OS algorithms and their implementation specifics.

    **TASK:**
    Based on the user's question and potentially provided C code, generate the specified documentation sections. Ensure the content is accurate, easy to understand, and directly relevant to the question.

    **INPUTS:**

    1.  **QUESTION:**
        {question}

    2.  {code_instruction}

    3.  **REQUESTED DOCUMENTATION SECTIONS:**
        {options_list if options_list else "No specific sections requested."}

    **INSTRUCTIONS FOR GENERATING SECTIONS:**

    *   **General:**
        *   Use clear and concise language suitable for an undergraduate student.
        *   Be accurate regarding OS concepts and C implementation details.
        *   If generating code, ensure it is correct, follows standard C practices, and includes meaningful comments.
        *   If analyzing provided code, base your explanations *on that code*, even if it's not the most optimal implementation (unless it's fundamentally wrong for the concept).
        *   Aim for the level of detail and clarity found in good OS textbook examples or lab manuals (like the provided FCFS/SJF/Memory Allocation examples).

    *   **Specific Section Guidelines (Only generate content for requested sections):**
        *   `overview`: Provide a brief, high-level explanation of the core OS concept addressed in the question (e.g., what is FCFS scheduling? What is shared memory IPC?).
        *   `shortAlgorithm`: List the main steps of the algorithm concisely using a numbered list (e.g., 1., 2., 3.). Focus on the core logic and flow, omitting deep implementation details or variable names unless essential for clarity. Aim for 4-7 high-level steps, similar to the provided examples (e.g., "1. Define Structure. 2. Input data. 3. Loop/Process logic. 4. Calculate results. 5. Display output.").
        *   `detailedAlgorithm`: Provide a step-by-step, implementation-oriented algorithm. Mention key data structures (like `struct Process`), main loops, function calls, and decision logic. Number the steps clearly (e.g., 1. Define Structure, 2. Input, 3. Sort...). This should closely map to the code (provided or generated).
        *   `code`: Present the complete C code solution. If code was provided by the user, present that code, potentially with minor formatting improvements for readability. If no code was provided, generate a functional, well-commented C implementation. Use standard libraries (like `stdio.h`, `stdlib.h`, `limits.h`, `pthread.h`, `semaphore.h`, `sys/ipc.h`, `sys/shm.h` where appropriate).
        *   `requiredModules`: List the necessary `#include` directives (e.g., `#include <stdio.h>`). For each include, briefly explain *why* it's needed (e.g., "`stdio.h`: For standard input/output functions like `printf` and `scanf`.").
        *   `variablesAndConstants`: Describe the key variables, constants, and data structures (like `structs`) used in the code. Explain the purpose of each (e.g., "`struct Process`: Holds process details like PID, AT, BT...; `currentTime`: Tracks the simulation clock."). Align this with the `CODE ANALYSIS` if provided.
        *   `functions`: Describe the purpose and basic logic of each major function in the code (e.g., "`sortByArrivalTime()`: Sorts processes based on arrival time using bubble sort; `fcfs()`: Calculates metrics and prints Gantt chart."). Align this with the `CODE ANALYSIS` if provided.
        *   `explanation`: Provide a holistic explanation of how the code implements the algorithm and solves the problem. Connect the algorithm steps to the code logic, variables, and functions. Explain *how* the OS concept is demonstrated. For scheduling algorithms, explain how the Gantt chart (if applicable) is derived and what it represents. For IPC/Sync problems, explain the roles of different processes/threads and synchronization primitives.

    **OUTPUT FORMAT:**

    **CRITICAL:** Respond *only* with a valid JSON object. Do not include any text before or after the JSON structure.
    Use the following exact structure. For any section that was *not* requested in the "REQUESTED DOCUMENTATION SECTIONS" list above, use an empty string `""` as its value. Do *not* omit the key.
    {json_template}

    Ensure all string values within the JSON are properly escaped if they contain special characters like newlines (\\n), quotes (\"), tabs (\\t), etc. For lists within sections (like algorithms or modules), use newline characters (\\n) for separation within the JSON string value.
    """

    # --- AI Call ---
    generation_config = {
        "temperature": 0.1, # Focused output
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json", # Request JSON output
    }

    try:
        # Assuming your 'model' object has a 'generate_content' method
        response = model.generate_content(
            prompt,
            generation_config=generation_config
            # Add safety_settings if needed
        )

        # --- Response Handling ---
        response_text = response.text

        # Basic validation/cleanup before parsing
        response_text = re.sub(r'^```json\s*', '', response_text.strip(), flags=re.IGNORECASE)
        response_text = re.sub(r'\s*```$', '', response_text)

        try:
            # The response should ideally be clean JSON now
            result = json.loads(response_text)

            # Validate expected keys exist, even if empty
            expected_keys = {"overview", "shortAlgorithm", "detailedAlgorithm", "code",
                             "requiredModules", "variablesAndConstants", "functions", "explanation"}
            for key in expected_keys:
                if key not in result:
                    print(f"Warning: Key '{key}' missing in JSON response. Adding as empty string.")
                    result[key] = "" # Add missing keys as empty strings

            # Ensure requested sections that might be empty in the response are still present
            for option, selected in options.items():
                 if selected and option not in result:
                     print(f"Warning: Requested key '{option}' missing in JSON response despite being requested. Adding as empty string.")
                     result[option] = ""


            return result
        except json.JSONDecodeError as json_err:
            print(f"Error: Failed to decode JSON response: {json_err}")
            print(f"Raw Response Text:\n---\n{response_text}\n---")
            # Fallback: Return error structure or attempt manual extraction as last resort
            # Your original regex fallback could go here if needed.
            # For now, return a dict indicating error for requested sections.
            error_result = {key: "" for key in {"overview", "shortAlgorithm", "detailedAlgorithm", "code",
                                                "requiredModules", "variablesAndConstants", "functions", "explanation"}}
            for option, selected in options.items():
                if selected:
                    error_result[option] = f"Error parsing JSON response. Raw text might contain info. Error: {json_err}"
            return error_result


    except Exception as e:
        # Handle API errors, connection issues etc.
        print(f"Error generating documentation via API: {str(e)}") # Use print or logging
        # Consider raising a custom exception or returning an error structure
        raise Exception(f"Error generating documentation via API: {str(e)}") # Or use HTTPException if in a web context