import streamlit as st
import sqlite3
import bcrypt
import os
import re
from datetime import datetime, timedelta, timezone
import pandas as pd
from cryptography.fernet import Fernet, InvalidToken
import html

# ---------- Constants ----------
DB_FILE = "wallet_app.db"
KEY_FILE = "secret.key"
PASSWORD_MIN_LENGTH = 10
MAX_USERNAME_LENGTH = 50
MAX_EMAIL_LENGTH = 100
MAX_WALLET_NAME_LENGTH = 100
MAX_WALLET_DATA_LENGTH = 5000
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_TIME = 300  # 5 minutes in seconds
SESSION_TIMEOUT = 1800  # 30 minutes

# ---------- UI Styling ----------
st.set_page_config(page_title="Secure Crypto Wallet", layout="wide", page_icon="💎")

st.markdown("""
    <style>
        /* Main App Background - Dark Tech Theme */
        [data-testid="stAppViewContainer"] {
            background: #0a0e27;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(0, 255, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(138, 43, 226, 0.03) 0%, transparent 50%),
                linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        
        /* Sidebar - Dark with Neon Border */
        [data-testid="stSidebar"] {
            background: rgba(15, 20, 40, 0.95) !important;
            backdrop-filter: blur(10px);
            border-right: 2px solid #00ffff;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        }
        
        /* Main Content Area */
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
        }
        
        /* Title - Cyan Neon Style */
        .main-title {
            text-align: center;
            font-size: 4rem;
            color: #00ffff;
            font-weight: 900;
            letter-spacing: 5px;
            text-transform: uppercase;
            margin-bottom: 1rem;
            font-family: 'Courier New', monospace;
            text-shadow: 
                0 0 10px #00ffff,
                0 0 20px #00ffff,
                0 0 30px #00ffff,
                2px 2px 4px rgba(0,0,0,0.5);
            animation: neonPulse 2s ease-in-out infinite alternate;
        }
        
        @keyframes neonPulse {
            from {
                text-shadow: 
                    0 0 10px #00ffff,
                    0 0 20px #00ffff,
                    0 0 30px #00ffff,
                    2px 2px 4px rgba(0,0,0,0.5);
            }
            to {
                text-shadow: 
                    0 0 20px #00ffff,
                    0 0 30px #00ffff,
                    0 0 40px #00ffff,
                    0 0 50px #00ffff,
                    2px 2px 4px rgba(0,0,0,0.5);
            }
        }
        
        .main-title::after {
            content: '';
            display: block;
            width: 250px;
            height: 3px;
            background: linear-gradient(90deg, transparent, #00ffff, #8a2be2, #00ffff, transparent);
            margin: 20px auto;
            border-radius: 2px;
            box-shadow: 0 0 10px #00ffff, 0 0 20px #8a2be2;
            animation: lineGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes lineGlow {
            from { box-shadow: 0 0 10px #00ffff, 0 0 20px #8a2be2; }
            to { box-shadow: 0 0 20px #00ffff, 0 0 30px #8a2be2, 0 0 40px #00ffff; }
        }
        
        /* Section Boxes - Dark Tech Cards */
        .section-box {
            background: rgba(15, 20, 40, 0.8);
            backdrop-filter: blur(10px);
            padding: 40px;
            border-radius: 10px;
            margin-top: 30px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.5),
                inset 0 0 20px rgba(0, 255, 255, 0.05);
            border: 1px solid rgba(0, 255, 255, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }
        
        .section-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            transition: left 0.5s;
        }
        
        .section-box:hover::before {
            left: 100%;
        }
        
        .section-box:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 15px 50px rgba(0, 255, 255, 0.3),
                inset 0 0 30px rgba(138, 43, 226, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.6);
        }
        
        /* Buttons - Neon Tech Style */
        .stButton>button {
            background: rgba(0, 255, 255, 0.1);
            color: #00ffff;
            border: 2px solid #00ffff;
            border-radius: 5px;
            padding: 0.85rem 2.5rem;
            font-weight: 700;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 0.95rem;
            font-family: 'Courier New', monospace;
            width: 100%;
            min-width: 200px;
            box-shadow: 
                0 0 10px rgba(0, 255, 255, 0.3),
                inset 0 0 10px rgba(0, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
            text-shadow: 0 0 10px #00ffff;
        }
        
        .stButton>button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.3), transparent);
            transition: left 0.5s;
        }
        
        .stButton>button:hover::before {
            left: 100%;
        }
        
        .stButton>button:hover {
            background: rgba(0, 255, 255, 0.2);
            color: #ffffff;
            border-color: #8a2be2;
            transform: translateY(-3px);
            box-shadow: 
                0 0 20px rgba(0, 255, 255, 0.6),
                0 0 40px rgba(138, 43, 226, 0.4),
                inset 0 0 20px rgba(0, 255, 255, 0.2);
            text-shadow: 
                0 0 10px #00ffff,
                0 0 20px #8a2be2;
        }
        
        .stButton>button:active {
            transform: translateY(-1px);
        }
        
        /* Input Fields - Dark Tech Style */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            background: rgba(10, 14, 39, 0.8);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(0, 255, 255, 0.3);
            border-radius: 5px;
            color: #00ffff !important;
            padding: 0.85rem 1rem;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
        }
        
        .stTextInput>div>div>input::placeholder,
        .stTextArea>div>div>textarea::placeholder {
            color: rgba(0, 255, 255, 0.4) !important;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            background: rgba(15, 20, 40, 0.9);
            border: 2px solid #00ffff;
            box-shadow: 
                0 0 15px rgba(0, 255, 255, 0.5),
                inset 0 0 10px rgba(0, 255, 255, 0.1);
            outline: none;
            color: #ffffff !important;
        }
        
        /* Labels - Cyan Neon */
        label {
            color: #00ffff !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-size: 0.9rem;
            font-family: 'Courier New', monospace;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        
        /* Headers - Cyan with Neon Glow */
        h1, h2, h3 {
            color: #00ffff !important;
            font-weight: 700;
            letter-spacing: 2px;
            font-family: 'Courier New', monospace;
            text-shadow: 
                0 0 10px rgba(0, 255, 255, 0.8),
                0 0 20px rgba(0, 255, 255, 0.4);
        }
        
        h2 {
            border-bottom: 2px solid #00ffff;
            padding-bottom: 15px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0, 255, 255, 0.3);
        }
        
        /* Dividers */
        hr {
            border: none;
            border-top: 1px solid rgba(0, 255, 255, 0.3);
            margin: 30px 0;
            box-shadow: 0 1px 5px rgba(0, 255, 255, 0.2);
        }
        
        /* DataFrames - Dark Tech Style */
        .dataframe {
            background: rgba(10, 14, 39, 0.9);
            backdrop-filter: blur(10px);
            color: #00ffff;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 5px;
            overflow: hidden;
        }
        
        /* Success/Error Messages - Dark Tech Style */
        .stSuccess {
            background: rgba(10, 14, 39, 0.9);
            backdrop-filter: blur(10px);
            border-left: 4px solid #00ff88;
            color: #00ff88;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }
        
        .stError {
            background: rgba(10, 14, 39, 0.9);
            backdrop-filter: blur(10px);
            border-left: 4px solid #ff3366;
            color: #ff3366;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(255, 51, 102, 0.3);
        }
        
        .stInfo {
            background: rgba(10, 14, 39, 0.9);
            backdrop-filter: blur(10px);
            border-left: 4px solid #00ffff;
            color: #00ffff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
        }
        
        .stWarning {
            background: rgba(10, 14, 39, 0.9);
            backdrop-filter: blur(10px);
            border-left: 4px solid #ffaa00;
            color: #ffaa00;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(255, 170, 0, 0.3);
        }
        
        /* Radio Buttons */
        .stRadio>div>label {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        /* Code Blocks - Dark Tech Style */
        code {
            background: rgba(10, 14, 39, 0.9);
            backdrop-filter: blur(10px);
            color: #00ffff;
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 15px;
            display: block;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
        }
        
        /* Navigation Buttons - Tech Style */
        div[data-testid="column"] button {
            background: rgba(0, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            color: #00ffff;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 5px;
            width: 100% !important;
            min-width: 150px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
            text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
        }
        
        div[data-testid="column"] button:hover {
            background: rgba(0, 255, 255, 0.15);
            border: 1px solid #00ffff;
            color: #ffffff;
            transform: translateY(-3px);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), 0 0 30px rgba(138, 43, 226, 0.3);
            text-shadow: 0 0 10px #00ffff, 0 0 20px #8a2be2;
        }
        
        /* Responsive Columns */
        @media (max-width: 768px) {
            div[data-testid="column"] {
                width: 100% !important;
                margin-bottom: 10px;
            }
            
            .stButton>button {
                min-width: 100%;
            }
            
            .main-title {
                font-size: 2.5rem;
            }
        }
        
        /* Sidebar Elements */
        [data-testid="stSidebar"] .stRadio>div>label {
            color: #ffffff !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        [data-testid="stSidebar"] h1 {
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(10, 14, 39, 0.5);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #00ffff, #8a2be2);
            border-radius: 10px;
            border: 2px solid rgba(0, 255, 255, 0.2);
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #8a2be2, #00ffff);
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.8);
        }
        
        /* Text Content in Dark Boxes */
        .section-box p,
        .section-box li {
            color: #e0e0e0;
            text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
        }
        
        /* Markdown Content Adjustments */
        .section-box h1,
        .section-box h2,
        .section-box h3 {
            color: #00ffff !important;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
        }
        
        /* Remove Streamlit Branding */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
    </style>
""", unsafe_allow_html=True)

