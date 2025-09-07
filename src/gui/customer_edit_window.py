"""
Bearbeitungsfenster für Kunden
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Optional

from src.models import Customer
from src.utils.data_manager import DataManager
from src.utils.theme_manager import theme_manager


class CustomerEditWindow:
    """Bearbeitungsfenster für Kunden"""
    
    def __init__(self, parent, customer: Customer, data_manager: DataManager):
        self.parent = parent
        self.original_customer = customer
        self.data_manager = data_manager
        self.result: Optional[Customer] = None
        
        # Kopie für Bearbeitung
        self.customer = Customer.from_dict(customer.to_dict())
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Kunde bearbeiten" if customer.id else "Kunde erstellen")
        self.window.geometry("800x900")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # Erscheinungsbild setzen
        self.window.configure(fg_color=("gray95", "gray10"))  # Hell/Dunkel-Theme
        
        # GUI erstellen
        self.setup_gui()
        self.load_data()
        
        # Zentrierung
        self.center_window()
        
        # Warten auf Schließung
        self.window.wait_window()
    
    def setup_gui(self):
        """Erstellt die GUI-Elemente"""
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Scrollable Frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.window)
        self.scrollable_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Grunddaten
        self.create_basic_section()
        
        # Adresse
        self.create_address_section()
        
        # Lieferadresse
        self.create_delivery_section()
        
        # Kontaktdaten
        self.create_contact_section()
        
        # Buttons
        self.create_buttons()
    
    def create_basic_section(self):
        """Erstellt den Grunddaten-Bereich"""
        self.scrollable_frame.columnconfigure(1, weight=1)
        
        # Überschrift
        basic_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Grunddaten",
            font=("Arial", 14, "bold")
        )
        basic_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        row = 1
        
        # Kundennummer
        ctk.CTkLabel(self.scrollable_frame, text="Kundennummer:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.customer_number_var = ctk.StringVar(value=self.customer.customer_number or "")
        customer_number_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.customer_number_var,
            width=200,
            placeholder_text="Wird automatisch vergeben"
        )
        customer_number_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Firmenname
        ctk.CTkLabel(self.scrollable_frame, text="Firma:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.company_name_var = ctk.StringVar(value=self.customer.company_name or "")
        company_name_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.company_name_var,
            width=400,
            placeholder_text="Firmenname eingeben..."
        )
        company_name_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # Kontaktperson
        ctk.CTkLabel(self.scrollable_frame, text="Kontaktperson:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.contact_person_var = ctk.StringVar(value=self.customer.contact_person or "")
        contact_person_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.contact_person_var,
            width=400,
            placeholder_text="Name der Kontaktperson..."
        )
        contact_person_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        self.basic_row_end = row
    
    def create_address_section(self):
        """Erstellt den Adress-Bereich"""
        row = self.basic_row_end + 2
        
        # Überschrift
        address_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Rechnungsadresse",
            font=("Arial", 14, "bold")
        )
        address_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        row += 1
        
        # Adresszeile 1
        ctk.CTkLabel(self.scrollable_frame, text="Straße:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.address_line1_var = ctk.StringVar(value=self.customer.address_line1 or "")
        address_line1_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.address_line1_var,
            width=400,
            placeholder_text="Straße und Hausnummer..."
        )
        address_line1_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # Adresszeile 2
        ctk.CTkLabel(self.scrollable_frame, text="Zusatz:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.address_line2_var = ctk.StringVar(value=self.customer.address_line2 or "")
        address_line2_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.address_line2_var,
            width=400,
            placeholder_text="Adresszusatz (optional)..."
        )
        address_line2_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # PLZ und Ort in einer Zeile
        ctk.CTkLabel(self.scrollable_frame, text="PLZ / Ort:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        plz_ort_frame = ctk.CTkFrame(self.scrollable_frame)
        plz_ort_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        plz_ort_frame.columnconfigure(1, weight=1)
        
        self.postal_code_var = ctk.StringVar(value=self.customer.postal_code or "")
        postal_code_entry = ctk.CTkEntry(
            plz_ort_frame, 
            textvariable=self.postal_code_var, 
            width=100,
            placeholder_text="PLZ"
        )
        postal_code_entry.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        self.city_var = ctk.StringVar(value=self.customer.city or "")
        city_entry = ctk.CTkEntry(
            plz_ort_frame, 
            textvariable=self.city_var, 
            placeholder_text="Stadt/Ort"
        )
        city_entry.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=10)
        
        row += 1
        
        # Land
        ctk.CTkLabel(self.scrollable_frame, text="Land:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.country_var = ctk.StringVar(value=self.customer.country or "Deutschland")
        country_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Deutschland", "Österreich", "Schweiz", "Niederlande", "Belgien", "Frankreich", "Italien"],
            variable=self.country_var,
            width=200
        )
        country_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # USt-IdNr
        ctk.CTkLabel(self.scrollable_frame, text="USt-IdNr.:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.vat_id_var = ctk.StringVar(value=self.customer.vat_id or "")
        vat_id_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.vat_id_var,
            width=200,
            placeholder_text="DE123456789 (optional)"
        )
        vat_id_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.address_row_end = row
    
    def create_delivery_section(self):
        """Erstellt den Lieferadress-Bereich"""
        row = self.address_row_end + 2
        
        # Überschrift mit Checkbox
        delivery_frame = ctk.CTkFrame(self.scrollable_frame)
        delivery_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        
        self.use_delivery_address_var = ctk.BooleanVar(
            value=bool(self.customer.delivery_company or self.customer.delivery_address_line1)
        )
        
        delivery_checkbox = ctk.CTkCheckBox(
            delivery_frame,
            text="Abweichende Lieferadresse",
            variable=self.use_delivery_address_var,
            font=("Arial", 14, "bold"),
            command=self.toggle_delivery_fields
        )
        delivery_checkbox.pack(side="left", padx=10, pady=5)
        
        row += 1
        
        # Lieferadress-Felder
        self.delivery_widgets = []
        
        # Firma
        delivery_company_label = ctk.CTkLabel(self.scrollable_frame, text="Firma:")
        delivery_company_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.delivery_widgets.append(delivery_company_label)
        
        self.delivery_company_var = ctk.StringVar(value=self.customer.delivery_company)
        delivery_company_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.delivery_company_var,
            width=300
        )
        delivery_company_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.delivery_widgets.append(delivery_company_entry)
        
        row += 1
        
        # Straße
        delivery_address1_label = ctk.CTkLabel(self.scrollable_frame, text="Straße:")
        delivery_address1_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.delivery_widgets.append(delivery_address1_label)
        
        self.delivery_address_line1_var = ctk.StringVar(value=self.customer.delivery_address_line1)
        delivery_address1_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.delivery_address_line1_var,
            width=300
        )
        delivery_address1_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.delivery_widgets.append(delivery_address1_entry)
        
        row += 1
        
        # Zusatz
        delivery_address2_label = ctk.CTkLabel(self.scrollable_frame, text="Zusatz:")
        delivery_address2_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.delivery_widgets.append(delivery_address2_label)
        
        self.delivery_address_line2_var = ctk.StringVar(value=self.customer.delivery_address_line2)
        delivery_address2_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.delivery_address_line2_var,
            width=300
        )
        delivery_address2_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.delivery_widgets.append(delivery_address2_entry)
        
        row += 1
        
        # PLZ / Ort
        delivery_plz_ort_label = ctk.CTkLabel(self.scrollable_frame, text="PLZ / Ort:")
        delivery_plz_ort_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.delivery_widgets.append(delivery_plz_ort_label)
        
        delivery_plz_ort_frame = ctk.CTkFrame(self.scrollable_frame)
        delivery_plz_ort_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.delivery_widgets.append(delivery_plz_ort_frame)
        
        self.delivery_postal_code_var = ctk.StringVar(value=self.customer.delivery_postal_code)
        delivery_postal_code_entry = ctk.CTkEntry(
            delivery_plz_ort_frame,
            textvariable=self.delivery_postal_code_var,
            width=80
        )
        delivery_postal_code_entry.pack(side="left", padx=(0, 10))
        
        self.delivery_city_var = ctk.StringVar(value=self.customer.delivery_city)
        delivery_city_entry = ctk.CTkEntry(
            delivery_plz_ort_frame,
            textvariable=self.delivery_city_var,
            width=200
        )
        delivery_city_entry.pack(side="left")
        
        row += 1
        
        # Land
        delivery_country_label = ctk.CTkLabel(self.scrollable_frame, text="Land:")
        delivery_country_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.delivery_widgets.append(delivery_country_label)
        
        self.delivery_country_var = ctk.StringVar(value=self.customer.delivery_country)
        delivery_country_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Deutschland", "Österreich", "Schweiz", "Niederlande", "Belgien", "Frankreich", "Italien"],
            variable=self.delivery_country_var,
            width=200
        )
        delivery_country_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        self.delivery_widgets.append(delivery_country_combo)
        
        self.delivery_row_end = row
        
        # Initial state setzen
        self.toggle_delivery_fields()
    
    def create_contact_section(self):
        """Erstellt den Kontaktdaten-Bereich"""
        row = self.delivery_row_end + 2
        
        # Überschrift
        contact_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Kontaktdaten",
            font=("Arial", 14, "bold")
        )
        contact_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        
        row += 1
        
        # Telefon
        ctk.CTkLabel(self.scrollable_frame, text="Telefon:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.phone_var = ctk.StringVar(value=self.customer.phone or "")
        phone_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.phone_var,
            width=200,
            placeholder_text="+49 123 456789"
        )
        phone_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # E-Mail
        ctk.CTkLabel(self.scrollable_frame, text="E-Mail:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.email_var = ctk.StringVar(value=self.customer.email or "")
        email_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.email_var,
            width=400,
            placeholder_text="kunde@example.com"
        )
        email_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        self.contact_row_end = row
    
    def create_buttons(self):
        """Erstellt die Buttons"""
        button_frame = ctk.CTkFrame(self.window)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Buttons rechtsbündig
        ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            width=100,
            command=self.cancel
        ).pack(side="right", padx=(5, 10), pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Speichern",
            width=100,
            command=self.save
        ).pack(side="right", padx=0, pady=5)
    
    def load_data(self):
        """Lädt die Kundendaten in die GUI"""
        # Alle Daten sind bereits über die StringVar-Variablen geladen
        pass
    
    def toggle_delivery_fields(self):
        """Schaltet die Lieferadress-Felder ein/aus"""
        state = "normal" if self.use_delivery_address_var.get() else "disabled"
        
        for widget in self.delivery_widgets:
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(state=state)
                except:
                    pass  # Manche Widgets unterstützen state nicht
    
    def save(self):
        """Speichert den Kunden"""
        try:
            # Grunddaten
            self.customer.customer_number = self.customer_number_var.get().strip()
            self.customer.company_name = self.company_name_var.get().strip()
            self.customer.contact_person = self.contact_person_var.get().strip()
            
            # Adresse
            self.customer.address_line1 = self.address_line1_var.get().strip()
            self.customer.address_line2 = self.address_line2_var.get().strip()
            self.customer.postal_code = self.postal_code_var.get().strip()
            self.customer.city = self.city_var.get().strip()
            self.customer.country = self.country_var.get().strip()
            self.customer.vat_id = self.vat_id_var.get().strip()
            
            # Lieferadresse (nur wenn aktiviert)
            if self.use_delivery_address_var.get():
                self.customer.delivery_company = self.delivery_company_var.get().strip()
                self.customer.delivery_address_line1 = self.delivery_address_line1_var.get().strip()
                self.customer.delivery_address_line2 = self.delivery_address_line2_var.get().strip()
                self.customer.delivery_postal_code = self.delivery_postal_code_var.get().strip()
                self.customer.delivery_city = self.delivery_city_var.get().strip()
                self.customer.delivery_country = self.delivery_country_var.get().strip()
            else:
                # Lieferadresse löschen
                self.customer.delivery_company = ""
                self.customer.delivery_address_line1 = ""
                self.customer.delivery_address_line2 = ""
                self.customer.delivery_postal_code = ""
                self.customer.delivery_city = ""
                self.customer.delivery_country = "Deutschland"
            
            # Kontaktdaten
            self.customer.phone = self.phone_var.get().strip()
            self.customer.email = self.email_var.get().strip()
            
            # Validierung
            if not self.customer.company_name and not self.customer.contact_person:
                messagebox.showerror("Fehler", "Bitte geben Sie mindestens einen Firmennamen oder eine Kontaktperson ein.")
                return
            
            if self.customer.email and '@' not in self.customer.email:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige E-Mail-Adresse ein.")
                return
            
            # ID vergeben wenn neu
            if not self.customer.id:
                import uuid
                self.customer.id = str(uuid.uuid4())
            
            # Automatische Kundennummer vergeben wenn leer
            if not self.customer.customer_number:
                settings = self.data_manager.get_settings()
                self.customer.customer_number = settings.get_next_customer_number()
                self.data_manager.update_settings(settings)
            
            # Erfolg setzen
            self.result = self.customer
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
            print(f"Fehler beim Speichern des Kunden: {e}")  # Debug output
    
    def cancel(self):
        """Bricht die Bearbeitung ab"""
        self.window.destroy()
    
    def center_window(self):
        """Zentriert das Fenster"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
