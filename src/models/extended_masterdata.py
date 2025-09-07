"""
Erweiterte Stammdatenmodelle für Kunden, Lieferanten und Artikel
"""
from enum import Enum
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from decimal import Decimal
import uuid


class CustomerType(Enum):
    """Kundentypen"""
    PRIVATE = "Privatkunde"
    BUSINESS = "Geschäftskunde"
    GOVERNMENT = "Behörde"
    NON_PROFIT = "Gemeinnützig"
    RESELLER = "Wiederverkäufer"
    DISTRIBUTOR = "Händler"


class CustomerStatus(Enum):
    """Kundenstatus"""
    ACTIVE = "Aktiv"
    INACTIVE = "Inaktiv"
    PROSPECT = "Interessent"
    LEAD = "Lead"
    BLOCKED = "Gesperrt"
    VIP = "VIP"


class AddressType(Enum):
    """Adresstypen"""
    BILLING = "Rechnungsadresse"
    SHIPPING = "Lieferadresse"
    OFFICE = "Büro"
    HOME = "Privat"
    WAREHOUSE = "Lager"
    OTHER = "Sonstiges"


class ContactType(Enum):
    """Kontakttypen"""
    PRIMARY = "Hauptkontakt"
    BILLING = "Buchhaltung"
    TECHNICAL = "Technik"
    SALES = "Vertrieb"
    EMERGENCY = "Notfall"
    OTHER = "Sonstiges"


class PaymentRating(Enum):
    """Zahlungsverhalten"""
    EXCELLENT = "Ausgezeichnet"
    GOOD = "Gut"
    AVERAGE = "Durchschnittlich"
    POOR = "Schlecht"
    VERY_POOR = "Sehr schlecht"
    UNKNOWN = "Unbekannt"


class Address:
    """Adresse"""
    
    def __init__(self, address_id: Optional[str] = None, address_type: AddressType = AddressType.BILLING,
                 company: str = "", title: str = "", first_name: str = "", last_name: str = "",
                 street: str = "", street2: str = "", postal_code: str = "", city: str = "",
                 state: str = "", country: str = "Deutschland", is_primary: bool = False):
        self.address_id = address_id or str(uuid.uuid4())
        self.address_type = address_type
        self.company = company
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.street = street
        self.street2 = street2  # Zusätzliche Adresszeile
        self.postal_code = postal_code
        self.city = city
        self.state = state
        self.country = country
        self.is_primary = is_primary
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.notes = ""
    
    def get_full_name(self) -> str:
        """Vollständiger Name"""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)
    
    def get_display_name(self) -> str:
        """Anzeigename (Firma oder Name)"""
        if self.company:
            return self.company
        return self.get_full_name()
    
    def get_formatted_address(self) -> str:
        """Formatierte Adresse"""
        lines = []
        
        # Name/Firma
        if self.company:
            lines.append(self.company)
        if self.get_full_name():
            lines.append(self.get_full_name())
        
        # Straße
        if self.street:
            lines.append(self.street)
        if self.street2:
            lines.append(self.street2)
        
        # PLZ/Ort
        city_line = ""
        if self.postal_code:
            city_line += self.postal_code
        if self.city:
            city_line += " " + self.city if city_line else self.city
        if city_line:
            lines.append(city_line)
        
        # Bundesland/Land
        if self.state and self.country != "Deutschland":
            lines.append(f"{self.state}, {self.country}")
        elif self.country != "Deutschland":
            lines.append(self.country)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'address_id': self.address_id,
            'address_type': self.address_type.value,
            'company': self.company,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'street': self.street,
            'street2': self.street2,
            'postal_code': self.postal_code,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Address':
        """Erstellt aus Dictionary"""
        address = cls()
        address.address_id = data.get('address_id', '')
        address.address_type = AddressType(data.get('address_type', AddressType.BILLING.value))
        address.company = data.get('company', '')
        address.title = data.get('title', '')
        address.first_name = data.get('first_name', '')
        address.last_name = data.get('last_name', '')
        address.street = data.get('street', '')
        address.street2 = data.get('street2', '')
        address.postal_code = data.get('postal_code', '')
        address.city = data.get('city', '')
        address.state = data.get('state', '')
        address.country = data.get('country', 'Deutschland')
        address.is_primary = data.get('is_primary', False)
        address.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        address.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        address.notes = data.get('notes', '')
        return address


