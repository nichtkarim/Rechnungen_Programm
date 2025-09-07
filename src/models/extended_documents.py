"""
Erweiterte Dokumenttypen für das Rechnungs-Tool
"""
from enum import Enum
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
import uuid


class DocumentType(Enum):
    """Erweiterte Dokumenttypen"""
    INVOICE = "Rechnung"
    QUOTE = "Angebot"
    CREDIT_NOTE = "Gutschrift"
    CANCELLATION = "Storno"
    DELIVERY_NOTE = "Lieferschein"
    ORDER_CONFIRMATION = "Auftragsbestätigung"
    REMINDER = "Mahnung"
    DUNNING = "Inkassomahnung"
    PROFORMA = "Proforma-Rechnung"
    RECEIPT = "Quittung"
    CONTRACT = "Vertrag"
    OFFER_REQUEST = "Anfrage"
    PURCHASE_ORDER = "Bestellung"
    EXPENSE_REPORT = "Ausgabenbericht"
    TIMESHEET = "Stundenzettel"


class DocumentStatus(Enum):
    """Dokumentstatus"""
    DRAFT = "Entwurf"
    SENT = "Versendet"
    ACCEPTED = "Angenommen"
    REJECTED = "Abgelehnt"
    PAID = "Bezahlt"
    OVERDUE = "Überfällig"
    CANCELLED = "Storniert"
    COMPLETED = "Abgeschlossen"


class PaymentMethod(Enum):
    """Zahlungsmethoden"""
    BANK_TRANSFER = "Überweisung"
    CASH = "Barzahlung"
    CREDIT_CARD = "Kreditkarte"
    PAYPAL = "PayPal"
    DIRECT_DEBIT = "Lastschrift"
    CHECK = "Scheck"
    BITCOIN = "Bitcoin"
    OTHER = "Sonstiges"


class PaymentTerms(Enum):
    """Zahlungsbedingungen"""
    IMMEDIATE = "Sofort"
    NET_7 = "7 Tage netto"
    NET_14 = "14 Tage netto"
    NET_30 = "30 Tage netto"
    NET_60 = "60 Tage netto"
    NET_90 = "90 Tage netto"
    CASH_DISCOUNT_2_7 = "2% bei 7 Tagen, sonst 30 Tage netto"
    CASH_DISCOUNT_3_10 = "3% bei 10 Tagen, sonst 30 Tage netto"
    END_OF_MONTH = "Zahlbar bis Monatsende"
    PARTIAL_PAYMENT = "Teilzahlung"


class DeliveryTerms(Enum):
    """Lieferbedingungen (Incoterms)"""
    EXW = "EXW - Ex Works"
    FCA = "FCA - Free Carrier"
    CPT = "CPT - Carriage Paid To"
    CIP = "CIP - Carriage and Insurance Paid To"
    DAP = "DAP - Delivered At Place"
    DPU = "DPU - Delivered At Place Unloaded"
    DDP = "DDP - Delivered Duty Paid"
    FAS = "FAS - Free Alongside Ship"
    FOB = "FOB - Free On Board"
    CFR = "CFR - Cost and Freight"
    CIF = "CIF - Cost, Insurance and Freight"


class Priority(Enum):
    """Prioritätsstufen"""
    LOW = "Niedrig"
    NORMAL = "Normal"
    HIGH = "Hoch"
    URGENT = "Dringend"
    CRITICAL = "Kritisch"


