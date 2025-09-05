"""
Firmeneinstellungen-Fenster
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional
import os

from src.models import CompanyData


class CompanySettingsWindow:
    """Firmeneinstellungen-Fenster"""
    
    def __init__(self, parent, company_data: CompanyData):
        self.parent = parent
        self.original_company_data = company_data
        self.result: Optional[CompanyData] = None
        
        # Kopie für Bearbeitung
        self.company_data = CompanyData.from_dict(company_data.to_dict())
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Firmeneinstellungen")
        self.window.geometry("600x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # GUI erstellen
        self.setup_gui()
        self.load_data()
        
        # Zentrierung
        self.center_window()
    
    def setup_gui(self):
        """Erstellt die GUI-Elemente"""
        self.window.columnconfigure(1, weight=1)
        
        # Scrollable Frame
        canvas = tk.Canvas(self.window)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        
        # Grunddaten
        self.create_basic_section()
        
        # Adresse
        self.create_address_section()
        
        # Kontakt
        self.create_contact_section()
        
        # Steuerdaten
        self.create_tax_section()
        
        # Bankdaten
        self.create_bank_section()
        
        # Logo
        self.create_logo_section()
        
        # Buttons
        self.create_buttons()
        
        # Frame-Größe aktualisieren
        self.scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def create_basic_section(self):
        """Erstellt den Grunddaten-Bereich"""
        self.scrollable_frame.columnconfigure(1, weight=1)
        
        # Überschrift
        basic_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Firmendaten",
            font=("Arial", 16, "bold")
        )
        basic_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 15))
        
        row = 1
        
        # Firmenname
        ctk.CTkLabel(self.scrollable_frame, text="Firmenname:*").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.name_var = ctk.StringVar(value=self.company_data.name)
        name_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.name_var,
            width=350
        )
        name_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        self.basic_row_end = row
    
    def create_address_section(self):
        """Erstellt den Adress-Bereich"""
        row = self.basic_row_end + 2
        
        # Überschrift
        address_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Adresse",
            font=("Arial", 14, "bold")
        )
        address_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Straße
        ctk.CTkLabel(self.scrollable_frame, text="Straße:*").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.address_line1_var = ctk.StringVar(value=self.company_data.address_line1)
        address_line1_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.address_line1_var,
            width=350
        )
        address_line1_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # Zusatz
        ctk.CTkLabel(self.scrollable_frame, text="Zusatz:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.address_line2_var = ctk.StringVar(value=self.company_data.address_line2)
        address_line2_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.address_line2_var,
            width=350
        )
        address_line2_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # PLZ und Ort
        ctk.CTkLabel(self.scrollable_frame, text="PLZ / Ort:*").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        plz_ort_frame = ctk.CTkFrame(self.scrollable_frame)
        plz_ort_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        self.postal_code_var = ctk.StringVar(value=self.company_data.postal_code)
        postal_code_entry = ctk.CTkEntry(plz_ort_frame, textvariable=self.postal_code_var, width=80)
        postal_code_entry.pack(side="left", padx=(0, 10))
        
        self.city_var = ctk.StringVar(value=self.company_data.city)
        city_entry = ctk.CTkEntry(plz_ort_frame, textvariable=self.city_var, width=250)
        city_entry.pack(side="left")
        
        row += 1
        
        # Land
        ctk.CTkLabel(self.scrollable_frame, text="Land:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.country_var = ctk.StringVar(value=self.company_data.country)
        country_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Deutschland", "Österreich", "Schweiz"],
            variable=self.country_var,
            width=200
        )
        country_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.address_row_end = row
    
    def create_contact_section(self):
        """Erstellt den Kontakt-Bereich"""
        row = self.address_row_end + 2
        
        # Überschrift
        contact_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Kontaktdaten",
            font=("Arial", 14, "bold")
        )
        contact_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Telefon
        ctk.CTkLabel(self.scrollable_frame, text="Telefon:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.phone_var = ctk.StringVar(value=self.company_data.phone)
        phone_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.phone_var,
            width=200
        )
        phone_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # E-Mail
        ctk.CTkLabel(self.scrollable_frame, text="E-Mail:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.email_var = ctk.StringVar(value=self.company_data.email)
        email_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.email_var,
            width=300
        )
        email_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # Website
        ctk.CTkLabel(self.scrollable_frame, text="Website:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.website_var = ctk.StringVar(value=self.company_data.website)
        website_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.website_var,
            width=300
        )
        website_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        self.contact_row_end = row
    
    def create_tax_section(self):
        """Erstellt den Steuer-Bereich"""
        row = self.contact_row_end + 2
        
        # Überschrift
        tax_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Steuerdaten",
            font=("Arial", 14, "bold")
        )
        tax_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Steuernummer
        ctk.CTkLabel(self.scrollable_frame, text="Steuernummer:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.tax_number_var = ctk.StringVar(value=self.company_data.tax_number)
        tax_number_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.tax_number_var,
            width=200
        )
        tax_number_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # USt-IdNr
        ctk.CTkLabel(self.scrollable_frame, text="USt-IdNr.:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.vat_id_var = ctk.StringVar(value=self.company_data.vat_id)
        vat_id_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.vat_id_var,
            width=200
        )
        vat_id_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Kleinunternehmer
        self.is_small_business_var = ctk.BooleanVar(value=self.company_data.is_small_business)
        small_business_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="Kleinunternehmer (§19 UStG)",
            variable=self.is_small_business_var
        )
        small_business_checkbox.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.tax_row_end = row
    
    def create_bank_section(self):
        """Erstellt den Bank-Bereich"""
        row = self.tax_row_end + 2
        
        # Überschrift
        bank_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Bankverbindung",
            font=("Arial", 14, "bold")
        )
        bank_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Bankname
        ctk.CTkLabel(self.scrollable_frame, text="Bank:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.bank_name_var = ctk.StringVar(value=self.company_data.bank_name)
        bank_name_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.bank_name_var,
            width=300
        )
        bank_name_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # IBAN
        ctk.CTkLabel(self.scrollable_frame, text="IBAN:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.iban_var = ctk.StringVar(value=self.company_data.iban)
        iban_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.iban_var,
            width=350
        )
        iban_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        row += 1
        
        # BIC
        ctk.CTkLabel(self.scrollable_frame, text="BIC:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.bic_var = ctk.StringVar(value=self.company_data.bic)
        bic_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.bic_var,
            width=200
        )
        bic_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.bank_row_end = row
    
    def create_logo_section(self):
        """Erstellt den Logo-Bereich"""
        row = self.bank_row_end + 2
        
        # Überschrift
        logo_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Logo",
            font=("Arial", 14, "bold")
        )
        logo_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Logo-Pfad
        ctk.CTkLabel(self.scrollable_frame, text="Logo-Datei:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        logo_frame = ctk.CTkFrame(self.scrollable_frame)
        logo_frame.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        
        self.logo_path_var = ctk.StringVar(value=self.company_data.logo_path)
        logo_path_entry = ctk.CTkEntry(logo_frame, textvariable=self.logo_path_var, width=250)
        logo_path_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            logo_frame,
            text="Durchsuchen",
            width=100,
            command=self.select_logo_file
        ).pack(side="left")
        
        row += 1
        
        # Info-Text
        info_text = "Unterstützte Formate: PNG, JPG, GIF\nEmpfohlene Größe: 200x100 Pixel"
        ctk.CTkLabel(
            self.scrollable_frame,
            text=info_text,
            font=("Arial", 10),
            text_color="gray"
        ).grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.logo_row_end = row
    
    def create_buttons(self):
        """Erstellt die Buttons"""
        button_frame = ctk.CTkFrame(self.window)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Buttons rechtsbündig
        buttons_right = ctk.CTkFrame(button_frame)
        buttons_right.pack(side="right", padx=10, pady=5)
        
        ctk.CTkButton(
            buttons_right,
            text="Abbrechen",
            width=100,
            command=self.cancel
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_right,
            text="Speichern",
            width=100,
            command=self.save
        ).pack(side="left", padx=5)
    
    def load_data(self):
        """Lädt die Firmendaten in die GUI"""
        # Alle Daten sind bereits über die StringVar-Variablen geladen
        pass
    
    def select_logo_file(self):
        """Öffnet den Datei-Dialog für Logo-Auswahl"""
        file_path = filedialog.askopenfilename(
            title="Logo-Datei auswählen",
            filetypes=[
                ("Bilddateien", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG-Dateien", "*.png"),
                ("JPEG-Dateien", "*.jpg *.jpeg"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if file_path:
            self.logo_path_var.set(file_path)
    
    def save(self):
        """Speichert die Firmendaten"""
        try:
            print("💾 CompanySettingsWindow: Speichere Firmendaten...")
            
            # Grunddaten
            self.company_data.name = self.name_var.get().strip()
            print(f"  Name: '{self.company_data.name}'")
            
            # Adresse
            self.company_data.address_line1 = self.address_line1_var.get().strip()
            self.company_data.address_line2 = self.address_line2_var.get().strip()
            self.company_data.postal_code = self.postal_code_var.get().strip()
            self.company_data.city = self.city_var.get().strip()
            self.company_data.country = self.country_var.get().strip()
            print(f"  Adresse: {self.company_data.address_line1}, {self.company_data.postal_code} {self.company_data.city}")
            
            # Kontakt
            self.company_data.phone = self.phone_var.get().strip()
            self.company_data.email = self.email_var.get().strip()
            self.company_data.website = self.website_var.get().strip()
            
            # Steuerdaten
            self.company_data.tax_number = self.tax_number_var.get().strip()
            self.company_data.vat_id = self.vat_id_var.get().strip()
            self.company_data.is_small_business = self.is_small_business_var.get()
            
            # Bankdaten
            self.company_data.bank_name = self.bank_name_var.get().strip()
            self.company_data.iban = self.iban_var.get().strip().replace(" ", "")
            self.company_data.bic = self.bic_var.get().strip()
            
            # Logo
            logo_path = self.logo_path_var.get().strip()
            if logo_path and os.path.exists(logo_path):
                self.company_data.logo_path = logo_path
            elif logo_path:
                messagebox.showwarning("Warnung", "Logo-Datei nicht gefunden. Pfad wird trotzdem gespeichert.")
                self.company_data.logo_path = logo_path
            else:
                self.company_data.logo_path = ""
            
            # Validierung
            if not self.company_data.name:
                messagebox.showerror("Fehler", "Bitte geben Sie einen Firmennamen ein.")
                return
            
            if not self.company_data.address_line1:
                messagebox.showerror("Fehler", "Bitte geben Sie eine Straße ein.")
                return
            
            if not self.company_data.postal_code or not self.company_data.city:
                messagebox.showerror("Fehler", "Bitte geben Sie PLZ und Ort ein.")
                return
            
            if self.company_data.email and '@' not in self.company_data.email:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige E-Mail-Adresse ein.")
                return
            
            # IBAN-Validierung (einfach)
            if self.company_data.iban:
                iban = self.company_data.iban.replace(" ", "")
                if len(iban) < 15 or not iban[:2].isalpha() or not iban[2:].isdigit():
                    messagebox.showwarning("Warnung", "IBAN scheint ungültig zu sein. Bitte prüfen Sie die Eingabe.")
            
            print("✅ CompanySettingsWindow: Validierung erfolgreich, setze Ergebnis")
            self.result = self.company_data
            print(f"✅ Result gesetzt: {self.result.name}")
            self.window.destroy()
            
        except Exception as e:
            print(f"❌ CompanySettingsWindow: Fehler beim Speichern: {e}")
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
