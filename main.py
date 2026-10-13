
"""
main.py - Contact Book Management System
Built with Python, CustomTkinter, and SQLite.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import database
import validators

# Set appearance theme and color palette
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "dark-blue", "green"


class DeleteConfirmModal(ctk.CTkToplevel):
    """Modern modal dialog for confirming contact deletion."""
    def __init__(self, parent, contact_name, on_confirm):
        super().__init__(parent)
        self.title("Confirm Deletion")
        self.geometry("420x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center modal relative to parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 210
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
        self.geometry(f"+{x}+{y}")

        self.on_confirm = on_confirm

        # Layout
        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        icon_label = ctk.CTkLabel(
            frame,
            text="⚠️",
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(12, 0))

        title_label = ctk.CTkLabel(
            frame,
            text="Delete Contact?",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(4, 6))

        msg_label = ctk.CTkLabel(
            frame,
            text=f"Are you sure you want to delete '{contact_name}'?\nThis action cannot be undone.",
            font=ctk.CTkFont(size=13),
            wraplength=350,
            text_color=("gray30", "gray70")
        )
        msg_label.pack(pady=(0, 15))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("black", "white"),
            width=110,
            command=self.destroy
        )
        cancel_btn.pack(side="left", expand=True, padx=6)

        delete_btn = ctk.CTkButton(
            btn_row,
            text="Delete",
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=110,
            command=self._confirm
        )
        delete_btn.pack(side="right", expand=True, padx=6)

    def _confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()


class ContactDetailsModal(ctk.CTkToplevel):
    """Modal dialog displaying all details of a selected contact."""
    def __init__(self, parent, contact, on_edit):
        super().__init__(parent)
        self.title("Contact Details")
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center relative to parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 230
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 210
        self.geometry(f"+{x}+{y}")

        card = ctk.CTkFrame(self, corner_radius=12)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        # Header with initials
        initials = "".join([part[0].upper() for part in contact["name"].split()[:2]]) if contact["name"] else "?"
        avatar = ctk.CTkLabel(
            card,
            text=initials,
            font=ctk.CTkFont(size=22, weight="bold"),
            fg_color=("#2563EB", "#1D4ED8"),
            text_color="white",
            corner_radius=24,
            width=48,
            height=48
        )
        avatar.pack(pady=(12, 4))

        name_label = ctk.CTkLabel(
            card,
            text=contact["name"],
            font=ctk.CTkFont(size=20, weight="bold")
        )
        name_label.pack(pady=(0, 10))

        # Details list frame
        info_frame = ctk.CTkFrame(card, fg_color=("gray92", "gray17"), corner_radius=8)
        info_frame.pack(fill="x", padx=16, pady=6)

        self._add_info_row(info_frame, "📞 Phone:", contact.get("phone", "—"))
        self._add_info_row(info_frame, "✉️ Email:", contact.get("email") or "—")
        self._add_info_row(info_frame, "📍 Address:", contact.get("address") or "—")
        self._add_info_row(info_frame, "📝 Notes:", contact.get("notes") or "—")
        created_str = contact.get("created_at", "—")
        self._add_info_row(info_frame, "🕒 Saved on:", created_str)

        # Action buttons
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(15, 8))

        close_btn = ctk.CTkButton(
            btn_box,
            text="Close",
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("black", "white"),
            width=100,
            command=self.destroy
        )
        close_btn.pack(side="left", padx=4)

        edit_btn = ctk.CTkButton(
            btn_box,
            text="✏️ Edit Contact",
            width=130,
            command=lambda: (self.destroy(), on_edit(contact))
        )
        edit_btn.pack(side="right", padx=4)

    def _add_info_row(self, container, label_text, val_text):
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=5)
        
        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray30", "gray70"),
            width=90,
            anchor="w"
        )
        lbl.pack(side="left")

        val = ctk.CTkLabel(
            row,
            text=val_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
            wraplength=270,
            justify="left"
        )
        val.pack(side="left", fill="x", expand=True)


class ContactBookApp(ctk.CTk):
    """Main Contact Book Application Window."""

    def __init__(self):
        super().__init__()

        # Database initialization
        database.init_db()

        # Window configuration
        self.title("ContactHub — Contact Book Management System")
        self.geometry("1100x700")
        self.minsize(980, 620)

        # State variables
        self.active_view = "all_contacts"
        self.editing_contact_id = None
        self.sort_order = "name ASC"
        self.search_query = ""

        # Layout grid setup (1 row, 2 columns: sidebar and main body)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Build UI
        self._build_sidebar()
        self._build_main_area()

        # Check and populate sample data if first time
        self._check_first_run()

        # Initial load
        self.show_all_contacts_view()

    # ==========================================
    # UI BUILDERS
    # ==========================================

    def _build_sidebar(self):
        """Constructs the left navigation sidebar."""
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Branding / Logo
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(24, 16), sticky="w")

        app_title = ctk.CTkLabel(
            logo_frame,
            text="📇 ContactHub",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        app_title.pack(anchor="w")

        app_subtitle = ctk.CTkLabel(
            logo_frame,
            text="SQLite Contact Manager",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60")
        )
        app_subtitle.pack(anchor="w")

        # Navigation Buttons
        self.nav_btn_contacts = ctk.CTkButton(
            self.sidebar_frame,
            text="👥  All Contacts",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            anchor="w",
            command=self.show_all_contacts_view
        )
        self.nav_btn_contacts.grid(row=1, column=0, padx=16, pady=6, sticky="ew")

        self.nav_btn_add = ctk.CTkButton(
            self.sidebar_frame,
            text="➕  Add Contact",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            anchor="w",
            command=self.show_add_contact_view
        )
        self.nav_btn_add.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        self.nav_btn_stats = ctk.CTkButton(
            self.sidebar_frame,
            text="📊  Dashboard Stats",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            anchor="w",
            command=self.show_stats_view
        )
        self.nav_btn_stats.grid(row=3, column=0, padx=16, pady=6, sticky="ew")

        # Bottom section: Appearance Mode & UI Scaling
        bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, padx=16, pady=16, sticky="ew")

        lbl_mode = ctk.CTkLabel(
            bottom_frame,
            text="Appearance Mode:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray30", "gray70")
        )
        lbl_mode.pack(anchor="w", pady=(0, 2))

        self.mode_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Dark", "Light", "System"],
            command=self._change_appearance_mode,
            height=30
        )
        self.mode_menu.set("Dark")
        self.mode_menu.pack(fill="x", pady=(0, 10))

        lbl_scale = ctk.CTkLabel(
            bottom_frame,
            text="Display Scaling:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray30", "gray70")
        )
        lbl_scale.pack(anchor="w", pady=(0, 2))

        self.scale_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=["90%", "100%", "110%", "120%"],
            command=self._change_scaling,
            height=30
        )
        self.scale_menu.set("100%")
        self.scale_menu.pack(fill="x")

    def _build_main_area(self):
        """Builds the main content container with top bar and dynamic view panels."""
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # ----------------- Top Navigation Bar -----------------
        self.top_bar = ctk.CTkFrame(self.main_container, height=56, corner_radius=10)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.top_bar.grid_columnconfigure(1, weight=1)

        # Page Heading
        self.page_title = ctk.CTkLabel(
            self.top_bar,
            text="All Contacts",
            font=ctk.CTkFont(size=19, weight="bold")
        )
        self.page_title.grid(row=0, column=0, padx=18, pady=10, sticky="w")

        # Search Bar Frame
        self.search_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.search_frame.grid(row=0, column=1, sticky="e", padx=12, pady=10)

        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="🔍 Search name, phone, email...",
            textvariable=self.search_var,
            width=260,
            height=34
        )
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        self.clear_search_btn = ctk.CTkButton(
            self.search_frame,
            text="✕",
            width=34,
            height=34,
            fg_color=("gray80", "gray25"),
            hover_color=("gray70", "gray35"),
            text_color=("black", "white"),
            command=self._clear_search
        )
        self.clear_search_btn.pack(side="left", padx=(0, 6))

        self.quick_add_btn = ctk.CTkButton(
            self.search_frame,
            text="+ Add Contact",
            height=34,
            width=110,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.show_add_contact_view
        )
        self.quick_add_btn.pack(side="left")

        # ----------------- View 1: Contacts Directory -----------------
        self.view_contacts = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_contacts.grid(row=1, column=0, sticky="nsew")
        self.view_contacts.grid_rowconfigure(1, weight=1)
        self.view_contacts.grid_columnconfigure(0, weight=1)

        # Filter / Sort toolbar
        toolbar = ctk.CTkFrame(self.view_contacts, height=40, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.contacts_count_label = ctk.CTkLabel(
            toolbar,
            text="Showing contacts",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("gray30", "gray70")
        )
        self.contacts_count_label.pack(side="left", padx=4)

        # Sort Dropdown
        sort_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        sort_frame.pack(side="right")

        ctk.CTkLabel(
            sort_frame,
            text="Sort by:",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        ).pack(side="left", padx=(0, 6))

        self.sort_menu = ctk.CTkOptionMenu(
            sort_frame,
            values=["Name (A - Z)", "Name (Z - A)", "Newest First", "Oldest First"],
            command=self._on_sort_changed,
            height=28,
            width=135
        )
        self.sort_menu.set("Name (A - Z)")
        self.sort_menu.pack(side="left")

        # Scrollable Contact Cards Area
        self.contacts_scroll = ctk.CTkScrollableFrame(self.view_contacts, corner_radius=10)
        self.contacts_scroll.grid(row=1, column=0, sticky="nsew")
        self.contacts_scroll.grid_columnconfigure(0, weight=1)

        # ----------------- View 2: Add / Edit Form -----------------
        self.view_form = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_form.grid(row=1, column=0, sticky="nsew")
        self.view_form.grid_rowconfigure(0, weight=1)
        self.view_form.grid_columnconfigure(0, weight=1)
        self._build_form_view()

        # ----------------- View 3: Dashboard Stats -----------------
        self.view_stats = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_stats.grid(row=1, column=0, sticky="nsew")
        self.view_stats.grid_rowconfigure(0, weight=1)
        self.view_stats.grid_columnconfigure(0, weight=1)
        self._build_stats_view()

    def _build_form_view(self):
        """Constructs the Add / Edit contact form layout."""
        # Scrollable form container so it never clips on smaller screens
        scroll_form = ctk.CTkScrollableFrame(self.view_form, corner_radius=12)
        scroll_form.grid(row=0, column=0, sticky="nsew")
        scroll_form.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(scroll_form, corner_radius=12)
        card.pack(fill="both", expand=True, padx=30, pady=20)
        card.grid_columnconfigure(0, weight=1)

        # Form Header
        self.form_header_label = ctk.CTkLabel(
            card,
            text="➕ Add New Contact",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.form_header_label.pack(anchor="w", padx=24, pady=(20, 4))

        self.form_subtitle_label = ctk.CTkLabel(
            card,
            text="Fill in contact details below. Name and Phone number are required.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.form_subtitle_label.pack(anchor="w", padx=24, pady=(0, 16))

        # Inline Alert / Notification Banner
        self.alert_frame = ctk.CTkFrame(card, corner_radius=8, height=36)
        self.alert_label = ctk.CTkLabel(
            self.alert_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.alert_label.pack(side="left", padx=12, pady=6)

        # Fields container
        fields_frame = ctk.CTkFrame(card, fg_color="transparent")
        fields_frame.pack(fill="x", padx=24, pady=10)
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=1)

        # Field: Full Name
        ctk.CTkLabel(
            fields_frame,
            text="Full Name *",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(4, 2), padx=(0, 10))

        self.name_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. Rahul Sharma or Jane Doe",
            height=38
        )
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12), padx=(0, 10))

        # Field: Phone Number
        ctk.CTkLabel(
            fields_frame,
            text="Phone Number * (Unique)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, sticky="w", pady=(4, 2), padx=(10, 0))

        self.phone_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. +91 9876543210 or 555-0199",
            height=38
        )
        self.phone_entry.grid(row=1, column=1, sticky="ew", pady=(0, 12), padx=(10, 0))

        # Field: Email Address
        ctk.CTkLabel(
            fields_frame,
            text="Email Address (Optional)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=(4, 2), padx=(0, 10))

        self.email_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. name@example.com",
            height=38
        )
        self.email_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12), padx=(0, 10))

        # Field: Address
        ctk.CTkLabel(
            fields_frame,
            text="Home / Office Address (Optional)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=1, sticky="w", pady=(4, 2), padx=(10, 0))

        self.address_entry = ctk.CTkEntry(
            fields_frame,
            placeholder_text="e.g. 221B Baker St, London",
            height=38
        )
        self.address_entry.grid(row=3, column=1, sticky="ew", pady=(0, 12), padx=(10, 0))

        # Field: Notes (Full width)
        ctk.CTkLabel(
            fields_frame,
            text="Additional Notes / Remarks (Optional)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 2))

        self.notes_textbox = ctk.CTkTextbox(
            fields_frame,
            height=85,
            corner_radius=8
        )
        self.notes_textbox.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        # Buttons Row
        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.pack(fill="x", padx=24, pady=(0, 24))

        self.save_btn = ctk.CTkButton(
            action_row,
            text="💾  Save Contact",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            width=150,
            command=self._handle_save_contact
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            action_row,
            text="🧹  Clear Form",
            font=ctk.CTkFont(size=13),
            height=40,
            width=120,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("black", "white"),
            command=self._clear_form
        )
        self.clear_btn.pack(side="left", padx=(0, 10))

        self.cancel_form_btn = ctk.CTkButton(
            action_row,
            text="← Back to All Contacts",
            font=ctk.CTkFont(size=13),
            height=40,
            width=160,
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray20", "gray80"),
            command=self.show_all_contacts_view
        )
        self.cancel_form_btn.pack(side="left")

    def _build_stats_view(self):
        """Constructs the statistics & project info dashboard."""
        scroll_stats = ctk.CTkScrollableFrame(self.view_stats, corner_radius=12)
        scroll_stats.grid(row=0, column=0, sticky="nsew")
        scroll_stats.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(scroll_stats, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=16)

        header = ctk.CTkLabel(
            container,
            text="📊 System Overview & Statistics",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(anchor="w", pady=(0, 16))

        # Metric Cards Frame
        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Total Contacts Card
        self.card_total = self._create_metric_card(
            cards_frame, 0, "Total Contacts", "0", "👥", "#2563EB"
        )
        # Contacts with Email Card
        self.card_email = self._create_metric_card(
            cards_frame, 1, "With Email Address", "0", "✉️", "#059669"
        )
        # Database Status Card
        self.card_db = self._create_metric_card(
            cards_frame, 2, "Database Engine", "SQLite3", "💾", "#7C3AED"
        )

        # Practical Info & Viva Card
        info_card = ctk.CTkFrame(container, corner_radius=12)
        info_card.pack(fill="x", pady=(0, 20), padx=2)

        info_title = ctk.CTkLabel(
            info_card,
            text="💡 Project Features & Architecture",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        info_title.pack(anchor="w", padx=18, pady=(16, 8))

        features_text = (
            "• GUI Framework: CustomTkinter with responsive grid layout and light/dark mode support.\n"
            "• Database Engine: SQLite with permanent storage, table schema, and parameterized queries.\n"
            "• Duplicate Check: Unique constraint on phone numbers prevents duplicate contact records.\n"
            "• Form Validation: Checks required fields, phone length & format, and RFC-compliant emails.\n"
            "• Instant Search: Real-time query matching across name, phone, and email records.\n"
            "• Clean Architecture: Modular design separating database.py, validators.py, and main.py."
        )
        info_desc = ctk.CTkLabel(
            info_card,
            text=features_text,
            font=ctk.CTkFont(size=13),
            justify="left",
            text_color=("gray30", "gray70")
        )
        info_desc.pack(anchor="w", padx=18, pady=(0, 16))

        # Quick Demo Data Actions
        actions_card = ctk.CTkFrame(container, corner_radius=12)
        actions_card.pack(fill="x", padx=2)

        ctk.CTkLabel(
            actions_card,
            text="⚡ Quick Management Actions",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", padx=18, pady=(16, 6))

        btn_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(6, 18))

        load_demo_btn = ctk.CTkButton(
            btn_row,
            text="⚡ Load Demo Sample Contacts",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36,
            command=self._load_sample_contacts
        )
        load_demo_btn.pack(side="left", padx=(0, 10))

        clear_all_btn = ctk.CTkButton(
            btn_row,
            text="🗑️ Delete All Contacts",
            font=ctk.CTkFont(size=13),
            height=36,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._confirm_clear_all
        )
        clear_all_btn.pack(side="left")

    def _create_metric_card(self, parent, col, title, value, icon, accent_color):
        """Creates a modern KPI card."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 4))

        lbl_title = ctk.CTkLabel(
            top_row,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        lbl_title.pack(side="left")

        lbl_icon = ctk.CTkLabel(
            top_row,
            text=icon,
            font=ctk.CTkFont(size=18)
        )
        lbl_icon.pack(side="right")

        val_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=accent_color
        )
        val_label.pack(anchor="w", padx=16, pady=(0, 14))

        return val_label

    # ==========================================
    # NAVIGATION & VIEW SWITCHING
    # ==========================================

    def _set_active_nav(self, active_btn):
        """Updates sidebar button styles to highlight the active tab."""
        for btn in [self.nav_btn_contacts, self.nav_btn_add, self.nav_btn_stats]:
            if btn == active_btn:
                btn.configure(fg_color=("#2563EB", "#1D4ED8"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

    def show_all_contacts_view(self):
        """Switches to the All Contacts Directory view."""
        self.active_view = "all_contacts"
        self._set_active_nav(self.nav_btn_contacts)
        self.page_title.configure(text="All Contacts")
        self.search_frame.grid()  # Show search bar

        self.view_form.grid_remove()
        self.view_stats.grid_remove()
        self.view_contacts.grid()

        self._refresh_contacts_list()

    def show_add_contact_view(self):
        """Switches to the Add Contact form view."""
        self.active_view = "add_contact"
        self.editing_contact_id = None
        self._set_active_nav(self.nav_btn_add)
        self.page_title.configure(text="Add New Contact")
        self.search_frame.grid_remove()  # Hide search bar on form view

        self.form_header_label.configure(text="➕ Add New Contact")
        self.form_subtitle_label.configure(text="Fill in contact details below. Name and Phone number are required.")
        self.save_btn.configure(text="💾  Save Contact")
        self._hide_alert()
        self._clear_form()

        self.view_contacts.grid_remove()
        self.view_stats.grid_remove()
        self.view_form.grid()

        self.name_entry.focus()

    def show_edit_contact_view(self, contact):
        """Populates and opens the form for editing an existing contact."""
        self.active_view = "edit_contact"
        self.editing_contact_id = contact["id"]
        self._set_active_nav(None)
        self.page_title.configure(text=f"Edit Contact: {contact['name']}")
        self.search_frame.grid_remove()

        self.form_header_label.configure(text=f"✏️ Edit Contact: {contact['name']}")
        self.form_subtitle_label.configure(text=f"Editing record ID #{contact['id']}. Update fields and click Save.")
        self.save_btn.configure(text="💾  Update Contact")
        self._hide_alert()

        # Populate form fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, contact.get("name", ""))

        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, contact.get("phone", ""))

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, contact.get("email", "") or "")

        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, contact.get("address", "") or "")

        self.notes_textbox.delete("1.0", tk.END)
        self.notes_textbox.insert("1.0", contact.get("notes", "") or "")

        self.view_contacts.grid_remove()
        self.view_stats.grid_remove()
        self.view_form.grid()

        self.name_entry.focus()

    def show_stats_view(self):
        """Switches to the Dashboard Stats view."""
        self.active_view = "stats"
        self._set_active_nav(self.nav_btn_stats)
        self.page_title.configure(text="Dashboard & Analytics")
        self.search_frame.grid_remove()

        stats = database.get_stats()
        self.card_total.configure(text=str(stats["total_contacts"]))
        self.card_email.configure(text=str(stats["contacts_with_email"]))

        self.view_contacts.grid_remove()
        self.view_form.grid_remove()
        self.view_stats.grid()

    # ==========================================
    # CONTACTS LIST RENDERING & SEARCH
    # ==========================================

    def _refresh_contacts_list(self):
        """Fetches and displays contacts in the scrollable cards list."""
        # Clear existing card widgets
        for widget in self.contacts_scroll.winfo_children():
            widget.destroy()

        if self.search_query.strip():
            contacts = database.search_contacts(self.search_query.strip())
            count_text = f"Found {len(contacts)} contact(s) matching '{self.search_query.strip()}'"
        else:
            contacts = database.get_all_contacts(order_by=self.sort_order)
            count_text = f"Total Contacts: {len(contacts)}"

        self.contacts_count_label.configure(text=count_text)

        # Empty state handling
        if not contacts:
            self._render_empty_state()
            return

        # Render contact cards
        for index, contact in enumerate(contacts):
            self._render_contact_card(contact, index)

    def _render_empty_state(self):
        """Displays a clean empty state card when no contacts are found."""
        empty_frame = ctk.CTkFrame(self.contacts_scroll, corner_radius=12, fg_color=("gray95", "gray18"))
        empty_frame.pack(fill="x", expand=True, padx=20, pady=40)

        icon_label = ctk.CTkLabel(
            empty_frame,
            text="📇",
            font=ctk.CTkFont(size=44)
        )
        icon_label.pack(pady=(28, 6))

        if self.search_query.strip():
            heading = f"No contacts found for '{self.search_query.strip()}'"
            sub = "Try checking for spelling mistakes or search by phone number."
        else:
            heading = "No contacts saved yet"
            sub = "Get started by adding your first contact or load demo data."

        title_label = ctk.CTkLabel(
            empty_frame,
            text=heading,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 4))

        sub_label = ctk.CTkLabel(
            empty_frame,
            text=sub,
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        sub_label.pack(pady=(0, 20))

        btn_box = ctk.CTkFrame(empty_frame, fg_color="transparent")
        btn_box.pack(pady=(0, 28))

        add_first_btn = ctk.CTkButton(
            btn_box,
            text="➕ Add New Contact",
            height=36,
            command=self.show_add_contact_view
        )
        add_first_btn.pack(side="left", padx=6)

        if not self.search_query.strip():
            seed_btn = ctk.CTkButton(
                btn_box,
                text="⚡ Load Sample Contacts",
                height=36,
                fg_color=("gray75", "gray30"),
                hover_color=("gray65", "gray40"),
                text_color=("black", "white"),
                command=self._load_sample_contacts
            )
            seed_btn.pack(side="left", padx=6)

    def _render_contact_card(self, contact, index):
        """Renders an individual contact card row."""
        card = ctk.CTkFrame(
            self.contacts_scroll,
            corner_radius=10,
            fg_color=("white", "gray17"),
            border_width=1,
            border_color=("gray85", "gray23")
        )
        card.pack(fill="x", expand=True, padx=4, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # 1. Avatar badge with initials
        initials = "".join([part[0].upper() for part in contact["name"].split()[:2]]) if contact["name"] else "?"
        # Color rotation based on ID
        colors = [
            ("#2563EB", "#1D4ED8"),
            ("#059669", "#047857"),
            ("#7C3AED", "#6D28D9"),
            ("#D97706", "#B45309"),
            ("#DC2626", "#B91C1C")
        ]
        badge_color = colors[contact["id"] % len(colors)]

        avatar = ctk.CTkLabel(
            card,
            text=initials,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=badge_color,
            text_color="white",
            corner_radius=20,
            width=42,
            height=42
        )
        avatar.grid(row=0, column=0, rowspan=2, padx=(14, 12), pady=12, sticky="w")

        # 2. Main Contact Info
        info_col = ctk.CTkFrame(card, fg_color="transparent")
        info_col.grid(row=0, column=1, rowspan=2, sticky="nsew", pady=10)

        # Name row
        name_row = ctk.CTkFrame(info_col, fg_color="transparent")
        name_row.pack(anchor="w", fill="x")

        name_lbl = ctk.CTkLabel(
            name_row,
            text=contact["name"],
            font=ctk.CTkFont(size=15, weight="bold")
        )
        name_lbl.pack(side="left")

        # Details row: Phone & Email
        meta_row = ctk.CTkFrame(info_col, fg_color="transparent")
        meta_row.pack(anchor="w", fill="x", pady=(2, 2))

        phone_text = f"📞 {contact['phone']}"
        phone_lbl = ctk.CTkLabel(
            meta_row,
            text=phone_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        phone_lbl.pack(side="left", padx=(0, 16))

        if contact.get("email"):
            email_text = f"✉️ {contact['email']}"
            email_lbl = ctk.CTkLabel(
                meta_row,
                text=email_text,
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60")
            )
            email_lbl.pack(side="left", padx=(0, 16))

        if contact.get("address"):
            addr_text = f"📍 {contact['address']}"
            addr_lbl = ctk.CTkLabel(
                meta_row,
                text=addr_text,
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60")
            )
            addr_lbl.pack(side="left")

        # Optional note snippet
        if contact.get("notes"):
            note_snip = contact['notes'][:60] + ("..." if len(contact['notes']) > 60 else "")
            note_lbl = ctk.CTkLabel(
                info_col,
                text=f"📝 {note_snip}",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color=("gray50", "gray50")
            )
            note_lbl.pack(anchor="w", pady=(1, 0))

        # 3. Action Buttons on Right
        action_col = ctk.CTkFrame(card, fg_color="transparent")
        action_col.grid(row=0, column=2, rowspan=2, padx=12, pady=10, sticky="e")

        view_btn = ctk.CTkButton(
            action_col,
            text="👁️ View",
            width=68,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=("gray85", "gray28"),
            hover_color=("gray75", "gray35"),
            text_color=("black", "white"),
            command=lambda c=contact: self._open_details_modal(c)
        )
        view_btn.pack(side="left", padx=3)

        edit_btn = ctk.CTkButton(
            action_col,
            text="✏️ Edit",
            width=68,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=("#2563EB", "#1D4ED8"),
            hover_color=("#1D4ED8", "#1E40AF"),
            command=lambda c=contact: self.show_edit_contact_view(c)
        )
        edit_btn.pack(side="left", padx=3)

        delete_btn = ctk.CTkButton(
            action_col,
            text="🗑️ Delete",
            width=70,
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=("#EF4444", "#DC2626"),
            hover_color=("#DC2626", "#B91C1C"),
            command=lambda c=contact: self._confirm_delete_contact(c)
        )
        delete_btn.pack(side="left", padx=3)

    # ==========================================
    # SEARCH & SORT HANDLERS
    # ==========================================

    def _on_search_key(self, event=None):
        """Triggers real-time search filtering."""
        self.search_query = self.search_var.get()
        self._refresh_contacts_list()

    def _clear_search(self):
        """Resets the search input and restores full contacts list."""
        self.search_var.set("")
        self.search_query = ""
        self._refresh_contacts_list()

    def _on_sort_changed(self, choice):
        """Handles sorting order selection."""
        mapping = {
            "Name (A - Z)": "name ASC",
            "Name (Z - A)": "name DESC",
            "Newest First": "id DESC",
            "Oldest First": "id ASC"
        }
        self.sort_order = mapping.get(choice, "name ASC")
        self._refresh_contacts_list()

    # ==========================================
    # FORM SUBMISSION & VALIDATION
    # ==========================================

    def _handle_save_contact(self):
        """Validates inputs and saves new contact or updates existing contact."""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()
        notes = self.notes_textbox.get("1.0", tk.END).strip()

        # Input Validation
        is_valid, err_msg = validators.validate_contact_payload(name, phone, email)
        if not is_valid:
            self._show_alert(err_msg, is_error=True)
            return

        # Perform Add or Update
        if self.editing_contact_id is None:
            # Adding new contact
            success, msg, _ = database.add_contact(name, phone, email, address, notes)
            if success:
                self._show_alert("Contact successfully created!", is_error=False)
                # Auto redirect back to all contacts after brief pause
                self.after(600, self.show_all_contacts_view)
            else:
                self._show_alert(msg, is_error=True)
        else:
            # Updating existing contact
            success, msg = database.update_contact(
                self.editing_contact_id, name, phone, email, address, notes
            )
            if success:
                self._show_alert("Contact successfully updated!", is_error=False)
                self.after(600, self.show_all_contacts_view)
            else:
                self._show_alert(msg, is_error=True)

    def _clear_form(self):
        """Clears all form fields."""
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.notes_textbox.delete("1.0", tk.END)
        self._hide_alert()

    def _show_alert(self, message, is_error=True):
        """Displays inline message banner."""
        if is_error:
            fg = ("#FEE2E2", "#450A0A")
            txt_color = ("#991B1B", "#FCA5A5")
            icon = "❌ "
        else:
            fg = ("#DCFCE7", "#052E16")
            txt_color = ("#166534", "#86EFAC")
            icon = "✅ "

        self.alert_frame.configure(fg_color=fg)
        self.alert_label.configure(text=f"{icon}{message}", text_color=txt_color)
        self.alert_frame.pack(fill="x", padx=24, pady=(0, 10))

    def _hide_alert(self):
        """Hides the message banner."""
        self.alert_frame.pack_forget()

    # ==========================================
    # MODALS & ACTIONS
    # ==========================================

    def _open_details_modal(self, contact):
        """Opens full contact details modal window."""
        ContactDetailsModal(
            self,
            contact,
            on_edit=self.show_edit_contact_view
        )

    def _confirm_delete_contact(self, contact):
        """Displays custom delete confirmation dialog."""
        def execute_delete():
            success, msg = database.delete_contact(contact["id"])
            if success:
                self._refresh_contacts_list()
            else:
                messagebox.showerror("Error", msg)

        DeleteConfirmModal(self, contact["name"], execute_delete)

    def _confirm_clear_all(self):
        """Prompts confirmation before deleting all contacts from database."""
        def execute_clear():
            with database.get_connection() as conn:
                conn.execute("DELETE FROM contacts")
                conn.commit()
            self.show_stats_view()

        DeleteConfirmModal(self, "ALL CONTACTS", execute_clear)

    def _load_sample_contacts(self):
        """Loads realistic demo contacts for presentations and testing."""
        samples = [
            ("Rahul Sharma", "+91 9876543210", "rahul.sharma@example.com", "Connaught Place, New Delhi", "Software Engineer at TechCorp"),
            ("Aanya Patel", "+91 9822011223", "aanya.patel@workmail.org", "Satellite Road, Ahmedabad", "College Project Partner"),
            ("Michael Brown", "+1 415-555-0199", "michael.b@california.edu", "742 Evergreen Terrace, San Francisco", "Professor - Computer Science"),
            ("Priya Nair", "+91 9447123456", "priya.nair@webmail.in", "Marine Drive, Kochi", "Freelance UI/UX Designer"),
        ]
        added = 0
        for name, phone, email, addr, notes in samples:
            success, _, _ = database.add_contact(name, phone, email, addr, notes)
            if success:
                added += 1

        self.show_all_contacts_view()

    def _check_first_run(self):
        """On initial first launch, populate sample data so the app looks complete."""
        stats = database.get_stats()
        if stats["total_contacts"] == 0:
            self._load_sample_contacts()

    # ==========================================
    # SETTINGS & APPEARANCE
    # ==========================================

    def _change_appearance_mode(self, new_mode):
        """Changes the UI appearance mode (Dark, Light, System)."""
        ctk.set_appearance_mode(new_mode)

    def _change_scaling(self, new_scale):
        """Changes window and widget scaling."""
        scale_float = int(new_scale.replace("%", "")) / 100
        ctk.set_widget_scaling(scale_float)


if __name__ == "__main__":
    app = ContactBookApp()
    app.mainloop()
