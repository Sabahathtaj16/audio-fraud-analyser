# 🚀 Streamlit for UI
import streamlit as st

# 🛠 Backend: SQL Database & Authentication
import sqlite3
import bcrypt

# 🎧 Audio Processing
from pydub import AudioSegment # For audio cropping
from pydub.exceptions import CouldntDecodeError

# 💎 Email Notifications
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✅ Other Utilities
import os
import io
import time
import base64

# 🔥 Google Gemini AI
import google.generativeai as genai

# --- Page Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="Audio Analysis Portal",
    page_icon="🔒",
    layout="wide"
)

# ------------------- CONFIGURATION -------------------

# --- Use your actual Gemini API Key ---
# WARNING: Hardcoding keys is insecure. Use secrets management (st.secrets).
GEMINI_API_KEY = "AIzaSyA57hSzsQaxJ5F8r73QSKy6pOe-2c_I1Jo" # Replace with your actual key

# --- Email Configuration ---
# WARNING: Hardcoding credentials is insecure. Use secrets management.
SENDER_EMAIL = "madihakhan83100@gmail.com"      # Replace with your sender email
RECEIVER_EMAIL = "fraud83100@gmail.com"         # Replace with the email to receive reports/feedback
EMAIL_APP_PASSWORD = "fhsz fows nvaz fwwy"      # Replace with your 16-digit Gmail App Password

# --- Database Configuration ---
DB_FILE = "calls.db"

# --- Background Image ---
BACKGROUND_IMAGE_FILE = "background.jpg" # Make sure this file exists

# --- Audio Cropping Config ---
MAX_AUDIO_DURATION_MS = 60 * 1000 # 60 seconds in milliseconds

# --- Initialize Gemini ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash') # Using Flash - faster, potentially slightly less nuanced than Pro
    print("Gemini configured successfully.")
except Exception as e:
    st.error(f"Fatal Error: Could not configure Google Gemini AI. Please check your API Key. Details: {e}")
    print(f"Fatal Error configuring Gemini: {e}")
    gemini_model = None

# ------------------- STYLING -------------------
# (Keep the existing styling functions - get_base64_of_bin_file and set_styles)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f: data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError: st.warning(f"BG image '{bin_file}' not found."); return None
    except Exception as e: st.error(f"Error reading BG image: {e}"); return None

