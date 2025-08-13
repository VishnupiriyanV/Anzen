import json
import os
from groq import Groq

<<<<<<< HEAD
# Set API key (replace with secure method when deploying)
os.environ["GROQ_API_KEY"] = "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"

# Initialize Groq client
client = Groq(api_key=os.environ["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"])
print("Groq client initialized successfully!")
=======

>>>>>>> 8fd3f2c28d7cf71fec4ae66beec0d28274100106

INPUT_FILENAME = 'semgrep_results.json'
OUTPUT_FILENAME = 'semgrep_results_analyzed.json'

def analyze_finding(client, result):
    """Analyzes a single Semgrep finding using the Groq API."""
    check_id = result.get('check_id')
    path = result.get('path')
    start_line = result.get('start', {}).get('line', '?')
    end_line = result.get('end', {}).get('line', '?')
    message = result.get('extra', {}).get('message', '')
    code_snippet = result.get('extra', {}).get('lines', '')

    prompt = (
        f"You are a helpful security analyst. Analyze the following security finding from a Semgrep scan:\n\n"
        f"File: {path}\n"
        f"Lines: {start_line}-{end_line}\n"
        f"Check ID: {check_id}\n"
        f"Message: {message}\n\n"
        f"Code Snippet:\n``````\n\n"
        f"Please provide your analysis in the following format:\n"
        f"1. **False Positive Analysis:** Based on the code and the finding, is this a likely false positive? Explain.\n"
        f"2. **Code Remediation:** If true positive, provide a secure code remediation."
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
<<<<<<< HEAD
        content = chat_completion.choices[0].message.content or ""

=======
        
        content = chat_completion.choices[0].message.content
        
>>>>>>> 8fd3f2c28d7cf71fec4ae66beec0d28274100106
        false_positive_analysis = "Not found in response."
        remediation = "Not found in response."

        lower_content = content.lower()
        if "false positive analysis:" in lower_content:
            parts = content.split("False Positive Analysis:")
            if len(parts) > 1:
                sub_parts = parts[1].split("Code Remediation:")
                false_positive_analysis = sub_parts[0].strip()

        if "code remediation:" in lower_content:
            parts = content.split("Code Remediation:")
            if len(parts) > 1:
                remediation = parts[1].strip()

        return false_positive_analysis, remediation

    except Exception as e:
        print(f"Groq API error: {e}")
        return None, None


def main():
<<<<<<< HEAD
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: Groq API key not configured.")
=======
    
    
    api_key = "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" 

    if api_key == "your_actual_api_key_here":
        print("ERROR: Please replace 'your_actual_api_key_here' with your real Groq API key in the script.")
        return

    
    try:
        client = Groq(api_key=api_key)
        print("Groq client initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
>>>>>>> 8fd3f2c28d7cf71fec4ae66beec0d28274100106
        return

    try:
        with open(INPUT_FILENAME, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{INPUT_FILENAME}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{INPUT_FILENAME}'.")
        return

    results = data.get('results', [])
    for result in results:
        print(f"Analyzing finding in: {result.get('path')}:{result.get('start', {}).get('line')}")
<<<<<<< HEAD
        false_positive_analysis, remediation = analyze_finding(result)
=======
        
        false_positive_analysis, remediation = analyze_finding(client, result)

>>>>>>> 8fd3f2c28d7cf71fec4ae66beec0d28274100106
        if 'extra' not in result:
            result['extra'] = {}
        result['extra']['llm_false_positive_analysis'] = false_positive_analysis
        result['extra']['llm_code_remediation'] = remediation

    try:
        with open(OUTPUT_FILENAME, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nAnalysis complete. Results saved to '{OUTPUT_FILENAME}'.")
    except IOError as e:
        print(f"Error writing '{OUTPUT_FILENAME}': {e}")

if __name__ == '__main__':
    main()