class Project:
    """Projekt für Zuordnung von Dokumenten"""
    
    def __init__(self, project_id: Optional[str] = None, name: str = "", description: str = "", 
                 start_date: Optional[date] = None, end_date: Optional[date] = None, 
                 budget: Optional[Decimal] = None, customer_id: Optional[str] = None):
        self.project_id = project_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.customer_id = customer_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = "Aktiv"
        self.tags: List[str] = []
        self.custom_fields: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'budget': str(self.budget) if self.budget else None,
            'customer_id': self.customer_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status,
            'tags': self.tags,
            'custom_fields': self.custom_fields
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Erstellt aus Dictionary"""
        project = cls()
        project.project_id = data.get('project_id', '')
        project.name = data.get('name', '')
        project.description = data.get('description', '')
        
        if data.get('start_date'):
            project.start_date = date.fromisoformat(data['start_date'])
        if data.get('end_date'):
            project.end_date = date.fromisoformat(data['end_date'])
        if data.get('budget'):
            project.budget = Decimal(data['budget'])
        
        project.customer_id = data.get('customer_id')
        project.created_at = datetime.fromisoformat(data['created_at'])
        project.updated_at = datetime.fromisoformat(data['updated_at'])
        project.status = data.get('status', 'Aktiv')
        project.tags = data.get('tags', [])
        project.custom_fields = data.get('custom_fields', {})
        
        return project


class ExtendedDocumentItem:
    """Erweiterte Dokumentposition"""
    
    def __init__(self, item_id: Optional[str] = None, description: str = "", quantity: Optional[Decimal] = None,
                 unit_price: Optional[Decimal] = None, unit: str = "Stück", discount_percent: Optional[Decimal] = None,
                 discount_amount: Optional[Decimal] = None, tax_rate: Optional[Decimal] = None,
                 category: str = "", sku: str = "", weight: Optional[Decimal] = None,
                 dimensions: str = "", notes: str = ""):
        self.item_id = item_id or str(uuid.uuid4())
        self.description = description
        self.quantity = quantity or Decimal('1')
        self.unit_price = unit_price or Decimal('0')
        self.unit = unit
        self.discount_percent = discount_percent or Decimal('0')
        self.discount_amount = discount_amount or Decimal('0')
        self.tax_rate = tax_rate or Decimal('19')
        self.category = category
        self.sku = sku  # Stock Keeping Unit / Artikelnummer
        self.weight = weight
        self.dimensions = dimensions
        self.notes = notes
        
        # Berechnete Felder
        self.line_total_net = self.calculate_line_total_net()
        self.line_total_gross = self.calculate_line_total_gross()
        self.tax_amount = self.calculate_tax_amount()
    
    def calculate_line_total_net(self) -> Decimal:
        """Berechnet Netto-Zeilensumme"""
        subtotal = self.quantity * self.unit_price
        
        # Prozentrabatt anwenden
        if self.discount_percent > 0:
            subtotal = subtotal * (Decimal('100') - self.discount_percent) / Decimal('100')
        
        # Absolutrabatt anwenden
        if self.discount_amount > 0:
            subtotal = subtotal - self.discount_amount
        
        return max(subtotal, Decimal('0'))
    
    def calculate_tax_amount(self) -> Decimal:
        """Berechnet Steuerbetrag"""
        return self.line_total_net * self.tax_rate / Decimal('100')
    
    def calculate_line_total_gross(self) -> Decimal:
        """Berechnet Brutto-Zeilensumme"""
        return self.line_total_net + self.calculate_tax_amount()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'item_id': self.item_id,
            'description': self.description,
            'quantity': str(self.quantity),
            'unit_price': str(self.unit_price),
            'unit': self.unit,
            'discount_percent': str(self.discount_percent),
            'discount_amount': str(self.discount_amount),
            'tax_rate': str(self.tax_rate),
            'category': self.category,
            'sku': self.sku,
            'weight': str(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'notes': self.notes,
            'line_total_net': str(self.line_total_net),
            'line_total_gross': str(self.line_total_gross),
            'tax_amount': str(self.tax_amount)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtendedDocumentItem':
        """Erstellt aus Dictionary"""
        item = cls()
        item.item_id = data.get('item_id', '')
        item.description = data.get('description', '')
        item.quantity = Decimal(data.get('quantity', '1'))
        item.unit_price = Decimal(data.get('unit_price', '0'))
        item.unit = data.get('unit', 'Stück')
        item.discount_percent = Decimal(data.get('discount_percent', '0'))
        item.discount_amount = Decimal(data.get('discount_amount', '0'))
        item.tax_rate = Decimal(data.get('tax_rate', '19'))
        item.category = data.get('category', '')
        item.sku = data.get('sku', '')
        item.weight = Decimal(data['weight']) if data.get('weight') else None
        item.dimensions = data.get('dimensions', '')
        item.notes = data.get('notes', '')
        
        # Werte neu berechnen
        item.line_total_net = item.calculate_line_total_net()
        item.line_total_gross = item.calculate_line_total_gross()
        item.tax_amount = item.calculate_tax_amount()
        
        return item


class ExtendedDocument:
    """Erweiterte Dokumentklasse"""
    
    def __init__(self, document_id: Optional[str] = None, document_type: DocumentType = DocumentType.INVOICE,
                 document_number: str = "", title: str = "", customer=None, 
                 document_date: Optional[date] = None, due_date: Optional[date] = None):
        self.document_id = document_id or str(uuid.uuid4())
        self.document_type = document_type
        self.document_number = document_number
        self.title = title
        self.customer = customer
        self.document_date = document_date or date.today()
        self.due_date = due_date
        
        # Status und Workflow
        self.status = DocumentStatus.DRAFT
        self.priority = Priority.NORMAL
        self.workflow_stage = "Erstellt"
        self.approval_required = False
        self.approved_by = None
        self.approved_at = None
        
        # Zahlungsinformationen
        self.payment_method = PaymentMethod.BANK_TRANSFER
        self.payment_terms = PaymentTerms.NET_14
        self.payment_reference = ""
        self.payment_date = None
        self.payment_amount = None
        
        # Versand und Lieferung
        self.delivery_terms: Optional[DeliveryTerms] = None
        self.delivery_date: Optional[date] = None
        self.delivery_address = ""
        self.shipping_method = ""
        self.tracking_number = ""
        
        # Projekt- und Kategoriezuordnung
        self.project_id: Optional[str] = None
        self.category = ""
        self.department = ""
        self.cost_center = ""
        
        # Dokumentinhalt
        self.items: List[ExtendedDocumentItem] = []
        self.notes = ""
        self.internal_notes = ""
        self.terms_and_conditions = ""
        self.footer_text = ""
        
        # Rabatte und Zuschläge auf Dokumentebene
        self.discount_percent = Decimal('0')
        self.discount_amount = Decimal('0')
        self.shipping_cost = Decimal('0')
        self.handling_fee = Decimal('0')
        self.additional_costs = Decimal('0')
        
        # Währung und Steuern
        self.currency = "EUR"
        self.exchange_rate = Decimal('1')
        self.tax_exempt = False
        self.tax_exempt_reason = ""
        self.reverse_charge = False
        
        # Metadaten
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.created_by = ""
        self.updated_by = ""
        self.version = 1
        self.revision_history: List[Dict[str, Any]] = []
        
        # Anhänge und Verknüpfungen
        self.attachments: List[str] = []
        self.related_documents: List[str] = []
        self.parent_document_id = None
        
        # Tags und benutzerdefinierte Felder
        self.tags: List[str] = []
        self.custom_fields: Dict[str, Any] = {}
        
        # E-Mail und Kommunikation
        self.email_sent = False
        self.email_sent_at = None
        self.email_recipients: List[str] = []
        self.last_reminder_sent = None
        self.reminder_count = 0
    
    def calculate_subtotal(self) -> Decimal:
        """Berechnet Zwischensumme aller Positionen (netto)"""
        if not self.items:
            return Decimal('0')
        return Decimal(str(sum(item.line_total_net for item in self.items)))
    
    def calculate_discount_amount(self) -> Decimal:
        """Berechnet Gesamtrabatt"""
        subtotal = self.calculate_subtotal()
        discount = Decimal('0')
        
        if self.discount_percent > 0:
            discount += subtotal * self.discount_percent / Decimal('100')
        
        discount += self.discount_amount
        return discount
    
    def calculate_net_total(self) -> Decimal:
        """Berechnet Netto-Gesamtsumme"""
        subtotal = self.calculate_subtotal()
        discount = self.calculate_discount_amount()
        additional = self.shipping_cost + self.handling_fee + self.additional_costs
        return subtotal - discount + additional
    
    def calculate_tax_amounts(self) -> Dict[str, Decimal]:
        """Berechnet Steuerbeträge nach Steuersätzen"""
        tax_amounts = {}
        net_total = self.calculate_net_total()
        
        if self.tax_exempt:
            return tax_amounts
        
        # Steuern auf Positionsebene
        for item in self.items:
            rate = str(item.tax_rate)
            if rate not in tax_amounts:
                tax_amounts[rate] = Decimal('0')
            tax_amounts[rate] += item.calculate_tax_amount()
        
        # Proportionale Verteilung von Rabatten und Zusatzkosten auf Steuersätze
        if self.discount_amount > 0 or self.shipping_cost > 0 or self.handling_fee > 0 or self.additional_costs > 0:
            # Vereinfachte Implementierung - proportional zur Steuersumme
            pass
        
        return tax_amounts
    
    def calculate_total_tax(self) -> Decimal:
        """Berechnet Gesamtsteuerbetrag"""
        tax_amounts = self.calculate_tax_amounts().values()
        return Decimal(str(sum(tax_amounts)))
    
    def calculate_gross_total(self) -> Decimal:
        """Berechnet Brutto-Gesamtsumme"""
        return self.calculate_net_total() + self.calculate_total_tax()
    
    def is_overdue(self) -> bool:
        """Prüft ob Dokument überfällig ist"""
        if not self.due_date or self.status in [DocumentStatus.PAID, DocumentStatus.CANCELLED]:
            return False
        return date.today() > self.due_date
    
    def days_overdue(self) -> int:
        """Anzahl Tage überfällig"""
        if not self.is_overdue() or not self.due_date:
            return 0
        return (date.today() - self.due_date).days
    
    def add_item(self, item: ExtendedDocumentItem):
        """Fügt Position hinzu"""
        self.items.append(item)
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: str):
        """Entfernt Position"""
        self.items = [item for item in self.items if item.item_id != item_id]
        self.updated_at = datetime.now()
    
    def update_item(self, item_id: str, updated_item: ExtendedDocumentItem):
        """Aktualisiert Position"""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                self.items[i] = updated_item
                self.updated_at = datetime.now()
                break
    
    def add_tag(self, tag: str):
        """Fügt Tag hinzu"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Entfernt Tag"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def set_custom_field(self, key: str, value: Any):
        """Setzt benutzerdefinierten Wert"""
        self.custom_fields[key] = value
        self.updated_at = datetime.now()
    
    def get_custom_field(self, key: str, default: Any = None) -> Any:
        """Gibt benutzerdefinierten Wert zurück"""
        return self.custom_fields.get(key, default)
    
    def create_revision(self, reason: str = ""):
        """Erstellt neue Revision"""
        revision = {
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'created_by': self.updated_by,
            'changes': {}  # Hier könnten konkrete Änderungen gespeichert werden
        }
        self.revision_history.append(revision)
        self.version += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'document_id': self.document_id,
            'document_type': self.document_type.value,
            'document_number': self.document_number,
            'title': self.title,
            'customer': self.customer.to_dict() if self.customer else None,
            'document_date': self.document_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            
            'status': self.status.value,
            'priority': self.priority.value,
            'workflow_stage': self.workflow_stage,
            'approval_required': self.approval_required,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            
            'payment_method': self.payment_method.value,
            'payment_terms': self.payment_terms.value,
            'payment_reference': self.payment_reference,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_amount': str(self.payment_amount) if self.payment_amount else None,
            
            'delivery_terms': self.delivery_terms.value if self.delivery_terms else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_address': self.delivery_address,
            'shipping_method': self.shipping_method,
            'tracking_number': self.tracking_number,
            
            'project_id': self.project_id,
            'category': self.category,
            'department': self.department,
            'cost_center': self.cost_center,
            
            'items': [item.to_dict() for item in self.items],
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'terms_and_conditions': self.terms_and_conditions,
            'footer_text': self.footer_text,
            
            'discount_percent': str(self.discount_percent),
            'discount_amount': str(self.discount_amount),
            'shipping_cost': str(self.shipping_cost),
            'handling_fee': str(self.handling_fee),
            'additional_costs': str(self.additional_costs),
            
            'currency': self.currency,
            'exchange_rate': str(self.exchange_rate),
            'tax_exempt': self.tax_exempt,
            'tax_exempt_reason': self.tax_exempt_reason,
            'reverse_charge': self.reverse_charge,
            
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'version': self.version,
            'revision_history': self.revision_history,
            
            'attachments': self.attachments,
            'related_documents': self.related_documents,
            'parent_document_id': self.parent_document_id,
            
            'tags': self.tags,
            'custom_fields': self.custom_fields,
            
            'email_sent': self.email_sent,
            'email_sent_at': self.email_sent_at.isoformat() if self.email_sent_at else None,
            'email_recipients': self.email_recipients,
            'last_reminder_sent': self.last_reminder_sent.isoformat() if self.last_reminder_sent else None,
            'reminder_count': self.reminder_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtendedDocument':
        """Erstellt aus Dictionary"""
        doc = cls()
        doc.document_id = data.get('document_id', '')
        doc.document_type = DocumentType(data.get('document_type', DocumentType.INVOICE.value))
        doc.document_number = data.get('document_number', '')
        doc.title = data.get('title', '')
        # customer wird separat geladen
        doc.document_date = date.fromisoformat(data['document_date']) if data.get('document_date') else date.today()
        doc.due_date = date.fromisoformat(data['due_date']) if data.get('due_date') else None
        
        doc.status = DocumentStatus(data.get('status', DocumentStatus.DRAFT.value))
        doc.priority = Priority(data.get('priority', Priority.NORMAL.value))
        doc.workflow_stage = data.get('workflow_stage', 'Erstellt')
        doc.approval_required = data.get('approval_required', False)
        doc.approved_by = data.get('approved_by')
        doc.approved_at = datetime.fromisoformat(data['approved_at']) if data.get('approved_at') else None
        
        doc.payment_method = PaymentMethod(data.get('payment_method', PaymentMethod.BANK_TRANSFER.value))
        doc.payment_terms = PaymentTerms(data.get('payment_terms', PaymentTerms.NET_14.value))
        doc.payment_reference = data.get('payment_reference', '')
        doc.payment_date = date.fromisoformat(data['payment_date']) if data.get('payment_date') else None
        doc.payment_amount = Decimal(data['payment_amount']) if data.get('payment_amount') else None
        
        if data.get('delivery_terms'):
            doc.delivery_terms = DeliveryTerms(data['delivery_terms'])
        doc.delivery_date = date.fromisoformat(data['delivery_date']) if data.get('delivery_date') else None
        doc.delivery_address = data.get('delivery_address', '')
        doc.shipping_method = data.get('shipping_method', '')
        doc.tracking_number = data.get('tracking_number', '')
        
        doc.project_id = data.get('project_id')
        doc.category = data.get('category', '')
        doc.department = data.get('department', '')
        doc.cost_center = data.get('cost_center', '')
        
        # Items laden
        doc.items = [ExtendedDocumentItem.from_dict(item_data) for item_data in data.get('items', [])]
        
        doc.notes = data.get('notes', '')
        doc.internal_notes = data.get('internal_notes', '')
        doc.terms_and_conditions = data.get('terms_and_conditions', '')
        doc.footer_text = data.get('footer_text', '')
        
        doc.discount_percent = Decimal(data.get('discount_percent', '0'))
        doc.discount_amount = Decimal(data.get('discount_amount', '0'))
        doc.shipping_cost = Decimal(data.get('shipping_cost', '0'))
        doc.handling_fee = Decimal(data.get('handling_fee', '0'))
        doc.additional_costs = Decimal(data.get('additional_costs', '0'))
        
        doc.currency = data.get('currency', 'EUR')
        doc.exchange_rate = Decimal(data.get('exchange_rate', '1'))
        doc.tax_exempt = data.get('tax_exempt', False)
        doc.tax_exempt_reason = data.get('tax_exempt_reason', '')
        doc.reverse_charge = data.get('reverse_charge', False)
        
        doc.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        doc.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        doc.created_by = data.get('created_by', '')
        doc.updated_by = data.get('updated_by', '')
        doc.version = data.get('version', 1)
        doc.revision_history = data.get('revision_history', [])
        
        doc.attachments = data.get('attachments', [])
        doc.related_documents = data.get('related_documents', [])
        doc.parent_document_id = data.get('parent_document_id')
        
        doc.tags = data.get('tags', [])
        doc.custom_fields = data.get('custom_fields', {})
        
        doc.email_sent = data.get('email_sent', False)
        doc.email_sent_at = datetime.fromisoformat(data['email_sent_at']) if data.get('email_sent_at') else None
        doc.email_recipients = data.get('email_recipients', [])
        doc.last_reminder_sent = datetime.fromisoformat(data['last_reminder_sent']) if data.get('last_reminder_sent') else None
        doc.reminder_count = data.get('reminder_count', 0)
        
        return doc


