"""
Bearbeitungsfenster für Rechnungen/Dokumente
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from datetime import datetime
from decimal import Decimal, InvalidOperation
from tkcalendar import DateEntry

from src.models import Invoice, Customer, InvoicePosition, DocumentType, TaxRate
from src.utils.data_manager import DataManager


class InvoiceEditWindow:
    """Bearbeitungsfenster für Rechnungen"""
    
    def __init__(self, parent, invoice: Invoice, data_manager: DataManager):
        self.parent = parent
        self.original_invoice = invoice
        self.data_manager = data_manager
        self.result: Optional[Invoice] = None
        
        # Kopie der Rechnung für Bearbeitung
        self.invoice = Invoice.from_dict(invoice.to_dict())
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"{self.invoice.document_type.value} bearbeiten")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # GUI erstellen
        self.setup_gui()
        self.load_data()
        
        # Zentrierung
        self.center_window()
        
        # Warten auf Schließung
        self.window.wait_window()
    
    def setup_gui(self):
        """Erstellt die GUI-Elemente"""
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        
        # Header mit Buttons
        self.create_header()
        
        # Hauptbereich mit Notebook
        self.create_main_area()
        
        # Footer mit Speichern/Abbrechen
        self.create_footer()
    
    def create_header(self):
        """Erstellt den Header"""
        header_frame = ctk.CTkFrame(self.window)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Titel
        title_text = f"{self.invoice.document_type.value}"
        if self.invoice.invoice_number:
            title_text += f" {self.invoice.invoice_number}"
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=("Arial", 18, "bold")
        )
        title_label.pack(side="left", padx=10, pady=10)
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(header_frame)
        actions_frame.pack(side="right", padx=10, pady=5)
        
        ctk.CTkButton(
            actions_frame,
            text="Position hinzufügen",
            width=140,
            command=self.add_position
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="Vorschau PDF",
            width=100,
            command=self.preview_pdf
        ).pack(side="left", padx=5)
    
    def create_main_area(self):
        """Erstellt den Hauptbereich"""
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Tab 1: Grunddaten
        self.create_basic_data_tab()
        
        # Tab 2: Positionen
        self.create_positions_tab()
        
        # Tab 3: Texte
        self.create_texts_tab()
        
        # Tab 4: Summen (readonly)
        self.create_totals_tab()
    
    def create_basic_data_tab(self):
        """Erstellt den Grunddaten-Tab"""
        basic_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(basic_frame, text="Grunddaten")
        
        # Scrollable Frame
        canvas = tk.Canvas(basic_frame)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Dokumenttyp und Nummer
        doc_frame = ctk.CTkFrame(scrollable_frame)
        doc_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(doc_frame, text="Dokumenttyp:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.doc_type_var = ctk.StringVar(value=self.invoice.document_type.value)
        doc_type_combo = ctk.CTkComboBox(
            doc_frame,
            values=[dt.value for dt in DocumentType],
            variable=self.doc_type_var,
            width=150,
            command=self.on_document_type_changed
        )
        doc_type_combo.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(doc_frame, text="Nummer:").grid(row=0, column=2, sticky="w", padx=(20, 10), pady=5)
        
        self.invoice_number_var = ctk.StringVar(value=self.invoice.invoice_number)
        invoice_number_entry = ctk.CTkEntry(doc_frame, textvariable=self.invoice_number_var, width=150)
        invoice_number_entry.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # Daten
        date_frame = ctk.CTkFrame(scrollable_frame)
        date_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(date_frame, text="Rechnungsdatum:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.invoice_date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy'
        )
        self.invoice_date_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.invoice_date_entry.set_date(self.invoice.invoice_date.date())
        
        ctk.CTkLabel(date_frame, text="Leistungsdatum:").grid(row=0, column=2, sticky="w", padx=(20, 10), pady=5)
        
        self.service_date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy'
        )
        self.service_date_entry.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        if self.invoice.service_date:
            self.service_date_entry.set_date(self.invoice.service_date.date())
        
        # Kunde
        customer_frame = ctk.CTkFrame(scrollable_frame)
        customer_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(customer_frame, text="Kunde:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Kunde auswählen
        customers = self.data_manager.get_customers()
        customer_values = ["Kein Kunde"] + [cust.get_display_name() for cust in customers]
        
        self.customer_var = ctk.StringVar()
        if self.invoice.customer:
            self.customer_var.set(self.invoice.customer.get_display_name())
        else:
            self.customer_var.set("Kein Kunde")
        
        customer_combo = ctk.CTkComboBox(
            customer_frame,
            values=customer_values,
            variable=self.customer_var,
            width=300,
            command=self.on_customer_changed
        )
        customer_combo.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ctk.CTkButton(
            customer_frame,
            text="Neuer Kunde",
            width=100,
            command=self.create_new_customer
        ).grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        # Zahlungskonditionen
        payment_frame = ctk.CTkFrame(scrollable_frame)
        payment_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(payment_frame, text="Zahlungskonditionen:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(payment_frame, text="Zahlungsziel (Tage):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.payment_terms_var = ctk.StringVar(value=str(self.invoice.payment_terms_days))
        payment_terms_entry = ctk.CTkEntry(payment_frame, textvariable=self.payment_terms_var, width=100)
        payment_terms_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Referenzen
        ref_frame = ctk.CTkFrame(scrollable_frame)
        ref_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ref_frame, text="Referenzen:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(ref_frame, text="Angebotsnummer:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.offer_number_var = ctk.StringVar(value=self.invoice.offer_number)
        offer_number_entry = ctk.CTkEntry(ref_frame, textvariable=self.offer_number_var, width=150)
        offer_number_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Status (nur bei Rechnungen)
        if self.invoice.document_type == DocumentType.RECHNUNG:
            status_frame = ctk.CTkFrame(scrollable_frame)
            status_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(status_frame, text="Status:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
            
            self.is_paid_var = ctk.BooleanVar(value=self.invoice.is_paid)
            paid_checkbox = ctk.CTkCheckBox(status_frame, text="Bezahlt", variable=self.is_paid_var)
            paid_checkbox.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Frame-Größe aktualisieren
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def create_positions_tab(self):
        """Erstellt den Positionen-Tab"""
        positions_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(positions_frame, text="Positionen")
        
        # Toolbar für Positionen
        pos_toolbar = ctk.CTkFrame(positions_frame)
        pos_toolbar.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            pos_toolbar,
            text="Position hinzufügen",
            width=140,
            command=self.add_position
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            pos_toolbar,
            text="Position bearbeiten",
            width=140,
            command=self.edit_selected_position
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            pos_toolbar,
            text="Position löschen",
            width=120,
            command=self.delete_selected_position
        ).pack(side="left", padx=5)
        
        # Positionsliste
        list_frame = ctk.CTkFrame(positions_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview für Positionen
        columns = ("Pos.", "Beschreibung", "Menge", "Einheit", "Preis", "Rabatt", "MwSt", "Gesamt")
        self.positions_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Spalten konfigurieren
        self.positions_tree.heading("Pos.", text="Pos.")
        self.positions_tree.heading("Beschreibung", text="Beschreibung")
        self.positions_tree.heading("Menge", text="Menge")
        self.positions_tree.heading("Einheit", text="Einheit")
        self.positions_tree.heading("Preis", text="Einzelpreis €")
        self.positions_tree.heading("Rabatt", text="Rabatt %")
        self.positions_tree.heading("MwSt", text="MwSt %")
        self.positions_tree.heading("Gesamt", text="Gesamt €")
        
        self.positions_tree.column("Pos.", width=50)
        self.positions_tree.column("Beschreibung", width=300)
        self.positions_tree.column("Menge", width=80, anchor="e")
        self.positions_tree.column("Einheit", width=80)
        self.positions_tree.column("Preis", width=100, anchor="e")
        self.positions_tree.column("Rabatt", width=80, anchor="e")
        self.positions_tree.column("MwSt", width=80, anchor="e")
        self.positions_tree.column("Gesamt", width=100, anchor="e")
        
        # Scrollbar
        pos_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=pos_scrollbar.set)
        
        self.positions_tree.pack(side="left", fill="both", expand=True)
        pos_scrollbar.pack(side="right", fill="y")
        
        # Doppelklick-Handler
        self.positions_tree.bind("<Double-1>", lambda e: self.edit_selected_position())
    
    def create_texts_tab(self):
        """Erstellt den Texte-Tab"""
        texts_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(texts_frame, text="Texte")
        
        # Header-Text
        ctk.CTkLabel(texts_frame, text="Kopftext:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.header_text = ctk.CTkTextbox(texts_frame, height=100)
        self.header_text.pack(fill="x", padx=10, pady=(0, 10))
        self.header_text.insert("1.0", self.invoice.header_text)
        
        # Footer-Text
        ctk.CTkLabel(texts_frame, text="Fußtext:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.footer_text = ctk.CTkTextbox(texts_frame, height=100)
        self.footer_text.pack(fill="x", padx=10, pady=(0, 10))
        self.footer_text.insert("1.0", self.invoice.footer_text)
        
        # Zahlungshinweis
        ctk.CTkLabel(texts_frame, text="Zahlungshinweis:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.payment_info_text = ctk.CTkTextbox(texts_frame, height=80)
        self.payment_info_text.pack(fill="x", padx=10, pady=(0, 10))
        self.payment_info_text.insert("1.0", self.invoice.payment_info_text)
    
    def create_totals_tab(self):
        """Erstellt den Summen-Tab (readonly)"""
        totals_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(totals_frame, text="Summen")
        
        # Summentabelle wird dynamisch erstellt
        self.totals_display_frame = ctk.CTkFrame(totals_frame)
        self.totals_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_totals_display()
    
    def create_footer(self):
        """Erstellt den Footer mit Buttons"""
        footer_frame = ctk.CTkFrame(self.window)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Buttons rechtsbündig
        button_frame = ctk.CTkFrame(footer_frame)
        button_frame.pack(side="right", padx=10, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            width=100,
            command=self.cancel
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Speichern",
            width=100,
            command=self.save
        ).pack(side="left", padx=5)
    
    def load_data(self):
        """Lädt die Daten in die GUI"""
        self.refresh_positions_list()
        self.update_totals_display()
    
    def refresh_positions_list(self):
        """Aktualisiert die Positionsliste"""
        # Alte Einträge löschen
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        # Positionen hinzufügen
        for pos in self.invoice.positions:
            self.positions_tree.insert("", "end", values=(
                pos.position_number,
                pos.description,
                f"{pos.quantity:,.2f}".replace('.', ','),
                pos.unit,
                f"{pos.unit_price:,.2f}".replace('.', ','),
                f"{pos.discount_percent:,.1f}".replace('.', ','),
                f"{pos.tax_rate.value * 100:,.0f}",
                f"{pos.calculate_line_total_net():,.2f}".replace('.', ',')
            ))
    
    def update_totals_display(self):
        """Aktualisiert die Summenanzeige"""
        # Lösche alte Widgets
        for widget in self.totals_display_frame.winfo_children():
            widget.destroy()
        
        # Netto-Summen nach Steuersatz
        net_totals = self.invoice.calculate_net_totals_by_tax_rate()
        tax_totals = self.invoice.calculate_tax_totals_by_rate()
        
        row = 0
        
        # Zwischensumme Netto
        total_net = self.invoice.calculate_total_net()
        ctk.CTkLabel(
            self.totals_display_frame,
            text="Zwischensumme (netto):",
            font=("Arial", 12)
        ).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(
            self.totals_display_frame,
            text=f"{total_net:,.2f} €".replace('.', ','),
            font=("Arial", 12)
        ).grid(row=row, column=1, sticky="e", padx=10, pady=5)
        
        row += 1
        
        # Steueraufschlüsselung
        for tax_rate in sorted(net_totals.keys(), key=lambda x: x.value):
            net_amount = net_totals[tax_rate]
            tax_amount = tax_totals[tax_rate]
            
            if net_amount > 0:
                tax_percent = tax_rate.value * 100
                
                ctk.CTkLabel(
                    self.totals_display_frame,
                    text=f"zzgl. {tax_percent:,.0f}% MwSt. auf {net_amount:,.2f} €:".replace('.', ','),
                    font=("Arial", 12)
                ).grid(row=row, column=0, sticky="w", padx=10, pady=5)
                
                ctk.CTkLabel(
                    self.totals_display_frame,
                    text=f"{tax_amount:,.2f} €".replace('.', ','),
                    font=("Arial", 12)
                ).grid(row=row, column=1, sticky="e", padx=10, pady=5)
                
                row += 1
        
        # Gesamtsumme
        total_gross = self.invoice.calculate_total_gross()
        
        # Leerzeile
        row += 1
        
        ctk.CTkLabel(
            self.totals_display_frame,
            text="Gesamtbetrag:",
            font=("Arial", 14, "bold")
        ).grid(row=row, column=0, sticky="w", padx=10, pady=10)
        
        ctk.CTkLabel(
            self.totals_display_frame,
            text=f"{total_gross:,.2f} €".replace('.', ','),
            font=("Arial", 14, "bold")
        ).grid(row=row, column=1, sticky="e", padx=10, pady=10)
        
        # Spalten konfigurieren
        self.totals_display_frame.grid_columnconfigure(0, weight=1)
        self.totals_display_frame.grid_columnconfigure(1, weight=0)
    
    # Event Handler
    def on_document_type_changed(self, value):
        """Behandelt Änderung des Dokumenttyps"""
        for doc_type in DocumentType:
            if doc_type.value == value:
                self.invoice.document_type = doc_type
                break
    
    def on_customer_changed(self, value):
        """Behandelt Änderung des Kunden"""
        if value == "Kein Kunde":
            self.invoice.customer = None
        else:
            customers = self.data_manager.get_customers()
            for customer in customers:
                if customer.get_display_name() == value:
                    self.invoice.customer = customer
                    break
    
    def create_new_customer(self):
        """Erstellt einen neuen Kunden"""
        from gui.customer_edit_window import CustomerEditWindow
        
        customer = Customer()
        editor = CustomerEditWindow(self.window, customer, self.data_manager)
        
        if editor.result:
            self.data_manager.add_customer(editor.result)
            # Customer-Dropdown aktualisieren
            # TODO: Implementiere Dropdown-Update
    
    def add_position(self):
        """Fügt eine neue Position hinzu"""
        print("🆕 Erstelle neue Position...")
        position = InvoicePosition()
        position.position_number = len(self.invoice.positions) + 1
        print(f"Position Nummer: {position.position_number}")
        
        editor = PositionEditDialog(self.window, position)
        if editor.result:
            print(f"✅ Position erstellt: {editor.result.description}")
            print(f"   Menge: {editor.result.quantity}, Preis: {editor.result.unit_price}")
            self.invoice.positions.append(editor.result)
            self.refresh_positions_list()
            self.update_totals_display()
            print(f"📊 Gesamt Positionen: {len(self.invoice.positions)}")
        else:
            print("❌ Position erstellen abgebrochen")
    
    def edit_selected_position(self):
        """Bearbeitet die ausgewählte Position"""
        selection = self.positions_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie eine Position aus.")
            return
        
        item = self.positions_tree.item(selection[0])
        pos_number = int(item['values'][0])
        
        # Position finden
        position = None
        for pos in self.invoice.positions:
            if pos.position_number == pos_number:
                position = pos
                break
        
        if position:
            editor = PositionEditDialog(self.window, position)
            if editor.result:
                # Position ersetzen
                for i, pos in enumerate(self.invoice.positions):
                    if pos.position_number == pos_number:
                        self.invoice.positions[i] = editor.result
                        break
                
                self.refresh_positions_list()
                self.update_totals_display()
    
    def delete_selected_position(self):
        """Löscht die ausgewählte Position"""
        selection = self.positions_tree.selection()
        if not selection:
            messagebox.showwarning("Auswahl", "Bitte wählen Sie eine Position aus.")
            return
        
        item = self.positions_tree.item(selection[0])
        pos_number = int(item['values'][0])
        
        if messagebox.askyesno("Löschen bestätigen", f"Position {pos_number} wirklich löschen?"):
            # Position entfernen
            self.invoice.positions = [pos for pos in self.invoice.positions if pos.position_number != pos_number]
            
            # Positionsnummern neu vergeben
            for i, pos in enumerate(self.invoice.positions):
                pos.position_number = i + 1
            
            self.refresh_positions_list()
            self.update_totals_display()
    
    def preview_pdf(self):
        """Zeigt eine PDF-Vorschau"""
        # TODO: Implementiere PDF-Vorschau
        messagebox.showinfo("PDF-Vorschau", "PDF-Vorschau wird in einer zukünftigen Version verfügbar sein.")
    
    def save(self):
        """Speichert die Rechnung"""
        try:
            print("💾 Speichere Rechnung...")
            print(f"Positionen vor Speichern: {len(self.invoice.positions)}")
            
            # Daten aus GUI übernehmen
            self.invoice.invoice_number = self.invoice_number_var.get()
            self.invoice.invoice_date = datetime.combine(self.invoice_date_entry.get_date(), datetime.min.time())
            self.invoice.service_date = datetime.combine(self.service_date_entry.get_date(), datetime.min.time())
            
            try:
                self.invoice.payment_terms_days = int(self.payment_terms_var.get())
            except ValueError:
                self.invoice.payment_terms_days = 14
            
            self.invoice.offer_number = self.offer_number_var.get()
            
            if hasattr(self, 'is_paid_var'):
                self.invoice.is_paid = self.is_paid_var.get()
            
            # Texte
            self.invoice.header_text = self.header_text.get("1.0", "end-1c")
            self.invoice.footer_text = self.footer_text.get("1.0", "end-1c")
            self.invoice.payment_info_text = self.payment_info_text.get("1.0", "end-1c")
            
            # Validierung
            if not self.invoice.invoice_number.strip():
                messagebox.showerror("Fehler", "Bitte geben Sie eine Rechnungsnummer ein.")
                return
            
            if not self.invoice.positions:
                messagebox.showerror("Fehler", "Bitte fügen Sie mindestens eine Position hinzu.")
                return
            
            print(f"✅ Rechnung validiert mit {len(self.invoice.positions)} Positionen")
            for i, pos in enumerate(self.invoice.positions):
                print(f"  Position {i+1}: {pos.description} - {pos.quantity} x {pos.unit_price}")
            
            self.result = self.invoice
            self.window.destroy()
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Rechnung: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def cancel(self):
        """Bricht die Bearbeitung ab"""
        self.window.destroy()
    
    def center_window(self):
        """Zentriert das Fenster"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")


