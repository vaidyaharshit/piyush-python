"""
database.py - SQLite Database Management for Contact Book Application.
Handles initialization, connection, and full CRUD operations.
"""

import sqlite3
import os

DB_FILENAME = "contacts.db"

def get_db_path():
    """Returns the absolute path to the SQLite database file in the same directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_FILENAME)

def get_connection():
    """Returns a SQLite connection object with row factory set to sqlite3.Row."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database and creates the contacts table if it doesn't exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT,
                address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def phone_exists(phone, exclude_id=None):
    """
    Checks if a phone number is already registered.
    If exclude_id is provided, excludes that record (used when updating).
    """
    clean_phone = phone.strip()
    with get_connection() as conn:
        cursor = conn.cursor()
        if exclude_id is not None:
            cursor.execute(
                "SELECT id FROM contacts WHERE phone = ? AND id != ?",
                (clean_phone, exclude_id)
            )
        else:
            cursor.execute(
                "SELECT id FROM contacts WHERE phone = ?",
                (clean_phone,)
            )
        return cursor.fetchone() is not None

def add_contact(name, phone, email="", address="", notes=""):
    """
    Adds a new contact to the database.
    Returns: (success: bool, message: str, contact_id: int or None)
    """
    clean_name = name.strip()
    clean_phone = phone.strip()
    clean_email = email.strip() if email else ""
    clean_address = address.strip() if address else ""
    clean_notes = notes.strip() if notes else ""

    if phone_exists(clean_phone):
        return False, f"A contact with phone number '{clean_phone}' already exists.", None

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (name, phone, email, address, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (clean_name, clean_phone, clean_email, clean_address, clean_notes))
            conn.commit()
            return True, "Contact successfully added!", cursor.lastrowid
    except sqlite3.IntegrityError as e:
        return False, f"Database Integrity Error: {str(e)}", None
    except Exception as e:
        return False, f"Failed to save contact: {str(e)}", None

def get_all_contacts(order_by="name ASC"):
    """
    Retrieves all contacts sorted by the specified column.
    Returns list of dictionaries.
    """
    allowed_orders = {
        "name ASC": "name COLLATE NOCASE ASC",
        "name DESC": "name COLLATE NOCASE DESC",
        "id DESC": "id DESC",
        "id ASC": "id ASC"
    }
    order_clause = allowed_orders.get(order_by, "name COLLATE NOCASE ASC")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM contacts ORDER BY {order_clause}")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_contact_by_id(contact_id):
    """
    Retrieves a single contact by its primary key ID.
    Returns dictionary or None.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def search_contacts(search_term):
    """
    Searches contacts by matching name, phone number, or email.
    Case-insensitive search.
    Returns list of dictionaries.
    """
    query = f"%{search_term.strip()}%"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY name COLLATE NOCASE ASC
        """, (query, query, query))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_contact(contact_id, name, phone, email="", address="", notes=""):
    """
    Updates an existing contact's information.
    Returns: (success: bool, message: str)
    """
    clean_name = name.strip()
    clean_phone = phone.strip()
    clean_email = email.strip() if email else ""
    clean_address = address.strip() if address else ""
    clean_notes = notes.strip() if notes else ""

    if phone_exists(clean_phone, exclude_id=contact_id):
        return False, f"Another contact already uses phone number '{clean_phone}'."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts
                SET name = ?, phone = ?, email = ?, address = ?, notes = ?
                WHERE id = ?
            """, (clean_name, clean_phone, clean_email, clean_address, clean_notes, contact_id))
            conn.commit()
            if cursor.rowcount == 0:
                return False, f"Contact with ID {contact_id} not found."
            return True, "Contact successfully updated!"
    except sqlite3.IntegrityError as e:
        return False, f"Database Integrity Error: {str(e)}"
    except Exception as e:
        return False, f"Failed to update contact: {str(e)}"

def delete_contact(contact_id):
    """
    Deletes a contact by ID from the database.
    Returns: (success: bool, message: str)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, f"Contact with ID {contact_id} not found."
            return True, "Contact successfully deleted!"
    except Exception as e:
        return False, f"Failed to delete contact: {str(e)}"

def get_stats():
    """
    Returns summary metrics for the dashboard.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM contacts")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS with_email FROM contacts WHERE email IS NOT NULL AND email != ''")
        with_email = cursor.fetchone()["with_email"]

        return {
            "total_contacts": total,
            "contacts_with_email": with_email,
        }
