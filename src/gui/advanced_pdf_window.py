"""
Erweiterte PDF-Export-Funktionen
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from src.utils.data_manager import DataManager
from src.utils.pdf_generator import InvoicePDFGenerator
from src.utils.pdf_preview import BulkExportManager
from src.utils.theme_manager import theme_manager


class AdvancedPDFWindow:
    """Fenster für erweiterte PDF-Export-Optionen"""
    
    def __init__(self, parent, data_manager: DataManager):
        self.parent = parent
        self.data_manager = data_manager
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("📄 Erweiterte PDF-Exports")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # Layout erstellen
        self.create_layout()
        
        # Daten laden
        self.load_data()
    
    def create_layout(self):
        """Erstellt das Layout des Fensters"""
        # Hauptcontainer
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="📄 Erweiterte PDF-Export-Optionen",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)
        
        # Tab-System
        self.create_tab_system(main_frame)
        
        # Button-Leiste
        self.create_button_bar(main_frame)
    
    def create_tab_system(self, parent):
        """Erstellt das Tab-System für verschiedene Export-Optionen"""
        # Tab-Frame
        tab_frame = ctk.CTkFrame(parent)
        tab_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Tab-Buttons
        button_frame = ctk.CTkFrame(tab_frame)
        button_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab-Variablen
        self.current_tab = "customer"
        
        # Tab-Buttons erstellen
        self.tab_buttons = {}
        tab_configs = [
            ("customer", "👥 Nach Kunde", self.show_customer_tab),
            ("date", "📅 Nach Datum", self.show_date_tab),
            ("pattern", "🎯 Muster-Export", self.show_pattern_tab),
            ("batch", "📦 Batch-Export", self.show_batch_tab)
        ]
        
        for tab_id, title, command in tab_configs:
            btn = ctk.CTkButton(
                button_frame,
                text=title,
                command=command,
                width=140,
                height=35
            )
            btn.pack(side="left", padx=5, pady=5)
            self.tab_buttons[tab_id] = btn
        
        # Content-Frame
        self.content_frame = ctk.CTkFrame(tab_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs erstellen
        self.create_customer_tab()
        self.create_date_tab()
        self.create_pattern_tab()
        self.create_batch_tab()
        
        # Ersten Tab anzeigen
        self.show_customer_tab()
    
    def create_customer_tab(self):
        """Erstellt den Kunden-Tab"""
        self.customer_tab = ctk.CTkFrame(self.content_frame)
        
        # Titel
        ctk.CTkLabel(
            self.customer_tab,
            text="👥 Export nach Kunde",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # Kunden-Auswahl
        selection_frame = ctk.CTkFrame(self.customer_tab)
        selection_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            selection_frame,
            text="Kunde auswählen:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.customer_var = ctk.StringVar()
        self.customer_combo = ctk.CTkComboBox(
            selection_frame,
            variable=self.customer_var,
            width=400
        )
        self.customer_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Optionen
        options_frame = ctk.CTkFrame(self.customer_tab)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            options_frame,
            text="Export-Optionen:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.customer_include_paid = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Bezahlte Rechnungen einschließen",
            variable=self.customer_include_paid
        ).pack(anchor="w", padx=10, pady=2)
        
        self.customer_include_unpaid = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Unbezahlte Rechnungen einschließen",
            variable=self.customer_include_unpaid
        ).pack(anchor="w", padx=10, pady=2)
        
        self.customer_create_subfolder = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Unterordner für Kunde erstellen",
            variable=self.customer_create_subfolder
        ).pack(anchor="w", padx=10, pady=(2, 10))
        
        # Export-Button
        ctk.CTkButton(
            self.customer_tab,
            text="📁 Verzeichnis wählen und exportieren",
            command=self.export_by_customer,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)
    
    def create_date_tab(self):
        """Erstellt den Datums-Tab"""
        self.date_tab = ctk.CTkFrame(self.content_frame)
        
        # Titel
        ctk.CTkLabel(
            self.date_tab,
            text="📅 Export nach Datumsbereich",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # Datums-Eingabe
        date_frame = ctk.CTkFrame(self.date_tab)
        date_frame.pack(fill="x", padx=20, pady=10)
        
        # Von-Datum
        from_frame = ctk.CTkFrame(date_frame)
        from_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            from_frame,
            text="Von (YYYY-MM-DD):",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.start_date_var = ctk.StringVar()
        self.start_date_entry = ctk.CTkEntry(
            from_frame,
            textvariable=self.start_date_var,
            placeholder_text="2024-01-01",
            width=150
        )
        self.start_date_entry.pack(side="right", padx=10, pady=10)
        
        # Bis-Datum
        to_frame = ctk.CTkFrame(date_frame)
        to_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            to_frame,
            text="Bis (YYYY-MM-DD):",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.end_date_var = ctk.StringVar()
        self.end_date_entry = ctk.CTkEntry(
            to_frame,
            textvariable=self.end_date_var,
            placeholder_text="2024-12-31",
            width=150
        )
        self.end_date_entry.pack(side="right", padx=10, pady=10)
        
        # Schnell-Auswahl
        quick_frame = ctk.CTkFrame(self.date_tab)
        quick_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            quick_frame,
            text="Schnellauswahl:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        quick_buttons_frame = ctk.CTkFrame(quick_frame)
        quick_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Schnell-Buttons
        quick_options = [
            ("Dieser Monat", self.set_current_month),
            ("Letzter Monat", self.set_last_month),
            ("Dieses Jahr", self.set_current_year),
            ("Letztes Jahr", self.set_last_year)
        ]
        
        for text, command in quick_options:
            ctk.CTkButton(
                quick_buttons_frame,
                text=text,
                command=command,
                width=120,
                height=30
            ).pack(side="left", padx=5, pady=5)
        
        # Export-Button
        ctk.CTkButton(
            self.date_tab,
            text="📁 Verzeichnis wählen und exportieren",
            command=self.export_by_date,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)
    
    def create_pattern_tab(self):
        """Erstellt den Muster-Tab"""
        self.pattern_tab = ctk.CTkFrame(self.content_frame)
        
        # Titel
        ctk.CTkLabel(
            self.pattern_tab,
            text="🎯 Export mit Dateinamen-Muster",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # Muster-Eingabe
        pattern_frame = ctk.CTkFrame(self.pattern_tab)
        pattern_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            pattern_frame,
            text="Dateinamen-Muster:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.pattern_var = ctk.StringVar(value="{doc_type}_{number}_{date}")
        self.pattern_entry = ctk.CTkEntry(
            pattern_frame,
            textvariable=self.pattern_var,
            width=400,
            height=35
        )
        self.pattern_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        # Hilfetext
        help_text = ("Verfügbare Platzhalter:\n"
                    "• {doc_type} - Dokumenttyp (Rechnung, Angebot, etc.)\n"
                    "• {number} - Rechnungsnummer\n"
                    "• {date} - Rechnungsdatum (YYYY-MM-DD)\n"
                    "• {customer} - Kundenname\n"
                    "• {year} - Jahr\n"
                    "• {month} - Monat")
        
        ctk.CTkLabel(
            pattern_frame,
            text=help_text,
            font=ctk.CTkFont(size=10),
            justify="left"
        ).pack(anchor="w", padx=10, pady=(5, 10))
        
        # Vorschau
        preview_frame = ctk.CTkFrame(self.pattern_tab)
        preview_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            preview_frame,
            text="Vorschau:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Rechnung_R2024-001_2024-09-05.pdf",
            font=ctk.CTkFont(family="Courier")
        )
        self.preview_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Pattern aktualisieren bei Eingabe
        self.pattern_entry.bind("<KeyRelease>", self.update_pattern_preview)
        
        # Export-Button
        ctk.CTkButton(
            self.pattern_tab,
            text="📁 Verzeichnis wählen und exportieren",
            command=self.export_with_pattern,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)
    
    def create_batch_tab(self):
        """Erstellt den Batch-Tab"""
        self.batch_tab = ctk.CTkFrame(self.content_frame)
        
        # Titel
        ctk.CTkLabel(
            self.batch_tab,
            text="📦 Batch-Export mit erweiterten Optionen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))
        
        # Filter-Optionen
        filter_frame = ctk.CTkFrame(self.batch_tab)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filter-Optionen:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Dokumenttyp-Filter
        doc_type_frame = ctk.CTkFrame(filter_frame)
        doc_type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            doc_type_frame,
            text="Dokumenttypen:"
        ).pack(side="left", padx=10, pady=5)
        
        self.include_invoices = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            doc_type_frame,
            text="Rechnungen",
            variable=self.include_invoices
        ).pack(side="left", padx=10)
        
        self.include_quotes = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            doc_type_frame,
            text="Angebote",
            variable=self.include_quotes
        ).pack(side="left", padx=10)
        
        self.include_credits = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            doc_type_frame,
            text="Gutschriften",
            variable=self.include_credits
        ).pack(side="left", padx=10)
        
        # Export-Optionen
        export_options_frame = ctk.CTkFrame(self.batch_tab)
        export_options_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            export_options_frame,
            text="Export-Optionen:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.create_date_folders = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            export_options_frame,
            text="Ordner nach Jahr/Monat erstellen",
            variable=self.create_date_folders
        ).pack(anchor="w", padx=10, pady=2)
        
        self.create_customer_folders = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            export_options_frame,
            text="Kundenordner erstellen",
            variable=self.create_customer_folders
        ).pack(anchor="w", padx=10, pady=2)
        
        self.overwrite_existing = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            export_options_frame,
            text="Vorhandene Dateien überschreiben",
            variable=self.overwrite_existing
        ).pack(anchor="w", padx=10, pady=(2, 10))
        
        # Export-Button
        ctk.CTkButton(
            self.batch_tab,
            text="📁 Verzeichnis wählen und exportieren",
            command=self.export_batch,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=20)
    
    def create_button_bar(self, parent):
        """Erstellt die Button-Leiste"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x")
        
        # Schließen-Button
        ctk.CTkButton(
            button_frame,
            text="Schließen",
            command=self.window.destroy,
            width=100
        ).pack(side="right", padx=10, pady=10)
        
        # Hilfe-Button
        ctk.CTkButton(
            button_frame,
            text="❓ Hilfe",
            command=self.show_help,
            width=100
        ).pack(side="right", padx=(0, 5), pady=10)
    
    def load_data(self):
        """Lädt die verfügbaren Daten"""
        # Kunden laden
        customers = self.data_manager.get_customers()
        customer_options = ["Alle Kunden"] + [f"{c.customer_number} - {c.get_display_name()}" for c in customers]
        self.customer_combo.configure(values=customer_options)
        self.customer_combo.set("Alle Kunden")
        
        # Standard-Daten setzen
        current_year = datetime.now().year
        self.start_date_var.set(f"{current_year}-01-01")
        self.end_date_var.set(f"{current_year}-12-31")
    
    # Tab-Navigation
    def show_customer_tab(self):
        """Zeigt den Kunden-Tab"""
        self.hide_all_tabs()
        self.customer_tab.pack(fill="both", expand=True)
        self.update_tab_buttons("customer")
    
    def show_date_tab(self):
        """Zeigt den Datums-Tab"""
        self.hide_all_tabs()
        self.date_tab.pack(fill="both", expand=True)
        self.update_tab_buttons("date")
    
    def show_pattern_tab(self):
        """Zeigt den Muster-Tab"""
        self.hide_all_tabs()
        self.pattern_tab.pack(fill="both", expand=True)
        self.update_tab_buttons("pattern")
        self.update_pattern_preview()
    
    def show_batch_tab(self):
        """Zeigt den Batch-Tab"""
        self.hide_all_tabs()
        self.batch_tab.pack(fill="both", expand=True)
        self.update_tab_buttons("batch")
    
    def hide_all_tabs(self):
        """Versteckt alle Tabs"""
        for tab in [self.customer_tab, self.date_tab, self.pattern_tab, self.batch_tab]:
            tab.pack_forget()
    
    def update_tab_buttons(self, active_tab):
        """Aktualisiert das Aussehen der Tab-Buttons"""
        for tab_id, button in self.tab_buttons.items():
            if tab_id == active_tab:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray65", "gray35"))
    
    # Datums-Schnellauswahl
    def set_current_month(self):
        """Setzt aktuellen Monat"""
        now = datetime.now()
        start = now.replace(day=1)
        # Nächsten Monat, dann einen Tag zurück = letzter Tag des aktuellen Monats
        if now.month == 12:
            end = now.replace(year=now.year+1, month=1, day=1) - timedelta(days=1)
        else:
            end = now.replace(month=now.month+1, day=1) - timedelta(days=1)
        
        self.start_date_var.set(start.strftime("%Y-%m-%d"))
        self.end_date_var.set(end.strftime("%Y-%m-%d"))
    
    def set_last_month(self):
        """Setzt letzten Monat"""
        from datetime import timedelta
        now = datetime.now()
        # Erster Tag des aktuellen Monats
        first_current = now.replace(day=1)
        # Letzter Tag des vorherigen Monats
        last_previous = first_current - timedelta(days=1)
        # Erster Tag des vorherigen Monats
        first_previous = last_previous.replace(day=1)
        
        self.start_date_var.set(first_previous.strftime("%Y-%m-%d"))
        self.end_date_var.set(last_previous.strftime("%Y-%m-%d"))
    
    def set_current_year(self):
        """Setzt aktuelles Jahr"""
        year = datetime.now().year
        self.start_date_var.set(f"{year}-01-01")
        self.end_date_var.set(f"{year}-12-31")
    
    def set_last_year(self):
        """Setzt letztes Jahr"""
        year = datetime.now().year - 1
        self.start_date_var.set(f"{year}-01-01")
        self.end_date_var.set(f"{year}-12-31")
    
    def update_pattern_preview(self, event=None):
        """Aktualisiert die Muster-Vorschau"""
        pattern = self.pattern_var.get()
        
        # Beispiel-Daten
        example_data = {
            'doc_type': 'Rechnung',
            'number': 'R2024-001',
            'date': '2024-09-05',
            'customer': 'Max_Mustermann',
            'year': '2024',
            'month': '09'
        }
        
        try:
            preview = pattern.format(**example_data) + ".pdf"
            self.preview_label.configure(text=preview)
        except KeyError as e:
            self.preview_label.configure(text=f"Fehler: Unbekannter Platzhalter {e}")
        except Exception:
            self.preview_label.configure(text="Ungültiges Muster")
    
    # Export-Funktionen
    def export_by_customer(self):
        """Exportiert Dokumente nach Kunde"""
        try:
            customer_selection = self.customer_var.get()
            if not customer_selection or customer_selection == "Alle Kunden":
                messagebox.showwarning("Warnung", "Bitte wählen Sie einen spezifischen Kunden aus.")
                return
            
            # Export-Verzeichnis wählen
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Kunde wählen")
            if not export_dir:
                return
            
            # Kunde finden
            customer_number = customer_selection.split(" - ")[0]
            customer = None
            for c in self.data_manager.get_customers():
                if c.customer_number == customer_number:
                    customer = c
                    break
            
            if not customer:
                messagebox.showerror("Fehler", "Kunde nicht gefunden.")
                return
            
            # Dokumente filtern
            invoices = self.data_manager.get_invoices_by_customer(customer.id)
            if not invoices:
                messagebox.showinfo("Info", f"Keine Dokumente für Kunde {customer.get_display_name()} gefunden.")
                return
            
            # Nach Zahlungsstatus filtern
            filtered_invoices = []
            for invoice in invoices:
                if (self.customer_include_paid.get() and invoice.is_paid) or \
                   (self.customer_include_unpaid.get() and not invoice.is_paid):
                    filtered_invoices.append(invoice)
            
            if not filtered_invoices:
                messagebox.showinfo("Info", f"Keine Dokumente für Kunde {customer.get_display_name()} gefunden.")
                return
            
            # Export durchführen
            company_data = self.data_manager.get_company_data()
            bulk_exporter = BulkExportManager(company_data)
            
            # Zielverzeichnis
            if self.customer_create_subfolder.get():
                customer_dir = Path(export_dir) / f"{customer.customer_number}_{customer.get_display_name()}"
                customer_dir.mkdir(exist_ok=True)
                target_dir = customer_dir
            else:
                target_dir = Path(export_dir)
            
            exported = bulk_exporter.export_customer_invoices(
                customer.id,
                filtered_invoices,
                target_dir
            )
            
            messagebox.showinfo(
                "Export erfolgreich",
                f"✅ {exported} Dokumente für {customer.get_display_name()} exportiert nach:\n{target_dir}"
            )
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Kunden-Export:\n{str(e)}")
    
    def export_by_date(self):
        """Exportiert Dokumente nach Datumsbereich"""
        try:
            start_date_str = self.start_date_var.get()
            end_date_str = self.end_date_var.get()
            
            if not start_date_str or not end_date_str:
                messagebox.showwarning("Warnung", "Bitte geben Sie Start- und Enddatum ein.")
                return
            
            # Daten parsen
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            if start_date > end_date:
                messagebox.showwarning("Warnung", "Startdatum muss vor dem Enddatum liegen.")
                return
            
            # Export-Verzeichnis wählen
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Datumsbereich wählen")
            if not export_dir:
                return
            
            # Dokumente filtern
            all_invoices = self.data_manager.get_invoices()
            date_filtered_invoices = [
                inv for inv in all_invoices 
                if start_date.date() <= inv.invoice_date <= end_date.date()
            ]
            
            if not date_filtered_invoices:
                messagebox.showinfo(
                    "Info", 
                    f"Keine Dokumente im Zeitraum {start_date_str} bis {end_date_str} gefunden."
                )
                return
            
            # Export durchführen
            company_data = self.data_manager.get_company_data()
            bulk_exporter = BulkExportManager(company_data)
            
            exported = bulk_exporter.export_by_date_range(
                date_filtered_invoices,
                start_date,
                end_date,
                Path(export_dir)
            )
            
            messagebox.showinfo(
                "Export erfolgreich",
                f"✅ {exported} Dokumente für Zeitraum {start_date_str} bis {end_date_str} exportiert."
            )
            
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiges Datumsformat. Bitte verwenden Sie YYYY-MM-DD.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Datumsbereich-Export:\n{str(e)}")
    
    def export_with_pattern(self):
        """Exportiert mit benutzerdefiniertem Dateinamen-Muster"""
        try:
            pattern = self.pattern_var.get().strip()
            if not pattern:
                messagebox.showwarning("Warnung", "Bitte geben Sie ein Dateinamen-Muster ein.")
                return
            
            # Export-Verzeichnis wählen
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Muster-Export wählen")
            if not export_dir:
                return
            
            # Alle Dokumente holen
            invoices = self.data_manager.get_invoices()
            if not invoices:
                messagebox.showinfo("Info", "Keine Dokumente zum Exportieren vorhanden.")
                return
            
            # Export durchführen
            company_data = self.data_manager.get_company_data()
            settings = self.data_manager.get_settings()
            pdf_generator = InvoicePDFGenerator(
                company_data,
                enable_qr_code=settings.enable_qr_codes
            )
            
            exported = 0
            errors = []
            
            for invoice in invoices:
                try:
                    # Dateinamen generieren
                    data = {
                        'doc_type': invoice.document_type.value,
                        'number': invoice.invoice_number,
                        'date': invoice.invoice_date.strftime('%Y-%m-%d'),
                        'customer': invoice.customer.get_display_name().replace(' ', '_') if invoice.customer else 'Unbekannt',
                        'year': invoice.invoice_date.strftime('%Y'),
                        'month': invoice.invoice_date.strftime('%m')
                    }
                    
                    filename = pattern.format(**data) + ".pdf"
                    # Ungültige Zeichen entfernen
                    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
                    filepath = Path(export_dir) / filename
                    
                    if pdf_generator.generate_pdf(invoice, str(filepath)):
                        exported += 1
                    else:
                        errors.append(f"PDF-Generierung für {invoice.invoice_number} fehlgeschlagen")
                        
                except Exception as e:
                    errors.append(f"Fehler bei {invoice.invoice_number}: {str(e)}")
            
            # Ergebnis anzeigen
            if errors:
                error_text = "\n".join(errors[:5])  # Nur erste 5 Fehler anzeigen
                if len(errors) > 5:
                    error_text += f"\n... und {len(errors) - 5} weitere Fehler"
                
                messagebox.showwarning(
                    "Export mit Fehlern",
                    f"✅ {exported} Dokumente exportiert.\n\n❌ Fehler:\n{error_text}"
                )
            else:
                messagebox.showinfo(
                    "Export erfolgreich",
                    f"✅ {exported} Dokumente mit Muster '{pattern}' exportiert."
                )
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Muster-Export:\n{str(e)}")
    
    def export_batch(self):
        """Führt Batch-Export mit erweiterten Optionen durch"""
        try:
            # Export-Verzeichnis wählen
            export_dir = filedialog.askdirectory(title="Export-Verzeichnis für Batch-Export wählen")
            if not export_dir:
                return
            
            # Dokumente nach Typ filtern
            all_invoices = self.data_manager.get_invoices()
            filtered_invoices = []
            
            for invoice in all_invoices:
                include = False
                doc_type = invoice.document_type.value
                
                if doc_type == "Rechnung" and self.include_invoices.get():
                    include = True
                elif doc_type == "Angebot" and self.include_quotes.get():
                    include = True
                elif doc_type == "Gutschrift" and self.include_credits.get():
                    include = True
                
                if include:
                    filtered_invoices.append(invoice)
            
            if not filtered_invoices:
                messagebox.showinfo("Info", "Keine Dokumente mit den gewählten Filtern gefunden.")
                return
            
            # Export durchführen
            company_data = self.data_manager.get_company_data()
            settings = self.data_manager.get_settings()
            pdf_generator = InvoicePDFGenerator(
                company_data,
                enable_qr_code=settings.enable_qr_codes
            )
            
            exported = 0
            errors = []
            
            for invoice in filtered_invoices:
                try:
                    # Zielverzeichnis bestimmen
                    target_dir = Path(export_dir)
                    
                    # Datums-Ordner erstellen
                    if self.create_date_folders.get():
                        year_month = invoice.invoice_date.strftime('%Y/%m')
                        target_dir = target_dir / year_month
                        target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Kunden-Ordner erstellen
                    if self.create_customer_folders.get() and invoice.customer:
                        customer_folder = f"{invoice.customer.customer_number}_{invoice.customer.get_display_name()}"
                        # Ungültige Zeichen entfernen
                        customer_folder = "".join(c for c in customer_folder if c.isalnum() or c in "._- ")
                        target_dir = target_dir / customer_folder
                        target_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Dateiname
                    filename = f"{invoice.document_type.value}_{invoice.invoice_number}.pdf"
                    filename = filename.replace("/", "-").replace("\\", "-")
                    filepath = target_dir / filename
                    
                    # Datei überschreiben?
                    if filepath.exists() and not self.overwrite_existing.get():
                        # Neuen Namen mit Timestamp generieren
                        timestamp = datetime.now().strftime('%H%M%S')
                        name, ext = filename.rsplit('.', 1)
                        filename = f"{name}_{timestamp}.{ext}"
                        filepath = target_dir / filename
                    
                    if pdf_generator.generate_pdf(invoice, str(filepath)):
                        exported += 1
                    else:
                        errors.append(f"PDF-Generierung für {invoice.invoice_number} fehlgeschlagen")
                        
                except Exception as e:
                    errors.append(f"Fehler bei {invoice.invoice_number}: {str(e)}")
            
            # Ergebnis anzeigen
            if errors:
                error_text = "\n".join(errors[:5])  # Nur erste 5 Fehler anzeigen
                if len(errors) > 5:
                    error_text += f"\n... und {len(errors) - 5} weitere Fehler"
                
                messagebox.showwarning(
                    "Export mit Fehlern",
                    f"✅ {exported} Dokumente exportiert.\n\n❌ Fehler:\n{error_text}"
                )
            else:
                messagebox.showinfo(
                    "Export erfolgreich",
                    f"✅ {exported} Dokumente im Batch-Export verarbeitet."
                )
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Batch-Export:\n{str(e)}")
    
    def show_help(self):
        """Zeigt Hilfe-Dialog"""
        help_window = ctk.CTkToplevel(self.window)
        help_window.title("❓ Hilfe - Erweiterte PDF-Exports")
        help_window.geometry("500x400")
        help_window.transient(self.window)
        help_window.grab_set()
        
        # Scrollbarer Text
        scroll_frame = ctk.CTkScrollableFrame(help_window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_text = """
📄 ERWEITERTE PDF-EXPORT HILFE

👥 NACH KUNDE:
• Exportiert alle Dokumente eines bestimmten Kunden
• Option: Bezahlte/Unbezahlte Rechnungen einschließen
• Option: Unterordner für Kunde erstellen

📅 NACH DATUM:
• Exportiert Dokumente in einem Datumsbereich
• Schnellauswahl für gängige Zeiträume
• Format: YYYY-MM-DD (z.B. 2024-01-01)

🎯 MUSTER-EXPORT:
• Benutzerdefinierte Dateinamen-Muster
• Platzhalter:
  - {doc_type}: Dokumenttyp
  - {number}: Rechnungsnummer
  - {date}: Datum (YYYY-MM-DD)
  - {customer}: Kundenname
  - {year}: Jahr
  - {month}: Monat

📦 BATCH-EXPORT:
• Alle Dokumente mit erweiterten Optionen
• Filter nach Dokumenttyp
• Automatische Ordnerstruktur
• Überschreiben-Schutz

💡 TIPPS:
• Große Exports können Zeit benötigen
• Prüfen Sie den verfügbaren Speicherplatz
• Ungültige Zeichen werden automatisch entfernt
• Bei Fehlern werden Details angezeigt
        """
        
        ctk.CTkLabel(
            scroll_frame,
            text=help_text,
            font=ctk.CTkFont(family="Courier", size=11),
            justify="left"
        ).pack(padx=10, pady=10)
        
        ctk.CTkButton(
            help_window,
            text="Schließen",
            command=help_window.destroy
        ).pack(pady=10)