class PositionEditDialog:
    """Dialog zur Bearbeitung einer Position"""
    
    def __init__(self, parent, position: InvoicePosition):
        self.parent = parent
        self.original_position = position
        self.result: Optional[InvoicePosition] = None
        
        # Kopie für Bearbeitung
        self.position = InvoicePosition.from_dict(position.to_dict())
        
        # Dialog erstellen
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Position bearbeiten")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_gui()
        self.load_data()
        self.center_dialog()
        
        # Warten auf Schließung des Dialogs
        self.dialog.wait_window()
    
    def setup_gui(self):
        """Erstellt die GUI"""
        self.dialog.columnconfigure(1, weight=1)
        
        # Positionsnummer
        ctk.CTkLabel(self.dialog, text="Position:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.pos_number_var = ctk.StringVar(value=str(self.position.position_number))
        pos_number_entry = ctk.CTkEntry(self.dialog, textvariable=self.pos_number_var, width=100)
        pos_number_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Beschreibung
        ctk.CTkLabel(self.dialog, text="Beschreibung:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.description_text = ctk.CTkTextbox(self.dialog, height=80)
        self.description_text.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # Menge
        ctk.CTkLabel(self.dialog, text="Menge:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.quantity_var = ctk.StringVar(value=f"{self.position.quantity:,.2f}".replace('.', ',') if self.position.quantity > 0 else "1,00")
        quantity_entry = ctk.CTkEntry(self.dialog, textvariable=self.quantity_var, width=150, placeholder_text="1,00")
        quantity_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Einheit
        ctk.CTkLabel(self.dialog, text="Einheit:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        self.unit_var = ctk.StringVar(value=self.position.unit or "Stk.")
        unit_combo = ctk.CTkComboBox(
            self.dialog,
            values=["Stk.", "h", "Tag", "Pkt.", "m", "m²", "m³", "kg", "l"],
            variable=self.unit_var,
            width=150
        )
        unit_combo.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        # Einzelpreis
        ctk.CTkLabel(self.dialog, text="Einzelpreis €:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        
        self.unit_price_var = ctk.StringVar(value=f"{self.position.unit_price:,.2f}".replace('.', ',') if self.position.unit_price > 0 else "0,00")
        unit_price_entry = ctk.CTkEntry(self.dialog, textvariable=self.unit_price_var, width=150, placeholder_text="0,00")
        unit_price_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # Rabatt
        ctk.CTkLabel(self.dialog, text="Rabatt %:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        
        self.discount_var = ctk.StringVar(value=f"{self.position.discount_percent:,.1f}".replace('.', ',') if self.position.discount_percent > 0 else "0,0")
        discount_entry = ctk.CTkEntry(self.dialog, textvariable=self.discount_var, width=150, placeholder_text="0,0")
        discount_entry.grid(row=5, column=1, sticky="w", padx=10, pady=5)
        
        # Steuersatz
        ctk.CTkLabel(self.dialog, text="MwSt. Satz:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        
        tax_values = ["0%", "7%", "19%"]
        self.tax_rate_var = ctk.StringVar(value=f"{self.position.tax_rate.value * 100:,.0f}%")
        tax_combo = ctk.CTkComboBox(
            self.dialog,
            values=tax_values,
            variable=self.tax_rate_var,
            width=150
        )
        tax_combo.grid(row=6, column=1, sticky="w", padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            width=100,
            command=self.cancel
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="OK",
            width=100,
            command=self.save
        ).pack(side="right", padx=5)
    
    def load_data(self):
        """Lädt die Daten"""
        self.description_text.insert("1.0", self.position.description or "")
        
        # Default-Werte setzen falls leer
        if not self.quantity_var.get() or self.quantity_var.get() == "0,00":
            self.quantity_var.set("1,00")
        
        if not self.unit_price_var.get() or self.unit_price_var.get() == "0,00":
            self.unit_price_var.set("0,00")
            
        if not self.discount_var.get():
            self.discount_var.set("0,0")
            
        if not self.unit_var.get():
            self.unit_var.set("Stk.")
    
    def save(self):
        """Speichert die Position"""
        try:
            print("💾 Speichere Position...")
            
            # Daten übernehmen
            self.position.position_number = int(self.pos_number_var.get())
            self.position.description = self.description_text.get("1.0", "end-1c")
            
            # Dezimalwerte parsen (mit deutscher Formatierung)
            quantity_str = self.quantity_var.get().replace(',', '.')
            self.position.quantity = Decimal(quantity_str)
            
            unit_price_str = self.unit_price_var.get().replace(',', '.')
            self.position.unit_price = Decimal(unit_price_str)
            
            discount_str = self.discount_var.get().replace(',', '.')
            self.position.discount_percent = Decimal(discount_str)
            
            self.position.unit = self.unit_var.get()
            
            # Steuersatz
            tax_str = self.tax_rate_var.get().replace('%', '')
            tax_value = Decimal(tax_str) / 100
            
            for rate in TaxRate:
                if rate.value == tax_value:
                    self.position.tax_rate = rate
                    break
            
            print(f"Position Daten: {self.position.description}, {self.position.quantity}, {self.position.unit_price}")
            
            # Validierung
            if not self.position.description.strip():
                messagebox.showerror("Fehler", "Bitte geben Sie eine Beschreibung ein.")
                return
            
            if self.position.quantity <= 0:
                messagebox.showerror("Fehler", "Die Menge muss größer als 0 sein.")
                return
            
            if self.position.unit_price < 0:
                messagebox.showerror("Fehler", "Der Einzelpreis darf nicht negativ sein.")
                return
            
            print("✅ Position validiert und gespeichert")
            self.result = self.position
            self.dialog.destroy()
            
        except (ValueError, InvalidOperation) as e:
            print(f"❌ Fehler bei Zahlenkonvertierung: {e}")
            messagebox.showerror("Fehler", f"Ungültige Zahleneingabe: {str(e)}")
        except Exception as e:
            print(f"❌ Allgemeiner Fehler: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def cancel(self):
        """Bricht ab"""
        self.dialog.destroy()
    
    def center_dialog(self):
        """Zentriert den Dialog"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
