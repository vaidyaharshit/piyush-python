# 📇 ContactHub — Contact Book Management System

A modern, desktop-based **Contact Book Management System** built with **Python**, **CustomTkinter**, and **SQLite**. 

Designed for academic practical demonstrations, personal contact management, and professional project presentations.

---

## 🌟 Key Features

- **Add Contact:** Save contact details including Full Name, Phone Number, Email, Address, and Notes.
- **View All Contacts:** Clean, organized list of contacts presented in cards with colored initial avatars and quick action buttons.
- **Instant Search:** Real-time search by Contact Name, Phone Number, or Email address.
- **Update / Edit Contact:** Pre-populates contact details into the form for easy updating.
- **Delete Contact with Confirmation:** Custom modern modal dialog to prevent accidental contact deletion.
- **Contact Details Modal:** Quick popup view showing complete information with timestamps.
- **Persistent SQLite Storage:** Permanent data storage using SQLite (`contacts.db`) with automatic table creation on first launch.
- **Data Validation & Duplicate Prevention:**
  - Full Name (required, alphabet verification)
  - Phone Number (required, format & digit length validation: 7–15 digits)
  - Unique Phone Number check (prevents duplicate phone numbers)
  - RFC-compliant Email format verification (optional field)
- **Modern UI / UX:**
  - Responsive layout (Sidebar navigation + dynamic main area)
  - Light & Dark mode support (switchable on-the-fly)
  - UI scaling support (90%, 100%, 110%, 120%)
  - Sorting (A-Z, Z-A, Newest First, Oldest First)
  - Inline feedback alerts for errors and success messages
  - 1-click **Load Demo Contacts** for instant practical viva demonstration

---

## 📁 Project Structure

```text
e:/piyush pytjon/
│
├── main.py            # Main application window, UI layout, routing & event handlers
├── database.py        # SQLite database connection, table initialization & CRUD functions
├── validators.py      # Input validation utilities (Name, Phone, Email)
├── requirements.txt   # Project dependencies (customtkinter)
├── contacts.db        # SQLite database file (created automatically on first launch)
└── README.md          # Project documentation and guide
```

---

## 🚀 Getting Started on Windows

### 1. Prerequisites
- Python 3.8 or higher installed on your Windows machine.
- Verify Python installation in PowerShell or Command Prompt:
  ```powershell
  python --version
  ```

### 2. Install Dependencies
Open **Command Prompt** or **PowerShell** in the project folder and run:
```powershell
pip install -r requirements.txt
```
*(Or install directly: `pip install customtkinter`)*

### 3. Run the Application
Execute the following command in terminal:
```powershell
python main.py
```

---

## 📊 Database Schema

The application uses an SQLite database (`contacts.db`) initialized automatically:

```sql
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎓 College Practical / Viva Q&A Guide

| Question | Answer / Explanation |
| :--- | :--- |
| **Why CustomTkinter instead of standard Tkinter?** | CustomTkinter provides modern UI widgets, rounded corners, dark/light theme switching, and high DPI scaling out-of-the-box. |
| **Why SQLite?** | SQLite is a serverless, self-contained, zero-configuration SQL database engine embedded directly into Python standard library (`sqlite3`). |
| **How is duplicate phone number prevented?** | By using a `UNIQUE` constraint in the SQLite schema as well as a pre-check query (`phone_exists()`) before inserting or updating. |
| **How does real-time search work?** | An event binding `<KeyRelease>` on the search entry dynamically executes `SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?`. |