def set_styles():
    bg_image_base64 = get_base64_of_bin_file(BACKGROUND_IMAGE_FILE)
    background_css = f""" background-image: url("data:image/jpeg;base64,{bg_image_base64}"); background-size: cover; background-repeat: no-repeat; background-attachment: fixed; """ if bg_image_base64 else ""
    # Use the same CSS rules as before for white text, inputs, buttons etc.
    st.markdown(f""" <style> .stApp {{ {background_css} }} /* General Text: White */ h1, h2, h3, h4, h5, h6, p, label, li, .stFileUploader > label, .stTextInput > label, .stTextArea > label {{ color: white !important; font-family: sans-serif !important; }} div[data-testid="stSidebar"] h1, div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3, div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] label, div[data-testid="stSidebar"] li {{ color: white !important; }} h1 {{ font-size: 28px !important; font-weight: bold; }} h2 {{ font-size: 24px !important; font-weight: bold; }} h3 {{ font-size: 20px !important; font-weight: bold; }} p, label, li {{ font-size: 18px !important; }} /* Input elements */ div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{ font-size: 16px !important; color: black !important; background-color: rgba(255, 255, 255, 0.9) !important; border: 1px solid #ccc !important; border-radius: 5px; }} div[data-testid="stTextInput"] input::placeholder, div[data-testid="stTextArea"] textarea::placeholder {{ color: #666 !important; }} /* Button Styling */ div[data-testid="stButton"] > button {{ font-size: 16px !important; color: white !important; background-color: #424242 !important; border: 1px solid #616161 !important; border-radius: 5px; padding: 8px 18px; margin: 5px 0; width: 100%; }} div[data-testid="stButton"] > button:hover {{ background-color: #616161 !important; border-color: #757575 !important; }} div[data-testid="stButton"] > button:active {{ background-color: #212121 !important; }} /* Specific Main Button Styles */ .main div[data-testid="stButton"] > button:has(span:contains("Analyze")), .main div[data-testid="stButton"] > button:has(span:contains("Transcribe")), .main div[data-testid="stButton"] > button:has(span:contains("Submit")), .main div[data-testid="stButton"] > button:has(span:contains("Login")), .main div[data-testid="stButton"] > button:has(span:contains("Sign Up")) {{ background-color: #388e3c !important; border-color: #4caf50 !important; }} .main div[data-testid="stButton"] > button:has(span:contains("Analyze")):hover, .main div[data-testid="stButton"] > button:has(span:contains("Login")):hover, .main div[data-testid="stButton"] > button:has(span:contains("Sign Up")):hover {{ background-color: #4caf50 !important; border-color: #66bb6a !important; }} .main div[data-testid="stButton"] > button:has(span:contains("Alert")) {{ background-color: #d32f2f !important; border-color: #f44336 !important; font-weight: bold; }} .main div[data-testid="stButton"] > button:has(span:contains("Alert")):hover {{ background-color: #f44336 !important; border-color: #ef5350 !important; }} .main div[data-testid="stButton"] > button:has(span:contains("Back")) {{ background-color: #757575 !important; border-color: #9e9e9e !important; }} .main div[data-testid="stButton"] > button:has(span:contains("Back")):hover {{ background-color: #9e9e9e !important; border-color: #bdbdbd !important; }} /* Sidebar Buttons */ div[data-testid="stSidebar"] div[data-testid="stButton"] > button {{ background-color: #4a4a4a !important; border: 1px solid #616161 !important; text-align: left; padding: 10px 15px; }} div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{ background-color: #616161 !important; border-color: #757575 !important; }} div[data-testid="stSidebar"] div[data-testid="stButton"] > button:has(span:contains("Logout")) {{ background-color: #b71c1c !important; border-color: #d32f2f !important; }} div[data-testid="stSidebar"] div[data-testid="stButton"] > button:has(span:contains("Logout")):hover {{ background-color: #d32f2f !important; border-color: #f44336 !important; }} </style> """, unsafe_allow_html=True)

# Apply styles early
set_styles()

# ------------------- DATABASE FUNCTIONS -------------------
# (Keep init_db, save_user, authenticate, save_audio_data functions as they were - UI messages are now English)
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY AUTOINCREMENT, user_email TEXT NOT NULL, file_name TEXT NOT NULL, file_data BLOB NOT NULL, classification TEXT NOT NULL, reason TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit(); print("Database initialized successfully.")
    except sqlite3.Error as e: print(f"DB init error: {e}")
    finally:
        if conn: conn.close()
init_db()

def save_user(name, email, password):
    if not name or not email or not password: st.warning("Please fill all fields."); return False
    try:
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_pw))
        conn.commit(); st.success("Registration successful!"); return True
    except sqlite3.IntegrityError: st.error("Email already exists!"); return False
    except sqlite3.Error as e: st.error(f"DB registration error: {e}"); print(f"DB error: {e}"); return False
    finally:
        if conn: conn.close()

def authenticate(email, password):
    if not email or not password: st.warning("Enter email and password."); return False
    try:
        conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email=?", (email,)); user = cursor.fetchone(); conn.close()
        if user and bcrypt.checkpw(password.encode("utf-8"), user[0].encode("utf-8")): return True
        else: st.error("Invalid email or password."); return False
    except sqlite3.Error as e: st.error(f"DB auth error: {e}"); print(f"DB error: {e}"); return False

def save_audio_data(user_email, file_name, audio_bytes, classification, reason):
    try:
        conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
        cursor.execute("INSERT INTO calls (user_email, file_name, file_data, classification, reason) VALUES (?, ?, ?, ?, ?)", (user_email, file_name, audio_bytes, classification, reason))
        conn.commit(); print(f"Audio saved: {file_name}"); return True
    except sqlite3.Error as e: st.error(f"DB error saving audio: {e}"); print(f"DB error saving audio: {e}"); return False
    finally:
        if conn: conn.close()