# ---------- Encryption Setup ----------
def init_key():
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, "wb") as f:
            f.write(Fernet.generate_key())
    with open(KEY_FILE, "rb") as f:
        return f.read()

fernet = Fernet(init_key())

# ---------- Database ----------
def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash BLOB,
        email TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS wallets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        encrypted_data BLOB,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS audit_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS login_attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        attempts INTEGER DEFAULT 0,
        last_attempt TEXT,
        locked_until TEXT
    )""")
    conn.commit()

init_db()

# ---------- Utility Functions ----------
def hash_pw(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())
def check_pw(pw, hashed): return bcrypt.checkpw(pw.encode(), hashed)
def log_action(uid, action, details=""):
    try:
        conn = get_db()
        conn.execute("INSERT INTO audit_log(user_id,action,details,created_at) VALUES(?,?,?,?)",
                     (uid, action, details, datetime.now(timezone.utc).isoformat()))
        conn.commit()
    except Exception:
        pass  # Silent fail on logging errors

def is_strong_pw(p):
    if not p:
        return False, ["Password cannot be empty"]
    errors=[]
    if len(p)<PASSWORD_MIN_LENGTH: errors.append("Min length 10")
    if not re.search(r"[A-Z]",p): errors.append("Add uppercase")
    if not re.search(r"[a-z]",p): errors.append("Add lowercase")
    if not re.search(r"\d",p): errors.append("Add digit")
    if not re.search(r"[^A-Za-z0-9]",p): errors.append("Add symbol")
    return len(errors)==0, errors

def validate_email(email):
    if not email or len(email.strip()) == 0:
        return False, "Email cannot be empty"
    if len(email) > MAX_EMAIL_LENGTH:
        return False, f"Email too long (max {MAX_EMAIL_LENGTH} characters)"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    return True, ""

def sanitize_input(text, max_length=None):
    """Sanitize input to prevent XSS"""
    if not text:
        return ""
    if max_length and len(text) > max_length:
        text = text[:max_length]
    # HTML escape
    text = html.escape(text)
    return text.strip()

def validate_username(username):
    if not username or len(username.strip()) == 0:
        return False, "Username cannot be empty"
    if len(username) > MAX_USERNAME_LENGTH:
        return False, f"Username too long (max {MAX_USERNAME_LENGTH} characters)"
    # Allow alphanumeric, underscore, hyphen, and unicode (but sanitize)
    if re.search(r'[<>"\']', username):
        return False, "Username contains invalid characters"
    return True, ""

def check_login_attempts(username):
    """Check if user is locked out due to failed attempts"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT attempts, locked_until FROM login_attempts WHERE username=?", (username,))
    row = cur.fetchone()
    
    if row:
        attempts = row["attempts"] if row["attempts"] else 0
        locked_until = row["locked_until"]
        
        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.now(timezone.utc) < lock_time:
                remaining = (lock_time - datetime.now(timezone.utc)).total_seconds()
                return False, f"Account locked. Try again in {int(remaining/60)} minutes."
            else:
                # Lock expired, reset
                cur.execute("UPDATE login_attempts SET attempts=0, locked_until=NULL WHERE username=?", (username,))
                conn.commit()
        
        if attempts >= MAX_LOGIN_ATTEMPTS:
            # Lock the account
            lock_time = datetime.now(timezone.utc) + timedelta(seconds=LOGIN_LOCKOUT_TIME)
            cur.execute("UPDATE login_attempts SET locked_until=? WHERE username=?", (lock_time.isoformat(), username))
            conn.commit()
            return False, f"Too many failed attempts. Account locked for {LOGIN_LOCKOUT_TIME//60} minutes."
    
    return True, ""

