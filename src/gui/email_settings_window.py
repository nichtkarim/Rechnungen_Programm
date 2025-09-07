"""
GUI für E-Mail Einstellungen und Management
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading

from src.utils.email_manager import EmailManager, EmailTemplate
from src.utils.theme_manager import theme_manager


class EmailSettingsWindow:
    """Fenster für E-Mail Einstellungen"""
    
    def __init__(self, parent, email_manager: EmailManager):
        self.parent = parent
        self.email_manager = email_manager
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("📧 E-Mail Einstellungen")
        self.window.geometry("800x700")
        self.window.transient(parent)
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # Layout erstellen
        self.create_layout()
        self.load_settings()
    
    def create_layout(self):
        """Erstellt das Layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(main_frame, text="📧 E-Mail Konfiguration", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # SMTP-Einstellungen Tab
        self.smtp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.smtp_frame, text="SMTP-Server")
        self.create_smtp_tab()
        
        # Vorlagen Tab
        self.templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.templates_frame, text="E-Mail Vorlagen")
        self.create_templates_tab()
        
        # Automatisierung Tab
        self.automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.automation_frame, text="Automatisierung")
        self.create_automation_tab()
        
        # Historie Tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Versand-Historie")
        self.create_history_tab()
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        test_btn = ctk.CTkButton(button_frame, text="🔧 Verbindung testen", 
                               command=self.test_connection)
        test_btn.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Speichern", 
                               command=self.save_settings)
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Abbrechen", 
                                 command=self.window.destroy)
        cancel_btn.pack(side="right", padx=5)
    
    def create_smtp_tab(self):
        """Erstellt SMTP-Einstellungen Tab"""
        # Scrollable Frame
        scroll_frame = ctk.CTkScrollableFrame(self.smtp_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # SMTP-Server
        ctk.CTkLabel(scroll_frame, text="SMTP-Server:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.smtp_server_entry = ctk.CTkEntry(scroll_frame, width=400)
        self.smtp_server_entry.pack(fill="x", pady=(0, 10))
        
        # Port und TLS
        port_frame = ctk.CTkFrame(scroll_frame)
        port_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(port_frame, text="Port:").pack(side="left", padx=(0, 5))
        self.smtp_port_entry = ctk.CTkEntry(port_frame, width=100)
        self.smtp_port_entry.pack(side="left", padx=(0, 20))
        
        self.use_tls_var = ctk.BooleanVar(value=True)
        tls_cb = ctk.CTkCheckBox(port_frame, text="TLS verwenden", variable=self.use_tls_var)
        tls_cb.pack(side="left")
        
        # Benutzerdaten
        ctk.CTkLabel(scroll_frame, text="E-Mail-Adresse:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.username_entry = ctk.CTkEntry(scroll_frame, width=400)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(scroll_frame, text="Passwort:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.password_entry = ctk.CTkEntry(scroll_frame, width=400, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))
        
        # Absender-Daten
        ctk.CTkLabel(scroll_frame, text="Absender-Name:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.sender_name_entry = ctk.CTkEntry(scroll_frame, width=400)
        self.sender_name_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(scroll_frame, text="Absender E-Mail:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.sender_email_entry = ctk.CTkEntry(scroll_frame, width=400)
        self.sender_email_entry.pack(fill="x", pady=(0, 10))
        
        # Signatur
        ctk.CTkLabel(scroll_frame, text="E-Mail Signatur:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.signature_text = ctk.CTkTextbox(scroll_frame, height=100)
        self.signature_text.pack(fill="x", pady=(0, 10))
        
        # Häufige Provider
        provider_frame = ctk.CTkFrame(scroll_frame)
        provider_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(provider_frame, text="Schnellkonfiguration:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        providers = {
            "Gmail": {"server": "smtp.gmail.com", "port": 587, "tls": True},
            "Outlook": {"server": "smtp-mail.outlook.com", "port": 587, "tls": True},
            "GMX": {"server": "mail.gmx.net", "port": 587, "tls": True},
            "Web.de": {"server": "smtp.web.de", "port": 587, "tls": True},
            "T-Online": {"server": "securesmtp.t-online.de", "port": 587, "tls": True}
        }
        
        provider_buttons_frame = ctk.CTkFrame(provider_frame)
        provider_buttons_frame.pack(fill="x", pady=5)
        
        for name, config in providers.items():
            btn = ctk.CTkButton(provider_buttons_frame, text=name, width=80,
                              command=lambda c=config: self.apply_provider_config(c))
            btn.pack(side="left", padx=2, pady=2)
    
    def create_templates_tab(self):
        """Erstellt Vorlagen Tab"""
        # Template-Liste
        list_frame = ctk.CTkFrame(self.templates_frame)
        list_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        
        ctk.CTkLabel(list_frame, text="Vorlagen:", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        
        # Listbox für Templates
        self.templates_listbox = tk.Listbox(list_frame, width=25, height=15)
        self.templates_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.templates_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        # Template Buttons
        template_btn_frame = ctk.CTkFrame(list_frame)
        template_btn_frame.pack(fill="x", padx=10, pady=5)
        
        new_template_btn = ctk.CTkButton(template_btn_frame, text="➕ Neu", 
                                       command=self.new_template)
        new_template_btn.pack(fill="x", pady=2)
        
        delete_template_btn = ctk.CTkButton(template_btn_frame, text="🗑️ Löschen", 
                                          command=self.delete_template)
        delete_template_btn.pack(fill="x", pady=2)
        
        # Template Editor
        editor_frame = ctk.CTkFrame(self.templates_frame)
        editor_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(editor_frame, text="Template Editor:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        
        # Template Name
        name_frame = ctk.CTkFrame(editor_frame)
        name_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(name_frame, text="Name:").pack(side="left", padx=(0, 5))
        self.template_name_entry = ctk.CTkEntry(name_frame)
        self.template_name_entry.pack(side="left", fill="x", expand=True)
        
        # Template Type
        type_frame = ctk.CTkFrame(editor_frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(type_frame, text="Typ:").pack(side="left", padx=(0, 5))
        self.template_type_var = ctk.StringVar(value="invoice")
        type_menu = ctk.CTkOptionMenu(type_frame, variable=self.template_type_var,
                                    values=["invoice", "reminder", "quote", "general"])
        type_menu.pack(side="left")
        
        # Subject
        ctk.CTkLabel(editor_frame, text="Betreff:").pack(anchor="w", padx=10, pady=(10, 5))
        self.template_subject_entry = ctk.CTkEntry(editor_frame)
        self.template_subject_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Body
        ctk.CTkLabel(editor_frame, text="Nachricht:").pack(anchor="w", padx=10, pady=(10, 5))
        self.template_body_text = ctk.CTkTextbox(editor_frame, height=300)
        self.template_body_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Template Variables Info
        vars_info = ctk.CTkLabel(editor_frame, 
                               text="Verfügbare Variablen: {invoice_number}, {invoice_date}, {due_date}, {total_amount}, {customer_name}, {company_name}, {sender_name}, {signature}",
                               wraplength=400, font=ctk.CTkFont(size=10))
        vars_info.pack(padx=10, pady=5)
        
        # Save Template Button
        save_template_btn = ctk.CTkButton(editor_frame, text="💾 Template speichern", 
                                        command=self.save_template)
        save_template_btn.pack(pady=10)
    
    def create_automation_tab(self):
        """Erstellt Automatisierung Tab"""
        auto_frame = ctk.CTkFrame(self.automation_frame)
        auto_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Auto-Send Invoices
        self.auto_send_var = ctk.BooleanVar()
        auto_send_cb = ctk.CTkCheckBox(auto_frame, text="Rechnungen automatisch per E-Mail versenden", 
                                     variable=self.auto_send_var)
        auto_send_cb.pack(anchor="w", pady=10)
        
        # Reminders
        self.send_reminders_var = ctk.BooleanVar()
        reminders_cb = ctk.CTkCheckBox(auto_frame, text="Automatische Mahnungen aktivieren", 
                                     variable=self.send_reminders_var)
        reminders_cb.pack(anchor="w", pady=10)
        
        # Reminder Days
        reminder_frame = ctk.CTkFrame(auto_frame)
        reminder_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(reminder_frame, text="Mahnung senden nach (Tage):", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        days_frame = ctk.CTkFrame(reminder_frame)
        days_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(days_frame, text="1. Mahnung:").pack(side="left", padx=(0, 5))
        self.reminder_1_entry = ctk.CTkEntry(days_frame, width=60)
        self.reminder_1_entry.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(days_frame, text="2. Mahnung:").pack(side="left", padx=(0, 5))
        self.reminder_2_entry = ctk.CTkEntry(days_frame, width=60)
        self.reminder_2_entry.pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(days_frame, text="3. Mahnung:").pack(side="left", padx=(0, 5))
        self.reminder_3_entry = ctk.CTkEntry(days_frame, width=60)
        self.reminder_3_entry.pack(side="left")
        
        # Manual Reminder Check
        manual_frame = ctk.CTkFrame(auto_frame)
        manual_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(manual_frame, text="Manuelle Mahnungen:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        check_reminders_btn = ctk.CTkButton(manual_frame, text="🔍 Fällige Mahnungen prüfen", 
                                          command=self.check_pending_reminders)
        check_reminders_btn.pack(side="left", padx=5)
        
        send_reminders_btn = ctk.CTkButton(manual_frame, text="📧 Alle Mahnungen senden", 
                                         command=self.send_all_reminders)
        send_reminders_btn.pack(side="left", padx=5)
        
        # Statistics
        stats_frame = ctk.CTkFrame(auto_frame)
        stats_frame.pack(fill="both", expand=True, pady=20)
        
        ctk.CTkLabel(stats_frame, text="E-Mail Statistiken:", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        
        self.stats_text = ctk.CTkTextbox(stats_frame, height=150)
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        refresh_stats_btn = ctk.CTkButton(stats_frame, text="🔄 Statistiken aktualisieren", 
                                        command=self.refresh_statistics)
        refresh_stats_btn.pack(pady=5)
    
    def create_history_tab(self):
        """Erstellt Historie Tab"""
        history_frame = ctk.CTkFrame(self.history_frame)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filter
        filter_frame = ctk.CTkFrame(history_frame)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=(10, 5))
        
        self.history_filter_var = ctk.StringVar(value="Alle")
        filter_menu = ctk.CTkOptionMenu(filter_frame, variable=self.history_filter_var,
                                      values=["Alle", "Rechnungen", "Mahnungen", "Angebote"],
                                      command=self.filter_history)
        filter_menu.pack(side="left", padx=5)
        
        # History Tree
        self.history_tree = ttk.Treeview(history_frame, 
                                       columns=("datum", "typ", "empfaenger", "betreff", "status"), 
                                       show="headings")
        
        self.history_tree.heading("datum", text="Datum")
        self.history_tree.heading("typ", text="Typ")
        self.history_tree.heading("empfaenger", text="Empfänger")
        self.history_tree.heading("betreff", text="Betreff")
        self.history_tree.heading("status", text="Status")
        
        self.history_tree.column("datum", width=120)
        self.history_tree.column("typ", width=100)
        self.history_tree.column("empfaenger", width=200)
        self.history_tree.column("betreff", width=300)
        self.history_tree.column("status", width=80)
        
        self.history_tree.pack(fill="both", expand=True)
        
        # Scrollbar
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", 
                                        command=self.history_tree.yview)
        history_scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
    
    def apply_provider_config(self, config: Dict[str, Any]):
        """Wendet Provider-Konfiguration an"""
        self.smtp_server_entry.delete(0, 'end')
        self.smtp_server_entry.insert(0, config['server'])
        
        self.smtp_port_entry.delete(0, 'end')
        self.smtp_port_entry.insert(0, str(config['port']))
        
        self.use_tls_var.set(config['tls'])
    
    def load_settings(self):
        """Lädt aktuelle Einstellungen"""
        config = self.email_manager.config
        
        # SMTP Settings
        self.smtp_server_entry.insert(0, config.smtp_server)
        self.smtp_port_entry.insert(0, str(config.smtp_port))
        self.use_tls_var.set(config.use_tls)
        self.username_entry.insert(0, config.username)
        self.password_entry.insert(0, config.password)
        self.sender_name_entry.insert(0, config.sender_name)
        self.sender_email_entry.insert(0, config.sender_email)
        self.signature_text.insert("1.0", config.signature)
        
        # Automation Settings
        self.auto_send_var.set(config.auto_send_invoices)
        self.send_reminders_var.set(config.send_reminders)
        
        if len(config.reminder_days) >= 3:
            self.reminder_1_entry.insert(0, str(config.reminder_days[0]))
            self.reminder_2_entry.insert(0, str(config.reminder_days[1]))
            self.reminder_3_entry.insert(0, str(config.reminder_days[2]))
        
        # Templates laden
        self.load_templates()
        
        # Historie laden
        self.load_history()
        
        # Statistiken laden
        self.refresh_statistics()
    
    def load_templates(self):
        """Lädt Template-Liste"""
        self.templates_listbox.delete(0, 'end')
        for name in self.email_manager.templates.keys():
            self.templates_listbox.insert('end', name)
    
    def load_history(self):
        """Lädt E-Mail Historie"""
        # Historie Tree leeren
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Historie laden
        for entry in reversed(self.email_manager.email_history[-100:]):  # Letzte 100
            datum = entry.get('sent_at', '').strftime('%d.%m.%Y %H:%M') if isinstance(entry.get('sent_at'), datetime) else str(entry.get('sent_at', ''))
            typ = entry.get('type', '')
            empfaenger = entry.get('recipient', '')
            betreff = entry.get('subject', '')
            status = "✅ Erfolgreich" if entry.get('success', False) else "❌ Fehler"
            
            self.history_tree.insert('', 'end', values=(datum, typ, empfaenger, betreff, status))
    
    def on_template_select(self, event):
        """Template auswählen"""
        selection = self.templates_listbox.curselection()
        if selection:
            template_name = self.templates_listbox.get(selection[0])
            template = self.email_manager.templates.get(template_name)
            
            if template:
                self.template_name_entry.delete(0, 'end')
                self.template_name_entry.insert(0, template.name)
                
                self.template_type_var.set(template.template_type)
                
                self.template_subject_entry.delete(0, 'end')
                self.template_subject_entry.insert(0, template.subject)
                
                self.template_body_text.delete("1.0", 'end')
                self.template_body_text.insert("1.0", template.body)
    
    def new_template(self):
        """Neues Template erstellen"""
        self.template_name_entry.delete(0, 'end')
        self.template_subject_entry.delete(0, 'end')
        self.template_body_text.delete("1.0", 'end')
        self.template_type_var.set("invoice")
    
    def save_template(self):
        """Template speichern"""
        try:
            name = self.template_name_entry.get().strip()
            if not name:
                messagebox.showerror("Fehler", "Template-Name ist erforderlich")
                return
            
            subject = self.template_subject_entry.get()
            body = self.template_body_text.get("1.0", 'end-1c')
            template_type = self.template_type_var.get()
            
            # Template erstellen
            template = EmailTemplate(name, subject, body, template_type)
            self.email_manager.templates[name] = template
            self.email_manager.save_templates()
            
            # Liste aktualisieren
            self.load_templates()
            
            messagebox.showinfo("Erfolg", f"Template '{name}' gespeichert")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def delete_template(self):
        """Template löschen"""
        selection = self.templates_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte Template auswählen")
            return
        
        template_name = self.templates_listbox.get(selection[0])
        
        if messagebox.askyesno("Bestätigung", f"Template '{template_name}' wirklich löschen?"):
            del self.email_manager.templates[template_name]
            self.email_manager.save_templates()
            self.load_templates()
            self.new_template()  # Editor leeren
    
    def test_connection(self):
        """Testet E-Mail Verbindung"""
        # Zuerst Einstellungen speichern
        self.save_settings_to_config()
        
        def test_in_thread():
            success, message = self.email_manager.test_connection()
            self.window.after(0, lambda: self.show_test_result(success, message))
        
        # Test in separatem Thread
        thread = threading.Thread(target=test_in_thread)
        thread.daemon = True
        thread.start()
        
        messagebox.showinfo("Test", "Verbindungstest läuft...")
    
    def show_test_result(self, success: bool, message: str):
        """Zeigt Testergebnis"""
        if success:
            messagebox.showinfo("Test erfolgreich", message)
        else:
            messagebox.showerror("Test fehlgeschlagen", message)
    
    def save_settings_to_config(self):
        """Speichert Einstellungen in Config"""
        config = self.email_manager.config
        
        config.smtp_server = self.smtp_server_entry.get()
        config.smtp_port = int(self.smtp_port_entry.get() or 587)
        config.use_tls = self.use_tls_var.get()
        config.username = self.username_entry.get()
        config.password = self.password_entry.get()
        config.sender_name = self.sender_name_entry.get()
        config.sender_email = self.sender_email_entry.get()
        config.signature = self.signature_text.get("1.0", 'end-1c')
        
        config.auto_send_invoices = self.auto_send_var.get()
        config.send_reminders = self.send_reminders_var.get()
        
        # Reminder Days
        try:
            config.reminder_days = [
                int(self.reminder_1_entry.get() or 7),
                int(self.reminder_2_entry.get() or 14),
                int(self.reminder_3_entry.get() or 30)
            ]
        except ValueError:
            config.reminder_days = [7, 14, 30]
    
    def save_settings(self):
        """Speichert alle Einstellungen"""
        try:
            self.save_settings_to_config()
            self.email_manager.save_config()
            messagebox.showinfo("Erfolg", "Einstellungen gespeichert")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def check_pending_reminders(self):
        """Prüft fällige Mahnungen"""
        try:
            pending = self.email_manager.get_pending_reminders()
            
            if not pending:
                messagebox.showinfo("Mahnungen", "Keine fälligen Mahnungen gefunden")
                return
            
            message = f"Fällige Mahnungen: {len(pending)}\n\n"
            for reminder in pending[:10]:  # Maximal 10 anzeigen
                message += f"• Rechnung {reminder['invoice'].invoice_number} ({reminder['days_overdue']} Tage überfällig)\n"
            
            if len(pending) > 10:
                message += f"\n... und {len(pending) - 10} weitere"
            
            messagebox.showinfo("Fällige Mahnungen", message)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Prüfen der Mahnungen: {str(e)}")
    
    def send_all_reminders(self):
        """Sendet alle fälligen Mahnungen"""
        if not messagebox.askyesno("Bestätigung", "Alle fälligen Mahnungen jetzt senden?"):
            return
        
        def send_in_thread():
            try:
                sent_count, errors = self.email_manager.send_automatic_reminders()
                
                result_message = f"Mahnungen gesendet: {sent_count}"
                if errors:
                    result_message += f"\nFehler: {len(errors)}\n\n" + "\n".join(errors[:5])
                
                self.window.after(0, lambda: messagebox.showinfo("Mahnungen gesendet", result_message))
                self.window.after(0, self.load_history)
                
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Fehler", f"Fehler beim Senden: {str(e)}"))
        
        thread = threading.Thread(target=send_in_thread)
        thread.daemon = True
        thread.start()
        
        messagebox.showinfo("Senden", "Mahnungen werden im Hintergrund gesendet...")
    
    def refresh_statistics(self):
        """Aktualisiert E-Mail Statistiken"""
        try:
            stats = self.email_manager.get_email_statistics()
            
            stats_text = f"""E-Mail Statistiken:

Gesamt gesendet: {stats.get('total_emails', 0)}
Erfolgreich: {stats.get('successful_emails', 0)}
Erfolgsrate: {stats.get('success_rate', 0):.1f}%

Letzte 30 Tage: {stats.get('last_30_days', 0)}
Fällige Mahnungen: {stats.get('pending_reminders', 0)}

Nach Typ:"""
            
            for email_type, count in stats.get('by_type', {}).items():
                stats_text += f"\n  {email_type}: {count}"
            
            self.stats_text.delete("1.0", 'end')
            self.stats_text.insert("1.0", stats_text)
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Statistiken: {e}")
    
    def filter_history(self, filter_type):
        """Filtert E-Mail Historie"""
        self.load_history()  # Erstmal alle laden, dann filtern implementieren


class EmailSendDialog:
    """Dialog zum Senden einer E-Mail"""
    
    def __init__(self, parent, email_manager: EmailManager, invoice=None, pdf_path: Optional[str] = None):
        self.parent = parent
        self.email_manager = email_manager
        self.invoice = invoice
        self.pdf_path = pdf_path
        self.result = None
        
        # Dialog erstellen
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("📧 E-Mail senden")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_layout()
        if invoice:
            self.load_invoice_data()
    
    def create_layout(self):
        """Erstellt Dialog Layout"""
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(main_frame, text="📧 E-Mail Versand", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(10, 20))
        
        # Empfänger
        ctk.CTkLabel(main_frame, text="Empfänger:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10)
        self.recipient_entry = ctk.CTkEntry(main_frame, width=500)
        self.recipient_entry.pack(fill="x", padx=10, pady=(5, 10))
        
        # Template
        template_frame = ctk.CTkFrame(main_frame)
        template_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(template_frame, text="Vorlage:").pack(side="left", padx=(10, 5))
        
        template_names = list(self.email_manager.templates.keys())
        self.template_var = ctk.StringVar(value=template_names[0] if template_names else "")
        template_menu = ctk.CTkOptionMenu(template_frame, variable=self.template_var,
                                        values=template_names,
                                        command=self.on_template_change)
        template_menu.pack(side="left", padx=5)
        
        # Betreff
        ctk.CTkLabel(main_frame, text="Betreff:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.subject_entry = ctk.CTkEntry(main_frame, width=500)
        self.subject_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Nachricht
        ctk.CTkLabel(main_frame, text="Nachricht:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.message_text = ctk.CTkTextbox(main_frame, height=200)
        self.message_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Anhang Info
        if self.pdf_path:
            attach_label = ctk.CTkLabel(main_frame, text=f"📎 Anhang: {self.pdf_path.split('/')[-1]}")
            attach_label.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        send_btn = ctk.CTkButton(button_frame, text="📧 Senden", command=self.send_email)
        send_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Abbrechen", command=self.dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        preview_btn = ctk.CTkButton(button_frame, text="👁️ Vorschau", command=self.preview_email)
        preview_btn.pack(side="left", padx=5)
    
    def load_invoice_data(self):
        """Lädt Rechnungsdaten"""
        if self.invoice and self.invoice.customer and hasattr(self.invoice.customer, 'email'):
            self.recipient_entry.insert(0, self.invoice.customer.email)
        
        # Standard-Template für Rechnungen wählen
        if "rechnung_standard" in self.email_manager.templates:
            self.template_var.set("rechnung_standard")
            self.on_template_change("rechnung_standard")
    
    def on_template_change(self, template_name):
        """Template wurde geändert"""
        if template_name in self.email_manager.templates:
            template = self.email_manager.templates[template_name]
            
            # Subject und Body mit Platzhaltern setzen
            self.subject_entry.delete(0, 'end')
            self.subject_entry.insert(0, template.subject)
            
            self.message_text.delete("1.0", 'end')
            self.message_text.insert("1.0", template.body)
    
    def preview_email(self):
        """Zeigt E-Mail Vorschau"""
        try:
            # Hier könnte man die Template-Variablen rendern
            subject = self.subject_entry.get()
            body = self.message_text.get("1.0", 'end-1c')
            
            preview_window = ctk.CTkToplevel(self.dialog)
            preview_window.title("👁️ E-Mail Vorschau")
            preview_window.geometry("500x400")
            
            preview_text = ctk.CTkTextbox(preview_window)
            preview_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            preview_content = f"Betreff: {subject}\n\n{body}"
            preview_text.insert("1.0", preview_content)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei Vorschau: {str(e)}")
    
    def send_email(self):
        """Sendet die E-Mail"""
        try:
            recipient = self.recipient_entry.get().strip()
            if not recipient:
                messagebox.showerror("Fehler", "Empfänger ist erforderlich")
                return
            
            # E-Mail senden
            if self.invoice:
                success, message = self.email_manager.send_invoice_email(
                    self.invoice, 
                    self.pdf_path, 
                    self.template_var.get(),
                    recipient
                )
            else:
                # Direkte E-Mail senden
                subject = self.subject_entry.get()
                body = self.message_text.get("1.0", 'end-1c')
                
                success, message = self.email_manager._send_email(
                    recipient, recipient, subject, body,
                    [self.pdf_path] if self.pdf_path else []
                )
            
            if success:
                messagebox.showinfo("Erfolg", "E-Mail erfolgreich gesendet!")
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Fehler", f"E-Mail konnte nicht gesendet werden:\n{message}")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Senden: {str(e)}")