# ------------------- EMAIL FUNCTIONS -------------------
# (Keep send_email, send_fraud_report, send_feedback_email functions - English UI messages)
def send_email(subject, body, recipient=RECEIVER_EMAIL):
    msg = MIMEMultipart(); msg['From'] = SENDER_EMAIL; msg['To'] = recipient; msg['Subject'] = subject; msg.attach(MIMEText(body, 'plain'))
    try:
        print(f"Sending email: '{subject}' to {recipient}..."); server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD); server.sendmail(SENDER_EMAIL, recipient, msg.as_string()); server.quit(); print("Email sent."); return True
    except smtplib.SMTPAuthenticationError as e: print(f"SMTP Auth Error: {e}"); st.error("Email Auth Failed."); return False
    except Exception as e: print(f"Error sending email: {e}"); st.error(f"Failed to send email: {e}"); return False

def send_fraud_report(user_email, classification, fraud_reason, file_name):
    subject = f"🚨 {classification.upper()} Call Alert: User {user_email} (File: {file_name})"
    body = f"A potentially {classification.lower()} call reported.\n\nUser: {user_email}\nFile: {file_name}\nClass: {classification}\n\nAI Justification:\n{fraud_reason}\n\nReview DB record if needed."
    if send_email(subject, body): st.success(f"{classification} report sent!") # English message

def send_feedback_email(user_email, feedback_text):
    subject = f"📝 User Feedback: {user_email}"
    body = f"Feedback submitted.\n\nUser: {user_email}\n\nFeedback:\n-----------------\n{feedback_text}\n-----------------\n\nTimestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    if send_email(subject, body): st.success("Feedback submitted!") # English message

# ------------------- AUDIO PROCESSING FUNCTION -------------------
# (Keep process_audio function - English UI messages)
def process_audio(audio_bytes, original_filename):
    print(f"Processing audio: {original_filename}")
    cropped = False
    try:
        audio_file_object = io.BytesIO(audio_bytes)
        audio_segment = AudioSegment.from_file(audio_file_object) # Requires ffmpeg for non-wav
        print(f"Audio loaded. Duration: {len(audio_segment) / 1000:.2f}s")
        if len(audio_segment) > MAX_AUDIO_DURATION_MS:
            print(f"Cropping audio to {MAX_AUDIO_DURATION_MS/1000}s...")
            cropped_segment = audio_segment[:MAX_AUDIO_DURATION_MS]
            cropped = True
            st.info(f"Audio cropped to the first {MAX_AUDIO_DURATION_MS/1000} seconds for processing.") # English info
        else:
            cropped_segment = audio_segment
        output_bytes_io = io.BytesIO()
        cropped_segment.export(output_bytes_io, format="wav") # Export as WAV
        cropped_audio_bytes = output_bytes_io.getvalue()
        processed_mime_type = "audio/wav"
        print(f"Processed audio size: {len(cropped_audio_bytes)} bytes, Type: {processed_mime_type}")
        return cropped_audio_bytes, processed_mime_type, cropped
    except CouldntDecodeError as e:
        st.error(f"Error decoding '{original_filename}'. Try WAV/MP3 format. Ensure FFmpeg is installed."); print(f"Pydub decode error: {e}"); return None, None, False
    except Exception as e: st.error(f"Audio processing error: {e}"); print(f"Audio processing error: {e}"); return None, None, False

# ------------------- GEMINI AI FUNCTIONS -------------------

