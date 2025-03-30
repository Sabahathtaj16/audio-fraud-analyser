# FraudShield AI 🛡️

**Tagline:** FraudShield AI: Your Digital Call Guardian.

## Overview

FraudShield AI is a Streamlit web application contained within the `myfraud.py` script. It helps users identify potentially fraudulent or spam phone calls by analyzing uploaded audio recordings using Google's Gemini 1.5 Flash LLM. The system classifies calls as Normal, Spam, or Fraud, provides reasoning, and allows users to report suspicious calls via email (using Gmail). User authentication and analysis results are managed using a local SQLite database.

## Problem Statement

Voice-based scams, including aggressive spam, phishing attempts, and impersonation of authorities ("digital arrest"), are a growing threat. FraudShield AI provides an accessible tool to analyze suspicious call recordings and empower users with AI-driven insights to enhance their security against these sophisticated tactics.

## Features

*   **User Authentication:** Secure registration and login (bcrypt hashing).
*   **Audio Upload:** Supports WAV, MP3, M4A file formats.
*   **AI-Powered Call Analysis (Gemini 1.5 Flash):**
    *   Audio Transcription (implicit).
    *   Call Classification (Normal, Spam, Fraud/Digital Arrest).
    *   Reasoning Generation.
*   **Result Display:** Clear presentation of classification and reason.
*   **Database Logging (SQLite):** Stores user info and analysis history.
*   **User Reporting (Gmail):** Option to email reports for Spam/Fraud classifications.
*   **Web Interface:** User-friendly interface built with Streamlit.
*   **Performance Metrics:** Displays system performance based on initial testing.


## Technology Stack

*   **Language:** Python 3.x
*   **Web Framework:** Streamlit
*   **AI/LLM:** Google Gemini API (`google-generativeai` library)
*   **Database:** SQLite (`sqlite3` module)
*   **Authentication:** `bcrypt` library
*   **Email:** `smtplib`, `ssl`, `email.message` (for Gmail integration)
*   **Core Libraries:** `os`, `tempfile`, `datetime`, `numpy`, `soundfile`

## Setup and Installation

**Prerequisites:**

*   Python 3.8+ installed.
*   Pip (Python package installer) available.
*   Google Cloud Account with Gemini API enabled.
*   Gmail Account with 2-Step Verification enabled and an App Password generated specifically for this application.

**Configuration (CRITICAL SECURITY WARNING!)**

⚠️ **EXTREMELY IMPORTANT:** This project currently requires you to place sensitive API keys and credentials **directly inside the `myfraud.py` code file**. This is **highly insecure** if the file is shared or not properly protected. Anyone with access to the file can see your keys and password. Use this method only for strictly private testing and understand the risks. For any deployment, use a secure method like Streamlit Secrets or environment variables.

1.  **Obtain the Code:** Get the `myfraud.py` file.

2.  **Install Dependencies:** Open your terminal or command prompt and run:
    ```bash
    pip install streamlit bcrypt google-generativeai numpy soundfile
    ```
    *(Optionally, create a `requirements.txt` file with these package names and run `pip install -r requirements.txt`)*

3.  **Configure Credentials within `myfraud.py`:**
    *   Open the `myfraud.py` file in a text editor.
    *   Scroll down to the **Configuration section** (around line 30-40, marked with `# 2. API Keys, Email Credentials...`).
    *   **Carefully replace** the placeholder values directly in the code:
        *   `GEMINI_API_KEY = "AIzaSy..."` **<-- Replace with your Gemini API Key**
        *   `SENDER_EMAIL = "madihakhan83100@gmail.com"` **<-- Verify this is your intended sender Gmail**
        *   `SENDER_APP_PASSWORD = "fhsz fows nvaz fwwy"` **<-- Replace with your 16-character Gmail App Password**
        *   `RECEIVER_EMAIL = "fraud83100@gmail.com"` **<-- Verify this is the correct recipient email**
    *   Save the `myfraud.py` file after editing.

**Running the Application:**

1.  Navigate to the directory containing `myfraud.py` in your terminal.
2.  Run the command:
    ```bash
    streamlit run myfraud.py
    ```
3.  Streamlit will provide a local URL (e.g., `http://localhost:8501`). Open this URL in your web browser.

## Usage

1.  Access the application via the URL provided by Streamlit.
2.  **Register/Login:** Use the tabs to create an account or log in.
3.  **Upload Audio:** Once logged in, use the file uploader to select a WAV, MP3, or M4A file.
4.  **Analyze:** Click "Analyze Call".
5.  **Review Results:** View the classification (Normal, Spam, Fraud) and the AI's reason.
6.  **(Optional) Report:** If classified as Spam or Fraud, click the red "Report..." button to email the details to the configured support address.
7.  **Logout:** Click the logout button to end the session.

## Performance Metrics (Based on Initial 85-Call Test Set)



*   **Overall Accuracy:** ~82.35%
*   **Precision:** Fraud (~82.14%), Spam (~79.41%), Normal (~86.96%)
*   **Recall:** Fraud (~76.67%), Spam (~84.38%), Normal (~86.96%)



## Future Outlook

*   Real-time analysis capabilities.
*   Integration with VoIP/Mobile platforms.
*   Model fine-tuning or exploration of larger models.
*   Structured data output from LLM.
*   Adaptive learning from user feedback.
*   Multi-language support expansion.
*   Administrator dashboard for analytics.
*   **Crucially:** Implement secure credential management (Secrets/Environment Variables).

