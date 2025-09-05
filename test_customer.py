"""
Test-Skript für Kundenerstellung und -speicherung
"""
import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models import Customer
from src.utils.data_manager import DataManager

def test_customer_creation():
    """Testet die Kundenerstellung"""
    print("🧪 Teste Kundenerstellung...")
    
    # DataManager erstellen
    dm = DataManager()
    
    # Neuen Kunden erstellen
    customer = Customer()
    customer.company_name = "Test GmbH"
    customer.contact_person = "Max Mustermann"
    customer.address_line1 = "Musterstraße 123"
    customer.postal_code = "12345"
    customer.city = "Musterstadt"
    customer.email = "test@example.com"
    customer.phone = "0123456789"
    
    print(f"Kunde erstellt: {customer.to_dict()}")
    
    # Kunde speichern
    saved_customer = dm.add_customer(customer)
    print(f"Kunde gespeichert mit ID: {saved_customer.id}")
    print(f"Kundennummer: {saved_customer.customer_number}")
    
    # Alle Kunden laden
    customers = dm.get_customers()
    print(f"Anzahl Kunden in der Datenbank: {len(customers)}")
    
    for cust in customers:
        print(f"  - {cust.customer_number}: {cust.company_name} ({cust.contact_person})")
    
    # JSON-Datei prüfen
    import json
    with open('data/customers.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        print(f"JSON enthält {len(json_data)} Kunden")
    
    print("✅ Test erfolgreich!")

if __name__ == "__main__":
    test_customer_creation()