# --- UPDATED FRAUD ANALYSIS PROMPT ---
# Explicitly mention handling various languages in the audio
FRAUD_ANALYSIS_PROMPT = (
    "You are an expert AI assistant specialized in identifying fraudulent phone calls (like digital arrest scams, bank impersonation, tech support scams), differentiating them from general spam and normal conversations, based *only* on the provided audio (maximum 60 seconds)."
    "Analyze the audio recording, **which may be in English or various Indian languages (like Hindi, Bengali,Kannada, Tamil, Telugu, Marathi, etc.)**, meticulously and classify it into ONE category: 'Fraud', 'Spam', 'Normal', or 'Unclear/Empty'. Apply the rules below regardless of the language detected in the audio."

    "**Classification Rules (Apply Strictly):**\n"
    "1.  **Fraud:** Classify as 'Fraud' ONLY if the call exhibits **clear indicators of deception combined with high-pressure tactics aimed at extracting sensitive information or money.** Key indicators include:\n"
    "    *   **Impersonation:** Caller claims to be from a position of authority (Police, CBI, TRAI, DoT, RBI, Bank Security, Tax Dept, Court, major company like Microsoft/Amazon *in a context unrelated to a recent transaction*) AND the context is unsolicited/suspicious.\n"
    "    *   **Urgency/Threats:** Creates extreme, immediate pressure (e.g., 'immediate legal action,' 'account blocked/compromised,' 'outstanding warrant,' 'fine must be paid now,' 'digital arrest,' 'your Aadhaar/PAN linked to illegal activity'). Uses fear-mongering.\n"
    "    *   **Information/Money Demand:** Uses the impersonation and urgency to demand sensitive data (Aadhaar, PAN, OTP, full bank details, passwords) OR demands payment through unusual/specific methods (gift cards, specific apps, wire transfer, cryptocurrency), especially for unexpected fees or taxes.\n"
    "    *   **Secrecy/Isolation:** Instructs the listener not to tell anyone or disconnect the call.\n"
    "    *   **Suspicious OTP Requests:** Treat requests for OTPs, verification codes, or passwords with EXTREME CAUTION. If unsolicited, pressured, or for accessing accounts/money, classify as 'Fraud'.\n"
    "    *   **Examples:** 'Officer Sharma from Cyber Crime...verify Aadhaar or face arrest.' / 'Your bank account is compromised, give OTP.' / 'Pay unpaid tax via gift card.'\n"

    "2.  **Spam:** Classify as 'Spam' for unsolicited calls primarily focused on:\n"
    "    *   **Initiating NEW Sales/Offers:** Cold calls trying to sell products/services (loans, insurance, property, subscriptions) that the listener did not request or inquire about.\n"
    "    *   **Unrelated Info Gathering:** Surveys asking for opinions or basic info *not tied* to a specific recent transaction or service the listener uses. Prize notifications asking for contact details to send winnings (becomes Fraud if they later ask for fees/bank details).\n"
    "    *   **Note:** This category is for calls trying to *start* a new commercial interaction or gather general info, not for calls discussing an existing order or service issue (even if unsolicited).\n"

    "3.  **Normal:** Classify as 'Normal' for calls that are generally expected, legitimate, or relate to an existing relationship/transaction, even if slightly unusual, provided they lack fraud/spam indicators:\n"
    "    *   **Personal Calls:** Conversations between known contacts without suspicious requests.\n"
    "    *   **Expected Customer Service/Follow-ups:** Calls you were expecting, appointment reminders, etc.\n"
    "    *   **Delivery Calls:** Standard delivery coordination.\n"
    "    *   **Proactive Notifications on EXISTING Orders/Services:** **This includes unsolicited calls from known companies (e.g., Flipkart, Amazon, your bank) regarding a specific existing order, delivery, account status, or recent transaction.** The reason given might be slightly vague ('technical issue with billing', 'delivery delay'). **Classify as 'Normal' IF AND ONLY IF:**\n"
    "        *   The call clearly refers to a plausible existing order/service.\n"
    "        *   There is **NO immediate demand** for unexpected payment.\n"
    "        *   There is **NO demand** for sensitive information (OTP, password, full Aadhaar/PAN, full bank details).\n"
    "        *   There are **NO threats** or high-pressure tactics.\n"
    "        *   The caller identifies themselves plausibly (e.g., 'Flipkart delivery team', 'Area Manager for Flipkart regarding order X').\n"
    "        *   **If the call *starts* like this but then *pivots* to asking for OTP/payment/sensitive info, it immediately becomes 'Fraud'.**\n"
    "    *   **Legitimate Verification (Low Risk):** Bank calling to verify a recent specific transaction (e.g., 'Did you just buy X?'), *without* asking for OTP/full details.\n"

    "4.  **Unclear/Empty:** Use this classification ONLY if:\n"
    "    *   Audio is silent, pure noise, or completely unintelligible.\n\n"

    "**Output Format (Strictly Follow):**\n"
    "Line 1: The single-word classification: Fraud, Spam, Normal, or Unclear/Empty.\n"
    "Line 2 onwards: A concise (1-3 sentences) justification explaining the key reasons, **written in English**. **For 'Normal' calls that were unsolicited or slightly vague (like the proactive notification type), explicitly state in English *why* it wasn't classified as Spam or Fraud (e.g., 'Caller identified as Flipkart regarding an order, no sensitive info/payment demanded, classifying as Normal despite vagueness.')**"
)

