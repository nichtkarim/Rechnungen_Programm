"""
Debug-Skript für GUI-Testing
"""
import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from src.models import Customer
from src.utils.data_manager import DataManager
from src.gui.customer_edit_window import CustomerEditWindow

def test_customer_gui():
    """Testet das Kunden-GUI"""
    print("🧪 Teste Kunden-GUI...")
    
    # CTk initialisieren
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Test GUI")
    root.geometry("400x300")
    
    # DataManager erstellen
    dm = DataManager()
    
    def test_new_customer():
        print("🆕 Teste neuen Kunden...")
        customer = Customer()
        
        editor = CustomerEditWindow(root, customer, dm)
        if editor.result:
            print(f"✅ Neuer Kunde gespeichert: {editor.result.get_display_name()}")
            print(f"ID: {editor.result.id}")
            print(f"Nummer: {editor.result.customer_number}")
            
            # Speichere in DataManager
            dm.add_customer(editor.result)
            
            # Zeige alle Kunden
            customers = dm.get_customers()
            print(f"📊 Gesamt: {len(customers)} Kunden")
            for c in customers:
                print(f"  - {c.customer_number}: {c.get_display_name()}")
        else:
            print("❌ Kundenerstellung abgebrochen")
    
    def test_edit_customer():
        print("✏️ Teste Kundenbearbeitung...")
        customers = dm.get_customers()
        if customers:
            customer = customers[0]
            print(f"Bearbeite: {customer.get_display_name()}")
            
            editor = CustomerEditWindow(root, customer, dm)
            if editor.result:
                print(f"✅ Kunde aktualisiert: {editor.result.get_display_name()}")
                dm.update_customer(editor.result)
            else:
                print("❌ Bearbeitung abgebrochen")
        else:
            print("❌ Keine Kunden vorhanden")
    
    # Test-Buttons
    ctk.CTkButton(root, text="Neuer Kunde", command=test_new_customer).pack(pady=20)
    ctk.CTkButton(root, text="Kunde bearbeiten", command=test_edit_customer).pack(pady=20)
    
    # Info-Label
    info_label = ctk.CTkLabel(root, text=f"Kunden in DB: {len(dm.get_customers())}")
    info_label.pack(pady=20)
    
    def update_info():
        customers = dm.get_customers()
        info_label.configure(text=f"Kunden in DB: {len(customers)}")
        root.after(1000, update_info)  # Update alle Sekunde
    
    update_info()
    
    root.mainloop()

if __name__ == "__main__":
    test_customer_gui()
