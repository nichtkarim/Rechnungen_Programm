"""
Hauptfenster der Rechnungs-Anwendung
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from src.models import DocumentType, Invoice, Customer, CompanyData
from src.utils.data_manager import DataManager
from src.utils.pdf_generator import InvoicePDFGenerator

# GUI-Module importieren
from src.gui.invoice_edit_window import InvoiceEditWindow
from src.gui.customer_edit_window import CustomerEditWindow
from src.gui.company_settings_window import CompanySettingsWindow
from src.gui.app_settings_window import AppSettingsWindow
from src.gui.email_settings_window import EmailSettingsWindow
from src.gui.security_window import SecuritySettingsWindow
from src.gui.compliance_window import ComplianceWindow
from src.gui.dashboard_window import DashboardWindow

# Erweiterte Manager
from src.utils.security_manager import SecurityManager
from src.utils.compliance_manager import ComplianceManager
from src.utils.email_manager import EmailManager
from src.utils.import_export_manager import DataExporter, DataImporter
from src.utils.theme_manager import theme_manager


class MainWindow:
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        # Manager initialisieren
        self.data_manager = DataManager()
        self.security_manager = SecurityManager()
        self.compliance_manager = ComplianceManager()
        self.email_manager = EmailManager(self.data_manager)
        self.data_exporter = DataExporter(self.data_manager)
        self.data_importer = DataImporter(self.data_manager)
        
        # Theme-Manager initialisieren
        theme_manager.set_data_manager(self.data_manager)
        
        # Dashboard-Fenster Referenz
        self.dashboard_window = None
        
        # Hauptfenster erstellen
        self.root = ctk.CTk()
        self.root.title("Rechnungs-Tool - Enterprise Edition")
        
        # Fenstereinstellungen
        settings = self.data_manager.get_settings()
        self.root.geometry(f"{settings.window_width}x{settings.window_height}")
        
        # Theme über Theme-Manager setzen
        theme_manager.apply_theme("dark", "blue")  # Erzwinge dark theme
        theme_manager.setup_window_theme(self.root)
        
        # GUI erstellen
        self.setup_gui()
        
        # Daten laden
        self.refresh_all_lists()
        
        # Event-Handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Erstellt die GUI-Elemente"""
        
        # Hauptlayout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Menüleiste
        self.create_menubar()
        
        # Toolbar
        self.create_toolbar()
        
        # Hauptbereich mit Tabs
        self.create_main_area()
        
        # Statusbar
        self.create_statusbar()
    
    def create_menubar(self):
        """Erstellt die Menüleiste"""
        # Menüleiste
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Datei Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="📁 Backup erstellen", command=self.create_backup)
        file_menu.add_command(label="📂 Backup wiederherstellen", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="📤 Daten exportieren", command=self.export_all_data)
        file_menu.add_command(label="📥 Daten importieren", command=self.import_all_data)
        file_menu.add_separator()
        # Erweiterte Import/Export-Untermenü
        import_export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="📊 Erweiterte Im-/Exporte", menu=import_export_menu)
        import_export_menu.add_command(label="📄 Kunden → CSV", command=lambda: self.advanced_export("customers", "csv"))
        import_export_menu.add_command(label="📊 Kunden → Excel", command=lambda: self.advanced_export("customers", "excel"))
        import_export_menu.add_command(label="📋 Kunden → XML", command=lambda: self.advanced_export("customers", "xml"))
        import_export_menu.add_separator()
        import_export_menu.add_command(label="🧾 Rechnungen → CSV", command=lambda: self.advanced_export("invoices", "csv"))
        import_export_menu.add_command(label="📊 Rechnungen → Excel", command=lambda: self.advanced_export("invoices", "excel"))
        import_export_menu.add_command(label="🏢 Rechnungen → DATEV", command=lambda: self.advanced_export("invoices", "datev"))
        import_export_menu.add_command(label="📈 Rechnungen → Lexware", command=lambda: self.advanced_export("invoices", "lexware"))
        import_export_menu.add_separator()
        import_export_menu.add_command(label="📥 CSV importieren", command=lambda: self.advanced_import("csv"))
        import_export_menu.add_command(label="📥 Excel importieren", command=lambda: self.advanced_import("excel"))
        file_menu.add_separator()
        file_menu.add_command(label="❌ Beenden", command=self.root.quit)
        
        # Extras Menu
        extras_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Extras", menu=extras_menu)
        extras_menu.add_command(label="📊 Dashboard", command=self.show_dashboard)
        extras_menu.add_separator()
        extras_menu.add_command(label="📋 Massen-Export", command=self.bulk_export)
        extras_menu.add_command(label="📄 Erweiterte PDF-Exports", command=self.show_advanced_pdf_exports)
        extras_menu.add_separator()
        extras_menu.add_command(label="🔍 Datenvalidierung", command=self.run_data_validation)
        extras_menu.add_command(label="📊 E-Mail-Statistiken", command=self.show_email_statistics)
        extras_menu.add_command(label="⚡ Automatische Erinnerungen", command=self.manage_automatic_reminders)
        extras_menu.add_separator()
        extras_menu.add_command(label="📧 E-Mail-Einstellungen", command=self.show_email_settings)
        extras_menu.add_command(label="🔐 Sicherheit", command=self.show_security_settings)
        extras_menu.add_command(label="📋 Compliance", command=self.show_compliance_management)
        extras_menu.add_separator()
        extras_menu.add_command(label="🔧 Einstellungen", command=self.show_app_settings)
        
        # Firma Menu
        company_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Firma", menu=company_menu)
        company_menu.add_command(label="🏢 Stammdaten", command=self.show_company_settings)
        
        # Hilfe Menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="ℹ️ Über", command=self.show_about)
    
    def create_toolbar(self):
        """Erstellt die Toolbar"""
        toolbar_frame = ctk.CTkFrame(self.root)
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Neue Dokumente
        new_frame = ctk.CTkFrame(toolbar_frame)
        new_frame.pack(side="left", padx=(10, 20))
        
        ctk.CTkLabel(new_frame, text="Neu:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        
        ctk.CTkButton(
            new_frame,
            text="Angebot",
            width=80,
            command=lambda: self.new_document(DocumentType.ANGEBOT)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            new_frame,
            text="Rechnung",
            width=80,
            command=lambda: self.new_document(DocumentType.RECHNUNG)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            new_frame,
            text="Gutschrift",
            width=80,
            command=lambda: self.new_document(DocumentType.GUTSCHRIFT)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            new_frame,
            text="Kunde",
            width=80,
            command=self.new_customer
        ).pack(side="left", padx=(10, 5))
        
        # Aktionen
        action_frame = ctk.CTkFrame(toolbar_frame)
        action_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(action_frame, text="Aktionen:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        
        ctk.CTkButton(
            action_frame,
            text="👁️ Vorschau",
            width=80,
            command=self.preview_selected_document
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="📄 Export",
            width=80,
            command=self.export_selected_document
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="Bearbeiten",
            width=80,
            command=self.edit_selected_document
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="Löschen",
            width=80,
            command=self.delete_selected_document
        ).pack(side="left", padx=(2, 10))
        
        # Erweiterte Aktionen
        advanced_frame = ctk.CTkFrame(toolbar_frame)
        advanced_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(advanced_frame, text="Erweitert:", font=("Arial", 12, "bold")).pack(side="left", padx=(10, 5))
        
        ctk.CTkButton(
            advanced_frame,
            text="🔍 Validierung",
            width=90,
            command=self.run_data_validation
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            advanced_frame,
            text="📊 Analytics",
            width=80,
            command=self.show_analytics_dialog
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            advanced_frame,
            text="⚡ Erinnerungen",
            width=100,
            command=self.manage_automatic_reminders
        ).pack(side="left", padx=(2, 10))
        
        # Einstellungen
        settings_frame = ctk.CTkFrame(toolbar_frame)
        settings_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            settings_frame,
            text="Einstellungen",
            width=100,
            command=self.show_app_settings
        ).pack(side="left", padx=(10, 5))
        
        ctk.CTkButton(
            settings_frame,
            text="Firma",
            width=80,
            command=self.show_company_settings
        ).pack(side="left", padx=(2, 10))
    
    def create_main_area(self):
        """Erstellt den Hauptbereich mit Tabs"""
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Tab für Dokumente
        self.create_documents_tab()
        
        # Tab für Kunden
        self.create_customers_tab()
        
        # Tab für Statistiken
        self.create_statistics_tab()
    
    def create_documents_tab(self):
        """Erstellt den Dokumente-Tab"""
        documents_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(documents_frame, text="Dokumente")
        
        # Filter-Bereich
        filter_frame = ctk.CTkFrame(documents_frame)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        # Dokumenttyp-Filter
        ctk.CTkLabel(filter_frame, text="Typ:").pack(side="left", padx=(10, 5))
        
        self.doc_type_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Alle"] + [dt.value for dt in DocumentType],
            width=120,
            command=self.filter_documents
        )
        self.doc_type_filter.pack(side="left", padx=(0, 10))
        self.doc_type_filter.set("Alle")
        
        # Jahr-Filter
        ctk.CTkLabel(filter_frame, text="Jahr:").pack(side="left", padx=(10, 5))
        
        current_year = datetime.now().year
        years = ["Alle"] + [str(year) for year in range(current_year - 5, current_year + 2)]
        
        self.year_filter = ctk.CTkComboBox(
            filter_frame,
            values=years,
            width=80,
            command=self.filter_documents
        )
        self.year_filter.pack(side="left", padx=(0, 10))
        self.year_filter.set(str(current_year))
        
        # Suchfeld
        ctk.CTkLabel(filter_frame, text="Suche:").pack(side="left", padx=(20, 5))
        
        self.search_entry = ctk.CTkEntry(filter_frame, width=200, placeholder_text="Nummer, Kunde, Beschreibung...")
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_documents())
        
        # Aktualisieren-Button
        ctk.CTkButton(
            filter_frame,
            text="Aktualisieren",
            width=100,
            command=self.refresh_documents_list
        ).pack(side="right", padx=10)
        
        # Dokumentenliste
        list_frame = ctk.CTkFrame(documents_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview für Dokumente
        columns = ("ID", "Typ", "Nummer", "Datum", "Kunde", "Netto", "Brutto", "Status")
        self.documents_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Spalten konfigurieren
        self.documents_tree.heading("ID", text="ID")
        self.documents_tree.heading("Typ", text="Typ")
        self.documents_tree.heading("Nummer", text="Nummer")
        self.documents_tree.heading("Datum", text="Datum")
        self.documents_tree.heading("Kunde", text="Kunde")
        self.documents_tree.heading("Netto", text="Netto €")
        self.documents_tree.heading("Brutto", text="Brutto €")
        self.documents_tree.heading("Status", text="Status")
        
        # ID-Spalte verstecken
        self.documents_tree.column("ID", width=0, stretch=False)
        self.documents_tree.column("Typ", width=80)
        self.documents_tree.column("Nummer", width=120)
        self.documents_tree.column("Datum", width=100)
        self.documents_tree.column("Kunde", width=200)
        self.documents_tree.column("Netto", width=100, anchor="e")
        self.documents_tree.column("Brutto", width=100, anchor="e")
        self.documents_tree.column("Status", width=100)
        
        # Scrollbar für Dokumente
        doc_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.documents_tree.yview)
        self.documents_tree.configure(yscrollcommand=doc_scrollbar.set)
        
        self.documents_tree.pack(side="left", fill="both", expand=True)
        doc_scrollbar.pack(side="right", fill="y")
        
        # Doppelklick-Handler
        self.documents_tree.bind("<Double-1>", lambda e: self.edit_selected_document())
    
    def create_customers_tab(self):
        """Erstellt den Kunden-Tab"""
        customers_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(customers_frame, text="Kunden")
        
        # Kunden-Toolbar
        cust_toolbar = ctk.CTkFrame(customers_frame)
        cust_toolbar.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            cust_toolbar,
            text="Neuer Kunde",
            width=120,
            command=self.new_customer
        ).pack(side="left", padx=(10, 5))
        
        ctk.CTkButton(
            cust_toolbar,
            text="Bearbeiten",
            width=100,
            command=self.edit_selected_customer
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            cust_toolbar,
            text="Löschen",
            width=80,
            command=self.delete_selected_customer
        ).pack(side="left", padx=5)
        
        # Kunden-Suchfeld
        ctk.CTkLabel(cust_toolbar, text="Suche:").pack(side="left", padx=(20, 5))
        
        self.customer_search_entry = ctk.CTkEntry(cust_toolbar, width=200, placeholder_text="Name, Firma, Kundennummer...")
        self.customer_search_entry.pack(side="left", padx=(0, 10))
        self.customer_search_entry.bind("<KeyRelease>", lambda e: self.filter_customers())
        
        # Kundenliste
        cust_list_frame = ctk.CTkFrame(customers_frame)
        cust_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview für Kunden
        cust_columns = ("Nummer", "Firma", "Kontakt", "Ort", "E-Mail", "Telefon")
        self.customers_tree = ttk.Treeview(cust_list_frame, columns=cust_columns, show="headings", height=15)
        
        # Spalten konfigurieren
        self.customers_tree.heading("Nummer", text="Kundennr.")
        self.customers_tree.heading("Firma", text="Firma")
        self.customers_tree.heading("Kontakt", text="Kontaktperson")
        self.customers_tree.heading("Ort", text="Ort")
        self.customers_tree.heading("E-Mail", text="E-Mail")
        self.customers_tree.heading("Telefon", text="Telefon")
        
        self.customers_tree.column("Nummer", width=100)
        self.customers_tree.column("Firma", width=200)
        self.customers_tree.column("Kontakt", width=150)
        self.customers_tree.column("Ort", width=120)
        self.customers_tree.column("E-Mail", width=180)
        self.customers_tree.column("Telefon", width=120)
        
        # Scrollbar für Kunden
        cust_scrollbar = ttk.Scrollbar(cust_list_frame, orient="vertical", command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=cust_scrollbar.set)
        
        self.customers_tree.pack(side="left", fill="both", expand=True)
        cust_scrollbar.pack(side="right", fill="y")
        
        # Doppelklick-Handler
        self.customers_tree.bind("<Double-1>", lambda e: self.edit_selected_customer())
    
    def create_statistics_tab(self):
        """Erstellt den Statistiken-Tab"""
        stats_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(stats_frame, text="Statistiken")
        
        # Statistiken werden hier angezeigt
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Statistiken werden hier angezeigt...",
            font=("Arial", 14)
        )
        self.stats_label.pack(expand=True)
    
    def create_statusbar(self):
        """Erstellt die Statusleiste"""
        self.statusbar = ctk.CTkFrame(self.root, height=30)
        self.statusbar.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(self.statusbar, text="Bereit", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Rechte Seite der Statusleiste
        self.stats_summary_label = ctk.CTkLabel(self.statusbar, text="", anchor="e")
        self.stats_summary_label.pack(side="right", padx=10, pady=5)
        
        self.update_status_statistics()
    
    # Event-Handler
    def new_document(self, document_type: DocumentType):
        """Erstellt ein neues Dokument"""
        self.set_status(f"Erstelle neues {document_type.value}...")
        
        # Neues Dokument erstellen
        invoice = Invoice()
        invoice.document_type = document_type
        invoice.invoice_date = datetime.now()
        
        # Editor öffnen
        editor = InvoiceEditWindow(self.root, invoice, self.data_manager)
        if editor.result:
            self.data_manager.add_invoice(editor.result)
            self.refresh_documents_list()
            self.update_status_statistics()
            self.set_status(f"{document_type.value} erstellt.")
    
    def new_customer(self):
        """Erstellt einen neuen Kunden"""
        self.set_status("Erstelle neuen Kunden...")
        
        customer = Customer()
        
        editor = CustomerEditWindow(self.root, customer, self.data_manager)
        if editor.result:
            print(f"🔄 Speichere neuen Kunden: {editor.result.get_display_name()}")
            self.data_manager.add_customer(editor.result)
            self.refresh_customers_list()
            self.update_status_statistics()
            self.set_status(f"Kunde erstellt: {editor.result.get_display_name()}")
        else:
            self.set_status("Kundenerstellung abgebrochen.")
    
    def edit_selected_document(self):
        """Bearbeitet das ausgewählte Dokument"""
        selection = self.documents_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie ein Dokument aus.")
            return
        
        item = self.documents_tree.item(selection[0])
        invoice_id = item['values'][0]  # ID aus der versteckten Spalte
        
        # Dokument anhand der ID finden
        invoice = self.data_manager.get_invoice_by_id(invoice_id)
        
        if not invoice:
            messagebox.showerror("Fehler", "Dokument nicht gefunden.")
            return
        
        self.set_status(f"Bearbeite {invoice.document_type.value} {invoice.invoice_number}...")
        
        editor = InvoiceEditWindow(self.root, invoice, self.data_manager)
        if editor.result:
            self.data_manager.update_invoice(editor.result)
            self.refresh_documents_list()
            self.update_status_statistics()
            self.set_status("Dokument gespeichert.")
    
    def edit_selected_customer(self):
        """Bearbeitet den ausgewählten Kunden"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie einen Kunden aus.")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_number = item['values'][0]
        
        # Kunde anhand der Nummer finden
        customers = self.data_manager.get_customers()
        customer = None
        for cust in customers:
            if cust.customer_number == customer_number:
                customer = cust
                break
        
        if not customer:
            messagebox.showerror("Fehler", "Kunde nicht gefunden.")
            return
        
        self.set_status(f"Bearbeite Kunde {customer.get_display_name()}...")
        
        editor = CustomerEditWindow(self.root, customer, self.data_manager)
        if editor.result:
            print(f"🔄 Aktualisiere Kunden: {editor.result.get_display_name()}")
            self.data_manager.update_customer(editor.result)
            self.refresh_customers_list()
            self.set_status(f"Kunde gespeichert: {editor.result.get_display_name()}")
        else:
            self.set_status("Bearbeitung abgebrochen.")
    
    def delete_selected_document(self):
        """Löscht das ausgewählte Dokument"""
        selection = self.documents_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie ein Dokument aus.")
            return
        
        item = self.documents_tree.item(selection[0])
        invoice_number = item['values'][1]
        doc_type = item['values'][0]
        
        if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie das {doc_type} {invoice_number} wirklich löschen?"):
            # Dokument finden und löschen
            invoices = self.data_manager.get_invoices()
            for invoice in invoices:
                if invoice.invoice_number == invoice_number:
                    self.data_manager.delete_invoice(invoice.id)
                    break
            
            self.refresh_documents_list()
            self.update_status_statistics()
            self.set_status("Dokument gelöscht.")
    
    def delete_selected_customer(self):
        """Löscht den ausgewählten Kunden"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie einen Kunden aus.")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_number = item['values'][0]
        customer_name = item['values'][1] or item['values'][2]
        
        if messagebox.askyesno("Löschen bestätigen", f"Möchten Sie den Kunden {customer_name} ({customer_number}) wirklich löschen?"):
            # Kunde finden und löschen
            customers = self.data_manager.get_customers()
            for customer in customers:
                if customer.customer_number == customer_number:
                    self.data_manager.delete_customer(customer.id)
                    break
            
            self.refresh_customers_list()
            self.update_status_statistics()
            self.set_status("Kunde gelöscht.")
    
    def export_selected_document(self):
        """Exportiert das ausgewählte Dokument als PDF"""
        selection = self.documents_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie ein Dokument aus.")
            return
        
        item = self.documents_tree.item(selection[0])
        invoice_id = item['values'][0]  # ID aus der versteckten Spalte
        
        # Dokument anhand der ID finden
        invoice = self.data_manager.get_invoice_by_id(invoice_id)
        
        if not invoice:
            messagebox.showerror("Fehler", "Dokument nicht gefunden.")
            return
        
        # Dateiname vorschlagen
        filename = f"{invoice.document_type.value}_{invoice.invoice_number}.pdf"
        filename = filename.replace("/", "-").replace("\\", "-")
        
        # Speicherort wählen
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF-Dateien", "*.pdf")]
        )
        
        if file_path:
            self.set_status(f"Exportiere {invoice.document_type.value} {invoice.invoice_number}...")
            
            try:
                # PDF generieren
                company_data = self.data_manager.get_company_data()
                settings = self.data_manager.get_settings()
                
                pdf_generator = InvoicePDFGenerator(
                    company_data, 
                    settings.pdf_company_color,
                    settings.enable_qr_codes
                )
                
                if pdf_generator.generate_pdf(invoice, file_path):
                    self.set_status(f"PDF erfolgreich exportiert: {file_path}")
                    messagebox.showinfo("Export erfolgreich", f"PDF wurde erfolgreich erstellt:\n{file_path}")
                else:
                    self.set_status("Fehler beim PDF-Export.")
                    messagebox.showerror("Export-Fehler", "Fehler beim Erstellen des PDFs.")
                    
            except Exception as e:
                self.set_status("Fehler beim PDF-Export.")
                messagebox.showerror("Export-Fehler", f"Fehler beim Erstellen des PDFs:\n{str(e)}")
    
    def preview_selected_document(self):
        """Zeigt Vorschau des ausgewählten Dokuments"""
        selection = self.documents_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie ein Dokument aus.")
            return
        
        item = self.documents_tree.item(selection[0])
        invoice_id = item['values'][0]  # ID aus der versteckten Spalte
        
        # Dokument anhand der ID finden
        invoice = self.data_manager.get_invoice_by_id(invoice_id)
        
        if not invoice:
            messagebox.showerror("Fehler", "Dokument nicht gefunden.")
            return
        
        self.set_status(f"Erstelle Vorschau für {invoice.document_type.value} {invoice.invoice_number}...")
        
        try:
            from src.utils.pdf_preview import PDFPreviewManager
            
            company_data = self.data_manager.get_company_data()
            settings = self.data_manager.get_settings()
            
            preview_manager = PDFPreviewManager(company_data, settings.pdf_company_color)
            
            if preview_manager.show_preview(invoice):
                self.set_status("Vorschau geöffnet.")
            else:
                self.set_status("Vorschau konnte nicht erstellt werden.")
                messagebox.showerror("Fehler", "Vorschau konnte nicht erstellt werden.")
                
        except Exception as e:
            error_msg = f"Fehler bei der Vorschau: {str(e)}"
            self.set_status(error_msg)
            messagebox.showerror("Fehler", error_msg)

    # Erweiterte Funktionen
    def create_backup(self):
        """Erstellt ein Backup"""
        try:
            from src.utils.backup_manager import BackupManager
            backup_manager = BackupManager()
            backup_path = backup_manager.create_backup()
            messagebox.showinfo("Backup", f"Backup erfolgreich erstellt:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Backup fehlgeschlagen:\n{str(e)}")
    
    def restore_backup(self):
        """Stellt ein Backup wieder her"""
        try:
            backup_file = filedialog.askopenfilename(
                title="Backup auswählen",
                filetypes=[("ZIP-Dateien", "*.zip")]
            )
            
            if backup_file:
                from src.utils.backup_manager import BackupManager
                backup_manager = BackupManager()
                
                if messagebox.askyesno("Warnung", 
                    "Das Wiederherstellen überschreibt alle aktuellen Daten!\n"
                    "Ein Notfall-Backup wird automatisch erstellt.\n\n"
                    "Fortfahren?"):
                    
                    if backup_manager.restore_backup(Path(backup_file)):
                        messagebox.showinfo("Erfolg", "Backup erfolgreich wiederhergestellt!")
                        self.refresh_all_lists()
                    else:
                        messagebox.showerror("Fehler", "Backup konnte nicht wiederhergestellt werden!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Backup-Wiederherstellung fehlgeschlagen:\n{str(e)}")
    
    def export_all_data(self):
        """Exportiert alle Daten"""
        try:
            export_file = filedialog.asksaveasfilename(
                title="Daten exportieren",
                defaultextension=".json",
                filetypes=[("JSON-Dateien", "*.json")]
            )
            
            if export_file:
                self.data_manager.export_all_data(export_file)
                messagebox.showinfo("Export", f"Daten erfolgreich exportiert:\n{export_file}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{str(e)}")
    
    def import_all_data(self):
        """Importiert alle Daten"""
        try:
            import_file = filedialog.askopenfilename(
                title="Daten importieren",
                filetypes=[("JSON-Dateien", "*.json")]
            )
            
            if import_file:
                if messagebox.askyesno("Warnung", 
                    "Das Importieren überschreibt alle aktuellen Daten!\n\n"
                    "Fortfahren?"):
                    
                    self.data_manager.import_all_data(import_file)
                    messagebox.showinfo("Import", "Daten erfolgreich importiert!")
                    self.refresh_all_lists()
        except Exception as e:
            messagebox.showerror("Fehler", f"Import fehlgeschlagen:\n{str(e)}")
    
    def run_data_validation(self):
        """Führt Datenvalidierung durch"""
        try:
            from ..utils.validation import DataIntegrityChecker
            checker = DataIntegrityChecker(self.data_manager)
            issues = checker.check_integrity()
            
            all_issues = []
            for severity, issue_list in issues.items():
                if issue_list:
                    all_issues.extend([f"[{severity.upper()}] {issue}" for issue in issue_list])
            
            if all_issues:
                issue_text = "\n".join([f"• {issue}" for issue in all_issues])
                messagebox.showwarning("Validierungsergebnisse", f"Folgende Probleme wurden gefunden:\n\n{issue_text}")
            else:
                messagebox.showinfo("Validierung", "✅ Keine Probleme gefunden! Alle Daten sind konsistent.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Datenvalidierung: {str(e)}")
    
    def bulk_export(self):
        """Führt Massen-Export durch"""
        try:
            from tkinter import filedialog
            
            # Export-Verzeichnis wählen
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis wählen")
            if not export_dir:
                return
            
            # Alle Dokumente als PDF exportieren
            company_data = self.data_manager.get_company_data()
            app_settings = self.data_manager.get_settings()
            pdf_generator = InvoicePDFGenerator(
                company_data,
                enable_qr_code=app_settings.enable_qr_codes
            )
            invoices = self.data_manager.get_invoices()
            
            exported = 0
            for invoice in invoices:
                try:
                    filename = f"{invoice.invoice_number}_{invoice.invoice_date.strftime('%Y%m%d')}.pdf"
                    filepath = os.path.join(export_dir, filename)
                    
                    pdf_generator.generate_pdf(invoice, filepath)
                    exported += 1
                except Exception as e:
                    print(f"Fehler beim Export von {invoice.invoice_number}: {e}")
            
            messagebox.showinfo("Export", f"{exported} Dokumente wurden nach {export_dir} exportiert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Massen-Export: {str(e)}")
    
    def show_advanced_pdf_exports(self):
        """Zeigt erweiterte PDF-Export-Optionen"""
        try:
            from .advanced_pdf_window import AdvancedPDFWindow
            AdvancedPDFWindow(self.root, self.data_manager)
        except ImportError:
            # Fallback: Erweiterte PDF-Optionen direkt implementieren
            self.show_advanced_pdf_dialog()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der erweiterten PDF-Exports: {str(e)}")
    
    def show_advanced_pdf_dialog(self):
        """Zeigt erweiterte PDF-Export-Dialog"""
        try:
            # Erstelle erweiterten PDF-Export-Dialog
            pdf_window = ctk.CTkToplevel(self.root)
            pdf_window.title("Erweiterte PDF-Exports")
            pdf_window.geometry("600x500")
            pdf_window.transient(self.root)
            pdf_window.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(pdf_window)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header_frame,
                text="📄 Erweiterte PDF-Export-Optionen",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=10)
            
            # Export-Optionen
            options_frame = ctk.CTkFrame(pdf_window)
            options_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Export nach Kunde
            customer_frame = ctk.CTkFrame(options_frame)
            customer_frame.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(customer_frame, text="Export nach Kunde:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            customers = self.data_manager.get_customers()
            customer_names = [f"{c.customer_number} - {c.get_display_name()}" for c in customers]
            
            customer_var = ctk.StringVar()
            customer_combo = ctk.CTkComboBox(customer_frame, values=customer_names, variable=customer_var)
            customer_combo.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkButton(
                customer_frame,
                text="Kunden-PDFs exportieren",
                command=lambda: self.export_customer_pdfs(customer_var.get())
            ).pack(pady=5)
            
            # Export nach Datumsbereich
            date_frame = ctk.CTkFrame(options_frame)
            date_frame.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(date_frame, text="Export nach Datumsbereich:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            date_input_frame = ctk.CTkFrame(date_frame)
            date_input_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(date_input_frame, text="Von (YYYY-MM-DD):").pack(side="left", padx=5)
            start_date_var = ctk.StringVar()
            start_date_entry = ctk.CTkEntry(date_input_frame, textvariable=start_date_var, placeholder_text="2024-01-01")
            start_date_entry.pack(side="left", padx=5)
            
            ctk.CTkLabel(date_input_frame, text="Bis (YYYY-MM-DD):").pack(side="left", padx=5)
            end_date_var = ctk.StringVar()
            end_date_entry = ctk.CTkEntry(date_input_frame, textvariable=end_date_var, placeholder_text="2024-12-31")
            end_date_entry.pack(side="left", padx=5)
            
            ctk.CTkButton(
                date_frame,
                text="Datumsbereich exportieren",
                command=lambda: self.export_date_range_pdfs(start_date_var.get(), end_date_var.get())
            ).pack(pady=5)
            
            # Batch-Export mit Mustern
            pattern_frame = ctk.CTkFrame(options_frame)
            pattern_frame.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(pattern_frame, text="Dateinamen-Muster:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            pattern_var = ctk.StringVar(value="{doc_type}_{number}_{date}")
            pattern_entry = ctk.CTkEntry(pattern_frame, textvariable=pattern_var)
            pattern_entry.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(pattern_frame, text="Verfügbare Platzhalter: {doc_type}, {number}, {date}, {customer}", font=ctk.CTkFont(size=10)).pack(padx=10)
            
            ctk.CTkButton(
                pattern_frame,
                text="Alle mit Muster exportieren",
                command=lambda: self.export_with_pattern(pattern_var.get())
            ).pack(pady=5)
            
            # Schließen-Button
            ctk.CTkButton(
                pdf_window,
                text="Schließen",
                command=pdf_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des PDF-Export-Dialogs: {str(e)}")
    
    def export_customer_pdfs(self, customer_selection):
        """Exportiert PDFs für einen bestimmten Kunden"""
        try:
            if not customer_selection:
                messagebox.showwarning("Warnung", "Bitte wählen Sie einen Kunden aus.")
                return
            
            customer_number = customer_selection.split(" - ")[0]
            customer = None
            for c in self.data_manager.get_customers():
                if c.customer_number == customer_number:
                    customer = c
                    break
            
            if not customer:
                messagebox.showerror("Fehler", "Kunde nicht gefunden.")
                return
            
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Kunde wählen")
            if not export_dir:
                return
            
            # PDF-Exporter verwenden
            from ..utils.pdf_preview import BulkExportManager
            company_data = self.data_manager.get_company_data()
            batch_exporter = BulkExportManager(company_data)
            
            invoices = self.data_manager.get_invoices_by_customer(customer.id)
            if not invoices:
                messagebox.showinfo("Info", f"Keine Dokumente für Kunde {customer.get_display_name()} gefunden.")
                return
            
            exported = batch_exporter.export_customer_invoices(
                customer.id,
                invoices,
                Path(export_dir)
            )
            
            messagebox.showinfo("Export", f"{exported} Dokumente für {customer.get_display_name()} exportiert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Kunden-Export: {str(e)}")
    
    def export_date_range_pdfs(self, start_date_str, end_date_str):
        """Exportiert PDFs für einen Datumsbereich"""
        try:
            if not start_date_str or not end_date_str:
                messagebox.showwarning("Warnung", "Bitte geben Sie Start- und Enddatum ein.")
                return
            
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Datumsbereich wählen")
            if not export_dir:
                return
            
            # PDF-Exporter verwenden
            from ..utils.pdf_preview import BulkExportManager
            company_data = self.data_manager.get_company_data()
            batch_exporter = BulkExportManager(company_data)
            
            all_invoices = self.data_manager.get_invoices()
            date_filtered_invoices = [
                inv for inv in all_invoices 
                if start_date.date() <= inv.invoice_date <= end_date.date()
            ]
            
            if not date_filtered_invoices:
                messagebox.showinfo("Info", f"Keine Dokumente im Zeitraum {start_date_str} bis {end_date_str} gefunden.")
                return
            
            exported = batch_exporter.export_by_date_range(
                date_filtered_invoices,
                start_date,
                end_date,
                Path(export_dir)
            )
            
            messagebox.showinfo("Export", f"{exported} Dokumente für Zeitraum {start_date_str} bis {end_date_str} exportiert.")
            
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiges Datumsformat. Bitte verwenden Sie YYYY-MM-DD.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Datumsbereich-Export: {str(e)}")
    
    def export_with_pattern(self, pattern):
        """Exportiert alle PDFs mit benutzerdefiniertem Dateinamen-Muster"""
        try:
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Muster-Export wählen")
            if not export_dir:
                return
            
            # PDF-Exporter verwenden
            from ..utils.pdf_preview import BulkExportManager
            company_data = self.data_manager.get_company_data()
            batch_exporter = BulkExportManager(company_data)
            
            invoices = self.data_manager.get_invoices()
            if not invoices:
                messagebox.showinfo("Info", "Keine Dokumente zum Exportieren vorhanden.")
                return
            
            exported = batch_exporter.export_multiple_invoices(
                invoices,
                Path(export_dir)
            )
            
            messagebox.showinfo("Export", f"{exported} Dokumente mit Muster '{pattern}' exportiert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Muster-Export: {str(e)}")
    
    def show_email_statistics(self):
        """Zeigt E-Mail-Statistiken"""
        try:
            stats = self.email_manager.get_email_statistics()
            
            # Erstelle Statistik-Dialog
            stats_window = ctk.CTkToplevel(self.root)
            stats_window.title("E-Mail-Statistiken")
            stats_window.geometry("500x400")
            stats_window.transient(self.root)
            stats_window.grab_set()
            
            # Scrollbarer Bereich
            scroll_frame = ctk.CTkScrollableFrame(stats_window)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            ctk.CTkLabel(
                scroll_frame,
                text="📊 E-Mail-Statistiken",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=(0, 20))
            
            # Statistik-Items
            for key, value in stats.items():
                frame = ctk.CTkFrame(scroll_frame)
                frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    frame,
                    text=f"{key}:",
                    font=ctk.CTkFont(weight="bold")
                ).pack(side="left", padx=10, pady=10)
                
                ctk.CTkLabel(
                    frame,
                    text=str(value)
                ).pack(side="right", padx=10, pady=10)
            
            # Schließen-Button
            ctk.CTkButton(
                stats_window,
                text="Schließen",
                command=stats_window.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der E-Mail-Statistiken: {str(e)}")
    
    def manage_automatic_reminders(self):
        """Verwaltet automatische Zahlungserinnerungen"""
        try:
            # Erstelle Erinnerungs-Management-Dialog
            reminder_window = ctk.CTkToplevel(self.root)
            reminder_window.title("Automatische Zahlungserinnerungen")
            reminder_window.geometry("700x500")
            reminder_window.transient(self.root)
            reminder_window.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(reminder_window)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header_frame,
                text="⚡ Automatische Zahlungserinnerungen",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(side="left", padx=10, pady=10)
            
            # Aktions-Buttons
            ctk.CTkButton(
                header_frame,
                text="Erinnerungen senden",
                command=self.send_automatic_reminders
            ).pack(side="right", padx=10, pady=10)
            
            # Pending Reminders anzeigen
            scroll_frame = ctk.CTkScrollableFrame(reminder_window)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            pending_reminders = self.email_manager.get_pending_reminders()
            
            if not pending_reminders:
                ctk.CTkLabel(
                    scroll_frame,
                    text="✅ Keine offenen Erinnerungen vorhanden",
                    font=ctk.CTkFont(size=14)
                ).pack(pady=20)
            else:
                for reminder in pending_reminders:
                    frame = ctk.CTkFrame(scroll_frame)
                    frame.pack(fill="x", pady=5)
                    
                    info_text = f"Rechnung {reminder['invoice_number']} - {reminder['customer_name']}\n"
                    info_text += f"Fällig seit: {reminder['days_overdue']} Tagen"
                    
                    ctk.CTkLabel(
                        frame,
                        text=info_text,
                        justify="left"
                    ).pack(side="left", padx=10, pady=10)
                    
                    ctk.CTkLabel(
                        frame,
                        text=f"Level {reminder['reminder_level']}",
                        font=ctk.CTkFont(weight="bold")
                    ).pack(side="right", padx=10, pady=10)
            
            # Schließen-Button
            ctk.CTkButton(
                reminder_window,
                text="Schließen",
                command=reminder_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Verwalten der Erinnerungen: {str(e)}")
    
    def send_automatic_reminders(self):
        """Sendet automatische Erinnerungen"""
        try:
            sent_count, errors = self.email_manager.send_automatic_reminders()
            
            if errors:
                error_text = "\n".join(errors)
                messagebox.showwarning(
                    "Erinnerungen gesendet", 
                    f"{sent_count} Erinnerungen gesendet.\n\nFehler:\n{error_text}"
                )
            else:
                messagebox.showinfo(
                    "Erinnerungen gesendet", 
                    f"✅ {sent_count} Erinnerungen erfolgreich gesendet."
                )
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Senden der Erinnerungen: {str(e)}")
    
    def advanced_export(self, data_type, format_type):
        """Führt erweiterte Exporte durch"""
        try:
            # Export-Dialog
            if data_type == "customers":
                file_types = {
                    "csv": [("CSV-Dateien", "*.csv")],
                    "excel": [("Excel-Dateien", "*.xlsx")],
                    "xml": [("XML-Dateien", "*.xml")]
                }
                default_name = f"kunden_export.{format_type}"
            else:  # invoices
                file_types = {
                    "csv": [("CSV-Dateien", "*.csv")],
                    "excel": [("Excel-Dateien", "*.xlsx")],
                    "datev": [("DATEV-Dateien", "*.csv")],
                    "lexware": [("Lexware-Dateien", "*.csv")]
                }
                default_name = f"rechnungen_export.{format_type}"
            
            file_path = filedialog.asksaveasfilename(
                title=f"{data_type.title()} als {format_type.upper()} exportieren",
                defaultextension=f".{format_type}",
                filetypes=file_types.get(format_type, [("Alle Dateien", "*.*")])
            )
            
            if not file_path:
                return
            
            # Export durchführen
            from ..utils.import_export_manager import DataExporter
            exporter = DataExporter(self.data_manager)
            
            success = False
            message = ""
            
            if data_type == "customers":
                if format_type == "csv":
                    success, message = exporter.export_customers(file_path, "csv")
                elif format_type == "excel":
                    success, message = exporter.export_customers(file_path, "excel")
                elif format_type == "xml":
                    success, message = exporter.export_customers(file_path, "xml")
            else:  # invoices
                if format_type == "csv":
                    success, message = exporter.export_invoices(file_path, "csv")
                elif format_type == "excel":
                    success, message = exporter.export_invoices(file_path, "excel")
                elif format_type == "datev":
                    success, message = exporter.export_invoices(file_path, "datev")
                elif format_type == "lexware":
                    success, message = exporter.export_invoices(file_path, "lexware")
            
            if success:
                messagebox.showinfo("Export erfolgreich", f"✅ Export nach {file_path} abgeschlossen.\n\n{message}")
            else:
                messagebox.showerror("Export-Fehler", f"❌ Export fehlgeschlagen:\n\n{message}")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim erweiterten Export: {str(e)}")
    
    def advanced_import(self, format_type):
        """Führt erweiterte Importe durch"""
        try:
            # Import-Dialog
            file_types = {
                "csv": [("CSV-Dateien", "*.csv")],
                "excel": [("Excel-Dateien", "*.xlsx")]
            }
            
            file_path = filedialog.askopenfilename(
                title=f"{format_type.upper()}-Datei zum Importieren wählen",
                filetypes=file_types.get(format_type, [("Alle Dateien", "*.*")])
            )
            
            if not file_path:
                return
            
            # Import-Optionen-Dialog
            import_window = ctk.CTkToplevel(self.root)
            import_window.title(f"{format_type.upper()}-Import")
            import_window.geometry("400x300")
            import_window.transient(self.root)
            import_window.grab_set()
            
            # Header
            ctk.CTkLabel(
                import_window,
                text=f"📥 {format_type.upper()}-Import",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=20)
            
            # Datei-Info
            file_frame = ctk.CTkFrame(import_window)
            file_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(file_frame, text="Datei:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            ctk.CTkLabel(file_frame, text=os.path.basename(file_path)).pack(anchor="w", padx=10)
            
            # Import-Optionen
            options_frame = ctk.CTkFrame(import_window)
            options_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(options_frame, text="Optionen:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            update_existing_var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                options_frame,
                text="Vorhandene Datensätze aktualisieren",
                variable=update_existing_var
            ).pack(anchor="w", padx=10, pady=2)
            
            validate_data_var = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                options_frame,
                text="Daten vor Import validieren",
                variable=validate_data_var
            ).pack(anchor="w", padx=10, pady=2)
            
            # Buttons
            button_frame = ctk.CTkFrame(import_window)
            button_frame.pack(fill="x", padx=20, pady=20)
            
            def perform_import():
                try:
                    from ..utils.import_export_manager import DataImporter
                    importer = DataImporter(self.data_manager)
                    
                    # Import durchführen
                    success, message, stats = importer.import_customers(
                        file_path,
                        format_type,
                        update_existing=update_existing_var.get()
                    )
                    
                    import_window.destroy()
                    
                    if success:
                        stats_text = "\n".join([f"• {key}: {value}" for key, value in stats.items()])
                        messagebox.showinfo(
                            "Import erfolgreich", 
                            f"✅ Import abgeschlossen!\n\n{message}\n\nStatistiken:\n{stats_text}"
                        )
                        # Listen aktualisieren
                        self.refresh_all_lists()
                    else:
                        messagebox.showerror("Import-Fehler", f"❌ Import fehlgeschlagen:\n\n{message}")
                        
                except Exception as e:
                    import_window.destroy()
                    messagebox.showerror("Fehler", f"Fehler beim Import: {str(e)}")
            
            ctk.CTkButton(
                button_frame,
                text="Abbrechen",
                command=import_window.destroy
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                button_frame,
                text="Importieren",
                command=perform_import
            ).pack(side="right", padx=10)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim erweiterten Import: {str(e)}")
    
    def show_analytics_dialog(self):
        """Zeigt erweiterte Analyse-Optionen"""
        try:
            # Analytics-Dialog
            analytics_window = ctk.CTkToplevel(self.root)
            analytics_window.title("Erweiterte Analytics")
            analytics_window.geometry("600x500")
            analytics_window.transient(self.root)
            analytics_window.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(analytics_window)
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header_frame,
                text="📊 Erweiterte Analytics & Berichte",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=10)
            
            # Analytics-Optionen
            options_frame = ctk.CTkScrollableFrame(analytics_window)
            options_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # PDF-Analyse
            pdf_frame = ctk.CTkFrame(options_frame)
            pdf_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(pdf_frame, text="📄 Dokument-Analyse", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkButton(
                pdf_frame,
                text="Dokument-Statistiken anzeigen",
                command=self.show_document_analytics
            ).pack(anchor="w", padx=10, pady=5)
            
            # E-Mail-Analyse
            email_frame = ctk.CTkFrame(options_frame)
            email_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(email_frame, text="📧 E-Mail-Analyse", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkButton(
                email_frame,
                text="E-Mail-Statistiken anzeigen",
                command=self.show_email_statistics
            ).pack(anchor="w", padx=10, pady=5)
            
            # Compliance-Analyse
            compliance_frame = ctk.CTkFrame(options_frame)
            compliance_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(compliance_frame, text="📋 Compliance-Analyse", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkButton(
                compliance_frame,
                text="Compliance-Bericht erstellen",
                command=self.show_compliance_report
            ).pack(anchor="w", padx=10, pady=5)
            
            # Geschäfts-Analytics
            business_frame = ctk.CTkFrame(options_frame)
            business_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(business_frame, text="💼 Geschäfts-Analytics", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkButton(
                business_frame,
                text="Umsatz-Analyse",
                command=self.show_revenue_analysis
            ).pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkButton(
                business_frame,
                text="Kunden-Analyse",
                command=self.show_customer_analysis
            ).pack(anchor="w", padx=10, pady=5)
            
            # Schließen-Button
            ctk.CTkButton(
                analytics_window,
                text="Schließen",
                command=analytics_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Analytics: {str(e)}")
    
    def show_document_analytics(self):
        """Zeigt Dokument-Statistiken"""
        try:
            from ..utils.pdf_preview import DocumentAnalyzer
            
            analyzer = DocumentAnalyzer()
            invoices = self.data_manager.get_invoices()
            
            if not invoices:
                messagebox.showinfo("Info", "Keine Dokumente für Analyse vorhanden.")
                return
            
            analysis = analyzer.analyze_invoices(invoices)
            
            # Analyse-Ergebnisse anzeigen
            result_window = ctk.CTkToplevel(self.root)
            result_window.title("Dokument-Analyse")
            result_window.geometry("500x400")
            result_window.transient(self.root)
            result_window.grab_set()
            
            scroll_frame = ctk.CTkScrollableFrame(result_window)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                scroll_frame,
                text="📄 Dokument-Analyse-Ergebnisse",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(0, 15))
            
            for key, value in analysis.items():
                frame = ctk.CTkFrame(scroll_frame)
                frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    frame,
                    text=f"{key}:",
                    font=ctk.CTkFont(weight="bold")
                ).pack(side="left", padx=10, pady=10)
                
                ctk.CTkLabel(
                    frame,
                    text=str(value)
                ).pack(side="right", padx=10, pady=10)
            
            ctk.CTkButton(
                result_window,
                text="Schließen",
                command=result_window.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Dokument-Analyse: {str(e)}")
    
    def show_compliance_report(self):
        """Zeigt Compliance-Bericht"""
        try:
            report = self.compliance_manager.generate_compliance_report()
            
            # Compliance-Bericht anzeigen
            report_window = ctk.CTkToplevel(self.root)
            report_window.title("Compliance-Bericht")
            report_window.geometry("600x500")
            report_window.transient(self.root)
            report_window.grab_set()
            
            scroll_frame = ctk.CTkScrollableFrame(report_window)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                scroll_frame,
                text="📋 Compliance-Bericht",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=(0, 20))
            
            # Bericht-Sections
            for section, data in report.items():
                section_frame = ctk.CTkFrame(scroll_frame)
                section_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    section_frame,
                    text=section.replace("_", " ").title(),
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(anchor="w", padx=10, pady=10)
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        detail_frame = ctk.CTkFrame(section_frame)
                        detail_frame.pack(fill="x", padx=10, pady=2)
                        
                        ctk.CTkLabel(
                            detail_frame,
                            text=f"• {key}: {value}",
                            font=ctk.CTkFont(size=11)
                        ).pack(anchor="w", padx=10, pady=5)
                elif isinstance(data, list):
                    for item in data:
                        ctk.CTkLabel(
                            section_frame,
                            text=f"• {item}",
                            font=ctk.CTkFont(size=11)
                        ).pack(anchor="w", padx=20, pady=2)
                else:
                    ctk.CTkLabel(
                        section_frame,
                        text=str(data),
                        font=ctk.CTkFont(size=11)
                    ).pack(anchor="w", padx=20, pady=5)
            
            ctk.CTkButton(
                report_window,
                text="Schließen",
                command=report_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Compliance-Bericht: {str(e)}")
    
    def show_revenue_analysis(self):
        """Zeigt Umsatz-Analyse"""
        try:
            invoices = self.data_manager.get_invoices()
            if not invoices:
                messagebox.showinfo("Info", "Keine Rechnungen für Umsatz-Analyse vorhanden.")
                return
            
            # Einfache Umsatz-Statistiken
            total_revenue = 0.0
            invoice_count = 0
            
            for invoice in invoices:
                if invoice.document_type.value == "Rechnung":
                    total_revenue += float(invoice.calculate_total_gross())
                    invoice_count += 1
            
            avg_invoice = total_revenue / invoice_count if invoice_count > 0 else 0.0
            
            # Analyse-Dialog
            analysis_window = ctk.CTkToplevel(self.root)
            analysis_window.title("Umsatz-Analyse")
            analysis_window.geometry("400x300")
            analysis_window.transient(self.root)
            analysis_window.grab_set()
            
            # Statistiken anzeigen
            stats_frame = ctk.CTkFrame(analysis_window)
            stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                stats_frame,
                text="💼 Umsatz-Übersicht",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=20)
            
            ctk.CTkLabel(
                stats_frame,
                text=f"Gesamtumsatz: {total_revenue:,.2f} €".replace(".", ","),
                font=ctk.CTkFont(size=14)
            ).pack(pady=5)
            
            ctk.CTkLabel(
                stats_frame,
                text=f"Anzahl Rechnungen: {invoice_count}",
                font=ctk.CTkFont(size=14)
            ).pack(pady=5)
            
            ctk.CTkLabel(
                stats_frame,
                text=f"Durchschnittliche Rechnung: {avg_invoice:,.2f} €".replace(".", ","),
                font=ctk.CTkFont(size=14)
            ).pack(pady=5)
            
            ctk.CTkButton(
                analysis_window,
                text="Schließen",
                command=analysis_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Umsatz-Analyse: {str(e)}")
    
    def show_customer_analysis(self):
        """Zeigt Kunden-Analyse"""
        try:
            customers = self.data_manager.get_customers()
            invoices = self.data_manager.get_invoices()
            
            if not customers:
                messagebox.showinfo("Info", "Keine Kunden für Analyse vorhanden.")
                return
            
            # Analyse-Dialog
            analysis_window = ctk.CTkToplevel(self.root)
            analysis_window.title("Kunden-Analyse")
            analysis_window.geometry("500x400")
            analysis_window.transient(self.root)
            analysis_window.grab_set()
            
            scroll_frame = ctk.CTkScrollableFrame(analysis_window)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                scroll_frame,
                text="👥 Kunden-Übersicht",
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(pady=(0, 20))
            
            # Basis-Statistiken
            stats_frame = ctk.CTkFrame(scroll_frame)
            stats_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                stats_frame,
                text=f"Gesamtzahl Kunden: {len(customers)}",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=10)
            
            # Kunden-Liste mit Basis-Infos
            for customer in customers[:10]:  # Nur erste 10 zeigen
                customer_frame = ctk.CTkFrame(scroll_frame)
                customer_frame.pack(fill="x", pady=2)
                
                info_text = f"{customer.customer_number} - {customer.get_display_name()}"
                if hasattr(customer, 'city') and customer.city:
                    info_text += f" ({customer.city})"
                
                ctk.CTkLabel(
                    customer_frame,
                    text=info_text,
                    font=ctk.CTkFont(size=11)
                ).pack(anchor="w", padx=10, pady=5)
            
            if len(customers) > 10:
                ctk.CTkLabel(
                    scroll_frame,
                    text=f"... und {len(customers) - 10} weitere Kunden",
                    font=ctk.CTkFont(size=10),
                    text_color=("gray50", "gray50")
                ).pack(pady=10)
            
            ctk.CTkButton(
                analysis_window,
                text="Schließen",
                command=analysis_window.destroy
            ).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Kunden-Analyse: {str(e)}")
    
    def show_email_settings(self):
        """Zeigt E-Mail-Einstellungen"""
        try:
            from .email_settings_window import EmailSettingsWindow
            EmailSettingsWindow(self.root, self.email_manager)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der E-Mail-Einstellungen: {str(e)}")
    
    def show_security_settings(self):
        """Zeigt Sicherheitseinstellungen"""
        try:
            from .security_window import SecuritySettingsWindow
            SecuritySettingsWindow(self.root, self.security_manager)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Sicherheitseinstellungen: {str(e)}")
    
    def show_compliance_management(self):
        """Zeigt Compliance-Management"""
        try:
            from .compliance_window import ComplianceWindow
            ComplianceWindow(self.root, self.compliance_manager)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Compliance-Managements: {str(e)}")
    
    def show_dashboard(self):
        """Zeigt Dashboard"""
        try:
            if self.dashboard_window is None or not self.dashboard_window.window.winfo_exists():
                self.dashboard_window = DashboardWindow(self.root, self.data_manager)
            else:
                self.dashboard_window.window.lift()
                self.dashboard_window.window.focus()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Dashboards: {str(e)}")


    
    def show_about(self):
        """Zeigt Über-Dialog"""
        about_text = """
🏢 Rechnungs-Tool - Enterprise Edition v2.1

Ein umfassendes Business-Management-System zur Erstellung und 
Verwaltung von Rechnungen, Angeboten und Gutschriften.

📋 KERNFUNKTIONEN:
✅ Deutsche Steuervorschriften konform (GoBD)
✅ PDF-Export mit professionellem Design  
✅ Erweiterte Dokumenttypen (Angebote, Lieferscheine, Stornos)
✅ Automatische Backup-Funktionen
✅ Umfassende Datenvalidierung

🔐 SICHERHEIT & COMPLIANCE:
✅ Benutzerverwaltung mit Rollenkonzept
✅ Audit-Logging aller Aktivitäten
✅ DSGVO-konforme Datenhaltung
✅ Verschlüsselung sensibler Daten
✅ 2FA-Authentifizierung

📧 BUSINESS-FEATURES:
✅ Email-Integration mit Templates
✅ Automatische Zahlungserinnerungen
✅ CRM-Funktionen für Kundenmanagement
✅ Import/Export (CSV, Excel, DATEV, Lexware)
✅ Live-Dashboard mit Statistiken

🎨 BENUTZEROBERFLÄCHE:
✅ Modernes Dark/Light Theme
✅ Responsive Design
✅ Interaktive Charts und Grafiken
✅ PDF-Live-Vorschau

Entwickelt für kleine bis große Unternehmen.
© 2025 - Professional Business Solutions
        """
        self.show_modern_about_dialog()
    
    def show_modern_about_dialog(self):
        """Zeigt modernes About-Dialog"""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("Über das Rechnungs-Tool")
        about_window.geometry("600x700")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Theme anwenden
        theme_manager.setup_window_theme(about_window)
        
        # Zentrierung
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (about_window.winfo_screenheight() // 2) - (700 // 2)
        about_window.geometry(f"600x700+{x}+{y}")
        
        # Scrollbarer Container
        scroll_frame = ctk.CTkScrollableFrame(about_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(scroll_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🏢 Rechnungs-Tool",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
        
        version_label = ctk.CTkLabel(
            header_frame,
            text="Enterprise Edition v2.1",
            font=ctk.CTkFont(size=16),
            text_color=("gray50", "gray50")
        )
        version_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Professionelles Business-Management-System",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(pady=(5, 10))
        
        # Features-Sektion
        features = [
            ("📋 KERNFUNKTIONEN", [
                "Deutsche Steuervorschriften konform (GoBD)",
                "PDF-Export mit professionellem Design",
                "Erweiterte Dokumenttypen (Angebote, Lieferscheine)",
                "Automatische Backup-Funktionen",
                "Umfassende Datenvalidierung"
            ]),
            ("🔐 SICHERHEIT & COMPLIANCE", [
                "Benutzerverwaltung mit Rollenkonzept",
                "Audit-Logging aller Aktivitäten", 
                "DSGVO-konforme Datenhaltung",
                "Verschlüsselung sensibler Daten",
                "2FA-Authentifizierung"
            ]),
            ("📧 BUSINESS-FEATURES", [
                "Email-Integration mit Templates",
                "Automatische Zahlungserinnerungen",
                "CRM-Funktionen für Kundenmanagement", 
                "Import/Export (CSV, Excel, DATEV, Lexware)",
                "Live-Dashboard mit Statistiken"
            ]),
            ("🎨 BENUTZEROBERFLÄCHE", [
                "Modernes Dark/Light Theme",
                "Responsive Design",
                "Interaktive Charts und Grafiken",
                "PDF-Live-Vorschau",
                "Touch-optimierte Bedienung"
            ])
        ]
        
        for section_title, items in features:
            # Sektion-Header
            section_frame = ctk.CTkFrame(scroll_frame)
            section_frame.pack(fill="x", pady=(10, 0))
            
            section_label = ctk.CTkLabel(
                section_frame,
                text=section_title,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            section_label.pack(fill="x", padx=15, pady=10)
            
            # Feature-Liste
            for item in items:
                item_label = ctk.CTkLabel(
                    section_frame,
                    text=f"✅ {item}",
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                item_label.pack(fill="x", padx=25, pady=2)
        
        # Footer
        footer_frame = ctk.CTkFrame(scroll_frame)
        footer_frame.pack(fill="x", pady=(20, 0))
        
        target_label = ctk.CTkLabel(
            footer_frame,
            text="Entwickelt für kleine bis große Unternehmen",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        target_label.pack(pady=10)
        
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2025 Professional Business Solutions",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        copyright_label.pack(pady=(0, 10))
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            about_window,
            text="OK",
            width=100,
            command=about_window.destroy
        )
        close_btn.pack(pady=20)

    # Einstellungen
    def show_company_settings(self):
        """Zeigt Firmeneinstellungen"""
        try:
            company_data = self.data_manager.get_company_data()
            window = CompanySettingsWindow(self.root, company_data)
            self.root.wait_window(window.window)  # Warten bis Dialog geschlossen wird
            if window.result:
                self.data_manager.update_company_data(window.result)
                self.refresh_all_lists()
                messagebox.showinfo("Erfolg", "Firmendaten wurden gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Firmeneinstellungen konnten nicht geöffnet werden:\n{str(e)}")
    
    def show_app_settings(self):
        """Zeigt Anwendungseinstellungen"""
        try:
            settings = self.data_manager.get_settings()
            window = AppSettingsWindow(self.root, settings)
            if window.result:
                self.data_manager.update_settings(window.result)
                # Theme über Theme-Manager aktualisieren
                theme_manager.apply_theme(window.result.theme_mode, "blue")
                theme_manager.setup_window_theme(self.root)
                self.refresh_all_lists()
        except Exception as e:
            messagebox.showerror("Fehler", f"Anwendungseinstellungen konnten nicht geöffnet werden:\n{str(e)}")
    
    # Listen-Updates
    def refresh_all_lists(self):
        """Aktualisiert alle Listen"""
        self.refresh_documents_list()
        self.refresh_customers_list()
        self.update_statistics()
        self.update_status_statistics()
    
    def refresh_documents_list(self):
        """Aktualisiert die Dokumentenliste"""
        # Alte Einträge löschen
        for item in self.documents_tree.get_children():
            self.documents_tree.delete(item)
        
        # Dokumente laden und anzeigen
        invoices = self.data_manager.get_invoices()
        
        for invoice in sorted(invoices, key=lambda x: x.invoice_date, reverse=True):
            # Status bestimmen
            status = "Offen"
            if invoice.document_type == DocumentType.RECHNUNG:
                status = "Bezahlt" if invoice.is_paid else "Offen"
            elif invoice.document_type == DocumentType.ANGEBOT:
                status = "Angebot"
            
            # Kunde
            customer_name = ""
            if invoice.customer:
                customer_name = invoice.customer.get_display_name()
            
            # Beträge formatieren
            net_amount = f"{invoice.calculate_total_net():,.2f}".replace('.', ',')
            gross_amount = f"{invoice.calculate_total_gross():,.2f}".replace('.', ',')
            
            self.documents_tree.insert("", "end", values=(
                invoice.id,  # Versteckte ID-Spalte
                invoice.document_type.value,
                invoice.invoice_number,
                invoice.invoice_date.strftime("%d.%m.%Y"),
                customer_name,
                net_amount,
                gross_amount,
                status
            ))
        
        self.filter_documents()
    
    def refresh_customers_list(self):
        """Aktualisiert die Kundenliste"""
        print("🔄 Aktualisiere Kundenliste...")
        
        # Alte Einträge löschen
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Kunden laden und anzeigen
        customers = self.data_manager.get_customers()
        print(f"📊 Lade {len(customers)} Kunden in die Liste")
        
        for customer in sorted(customers, key=lambda x: x.customer_number):
            display_name = customer.get_display_name()
            print(f"  ➕ {customer.customer_number}: {display_name}")
            
            self.customers_tree.insert("", "end", values=(
                customer.customer_number,
                customer.company_name,
                customer.contact_person,
                customer.city,
                customer.email,
                customer.phone
            ))
        
        self.filter_customers()
        print("✅ Kundenliste aktualisiert")
    
    def filter_documents(self, *args):
        """Filtert die Dokumentenliste"""
        # TODO: Implementiere Filterlogik
        pass
    
    def filter_customers(self, *args):
        """Filtert die Kundenliste"""
        # TODO: Implementiere Filterlogik
        pass
    
    def update_statistics(self):
        """Aktualisiert die Statistiken"""
        stats = self.data_manager.get_statistics()
        
        stats_text = f"""
Statistiken:

Kunden: {stats['total_customers']}
Dokumente: {stats['total_invoices']}

Dokumente nach Typ:
"""
        
        for doc_type, count in stats['invoices_by_type'].items():
            stats_text += f"  {doc_type}: {count}\n"
        
        stats_text += f"""
Umsatz (Rechnungen): {stats['total_revenue']:,.2f} €
Offene Rechnungen: {stats['unpaid_invoices']} ({stats['unpaid_amount']:,.2f} €)
"""
        
        self.stats_label.configure(text=stats_text.replace('.', ','))
    
    def update_status_statistics(self):
        """Aktualisiert die Statistiken in der Statusleiste"""
        stats = self.data_manager.get_statistics()
        summary = f"Kunden: {stats['total_customers']} | Dokumente: {stats['total_invoices']} | Offen: {stats['unpaid_amount']:,.2f} €".replace('.', ',')
        self.stats_summary_label.configure(text=summary)
    
    def set_status(self, message: str):
        """Setzt die Statusnachricht"""
        self.status_label.configure(text=message)
        self.root.update()
    
    def on_closing(self):
        """Behandelt das Schließen der Anwendung"""
        # Einstellungen speichern
        settings = self.data_manager.get_settings()
        settings.window_width = self.root.winfo_width()
        settings.window_height = self.root.winfo_height()
        self.data_manager.update_settings(settings)
        
        # Alle Daten speichern
        self.data_manager.save_all_data()
        
        self.root.destroy()
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