# --- TRANSCRIPTION PROMPT REMAINS ENGLISH ---
TRANSCRIPTION_PROMPT = (
    "Accurately transcribe the speech from the provided audio recording (maximum 60 seconds)."
    "You are an expert multilingual transcription machine, you can take inputs in any indian language(like Hindi, Bengali,Kannada, Tamil, Telugu, Marathi, etc.) including english"
    "Follow this format precisely:\n"
    "1.  On the first line, provide the full transcription in English.\n"
    "2.  On a new line, write 'Original Language Transcription:'.\n"
    "3.  On the next line, provide the transcription in the primary language detected in the audio (this might be the same as the English transcription if English was the primary language).\n\n"
    "If the audio is silent, contains no discernible speech, or is too unclear to transcribe, output only the single line: 'Audio is silent or contains no clear speech'."
)


# --- GEMINI API CALL FUNCTION ---
# (Keep get_gemini_response function as it was - English UI errors)
def get_gemini_response(prompt, audio_bytes, mime_type):
    if not gemini_model: return "Error: Gemini model not configured."
    if not audio_bytes: return "Error: No audio data provided."
    print(f"Uploading audio ({mime_type}, {len(audio_bytes)} bytes) to Gemini...")
    uploaded_file = None
    try:
        audio_file_object = io.BytesIO(audio_bytes)
        # Using path= parameter which expects a file-like object or path string
        uploaded_file = genai.upload_file(path=audio_file_object, mime_type=mime_type)
        print(f"Audio uploaded: {uploaded_file.name}. Waiting for processing...")
        # Wait for the file to be active
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2) # Wait 2 seconds
            uploaded_file = genai.get_file(uploaded_file.name) # Check status again
        # Check if processing failed or file is not active
        if uploaded_file.state.name == "FAILED":
            raise ValueError(f"Gemini file processing failed: {uploaded_file.name}")
        if uploaded_file.state.name != "ACTIVE":
             raise ValueError(f"Uploaded file state is not ACTIVE: {uploaded_file.state.name}")

        print("File is ACTIVE. Generating content...")
        # Pass the file object directly to generate_content
        response = gemini_model.generate_content([prompt, uploaded_file]) # Pass the file object
        result_text = response.text.strip()
        print(f"Gemini raw response captured.")

        # Clean up the uploaded file
        try:
            print(f"Deleting Gemini file: {uploaded_file.name}")
            genai.delete_file(uploaded_file.name)
            print(f"Deleted.")
        except Exception as del_e:
            print(f"Warning: Could not delete Gemini file {uploaded_file.name}: {del_e}") # Log deletion error but continue

        return result_text

    except Exception as e:
        error_msg = f"Gemini API Error: {e}"
        print(error_msg)
        # Attempt to delete the file if it was created before the error occurred
        if uploaded_file and hasattr(uploaded_file, 'name'):
            try:
                print(f"Attempting to delete Gemini file after error: {uploaded_file.name}")
                genai.delete_file(uploaded_file.name)
                print(f"Deleted file after error.")
            except Exception as del_e:
                print(f"Could not delete Gemini file {uploaded_file.name} after error: {del_e}") # Log deletion error but continue
        return f"Error: {error_msg}" # Return the error message

# --- RESPONSE PARSING ---
# (Keep parse_fraud_analysis_response function as it was - expects English keywords)
def parse_fraud_analysis_response(response_text):
    if response_text.startswith("Error:"): return "Error", response_text
    lines = response_text.strip().split('\n', 1)
    classification = lines[0].strip().capitalize()
    reason = lines[1].strip() if len(lines) > 1 else "No detailed reason provided."
    valid_classifications = ["Fraud", "Spam", "Normal", "Unclear/Empty"] # Keep these English
    if classification not in valid_classifications:
        print(f"Warning: Unexpected classification '{classification}'. Falling back.")
        # Fallback based on keywords (English)
        if "fraud" in response_text.lower() or "digital arrest" in response_text.lower(): classification = "Fraud"
        elif "spam" in response_text.lower(): classification = "Spam"
        elif "unclear" in response_text.lower() or "silent" in response_text.lower(): classification = "Unclear/Empty"
        else: classification = "Normal"
        reason = response_text # Use full text if parsing failed
    return classification, reason

