"""
Datenmodelle für das Rechnungs-Tool
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
import json
from enum import Enum


class DocumentType(Enum):
    ANGEBOT = "Angebot"
    RECHNUNG = "Rechnung"
    GUTSCHRIFT = "Gutschrift"
    STORNO = "Storno"


class TaxRate(Enum):
    ZERO = Decimal("0.00")
    REDUCED = Decimal("0.07")
    STANDARD = Decimal("0.19")


class PaymentStatus(Enum):
    """Zahlungsstatus"""
    OFFEN = "Offen"
    BEZAHLT = "Bezahlt"
    TEILWEISE_BEZAHLT = "Teilweise bezahlt"
    UEBERFAELLIG = "Überfällig"
    STORNIERT = "Storniert"


@dataclass
class CompanyData:
    """Stammdaten des Unternehmens"""
    name: str = ""
    address_line1: str = ""
    address_line2: str = ""
    postal_code: str = ""
    city: str = ""
    country: str = "Deutschland"
    phone: str = ""
    email: str = ""
    website: str = ""
    tax_number: str = ""  # Steuernummer
    vat_id: str = ""  # USt-IdNr.
    iban: str = ""
    bic: str = ""
    bank_name: str = ""
    logo_path: str = ""
    is_small_business: bool = False  # §19 UStG
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyData':
        return cls(**data)


@dataclass
class Customer:
    """Kundendaten"""
    id: str = ""
    company_name: str = ""
    contact_person: str = ""
    address_line1: str = ""
    address_line2: str = ""
    postal_code: str = ""
    city: str = ""
    country: str = "Deutschland"
    phone: str = ""
    email: str = ""
    vat_id: str = ""  # Für Reverse Charge
    customer_number: str = ""
    
    # Separate Lieferadresse (optional)
    delivery_company: str = ""
    delivery_address_line1: str = ""
    delivery_address_line2: str = ""
    delivery_postal_code: str = ""
    delivery_city: str = ""
    delivery_country: str = "Deutschland"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        return cls(**data)
    
    def get_display_name(self) -> str:
        """Gibt den Anzeigenamen zurück"""
        if self.company_name and self.contact_person:
            return f"{self.company_name} ({self.contact_person})"
        elif self.company_name:
            return self.company_name
        elif self.contact_person:
            return self.contact_person
        else:
            return f"Kunde {self.customer_number}"


@dataclass
class InvoicePosition:
    """Rechnungsposition"""
    position_number: int = 1
    description: str = ""
    quantity: Decimal = Decimal("1.00")
    unit: str = "Stk."
    unit_price: Decimal = Decimal("0.00")
    discount_percent: Decimal = Decimal("0.00")
    tax_rate: TaxRate = TaxRate.STANDARD
    
    def calculate_line_total_net(self) -> Decimal:
        """Berechnet den Netto-Zeilenbetrag"""
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percent / Decimal("100"))
        return (subtotal - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def calculate_tax_amount(self) -> Decimal:
        """Berechnet den Steuerbetrag der Position"""
        net_amount = self.calculate_line_total_net()
        return (net_amount * self.tax_rate.value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def calculate_line_total_gross(self) -> Decimal:
        """Berechnet den Brutto-Zeilenbetrag"""
        return self.calculate_line_total_net() + self.calculate_tax_amount()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Konvertiere Decimal zu String für JSON-Serialisierung
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
        # Konvertiere TaxRate zu Wert
        data['tax_rate'] = str(self.tax_rate.value)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InvoicePosition':
        # Konvertiere String zurück zu Decimal
        decimal_fields = ['quantity', 'unit_price', 'discount_percent']
        for field in decimal_fields:
            if field in data:
                data[field] = Decimal(str(data[field]))
        
        # Konvertiere tax_rate zurück
        if 'tax_rate' in data:
            tax_rate_value = Decimal(str(data['tax_rate']))
            for rate in TaxRate:
                if rate.value == tax_rate_value:
                    data['tax_rate'] = rate
                    break
        
        return cls(**data)


@dataclass
class Invoice:
    """Rechnung/Dokument"""
    id: str = ""
    document_type: DocumentType = DocumentType.RECHNUNG
    invoice_number: str = ""
    invoice_date: datetime = field(default_factory=datetime.now)
    service_date: Optional[datetime] = None
    customer: Optional[Customer] = None
    positions: List[InvoicePosition] = field(default_factory=list)
    
    # Zahlungskonditionen
    payment_terms_days: int = 14
    discount_days: int = 0
    discount_percent: Decimal = Decimal("0.00")
    
    # Texte
    header_text: str = ""
    footer_text: str = ""
    payment_info_text: str = ""
    
    # Status
    is_paid: bool = False
    payment_date: Optional[datetime] = None
    payment_status: PaymentStatus = PaymentStatus.OFFEN
    
    # Referenzen
    reference_invoice_id: str = ""  # Für Gutschriften/Stornos
    offer_number: str = ""  # Angebotsnummer bei Rechnung
    
    def calculate_net_totals_by_tax_rate(self) -> Dict[TaxRate, Decimal]:
        """Berechnet Netto-Summen gruppiert nach Steuersatz"""
        totals = {}
        for position in self.positions:
            tax_rate = position.tax_rate
            if tax_rate not in totals:
                totals[tax_rate] = Decimal("0.00")
            totals[tax_rate] += position.calculate_line_total_net()
        return totals
    
    def calculate_tax_totals_by_rate(self) -> Dict[TaxRate, Decimal]:
        """Berechnet Steuerbeträge gruppiert nach Steuersatz"""
        totals = {}
        for position in self.positions:
            tax_rate = position.tax_rate
            if tax_rate not in totals:
                totals[tax_rate] = Decimal("0.00")
            totals[tax_rate] += position.calculate_tax_amount()
        return totals
    
    def calculate_total_net(self) -> Decimal:
        """Berechnet die Netto-Gesamtsumme"""
        return sum(self.calculate_net_totals_by_tax_rate().values(), Decimal("0.00"))
    
    def calculate_total_tax(self) -> Decimal:
        """Berechnet die Gesamtsteuer"""
        return sum(self.calculate_tax_totals_by_rate().values(), Decimal("0.00"))
    
    def calculate_total_gross(self) -> Decimal:
        """Berechnet die Brutto-Gesamtsumme"""
        return self.calculate_total_net() + self.calculate_total_tax()
    
    def has_reverse_charge(self) -> bool:
        """Prüft ob Reverse Charge anzuwenden ist (alle Positionen 0% MwSt)"""
        return all(pos.tax_rate == TaxRate.ZERO for pos in self.positions)
    
    def get_default_payment_text(self) -> str:
        """Generiert Standard-Zahlungstext"""
        if self.document_type == DocumentType.RECHNUNG:
            due_date = self.invoice_date.replace(day=self.invoice_date.day + self.payment_terms_days)
            return f"Zahlbar innerhalb von {self.payment_terms_days} Tagen bis zum {due_date.strftime('%d.%m.%Y')} ohne Abzug."
        return ""
    
    def update_payment_status(self):
        """Aktualisiert den Zahlungsstatus basierend auf anderen Attributen"""
        if self.is_paid and self.payment_date:
            self.payment_status = PaymentStatus.BEZAHLT
        elif self.document_type == DocumentType.STORNO:
            self.payment_status = PaymentStatus.STORNIERT
        elif self.invoice_date and self.payment_terms_days:
            # Prüfe ob überfällig
            from datetime import timedelta
            due_date = self.invoice_date + timedelta(days=self.payment_terms_days)
            if datetime.now() > due_date:
                self.payment_status = PaymentStatus.UEBERFAELLIG
            else:
                self.payment_status = PaymentStatus.OFFEN
        else:
            self.payment_status = PaymentStatus.OFFEN
    
    def get_payment_status_display(self) -> str:
        """Gibt den Zahlungsstatus als String zurück (für Kompatibilität)"""
        return self.payment_status.value
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        
        # Konvertiere datetime zu ISO-String
        if self.invoice_date:
            data['invoice_date'] = self.invoice_date.isoformat()
        if self.service_date:
            data['service_date'] = self.service_date.isoformat()
        if self.payment_date:
            data['payment_date'] = self.payment_date.isoformat()
        
        # Konvertiere DocumentType zu String
        data['document_type'] = self.document_type.value
        
        # Konvertiere PaymentStatus zu String
        data['payment_status'] = self.payment_status.value
        
        # Konvertiere Decimal zu String
        decimal_fields = ['discount_percent']
        for field in decimal_fields:
            if field in data:
                data[field] = str(data[field])
        
        # Konvertiere Customer und Positions
        if self.customer:
            data['customer'] = self.customer.to_dict()
        
        data['positions'] = [pos.to_dict() for pos in self.positions]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        # Konvertiere datetime von ISO-String
        if 'invoice_date' in data and data['invoice_date']:
            data['invoice_date'] = datetime.fromisoformat(data['invoice_date'])
        if 'service_date' in data and data['service_date']:
            data['service_date'] = datetime.fromisoformat(data['service_date'])
        if 'payment_date' in data and data['payment_date']:
            data['payment_date'] = datetime.fromisoformat(data['payment_date'])
        
        # Konvertiere DocumentType
        if 'document_type' in data:
            for doc_type in DocumentType:
                if doc_type.value == data['document_type']:
                    data['document_type'] = doc_type
                    break
        
        # Konvertiere PaymentStatus
        if 'payment_status' in data:
            for status in PaymentStatus:
                if status.value == data['payment_status']:
                    data['payment_status'] = status
                    break
        
        # Konvertiere Decimal
        decimal_fields = ['discount_percent']
        for field in decimal_fields:
            if field in data:
                data[field] = Decimal(str(data[field]))
        
        # Konvertiere Customer
        if 'customer' in data and data['customer']:
            data['customer'] = Customer.from_dict(data['customer'])
        
        # Konvertiere Positions
        if 'positions' in data:
            data['positions'] = [InvoicePosition.from_dict(pos) for pos in data['positions']]
        
        return cls(**data)


@dataclass
class AppSettings:
    """Anwendungseinstellungen"""
    
    # UI-Einstellungen
    theme_mode: str = "system"  # "light", "dark", "system"
    window_width: int = 1200
    window_height: int = 800
    
    # Rechnungsnummern
    invoice_number_format: str = "R{year}-{counter:04d}"
    offer_number_format: str = "A{year}-{counter:04d}"
    credit_note_format: str = "G{year}-{counter:04d}"
    
    # Zähler für Nummernkreise
    invoice_counter: int = 1
    offer_counter: int = 1
    credit_note_counter: int = 1
    customer_counter: int = 1
    
    # Standard-Werte
    default_payment_terms: int = 14
    default_tax_rate: str = "0.19"  # String für TaxRate
    default_currency: str = "EUR"
    
    # PDF-Einstellungen
    pdf_company_color: str = "#2E86AB"  # Hex-Farbcode für CI
    pdf_font_size: int = 10
    enable_qr_codes: bool = True  # QR-Codes für Banking in PDFs
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        return cls(**data)
    
    def get_next_invoice_number(self) -> str:
        """Generiert die nächste Rechnungsnummer"""
        from datetime import datetime
        year = datetime.now().year
        number = self.invoice_number_format.format(year=year, counter=self.invoice_counter)
        self.invoice_counter += 1
        return number
    
    def get_next_offer_number(self) -> str:
        """Generiert die nächste Angebotsnummer"""
        from datetime import datetime
        year = datetime.now().year
        number = self.offer_number_format.format(year=year, counter=self.offer_counter)
        self.offer_counter += 1
        return number
    
    def get_next_credit_note_number(self) -> str:
        """Generiert die nächste Gutschriftsnummer"""
        from datetime import datetime
        year = datetime.now().year
        number = self.credit_note_format.format(year=year, counter=self.credit_note_counter)
        self.credit_note_counter += 1
        return number
    
    def get_next_customer_number(self) -> str:
        """Generiert die nächste Kundennummer"""
        number = f"K{self.customer_counter:04d}"
        self.customer_counter += 1
        return number
