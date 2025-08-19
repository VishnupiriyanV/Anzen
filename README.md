
# Anzen AI

Anzen AI is a web application that analyzes source code repositories for security vulnerabilities.

## Features

- Repository Scanning – Provide a GitHub repository URL, and Anzen AI will fetch and scan the codebase.
- Multi-Language Support – Detect vulnerabilities in over 35 programming languages.
- Automated Analysis – Uses advanced AI-powered scanning for security issues.
- JSON Output – Results are returned as structured JSON for further processing or integration.
- No Installation Required – Works directly from your browser via a simple web interface.


## Run Locally

**To Deploy Frontend**
Clone the project


```bash
  git clone https://github.com/VishnupiriyanV/Anzen.git
```


Go to the project directory

```bash
  cd Anzen
```

**To Deploy Frontend**

```bash
    cd frontend

```

Install dependencies

```bash
  npm install
```

To start the Frontend

```bash
  npm run dev
```

**To Deploy Backend**

Change directory
```bash
    cd backend
```

Create a virtual environment
```bash
    python3 -m venv venv
    .\venv\Scripts\activate
```

Run app.py

```bash
    python3 app.py
```


## Tech Stack

**Frontend:** React.js, TailwindCSS 

**Backend:** Flask, Semgrep (Static Code Analysis), Grok API (False Positive Analysis and Code Remediation), SQLAlchemy

**Database:** MySQL



## Authors

- [Vishal M](https://github.com/Valiant-Vishal)
- [Deepthi Muthukumar](https://github.com/deepthimuthu77)
- [Nishanth S](https://github.com/NishanthGit3)
- [Vishnupiriyan V](https://github.com/VishnupiriyanV)