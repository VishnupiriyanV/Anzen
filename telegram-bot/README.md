# **AI-Powered Security Scan Telegram Bot**

This project is a Telegram bot that automates the process of scanning Git repositories for security vulnerabilities. It uses **Semgrep** for static analysis and the **Groq API** (running Llama 3\) to provide AI-powered analysis and remediation suggestions for the findings.

## **Features**

* **Git Integration**: Clones any public Git repository directly from a URL.  
* **Automated Scanning**: Uses Semgrep with its automatic configuration (--config auto) to scan a wide range of languages.  
* **AI-Powered Analysis**: Each finding from the Semgrep scan is sent to the Groq API for analysis to determine if it's a likely false positive and to suggest code fixes.  
* **Simple Bot Interface**: Interact with the bot through simple commands in Telegram.  
* **Clean JSON Output**: Delivers a single, enriched JSON file containing the original scan results plus the AI analysis and remediation advice.

## **How It Works**

The bot follows a simple, powerful pipeline:

1. **Command**: A user sends the /scan \<repository\_url\> command to the bot in Telegram.  
2. **Clone**: The bot's server clones the specified Git repository into a temporary directory.  
3. **Filter**: It filters the cloned repository to include only relevant source code files, ignoring assets and other non-code files.  
4. **Scan**: **Semgrep** is run on the filtered code. The results are saved as a JSON file.  
5. **Analyze**: The bot iterates through each finding in the Semgrep JSON output. For each one, it calls the **Groq API** with a prompt asking for analysis and a remediation plan.  
6. **Enrich**: The AI's response (analysis and remediation) is added back into the JSON data for that specific finding.  
7. **Report**: The final, enriched analyzed\_security\_report.json file is sent back to the user in the Telegram chat. All temporary files and directories are cleaned up.

## **Setup and Installation**

Follow these steps to get the bot running on your own server.

### **1\. Prerequisites**

Make sure you have the following installed on your system:

* Python 3.8+  
* Git  
* Semgrep CLI

You can install Semgrep easily via pip:  
pip install semgrep

### **2\. Clone the Repository**

Clone this project to your local machine or server.  
\# Replace with your repository's URL if you've hosted it  
git clone https://your-repository-url.git  
cd your-repository-directory

### **3\. Install Python Dependencies**

The required Python libraries are python-telegram-bot, GitPython, and groq.  
pip install python-telegram-bot \--upgrade  
pip install GitPython  
pip install groq

### **4\. Configuration**

You must provide your own API keys for the bot to function. Open the Python script and replace the placeholder values for the following constants:

* TELEGRAM\_BOT\_TOKEN: Your token from the Telegram BotFather.  
* GROQ\_API\_KEY: Your API key from the GroqCloud console.

\# \--- CONFIGURATION \---  
\# IMPORTANT: Replace these with your actual tokens.  
TELEGRAM\_BOT\_TOKEN \= "YOUR\_TELEGRAM\_BOT\_TOKEN"  
GROQ\_API\_KEY \= "YOUR\_GROQ\_API\_KEY"

### **5\. Run the Bot**

Once the dependencies are installed and the configuration is set, you can start the bot:  
python your\_script\_name.py

The bot will start polling for messages from Telegram.

## **Usage**

You can interact with the bot using the following commands in its Telegram chat.

* **/start**  
  * Displays a welcome message and provides a brief overview of how to use the bot.  
* **/scan \<repository\_url\>**  
  * This is the main command. It kicks off the entire scanning and analysis pipeline.  
  * **Example**: /scan https://github.com/someuser/some-repo

The bot will send a temporary message to let you know it has started. Once the process is complete, that message will be deleted, and the final JSON report will be uploaded to the chat.