# Anzen AI

Anzen AI is a web application that analyzes source code repositories for security vulnerabilities.
It supports 35+ programming languages and works directly with GitHub repositories.

## Features

Repository Scanning – Provide a GitHub repository URL, and Anzen AI will fetch and scan the codebase.

Multi-Language Support – Detect vulnerabilities in over 35 programming languages.

Automated Analysis – Uses advanced AI-powered scanning for security issues.

JSON Output – Results are returned as structured JSON for further processing or integration.

No Installation Required – Works directly from your browser via a simple web interface.

## How It Works

Enter Repository URL – Paste the GitHub repository link in the provided field.

Automatic Cloning – The backend fetches the repository source.

Vulnerability Scanning – Code is analyzed using a multi-language security analysis engine.

View Results – See detailed JSON output with vulnerability types, affected files, and severity levels.

## Anzen Lite

Extension for VS Code that runs locally, a lite version of Anzen without AI features. Install using the VSIX file.

## Usage
1. Install Dependency:
   ```bash
   pip install semgrep
   ```
2. Open a file in VS Code.
3. Press `Cmd+Shift+P` → "Anzen Lite".
4. Vulnerabilities will be highlighted in red.

## Anzen AI Telegram Bot

Scan your GitHub repositories for vulnerabilities directly from Telegram.

## Usage:

Open the Anzenatorbot on Telegram.

Send your GitHub repository link.

Get a detailed vulnerability report in seconds.

Supports 35+ languages.

![Logo](logo.jpeg)
