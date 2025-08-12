#ONLY FOR TESTING
import os
import subprocess

def insecure_program(user_input):
    """
    This function contains common vulnerabilities for demonstration purposes.
    DO NOT use this code in a production environment.
    """

    # 1. Command Injection
    # The user input is directly passed to the shell without sanitization.
    # An attacker could enter 'ls; rm -rf /' to delete files.
    print(f"--- 1. Command Injection ---")
    print(f"Executing: ping -c 1 {user_input}")
    try:
        subprocess.run(f"ping -c 1 {user_input}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during command injection attempt: {e}")
    print("-" * 30)

    # 2. Path Traversal (Directory Traversal)
    # The program is susceptible to path traversal, allowing access to files outside the intended directory.
    # An attacker could use '..%2F..%2Fetc%2Fpasswd' to read system files.
    print(f"--- 2. Path Traversal ---")
    file_path = os.path.join("vulnerable_files", user_input)
    try:
        with open(file_path, "r") as f:
            print(f"Contents of {file_path}:\n{f.read()}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error during path traversal attempt: {e}")
    print("-" * 30)

    # 3. Insecure Deserialization
    # This example uses `eval` which is extremely dangerous. An attacker can execute arbitrary code.
    print(f"--- 3. Insecure Deserialization ---")
    insecure_data = f"result = 5 + 5\nprint(f'The result of an insecure eval is: {{result}}')"
    print(f"Executing `eval` with insecure data...")
    try:
        eval(insecure_data)
    except Exception as e:
        print(f"Error during insecure deserialization attempt: {e}")
    print("-" * 30)

    # 4. SQL Injection (Conceptual)
    # This is a conceptual example without a real database. It demonstrates the dangerous string formatting.
    # The user input is directly inserted into the query string.
    # An attacker could enter `' OR '1'='1` to bypass authentication.
    print(f"--- 4. SQL Injection ---")
    user_id = user_input
    sql_query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"Simulated SQL query: {sql_query}")
    print("This query is vulnerable to SQL injection.")
    print("-" * 30)


if __name__ == "__main__":
    # Create a dummy directory and file for the path traversal example
    os.makedirs("vulnerable_files", exist_ok=True)
    with open("vulnerable_files/secret.txt", "w") as f:
        f.write("This is a secret file.\n")

    # Example of how an attacker might use these vulnerabilities
    print("Running the program with a malicious input ('127.0.0.1; ls -la')...")
    insecure_program("127.0.0.1; ls -la")
    print("\n" + "="*50 + "\n")
    print("Running the program with a path traversal input ('../secret.txt')...")
    insecure_program("../secret.txt")