class Contact:
    """Kontaktperson"""
    
    def __init__(self, contact_id: Optional[str] = None, contact_type: ContactType = ContactType.PRIMARY,
                 title: str = "", first_name: str = "", last_name: str = "", position: str = "",
                 department: str = "", email: str = "", phone: str = "", mobile: str = "",
                 fax: str = "", website: str = "", is_primary: bool = False):
        self.contact_id = contact_id or str(uuid.uuid4())
        self.contact_type = contact_type
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.department = department
        self.email = email
        self.phone = phone
        self.mobile = mobile
        self.fax = fax
        self.website = website
        self.is_primary = is_primary
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.notes = ""
        self.birthday: Optional[date] = None
        self.language = "de"
        self.timezone = "Europe/Berlin"
        self.preferred_contact_method = "email"
    
    def get_full_name(self) -> str:
        """Vollständiger Name"""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)
    
    def get_display_name(self) -> str:
        """Anzeigename mit Position"""
        name = self.get_full_name()
        if self.position:
            name += f" ({self.position})"
        return name
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'contact_id': self.contact_id,
            'contact_type': self.contact_type.value,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'position': self.position,
            'department': self.department,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'fax': self.fax,
            'website': self.website,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'language': self.language,
            'timezone': self.timezone,
            'preferred_contact_method': self.preferred_contact_method
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Erstellt aus Dictionary"""
        contact = cls()
        contact.contact_id = data.get('contact_id', '')
        contact.contact_type = ContactType(data.get('contact_type', ContactType.PRIMARY.value))
        contact.title = data.get('title', '')
        contact.first_name = data.get('first_name', '')
        contact.last_name = data.get('last_name', '')
        contact.position = data.get('position', '')
        contact.department = data.get('department', '')
        contact.email = data.get('email', '')
        contact.phone = data.get('phone', '')
        contact.mobile = data.get('mobile', '')
        contact.fax = data.get('fax', '')
        contact.website = data.get('website', '')
        contact.is_primary = data.get('is_primary', False)
        contact.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        contact.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        contact.notes = data.get('notes', '')
        contact.birthday = date.fromisoformat(data['birthday']) if data.get('birthday') else None
        contact.language = data.get('language', 'de')
        contact.timezone = data.get('timezone', 'Europe/Berlin')
        contact.preferred_contact_method = data.get('preferred_contact_method', 'email')
        return contact


class ExtendedCustomer:
    """Erweiterte Kundendatenklasse"""
    
    def __init__(self, customer_id: Optional[str] = None, customer_number: str = "",
                 customer_type: CustomerType = CustomerType.BUSINESS,
                 status: CustomerStatus = CustomerStatus.ACTIVE):
        self.customer_id = customer_id or str(uuid.uuid4())
        self.customer_number = customer_number
        self.customer_type = customer_type
        self.status = status
        
        # Grunddaten
        self.company_name = ""
        self.brand_name = ""
        self.legal_form = ""  # GmbH, AG, etc.
        self.industry = ""
        self.website = ""
        
        # Registrierungsdaten
        self.tax_id = ""  # Steuernummer
        self.vat_id = ""  # Umsatzsteuer-ID
        self.commercial_register = ""  # Handelsregisternummer
        self.court_of_registration = ""  # Registergericht
        
        # Adressen und Kontakte
        self.addresses: List[Address] = []
        self.contacts: List[Contact] = []
        
        # Geschäftsbedingungen
        self.payment_terms = "NET_14"
        self.payment_method = "BANK_TRANSFER"
        self.credit_limit: Optional[Decimal] = None
        self.payment_rating = PaymentRating.UNKNOWN
        self.discount_percent: Decimal = Decimal('0')
        self.currency = "EUR"
        
        # Verkaufsrelevante Daten
        self.sales_representative = ""
        self.customer_group = ""
        self.price_group = ""
        self.marketing_consent = False
        self.newsletter_consent = False
        
        # CRM-Daten
        self.source = ""  # Woher kommt der Kunde?
        self.lead_date: Optional[date] = None
        self.first_contact_date: Optional[date] = None
        self.first_order_date: Optional[date] = None
        self.last_order_date: Optional[date] = None
        self.total_orders = 0
        self.total_revenue: Decimal = Decimal('0')
        self.average_order_value: Decimal = Decimal('0')
        
        # Metadaten
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.created_by = ""
        self.updated_by = ""
        self.notes = ""
        self.internal_notes = ""
        
        # Tags und Kategorisierung
        self.tags: List[str] = []
        self.categories: List[str] = []
        self.custom_fields: Dict[str, Any] = {}
        
        # DSGVO und Compliance
        self.data_processing_consent = False
        self.data_processing_consent_date: Optional[date] = None
        self.data_retention_period = 10  # Jahre
        self.gdpr_notes = ""
        
        # Kommunikation
        self.preferred_language = "de"
        self.communication_preferences: Dict[str, bool] = {
            'email': True,
            'phone': True,
            'post': False,
            'sms': False
        }
        
        # Anhänge und Dokumente
        self.attachments: List[str] = []
        self.contracts: List[str] = []
        self.certificates: List[str] = []
    
    def get_primary_address(self) -> Optional[Address]:
        """Hauptadresse ermitteln"""
        for address in self.addresses:
            if address.is_primary:
                return address
        return self.addresses[0] if self.addresses else None
    
    def get_billing_address(self) -> Optional[Address]:
        """Rechnungsadresse ermitteln"""
        for address in self.addresses:
            if address.address_type == AddressType.BILLING:
                return address
        return self.get_primary_address()
    
    def get_shipping_address(self) -> Optional[Address]:
        """Lieferadresse ermitteln"""
        for address in self.addresses:
            if address.address_type == AddressType.SHIPPING:
                return address
        return self.get_primary_address()
    
    def get_primary_contact(self) -> Optional[Contact]:
        """Hauptkontakt ermitteln"""
        for contact in self.contacts:
            if contact.is_primary:
                return contact
        return self.contacts[0] if self.contacts else None
    
    def get_contact_by_type(self, contact_type: ContactType) -> Optional[Contact]:
        """Kontakt nach Typ ermitteln"""
        for contact in self.contacts:
            if contact.contact_type == contact_type:
                return contact
        return None
    
    def get_display_name(self) -> str:
        """Anzeigename"""
        if self.company_name:
            return self.company_name
        
        primary_address = self.get_primary_address()
        if primary_address:
            return primary_address.get_display_name()
        
        primary_contact = self.get_primary_contact()
        if primary_contact:
            return primary_contact.get_full_name()
        
        return f"Kunde {self.customer_number}" if self.customer_number else "Unbekannter Kunde"
    
    def add_address(self, address: Address):
        """Adresse hinzufügen"""
        # Wenn es die erste Adresse ist oder als primär markiert
        if not self.addresses or address.is_primary:
            # Andere Adressen als nicht-primär markieren
            for addr in self.addresses:
                addr.is_primary = False
            address.is_primary = True
        
        self.addresses.append(address)
        self.updated_at = datetime.now()
    
    def add_contact(self, contact: Contact):
        """Kontakt hinzufügen"""
        # Wenn es der erste Kontakt ist oder als primär markiert
        if not self.contacts or contact.is_primary:
            # Andere Kontakte als nicht-primär markieren
            for cont in self.contacts:
                cont.is_primary = False
            contact.is_primary = True
        
        self.contacts.append(contact)
        self.updated_at = datetime.now()
    
    def calculate_customer_value(self) -> Dict[str, Any]:
        """Berechnet Kundenwert-Kennzahlen"""
        return {
            'total_revenue': self.total_revenue,
            'total_orders': self.total_orders,
            'average_order_value': self.average_order_value,
            'customer_lifetime_value': self.total_revenue,  # Vereinfacht
            'order_frequency': self.calculate_order_frequency(),
            'days_since_last_order': self.calculate_days_since_last_order(),
            'payment_reliability': self.payment_rating.value
        }
    
    def calculate_order_frequency(self) -> float:
        """Bestellfrequenz in Tagen"""
        if not self.first_order_date or not self.last_order_date or self.total_orders <= 1:
            return 0.0
        
        days_span = (self.last_order_date - self.first_order_date).days
        if days_span <= 0:
            return 0.0
        
        return days_span / max(self.total_orders - 1, 1)
    
    def calculate_days_since_last_order(self) -> int:
        """Tage seit letzter Bestellung"""
        if not self.last_order_date:
            return -1
        return (date.today() - self.last_order_date).days
    
    def update_order_statistics(self, order_amount: Decimal, order_date: date):
        """Aktualisiert Bestellstatistiken"""
        if not self.first_order_date:
            self.first_order_date = order_date
        
        self.last_order_date = order_date
        self.total_orders += 1
        self.total_revenue += order_amount
        
        if self.total_orders > 0:
            self.average_order_value = self.total_revenue / Decimal(str(self.total_orders))
        
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str):
        """Tag hinzufügen"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """Tag entfernen"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def set_custom_field(self, key: str, value: Any):
        """Benutzerdefinierten Wert setzen"""
        self.custom_fields[key] = value
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'customer_id': self.customer_id,
            'customer_number': self.customer_number,
            'customer_type': self.customer_type.value,
            'status': self.status.value,
            
            'company_name': self.company_name,
            'brand_name': self.brand_name,
            'legal_form': self.legal_form,
            'industry': self.industry,
            'website': self.website,
            
            'tax_id': self.tax_id,
            'vat_id': self.vat_id,
            'commercial_register': self.commercial_register,
            'court_of_registration': self.court_of_registration,
            
            'addresses': [addr.to_dict() for addr in self.addresses],
            'contacts': [cont.to_dict() for cont in self.contacts],
            
            'payment_terms': self.payment_terms,
            'payment_method': self.payment_method,
            'credit_limit': str(self.credit_limit) if self.credit_limit else None,
            'payment_rating': self.payment_rating.value,
            'discount_percent': str(self.discount_percent),
            'currency': self.currency,
            
            'sales_representative': self.sales_representative,
            'customer_group': self.customer_group,
            'price_group': self.price_group,
            'marketing_consent': self.marketing_consent,
            'newsletter_consent': self.newsletter_consent,
            
            'source': self.source,
            'lead_date': self.lead_date.isoformat() if self.lead_date else None,
            'first_contact_date': self.first_contact_date.isoformat() if self.first_contact_date else None,
            'first_order_date': self.first_order_date.isoformat() if self.first_order_date else None,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'total_orders': self.total_orders,
            'total_revenue': str(self.total_revenue),
            'average_order_value': str(self.average_order_value),
            
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            
            'tags': self.tags,
            'categories': self.categories,
            'custom_fields': self.custom_fields,
            
            'data_processing_consent': self.data_processing_consent,
            'data_processing_consent_date': self.data_processing_consent_date.isoformat() if self.data_processing_consent_date else None,
            'data_retention_period': self.data_retention_period,
            'gdpr_notes': self.gdpr_notes,
            
            'preferred_language': self.preferred_language,
            'communication_preferences': self.communication_preferences,
            
            'attachments': self.attachments,
            'contracts': self.contracts,
            'certificates': self.certificates
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtendedCustomer':
        """Erstellt aus Dictionary"""
        customer = cls()
        
        customer.customer_id = data.get('customer_id', '')
        customer.customer_number = data.get('customer_number', '')
        customer.customer_type = CustomerType(data.get('customer_type', CustomerType.BUSINESS.value))
        customer.status = CustomerStatus(data.get('status', CustomerStatus.ACTIVE.value))
        
        customer.company_name = data.get('company_name', '')
        customer.brand_name = data.get('brand_name', '')
        customer.legal_form = data.get('legal_form', '')
        customer.industry = data.get('industry', '')
        customer.website = data.get('website', '')
        
        customer.tax_id = data.get('tax_id', '')
        customer.vat_id = data.get('vat_id', '')
        customer.commercial_register = data.get('commercial_register', '')
        customer.court_of_registration = data.get('court_of_registration', '')
        
        # Adressen und Kontakte
        customer.addresses = [Address.from_dict(addr_data) for addr_data in data.get('addresses', [])]
        customer.contacts = [Contact.from_dict(cont_data) for cont_data in data.get('contacts', [])]
        
        customer.payment_terms = data.get('payment_terms', 'NET_14')
        customer.payment_method = data.get('payment_method', 'BANK_TRANSFER')
        customer.credit_limit = Decimal(data['credit_limit']) if data.get('credit_limit') else None
        customer.payment_rating = PaymentRating(data.get('payment_rating', PaymentRating.UNKNOWN.value))
        customer.discount_percent = Decimal(data.get('discount_percent', '0'))
        customer.currency = data.get('currency', 'EUR')
        
        customer.sales_representative = data.get('sales_representative', '')
        customer.customer_group = data.get('customer_group', '')
        customer.price_group = data.get('price_group', '')
        customer.marketing_consent = data.get('marketing_consent', False)
        customer.newsletter_consent = data.get('newsletter_consent', False)
        
        customer.source = data.get('source', '')
        customer.lead_date = date.fromisoformat(data['lead_date']) if data.get('lead_date') else None
        customer.first_contact_date = date.fromisoformat(data['first_contact_date']) if data.get('first_contact_date') else None
        customer.first_order_date = date.fromisoformat(data['first_order_date']) if data.get('first_order_date') else None
        customer.last_order_date = date.fromisoformat(data['last_order_date']) if data.get('last_order_date') else None
        customer.total_orders = data.get('total_orders', 0)
        customer.total_revenue = Decimal(data.get('total_revenue', '0'))
        customer.average_order_value = Decimal(data.get('average_order_value', '0'))
        
        customer.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        customer.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        customer.created_by = data.get('created_by', '')
        customer.updated_by = data.get('updated_by', '')
        customer.notes = data.get('notes', '')
        customer.internal_notes = data.get('internal_notes', '')
        
        customer.tags = data.get('tags', [])
        customer.categories = data.get('categories', [])
        customer.custom_fields = data.get('custom_fields', {})
        
        customer.data_processing_consent = data.get('data_processing_consent', False)
        customer.data_processing_consent_date = date.fromisoformat(data['data_processing_consent_date']) if data.get('data_processing_consent_date') else None
        customer.data_retention_period = data.get('data_retention_period', 10)
        customer.gdpr_notes = data.get('gdpr_notes', '')
        
        customer.preferred_language = data.get('preferred_language', 'de')
        customer.communication_preferences = data.get('communication_preferences', {
            'email': True, 'phone': True, 'post': False, 'sms': False
        })
        
        customer.attachments = data.get('attachments', [])
        customer.contracts = data.get('contracts', [])
        customer.certificates = data.get('certificates', [])
        
        return customer


