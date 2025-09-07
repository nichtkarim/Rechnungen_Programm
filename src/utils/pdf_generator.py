"""
PDF-Export für Rechnungen
Erstellt professionelle PDF-Dokumente im DIN A4 Format
"""
import os
import io
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, List

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, grey
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import colors

from src.models import Invoice, CompanyData, DocumentType, TaxRate


class InvoicePDFGenerator:
    """PDF-Generator für Rechnungen"""
    
    def __init__(self, company_data: CompanyData, pdf_color: str = "#2E86AB", enable_qr_code: bool = True):
        self.company_data = company_data
        self.pdf_color = HexColor(pdf_color)
        self.enable_qr_code = enable_qr_code
        self.page_width, self.page_height = A4
        
        # Seitenränder
        self.margin_left = 2 * cm
        self.margin_right = 2 * cm
        self.margin_top = 2.5 * cm
        self.margin_bottom = 2 * cm
        
        # Verfügbare Breite für Inhalte
        self.content_width = self.page_width - self.margin_left - self.margin_right
        
        # Styles initialisieren
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Erstellt benutzerdefinierte Styles"""
        
        # Company Name Style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=self.pdf_color,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Company Address Style
        self.styles.add(ParagraphStyle(
            name='CompanyAddress',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=black,
            spaceAfter=3
        ))
        
        # Document Title Style
        self.styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=self.pdf_color,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Customer Address Style
        self.styles.add(ParagraphStyle(
            name='CustomerAddress',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Small Text Style
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=grey
        ))
        
        # Footer Style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=grey,
            alignment=TA_CENTER
        ))
    
    def _generate_girocode_qr(self, invoice: Invoice) -> Optional[Image]:
        """
        Generiert einen GiroCode QR-Code für die Rechnung
        Der QR-Code enthält alle Bankdaten für das Mobile Banking
        """
        if (not self.enable_qr_code or 
            not self.company_data.iban or 
            invoice.document_type != DocumentType.RECHNUNG):
            return None
        
        try:
            # GiroCode Format nach EPC-Standard
            # Format: [Service Tag][Version][Character set][Identification][BIC][Beneficiary Name][Beneficiary Account][Amount][Purpose][Remittance Reference][Remittance Text]
            
            amount = invoice.calculate_total_gross()
            
            # IBAN normalisieren (Leerzeichen entfernen, Großbuchstaben)
            clean_iban = self.company_data.iban.replace(" ", "").upper()
            
            # BIC normalisieren
            clean_bic = (self.company_data.bic or "").replace(" ", "").upper()
            
            # Name auf max. 70 Zeichen begrenzen
            beneficiary_name = self.company_data.name[:70]
            
            # Verwendungszweck erstellen
            reference = invoice.invoice_number[:35]  # Max 35 Zeichen
            remittance_info = f"Rechnung {invoice.invoice_number}"[:140]  # Max 140 Zeichen
            
            # GiroCode-Datenstring zusammenstellen
            girocode_data = [
                "BCD",  # Service Tag
                "002",  # Version (002 = aktueller Standard)
                "1",    # Character set (1 = UTF-8)
                "SCT",  # Identification (SCT = SEPA Credit Transfer)
                clean_bic,  # BIC (kann leer sein für deutsche IBANs)
                beneficiary_name,  # Empfängername
                clean_iban,  # IBAN
                f"EUR{amount:.2f}",  # Betrag in EUR mit 2 Dezimalstellen
                "",     # Purpose (leer für normale Überweisungen)
                reference,  # Structured reference (Rechnungsnummer)
                remittance_info  # Unstructured remittance information
            ]
            
            # QR-Code-String mit Zeilentrennung erstellen
            qr_string = "\n".join(girocode_data)
            
            # QR-Code mit optimalen Einstellungen generieren
            qr = qrcode.QRCode(
                version=1,  # Automatische Größenanpassung
                error_correction=qrcode.ERROR_CORRECT_M,  # Mittlere Fehlerkorrektur
                box_size=4,  # Größere Boxen für bessere Lesbarkeit
                border=2,    # Etwas größerer Rand
            )
            qr.add_data(qr_string)
            qr.make(fit=True)
            
            # QR-Code als PIL Image erstellen
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # PIL Image in BytesIO umwandeln für ReportLab
            img_buffer = io.BytesIO()
            qr_image.save(img_buffer, 'PNG')
            img_buffer.seek(0)
            
            # ReportLab Image erstellen mit fester Größe
            qr_reportlab_image = Image(img_buffer)
            qr_reportlab_image.drawHeight = 2.5 * cm  # Etwas kleiner für bessere Balance
            qr_reportlab_image.drawWidth = 2.5 * cm
            
            return qr_reportlab_image
            
        except Exception as e:
            print(f"Fehler beim Generieren des QR-Codes: {e}")
            return None
    
    def generate_pdf(self, invoice: Invoice, output_path: str) -> bool:
        """Generiert das PDF-Dokument"""
        try:
            # Stelle sicher, dass das Ausgabeverzeichnis existiert
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Erstelle das PDF-Dokument
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=self.margin_left,
                rightMargin=self.margin_right,
                topMargin=self.margin_top,
                bottomMargin=self.margin_bottom
            )
            
            # Story-Inhalt sammeln
            story = []
            
            # Header
            story.extend(self._build_header(invoice))
            
            # Kundenadresse
            story.extend(self._build_customer_address(invoice))
            
            # Dokumenttitel und Metadaten
            story.extend(self._build_document_title(invoice))
            
            # Positionstabelle
            story.extend(self._build_positions_table(invoice))
            
            # Summentabelle
            story.extend(self._build_totals_table(invoice))
            
            # Zahlungshinweise
            story.extend(self._build_payment_info(invoice))
            
            # Footer-Texte
            story.extend(self._build_footer_text(invoice))
            
            # Footer
            story.extend(self._build_footer())
            
            # PDF erstellen
            doc.build(story)
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Erstellen des PDFs: {e}")
            return False
    
    def _build_header(self, invoice: Invoice) -> List:
        """Erstellt den Header mit Firmenlogo und -daten"""
        elements = []
        
        # Zwei-Spalten-Layout für Logo und Firmendaten
        data = []
        
        # Logo (falls vorhanden)
        logo_cell = ""
        if self.company_data.logo_path and os.path.exists(self.company_data.logo_path):
            try:
                # Logo laden und skalieren
                logo = Image(self.company_data.logo_path)
                logo.drawHeight = 40
                logo.drawWidth = 40 * logo.imageWidth / logo.imageHeight
                logo_cell = logo
            except:
                logo_cell = ""
        
        # Firmendaten
        company_info = []
        company_info.append(Paragraph(self.company_data.name, self.styles['CompanyName']))
        
        address_lines = []
        if self.company_data.address_line1:
            address_lines.append(self.company_data.address_line1)
        if self.company_data.address_line2:
            address_lines.append(self.company_data.address_line2)
        if self.company_data.postal_code and self.company_data.city:
            address_lines.append(f"{self.company_data.postal_code} {self.company_data.city}")
        if self.company_data.country and self.company_data.country != "Deutschland":
            address_lines.append(self.company_data.country)
        
        for line in address_lines:
            company_info.append(Paragraph(line, self.styles['CompanyAddress']))
        
        # Kontaktdaten
        if self.company_data.phone:
            company_info.append(Paragraph(f"Tel: {self.company_data.phone}", self.styles['CompanyAddress']))
        if self.company_data.email:
            company_info.append(Paragraph(f"E-Mail: {self.company_data.email}", self.styles['CompanyAddress']))
        if self.company_data.website:
            company_info.append(Paragraph(f"Web: {self.company_data.website}", self.styles['CompanyAddress']))
        
        # Header-Tabelle
        if logo_cell:
            header_data = [[logo_cell, company_info]]
            header_table = Table(header_data, colWidths=[60, self.content_width - 60])
        else:
            header_data = [[company_info]]
            header_table = Table(header_data, colWidths=[self.content_width])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_customer_address(self, invoice: Invoice) -> List:
        """Erstellt die Kundenadresse"""
        elements = []
        
        if not invoice.customer:
            return elements
        
        customer = invoice.customer
        
        # Adressfeld mit Absenderzeile (klein)
        sender_line = f"{self.company_data.name}, {self.company_data.address_line1}, {self.company_data.postal_code} {self.company_data.city}"
        elements.append(Paragraph(sender_line, self.styles['SmallText']))
        elements.append(Spacer(1, 6))
        
        # Kundenadresse
        address_lines = []
        if customer.company_name:
            address_lines.append(customer.company_name)
        if customer.contact_person:
            address_lines.append(customer.contact_person)
        if customer.address_line1:
            address_lines.append(customer.address_line1)
        if customer.address_line2:
            address_lines.append(customer.address_line2)
        if customer.postal_code and customer.city:
            address_lines.append(f"{customer.postal_code} {customer.city}")
        if customer.country and customer.country != "Deutschland":
            address_lines.append(customer.country)
        
        for line in address_lines:
            elements.append(Paragraph(line, self.styles['CustomerAddress']))
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_document_title(self, invoice: Invoice) -> List:
        """Erstellt den Dokumenttitel und Metadaten"""
        elements = []
        
        # Dokumenttitel
        title = invoice.document_type.value
        elements.append(Paragraph(title, self.styles['DocumentTitle']))
        
        # Metadaten-Tabelle
        meta_data = []
        
        # Rechnungsnummer
        meta_data.append([f"{invoice.document_type.value}snummer:", invoice.invoice_number])
        
        # Rechnungsdatum
        date_str = invoice.invoice_date.strftime("%d.%m.%Y")
        meta_data.append([f"{invoice.document_type.value}sdatum:", date_str])
        
        # Leistungsdatum
        if invoice.service_date:
            service_date_str = invoice.service_date.strftime("%d.%m.%Y")
            meta_data.append(["Leistungsdatum:", service_date_str])
        
        # Kundennummer
        if invoice.customer and invoice.customer.customer_number:
            meta_data.append(["Kundennummer:", invoice.customer.customer_number])
        
        # Angebotsnummer bei Rechnung
        if invoice.document_type == DocumentType.RECHNUNG and invoice.offer_number:
            meta_data.append(["Angebotsnummer:", invoice.offer_number])
        
        # Referenz bei Gutschrift/Storno
        if (invoice.document_type in [DocumentType.GUTSCHRIFT, DocumentType.STORNO] 
            and invoice.reference_invoice_id):
            meta_data.append(["Referenz:", invoice.reference_invoice_id])
        
        meta_table = Table(meta_data, colWidths=[4*cm, 6*cm])
        meta_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (0, -1), 0),
            ('RIGHTPADDING', (1, 0), (1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(meta_table)
        elements.append(Spacer(1, 20))
        
        # Header-Text
        if invoice.header_text:
            elements.append(Paragraph(invoice.header_text, self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _build_positions_table(self, invoice: Invoice) -> List:
        """Erstellt die Positionstabelle"""
        elements = []
        
        if not invoice.positions:
            return elements
        
        # Tabellenkopf
        headers = [
            "Pos.",
            "Beschreibung",
            "Menge",
            "Einheit",
            "Einzelpreis €",
            "Rabatt %",
            "MwSt. %",
            "Gesamt €"
        ]
        
        # Spaltenbreiten
        col_widths = [1*cm, 6*cm, 1.5*cm, 1.5*cm, 2*cm, 1.5*cm, 1.5*cm, 2*cm]
        
        table_data = [headers]
        
        # Positionen
        for pos in invoice.positions:
            row = [
                str(pos.position_number),
                pos.description,
                f"{pos.quantity:,.2f}".replace('.', ','),
                pos.unit,
                f"{pos.unit_price:,.2f}".replace('.', ','),
                f"{pos.discount_percent:,.1f}".replace('.', ',') if pos.discount_percent > 0 else "-",
                f"{pos.tax_rate.value * 100:,.0f}",
                f"{pos.calculate_line_total_net():,.2f}".replace('.', ',')
            ]
            table_data.append(row)
        
        # Tabelle erstellen
        positions_table = Table(table_data, colWidths=col_widths)
        
        # Tabellenstyle
        style = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.pdf_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            
            # Datenzeilen
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            
            # Ausrichtung
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Pos.
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Menge
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),   # Einzelpreis
            ('ALIGN', (5, 0), (5, -1), 'RIGHT'),   # Rabatt
            ('ALIGN', (6, 0), (6, -1), 'CENTER'),  # MwSt.
            ('ALIGN', (7, 0), (7, -1), 'RIGHT'),   # Gesamt
            
            # Vertikale Ausrichtung
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # Rahmen
            ('GRID', (0, 0), (-1, -1), 0.5, black),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        # Zebra-Streifen für bessere Lesbarkeit
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
        
        positions_table.setStyle(TableStyle(style))
        
        elements.append(positions_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_totals_table(self, invoice: Invoice) -> List:
        """Erstellt die Summentabelle"""
        elements = []
        
        # Summentabelle rechtsbündig
        totals_data = []
        
        # Netto-Summen nach Steuersatz
        net_totals = invoice.calculate_net_totals_by_tax_rate()
        tax_totals = invoice.calculate_tax_totals_by_rate()
        
        # Zwischensumme Netto
        total_net = invoice.calculate_total_net()
        totals_data.append(["Zwischensumme (netto):", f"{total_net:,.2f} €".replace('.', ',')])
        
        # Steueraufschlüsselung
        for tax_rate in sorted(net_totals.keys(), key=lambda x: x.value):
            net_amount = net_totals[tax_rate]
            tax_amount = tax_totals[tax_rate]
            
            if net_amount > 0:
                tax_percent = tax_rate.value * 100
                totals_data.append([
                    f"zzgl. {tax_percent:,.0f}% MwSt. auf {net_amount:,.2f} €:".replace('.', ','),
                    f"{tax_amount:,.2f} €".replace('.', ',')
                ])
        
        # Kleinunternehmer-Hinweis
        if self.company_data.is_small_business:
            totals_data.append([
                "Gemäß §19 UStG wird keine MwSt. berechnet.", ""
            ])
        
        # Reverse Charge Hinweis
        if invoice.has_reverse_charge() and not self.company_data.is_small_business:
            totals_data.append([
                "Steuerschuldnerschaft des Leistungsempfängers", ""
            ])
        
        # Gesamtsumme
        total_gross = invoice.calculate_total_gross()
        totals_data.append(["", ""])  # Leerzeile
        totals_data.append([
            "Gesamtbetrag:", 
            f"{total_gross:,.2f} €".replace('.', ',')
        ])
        
        # Tabelle erstellen (rechtsbündig)
        totals_table = Table(totals_data, colWidths=[8*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Linie über Gesamtbetrag
            ('LINEABOVE', (0, -1), (-1, -1), 1, black),
        ]))
        
        # Rechtsbündig positionieren
        right_aligned_table = Table([[totals_table]], colWidths=[self.content_width])
        right_aligned_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(right_aligned_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_payment_info(self, invoice: Invoice) -> List:
        """Erstellt die Zahlungsinformationen mit QR-Code"""
        elements = []
        
        if invoice.document_type != DocumentType.RECHNUNG:
            return elements
        
        # Zahlungstext
        payment_text = invoice.payment_info_text or invoice.get_default_payment_text()
        if payment_text:
            elements.append(Paragraph(payment_text, self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # QR-Code und Bankdaten in einer Tabelle nebeneinander
        qr_code = self._generate_girocode_qr(invoice)
        
        if self.company_data.iban:
            # Bankdaten-Text
            bank_info = "<b>Bankverbindung:</b><br/>"
            if self.company_data.bank_name:
                bank_info += f"Bank: {self.company_data.bank_name}<br/>"
            bank_info += f"IBAN: {self.company_data.iban}<br/>"
            if self.company_data.bic:
                bank_info += f"BIC: {self.company_data.bic}<br/>"
            
            bank_paragraph = Paragraph(bank_info, self.styles['Normal'])
            
            if qr_code:
                # QR-Code-Beschreibung
                qr_description = Paragraph(
                    "<b>QR-Code scannen für Überweisung:</b><br/>"
                    "Mit Ihrer Banking-App scannen für<br/>"
                    "automatische Überweisung mit allen<br/>"
                    "Daten (Betrag, IBAN, Verwendungszweck)",
                    self.styles['SmallText']
                )
                
                # Tabelle mit Bankdaten und QR-Code
                payment_data = [
                    [bank_paragraph, qr_code],
                    ["", qr_description]
                ]
                
                payment_table = Table(payment_data, colWidths=[9*cm, 3.5*cm])
                payment_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    # Dünner Rahmen um QR-Code-Bereich
                    ('BOX', (1, 0), (1, 1), 0.5, colors.lightgrey),
                    ('BACKGROUND', (1, 0), (1, 1), colors.whitesmoke),
                ]))
                
                elements.append(payment_table)
            else:
                # Nur Bankdaten ohne QR-Code
                elements.append(bank_paragraph)
            
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _build_footer_text(self, invoice: Invoice) -> List:
        """Erstellt Footer-Texte"""
        elements = []
        
        if invoice.footer_text:
            elements.append(Paragraph(invoice.footer_text, self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _build_footer(self) -> List:
        """Erstellt den Footer mit Firmendaten"""
        elements = []
        
        # Spacer to push footer to bottom
        elements.append(Spacer(1, 30))
        
        # Footer-Linie
        footer_data = [[""]]
        footer_line = Table(footer_data, colWidths=[self.content_width])
        footer_line.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, self.pdf_color),
        ]))
        elements.append(footer_line)
        elements.append(Spacer(1, 6))
        
        # Footer-Inhalte in drei Spalten
        left_content = []
        if self.company_data.name:
            left_content.append(self.company_data.name)
        if self.company_data.address_line1:
            left_content.append(self.company_data.address_line1)
        if self.company_data.postal_code and self.company_data.city:
            left_content.append(f"{self.company_data.postal_code} {self.company_data.city}")
        
        middle_content = []
        if self.company_data.phone:
            middle_content.append(f"Tel: {self.company_data.phone}")
        if self.company_data.email:
            middle_content.append(f"E-Mail: {self.company_data.email}")
        if self.company_data.website:
            middle_content.append(f"Web: {self.company_data.website}")
        
        right_content = []
        if self.company_data.tax_number:
            right_content.append(f"Steuernr.: {self.company_data.tax_number}")
        if self.company_data.vat_id:
            right_content.append(f"USt-IdNr.: {self.company_data.vat_id}")
        if self.company_data.iban:
            right_content.append(f"IBAN: {self.company_data.iban}")
        
        footer_content = [
            Paragraph("<br/>".join(left_content), self.styles['Footer']),
            Paragraph("<br/>".join(middle_content), self.styles['Footer']),
            Paragraph("<br/>".join(right_content), self.styles['Footer'])
        ]
        
        footer_table = Table([footer_content], colWidths=[
            self.content_width / 3,
            self.content_width / 3,
            self.content_width / 3
        ])
        footer_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(footer_table)
        
        return elements
