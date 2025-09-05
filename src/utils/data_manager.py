"""
Datenmanagement für das Rechnungs-Tool
Verwaltet das Laden und Speichern aller Daten in JSON-Dateien
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from src.models import (
    CompanyData, Customer, Invoice, AppSettings,
    DocumentType, TaxRate, InvoicePosition
)


class DataManager:
    """Zentrale Datenverwalungsklasse"""
    
    def __init__(self, data_dir: str = "storage"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Dateipfade
        self.company_file = self.data_dir / "company.json"
        self.customers_file = self.data_dir / "customers.json"
        self.invoices_file = self.data_dir / "invoices.json"
        self.settings_file = self.data_dir / "settings.json"
        
        # Daten-Cache
        self._company_data: Optional[CompanyData] = None
        self._customers: List[Customer] = []
        self._invoices: List[Invoice] = []
        self._settings: Optional[AppSettings] = None
        
        # Automatisches Backup
        try:
            from src.utils.backup_manager import BackupManager
            self.backup_manager = BackupManager()
            # Backup erstellen wenn keins vom heutigen Tag existiert
            self.backup_manager.auto_backup_if_needed()
        except Exception as e:
            print(f"⚠️ Backup-Manager konnte nicht initialisiert werden: {e}")
            self.backup_manager = None
        
        # Lade alle Daten beim Start
        self.load_all_data()
        print(f"📁 DataManager initialisiert mit Datenordner: {self.data_dir.absolute()}")
        print(f"📊 Geladene Daten: {len(self._customers)} Kunden, {len(self._invoices)} Dokumente")
    
    def load_all_data(self):
        """Lädt alle Daten aus den JSON-Dateien"""
        self.load_company_data()
        self.load_customers()
        self.load_invoices()
        self.load_settings()
    
    def save_all_data(self):
        """Speichert alle Daten in die JSON-Dateien"""
        self.save_company_data()
        self.save_customers()
        self.save_invoices()
        self.save_settings()
    
    # Company Data
    def load_company_data(self) -> CompanyData:
        """Lädt die Firmendaten"""
        if self.company_file.exists():
            try:
                print(f"📁 Lade Firmendaten aus: {self.company_file}")
                with open(self.company_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._company_data = CompanyData.from_dict(data)
                print(f"✅ Firmendaten geladen: {self._company_data.name}")
            except Exception as e:
                print(f"❌ Fehler beim Laden der Firmendaten: {e}")
                self._company_data = CompanyData()
        else:
            print(f"📄 Keine Firmendaten-Datei gefunden, erstelle neue: {self.company_file}")
            self._company_data = CompanyData()
        
        return self._company_data
    
    def save_company_data(self):
        """Speichert die Firmendaten"""
        if self._company_data:
            try:
                print(f"💾 Speichere Firmendaten: {self._company_data.name}")
                with open(self.company_file, 'w', encoding='utf-8') as f:
                    json.dump(self._company_data.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"✅ Firmendaten gespeichert in: {self.company_file}")
            except Exception as e:
                print(f"❌ Fehler beim Speichern der Firmendaten: {e}")
        else:
            print("⚠️ Keine Firmendaten zum Speichern vorhanden")
    
    def get_company_data(self) -> CompanyData:
        """Gibt die Firmendaten zurück"""
        if self._company_data is None:
            self.load_company_data()
        return self._company_data or CompanyData()
    
    def update_company_data(self, company_data: CompanyData):
        """Aktualisiert die Firmendaten"""
        print(f"🔄 Aktualisiere Firmendaten: {company_data.name}")
        self._company_data = company_data
        self.save_company_data()
    
    # Customers
    def load_customers(self) -> List[Customer]:
        """Lädt alle Kunden"""
        if self.customers_file.exists():
            try:
                with open(self.customers_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                self._customers = [Customer.from_dict(data) for data in data_list]
            except Exception as e:
                print(f"Fehler beim Laden der Kundendaten: {e}")
                self._customers = []
        else:
            self._customers = []
        
        return self._customers
    
    def save_customers(self):
        """Speichert alle Kunden"""
        try:
            data_list = [customer.to_dict() for customer in self._customers]
            with open(self.customers_file, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Kundendaten: {e}")
    
    def get_customers(self) -> List[Customer]:
        """Gibt alle Kunden zurück"""
        return self._customers.copy()
    
    def add_customer(self, customer: Customer) -> Customer:
        """Fügt einen neuen Kunden hinzu"""
        if not customer.id:
            customer.id = self.generate_customer_id()
        if not customer.customer_number:
            customer.customer_number = self.get_settings().get_next_customer_number()
            self.save_settings()  # Zähler speichern
        
        self._customers.append(customer)
        self.save_customers()
        print(f"✅ Kunde hinzugefügt: {customer.customer_number} - {customer.get_display_name()}")
        return customer
    
    def update_customer(self, customer: Customer):
        """Aktualisiert einen Kunden"""
        for i, existing_customer in enumerate(self._customers):
            if existing_customer.id == customer.id:
                self._customers[i] = customer
                self.save_customers()
                print(f"✅ Kunde aktualisiert: {customer.customer_number} - {customer.get_display_name()}")
                return
        # Kunde nicht gefunden, füge hinzu
        print(f"⚠️ Kunde nicht gefunden, wird neu hinzugefügt: {customer.get_display_name()}")
        self.add_customer(customer)
    
    def delete_customer(self, customer_id: str):
        """Löscht einen Kunden"""
        self._customers = [c for c in self._customers if c.id != customer_id]
        self.save_customers()
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Findet einen Kunden anhand der ID"""
        for customer in self._customers:
            if customer.id == customer_id:
                return customer
        return None
    
    def generate_customer_id(self) -> str:
        """Generiert eine eindeutige Kunden-ID"""
        import uuid
        return str(uuid.uuid4())
    
    # Invoices
    def load_invoices(self) -> List[Invoice]:
        """Lädt alle Rechnungen"""
        if self.invoices_file.exists():
            try:
                with open(self.invoices_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                self._invoices = [Invoice.from_dict(data) for data in data_list]
            except Exception as e:
                print(f"Fehler beim Laden der Rechnungen: {e}")
                self._invoices = []
        else:
            self._invoices = []
        
        return self._invoices
    
    def save_invoices(self):
        """Speichert alle Rechnungen"""
        try:
            data_list = [invoice.to_dict() for invoice in self._invoices]
            with open(self.invoices_file, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Rechnungen: {e}")
    
    def get_invoices(self) -> List[Invoice]:
        """Gibt alle Rechnungen zurück"""
        return self._invoices.copy()
    
    def add_invoice(self, invoice: Invoice) -> Invoice:
        """Fügt eine neue Rechnung hinzu"""
        if not invoice.id:
            invoice.id = self.generate_invoice_id()
        
        # Automatische Nummernvergabe
        if not invoice.invoice_number:
            settings = self.get_settings()
            if invoice.document_type == DocumentType.ANGEBOT:
                invoice.invoice_number = settings.get_next_offer_number()
            elif invoice.document_type == DocumentType.RECHNUNG:
                invoice.invoice_number = settings.get_next_invoice_number()
            elif invoice.document_type == DocumentType.GUTSCHRIFT:
                invoice.invoice_number = settings.get_next_credit_note_number()
            elif invoice.document_type == DocumentType.STORNO:
                invoice.invoice_number = settings.get_next_credit_note_number()
            
            self.save_settings()  # Zähler speichern
        
        self._invoices.append(invoice)
        self.save_invoices()
        return invoice
    
    def update_invoice(self, invoice: Invoice):
        """Aktualisiert eine Rechnung"""
        for i, existing_invoice in enumerate(self._invoices):
            if existing_invoice.id == invoice.id:
                self._invoices[i] = invoice
                self.save_invoices()
                return
        # Rechnung nicht gefunden, füge hinzu
        self.add_invoice(invoice)
    
    def delete_invoice(self, invoice_id: str):
        """Löscht eine Rechnung"""
        self._invoices = [inv for inv in self._invoices if inv.id != invoice_id]
        self.save_invoices()
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Findet eine Rechnung anhand der ID"""
        for invoice in self._invoices:
            if invoice.id == invoice_id:
                return invoice
        return None
    
    def get_invoices_by_customer(self, customer_id: str) -> List[Invoice]:
        """Gibt alle Rechnungen eines Kunden zurück"""
        return [inv for inv in self._invoices if inv.customer and inv.customer.id == customer_id]
    
    def get_invoices_by_type(self, document_type: DocumentType) -> List[Invoice]:
        """Gibt alle Dokumente eines bestimmten Typs zurück"""
        return [inv for inv in self._invoices if inv.document_type == document_type]
    
    def generate_invoice_id(self) -> str:
        """Generiert eine eindeutige Rechnungs-ID"""
        import uuid
        return str(uuid.uuid4())
    
    # Settings
    def load_settings(self) -> AppSettings:
        """Lädt die Anwendungseinstellungen"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._settings = AppSettings.from_dict(data)
            except Exception as e:
                print(f"Fehler beim Laden der Einstellungen: {e}")
                self._settings = AppSettings()
        else:
            self._settings = AppSettings()
        
        return self._settings
    
    def save_settings(self):
        """Speichert die Anwendungseinstellungen"""
        if self._settings:
            try:
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(self._settings.to_dict(), f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Fehler beim Speichern der Einstellungen: {e}")
    
    def get_settings(self) -> AppSettings:
        """Gibt die Anwendungseinstellungen zurück"""
        if self._settings is None:
            self.load_settings()
        return self._settings or AppSettings()
    
    def update_settings(self, settings: AppSettings):
        """Aktualisiert die Anwendungseinstellungen"""
        self._settings = settings
        self.save_settings()
    
    # Hilfsfunktionen
    def export_all_data(self, export_path: str):
        """Exportiert alle Daten in eine JSON-Datei"""
        export_data = {
            "company": self.get_company_data().to_dict(),
            "customers": [customer.to_dict() for customer in self.get_customers()],
            "invoices": [invoice.to_dict() for invoice in self.get_invoices()],
            "settings": self.get_settings().to_dict(),
            "export_date": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def import_all_data(self, import_path: str):
        """Importiert alle Daten aus einer JSON-Datei"""
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        # Importiere Daten
        if "company" in import_data:
            self._company_data = CompanyData.from_dict(import_data["company"])
        
        if "customers" in import_data:
            self._customers = [Customer.from_dict(data) for data in import_data["customers"]]
        
        if "invoices" in import_data:
            self._invoices = [Invoice.from_dict(data) for data in import_data["invoices"]]
        
        if "settings" in import_data:
            self._settings = AppSettings.from_dict(import_data["settings"])
        
        # Speichere alles
        self.save_all_data()
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken über die Daten zurück"""
        invoices = self.get_invoices()
        customers = self.get_customers()
        
        # Grundstatistiken
        stats = {
            "total_customers": len(customers),
            "total_invoices": len(invoices),
            "invoices_by_type": {},
            "total_revenue": 0,
            "unpaid_invoices": 0,
            "unpaid_amount": 0
        }
        
        # Dokumente nach Typ
        for doc_type in DocumentType:
            stats["invoices_by_type"][doc_type.value] = len(
                [inv for inv in invoices if inv.document_type == doc_type]
            )
        
        # Umsatz und offene Posten
        for invoice in invoices:
            if invoice.document_type == DocumentType.RECHNUNG:
                amount = float(invoice.calculate_total_gross())
                stats["total_revenue"] += amount
                
                if not invoice.is_paid:
                    stats["unpaid_invoices"] += 1
                    stats["unpaid_amount"] += amount
        
        return stats
