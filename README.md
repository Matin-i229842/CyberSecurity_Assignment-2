# 💎 Secure Crypto Wallet

### Developed by: **M. Matin Khan**  
**Roll No.: 22i-9842**  
**Instructor:** Dr. Osama Arshad  
**Course:** Cybersecurity for FinTech  

---

## 🚀 Project Overview

**Secure Crypto Wallet** is a **Streamlit-based web application** designed to provide a **secure platform for managing encrypted cryptocurrency wallets**.  
It integrates advanced security mechanisms including:

- 🔐 **Password Hashing (bcrypt)**  
- 🔒 **AES-256 Data Encryption**  
- 🛡️ **SQL Injection & XSS Prevention**  
- 📋 **Comprehensive Audit Logging**  
- ⏱️ **Session Timeout and Login Lockout Protection**

This project demonstrates **secure software engineering principles** applied within a **FinTech cybersecurity** context.

---

## 🧩 Key Features

| Category | Description |
|-----------|-------------|
| **User Management** | Secure registration and login with strong password enforcement |
| **Encryption** | Uses AES-256 (via Fernet) to encrypt wallet data |
| **Data Integrity** | Sanitized inputs and validation against SQL Injection & XSS |
| **Audit Logging** | Every user action is recorded for traceability |
| **Session Security** | Idle sessions auto-expire to prevent hijacking |
| **Profile Management** | Email and password updates with full validation |
| **Modern UI** | Neon dark-theme interface designed for readability and user focus |

---

## 🧠 Technical Stack

- **Frontend:** Streamlit (Python)
- **Backend:** SQLite3
- **Security Libraries:** bcrypt, cryptography (Fernet)
- **Language:** Python 3.x
- **Data Handling:** pandas
- **Additional Modules:** datetime, re, os, html

---

## 🧪 Security Test Summary

| Test Area | Description | Result |
|------------|-------------|--------|
| Input Validation | SQL Injection, XSS, and empty field validation | ✅ Pass |
| Password Policies | Weak & strong password handling | ✅ Pass |
| Encryption | AES-256 encryption confirmed | ✅ Pass |
| Session Handling | Timeout & logout functionality verified | ✅ Pass |
| Access Control | Unauthorized access and IDOR prevention | ✅ Pass |
| Audit Logs | Accurate tracking of all user actions | ✅ Pass |
| Error Handling | Graceful error control, no data leaks | ✅ Pass |

All **25 security test cases** were executed successfully (see `matin.pdf` for full QA results).

---

## 🛠️ How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
pip install -r requirements.txt
streamlit run app.py
├── app.py              # Main Streamlit application
├── wallet_app.db       # SQLite database (auto-generated)
├── secret.key          # AES encryption key (auto-generated)
├── matin.pdf           # Security & QA test report
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
