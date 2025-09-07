"""
GUI für Sicherheits- und Benutzerverwaltung
"""
import customtkinter as ctk
from typing import Dict, Any, Optional, List
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import threading

from ..utils.security_manager import (
    SecurityManager, User, UserRole, Permission, AuditEvent, 
    AuditEventType, SecurityLevel
)
from src.utils.theme_manager import theme_manager


class SecuritySettingsWindow:
    """Fenster für Sicherheitseinstellungen"""
    
    def __init__(self, parent, security_manager: SecurityManager):
        self.parent = parent
        self.security_manager = security_manager
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Sicherheitseinstellungen")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # Zentrieren
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"1000x700+{x}+{y}")
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Notebook für Tabs
        self.notebook = ctk.CTkTabview(self.window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tabs erstellen
        self.create_users_tab()
        self.create_security_tab()
        self.create_audit_tab()
        self.create_statistics_tab()
    
    def create_users_tab(self):
        """Erstellt Benutzer-Tab"""
        tab = self.notebook.add("Benutzer")
        
        # Toolbar
        toolbar_frame = ctk.CTkFrame(tab)
        toolbar_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        add_btn = ctk.CTkButton(
            toolbar_frame,
            text="➕ Neuer Benutzer",
            command=self.add_user
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            toolbar_frame,
            text="✏️ Bearbeiten",
            command=self.edit_user
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            toolbar_frame,
            text="🗑️ Löschen",
            command=self.delete_user,
            fg_color="red"
        )
        delete_btn.pack(side="left", padx=5)
        
        unlock_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔓 Entsperren",
            command=self.unlock_user
        )
        unlock_btn.pack(side="left", padx=5)
        
        reset_pw_btn = ctk.CTkButton(
            toolbar_frame,
            text="🔑 Passwort zurücksetzen",
            command=self.reset_password
        )
        reset_pw_btn.pack(side="left", padx=5)
        
        # Benutzerliste
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview für Benutzer
        columns = ("username", "email", "role", "status", "last_login", "failed_attempts")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Spalten konfigurieren
        self.users_tree.heading("username", text="Benutzername")
        self.users_tree.heading("email", text="E-Mail")
        self.users_tree.heading("role", text="Rolle")
        self.users_tree.heading("status", text="Status")
        self.users_tree.heading("last_login", text="Letzter Login")
        self.users_tree.heading("failed_attempts", text="Fehlversuche")
        
        self.users_tree.column("username", width=150)
        self.users_tree.column("email", width=200)
        self.users_tree.column("role", width=120)
        self.users_tree.column("status", width=100)
        self.users_tree.column("last_login", width=150)
        self.users_tree.column("failed_attempts", width=100)
        
        # Scrollbar
        users_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.pack(side="left", fill="both", expand=True)
        users_scrollbar.pack(side="right", fill="y")
    
    def create_security_tab(self):
        """Erstellt Sicherheits-Tab"""
        tab = self.notebook.add("Sicherheit")
        
        # Scrollable Frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Passwort-Richtlinien
        password_frame = ctk.CTkFrame(scroll_frame)
        password_frame.pack(fill="x", pady=(0, 10))
        
        password_label = ctk.CTkLabel(password_frame, text="Passwort-Richtlinien", font=("Arial", 16, "bold"))
        password_label.pack(pady=10)
        
        # Mindestlänge
        length_frame = ctk.CTkFrame(password_frame)
        length_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(length_frame, text="Mindestlänge:").pack(side="left", padx=5)
        self.min_length_var = ctk.StringVar(value=str(self.security_manager.settings['password_min_length']))
        length_entry = ctk.CTkEntry(length_frame, textvariable=self.min_length_var, width=100)
        length_entry.pack(side="left", padx=5)
        
        # Checkbox-Optionen
        self.require_uppercase_var = ctk.BooleanVar(value=self.security_manager.settings['password_require_uppercase'])
        ctk.CTkCheckBox(password_frame, text="Großbuchstaben erforderlich", variable=self.require_uppercase_var).pack(anchor="w", padx=10, pady=2)
        
        self.require_lowercase_var = ctk.BooleanVar(value=self.security_manager.settings['password_require_lowercase'])
        ctk.CTkCheckBox(password_frame, text="Kleinbuchstaben erforderlich", variable=self.require_lowercase_var).pack(anchor="w", padx=10, pady=2)
        
        self.require_numbers_var = ctk.BooleanVar(value=self.security_manager.settings['password_require_numbers'])
        ctk.CTkCheckBox(password_frame, text="Zahlen erforderlich", variable=self.require_numbers_var).pack(anchor="w", padx=10, pady=2)
        
        self.require_special_var = ctk.BooleanVar(value=self.security_manager.settings['password_require_special'])
        ctk.CTkCheckBox(password_frame, text="Sonderzeichen erforderlich", variable=self.require_special_var).pack(anchor="w", padx=10, pady=2)
        
        # Passwort-Alter
        age_frame = ctk.CTkFrame(password_frame)
        age_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(age_frame, text="Max. Alter (Tage):").pack(side="left", padx=5)
        self.password_age_var = ctk.StringVar(value=str(self.security_manager.settings['password_max_age_days']))
        age_entry = ctk.CTkEntry(age_frame, textvariable=self.password_age_var, width=100)
        age_entry.pack(side="left", padx=5)
        
        # Login-Sicherheit
        login_frame = ctk.CTkFrame(scroll_frame)
        login_frame.pack(fill="x", pady=(0, 10))
        
        login_label = ctk.CTkLabel(login_frame, text="Login-Sicherheit", font=("Arial", 16, "bold"))
        login_label.pack(pady=10)
        
        # Max. Fehlversuche
        attempts_frame = ctk.CTkFrame(login_frame)
        attempts_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(attempts_frame, text="Max. Fehlversuche:").pack(side="left", padx=5)
        self.max_attempts_var = ctk.StringVar(value=str(self.security_manager.settings['max_failed_login_attempts']))
        attempts_entry = ctk.CTkEntry(attempts_frame, textvariable=self.max_attempts_var, width=100)
        attempts_entry.pack(side="left", padx=5)
        
        # Sperrzeit
        lockout_frame = ctk.CTkFrame(login_frame)
        lockout_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lockout_frame, text="Sperrzeit (Minuten):").pack(side="left", padx=5)
        self.lockout_duration_var = ctk.StringVar(value=str(self.security_manager.settings['account_lockout_duration_minutes']))
        lockout_entry = ctk.CTkEntry(lockout_frame, textvariable=self.lockout_duration_var, width=100)
        lockout_entry.pack(side="left", padx=5)
        
        # Session-Timeout
        session_frame = ctk.CTkFrame(login_frame)
        session_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(session_frame, text="Session-Timeout (Minuten):").pack(side="left", padx=5)
        self.session_timeout_var = ctk.StringVar(value=str(self.security_manager.settings['session_timeout_minutes']))
        session_entry = ctk.CTkEntry(session_frame, textvariable=self.session_timeout_var, width=100)
        session_entry.pack(side="left", padx=5)
        
        # Verschlüsselung
        encryption_frame = ctk.CTkFrame(scroll_frame)
        encryption_frame.pack(fill="x", pady=(0, 10))
        
        encryption_label = ctk.CTkLabel(encryption_frame, text="Verschlüsselung", font=("Arial", 16, "bold"))
        encryption_label.pack(pady=10)
        
        self.data_encryption_var = ctk.BooleanVar(value=self.security_manager.settings['data_encryption_enabled'])
        ctk.CTkCheckBox(encryption_frame, text="Datenverschlüsselung aktiviert", variable=self.data_encryption_var).pack(anchor="w", padx=10, pady=2)
        
        self.backup_encryption_var = ctk.BooleanVar(value=self.security_manager.settings['backup_encryption_enabled'])
        ctk.CTkCheckBox(encryption_frame, text="Backup-Verschlüsselung aktiviert", variable=self.backup_encryption_var).pack(anchor="w", padx=10, pady=2)
        
        # Speichern-Button
        save_btn = ctk.CTkButton(
            scroll_frame,
            text="💾 Einstellungen speichern",
            command=self.save_security_settings
        )
        save_btn.pack(pady=20)
    
    def create_audit_tab(self):
        """Erstellt Audit-Tab"""
        tab = self.notebook.add("Audit-Log")
        
        # Filter
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Event-Type Filter
        ctk.CTkLabel(filter_frame, text="Event-Typ:").pack(side="left", padx=5)
        self.event_type_var = ctk.StringVar(value="Alle")
        event_types = ["Alle"] + [event.value for event in AuditEventType]
        event_combo = ctk.CTkComboBox(filter_frame, values=event_types, variable=self.event_type_var)
        event_combo.pack(side="left", padx=5)
        
        # Zeitraum
        ctk.CTkLabel(filter_frame, text="Letzte:").pack(side="left", padx=(20, 5))
        self.timeframe_var = ctk.StringVar(value="24 Stunden")
        timeframes = ["24 Stunden", "7 Tage", "30 Tage", "Alle"]
        timeframe_combo = ctk.CTkComboBox(filter_frame, values=timeframes, variable=self.timeframe_var)
        timeframe_combo.pack(side="left", padx=5)
        
        # Aktualisieren-Button
        refresh_btn = ctk.CTkButton(
            filter_frame,
            text="🔄 Aktualisieren",
            command=self.refresh_audit_log
        )
        refresh_btn.pack(side="left", padx=(20, 5))
        
        # Export-Button
        export_btn = ctk.CTkButton(
            filter_frame,
            text="📤 Export",
            command=self.export_audit_log
        )
        export_btn.pack(side="left", padx=5)
        
        # Audit-Liste
        audit_frame = ctk.CTkFrame(tab)
        audit_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview für Audit-Events
        audit_columns = ("timestamp", "event_type", "user", "description", "severity")
        self.audit_tree = ttk.Treeview(audit_frame, columns=audit_columns, show="headings", height=20)
        
        # Spalten konfigurieren
        self.audit_tree.heading("timestamp", text="Zeitstempel")
        self.audit_tree.heading("event_type", text="Event-Typ")
        self.audit_tree.heading("user", text="Benutzer")
        self.audit_tree.heading("description", text="Beschreibung")
        self.audit_tree.heading("severity", text="Kritikalität")
        
        self.audit_tree.column("timestamp", width=150)
        self.audit_tree.column("event_type", width=120)
        self.audit_tree.column("user", width=100)
        self.audit_tree.column("description", width=300)
        self.audit_tree.column("severity", width=100)
        
        # Scrollbar
        audit_scrollbar = ttk.Scrollbar(audit_frame, orient="vertical", command=self.audit_tree.yview)
        self.audit_tree.configure(yscrollcommand=audit_scrollbar.set)
        
        self.audit_tree.pack(side="left", fill="both", expand=True)
        audit_scrollbar.pack(side="right", fill="y")
        
        # Details-Bereich
        details_frame = ctk.CTkFrame(tab)
        details_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(details_frame, text="Event-Details:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.details_text = ctk.CTkTextbox(details_frame, height=80)
        self.details_text.pack(fill="x", padx=5, pady=5)
        
        # Event-Selection Binding
        self.audit_tree.bind("<<TreeviewSelect>>", self.on_audit_select)
    
    def create_statistics_tab(self):
        """Erstellt Statistik-Tab"""
        tab = self.notebook.add("Statistiken")
        
        # Aktualisieren-Button
        refresh_stats_btn = ctk.CTkButton(
            tab,
            text="🔄 Statistiken aktualisieren",
            command=self.refresh_statistics
        )
        refresh_stats_btn.pack(pady=10)
        
        # Statistik-Grid
        stats_frame = ctk.CTkFrame(tab)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Verschiedene Statistik-Bereiche
        self.create_stats_cards(stats_frame)
    
    def create_stats_cards(self, parent):
        """Erstellt Statistik-Karten"""
        # Grid für Karten
        cards_frame = ctk.CTkFrame(parent)
        cards_frame.pack(fill="x", padx=10, pady=10)
        
        # Row 1
        row1 = ctk.CTkFrame(cards_frame)
        row1.pack(fill="x", pady=5)
        
        self.create_stat_card(row1, "Aktive Sessions", "0", "🖥️")
        self.create_stat_card(row1, "Gesamt Benutzer", "0", "👥")
        self.create_stat_card(row1, "Gesperrte Benutzer", "0", "🔒")
        
        # Row 2
        row2 = ctk.CTkFrame(cards_frame)
        row2.pack(fill="x", pady=5)
        
        self.create_stat_card(row2, "Login-Fehler (24h)", "0", "❌")
        self.create_stat_card(row2, "Erfolg. Logins (24h)", "0", "✅")
        self.create_stat_card(row2, "Sicherheitsverletzungen", "0", "⚠️")
        
        # Charts-Bereich
        charts_frame = ctk.CTkFrame(parent)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(charts_frame, text="Aktivitäts-Timeline (Letzte 7 Tage)", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Hier könnte ein Chart-Widget eingefügt werden
        self.activity_chart = ctk.CTkTextbox(charts_frame, height=200)
        self.activity_chart.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_stat_card(self, parent, title: str, value: str, icon: str):
        """Erstellt eine Statistik-Karte"""
        card = ctk.CTkFrame(parent)
        card.pack(side="left", fill="x", expand=True, padx=5)
        
        icon_label = ctk.CTkLabel(card, text=icon, font=("Arial", 24))
        icon_label.pack(pady=(10, 0))
        
        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"))
        value_label.pack()
        
        title_label = ctk.CTkLabel(card, text=title, font=("Arial", 12))
        title_label.pack(pady=(0, 10))
        
        # Speichere Referenz für Updates
        if not hasattr(self, 'stat_labels'):
            self.stat_labels = {}
        self.stat_labels[title] = value_label
    
    def load_data(self):
        """Lädt alle Daten"""
        self.refresh_users()
        self.refresh_audit_log()
        self.refresh_statistics()
    
    def refresh_users(self):
        """Aktualisiert Benutzerliste"""
        # Alle Items löschen
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Benutzer hinzufügen
        for user in self.security_manager.users.values():
            status = "Aktiv"
            if user.is_locked:
                status = "Gesperrt"
            elif not user.is_active:
                status = "Inaktiv"
            
            last_login = ""
            if user.last_login:
                last_login = user.last_login.strftime("%d.%m.%Y %H:%M")
            
            self.users_tree.insert("", "end", values=(
                user.username,
                user.email,
                user.role.value,
                status,
                last_login,
                user.failed_login_attempts
            ), tags=(user.user_id,))
    
    def refresh_audit_log(self):
        """Aktualisiert Audit-Log"""
        # Filter anwenden
        event_type = None
        if self.event_type_var.get() != "Alle":
            event_type = AuditEventType(self.event_type_var.get())
        
        date_from = None
        timeframe = self.timeframe_var.get()
        if timeframe == "24 Stunden":
            date_from = datetime.now() - timedelta(hours=24)
        elif timeframe == "7 Tage":
            date_from = datetime.now() - timedelta(days=7)
        elif timeframe == "30 Tage":
            date_from = datetime.now() - timedelta(days=30)
        
        events = self.security_manager.get_audit_events(
            event_type=event_type,
            date_from=date_from,
            limit=500
        )
        
        # Alle Items löschen
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
        
        # Events hinzufügen
        for event in events:
            user_name = ""
            if event.user_id:
                user = self.security_manager.users.get(event.user_id)
                if user:
                    user_name = user.username
            
            # Farbe basierend auf Kritikalität
            tags = []
            if event.severity == SecurityLevel.HIGH:
                tags = ["high"]
            elif event.severity == SecurityLevel.CRITICAL:
                tags = ["critical"]
            
            self.audit_tree.insert("", "end", values=(
                event.timestamp.strftime("%d.%m.%Y %H:%M:%S"),
                event.event_type.value,
                user_name,
                event.description,
                event.severity.value
            ), tags=tags)
        
        # Tags konfigurieren
        self.audit_tree.tag_configure("high", background="#ffcccc")
        self.audit_tree.tag_configure("critical", background="#ff9999")
    
    def refresh_statistics(self):
        """Aktualisiert Statistiken"""
        stats = self.security_manager.get_security_statistics()
        
        # Stat-Cards aktualisieren
        if hasattr(self, 'stat_labels'):
            updates = {
                "Aktive Sessions": str(stats.get('active_sessions', 0)),
                "Gesamt Benutzer": str(stats.get('total_users', 0)),
                "Gesperrte Benutzer": str(stats.get('locked_users', 0)),
                "Login-Fehler (24h)": str(stats.get('failed_logins_24h', 0)),
                "Erfolg. Logins (24h)": str(stats.get('successful_logins_24h', 0)),
                "Sicherheitsverletzungen": str(stats.get('security_violations_24h', 0))
            }
            
            for title, value in updates.items():
                if title in self.stat_labels:
                    self.stat_labels[title].configure(text=value)
        
        # Activity Chart aktualisieren
        activity_text = f"""
Sicherheitsübersicht:
═══════════════════

🔒 Verschlüsselung: {'Aktiviert' if stats.get('encryption_enabled') else 'Deaktiviert'}
🔐 2FA-Nutzer: {stats.get('two_factor_enabled_users', 0)}
⚠️ Passwort läuft bald ab: {stats.get('password_expires_soon', 0)}
📊 Audit-Events gesamt: {stats.get('audit_events_total', 0)}

Letzte Aktivitäten:
• Aktive Sessions: {stats.get('active_sessions', 0)}
• Erfolgreiche Logins: {stats.get('successful_logins_24h', 0)}
• Fehlgeschlagene Logins: {stats.get('failed_logins_24h', 0)}
• Sicherheitsverletzungen: {stats.get('security_violations_24h', 0)}
        """
        
        self.activity_chart.delete("1.0", "end")
        self.activity_chart.insert("1.0", activity_text)
    
    def on_audit_select(self, event):
        """Audit-Event ausgewählt"""
        selection = self.audit_tree.selection()
        if not selection:
            return
        
        item = self.audit_tree.item(selection[0])
        timestamp_str = item['values'][0]
        
        # Event in der Liste finden
        for event in self.security_manager.audit_events:
            if event.timestamp.strftime("%d.%m.%Y %H:%M:%S") == timestamp_str:
                details = f"""Event-ID: {event.event_id}
IP-Adresse: {event.ip_address or 'Unbekannt'}
User-Agent: {event.user_agent or 'Unbekannt'}
Session-ID: {event.session_id or 'Keine'}

Details:
{event.details}"""
                
                self.details_text.delete("1.0", "end")
                self.details_text.insert("1.0", details)
                break
    
    def add_user(self):
        """Neuen Benutzer hinzufügen"""
        dialog = UserEditDialog(self.window, self.security_manager, None)
        if dialog.result:
            self.refresh_users()
    
    def edit_user(self):
        """Benutzer bearbeiten"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Benutzer aus.")
            return
        
        # User-ID aus Tags holen
        item = self.users_tree.item(selection[0])
        user_id = item['tags'][0]
        user = self.security_manager.users.get(user_id)
        
        if user:
            dialog = UserEditDialog(self.window, self.security_manager, user)
            if dialog.result:
                self.refresh_users()
    
    def delete_user(self):
        """Benutzer löschen"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Benutzer aus.")
            return
        
        if messagebox.askyesno("Bestätigung", "Benutzer wirklich löschen?"):
            # User-ID aus Tags holen
            item = self.users_tree.item(selection[0])
            user_id = item['tags'][0]
            
            if user_id in self.security_manager.users:
                user = self.security_manager.users[user_id]
                del self.security_manager.users[user_id]
                self.security_manager.save_users()
                
                # Audit-Event
                event = AuditEvent(
                    event_type=AuditEventType.USER_DELETED,
                    description=f"Benutzer '{user.username}' gelöscht",
                    details={'deleted_user_id': user_id}
                )
                self.security_manager.log_audit_event(event)
                
                self.refresh_users()
                messagebox.showinfo("Erfolg", "Benutzer wurde gelöscht.")
    
    def unlock_user(self):
        """Benutzer entsperren"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Benutzer aus.")
            return
        
        # User-ID aus Tags holen
        item = self.users_tree.item(selection[0])
        user_id = item['tags'][0]
        user = self.security_manager.users.get(user_id)
        
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0
            self.security_manager.save_users()
            
            # Audit-Event
            event = AuditEvent(
                event_type=AuditEventType.USER_MODIFIED,
                description=f"Benutzer '{user.username}' entsperrt",
                details={'user_id': user_id}
            )
            self.security_manager.log_audit_event(event)
            
            self.refresh_users()
            messagebox.showinfo("Erfolg", "Benutzer wurde entsperrt.")
    
    def reset_password(self):
        """Passwort zurücksetzen"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Benutzer aus.")
            return
        
        # User-ID aus Tags holen
        item = self.users_tree.item(selection[0])
        user_id = item['tags'][0]
        user = self.security_manager.users.get(user_id)
        
        if user:
            # Neues temporäres Passwort
            new_password = "TempPass123!"
            user.set_password(new_password)
            user.must_change_password = True
            self.security_manager.save_users()
            
            # Audit-Event
            event = AuditEvent(
                event_type=AuditEventType.PASSWORD_CHANGED,
                description=f"Passwort für '{user.username}' zurückgesetzt",
                details={'user_id': user_id, 'reset_by_admin': True}
            )
            self.security_manager.log_audit_event(event)
            
            messagebox.showinfo("Erfolg", f"Neues temporäres Passwort: {new_password}\nBenutzer muss beim nächsten Login das Passwort ändern.")
    
    def save_security_settings(self):
        """Speichert Sicherheitseinstellungen"""
        try:
            # Validierung
            min_length = int(self.min_length_var.get())
            if min_length < 4:
                messagebox.showerror("Fehler", "Mindestlänge muss mindestens 4 sein.")
                return
            
            password_age = int(self.password_age_var.get())
            if password_age < 1:
                messagebox.showerror("Fehler", "Passwort-Alter muss mindestens 1 Tag sein.")
                return
            
            max_attempts = int(self.max_attempts_var.get())
            if max_attempts < 1:
                messagebox.showerror("Fehler", "Max. Fehlversuche muss mindestens 1 sein.")
                return
            
            # Einstellungen aktualisieren
            self.security_manager.settings.update({
                'password_min_length': min_length,
                'password_require_uppercase': self.require_uppercase_var.get(),
                'password_require_lowercase': self.require_lowercase_var.get(),
                'password_require_numbers': self.require_numbers_var.get(),
                'password_require_special': self.require_special_var.get(),
                'password_max_age_days': password_age,
                'max_failed_login_attempts': max_attempts,
                'account_lockout_duration_minutes': int(self.lockout_duration_var.get()),
                'session_timeout_minutes': int(self.session_timeout_var.get()),
                'data_encryption_enabled': self.data_encryption_var.get(),
                'backup_encryption_enabled': self.backup_encryption_var.get()
            })
            
            messagebox.showinfo("Erfolg", "Sicherheitseinstellungen wurden gespeichert.")
            
        except ValueError as e:
            messagebox.showerror("Fehler", "Ungültige Eingabe. Bitte prüfen Sie die numerischen Werte.")
    
    def export_audit_log(self):
        """Exportiert Audit-Log"""
        from tkinter import filedialog
        import csv
        
        filename = filedialog.asksaveasfilename(
            title="Audit-Log exportieren",
            defaultextension=".csv",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )
        
        if filename:
            try:
                events = self.security_manager.get_audit_events(limit=10000)
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Zeitstempel', 'Event-Typ', 'Benutzer-ID', 'Beschreibung', 'Details', 'IP-Adresse', 'Kritikalität'])
                    
                    for event in events:
                        writer.writerow([
                            event.timestamp.isoformat(),
                            event.event_type.value,
                            event.user_id,
                            event.description,
                            str(event.details),
                            event.ip_address,
                            event.severity.value
                        ])
                
                messagebox.showinfo("Erfolg", f"Audit-Log wurde nach {filename} exportiert.")
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Export: {str(e)}")