class Article:
    """Artikel/Produkt"""
    
    def __init__(self, article_id: Optional[str] = None, article_number: str = "",
                 name: str = "", description: str = ""):
        self.article_id = article_id or str(uuid.uuid4())
        self.article_number = article_number  # SKU
        self.name = name
        self.description = description
        self.long_description = ""
        
        # Kategorisierung
        self.category = ""
        self.subcategory = ""
        self.brand = ""
        self.manufacturer = ""
        self.supplier = ""
        
        # Preise
        self.purchase_price: Decimal = Decimal('0')
        self.selling_price: Decimal = Decimal('0')
        self.msrp: Decimal = Decimal('0')  # Unverbindliche Preisempfehlung
        self.currency = "EUR"
        self.tax_rate: Decimal = Decimal('19')
        
        # Einheiten und Verpackung
        self.unit = "Stück"
        self.package_size: Decimal = Decimal('1')
        self.minimum_order_quantity: Decimal = Decimal('1')
        self.weight: Optional[Decimal] = None
        self.dimensions = ""  # L x B x H
        self.volume: Optional[Decimal] = None
        
        # Lager und Verfügbarkeit
        self.stock_quantity: Decimal = Decimal('0')
        self.reserved_quantity: Decimal = Decimal('0')
        self.reorder_level: Decimal = Decimal('0')
        self.maximum_stock: Decimal = Decimal('0')
        self.location = ""  # Lagerplatz
        
        # Status
        self.is_active = True
        self.is_discontinued = False
        self.is_virtual = False  # Virtueller Artikel (Dienstleistung)
        self.requires_approval = False
        
        # Barcodes und Identifikation
        self.ean = ""  # European Article Number
        self.gtin = ""  # Global Trade Item Number
        self.upc = ""  # Universal Product Code
        self.isbn = ""  # Für Bücher
        
        # Metadaten
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.created_by = ""
        self.updated_by = ""
        self.notes = ""
        
        # SEO und Marketing
        self.seo_title = ""
        self.seo_description = ""
        self.keywords: List[str] = []
        self.images: List[str] = []
        self.documents: List[str] = []
        
        # Varianten und Optionen
        self.has_variants = False
        self.variant_attributes: Dict[str, List[str]] = {}  # Farbe: [Rot, Blau], Größe: [S, M, L]
        self.parent_article_id: Optional[str] = None
        
        # Preisgruppen und Rabatte
        self.price_groups: Dict[str, Decimal] = {}  # Gruppe -> Preis
        self.quantity_discounts: List[Dict[str, Any]] = []  # Mengenstaffeln
        
        # Steuerliche Besonderheiten
        self.tax_exempt = False
        self.tax_exempt_reason = ""
        self.customs_tariff_number = ""
        self.country_of_origin = ""
        
        # Tags und benutzerdefinierte Felder
        self.tags: List[str] = []
        self.custom_fields: Dict[str, Any] = {}
    
    def calculate_available_quantity(self) -> Decimal:
        """Verfügbare Menge berechnen"""
        return self.stock_quantity - self.reserved_quantity
    
    def is_in_stock(self) -> bool:
        """Prüft ob Artikel vorrätig"""
        return self.calculate_available_quantity() > 0
    
    def needs_reorder(self) -> bool:
        """Prüft ob Nachbestellung nötig"""
        return self.stock_quantity <= self.reorder_level
    
    def get_price_for_group(self, price_group: str) -> Decimal:
        """Preis für Preisgruppe ermitteln"""
        return self.price_groups.get(price_group, self.selling_price)
    
    def get_quantity_discount_price(self, quantity: Decimal) -> Decimal:
        """Preis mit Mengenstaffel ermitteln"""
        applicable_discount = None
        
        for discount in self.quantity_discounts:
            min_qty = Decimal(str(discount.get('min_quantity', 0)))
            if quantity >= min_qty:
                if not applicable_discount or min_qty > Decimal(str(applicable_discount.get('min_quantity', 0))):
                    applicable_discount = discount
        
        if applicable_discount:
            if 'price' in applicable_discount:
                return Decimal(str(applicable_discount['price']))
            elif 'discount_percent' in applicable_discount:
                discount_percent = Decimal(str(applicable_discount['discount_percent']))
                return self.selling_price * (Decimal('100') - discount_percent) / Decimal('100')
        
        return self.selling_price
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'article_id': self.article_id,
            'article_number': self.article_number,
            'name': self.name,
            'description': self.description,
            'long_description': self.long_description,
            
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'manufacturer': self.manufacturer,
            'supplier': self.supplier,
            
            'purchase_price': str(self.purchase_price),
            'selling_price': str(self.selling_price),
            'msrp': str(self.msrp),
            'currency': self.currency,
            'tax_rate': str(self.tax_rate),
            
            'unit': self.unit,
            'package_size': str(self.package_size),
            'minimum_order_quantity': str(self.minimum_order_quantity),
            'weight': str(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'volume': str(self.volume) if self.volume else None,
            
            'stock_quantity': str(self.stock_quantity),
            'reserved_quantity': str(self.reserved_quantity),
            'reorder_level': str(self.reorder_level),
            'maximum_stock': str(self.maximum_stock),
            'location': self.location,
            
            'is_active': self.is_active,
            'is_discontinued': self.is_discontinued,
            'is_virtual': self.is_virtual,
            'requires_approval': self.requires_approval,
            
            'ean': self.ean,
            'gtin': self.gtin,
            'upc': self.upc,
            'isbn': self.isbn,
            
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'notes': self.notes,
            
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'keywords': self.keywords,
            'images': self.images,
            'documents': self.documents,
            
            'has_variants': self.has_variants,
            'variant_attributes': self.variant_attributes,
            'parent_article_id': self.parent_article_id,
            
            'price_groups': {k: str(v) for k, v in self.price_groups.items()},
            'quantity_discounts': self.quantity_discounts,
            
            'tax_exempt': self.tax_exempt,
            'tax_exempt_reason': self.tax_exempt_reason,
            'customs_tariff_number': self.customs_tariff_number,
            'country_of_origin': self.country_of_origin,
            
            'tags': self.tags,
            'custom_fields': self.custom_fields
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Erstellt aus Dictionary"""
        article = cls()
        
        article.article_id = data.get('article_id', '')
        article.article_number = data.get('article_number', '')
        article.name = data.get('name', '')
        article.description = data.get('description', '')
        article.long_description = data.get('long_description', '')
        
        article.category = data.get('category', '')
        article.subcategory = data.get('subcategory', '')
        article.brand = data.get('brand', '')
        article.manufacturer = data.get('manufacturer', '')
        article.supplier = data.get('supplier', '')
        
        article.purchase_price = Decimal(data.get('purchase_price', '0'))
        article.selling_price = Decimal(data.get('selling_price', '0'))
        article.msrp = Decimal(data.get('msrp', '0'))
        article.currency = data.get('currency', 'EUR')
        article.tax_rate = Decimal(data.get('tax_rate', '19'))
        
        article.unit = data.get('unit', 'Stück')
        article.package_size = Decimal(data.get('package_size', '1'))
        article.minimum_order_quantity = Decimal(data.get('minimum_order_quantity', '1'))
        article.weight = Decimal(data['weight']) if data.get('weight') else None
        article.dimensions = data.get('dimensions', '')
        article.volume = Decimal(data['volume']) if data.get('volume') else None
        
        article.stock_quantity = Decimal(data.get('stock_quantity', '0'))
        article.reserved_quantity = Decimal(data.get('reserved_quantity', '0'))
        article.reorder_level = Decimal(data.get('reorder_level', '0'))
        article.maximum_stock = Decimal(data.get('maximum_stock', '0'))
        article.location = data.get('location', '')
        
        article.is_active = data.get('is_active', True)
        article.is_discontinued = data.get('is_discontinued', False)
        article.is_virtual = data.get('is_virtual', False)
        article.requires_approval = data.get('requires_approval', False)
        
        article.ean = data.get('ean', '')
        article.gtin = data.get('gtin', '')
        article.upc = data.get('upc', '')
        article.isbn = data.get('isbn', '')
        
        article.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        article.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        article.created_by = data.get('created_by', '')
        article.updated_by = data.get('updated_by', '')
        article.notes = data.get('notes', '')
        
        article.seo_title = data.get('seo_title', '')
        article.seo_description = data.get('seo_description', '')
        article.keywords = data.get('keywords', [])
        article.images = data.get('images', [])
        article.documents = data.get('documents', [])
        
        article.has_variants = data.get('has_variants', False)
        article.variant_attributes = data.get('variant_attributes', {})
        article.parent_article_id = data.get('parent_article_id')
        
        price_groups_data = data.get('price_groups', {})
        article.price_groups = {k: Decimal(str(v)) for k, v in price_groups_data.items()}
        article.quantity_discounts = data.get('quantity_discounts', [])
        
        article.tax_exempt = data.get('tax_exempt', False)
        article.tax_exempt_reason = data.get('tax_exempt_reason', '')
        article.customs_tariff_number = data.get('customs_tariff_number', '')
        article.country_of_origin = data.get('country_of_origin', '')
        
        article.tags = data.get('tags', [])
        article.custom_fields = data.get('custom_fields', {})
        
        return article
