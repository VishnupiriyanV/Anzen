import os
import shutil
import subprocess
import json
import logging
from git import Repo, exc
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


TELEGRAM_BOT_TOKEN = "Bot token"
GROQ_API_KEY = "Give your API key"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLONED_DIR = os.path.join(BASE_DIR, "cloned_repo")
FILTERED_DIR = os.path.join(BASE_DIR, "filtered_code")
SEMGREP_RESULTS_FILE = os.path.join(BASE_DIR, "semgrep_results.json")
ANALYZED_RESULTS_FILE = os.path.join(BASE_DIR, "semgrep_results_analyzed.json")


def cleanup_directories():
    """Removes old directories and files from previous runs."""
    logger.info("Cleaning up old directories and files...")
    for path in [CLONED_DIR, FILTERED_DIR, SEMGREP_RESULTS_FILE, ANALYZED_RESULTS_FILE]:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
        except OSError as e:
            logger.error(f"Error during cleanup: {e}")


def run_semgrep_scan(repo_url: str) -> str | None:
    """
    Clones a Git repo, filters for specific code files, and runs a Semgrep scan.
    This function combines the logic from your 'main-git.py'.

    Args:
        repo_url: The URL of the Git repository to scan.

    Returns:
        The path to the Semgrep JSON results file, or None if an error occurred.
    """
    try:
        logger.info(f"Cloning repository: {repo_url}")
        Repo.clone_from(repo_url, CLONED_DIR)
    except exc.GitCommandError as e:
        logger.error(f"Failed to clone repo. Is the URL correct? Error: {e}")
        return None

    # Extensions to keep for the scan
    extensions = {
        ".cs", ".go", ".java", ".js", ".kt", ".kts", ".py", ".ts", ".c", ".cpp",
        ".cc", ".cxx", ".h", ".hpp", ".hh", ".hxx", ".jsx", ".rb", ".scala",
        ".swift", ".rs", ".php", ".tf", ".tfvars", ".hcl", ".generic", ".json",
        ".ex", ".exs", ".cls", ".trigger", ".dart"
    }

    os.makedirs(FILTERED_DIR, exist_ok=True)
    logger.info("Filtering for relevant code files...")
    for root, _, files in os.walk(CLONED_DIR):
        for file in files:
            if os.path.splitext(file)[1].lower() in extensions:
                shutil.copy(os.path.join(root, file), FILTERED_DIR)

    logger.info("Running Semgrep scan...")
    try:
        cmd = ["semgrep", "--config", "auto", FILTERED_DIR, "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        with open(SEMGREP_RESULTS_FILE, "w") as f:
            json.dump(json.loads(result.stdout), f, indent=2)
        logger.info(f"Semgrep scan complete. Results saved to {SEMGREP_RESULTS_FILE}")
        return SEMGREP_RESULTS_FILE
    except FileNotFoundError:
        logger.error("Semgrep command not found. Is Semgrep installed and in your PATH?")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Semgrep scan failed: {e.stdout}")
        return None


def analyze_finding_with_ai(client: Groq, finding: dict) -> tuple[str, str]:
    """
    Analyzes a single Semgrep finding using the Groq API.
    This function is from your 'ai-main.py'.
    """
    path = finding.get('path')
    start_line = finding.get('start', {}).get('line')
    message = finding.get('extra', {}).get('message')
    code_snippet = finding.get('extra', {}).get('lines')

    prompt = (
        f"You are a security analyst. Analyze the following Semgrep finding:\n\n"
        f"File: {path}\n"
        f"Line: {start_line}\n"
        f"Message: {message}\n"
        f"Code:\n```\n{code_snippet}\n```\n\n"
        f"Provide a brief analysis of whether this is a likely false positive and suggest a code remediation if it is a true positive."
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        content = chat_completion.choices[0].message.content
        # Simple parsing for demonstration. You can improve this.
        false_positive_analysis = content.split("Code Remediation:")[0].strip()
        remediation = content.split("Code Remediation:")[-1].strip() if "Code Remediation:" in content else "N/A"
        return false_positive_analysis, remediation
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return "Error during analysis.", "Could not retrieve remediation."


def run_ai_analysis(groq_client: Groq, input_json_path: str) -> str | None:
    """
    Reads a Semgrep results file and enriches it with AI analysis.
    This function combines the logic from your 'ai-main.py'.

    Args:
        groq_client: An initialized Groq API client.
        input_json_path: The path to the Semgrep results JSON file.

    Returns:
        The path to the analyzed results file, or None if an error occurred.
    """
    logger.info(f"Starting AI analysis on {input_json_path}")
    try:
        with open(input_json_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Could not read or parse the Semgrep results file: {e}")
        return None

    results = data.get('results', [])
    for result in results:
        logger.info(f"Analyzing finding in: {result.get('path')}:{result.get('start', {}).get('line')}")
        analysis, remediation = analyze_finding_with_ai(groq_client, result)
        result['extra']['llm_analysis'] = analysis
        result['extra']['llm_remediation'] = remediation

    try:
        with open(ANALYZED_RESULTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"AI analysis complete. Results saved to {ANALYZED_RESULTS_FILE}")
        return ANALYZED_RESULTS_FILE
    except IOError as e:
        logger.error(f"Could not write the final analyzed file: {e}")
        return None


# --- Telegram Bot Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hi! I'm a Security Scan Bot. "
        "Send me a Git repository URL using the /scan command and I'll send back a JSON security report.\n\n"
        "Usage: /scan <repository_url>"
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /scan command. Runs the analysis and sends the
    resulting JSON file.
    """
    if not context.args:
        await update.message.reply_text("Please provide a repository URL.\nUsage: /scan <repository_url>")
        return

    repo_url = context.args[0]
    chat_id = update.message.chat_id

    # Acknowledge the command and inform the user that the process is starting.
    # This is important because the scan can take a while.
    processing_message = await context.bot.send_message(
        chat_id,
        f"Scanning {repo_url}... this may take a few minutes."
    )

    # Clean up before starting
    cleanup_directories()

    # --- Step 1: Run Semgrep Scan ---
    semgrep_file = run_semgrep_scan(repo_url)
    if not semgrep_file:
        await processing_message.edit_text("Failed to run the Semgrep scan. Please check the repository URL and make sure Semgrep is installed correctly on the server.")
        return

    # --- Step 2: Run AI Analysis ---
    analyzed_file = run_ai_analysis(context.bot_data['groq_client'], semgrep_file)
    if not analyzed_file:
        await processing_message.edit_text("Failed during the AI analysis phase. The raw Semgrep results are available on the server if needed.")
        return

    # --- Step 3: Send the final report to the user ---
    try:
        # Delete the "Scanning..." message before sending the file
        # to make the output cleaner.
        await processing_message.delete()

        with open(analyzed_file, 'rb') as document:
            await context.bot.send_document(chat_id, document=document, filename="analyzed_security_report.json")
    except FileNotFoundError:
         await context.bot.send_message(chat_id, "Sorry, I couldn't find the final report file to send.")
    finally:
        # Clean up after a successful run
        cleanup_directories()


def main() -> None:
    """Starts the Telegram bot."""
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or GROQ_API_KEY == "YOUR_GROQ_API_KEY":
        print("!!! IMPORTANT !!!")
        print("Please open the script and replace 'YOUR_TELEGRAM_BOT_TOKEN' and 'YOUR_GROQ_API_KEY' with your actual keys.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Initialize the Groq client and add it to bot_data so it's accessible in handlers
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        application.bot_data['groq_client'] = groq_client
        logger.info("Groq client initialized successfully.")
    except Exception as e:
        logger.fatal(f"Failed to initialize Groq client: {e}")
        return

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("scan", scan))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is running. Press Ctrl-C to stop.")
    application.run_polling()


if __name__ == '__main__':
    main()
