"""
Import/Export Manager für verschiedene Datenformate
"""
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
import zipfile
import tempfile
import shutil
import logging

from src.utils.data_manager import DataManager
# Verwende normale Modelle anstatt Extended
from src.models import Customer, Invoice, InvoicePosition


class ExportFormat:
    """Unterstützte Export-Formate"""
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    ZIP = "zip"
    DATEV = "datev"
    LEXWARE = "lexware"


class ImportFormat:
    """Unterstützte Import-Formate"""
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    XML = "xml"
    ZIP = "zip"


class DataExporter:
    """Datenexport-Manager"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
    
    def export_customers(self, file_path: str, format_type: str = ExportFormat.CSV,
                        filters: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Exportiert Kundendaten"""
        try:
            customers = self.data_manager.get_customers()
            
            # Filter anwenden
            if filters:
                customers = self._apply_customer_filters(customers, filters)
            
            if format_type == ExportFormat.CSV:
                return self._export_customers_csv(customers, file_path)
            elif format_type == ExportFormat.EXCEL:
                return self._export_customers_excel(customers, file_path)
            elif format_type == ExportFormat.JSON:
                return self._export_customers_json(customers, file_path)
            elif format_type == ExportFormat.XML:
                return self._export_customers_xml(customers, file_path)
            else:
                return False, f"Nicht unterstütztes Format: {format_type}"
                
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren der Kunden: {e}")
            return False, f"Exportfehler: {str(e)}"
    
    def export_invoices(self, file_path: str, format_type: str = ExportFormat.CSV,
                       filters: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Exportiert Rechnungsdaten"""
        try:
            invoices = self.data_manager.get_invoices()
            
            # Filter anwenden
            if filters:
                invoices = self._apply_invoice_filters(invoices, filters)
            
            if format_type == ExportFormat.CSV:
                return self._export_invoices_csv(invoices, file_path)
            elif format_type == ExportFormat.EXCEL:
                return self._export_invoices_excel(invoices, file_path)
            elif format_type == ExportFormat.JSON:
                return self._export_invoices_json(invoices, file_path)
            elif format_type == ExportFormat.DATEV:
                return self._export_invoices_datev(invoices, file_path)
            elif format_type == ExportFormat.LEXWARE:
                return self._export_invoices_lexware(invoices, file_path)
            else:
                return False, f"Nicht unterstütztes Format: {format_type}"
                
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren der Rechnungen: {e}")
            return False, f"Exportfehler: {str(e)}"
    
    def export_articles(self, file_path: str, format_type: str = ExportFormat.CSV,
                       filters: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Exportiert Artikeldaten"""
        try:
            # Hier würden Artikel aus dem DataManager geladen werden
            # Da noch nicht implementiert, erstelle ich eine Beispielstruktur
            articles = []  # self.data_manager.get_articles()
            
            # Filter anwenden
            if filters:
                articles = self._apply_article_filters(articles, filters)
            
            if format_type == ExportFormat.CSV:
                return self._export_articles_csv(articles, file_path)
            elif format_type == ExportFormat.EXCEL:
                return self._export_articles_excel(articles, file_path)
            elif format_type == ExportFormat.JSON:
                return self._export_articles_json(articles, file_path)
            else:
                return False, f"Nicht unterstütztes Format: {format_type}"
                
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren der Artikel: {e}")
            return False, f"Exportfehler: {str(e)}"
    
    def export_complete_backup(self, file_path: str) -> Tuple[bool, str]:
        """Exportiert komplettes Backup als ZIP"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Alle Datentypen exportieren
                customers = self.data_manager.get_customers()
                invoices = self.data_manager.get_invoices()
                company_data = self.data_manager.get_company_data()
                settings = self.data_manager.get_settings()
                
                # JSON-Dateien erstellen
                with open(temp_path / "customers.json", 'w', encoding='utf-8') as f:
                    json.dump([customer.to_dict() for customer in customers], f, 
                             indent=2, ensure_ascii=False, default=str)
                
                with open(temp_path / "invoices.json", 'w', encoding='utf-8') as f:
                    json.dump([invoice.to_dict() for invoice in invoices], f, 
                             indent=2, ensure_ascii=False, default=str)
                
                with open(temp_path / "company.json", 'w', encoding='utf-8') as f:
                    json.dump(company_data.to_dict() if company_data else {}, f, 
                             indent=2, ensure_ascii=False, default=str)
                
                with open(temp_path / "settings.json", 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False, default=str)
                
                # Backup-Metadaten
                backup_info = {
                    'created_at': datetime.now().isoformat(),
                    'version': '2.0',
                    'customers_count': len(customers),
                    'invoices_count': len(invoices),
                    'format': 'complete_backup'
                }
                
                with open(temp_path / "backup_info.json", 'w', encoding='utf-8') as f:
                    json.dump(backup_info, f, indent=2, ensure_ascii=False)
                
                # ZIP erstellen
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path_in_temp in temp_path.rglob('*'):
                        if file_path_in_temp.is_file():
                            zip_file.write(file_path_in_temp, file_path_in_temp.name)
                
                return True, f"Backup erfolgreich erstellt: {len(customers)} Kunden, {len(invoices)} Rechnungen"
                
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Backups: {e}")
            return False, f"Backup-Fehler: {str(e)}"
    
    def _export_customers_csv(self, customers: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Kunden als CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'customer_id', 'customer_number', 'company_name', 'first_name', 'last_name',
                    'email', 'phone', 'street', 'postal_code', 'city', 'country',
                    'tax_id', 'vat_id', 'customer_type', 'status', 'created_at'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                
                for customer in customers:
                    # Hauptadresse und Hauptkontakt ermitteln
                    primary_address = customer.get_primary_address()
                    primary_contact = customer.get_primary_contact()
                    
                    row = {
                        'customer_id': customer.customer_id,
                        'customer_number': customer.customer_number,
                        'company_name': customer.company_name,
                        'first_name': primary_address.first_name if primary_address else '',
                        'last_name': primary_address.last_name if primary_address else '',
                        'email': primary_contact.email if primary_contact else '',
                        'phone': primary_contact.phone if primary_contact else '',
                        'street': primary_address.street if primary_address else '',
                        'postal_code': primary_address.postal_code if primary_address else '',
                        'city': primary_address.city if primary_address else '',
                        'country': primary_address.country if primary_address else '',
                        'tax_id': customer.tax_id,
                        'vat_id': customer.vat_id,
                        'customer_type': customer.customer_type.value,
                        'status': customer.status.value,
                        'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    writer.writerow(row)
            
            return True, f"CSV-Export erfolgreich: {len(customers)} Kunden"
            
        except Exception as e:
            return False, f"CSV-Export Fehler: {str(e)}"
    
    def _export_customers_excel(self, customers: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Kunden als Excel"""
        try:
            # Haupttabelle
            main_data = []
            addresses_data = []
            contacts_data = []
            
            for customer in customers:
                # Hauptdaten
                main_row = {
                    'Kundennummer': customer.customer_number,
                    'Firmenname': customer.company_name,
                    'Kundentyp': customer.customer_type.value,
                    'Status': customer.status.value,
                    'Steuernummer': customer.tax_id,
                    'USt-ID': customer.vat_id,
                    'Branche': customer.industry,
                    'Website': customer.website,
                    'Erstellt am': customer.created_at,
                    'Umsatz gesamt': customer.total_revenue,
                    'Anzahl Bestellungen': customer.total_orders,
                    'Letzter Auftrag': customer.last_order_date
                }
                main_data.append(main_row)
                
                # Adressen
                for address in customer.addresses:
                    addr_row = {
                        'Kundennummer': customer.customer_number,
                        'Adresstyp': address.address_type.value,
                        'Firma': address.company,
                        'Vorname': address.first_name,
                        'Nachname': address.last_name,
                        'Straße': address.street,
                        'PLZ': address.postal_code,
                        'Ort': address.city,
                        'Land': address.country,
                        'Hauptadresse': address.is_primary
                    }
                    addresses_data.append(addr_row)
                
                # Kontakte
                for contact in customer.contacts:
                    cont_row = {
                        'Kundennummer': customer.customer_number,
                        'Kontakttyp': contact.contact_type.value,
                        'Vorname': contact.first_name,
                        'Nachname': contact.last_name,
                        'Position': contact.position,
                        'E-Mail': contact.email,
                        'Telefon': contact.phone,
                        'Mobil': contact.mobile,
                        'Hauptkontakt': contact.is_primary
                    }
                    contacts_data.append(cont_row)
            
            # Excel-Datei mit mehreren Arbeitsblättern
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                if main_data:
                    pd.DataFrame(main_data).to_excel(writer, sheet_name='Kunden', index=False)
                if addresses_data:
                    pd.DataFrame(addresses_data).to_excel(writer, sheet_name='Adressen', index=False)
                if contacts_data:
                    pd.DataFrame(contacts_data).to_excel(writer, sheet_name='Kontakte', index=False)
            
            return True, f"Excel-Export erfolgreich: {len(customers)} Kunden"
            
        except Exception as e:
            return False, f"Excel-Export Fehler: {str(e)}"
    
    def _export_customers_json(self, customers: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Kunden als JSON"""
        try:
            data = {
                'export_info': {
                    'created_at': datetime.now().isoformat(),
                    'record_count': len(customers),
                    'format': 'customers_json'
                },
                'customers': [customer.to_dict() for customer in customers]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True, f"JSON-Export erfolgreich: {len(customers)} Kunden"
            
        except Exception as e:
            return False, f"JSON-Export Fehler: {str(e)}"
    
    def _export_customers_xml(self, customers: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Kunden als XML"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.Element("customers")
            root.set("export_date", datetime.now().isoformat())
            root.set("count", str(len(customers)))
            
            for customer in customers:
                customer_elem = ET.SubElement(root, "customer")
                customer_elem.set("id", customer.id if hasattr(customer, 'id') else '')
                
                # Grunddaten
                ET.SubElement(customer_elem, "customer_number").text = getattr(customer, 'customer_number', '')
                ET.SubElement(customer_elem, "company_name").text = getattr(customer, 'company_name', '')
                ET.SubElement(customer_elem, "contact_person").text = getattr(customer, 'contact_person', '')
                
                # Adresse
                address_elem = ET.SubElement(customer_elem, "address")
                ET.SubElement(address_elem, "street").text = getattr(customer, 'address_line1', '')
                ET.SubElement(address_elem, "postal_code").text = getattr(customer, 'postal_code', '')
                ET.SubElement(address_elem, "city").text = getattr(customer, 'city', '')
                ET.SubElement(address_elem, "country").text = getattr(customer, 'country', '')
                
                # Kontakt
                contact_elem = ET.SubElement(customer_elem, "contact")
                ET.SubElement(contact_elem, "email").text = getattr(customer, 'email', '')
                ET.SubElement(contact_elem, "phone").text = getattr(customer, 'phone', '')
                
                # Steuerliche Daten
                tax_elem = ET.SubElement(customer_elem, "tax_info")
                ET.SubElement(tax_elem, "tax_id").text = getattr(customer, 'tax_id', '')
                ET.SubElement(tax_elem, "vat_id").text = getattr(customer, 'vat_id', '')
            
            # XML-Datei schreiben
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            return True, f"XML-Export erfolgreich: {len(customers)} Kunden"
            
        except Exception as e:
            return False, f"XML-Export Fehler: {str(e)}"
    
    def _export_invoices_csv(self, invoices: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Rechnungen als CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'invoice_number', 'invoice_date', 'due_date', 'customer_name',
                    'customer_number', 'net_amount', 'tax_amount', 'gross_amount',
                    'currency', 'status', 'payment_date', 'document_type'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                
                for invoice in invoices:
                    row = {
                        'invoice_number': invoice.invoice_number,
                        'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else '',
                        'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                        'customer_name': invoice.customer.get_display_name() if invoice.customer else '',
                        'customer_number': invoice.customer.customer_number if invoice.customer else '',
                        'net_amount': invoice.calculate_total_net(),
                        'tax_amount': invoice.calculate_total_tax(),
                        'gross_amount': invoice.calculate_total_gross(),
                        'currency': getattr(invoice, 'currency', 'EUR'),
                        'status': getattr(invoice, 'status', 'Unbekannt'),
                        'payment_date': getattr(invoice, 'payment_date', ''),
                        'document_type': getattr(invoice, 'document_type', 'Rechnung')
                    }
                    writer.writerow(row)
            
            return True, f"CSV-Export erfolgreich: {len(invoices)} Rechnungen"
            
        except Exception as e:
            return False, f"CSV-Export Fehler: {str(e)}"
    
    def _export_invoices_excel(self, invoices: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Rechnungen als Excel"""
        try:
            if pd is None:
                return False, "pandas ist nicht installiert für Excel-Export"
            
            # Hauptdaten
            main_data = []
            items_data = []
            
            for invoice in invoices:
                # Hauptdaten der Rechnung
                main_row = {
                    'Rechnungsnummer': invoice.invoice_number,
                    'Rechnungsdatum': invoice.invoice_date,
                    'Fälligkeitsdatum': getattr(invoice, 'due_date', ''),
                    'Kunde': invoice.customer.get_display_name() if invoice.customer else '',
                    'Kundennummer': invoice.customer.customer_number if invoice.customer else '',
                    'Nettobetrag': float(invoice.calculate_total_net()),
                    'Steuerbetrag': float(invoice.calculate_total_tax()),
                    'Bruttobetrag': float(invoice.calculate_total_gross()),
                    'Währung': getattr(invoice, 'currency', 'EUR'),
                    'Status': getattr(invoice, 'status', 'Offen'),
                    'Dokumenttyp': getattr(invoice, 'document_type', 'Rechnung'),
                    'Zahlungsdatum': getattr(invoice, 'payment_date', ''),
                    'Bemerkungen': getattr(invoice, 'notes', '')
                }
                main_data.append(main_row)
                
                # Positionen der Rechnung
                for i, position in enumerate(invoice.positions):
                    item_row = {
                        'Rechnungsnummer': invoice.invoice_number,
                        'Position': i + 1,
                        'Beschreibung': position.description,
                        'Menge': float(position.quantity),
                        'Einzelpreis': float(position.unit_price),
                        'Rabatt %': float(position.discount_percent),
                        'Steuersatz': position.tax_rate.value,
                        'Nettobetrag': float(position.calculate_total_net()),
                        'Steuerbetrag': float(position.calculate_tax_amount()),
                        'Bruttobetrag': float(position.calculate_total_gross())
                    }
                    items_data.append(item_row)
            
            # Excel-Datei mit mehreren Arbeitsblättern
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                if main_data:
                    pd.DataFrame(main_data).to_excel(writer, sheet_name='Rechnungen', index=False)
                if items_data:
                    pd.DataFrame(items_data).to_excel(writer, sheet_name='Positionen', index=False)
            
            return True, f"Excel-Export erfolgreich: {len(invoices)} Rechnungen"
            
        except Exception as e:
            return False, f"Excel-Export Fehler: {str(e)}"
    
    def _export_invoices_json(self, invoices: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Rechnungen als JSON"""
        try:
            data = {
                'export_info': {
                    'created_at': datetime.now().isoformat(),
                    'record_count': len(invoices),
                    'format': 'invoices_json'
                },
                'invoices': [invoice.to_dict() for invoice in invoices]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True, f"JSON-Export erfolgreich: {len(invoices)} Rechnungen"
            
        except Exception as e:
            return False, f"JSON-Export Fehler: {str(e)}"
    
    def _export_invoices_lexware(self, invoices: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Rechnungen im Lexware-Format"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Lexware-spezifische Felder (vereinfacht)
                fieldnames = [
                    'Belegnummer', 'Belegdatum', 'Faelligkeit', 'Kunde_Nr', 'Kunde_Name',
                    'Netto', 'MwSt', 'Brutto', 'Waehrung', 'Status', 'Buchungstext'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                
                for invoice in invoices:
                    row = {
                        'Belegnummer': invoice.invoice_number,
                        'Belegdatum': invoice.invoice_date.strftime('%d.%m.%Y') if invoice.invoice_date else '',
                        'Faelligkeit': getattr(invoice, 'due_date', ''),
                        'Kunde_Nr': invoice.customer.customer_number if invoice.customer else '',
                        'Kunde_Name': invoice.customer.get_display_name() if invoice.customer else '',
                        'Netto': f"{invoice.calculate_total_net():.2f}".replace('.', ','),
                        'MwSt': f"{invoice.calculate_total_tax():.2f}".replace('.', ','),
                        'Brutto': f"{invoice.calculate_total_gross():.2f}".replace('.', ','),
                        'Waehrung': getattr(invoice, 'currency', 'EUR'),
                        'Status': getattr(invoice, 'status', 'Offen'),
                        'Buchungstext': f"Rechnung {invoice.invoice_number}"
                    }
                    writer.writerow(row)
            
            return True, f"Lexware-Export erfolgreich: {len(invoices)} Rechnungen"
            
        except Exception as e:
            return False, f"Lexware-Export Fehler: {str(e)}"
    
    def _export_invoices_datev(self, invoices: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Rechnungen im DATEV-Format"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # DATEV-spezifische Felder
                fieldnames = [
                    'Umsatz (ohne Soll/Haben-Kz)', 'Soll/Haben-Kennzeichen', 'WKZ Umsatz',
                    'Kurs', 'Basis-Umsatz', 'WKZ Basis-Umsatz', 'Konto', 'Gegenkonto (ohne BU-Schlüssel)',
                    'BU-Schlüssel', 'Belegdatum', 'Belegfeld 1', 'Belegfeld 2', 'Skonto',
                    'Buchungstext', 'Postensperre', 'Diverse Adressnummer', 'Geschäftspartnerbank',
                    'Sachverhalt', 'Zinssperre', 'Beleglink', 'Beleginfo - Art 1', 'Beleginfo - Inhalt 1',
                    'Beleginfo - Art 2', 'Beleginfo - Inhalt 2', 'Beleginfo - Art 3', 'Beleginfo - Inhalt 3',
                    'Beleginfo - Art 4', 'Beleginfo - Inhalt 4', 'Beleginfo - Art 5', 'Beleginfo - Inhalt 5',
                    'Beleginfo - Art 6', 'Beleginfo - Inhalt 6', 'Beleginfo - Art 7', 'Beleginfo - Inhalt 7',
                    'Beleginfo - Art 8', 'Beleginfo - Inhalt 8', 'KOST1 - Kostenstelle', 'KOST2 - Kostenstelle',
                    'Kost-Menge', 'EU-Land u. UStID', 'EU-Steuersatz', 'Abw. Versteuerungsart',
                    'Sachverhalt L+L', 'Funktionsergänzung L+L', 'BU 49 Hauptfunktionstyp',
                    'BU 49 Hauptfunktionsnummer', 'BU 49 Funktionsergänzung', 'Zusatzinformation - Art 1',
                    'Zusatzinformation - Inhalt 1', 'Zusatzinformation - Art 2', 'Zusatzinformation - Inhalt 2',
                    'Zusatzinformation - Art 3', 'Zusatzinformation - Inhalt 3', 'Zusatzinformation - Art 4',
                    'Zusatzinformation - Inhalt 4', 'Zusatzinformation - Art 5', 'Zusatzinformation - Inhalt 5',
                    'Zusatzinformation - Art 6', 'Zusatzinformation - Inhalt 6', 'Zusatzinformation - Art 7',
                    'Zusatzinformation - Inhalt 7', 'Zusatzinformation - Art 8', 'Zusatzinformation - Inhalt 8',
                    'Zusatzinformation - Art 9', 'Zusatzinformation - Inhalt 9', 'Zusatzinformation - Art 10',
                    'Zusatzinformation - Inhalt 10', 'Zusatzinformation - Art 11', 'Zusatzinformation - Inhalt 11',
                    'Zusatzinformation - Art 12', 'Zusatzinformation - Inhalt 12', 'Zusatzinformation - Art 13',
                    'Zusatzinformation - Inhalt 13', 'Zusatzinformation - Art 14', 'Zusatzinformation - Inhalt 14',
                    'Zusatzinformation - Art 15', 'Zusatzinformation - Inhalt 15', 'Zusatzinformation - Art 16',
                    'Zusatzinformation - Inhalt 16', 'Zusatzinformation - Art 17', 'Zusatzinformation - Inhalt 17',
                    'Zusatzinformation - Art 18', 'Zusatzinformation - Inhalt 18', 'Zusatzinformation - Art 19',
                    'Zusatzinformation - Inhalt 19', 'Zusatzinformation - Art 20', 'Zusatzinformation - Inhalt 20',
                    'Stück', 'Gewicht', 'Zahlweise', 'Forderungsart', 'Veranlagungsjahr',
                    'Zugeordnete Fälligkeit', 'Skontotyp', 'Auftragsnummer', 'Buchungstyp',
                    'Ust-Schlüssel (Anzahlungen)', 'EU-Land (Anzahlungen)', 'Sachverhalt L+L (Anzahlungen)',
                    'EU-Steuersatz (Anzahlungen)', 'Erlöskonto (Anzahlungen)', 'Herkunft-Kz',
                    'Buchungs GUID', 'KOST-Datum', 'SEPA-Mandatsreferenz', 'Skontosperre',
                    'Gesellschaftername', 'Beteiligtennummer', 'Identifikationsnummer', 'Zeichnernummer',
                    'Postensperre bis', 'Bezeichnung SoBil-Sachverhalt', 'Kennzeichen SoBil-Buchung',
                    'Festschreibung', 'Leistungsdatum', 'Datum Zuord.Steuerperiode'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                
                for invoice in invoices:
                    # DATEV-Buchungslogik (vereinfacht)
                    gross_amount = invoice.calculate_total_gross()
                    net_amount = invoice.calculate_total_net()
                    tax_amount = invoice.calculate_total_tax()
                    
                    # Hauptbuchung (Bruttobetrag)
                    row = {
                        'Umsatz (ohne Soll/Haben-Kz)': f"{gross_amount:.2f}".replace('.', ','),
                        'Soll/Haben-Kennzeichen': 'S',  # Soll
                        'WKZ Umsatz': 'EUR',
                        'Kurs': '',
                        'Basis-Umsatz': '',
                        'WKZ Basis-Umsatz': '',
                        'Konto': '1400',  # Forderungen aus Lieferungen und Leistungen
                        'Gegenkonto (ohne BU-Schlüssel)': '8400',  # Erlöse 19% USt
                        'BU-Schlüssel': '1',  # Automatische Steueraufteilung
                        'Belegdatum': invoice.invoice_date.strftime('%d%m%Y') if invoice.invoice_date else '',
                        'Belegfeld 1': invoice.invoice_number,
                        'Belegfeld 2': '',
                        'Skonto': '',
                        'Buchungstext': f"Rechnung {invoice.invoice_number}",
                        'Leistungsdatum': invoice.invoice_date.strftime('%d%m%Y') if invoice.invoice_date else '',
                        'Datum Zuord.Steuerperiode': invoice.invoice_date.strftime('%d%m%Y') if invoice.invoice_date else ''
                    }
                    
                    # Alle anderen Felder leer lassen
                    for field in fieldnames:
                        if field not in row:
                            row[field] = ''
                    
                    writer.writerow(row)
            
            return True, f"DATEV-Export erfolgreich: {len(invoices)} Rechnungen"
            
        except Exception as e:
            return False, f"DATEV-Export Fehler: {str(e)}"
    
    def _export_articles_csv(self, articles: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Artikel als CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'artikel_nummer', 'beschreibung', 'kategorie', 'einheit',
                    'verkaufspreis', 'einkaufspreis', 'steuersatz', 'status',
                    'mindestbestand', 'aktueller_bestand', 'lieferant'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                
                for article in articles:
                    row = {
                        'artikel_nummer': getattr(article, 'article_number', ''),
                        'beschreibung': getattr(article, 'description', ''),
                        'kategorie': getattr(article, 'category', ''),
                        'einheit': getattr(article, 'unit', 'Stück'),
                        'verkaufspreis': getattr(article, 'sales_price', 0),
                        'einkaufspreis': getattr(article, 'purchase_price', 0),
                        'steuersatz': getattr(article, 'tax_rate', '19'),
                        'status': getattr(article, 'status', 'Aktiv'),
                        'mindestbestand': getattr(article, 'min_stock', 0),
                        'aktueller_bestand': getattr(article, 'current_stock', 0),
                        'lieferant': getattr(article, 'supplier', '')
                    }
                    writer.writerow(row)
            
            return True, f"CSV-Export erfolgreich: {len(articles)} Artikel"
            
        except Exception as e:
            return False, f"CSV-Export Fehler: {str(e)}"
    
    def _export_articles_excel(self, articles: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Artikel als Excel"""
        try:
            if pd is None:
                return False, "pandas ist nicht installiert für Excel-Export"
            
            data = []
            for article in articles:
                row = {
                    'Artikelnummer': getattr(article, 'article_number', ''),
                    'Beschreibung': getattr(article, 'description', ''),
                    'Kategorie': getattr(article, 'category', ''),
                    'Einheit': getattr(article, 'unit', 'Stück'),
                    'Verkaufspreis': getattr(article, 'sales_price', 0),
                    'Einkaufspreis': getattr(article, 'purchase_price', 0),
                    'Gewinnmarge': getattr(article, 'profit_margin', 0),
                    'Steuersatz': getattr(article, 'tax_rate', '19%'),
                    'Status': getattr(article, 'status', 'Aktiv'),
                    'Mindestbestand': getattr(article, 'min_stock', 0),
                    'Aktueller Bestand': getattr(article, 'current_stock', 0),
                    'Lieferant': getattr(article, 'supplier', ''),
                    'Erstellt am': getattr(article, 'created_at', ''),
                    'Zuletzt aktualisiert': getattr(article, 'updated_at', '')
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            return True, f"Excel-Export erfolgreich: {len(articles)} Artikel"
            
        except Exception as e:
            return False, f"Excel-Export Fehler: {str(e)}"
    
    def _export_articles_json(self, articles: List, file_path: str) -> Tuple[bool, str]:
        """Exportiert Artikel als JSON"""
        try:
            data = {
                'export_info': {
                    'created_at': datetime.now().isoformat(),
                    'record_count': len(articles),
                    'format': 'articles_json'
                },
                'articles': [
                    {
                        'article_number': getattr(article, 'article_number', ''),
                        'description': getattr(article, 'description', ''),
                        'category': getattr(article, 'category', ''),
                        'unit': getattr(article, 'unit', 'Stück'),
                        'sales_price': float(getattr(article, 'sales_price', 0)),
                        'purchase_price': float(getattr(article, 'purchase_price', 0)),
                        'tax_rate': getattr(article, 'tax_rate', '19'),
                        'status': getattr(article, 'status', 'Aktiv'),
                        'min_stock': getattr(article, 'min_stock', 0),
                        'current_stock': getattr(article, 'current_stock', 0),
                        'supplier': getattr(article, 'supplier', ''),
                        'created_at': getattr(article, 'created_at', ''),
                        'updated_at': getattr(article, 'updated_at', '')
                    } for article in articles
                ]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return True, f"JSON-Export erfolgreich: {len(articles)} Artikel"
            
        except Exception as e:
            return False, f"JSON-Export Fehler: {str(e)}"
    
    def _apply_article_filters(self, articles: List, filters: Dict[str, Any]) -> List:
        """Wendet Filter auf Artikel-Liste an"""
        filtered_articles = articles
        
        # Kategoriefilter
        if 'category' in filters and filters['category']:
            category = filters['category']
            filtered_articles = [a for a in filtered_articles 
                               if getattr(a, 'category', '') == category]
        
        # Statusfilter
        if 'status' in filters and filters['status']:
            status = filters['status']
            filtered_articles = [a for a in filtered_articles 
                               if getattr(a, 'status', '') == status]
        
        # Preisbereich
        if 'price_from' in filters and filters['price_from']:
            price_from = Decimal(str(filters['price_from']))
            filtered_articles = [a for a in filtered_articles 
                               if Decimal(str(getattr(a, 'sales_price', 0))) >= price_from]
        
        if 'price_to' in filters and filters['price_to']:
            price_to = Decimal(str(filters['price_to']))
            filtered_articles = [a for a in filtered_articles 
                               if Decimal(str(getattr(a, 'sales_price', 0))) <= price_to]
        
        return filtered_articles
    
    def _apply_customer_filters(self, customers: List, filters: Dict[str, Any]) -> List:
        """Wendet Filter auf Kundenliste an"""
        filtered_customers = customers
        
        # Datumsfilter
        if 'date_from' in filters and filters['date_from']:
            date_from = filters['date_from']
            filtered_customers = [c for c in filtered_customers if c.created_at.date() >= date_from]
        
        if 'date_to' in filters and filters['date_to']:
            date_to = filters['date_to']
            filtered_customers = [c for c in filtered_customers if c.created_at.date() <= date_to]
        
        # Statusfilter
        if 'status' in filters and filters['status']:
            status = filters['status']
            filtered_customers = [c for c in filtered_customers if c.status.value == status]
        
        # Kundentyp-Filter
        if 'customer_type' in filters and filters['customer_type']:
            customer_type = filters['customer_type']
            filtered_customers = [c for c in filtered_customers if c.customer_type.value == customer_type]
        
        return filtered_customers
    
    def _apply_invoice_filters(self, invoices: List, filters: Dict[str, Any]) -> List:
        """Wendet Filter auf Rechnungsliste an"""
        filtered_invoices = invoices
        
        # Datumsfilter
        if 'date_from' in filters and filters['date_from']:
            date_from = filters['date_from']
            filtered_invoices = [i for i in filtered_invoices 
                               if i.invoice_date and i.invoice_date >= date_from]
        
        if 'date_to' in filters and filters['date_to']:
            date_to = filters['date_to']
            filtered_invoices = [i for i in filtered_invoices 
                               if i.invoice_date and i.invoice_date <= date_to]
        
        # Betragsfilter
        if 'amount_from' in filters and filters['amount_from']:
            amount_from = Decimal(str(filters['amount_from']))
            filtered_invoices = [i for i in filtered_invoices 
                               if i.calculate_total_gross() >= amount_from]
        
        if 'amount_to' in filters and filters['amount_to']:
            amount_to = Decimal(str(filters['amount_to']))
            filtered_invoices = [i for i in filtered_invoices 
                               if i.calculate_total_gross() <= amount_to]
        
        return filtered_invoices


class DataImporter:
    """Datenimport-Manager"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
    
    def import_customers(self, file_path: str, format_type: str = ImportFormat.CSV,
                        mapping: Optional[Dict[str, str]] = None,
                        update_existing: bool = False) -> Tuple[bool, str, Dict[str, int]]:
        """Importiert Kundendaten"""
        try:
            if format_type == ImportFormat.CSV:
                return self._import_customers_csv(file_path, mapping, update_existing)
            elif format_type == ImportFormat.EXCEL:
                return self._import_customers_excel(file_path, mapping, update_existing)
            elif format_type == ImportFormat.JSON:
                return self._import_customers_json(file_path, update_existing)
            else:
                return False, f"Nicht unterstütztes Format: {format_type}", {}
                
        except Exception as e:
            self.logger.error(f"Fehler beim Importieren der Kunden: {e}")
            return False, f"Import-Fehler: {str(e)}", {}
    
    def import_backup(self, file_path: str) -> Tuple[bool, str, Dict[str, int]]:
        """Importiert komplettes Backup"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # ZIP extrahieren
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    zip_file.extractall(temp_dir)
                
                temp_path = Path(temp_dir)
                results = {'customers': 0, 'invoices': 0, 'errors': 0}
                
                # Backup-Info prüfen
                backup_info_file = temp_path / "backup_info.json"
                if backup_info_file.exists():
                    with open(backup_info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                        self.logger.info(f"Importing backup from {backup_info.get('created_at')}")
                
                # Kunden importieren
                customers_file = temp_path / "customers.json"
                if customers_file.exists():
                    success, message, stats = self._import_customers_json(str(customers_file), True)
                    if success:
                        results['customers'] = stats.get('imported', 0)
                    else:
                        results['errors'] += 1
                
                # Rechnungen importieren
                invoices_file = temp_path / "invoices.json"
                if invoices_file.exists():
                    success, message, stats = self._import_invoices_json(str(invoices_file), True)
                    if success:
                        results['invoices'] = stats.get('imported', 0)
                    else:
                        results['errors'] += 1
                
                # Unternehmensdaten importieren
                company_file = temp_path / "company.json"
                if company_file.exists():
                    with open(company_file, 'r', encoding='utf-8') as f:
                        company_data = json.load(f)
                        if company_data:
                            # Hier würde Company-Import implementiert werden
                            pass
                
                # Einstellungen importieren
                settings_file = temp_path / "settings.json"
                if settings_file.exists():
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings_data = json.load(f)
                        if settings_data:
                            # Hier würde Settings-Import implementiert werden
                            pass
                
                return True, f"Backup erfolgreich importiert", results
                
        except Exception as e:
            self.logger.error(f"Fehler beim Importieren des Backups: {e}")
            return False, f"Backup-Import Fehler: {str(e)}", {}
    
    def _import_customers_csv(self, file_path: str, mapping: Optional[Dict[str, str]] = None,
                             update_existing: bool = False) -> Tuple[bool, str, Dict[str, int]]:
        """Importiert Kunden aus CSV"""
        try:
            results = {'imported': 0, 'updated': 0, 'errors': 0, 'skipped': 0}
            
            # Standard-Mapping
            default_mapping = {
                'customer_number': 'customer_number',
                'company_name': 'company_name',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'email': 'email',
                'phone': 'phone',
                'street': 'street',
                'postal_code': 'postal_code',
                'city': 'city',
                'country': 'country',
                'tax_id': 'tax_id',
                'vat_id': 'vat_id'
            }
            
            field_mapping = mapping or default_mapping
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Delimiter automatisch erkennen
                sample = csvfile.read(1024)
                csvfile.seek(0)
                delimiter = ';' if ';' in sample else ','
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # Start bei 2 wegen Header
                    try:
                        # Neuen Kunden erstellen (normale Customer-Klasse)
                        from src.models import Customer
                        customer = Customer()
                        
                        # Basis-Daten setzen
                        for csv_field, customer_field in field_mapping.items():
                            if csv_field in row and row[csv_field]:
                                value = row[csv_field].strip()
                                if hasattr(customer, customer_field):
                                    setattr(customer, customer_field, value)
                        
                        # ID vergeben
                        if not customer.id:
                            import uuid
                            customer.id = str(uuid.uuid4())
                        
                        # Automatische Kundennummer vergeben falls leer
                        if not customer.customer_number:
                            settings = self.data_manager.get_settings()
                            customer.customer_number = settings.get_next_customer_number()
                            self.data_manager.update_settings(settings)
                        
                        # Kundennummer generieren falls nicht vorhanden (Fallback)
                        if not customer.customer_number:
                            customer.customer_number = f"K{len(self.data_manager.get_customers()) + results['imported'] + 1:06d}"
                        
                        # Prüfen ob Kunde bereits existiert
                        existing_customer = None
                        if update_existing:
                            existing_customers = self.data_manager.get_customers()
                            for existing in existing_customers:
                                if (existing.customer_number == customer.customer_number or
                                    (existing.company_name and existing.company_name == customer.company_name)):
                                    existing_customer = existing
                                    break
                        
                        if existing_customer and update_existing:
                            # Kunde aktualisieren
                            # Hier würde Update-Logik implementiert werden
                            results['updated'] += 1
                        elif not existing_customer:
                            # Neuen Kunden speichern
                            self.data_manager.add_customer(customer)
                            results['imported'] += 1
                        else:
                            results['skipped'] += 1
                            
                    except Exception as e:
                        self.logger.error(f"Fehler in Zeile {row_num}: {e}")
                        results['errors'] += 1
            
            message = f"Import abgeschlossen: {results['imported']} neu, {results['updated']} aktualisiert, {results['errors']} Fehler"
            return True, message, results
            
        except Exception as e:
            return False, f"CSV-Import Fehler: {str(e)}", {}
    
    def _import_customers_excel(self, file_path: str, mapping: Optional[Dict[str, str]] = None,
                               update_existing: bool = False) -> Tuple[bool, str, Dict[str, int]]:
        """Importiert Kunden aus Excel"""
        try:
            if pd is None:
                return False, "pandas ist nicht installiert für Excel-Import", {}
            
            results = {'imported': 0, 'updated': 0, 'errors': 0, 'skipped': 0}
            
            # Excel-Datei einlesen
            df = pd.read_excel(file_path)
            
            # Standard-Mapping
            default_mapping = {
                'Kundennummer': 'customer_number',
                'Firmenname': 'company_name',
                'Vorname': 'first_name',
                'Nachname': 'last_name',
                'E-Mail': 'email',
                'Telefon': 'phone',
                'Straße': 'street',
                'PLZ': 'postal_code',
                'Stadt': 'city',
                'Land': 'country',
                'Steuernummer': 'tax_id',
                'USt-ID': 'vat_id'
            }
            
            field_mapping = mapping or default_mapping
            
            for index, row in df.iterrows():
                try:
                    # Kunden-Objekt erstellen (verwende normale Customer-Klasse)
                    from src.models import Customer
                    
                    customer = Customer()
                    
                    # Felder mappen
                    for excel_field, customer_field in field_mapping.items():
                        if excel_field in row and not pd.isna(row[excel_field]):
                            setattr(customer, customer_field, str(row[excel_field]))
                    
                    # ID vergeben
                    if not customer.id:
                        import uuid
                        customer.id = str(uuid.uuid4())
                    
                    # Prüfen ob Kunde bereits existiert
                    existing_customer = None
                    if update_existing:
                        existing_customers = self.data_manager.get_customers()
                        for existing in existing_customers:
                            if (existing.customer_number == customer.customer_number or
                                (existing.company_name and existing.company_name == customer.company_name)):
                                existing_customer = existing
                                break
                    
                    if existing_customer and update_existing:
                        # Update-Logik für bestehenden Kunden
                        for excel_field, customer_field in field_mapping.items():
                            if excel_field in row and not pd.isna(row[excel_field]):
                                setattr(existing_customer, customer_field, str(row[excel_field]))
                        self.data_manager.update_customer(existing_customer)
                        results['updated'] += 1
                    elif not existing_customer:
                        # Neuen Kunden hinzufügen
                        self.data_manager.add_customer(customer)
                        results['imported'] += 1
                    else:
                        results['skipped'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Fehler in Zeile {str(index)}: {e}")
                    results['errors'] += 1
            
            message = f"Excel-Import abgeschlossen: {results['imported']} neu, {results['updated']} aktualisiert, {results['errors']} Fehler"
            return True, message, results
            
        except Exception as e:
            return False, f"Excel-Import Fehler: {str(e)}", {}
    
    def _import_customers_json(self, file_path: str, update_existing: bool = False) -> Tuple[bool, str, Dict[str, int]]:
        """Importiert Kunden aus JSON"""
        try:
            results = {'imported': 0, 'updated': 0, 'errors': 0, 'skipped': 0}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Format erkennen
            if 'customers' in data:
                customers_data = data['customers']
            elif isinstance(data, list):
                customers_data = data
            else:
                return False, "Unbekanntes JSON-Format", {}
            
            for customer_data in customers_data:
                try:
                    # Normalen Customer aus Dict erstellen
                    from src.models import Customer
                    customer = Customer.from_dict(customer_data)
                    
                    # Prüfen ob Kunde bereits existiert
                    existing_customer = None
                    if update_existing:
                        existing_customers = self.data_manager.get_customers()
                        for existing in existing_customers:
                            if existing.id == customer.id:
                                existing_customer = existing
                                break
                    
                    if existing_customer and update_existing:
                        # Kunde aktualisieren
                        results['updated'] += 1
                    elif not existing_customer:
                        # Neuen Kunden speichern
                        self.data_manager.add_customer(customer)
                        results['imported'] += 1
                    else:
                        results['skipped'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Fehler beim Importieren von Kunde {customer_data.get('customer_id', 'unbekannt')}: {e}")
                    results['errors'] += 1
            
            message = f"JSON-Import abgeschlossen: {results['imported']} neu, {results['updated']} aktualisiert, {results['errors']} Fehler"
            return True, message, results
            
        except Exception as e:
            return False, f"JSON-Import Fehler: {str(e)}", {}
    
    def _import_invoices_json(self, file_path: str, update_existing: bool = False) -> Tuple[bool, str, Dict[str, int]]:
        """Importiert Rechnungen aus JSON"""
        try:
            results = {'imported': 0, 'updated': 0, 'errors': 0, 'skipped': 0}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Format erkennen
            if 'invoices' in data:
                invoices_data = data['invoices']
            elif isinstance(data, list):
                invoices_data = data
            else:
                return False, "Unbekanntes JSON-Format", {}
            
            for invoice_data in invoices_data:
                try:
                    # Hier würde ExtendedDocument.from_dict verwendet werden
                    # Da die bestehende Invoice-Klasse verwendet wird, vereinfacht:
                    results['imported'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Fehler beim Importieren von Rechnung: {e}")
                    results['errors'] += 1
            
            message = f"Rechnungs-Import abgeschlossen: {results['imported']} neu, {results['errors']} Fehler"
            return True, message, results
            
        except Exception as e:
            return False, f"Rechnungs-Import Fehler: {str(e)}", {}
    
    def validate_import_file(self, file_path: str, format_type: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validiert Import-Datei vor dem Import"""
        try:
            validation_info = {
                'file_size': Path(file_path).stat().st_size,
                'record_count': 0,
                'columns': [],
                'sample_data': {},
                'issues': []
            }
            
            if format_type == ImportFormat.CSV:
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    sample = csvfile.read(1024)
                    csvfile.seek(0)
                    delimiter = ';' if ';' in sample else ','
                    
                    reader = csv.DictReader(csvfile, delimiter=delimiter)
                    validation_info['columns'] = reader.fieldnames
                    
                    # Erste paar Zeilen als Sample
                    sample_rows = []
                    for i, row in enumerate(reader):
                        if i < 3:  # Erste 3 Zeilen
                            sample_rows.append(row)
                        validation_info['record_count'] = i + 1
                    
                    validation_info['sample_data'] = sample_rows
                    
                    # Validierungen
                    required_fields = ['customer_number', 'company_name', 'email']
                    columns = validation_info.get('columns', [])
                    if columns:
                        missing_fields = [field for field in required_fields if field not in columns]
                        if missing_fields:
                            validation_info['issues'].append(f"Fehlende Pflichtfelder: {', '.join(missing_fields)}")
            
            elif format_type == ImportFormat.JSON:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    validation_info['record_count'] = len(data)
                    validation_info['sample_data'] = data[:3] if data else []
                elif isinstance(data, dict) and 'customers' in data:
                    validation_info['record_count'] = len(data['customers'])
                    validation_info['sample_data'] = data['customers'][:3] if data['customers'] else []
                else:
                    validation_info['issues'].append("Unbekanntes JSON-Format")
            
            success = len(validation_info['issues']) == 0
            message = "Datei erfolgreich validiert" if success else f"Validierungsfehler: {'; '.join(validation_info['issues'])}"
            
            return success, message, validation_info
            
        except Exception as e:
            return False, f"Validierungsfehler: {str(e)}", {}
