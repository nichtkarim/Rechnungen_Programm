"""
Anwendungseinstellungen-Fenster
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
from typing import Optional

from src.models import AppSettings
from src.utils.theme_manager import theme_manager


class AppSettingsWindow:
    """Anwendungseinstellungen-Fenster"""
    
    def __init__(self, parent, settings: AppSettings):
        self.parent = parent
        self.original_settings = settings
        self.result: Optional[AppSettings] = None
        
        # Kopie für Bearbeitung
        self.settings = AppSettings.from_dict(settings.to_dict())
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Anwendungseinstellungen")
        self.window.geometry("500x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # GUI erstellen
        self.setup_gui()
        self.load_data()
        
        # Zentrierung
        self.center_window()
        
        # Warten auf Schließung
        self.window.wait_window()
    
    def setup_gui(self):
        """Erstellt die GUI-Elemente"""
        # Main container mit Pack-Layout
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollable Frame für Inhalte
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Grid-Konfiguration
        self.scrollable_frame.columnconfigure(1, weight=1)
        
        # UI-Einstellungen
        self.create_ui_section()
        
        # Nummernkreise
        self.create_numbering_section()
        
        # Standard-Werte
        self.create_defaults_section()
        
        # PDF-Einstellungen
        self.create_pdf_section()
        
        # Buttons
        self.create_buttons()
    
    def create_ui_section(self):
        """Erstellt den UI-Einstellungen-Bereich"""
        self.scrollable_frame.columnconfigure(1, weight=1)
        
        # Überschrift
        ui_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Benutzeroberfläche",
            font=("Arial", 16, "bold")
        )
        ui_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 15))
        
        row = 1
        
        # Theme-Modus
        ctk.CTkLabel(self.scrollable_frame, text="Theme:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.theme_mode_var = ctk.StringVar(value=self.settings.theme_mode)
        theme_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["light", "dark", "system"],
            variable=self.theme_mode_var,
            width=150,
            command=self.on_theme_change  # Live-Preview hinzufügen
        )
        theme_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Fenstergröße
        ctk.CTkLabel(self.scrollable_frame, text="Fenstergröße:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        size_frame = ctk.CTkFrame(self.scrollable_frame)
        size_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.window_width_var = ctk.StringVar(value=str(self.settings.window_width))
        width_entry = ctk.CTkEntry(size_frame, textvariable=self.window_width_var, width=80)
        width_entry.pack(side="left")
        
        ctk.CTkLabel(size_frame, text=" x ").pack(side="left")
        
        self.window_height_var = ctk.StringVar(value=str(self.settings.window_height))
        height_entry = ctk.CTkEntry(size_frame, textvariable=self.window_height_var, width=80)
        height_entry.pack(side="left")
        
        ctk.CTkLabel(size_frame, text=" Pixel").pack(side="left")
        
        self.ui_row_end = row
    
    def create_numbering_section(self):
        """Erstellt den Nummernkreis-Bereich"""
        row = self.ui_row_end + 2
        
        # Überschrift
        numbering_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Nummernkreise",
            font=("Arial", 14, "bold")
        )
        numbering_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Erklärungstext
        info_text = "Verfügbare Platzhalter: {year} = Jahr, {counter:04d} = Zähler mit 4 Stellen"
        ctk.CTkLabel(
            self.scrollable_frame,
            text=info_text,
            font=("Arial", 10),
            text_color="gray"
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Rechnungsformat
        ctk.CTkLabel(self.scrollable_frame, text="Rechnungsformat:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.invoice_number_format_var = ctk.StringVar(value=self.settings.invoice_number_format)
        invoice_format_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.invoice_number_format_var,
            width=200
        )
        invoice_format_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Angebotsformat
        ctk.CTkLabel(self.scrollable_frame, text="Angebotsformat:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.offer_number_format_var = ctk.StringVar(value=self.settings.offer_number_format)
        offer_format_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.offer_number_format_var,
            width=200
        )
        offer_format_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Gutschriftformat
        ctk.CTkLabel(self.scrollable_frame, text="Gutschriftformat:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.credit_note_format_var = ctk.StringVar(value=self.settings.credit_note_format)
        credit_format_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.credit_note_format_var,
            width=200
        )
        credit_format_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Separator
        ctk.CTkLabel(self.scrollable_frame, text="").grid(row=row, column=0, pady=5)
        row += 1
        
        # Aktuelle Zähler
        ctk.CTkLabel(
            self.scrollable_frame,
            text="Aktuelle Zähler:",
            font=("Arial", 12, "bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Rechnungszähler
        ctk.CTkLabel(self.scrollable_frame, text="Nächste Rechnung:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.invoice_counter_var = ctk.StringVar(value=str(self.settings.invoice_counter))
        invoice_counter_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.invoice_counter_var,
            width=100
        )
        invoice_counter_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Angebotszähler
        ctk.CTkLabel(self.scrollable_frame, text="Nächstes Angebot:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.offer_counter_var = ctk.StringVar(value=str(self.settings.offer_counter))
        offer_counter_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.offer_counter_var,
            width=100
        )
        offer_counter_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Gutschriftszähler
        ctk.CTkLabel(self.scrollable_frame, text="Nächste Gutschrift:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.credit_note_counter_var = ctk.StringVar(value=str(self.settings.credit_note_counter))
        credit_counter_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.credit_note_counter_var,
            width=100
        )
        credit_counter_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Kundenzähler
        ctk.CTkLabel(self.scrollable_frame, text="Nächster Kunde:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.customer_counter_var = ctk.StringVar(value=str(self.settings.customer_counter))
        customer_counter_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.customer_counter_var,
            width=100
        )
        customer_counter_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.numbering_row_end = row
    
    def create_defaults_section(self):
        """Erstellt den Standard-Werte-Bereich"""
        row = self.numbering_row_end + 2
        
        # Überschrift
        defaults_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Standard-Werte",
            font=("Arial", 14, "bold")
        )
        defaults_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Zahlungsziel
        ctk.CTkLabel(self.scrollable_frame, text="Zahlungsziel (Tage):").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.default_payment_terms_var = ctk.StringVar(value=str(self.settings.default_payment_terms))
        payment_terms_entry = ctk.CTkEntry(
            self.scrollable_frame,
            textvariable=self.default_payment_terms_var,
            width=100
        )
        payment_terms_entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Standard-Steuersatz
        ctk.CTkLabel(self.scrollable_frame, text="Standard-Steuersatz:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.default_tax_rate_var = ctk.StringVar(value=self.settings.default_tax_rate)
        tax_rate_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["0.00", "0.07", "0.19"],
            variable=self.default_tax_rate_var,
            width=100
        )
        tax_rate_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # Währung
        ctk.CTkLabel(self.scrollable_frame, text="Währung:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.default_currency_var = ctk.StringVar(value=self.settings.default_currency)
        currency_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["EUR", "USD", "CHF", "GBP"],
            variable=self.default_currency_var,
            width=100
        )
        currency_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.defaults_row_end = row
    
    def create_pdf_section(self):
        """Erstellt den PDF-Einstellungen-Bereich"""
        row = self.defaults_row_end + 2
        
        # Überschrift
        pdf_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="PDF-Einstellungen",
            font=("Arial", 14, "bold")
        )
        pdf_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        row += 1
        
        # Firmenfarbe
        ctk.CTkLabel(self.scrollable_frame, text="Firmenfarbe:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        color_frame = ctk.CTkFrame(self.scrollable_frame)
        color_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        self.pdf_company_color_var = ctk.StringVar(value=self.settings.pdf_company_color)
        
        # Farbvorschau
        self.color_preview = ctk.CTkFrame(color_frame, width=30, height=20, fg_color=self.settings.pdf_company_color)
        self.color_preview.pack(side="left", padx=(0, 10))
        
        # Farbcode-Eingabe
        color_entry = ctk.CTkEntry(color_frame, textvariable=self.pdf_company_color_var, width=100)
        color_entry.pack(side="left", padx=(0, 10))
        
        # Farbwähler-Button
        ctk.CTkButton(
            color_frame,
            text="Wählen",
            width=70,
            command=self.choose_color
        ).pack(side="left")
        
        row += 1
        
        # Schriftgröße
        ctk.CTkLabel(self.scrollable_frame, text="Schriftgröße:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.pdf_font_size_var = ctk.StringVar(value=str(self.settings.pdf_font_size))
        font_size_combo = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["8", "9", "10", "11", "12"],
            variable=self.pdf_font_size_var,
            width=100
        )
        font_size_combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        row += 1
        
        # QR-Code für Banking
        ctk.CTkLabel(self.scrollable_frame, text="QR-Code für Banking:").grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        
        self.enable_qr_codes_var = ctk.BooleanVar(value=self.settings.enable_qr_codes)
        qr_code_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="QR-Code in Rechnungen einfügen",
            variable=self.enable_qr_codes_var
        )
        qr_code_checkbox.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        
        # Hilfstext für QR-Code
        help_text = ctk.CTkLabel(
            self.scrollable_frame,
            text="(Ermöglicht Banking-Apps das automatische Scannen der Überweisungsdaten)",
            font=("Arial", 9),
            text_color="gray"
        )
        help_text.grid(row=row+1, column=1, sticky="w", padx=10, pady=(0, 5))
        
        self.pdf_row_end = row + 1
    
    def create_buttons(self):
        """Erstellt die Buttons"""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        
        # Buttons linksbündig
        buttons_left = ctk.CTkFrame(button_frame)
        buttons_left.pack(side="left", padx=10, pady=5)
        
        ctk.CTkButton(
            buttons_left,
            text="Standard zurücksetzen",
            width=150,
            command=self.reset_to_defaults
        ).pack(side="left", padx=5)
        
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
        """Lädt die Einstellungen in die GUI"""
        # Alle Daten sind bereits über die StringVar-Variablen geladen
        pass
    
    def choose_color(self):
        """Öffnet den Farbwähler"""
        color = colorchooser.askcolor(
            initialcolor=self.pdf_company_color_var.get(),
            title="Firmenfarbe wählen"
        )
        
        if color[1]:  # color[1] ist der Hex-Wert
            self.pdf_company_color_var.set(color[1])
            self.color_preview.configure(fg_color=color[1])
    
    def reset_to_defaults(self):
        """Setzt alle Einstellungen auf Standardwerte zurück"""
        if messagebox.askyesno(
            "Standard zurücksetzen",
            "Möchten Sie alle Einstellungen auf die Standardwerte zurücksetzen?\n\n"
            "Achtung: Die aktuellen Zähler werden NICHT zurückgesetzt."
        ):
            default_settings = AppSettings()
            
            # Theme und Fenstergröße beibehalten
            default_settings.theme_mode = self.settings.theme_mode
            default_settings.window_width = self.settings.window_width
            default_settings.window_height = self.settings.window_height
            
            # Zähler beibehalten
            default_settings.invoice_counter = self.settings.invoice_counter
            default_settings.offer_counter = self.settings.offer_counter
            default_settings.credit_note_counter = self.settings.credit_note_counter
            default_settings.customer_counter = self.settings.customer_counter
            
            # Neue Werte in GUI laden
            self.settings = default_settings
            
            # GUI aktualisieren
            self.invoice_number_format_var.set(self.settings.invoice_number_format)
            self.offer_number_format_var.set(self.settings.offer_number_format)
            self.credit_note_format_var.set(self.settings.credit_note_format)
            self.default_payment_terms_var.set(str(self.settings.default_payment_terms))
            self.default_tax_rate_var.set(self.settings.default_tax_rate)
            self.default_currency_var.set(self.settings.default_currency)
            self.pdf_company_color_var.set(self.settings.pdf_company_color)
            self.pdf_font_size_var.set(str(self.settings.pdf_font_size))
            
            # Farbvorschau aktualisieren
            self.color_preview.configure(fg_color=self.settings.pdf_company_color)
    
    def save(self):
        """Speichert die Einstellungen"""
        try:
            # UI-Einstellungen
            self.settings.theme_mode = self.theme_mode_var.get()
            self.settings.window_width = int(self.window_width_var.get())
            self.settings.window_height = int(self.window_height_var.get())
            
            # Nummernkreise
            self.settings.invoice_number_format = self.invoice_number_format_var.get().strip()
            self.settings.offer_number_format = self.offer_number_format_var.get().strip()
            self.settings.credit_note_format = self.credit_note_format_var.get().strip()
            
            # Zähler
            self.settings.invoice_counter = int(self.invoice_counter_var.get())
            self.settings.offer_counter = int(self.offer_counter_var.get())
            self.settings.credit_note_counter = int(self.credit_note_counter_var.get())
            self.settings.customer_counter = int(self.customer_counter_var.get())
            
            # Standard-Werte
            self.settings.default_payment_terms = int(self.default_payment_terms_var.get())
            self.settings.default_tax_rate = self.default_tax_rate_var.get()
            self.settings.default_currency = self.default_currency_var.get()
            
            # PDF-Einstellungen
            self.settings.pdf_company_color = self.pdf_company_color_var.get().strip()
            self.settings.pdf_font_size = int(self.pdf_font_size_var.get())
            self.settings.enable_qr_codes = self.enable_qr_codes_var.get()
            
            # Validierung
            if self.settings.window_width < 800 or self.settings.window_height < 600:
                messagebox.showerror("Fehler", "Fenstergröße muss mindestens 800x600 Pixel betragen.")
                return
            
            if not self.settings.invoice_number_format or "{counter" not in self.settings.invoice_number_format:
                messagebox.showerror("Fehler", "Rechnungsformat muss einen Zähler enthalten (z.B. {counter:04d}).")
                return
            
            if not self.settings.offer_number_format or "{counter" not in self.settings.offer_number_format:
                messagebox.showerror("Fehler", "Angebotsformat muss einen Zähler enthalten (z.B. {counter:04d}).")
                return
            
            if not self.settings.credit_note_format or "{counter" not in self.settings.credit_note_format:
                messagebox.showerror("Fehler", "Gutschriftformat muss einen Zähler enthalten (z.B. {counter:04d}).")
                return
            
            if self.settings.default_payment_terms < 1:
                messagebox.showerror("Fehler", "Zahlungsziel muss mindestens 1 Tag betragen.")
                return
            
            if any(counter < 1 for counter in [
                self.settings.invoice_counter,
                self.settings.offer_counter,
                self.settings.credit_note_counter,
                self.settings.customer_counter
            ]):
                messagebox.showerror("Fehler", "Alle Zähler müssen mindestens 1 betragen.")
                return
            
            # Farbcode validieren
            color = self.settings.pdf_company_color
            if not color.startswith('#') or len(color) != 7:
                messagebox.showerror("Fehler", "Farbcode muss im Format #RRGGBB angegeben werden.")
                return
            
            if self.settings.pdf_font_size < 6 or self.settings.pdf_font_size > 16:
                messagebox.showerror("Fehler", "Schriftgröße muss zwischen 6 und 16 liegen.")
                return
            
            self.result = self.settings
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Fehler", f"Ungültige Zahleneingabe: {str(e)}")
        except Exception as e:
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
    
    def on_theme_change(self, value):
        """Live-Preview beim Ändern des Themes"""
        try:
            # Theme sofort anwenden für Preview
            theme_manager.apply_theme(value, "blue")
            theme_manager.setup_window_theme(self.window)
            print(f"✅ Theme Preview: {value}")
        except Exception as e:
            print(f"❌ Fehler beim Theme-Preview: {e}")
