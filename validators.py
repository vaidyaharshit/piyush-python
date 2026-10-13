"""
validators.py - Input validation utilities for Contact Book.
Validates contact names, phone numbers, and email addresses.
"""

import re

# Email regex supporting standard formats
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)

# Phone regex allowing optional '+' at the start, followed by digits, spaces, hyphens, and parentheses
PHONE_FORMAT_REGEX = re.compile(
    r"^\+?[0-9\s\-\(\)\.]{7,25}$"
)

def validate_name(name):
    """
    Validates a contact name.
    Returns: (is_valid: bool, error_message: str)
    """
    if not name or not name.strip():
        return False, "Full Name is required."
    
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, "Name must be at least 2 characters long."
    
    if len(cleaned) > 80:
        return False, "Name cannot exceed 80 characters."
    
    # Check that name is not just digits or special characters
    if not re.search(r"[a-zA-Z\u00C0-\u017F]", cleaned):
        return False, "Name must contain at least one alphabet character."

    return True, ""

def validate_phone(phone):
    """
    Validates a contact phone number.
    Returns: (is_valid: bool, error_message: str)
    """
    if not phone or not phone.strip():
        return False, "Phone Number is required."
    
    cleaned = phone.strip()
    
    if not PHONE_FORMAT_REGEX.match(cleaned):
        return False, "Phone number contains invalid characters (digits, +, -, () allowed)."
    
    # Count actual digits
    digit_count = sum(c.isdigit() for c in cleaned)
    if digit_count < 7:
        return False, f"Phone number is too short ({digit_count} digits). Minimum 7 digits required."
    
    if digit_count > 15:
        return False, f"Phone number is too long ({digit_count} digits). Maximum 15 digits allowed (E.164 standard)."

    return True, ""

def validate_email(email):
    """
    Validates an email address. Optional field: empty string is valid.
    Returns: (is_valid: bool, error_message: str)
    """
    if not email or not email.strip():
        return True, ""  # Optional field
    
    cleaned = email.strip()
    if not EMAIL_REGEX.match(cleaned):
        return False, "Invalid email address format (example: user@example.com)."

    if len(cleaned) > 120:
        return False, "Email address is too long (max 120 characters)."

    return True, ""

def validate_contact_payload(name, phone, email):
    """
    Validates all contact inputs together.
    Returns: (is_valid: bool, error_message: str)
    """
    valid_name, err_name = validate_name(name)
    if not valid_name:
        return False, err_name

    valid_phone, err_phone = validate_phone(phone)
    if not valid_phone:
        return False, err_phone

    valid_email, err_email = validate_email(email)
    if not valid_email:
        return False, err_email

    return True, ""
