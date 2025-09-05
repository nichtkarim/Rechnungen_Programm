"""
Erweiterte Validierung für Geschäftsdaten
"""
import re
from typing import List, Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime
from dataclasses import dataclass

from src.models import Customer, Invoice, InvoicePosition, CompanyData


@dataclass
class ValidationError:
    """Repräsentiert einen Validierungsfehler"""
    field: str
    message: str
    severity: str = "error"  # "error", "warning", "info"


@dataclass
class ValidationResult:
    """Ergebnis einer Validierung"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    
    def add_error(self, field: str, message: str):
        self.errors.append(ValidationError(field, message, "error"))
        self.is_valid = False
    
    def add_warning(self, field: str, message: str):
        self.warnings.append(ValidationError(field, message, "warning"))


class BusinessValidator:
    """Erweiterte Geschäftsdatenvalidierung"""
    
    # Deutsche Postleitzahlen: 5 Ziffern
    PLZ_PATTERN = re.compile(r'^\d{5}$')
    
    # E-Mail Validierung (einfach aber robust)
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Deutsche Telefonnummern (flexibel)
    PHONE_PATTERN = re.compile(r'^(\+49|0)[0-9\s\-\/\(\)]{6,20}$')
    
    # IBAN Validierung (Deutschland)
    IBAN_PATTERN = re.compile(r'^DE\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}$')
    
    # BIC Validierung
    BIC_PATTERN = re.compile(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$')
    
    # Deutsche Steuernummer (variiert je nach Bundesland)
    TAX_NUMBER_PATTERN = re.compile(r'^[0-9]{2,3}\/[0-9]{3,4}\/[0-9]{4,5}$')
    
    # USt-IdNr. (Deutschland)
    VAT_ID_PATTERN = re.compile(r'^DE[0-9]{9}$')
    
    def validate_customer(self, customer: Customer) -> ValidationResult:
        """Validiert Kundendaten umfassend"""
        result = ValidationResult(True, [], [])
        
        # Grunddaten prüfen
        if not customer.company_name.strip() and not customer.contact_person.strip():
            result.add_error("company_name", "Firmenname oder Kontaktperson ist erforderlich")
        
        # Kundennummer prüfen
        if not customer.customer_number.strip():
            result.add_error("customer_number", "Kundennummer ist erforderlich")
        
        # Adressdaten validieren
        self._validate_address(customer, result, prefix="")
        
        # Lieferadresse validieren (falls vorhanden)
        if any([customer.delivery_company, customer.delivery_address_line1, 
                customer.delivery_city, customer.delivery_postal_code]):
            self._validate_address(customer, result, prefix="delivery_")
        
        # Kontaktdaten validieren
        if customer.email and not self.EMAIL_PATTERN.match(customer.email):
            result.add_error("email", "Ungültige E-Mail-Adresse")
        
        if customer.phone and not self.PHONE_PATTERN.match(customer.phone):
            result.add_warning("phone", "Telefonnummer entspricht nicht dem deutschen Format")
        
        # USt-IdNr. validieren (falls vorhanden)
        if customer.vat_id and not self.VAT_ID_PATTERN.match(customer.vat_id.replace(" ", "")):
            result.add_error("vat_id", "USt-IdNr. entspricht nicht dem deutschen Format (DE123456789)")
        
        return result
    
    def validate_company(self, company: CompanyData) -> ValidationResult:
        """Validiert Firmendaten"""
        result = ValidationResult(True, [], [])
        
        # Grunddaten
        if not company.name.strip():
            result.add_error("name", "Firmenname ist erforderlich")
        
        # Adresse
        if not company.address_line1.strip():
            result.add_error("address_line1", "Straße ist erforderlich")
        
        if not company.city.strip():
            result.add_error("city", "Stadt ist erforderlich")
        
        if company.postal_code and not self.PLZ_PATTERN.match(company.postal_code):
            result.add_error("postal_code", "Postleitzahl muss 5-stellig sein")
        
        # Kontaktdaten
        if company.email and not self.EMAIL_PATTERN.match(company.email):
            result.add_error("email", "Ungültige E-Mail-Adresse")
        
        if company.phone and not self.PHONE_PATTERN.match(company.phone):
            result.add_warning("phone", "Telefonnummer entspricht nicht dem deutschen Format")
        
        # Steuerliche Daten
        if company.tax_number and not self.TAX_NUMBER_PATTERN.match(company.tax_number):
            result.add_warning("tax_number", "Steuernummer entspricht nicht dem üblichen Format")
        
        if company.vat_id and not self.VAT_ID_PATTERN.match(company.vat_id.replace(" ", "")):
            result.add_error("vat_id", "USt-IdNr. entspricht nicht dem deutschen Format")
        
        # Bankdaten
        if company.iban and not self._validate_german_iban(company.iban):
            result.add_error("iban", "IBAN ist ungültig")
        
        if company.bic and not self.BIC_PATTERN.match(company.bic.replace(" ", "")):
            result.add_error("bic", "BIC ist ungültig")
        
        # Kleinunternehmer-Prüfung
        if company.is_small_business and company.vat_id:
            result.add_warning("is_small_business", "Kleinunternehmer haben normalerweise keine USt-IdNr.")
        
        return result
    
    def validate_invoice(self, invoice: Invoice) -> ValidationResult:
        """Validiert Rechnung umfassend"""
        result = ValidationResult(True, [], [])
        
        # Grunddaten
        if not invoice.invoice_number.strip():
            result.add_error("invoice_number", "Rechnungsnummer ist erforderlich")
        
        if not invoice.customer:
            result.add_error("customer", "Kunde ist erforderlich")
        else:
            # Kundendaten validieren
            customer_result = self.validate_customer(invoice.customer)
            result.errors.extend(customer_result.errors)
            result.warnings.extend(customer_result.warnings)
            if not customer_result.is_valid:
                result.is_valid = False
        
        # Datum validieren
        if invoice.invoice_date > datetime.now():
            result.add_warning("invoice_date", "Rechnungsdatum liegt in der Zukunft")
        
        if invoice.service_date and invoice.service_date > datetime.now():
            result.add_warning("service_date", "Leistungsdatum liegt in der Zukunft")
        
        # Positionen validieren
        if not invoice.positions:
            result.add_error("positions", "Mindestens eine Position ist erforderlich")
        else:
            for i, position in enumerate(invoice.positions):
                pos_result = self.validate_position(position)
                # Fehlermeldungen mit Positionsnummer erweitern
                for error in pos_result.errors:
                    result.add_error(f"position_{i+1}_{error.field}", error.message)
                for warning in pos_result.warnings:
                    result.add_warning(f"position_{i+1}_{warning.field}", warning.message)
                if not pos_result.is_valid:
                    result.is_valid = False
        
        # Zahlungsbedingungen
        if invoice.payment_terms_days <= 0:
            result.add_error("payment_terms_days", "Zahlungsziel muss positiv sein")
        
        if invoice.payment_terms_days > 90:
            result.add_warning("payment_terms_days", "Zahlungsziel über 90 Tage ist unüblich")
        
        # Reverse Charge Prüfung
        if invoice.has_reverse_charge() and invoice.customer and not invoice.customer.vat_id:
            result.add_error("reverse_charge", "Reverse Charge erfordert USt-IdNr. des Kunden")
        
        return result
    
    def validate_position(self, position: InvoicePosition) -> ValidationResult:
        """Validiert Rechnungsposition"""
        result = ValidationResult(True, [], [])
        
        # Beschreibung
        if not position.description.strip():
            result.add_error("description", "Beschreibung ist erforderlich")
        
        # Menge
        if position.quantity <= 0:
            result.add_error("quantity", "Menge muss positiv sein")
        
        if position.quantity > Decimal("9999999"):
            result.add_warning("quantity", "Sehr große Menge - bitte prüfen")
        
        # Einzelpreis
        if position.unit_price < 0:
            result.add_error("unit_price", "Einzelpreis darf nicht negativ sein")
        
        if position.unit_price > Decimal("999999"):
            result.add_warning("unit_price", "Sehr hoher Einzelpreis - bitte prüfen")
        
        # Rabatt
        if position.discount_percent < 0 or position.discount_percent > 100:
            result.add_error("discount_percent", "Rabatt muss zwischen 0% und 100% liegen")
        
        # Positionsnummer
        if position.position_number <= 0:
            result.add_error("position_number", "Positionsnummer muss positiv sein")
        
        return result
    
    def _validate_address(self, customer: Customer, result: ValidationResult, prefix: str = ""):
        """Hilfsmethode für Adressvalidierung"""
        address_line1 = getattr(customer, f"{prefix}address_line1", "")
        postal_code = getattr(customer, f"{prefix}postal_code", "")
        city = getattr(customer, f"{prefix}city", "")
        
        if not address_line1.strip():
            result.add_error(f"{prefix}address_line1", "Straße ist erforderlich")
        
        if not city.strip():
            result.add_error(f"{prefix}city", "Stadt ist erforderlich")
        
        if postal_code and not self.PLZ_PATTERN.match(postal_code):
            result.add_error(f"{prefix}postal_code", "Postleitzahl muss 5-stellig sein")
    
    def _validate_german_iban(self, iban: str) -> bool:
        """Validiert deutsche IBAN mit Prüfsumme"""
        # Leerzeichen entfernen
        iban = iban.replace(" ", "").upper()
        
        # Format prüfen
        if not self.IBAN_PATTERN.match(iban):
            return False
        
        # Prüfsummen-Algorithmus (vereinfacht)
        # Für Produktiveinsatz sollte eine vollständige IBAN-Validierung verwendet werden
        try:
            # Umstellung für Modulo-97-Berechnung
            rearranged = iban[4:] + iban[:4]
            
            # Buchstaben zu Zahlen konvertieren
            numeric = ""
            for char in rearranged:
                if char.isalpha():
                    numeric += str(ord(char) - ord('A') + 10)
                else:
                    numeric += char
            
            # Prüfsumme berechnen
            return int(numeric) % 97 == 1
        except (ValueError, OverflowError):
            return False


class DataIntegrityChecker:
    """Prüft Datenintegrität und findet Inkonsistenzen"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def check_integrity(self) -> Dict[str, List[str]]:
        """Führt umfassende Integritätsprüfung durch"""
        issues = {
            "critical": [],
            "warnings": [],
            "info": []
        }
        
        # Kundennummern-Duplikate prüfen
        self._check_customer_duplicates(issues)
        
        # Rechnungsnummern-Duplikate prüfen
        self._check_invoice_duplicates(issues)
        
        # Orphaned References prüfen
        self._check_orphaned_references(issues)
        
        # Dateninkonsistenzen prüfen
        self._check_data_consistency(issues)
        
        return issues
    
    def _check_customer_duplicates(self, issues: Dict[str, List[str]]):
        """Prüft auf doppelte Kundennummern"""
        customers = self.data_manager.get_customers()
        customer_numbers = {}
        
        for customer in customers:
            if customer.customer_number in customer_numbers:
                issues["critical"].append(
                    f"Doppelte Kundennummer: {customer.customer_number} "
                    f"({customer.get_display_name()} und {customer_numbers[customer.customer_number]})"
                )
            else:
                customer_numbers[customer.customer_number] = customer.get_display_name()
    
    def _check_invoice_duplicates(self, issues: Dict[str, List[str]]):
        """Prüft auf doppelte Rechnungsnummern"""
        invoices = self.data_manager.get_invoices()
        invoice_numbers = {}
        
        for invoice in invoices:
            key = f"{invoice.document_type.value}_{invoice.invoice_number}"
            if key in invoice_numbers:
                issues["critical"].append(
                    f"Doppelte {invoice.document_type.value}-Nummer: {invoice.invoice_number}"
                )
            else:
                invoice_numbers[key] = invoice.id
    
    def _check_orphaned_references(self, issues: Dict[str, List[str]]):
        """Prüft auf verwaiste Referenzen"""
        customers = self.data_manager.get_customers()
        invoices = self.data_manager.get_invoices()
        
        customer_ids = {c.id for c in customers}
        
        for invoice in invoices:
            if invoice.customer and invoice.customer.id not in customer_ids:
                issues["warnings"].append(
                    f"Rechnung {invoice.invoice_number} referenziert unbekannten Kunden"
                )
    
    def _check_data_consistency(self, issues: Dict[str, List[str]]):
        """Prüft allgemeine Datenkonsistenz"""
        settings = self.data_manager.get_settings()
        invoices = self.data_manager.get_invoices()
        
        # Zähler-Konsistenz prüfen
        max_invoice_counter = 0
        for invoice in invoices:
            if invoice.document_type.value == "Rechnung":
                try:
                    # Versuche Zähler aus Rechnungsnummer zu extrahieren
                    parts = invoice.invoice_number.split('-')
                    if len(parts) == 2 and parts[1].isdigit():
                        counter = int(parts[1])
                        max_invoice_counter = max(max_invoice_counter, counter)
                except (ValueError, IndexError):
                    pass
        
        if settings.invoice_counter <= max_invoice_counter:
            issues["warnings"].append(
                f"Rechnungszähler ({settings.invoice_counter}) ist nicht höher als höchste Rechnungsnummer ({max_invoice_counter})"
            )
