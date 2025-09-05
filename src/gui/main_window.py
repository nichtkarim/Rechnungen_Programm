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

# GUI-Module importieren (werden später erstellt)
from src.gui.invoice_edit_window import InvoiceEditWindow
from src.gui.customer_edit_window import CustomerEditWindow
from src.gui.company_settings_window import CompanySettingsWindow
from src.gui.app_settings_window import AppSettingsWindow


class MainWindow:
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        # Datenmanager initialisieren
        self.data_manager = DataManager()
        
        # Hauptfenster erstellen
        self.root = ctk.CTk()
        self.root.title("Rechnungs-Tool")
        
        # Fenstereinstellungen
        settings = self.data_manager.get_settings()
        self.root.geometry(f"{settings.window_width}x{settings.window_height}")
        
        # Theme setzen
        ctk.set_appearance_mode(settings.theme_mode)
        ctk.set_default_color_theme("blue")
        
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
        file_menu.add_command(label="❌ Beenden", command=self.root.quit)
        
        # Extras Menu
        extras_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Extras", menu=extras_menu)
        extras_menu.add_command(label="📊 Dashboard", command=self.show_dashboard)
        extras_menu.add_command(label="✅ Datenvalidierung", command=self.run_data_validation)
        extras_menu.add_command(label="📋 Massen-Export", command=self.bulk_export)
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
                
                pdf_generator = InvoicePDFGenerator(company_data, settings.pdf_company_color)
                
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
    
    def show_dashboard(self):
        """Zeigt das Dashboard"""
        try:
            from src.gui.dashboard_window import DashboardWindow
            DashboardWindow(self.root, self.data_manager)
        except ImportError:
            messagebox.showinfo("Info", "Dashboard-Feature benötigt matplotlib.\nBitte installieren Sie: pip install matplotlib")
        except Exception as e:
            messagebox.showerror("Fehler", f"Dashboard konnte nicht geöffnet werden:\n{str(e)}")
    
    def run_data_validation(self):
        """Führt Datenvalidierung durch"""
        try:
            from src.utils.validation import BusinessValidator, DataIntegrityChecker
            
            validator = BusinessValidator()
            integrity_checker = DataIntegrityChecker(self.data_manager)
            
            # Validierung durchführen
            issues = integrity_checker.check_integrity()
            
            # Ergebnisse anzeigen
            self.show_validation_results(issues)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Validierung fehlgeschlagen:\n{str(e)}")
    
    def show_validation_results(self, issues: dict):
        """Zeigt Validierungsergebnisse"""
        result_window = ctk.CTkToplevel(self.root)
        result_window.title("Datenvalidierung")
        result_window.geometry("600x400")
        
        # Text-Widget für Ergebnisse
        text_widget = tk.Text(result_window, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Ergebnisse formatieren
        result_text = "DATENVALIDIERUNG ERGEBNISSE\n" + "="*40 + "\n\n"
        
        if issues["critical"]:
            result_text += "❌ KRITISCHE PROBLEME:\n"
            for issue in issues["critical"]:
                result_text += f"  • {issue}\n"
            result_text += "\n"
        
        if issues["warnings"]:
            result_text += "⚠️ WARNUNGEN:\n"
            for warning in issues["warnings"]:
                result_text += f"  • {warning}\n"
            result_text += "\n"
        
        if not issues["critical"] and not issues["warnings"]:
            result_text += "✅ Keine Probleme gefunden!"
        
        text_widget.insert("1.0", result_text)
        text_widget.config(state="disabled")
        
        # Layout
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def bulk_export(self):
        """Massen-Export von Dokumenten"""
        try:
            from src.utils.pdf_preview import BulkExportManager
            
            # Einfacher Dialog für Massen-Export
            export_dir = filedialog.askdirectory(title="Export-Ordner auswählen")
            if not export_dir:
                return
            
            # Alle Rechnungen exportieren
            invoices = self.data_manager.get_invoices()
            company_data = self.data_manager.get_company_data()
            settings = self.data_manager.get_settings()
            
            bulk_manager = BulkExportManager(company_data, settings.pdf_company_color)
            results = bulk_manager.export_multiple_invoices(invoices, Path(export_dir))
            
            # Ergebnis anzeigen
            message = f"Export abgeschlossen!\n\n"
            message += f"Erfolgreich: {results['success_count']}\n"
            message += f"Fehler: {results['error_count']}\n"
            
            if results['errors']:
                message += f"\nFehler:\n" + "\n".join(results['errors'][:5])
                if len(results['errors']) > 5:
                    message += f"\n... und {len(results['errors']) - 5} weitere"
            
            messagebox.showinfo("Massen-Export", message)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Massen-Export fehlgeschlagen:\n{str(e)}")
    
    def show_about(self):
        """Zeigt Über-Dialog"""
        about_text = """
Rechnungs-Tool v1.0

Ein professionelles Tool zur Erstellung und Verwaltung 
von Rechnungen, Angeboten und Gutschriften.

✅ Deutsche Steuervorschriften konform
✅ PDF-Export mit modernem Design  
✅ Offline-fähige JSON-Datenhaltung
✅ Automatische Backup-Funktionen
✅ Umfassende Datenvalidierung

Entwickelt für kleine und mittelständische Unternehmen.
        """
        messagebox.showinfo("Über Rechnungs-Tool", about_text)

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
                # Theme kann sich geändert haben
                ctk.set_appearance_mode(window.result.theme_mode)
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
