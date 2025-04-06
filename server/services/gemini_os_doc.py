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



def detect_language(question: str, model) -> str:
    """
    Uses Gemini to detect if the question requires a C program or a Shell script.

    Args:
        question: The OS lab question text.
        model: The initialized Gemini model instance.

    Returns:
        "Shell" or "C". Defaults to "C" if detection is unclear.
    """
    prompt = f"""
    Analyze the following Operating Systems lab question and determine if the primary implementation requirement is a C program or a Bash Shell Script.

    QUESTION:
    "{question}"

    GUIDELINES:
    - Assume **Bash Shell Script** if the question explicitly mentions 'shell programming', 'shell script', 'bash script', or describes tasks primarily involving file system operations (listing, checking existence, creating/deleting files based on conditions), text processing using standard Unix tools (grep, sed, awk), or managing processes from the command line, *without* requiring low-level system calls (like `fork`, `shmget`, `sem_init`, complex data structures like linked lists/structs for algorithms).
    - Otherwise, assume **C program** is required, especially for implementing scheduling algorithms, memory management algorithms, IPC using semaphores/shared memory, Banker's algorithm, or tasks requiring direct system calls or complex data structures.

    Respond with ONLY the single word "C" or "Shell". Do not include any other text, explanation, or formatting.
    """

    generation_config = {
        "temperature": 0, # Deterministic classification
        "max_output_tokens": 5, # Just need one word
        "top_p": 1,
        "top_k": 1,
    }

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        detected = response.text.strip().lower()

        if "shell" in detected:
            print(f"Language Detected: Shell for question: '{question[:50]}...'")
            return "Shell"
        else:
            # Default to C if response is not clearly "Shell"
            print(f"Language Detected: C (or default) for question: '{question[:50]}...'")
            return "C"
    except Exception as e:
        print(f"Warning: Language detection failed: {e}. Defaulting to C.")
        return "C"