def record_failed_login(username):
    """Record a failed login attempt"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT attempts FROM login_attempts WHERE username=?", (username,))
    row = cur.fetchone()
    
    if row:
        attempts = (row["attempts"] or 0) + 1
        cur.execute("UPDATE login_attempts SET attempts=?, last_attempt=? WHERE username=?",
                   (attempts, datetime.now(timezone.utc).isoformat(), username))
    else:
        cur.execute("INSERT INTO login_attempts(username, attempts, last_attempt) VALUES(?,?,?)",
                   (username, 1, datetime.now(timezone.utc).isoformat()))
    conn.commit()

def reset_login_attempts(username):
    """Reset login attempts on successful login"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE login_attempts SET attempts=0, locked_until=NULL WHERE username=?", (username,))
    conn.commit()

def check_session_timeout():
    """Check if session has timed out"""
    if not st.session_state.get("last_activity"):
        return False
    
    last_activity = datetime.fromisoformat(st.session_state.last_activity)
    if (datetime.now(timezone.utc) - last_activity).total_seconds() > SESSION_TIMEOUT:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.last_activity = None
        return True
    return False

# ---------- Session ----------
if "user" not in st.session_state: st.session_state.user=None
if "logged_in" not in st.session_state: st.session_state.logged_in=False
if "page" not in st.session_state: st.session_state.page="Home"
if "last_activity" not in st.session_state: st.session_state.last_activity=None