# ------------------- STREAMLIT UI PAGE FUNCTIONS -------------------
# (Keep page functions - use English strings directly)
def show_welcome_page():
    st.title(f"👋 Welcome, {st.session_state.user_email}!")
    st.markdown("---"); st.header("Audio Analysis Portal")
    st.write("Use the options in the sidebar to:"); st.markdown(""" *   **Analyze Calls:** Upload audio (first 60s processed) to detect Fraud/Spam.\n *   **Transcribe Audio:** Get transcription (first 60s processed).\n *   **Feedback:** Send comments or report issues. """)
    st.info("Select an option from the sidebar to begin.")

def fraud_analysis_page():
    st.header("🚨 Fraud Call Analysis"); st.write(f"Upload audio. First {MAX_AUDIO_DURATION_MS/1000} seconds processed.")
    uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a", "ogg", "flac"], key="analysis_uploader")
    if uploaded_file:
        original_audio_bytes = uploaded_file.getvalue(); file_name = uploaded_file.name
        result_key = f'analysis_result_{file_name}'; analyze_button_key = f"analyze_btn_{file_name}"
        if st.button("Analyze Call", key=analyze_button_key):
            if gemini_model is None: st.error("Gemini model unavailable."); return
            with st.spinner("Processing audio..."): processed_audio_bytes, processed_mime_type, _ = process_audio(original_audio_bytes, file_name)
            if processed_audio_bytes:
                st.audio(processed_audio_bytes, format=processed_mime_type) # Play processed
                with st.spinner("Analyzing with AI..."):
                    # Use the updated prompt
                    analysis_response = get_gemini_response(FRAUD_ANALYSIS_PROMPT, processed_audio_bytes, processed_mime_type)
                    classification, reason = parse_fraud_analysis_response(analysis_response)
                    st.session_state[result_key] = {"classification": classification, "reason": reason}
                    if classification != "Error": save_audio_data(st.session_state.user_email, file_name, processed_audio_bytes, classification, reason)
                    else: st.error(f"Analysis Failed: {reason}") # Show English error
                    st.rerun()
        if result_key in st.session_state:
            result = st.session_state[result_key]; classification = result["classification"]; reason = result["reason"]
            st.subheader("Analysis Result:") # English label
            if classification == "Fraud": st.error(f"**Classification:** {classification}")
            elif classification == "Spam": st.warning(f"**Classification:** {classification}")
            elif classification == "Normal": st.success(f"**Classification:** {classification}")
            else: st.info(f"**Classification/Status:** {classification}") # English label
            st.write("**AI Justification:**"); st.write(reason) # English label
            if classification in ["Spam", "Fraud"]:
                 report_button_key = f"report_btn_{file_name}_{classification}"
                 if st.button(f"🚨 Send {classification} Alert", key=report_button_key): # English button
                     with st.spinner("Sending report..."): send_fraud_report(st.session_state.user_email, classification, reason, file_name) # Handles success msg

def transcribe_page():
    st.header("🎧 Audio Transcription"); st.write(f"Upload audio. First {MAX_AUDIO_DURATION_MS/1000} seconds processed.")
    uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a", "ogg", "flac"], key="transcribe_uploader")
    if uploaded_file:
        original_audio_bytes = uploaded_file.getvalue(); file_name = uploaded_file.name
        result_key = f'transcription_result_{file_name}'; transcribe_button_key = f"transcribe_btn_{file_name}"
        if st.button("Transcribe Audio", key=transcribe_button_key): # English button
            if gemini_model is None: st.error("Gemini model unavailable."); return
            with st.spinner("Processing audio..."): processed_audio_bytes, processed_mime_type, _ = process_audio(original_audio_bytes, file_name)
            if processed_audio_bytes:
                st.audio(processed_audio_bytes, format=processed_mime_type) # Play processed
                with st.spinner("Transcribing with AI..."):
                    transcription_response = get_gemini_response(TRANSCRIPTION_PROMPT, processed_audio_bytes, processed_mime_type)
                    # Handle specific "no speech" case from Gemini
                    if transcription_response.strip() == "Audio is silent or contains no clear speech":
                         st.session_state[result_key] = "Audio is silent or contains no clear speech" # Store English message
                    # Handle API errors returned by get_gemini_response
                    elif transcription_response.startswith("Error:"):
                         st.session_state[result_key] = transcription_response # Keep error as is
                    else:
                         st.session_state[result_key] = transcription_response # Store raw transcription
                    st.rerun()
        if result_key in st.session_state:
            transcription = st.session_state[result_key]
            st.subheader("Transcription Result:") # English label
            if transcription.startswith("Error:"): st.error(transcription) # Show English error
            elif transcription == "Audio is silent or contains no clear speech": st.info(transcription) # Show info
            else: st.text_area("Transcription:", transcription, height=300, disabled=False) # English label