# Fixed version: Use raw string for the JSON template part
c_json_template = r'''
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

shell_json_template = r'''
```json
{{
    "overview": "{'overview text if requested' or ''}",
    "shortAlgorithm": "{'short algorithm text if requested, formatted as a numbered list with \\n between items' or ''}",
    "detailedAlgorithm": "{'detailed algorithm text if requested, formatted as a numbered list with \\n between items' or ''}",
    "code": "{'Bash script solution (potentially formatted with \\n and \\t) if requested' or ''}",
    "requiredModules": "{'required utilities explanation if requested, potentially with \\n between items' or ''}",
    "variablesAndConstants": "{'shell variables explanation if requested, potentially with \\n between items' or ''}",
    "functions": "{'shell functions/blocks explanation if requested, potentially with \\n between items' or ''}",
    "explanation": "{'holistic script explanation if requested' or ''}"
}}
```
'''


def get_shell_generation_prompt(question: str, code_instruction: str, options_list: str) -> str:
    """Returns the prompt optimized for generating Shell script documentation."""
    return f"""
    **ROLE AND GOAL:**
    You are an expert Bash Shell Scripter and Operating Systems Teaching Assistant. Your goal is to help a university student prepare for their OS Lab Exam by generating clear, accurate, and educational documentation for a Shell scripting problem, including functional Bash scripts with specific feedback requirements when requested.

    **CONTEXT:**
    The student needs to understand OS concepts achievable via Shell scripting, including how to verify results through script output/feedback. The output should be suitable for studying for a practical lab exam.

    **TASK:**
    Generate the specified documentation sections for the given Shell scripting question. Ensure accuracy, clarity, and relevance. Pay close attention to mandatory output/feedback requirements for generated Shell scripts.

    **INPUTS:**

    1.  **QUESTION:**
        {question}

    2.  {code_instruction}

    3.  **REQUESTED DOCUMENTATION SECTIONS:**
        {options_list if options_list else "No specific sections requested."}

    **INSTRUCTIONS FOR GENERATING SECTIONS (Shell Focus):**

    *   **General Guidelines:**
        *   Use clear, concise language suitable for undergraduate students.
        *   Be accurate regarding Shell scripting concepts and standard Unix utilities.
        *   If analyzing provided Shell script, base explanations *on that script*.
        *   Aim for the detail and clarity of good OS lab manuals/examples.
        *   **Mandatory Output/Feedback in Generated Shell Script:** When generating Shell scripts, *must* include `echo` statements to provide clear user feedback as specified below.

    *   **Specific Section Guidelines (Shell):**
        *   `overview`: Brief, high-level explanation of the task the script performs.
        *   `shortAlgorithm`: Concise, numbered list (4-7 steps) of the main sequence of shell commands and logic.
        *   `detailedAlgorithm`: Step-by-step description mapping closely to the script's commands and control flow (loops, conditionals).
        *   `code`:
            *   If Shell script was provided: Present that script.
            *   If no code was provided: Generate a functional, well-commented Bash Shell Script (`#!/bin/bash`).
            *   **Required Output/Feedback in Generated Shell Script:**
                *   **File/Directory Operations:** Use `echo` to provide clear user feedback. Examples:
                    *   For a question like "Create a shell programming which lists files and folders in a directory, and save this information into a textfile.": The script should `echo` a confirmation message like `echo "Directory listing saved to output.txt."` after performing the `ls > output.txt` operation.
                    *   For a question like "Create a shell script which checks a file exists or not in a given directory. If it doesnt exist, create that file. If it exists , delete that file.": The script must `echo` messages like `echo "File 'filename' exists. Deleting..."` or `echo "File 'filename' does not exist. Creating..."`.
        *   `requiredModules`: Usually leave empty. Mention required command-line utilities only if they are non-standard (e.g., `jq`). Standard utilities like `ls`, `grep`, `test`, `rm`, `touch`, `echo` do not need listing.
        *   `variablesAndConstants`: Describe important shell variables (e.g., script arguments `$1`, `$2`, loop variables, variables holding filenames/paths from user input or command substitution).
        *   `functions`: Describe any shell functions defined (`my_func() {{ ... }}`) or explain the purpose of key command blocks/pipelines (e.g., the `if/then/else` block for checking file existence).
        *   `explanation`: Provide a holistic explanation connecting the script's logic, commands, and variables. Explain how the task is achieved using shell features. **Crucially, explain how the `echo` feedback generated demonstrates the script's actions and results. If analyzing user-provided script lacking required feedback, state this limitation.**

    **OUTPUT FORMAT:**

    **CRITICAL:** Respond *only* with a valid JSON object. Do not include any text before or after the JSON structure.
    Use the following exact structure. For any section that was *not* requested, use an empty string `""`. Do *not* omit the key.

    {shell_json_template}

    Ensure all string values within the JSON are properly escaped (newlines `\\n`, quotes `\\"`, tabs `\\t`, etc.). Use newline characters (`\\n`) for list separation within JSON string values.
    """
#havto separate the json frm prompt
#also rename below fn to c generation prompt


def get_c_generation_prompt(question: str, code_instruction: str, options_list: str) -> str:
    """Returns the prompt optimized for generating C program documentation."""
    return f"""
    **ROLE AND GOAL:**
    You are an expert C programmer and Operating Systems Teaching Assistant. Your goal is to help a university student prepare for their OS Lab Exam by generating clear, accurate, and educational documentation for a given problem, including functional C code with specific output requirements when requested.
    
    **CONTEXT:**
    The student needs to understand OS concepts and their C implementation, including how to verify the results through program output. The output should be suitable for studying for a practical lab exam. Assume the student has basic C programming knowledge but needs detailed explanations for OS algorithms and their implementation specifics.

    **TASK:**
    Based on the user's question and potentially provided C code, generate the specified documentation sections. Ensure accuracy, clarity, and relevance. **Pay close attention to the mandatory output requirements for generated code.**
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
        *   **Mandatory Output in Generated Code:** When generating C code (i.e., no code provided by user), it *must* include `printf` statements to clearly display the results of the simulation or operation. See the `code` section guideline below for specific required output formats based on the problem type.


    *   **Specific Section Guidelines (Only generate content for requested sections):**
        *   `overview`: Provide a brief, high-level explanation of the core OS concept addressed in the question (e.g., what is FCFS scheduling? What is shared memory IPC?).
        *   `shortAlgorithm`: List the main steps of the algorithm concisely using a numbered list (e.g., 1., 2., 3.). Focus on the core logic and flow, omitting deep implementation details or variable names unless essential for clarity. Aim for 4-7 high-level steps, similar to the provided examples (e.g., "1. Define Structure. 2. Input data. 3. Loop/Process logic. 4. Calculate results. 5. Display output.").
        *   `detailedAlgorithm`: Provide a step-by-step, implementation-oriented algorithm. Mention key data structures (like `struct Process`), main loops, function calls, and decision logic. Number the steps clearly (e.g., 1. Define Structure, 2. Input, 3. Sort...). This should closely map to the code (provided or generated).
        *   `code`: Present the complete C code solution. If code was provided by the user, present that code, potentially with minor formatting improvements for readability. If no code was provided, generate a functional, well-commented C implementation. Use standard libraries (like `stdio.h`, `stdlib.h`, `limits.h`, `pthread.h`, `semaphore.h`, `sys/ipc.h`, `sys/shm.h` where appropriate).**This generated code MUST include the appropriate output printing as specified below:**
        *   `code`:
            *   If code was provided: Present that code, potentially with minor formatting improvements.
            *   If no code was provided: Generate a functional, well-commented C implementation using standard libraries. **This generated code MUST include the appropriate output printing as specified below:**
            *   **Required Output Formats in Generated Code:**
                *   **Memory Allocation (First/Best/Worst Fit):** Must print the final state of memory blocks, showing their size and which process ID is allocated (or 'Free'/'Not Allocated'). Use a clear table format, e.g., `printf("Block Size\\tProcess ID\\n");` followed by loops printing `printf("%d\\t\\tProcess %d\\n", block_size, process_id);` or `printf("%d\\t\\tNot Allocated\\n", block_size);`.
                *   **CPU Scheduling (FCFS, SJF, RR, Priority):** Must print a textual Gantt chart representation (e.g., `| P1 (5) | P3 (12) | ... ` showing process ID and completion time of that segment). Must also print a final table summarizing results (PID, AT, BT, CT, TAT, WT). Use clear headers like `printf("PID\\tAT\\tBT\\tCT\\tTAT\\tWT\\n");` followed by process details. Calculate and print Average Waiting Time and Average Turnaround Time.
                *   **Banker's Algorithm:** Must print a clear message indicating if the system is in a "Safe State" or an "Unsafe State". If safe, it must print the calculated "Safe Sequence: Px Py Pz ...".
                *   **IPC/Synchronization (Shared Memory, Producer-Consumer):** Must include `printf` statements showing key actions from the perspective of each participant (e.g., `Parent: Writing data '...'`, `Child: Reading data '...'`, `Producer: Produced item X`, `Consumer: Consumed item Y`).
        *   `requiredModules`: List the necessary `#include` directives (e.g., `#include <stdio.h>`). For each include, briefly explain *why* it's needed (e.g., "`stdio.h`: For standard input/output functions like `printf` and `scanf`.").
        *   `variablesAndConstants`: Describe the key variables, constants, and data structures (like `structs`) used in the code. Explain the purpose of each (e.g., "`struct Process`: Holds process details like PID, AT, BT...; `currentTime`: Tracks the simulation clock."). Align this with the `CODE ANALYSIS` if provided.
        *   `functions`: Describe the purpose and basic logic of each major function in the code (e.g., "`sortByArrivalTime()`: Sorts processes based on arrival time using bubble sort; `fcfs()`: Calculates metrics and prints Gantt chart."). Align this with the `CODE ANALYSIS` if provided.
        *   `explanation`: Provide a holistic explanation of how the code implements the algorithm and solves the problem. Connect the algorithm steps to the code logic, variables, and functions. Explain *how* the OS concept is demonstrated. For scheduling algorithms, explain how the Gantt chart (if applicable) is derived and what it represents. For IPC/Sync problems, explain the roles of different processes/threads and synchronization primitives.**Crucially, explain how the output generated by the code (e.g., the allocation table, Gantt chart, safe sequence, IPC messages) demonstrates the algorithm's behavior and results. If analyzing user-provided code that lacks the required output, explicitly state this limitation.**

    **OUTPUT FORMAT:**

    **CRITICAL:** Respond *only* with a valid JSON object. Do not include any text before or after the JSON structure.
    Use the following exact structure. For any section that was *not* requested in the "REQUESTED DOCUMENTATION SECTIONS" list above, use an empty string `""` as its value. Do *not* omit the key.
    {c_json_template}

    Ensure all string values within the JSON are properly escaped if they contain special characters like newlines (\\n), quotes (\"), tabs (\\t), etc. For lists within sections (like algorithms or modules), use newline characters (\\n) for separation within the JSON string value.
    """




# --- Main Orchestration Function ---
def generate_documentation_with_ai(question: str, code: Optional[str], options: Dict[str, bool]):
    """
    Generates documentation using a two-step process:
    1. Detect language (C or Shell).
    2. Call the appropriate language-specific generation prompt.
    """

    # Step 1: Detect Language
    language = detect_language(question, model) # Pass the model instance

    # --- Prepare Inputs for Generation Prompt ---
    is_shell_script_provided = code and code.strip().startswith("#!/")
    parsed_code_info = ""

    # Perform C parsing only if language is C and code is provided and doesn't look like shell
    if language == "C" and code and not is_shell_script_provided:
        try:
            includes = CParser.extract_includes(code)
            functions = CParser.extract_functions(code)
            variables = CParser.extract_variables(code)
            parsed_code_info = f"""
        CODE ANALYSIS (C):
        - Includes: {', '.join(includes) if includes else 'None detected'}
        - Functions: {', '.join([f['name'] for f in functions]) if functions else 'None detected'}
        - Key Variables/Structs: {', '.join([f"{v['type']} {v['name']}" for v in variables]) if variables else 'None detected'}
        Use this analysis to inform your documentation.
        """
        except Exception as e:
            print(f"Warning: C Code parsing failed - {e}")
            parsed_code_info = "\n        CODE ANALYSIS: Could not perform static C code analysis.\n"
    elif is_shell_script_provided:
         parsed_code_info = "\n        CODE ANALYSIS: Provided code appears to be a Shell script. Analysis skipped.\n"


    requested_sections = [option for option, selected in options.items() if selected]
    options_list = "\n".join([f"- {section}" for section in requested_sections])

    code_instruction = ""
    code_block_lang = "c" # Default for C
    if language == "Shell":
        code_block_lang = "bash"

    if code:
        # Adjust code block language tag based on provided code if possible
        if is_shell_script_provided:
            code_block_lang = "bash"
        elif language == "C": # Only assume C if detected language is C
             code_block_lang = "c"
        # If language is Shell but provided code doesn't start with #!/, still tag as bash
        elif language == "Shell":
             code_block_lang = "bash"


        code_instruction = f"""
    CODE PROVIDED BY USER:
    ```{code_block_lang}
    {code}
    ```
    {parsed_code_info}
    Focus your documentation on THIS specific code. Ensure algorithms/explanations reflect its logic. **Verify if it includes necessary output/feedback. If not, mention this limitation in the 'explanation'.**
    """
    else:
        code_instruction = f"""
    CODE PROVIDED BY USER: None
    Generate a standard, correct, and well-commented implementation in **{language}**. **Crucially, ensure the generated code includes the mandatory output/feedback specified in the {language} guidelines.** Base other relevant sections on this generated code.
    """

    # Step 2: Select and Call Generation Prompt
    if language == "Shell":
        prompt = get_shell_generation_prompt(question, code_instruction, options_list)
    else: # Default to C
        prompt = get_c_generation_prompt(question, code_instruction, options_list)


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