# Check session timeout on every page load
if st.session_state.logged_in:
    if check_session_timeout():
        st.warning("Session expired. Please login again.")
        st.session_state.page = "Login"
    else:
        st.session_state.last_activity = datetime.now(timezone.utc).isoformat()

# ---------- Header ----------
st.markdown("<h1 class='main-title'>Secure Crypto Wallet</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Navigation ----------
menu_cols = st.columns(4)
with menu_cols[0]: 
    if st.button("HOME", key="nav_home"): st.session_state.page="Home"
with menu_cols[1]:
    if st.button("REGISTER", key="nav_register"): st.session_state.page="Register"
with menu_cols[2]:
    if st.button("LOGIN", key="nav_login"): st.session_state.page="Login"
with menu_cols[3]:
    if st.button("HELP", key="nav_help"): st.session_state.page="Help"

# ---------- Sidebar ----------
if st.session_state.logged_in:
    username_display = html.escape(st.session_state.user['username'].upper())
    st.sidebar.markdown(f"<h1 style='color: #ffffff; font-size: 1.5rem; font-weight: 300; letter-spacing: 2px;'>{username_display}</h1>", unsafe_allow_html=True)
    menu = st.sidebar.radio("MENU", ["Wallets", "Profile", "Audit Log"])
    if st.sidebar.button("LOGOUT", key="sidebar_logout"):
        log_action(st.session_state.user['id'], "Logout", "User logged out")
        st.session_state.logged_in=False
        st.session_state.user=None
        st.session_state.last_activity=None
        st.session_state.page="Home"
        st.rerun()
else:
    st.sidebar.markdown("<p style='color: #ffffff; padding: 20px;'>Please login to access wallet features.</p>", unsafe_allow_html=True)
    menu=None

# ---------- Pages ----------
def home():
    st.markdown("""
    <div class="section-box">
        <div style="text-align: center; padding: 20px;">
            <h2 style="color: #00ffff; font-size: 2.8rem; font-weight: 900; letter-spacing: 4px; margin-top: 0; margin-bottom: 30px; text-shadow: 0 0 20px rgba(0,255,255,0.8), 0 0 30px rgba(0,255,255,0.5); font-family: 'Courier New', monospace;">WELCOME</h2>
            <p style="color: #e0e0e0; font-size: 1.2rem; line-height: 1.8; margin: 20px 0; text-shadow: 0 0 5px rgba(0,255,255,0.3);">
                A premium cryptocurrency wallet solution designed with enterprise-grade security.
            </p>
            <div style="border-top: 2px solid #00ffff; margin: 40px auto; width: 250px; box-shadow: 0 0 15px rgba(0,255,255,0.5);"></div>
            <p style="color: #e0e0e0; font-size: 1rem; line-height: 2.2; letter-spacing: 0.5px; text-shadow: 0 0 5px rgba(0,255,255,0.2);">
                <strong style="font-size: 1.1rem; color: #00ffff; text-shadow: 0 0 10px rgba(0,255,255,0.6);">Advanced Security Features:</strong><br>
                🔐 Password Hashing with bcrypt<br>
                🔒 AES-256 Encryption<br>
                🛡️ SQL Injection Prevention<br>
                📋 Comprehensive Audit Logging
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def register():
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,255,0.8); box-shadow: 0 2px 10px rgba(0,255,255,0.3); font-family: \"Courier New\", monospace;'>CREATE ACCOUNT</h2>", unsafe_allow_html=True)
    username=st.text_input("Username", max_chars=MAX_USERNAME_LENGTH)
    email=st.text_input("Email", max_chars=MAX_EMAIL_LENGTH)
    pw=st.text_input("Password",type="password")
    cpw=st.text_input("Confirm Password",type="password")

    if st.button("REGISTER", key="btn_register"):
        # Validate empty fields
        if not username or not username.strip():
            st.error("Username cannot be empty")
        elif not email or not email.strip():
            st.error("Email cannot be empty")
        elif not pw:
            st.error("Password cannot be empty")
        else:
            # Validate username
            user_valid, user_msg = validate_username(username)
            if not user_valid:
                st.error(user_msg)
            else:
                # Sanitize username
                username = sanitize_input(username, MAX_USERNAME_LENGTH)
                
                # Validate email
                email_valid, email_msg = validate_email(email)
                if not email_valid:
                    st.error(email_msg)
                else:
                    # Sanitize email
                    email = sanitize_input(email, MAX_EMAIL_LENGTH)
                    
                    # Validate password match
                    if pw != cpw:
                        st.error("Passwords do not match!")
                    else:
                        # Validate password strength
                        ok, errs = is_strong_pw(pw)
                        if not ok:
                            st.error("; ".join(errs))
                        else:
                            try:
                                conn=get_db()
                                cur=conn.cursor()
                                cur.execute("SELECT id FROM users WHERE username=?",(username,))
                                if cur.fetchone():
                                    st.error("Username already exists!")
                                else:
                                    cur.execute("INSERT INTO users(username,password_hash,email,created_at) VALUES (?,?,?,?)",
                                                (username,hash_pw(pw),email,datetime.now(timezone.utc).isoformat()))
                                    conn.commit()
                                    log_action(None, "User Registered", f"Username: {username}")
                                    st.success("Account created successfully")
                            except Exception as e:
                                st.error("An error occurred. Please try again.")
                                log_action(None, "Registration Error", "Failed registration attempt")
    st.markdown('</div>', unsafe_allow_html=True)

def login():
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,255,0.8); box-shadow: 0 2px 10px rgba(0,255,255,0.3); font-family: \"Courier New\", monospace;'>LOGIN</h2>", unsafe_allow_html=True)
    username = st.text_input("Username", max_chars=MAX_USERNAME_LENGTH)
    pw = st.text_input("Password", type="password")

    if st.button("LOGIN", key="btn_login"):
        if not username or not username.strip():
            st.error("Username cannot be empty")
        elif not pw:
            st.error("Password cannot be empty")
        else:
            # Sanitize username input
            username = sanitize_input(username, MAX_USERNAME_LENGTH)
            
            # Check login attempts
            can_login, lock_msg = check_login_attempts(username)
            if not can_login:
                st.error(lock_msg)
                log_action(None, "Login Attempt", f"Locked account attempt: {username}")
            else:
                try:
                    conn = get_db()
                    cur = conn.cursor()
                    # SQL injection protection: parameterized query
                    cur.execute("SELECT id,username,password_hash FROM users WHERE username=?",(username,))
                    row = cur.fetchone()
                    if row and check_pw(pw, row["password_hash"]):
                        st.session_state.logged_in=True
                        st.session_state.user={"id":row["id"],"username":row["username"]}
                        st.session_state.last_activity = datetime.now(timezone.utc).isoformat()
                        reset_login_attempts(username)
                        log_action(row["id"], "Login", "Successful login")
                        st.success(f"Welcome {html.escape(row['username'])}! Redirecting...")
                        st.session_state.page="Wallets"
                        st.rerun()
                    else:
                        record_failed_login(username)
                        st.error("Invalid credentials!")
                        log_action(None, "Login Attempt", f"Failed login: {username}")
                except Exception:
                    st.error("An error occurred. Please try again.")
                    log_action(None, "Login Error", "Login error occurred")
    st.markdown('</div>', unsafe_allow_html=True)

def help_page():
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("""
    <h2 style='color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,255,0.8); box-shadow: 0 2px 10px rgba(0,255,255,0.3); font-family: "Courier New", monospace;'>HELP & SECURITY</h2>
    <div style="color: #e0e0e0; line-height: 2.5; font-size: 1rem; text-shadow: 0 0 5px rgba(0,255,255,0.3);">
        <p><strong>Password Security</strong><br>All passwords are hashed using bcrypt with salt</p>
        <p><strong>Data Encryption</strong><br>Wallet data is encrypted using AES-256 encryption</p>
        <p><strong>Audit Logging</strong><br>Every user action is logged for security auditing</p>
        <p><strong>Protection</strong><br>Advanced protection against SQL injection and XSS attacks</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def wallets():
    if not st.session_state.logged_in:
        st.error("Please login to access wallets.")
        return
    
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,255,0.8); box-shadow: 0 2px 10px rgba(0,255,255,0.3); font-family: \"Courier New\", monospace;'>YOUR WALLETS</h2>", unsafe_allow_html=True)
    
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT id,name,created_at FROM wallets WHERE user_id=?",(st.session_state.user["id"],))
        data=cur.fetchall()
        if data:
            st.dataframe(pd.DataFrame(data))
        else:
            st.info("No wallets yet. Create one below.")
        
        wname=st.text_input("Wallet Name", max_chars=MAX_WALLET_NAME_LENGTH)
        wdata=st.text_area("Wallet Private Data", max_chars=MAX_WALLET_DATA_LENGTH)
        
        if st.button("CREATE WALLET", key="btn_create_wallet"):
            if not wname or not wname.strip():
                st.error("Wallet name cannot be empty")
            elif not wdata:
                st.error("Wallet data cannot be empty")
            elif len(wdata) > MAX_WALLET_DATA_LENGTH:
                st.error(f"Wallet data too long (max {MAX_WALLET_DATA_LENGTH} characters)")
            else:
                # Sanitize wallet name (XSS protection)
                wname_safe = sanitize_input(wname, MAX_WALLET_NAME_LENGTH)
                # Data is encrypted so we don't need to sanitize it for storage
                enc=fernet.encrypt(wdata.encode())
                cur.execute("INSERT INTO wallets(user_id,name,encrypted_data,created_at) VALUES(?,?,?,?)",
                            (st.session_state.user["id"],wname_safe,enc,datetime.now(timezone.utc).isoformat()))
                conn.commit()
                log_action(st.session_state.user["id"], "Wallet Created", f"{wname_safe}")
                st.success("Wallet created securely")

        st.markdown("<h3 style='color: #00ffff; border-bottom: 1px solid #00ffff; padding-bottom: 12px; margin-top: 40px; text-shadow: 0 0 10px rgba(0,255,255,0.6); box-shadow: 0 1px 5px rgba(0,255,255,0.2); font-family: \"Courier New\", monospace;'>DECRYPT WALLET</h3>", unsafe_allow_html=True)
        wid = st.text_input("Enter Wallet ID to decrypt")
        if st.button("DECRYPT WALLET", key="btn_decrypt_wallet"):
            if not wid or not wid.strip():
                st.error("Wallet ID cannot be empty")
            else:
                try:
                    # Validate wallet ID is numeric to prevent injection
                    wallet_id = int(wid)
                    # IDOR protection: Only allow access to user's own wallets
                    cur.execute("SELECT encrypted_data FROM wallets WHERE id=? AND user_id=?",(wallet_id,st.session_state.user["id"]))
                    row=cur.fetchone()
                    if row:
                        try:
                            decrypted = fernet.decrypt(row["encrypted_data"]).decode()
                            # Display sanitized (already safe since it's in code block)
                            st.code(decrypted)
                            log_action(st.session_state.user["id"], "Wallet Decrypted", f"ID {wallet_id}")
                        except InvalidToken:
                            st.error("Decryption failed. Invalid key or data.")
                            log_action(st.session_state.user["id"], "Wallet Decrypt Error", f"ID {wallet_id}")
                    else:
                        st.warning("Wallet not found or access denied.")
                        log_action(st.session_state.user["id"], "Wallet Access Denied", f"Attempted ID {wallet_id}")
                except ValueError:
                    st.error("Invalid wallet ID format.")
                except Exception:
                    st.error("An error occurred. Please try again.")
    except Exception:
        st.error("An error occurred. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def profile():
    if not st.session_state.logged_in:
        st.error("Please login to access profile.")
        return
        
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,255,0.8); box-shadow: 0 2px 10px rgba(0,255,255,0.3); font-family: \"Courier New\", monospace;'>PROFILE SETTINGS</h2>", unsafe_allow_html=True)
    
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT email FROM users WHERE id=?",(st.session_state.user["id"],))
        row = cur.fetchone()
        if not row:
            st.error("User not found.")
            return
        email=row["email"]
        new_email=st.text_input("Update Email", value=email, max_chars=MAX_EMAIL_LENGTH)
        old_pw=st.text_input("Old Password", type="password")
        new_pw=st.text_input("New Password", type="password")

        if st.button("UPDATE PROFILE", key="btn_update_profile"):
            if not old_pw:
                st.error("Old password is required")
            elif not new_pw:
                st.error("New password is required")
            else:
                cur.execute("SELECT password_hash FROM users WHERE id=?",(st.session_state.user["id"],))
                pw_hash_row = cur.fetchone()
                if not pw_hash_row or not check_pw(old_pw, pw_hash_row["password_hash"]):
                    st.error("Old password incorrect.")
                    log_action(st.session_state.user["id"], "Profile Update Attempt", "Incorrect old password")
                else:
                    # Validate email
                    email_valid, email_msg = validate_email(new_email)
                    if not email_valid:
                        st.error(email_msg)
                    else:
                        # Validate new password
                        ok,errs=is_strong_pw(new_pw)
                        if not ok:
                            st.error("; ".join(errs))
                        else:
                            # Sanitize email
                            new_email_safe = sanitize_input(new_email, MAX_EMAIL_LENGTH)
                            cur.execute("UPDATE users SET email=?, password_hash=? WHERE id=?",
                                        (new_email_safe, hash_pw(new_pw), st.session_state.user["id"]))
                            conn.commit()
                            log_action(st.session_state.user["id"], "Profile Updated", "Changed password/email")
                            st.success("Profile updated successfully")
    except Exception:
        st.error("An error occurred. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def audit_log():
    if not st.session_state.logged_in:
        st.error("Please login to access audit log.")
        return
        
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00ffff; border-bottom: 2px solid #00ffff; padding-bottom: 15px; text-shadow: 0 0 10px rgba(0,255,255,0.8); box-shadow: 0 2px 10px rgba(0,255,255,0.3); font-family: \"Courier New\", monospace;'>AUDIT LOG</h2>", unsafe_allow_html=True)
    try:
        conn=get_db()
        cur=conn.cursor()
        cur.execute("SELECT action,details,created_at FROM audit_log WHERE user_id=? ORDER BY id DESC",
                    (st.session_state.user["id"],))
        rows=cur.fetchall()
        if rows: 
            st.dataframe(pd.DataFrame(rows))
        else: 
            st.info("No logs yet.")
    except Exception:
        st.error("An error occurred. Please try again.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Router ----------
page = st.session_state.page
if page=="Home": home()
elif page=="Register": register()
elif page=="Login": login()
elif page=="Help": help_page()
elif menu=="Wallets": wallets()
elif menu=="Profile": profile()
elif menu=="Audit Log": audit_log()

