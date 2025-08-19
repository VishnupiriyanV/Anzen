import json
import os
from groq import Groq
import subprocess



INPUT_FILENAME = 'semgrep_results.json'
OUTPUT_FILENAME = 'semgrep_results_analyzed.json'

def analyze_finding(client, result):
    """Analyzes a single Semgrep finding using the Groq API."""
    check_id = result.get('check_id')
    path = result.get('path')
    start_line = result.get('start', {}).get('line')
    end_line = result.get('end', {}).get('line')
    message = result.get('extra', {}).get('message')
    code_snippet = result.get('extra', {}).get('lines')

    prompt = (
        f"You are a helpful security analyst. Analyze the following security finding from a Semgrep scan:\n\n"
        f"File: {path}\n"
        f"Lines: {start_line}-{end_line}\n"
        f"Check ID: {check_id}\n"
        f"Message: {message}\n\n"
        f"Code Snippet:\n```\n{code_snippet}\n```\n\n"
        f"Please provide your analysis in the following format:\n"
        f"1.  **False Positive Analysis:** Based on the code and the finding, is this a likely "
        f"false positive? Please explain your reasoning.\n"
        f"2.  **Code Remediation:** If this is a true positive, provide a secure code "
        f"remediation. The remediation should be a drop-in replacement for the snippet if possible."
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        
        content = chat_completion.choices[0].message.content
        
        false_positive_analysis = "Not found in response."
        remediation = "Not found in response."

        if "False Positive Analysis:" in content:
            parts = content.split("False Positive Analysis:")
            if len(parts) > 1:
                sub_parts = parts[1].split("Code Remediation:")
                false_positive_analysis = sub_parts[0].strip()
        
        if "Code Remediation:" in content:
            parts = content.split("Code Remediation:")
            if len(parts) > 1:
                remediation = parts[1].strip()
            
        return false_positive_analysis, remediation

    except Exception as e:
        print(f"An unexpected error occurred with the Groq API: {e}")
        return None, None


def main():
    
    
    #api_key = "add your API key here" 

    if api_key == "your_actual_api_key_here":
        print("ERROR: Please replace 'your_actual_api_key_here' with your real Groq API key in the script.")
        return

    
    try:
        client = Groq(api_key=api_key)
        print("Groq client initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        return

    try:
        with open(INPUT_FILENAME, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_FILENAME}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{INPUT_FILENAME}'.")
        return

    results = data.get('results', [])
    for result in results:
        print(f"Analyzing finding in: {result.get('path')}:{result.get('start', {}).get('line')}")
        
        false_positive_analysis, remediation = analyze_finding(client, result)

        if 'extra' not in result:
            result['extra'] = {}
            
        result['extra']['llm_false_positive_analysis'] = false_positive_analysis
        result['extra']['llm_code_remediation'] = remediation

    try:
        with open(OUTPUT_FILENAME, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nAnalysis complete. The updated results have been saved to '{OUTPUT_FILENAME}'.")
    except IOError as e:
        print(f"Error writing to file '{OUTPUT_FILENAME}': {e}")
        

if __name__ == '__main__':
    main()