class UserEditDialog:
    """Dialog zum Bearbeiten von Benutzern"""
    
    def __init__(self, parent, security_manager: SecurityManager, user: Optional[User] = None):
        self.security_manager = security_manager
        self.user = user
        self.result = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Benutzer bearbeiten" if user else "Neuer Benutzer")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentrieren
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        
        self.setup_ui()
        if user:
            self.load_user_data()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Scroll-Frame
        scroll_frame = ctk.CTkScrollableFrame(self.dialog)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grunddaten
        basic_frame = ctk.CTkFrame(scroll_frame)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(basic_frame, text="Grunddaten", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Benutzername
        username_frame = ctk.CTkFrame(basic_frame)
        username_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(username_frame, text="Benutzername:", width=120).pack(side="left", padx=5)
        self.username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(username_frame, textvariable=self.username_var)
        username_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # E-Mail
        email_frame = ctk.CTkFrame(basic_frame)
        email_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(email_frame, text="E-Mail:", width=120).pack(side="left", padx=5)
        self.email_var = ctk.StringVar()
        email_entry = ctk.CTkEntry(email_frame, textvariable=self.email_var)
        email_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Rolle
        role_frame = ctk.CTkFrame(basic_frame)
        role_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(role_frame, text="Rolle:", width=120).pack(side="left", padx=5)
        self.role_var = ctk.StringVar(value=UserRole.USER.value)
        role_combo = ctk.CTkComboBox(role_frame, values=[role.value for role in UserRole], variable=self.role_var)
        role_combo.pack(side="left", fill="x", expand=True, padx=5)
        
        # Passwort (nur bei neuem Benutzer)
        if not self.user:
            password_frame = ctk.CTkFrame(basic_frame)
            password_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(password_frame, text="Passwort:", width=120).pack(side="left", padx=5)
            self.password_var = ctk.StringVar()
            password_entry = ctk.CTkEntry(password_frame, textvariable=self.password_var, show="*")
            password_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Status
        status_frame = ctk.CTkFrame(scroll_frame)
        status_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(status_frame, text="Status", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.is_active_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(status_frame, text="Konto aktiv", variable=self.is_active_var).pack(anchor="w", padx=10, pady=2)
        
        self.must_change_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(status_frame, text="Muss Passwort ändern", variable=self.must_change_password_var).pack(anchor="w", padx=10, pady=2)
        
        # Session-Timeout
        timeout_frame = ctk.CTkFrame(status_frame)
        timeout_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(timeout_frame, text="Session-Timeout (Min):", width=150).pack(side="left", padx=5)
        self.session_timeout_var = ctk.StringVar(value="30")
        timeout_entry = ctk.CTkEntry(timeout_frame, textvariable=self.session_timeout_var, width=100)
        timeout_entry.pack(side="left", padx=5)
        
        # Notizen
        notes_frame = ctk.CTkFrame(scroll_frame)
        notes_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(notes_frame, text="Notizen", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.notes_text = ctk.CTkTextbox(notes_frame, height=100)
        self.notes_text.pack(fill="x", padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(scroll_frame)
        button_frame.pack(fill="x", pady=10)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Speichern",
            command=self.save_user
        )
        save_btn.pack(side="left", padx=(10, 5))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Abbrechen",
            command=self.dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)
    
    def load_user_data(self):
        """Lädt Benutzerdaten"""
        if self.user:
            self.username_var.set(self.user.username)
            self.email_var.set(self.user.email)
            self.role_var.set(self.user.role.value)
            self.is_active_var.set(self.user.is_active)
            self.must_change_password_var.set(self.user.must_change_password)
            self.session_timeout_var.set(str(self.user.session_timeout_minutes))
            self.notes_text.insert("1.0", self.user.notes)
    
    def save_user(self):
        """Speichert Benutzer"""
        try:
            username = self.username_var.get().strip()
            email = self.email_var.get().strip()
            role = UserRole(self.role_var.get())
            
            if not username or not email:
                messagebox.showerror("Fehler", "Benutzername und E-Mail sind erforderlich.")
                return
            
            # Prüfen ob Benutzername/E-Mail bereits existiert (außer bei aktueller Bearbeitung)
            for user_id, user in self.security_manager.users.items():
                if self.user and user_id == self.user.user_id:
                    continue
                if user.username.lower() == username.lower():
                    messagebox.showerror("Fehler", "Benutzername bereits vergeben.")
                    return
                if user.email.lower() == email.lower():
                    messagebox.showerror("Fehler", "E-Mail-Adresse bereits vergeben.")
                    return
            
            if self.user:
                # Bestehenden Benutzer aktualisieren
                self.user.username = username
                self.user.email = email
                self.user.role = role
                self.user.is_active = self.is_active_var.get()
                self.user.must_change_password = self.must_change_password_var.get()
                self.user.session_timeout_minutes = int(self.session_timeout_var.get())
                self.user.notes = self.notes_text.get("1.0", "end-1c")
                self.user.updated_at = datetime.now()
                
                event_type = AuditEventType.USER_MODIFIED
                description = f"Benutzer '{username}' bearbeitet"
                
            else:
                # Neuen Benutzer erstellen
                password = self.password_var.get()
                if not password:
                    messagebox.showerror("Fehler", "Passwort ist erforderlich.")
                    return
                
                # Passwort validieren
                is_valid, message = self.security_manager.validate_password(password)
                if not is_valid:
                    messagebox.showerror("Fehler", message)
                    return
                
                user = User(username=username, email=email, role=role)
                user.set_password(password)
                user.is_active = self.is_active_var.get()
                user.must_change_password = self.must_change_password_var.get()
                user.session_timeout_minutes = int(self.session_timeout_var.get())
                user.notes = self.notes_text.get("1.0", "end-1c")
                
                self.security_manager.users[user.user_id] = user
                
                event_type = AuditEventType.USER_CREATED
                description = f"Benutzer '{username}' erstellt"
            
            # Speichern
            self.security_manager.save_users()
            
            # Audit-Event
            event = AuditEvent(
                event_type=event_type,
                description=description,
                details={'username': username, 'role': role.value}
            )
            self.security_manager.log_audit_event(event)
            
            self.result = True
            self.dialog.destroy()
            messagebox.showinfo("Erfolg", "Benutzer wurde gespeichert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