def feedback_page():
    st.header("📝 Give Feedback"); st.write("We appreciate your feedback!") # English text
    feedback_key = "feedback_text_area_content"
    feedback_text = st.text_area("Enter feedback:", value=st.session_state.get(feedback_key, ""), height=200, key=feedback_key+"_widget") # English label
    if st.button("Submit Feedback", key="submit_feedback_btn"): # English button
        current_feedback = st.session_state[feedback_key+"_widget"]
        if current_feedback and current_feedback.strip():
            with st.spinner("Submitting..."):
                if send_feedback_email(st.session_state.user_email, current_feedback.strip()): # Handles success msg
                   st.session_state[feedback_key] = ""; st.rerun()
        else: st.warning("Please enter feedback before submitting.") # English warning

# ------------------- MAIN APPLICATION LOGIC -------------------
# (Keep main function logic - uses English strings directly now)
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "user_email" not in st.session_state: st.session_state.user_email = None
    if "current_page" not in st.session_state: st.session_state.current_page = "welcome"

    if st.session_state.logged_in:
        with st.sidebar:
            st.title("Navigation"); st.markdown("---") # English title
            st.write(f"Logged in as:\n**{st.session_state.user_email}**"); st.markdown("---") # English text
            # English button labels
            if st.button("🏠 Home", key="nav_welcome"): st.session_state.current_page = "welcome"; st.rerun()
            if st.button("🚨 Analyze Calls", key="nav_analyze"): st.session_state.current_page = "analyze"; st.rerun()
            if st.button("🎧 Transcribe Audio", key="nav_transcribe"): st.session_state.current_page = "transcribe"; st.rerun()
            if st.button("📝 Give Feedback", key="nav_feedback"): st.session_state.current_page = "feedback"; st.rerun()
            st.markdown("---")
            if st.button("Logout", key="logout_sidebar"): # English button
                keys_to_clear = ["logged_in", "user_email", "current_page"]
                for key in list(st.session_state.keys()):
                    if key.startswith(('analysis_result_', 'transcription_result_', 'feedback_text')): keys_to_clear.append(key)
                for key in keys_to_clear:
                    if key in st.session_state: del st.session_state[key]
                st.success("Logged out."); time.sleep(1); st.rerun() # English message

        page = st.session_state.current_page
        if page == "analyze": fraud_analysis_page()
        elif page == "transcribe": transcribe_page()
        elif page == "feedback": feedback_page()
        else: show_welcome_page() # Default to welcome page

    else: # Not logged in
        st.title("🔐 Fraudshield AI"); st.write("Please log in or register."); st.markdown("---") # English text
        tab1, tab2 = st.tabs(["Login", "Register"]) # English tabs
        with tab1:
            st.subheader("Login") # English subheader
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email") # English label
                password = st.text_input("Password", type="password", key="login_password") # English label
                login_submitted = st.form_submit_button("Login") # English button
                if login_submitted:
                    if authenticate(email, password): # Handles its own UI messages
                        st.session_state.logged_in = True; st.session_state.user_email = email
                        st.session_state.current_page = "welcome" # Go to welcome page
                        st.success("Login Successful!"); time.sleep(1); st.rerun() # English message
        with tab2:
            st.subheader("Register") # English subheader
            with st.form("register_form"):
                name = st.text_input("Name", key="register_name") # English label
                reg_email = st.text_input("Email", key="register_email") # English label
                reg_password = st.text_input("Create Password", type="password", key="register_password") # English label
                register_submitted = st.form_submit_button("Sign Up") # English button
                if register_submitted:
                    if save_user(name, reg_email, reg_password): # Handles its own UI messages
                        st.info("Registration complete. Please Login.") # English message

# --- Run the main function ---
if __name__ == "__main__":
    main()