def create_document_from_template(template_type: DocumentType, customer=None, project_id: Optional[str] = None) -> ExtendedDocument:
    """Erstellt Dokument aus Vorlage"""
    doc = ExtendedDocument(
        document_type=template_type,
        customer=customer
    )
    
    # Projekt zuordnen falls angegeben
    if project_id:
        doc.project_id = project_id
    
    # Standardwerte je nach Dokumenttyp
    if template_type == DocumentType.QUOTE:
        doc.due_date = date.today() + timedelta(days=30)  # Angebote 30 Tage gültig
        doc.terms_and_conditions = "Angebot gültig 30 Tage. Preise verstehen sich zzgl. MwSt."
        
    elif template_type == DocumentType.INVOICE:
        doc.due_date = date.today() + timedelta(days=14)  # Zahlungsziel 14 Tage
        doc.payment_terms = PaymentTerms.NET_14
        
    elif template_type == DocumentType.REMINDER:
        doc.priority = Priority.HIGH
        doc.due_date = date.today() + timedelta(days=7)  # Zahlung binnen 7 Tagen
        
    elif template_type == DocumentType.DELIVERY_NOTE:
        doc.delivery_date = date.today()
        doc.tax_exempt = True  # Lieferscheine oft ohne MwSt.
        doc.tax_exempt_reason = "Lieferschein"
        
    elif template_type == DocumentType.PROFORMA:
        doc.due_date = date.today() + timedelta(days=7)  # Proforma oft kurzfristig
        doc.notes = "Proforma-Rechnung - keine Zahlungsaufforderung"
    
    return doc
