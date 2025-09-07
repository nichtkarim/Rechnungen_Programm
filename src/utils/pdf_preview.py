"""
PDF-Vorschau und erweiterte Export-Funktionen
"""
import tempfile
import webbrowser
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import os

from src.models import Invoice, CompanyData
from src.utils.pdf_generator import InvoicePDFGenerator


class PDFPreviewManager:
    """Verwaltet PDF-Vorschau und erweiterte Export-Optionen"""
    
    def __init__(self, company_data: CompanyData, pdf_color: str = "#2E86AB", enable_qr_codes: bool = True):
        self.company_data = company_data
        self.pdf_color = pdf_color
        self.enable_qr_codes = enable_qr_codes
        self.temp_dir = Path(tempfile.gettempdir()) / "rechnungs_tool_previews"
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_preview(self, invoice: Invoice) -> Optional[Path]:
        """Erstellt eine temporäre PDF für Vorschau"""
        try:
            # Temporären Dateinamen generieren
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"preview_{invoice.document_type.value}_{timestamp}.pdf"
            preview_path = self.temp_dir / preview_filename
            
            # PDF generieren
            pdf_generator = InvoicePDFGenerator(
                self.company_data, 
                self.pdf_color,
                self.enable_qr_codes
            )
            
            if pdf_generator.generate_pdf(invoice, str(preview_path)):
                return preview_path
            else:
                return None
                
        except Exception as e:
            print(f"❌ Fehler bei PDF-Vorschau: {e}")
            return None
    
    def show_preview(self, invoice: Invoice) -> bool:
        """Zeigt PDF-Vorschau im Standard-PDF-Viewer"""
        preview_path = self.create_preview(invoice)
        
        if not preview_path or not preview_path.exists():
            return False
        
        try:
            # Systemspezifisches Öffnen
            if platform.system() == "Windows":
                os.startfile(str(preview_path))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(preview_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(preview_path)])
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Öffnen der Vorschau: {e}")
            # Fallback: Im Browser öffnen
            try:
                webbrowser.open(f"file://{preview_path.absolute()}")
                return True
            except Exception:
                return False
    
    def cleanup_old_previews(self, max_age_minutes: int = 60):
        """Bereinigt alte Vorschau-Dateien"""
        try:
            current_time = datetime.now()
            
            for preview_file in self.temp_dir.glob("preview_*.pdf"):
                file_time = datetime.fromtimestamp(preview_file.stat().st_mtime)
                age_minutes = (current_time - file_time).total_seconds() / 60
                
                if age_minutes > max_age_minutes:
                    try:
                        preview_file.unlink()
                        print(f"🗑️ Alte Vorschau gelöscht: {preview_file.name}")
                    except Exception as e:
                        print(f"⚠️ Konnte Vorschau nicht löschen: {e}")
                        
        except Exception as e:
            print(f"⚠️ Fehler bei Vorschau-Bereinigung: {e}")


class BulkExportManager:
    """Verwaltet Massen-Export von Dokumenten"""
    
    def __init__(self, company_data: CompanyData, pdf_color: str = "#2E86AB", enable_qr_codes: bool = True):
        self.company_data = company_data
        self.pdf_color = pdf_color
        self.enable_qr_codes = enable_qr_codes
    
    def export_multiple_invoices(self, invoices: list, output_dir: Path, 
                                naming_pattern: str = "{document_type}_{invoice_number}") -> Dict[str, Any]:
        """Exportiert mehrere Rechnungen in einen Ordner"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "errors": [],
            "exported_files": []
        }
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_generator = InvoicePDFGenerator(
            self.company_data, 
            self.pdf_color,
            self.enable_qr_codes
        )
        
        for invoice in invoices:
            try:
                # Dateiname generieren
                filename = self._generate_filename(invoice, naming_pattern)
                output_path = output_dir / f"{filename}.pdf"
                
                # PDF generieren
                if pdf_generator.generate_pdf(invoice, str(output_path)):
                    results["success_count"] += 1
                    results["exported_files"].append(str(output_path))
                else:
                    results["error_count"] += 1
                    results["errors"].append(f"PDF-Generierung fehlgeschlagen: {invoice.invoice_number}")
                    
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append(f"Fehler bei {invoice.invoice_number}: {str(e)}")
        
        return results
    
    def export_customer_invoices(self, customer_id: str, invoices: list, 
                                output_dir: Path) -> Dict[str, Any]:
        """Exportiert alle Rechnungen eines Kunden"""
        customer_invoices = [inv for inv in invoices if inv.customer and inv.customer.id == customer_id]
        
        if not customer_invoices:
            return {"success_count": 0, "error_count": 0, "errors": ["Keine Rechnungen für diesen Kunden gefunden"]}
        
        # Kundenordner erstellen
        customer_name = customer_invoices[0].customer.get_display_name()
        safe_customer_name = self._make_filename_safe(customer_name)
        customer_dir = output_dir / safe_customer_name
        
        return self.export_multiple_invoices(customer_invoices, customer_dir)
    
    def export_by_date_range(self, invoices: list, start_date: datetime, 
                           end_date: datetime, output_dir: Path) -> Dict[str, Any]:
        """Exportiert Rechnungen in einem Datumsbereich"""
        filtered_invoices = [
            inv for inv in invoices 
            if start_date <= inv.invoice_date <= end_date
        ]
        
        if not filtered_invoices:
            return {"success_count": 0, "error_count": 0, "errors": ["Keine Rechnungen im gewählten Zeitraum"]}
        
        # Ordner mit Datumsbereich erstellen
        date_range_str = f"{start_date.strftime('%Y%m%d')}_bis_{end_date.strftime('%Y%m%d')}"
        date_dir = output_dir / date_range_str
        
        return self.export_multiple_invoices(filtered_invoices, date_dir)
    
    def _generate_filename(self, invoice: Invoice, pattern: str) -> str:
        """Generiert Dateiname basierend auf Pattern"""
        replacements = {
            "document_type": invoice.document_type.value,
            "invoice_number": invoice.invoice_number,
            "customer_number": invoice.customer.customer_number if invoice.customer else "unknown",
            "customer_name": invoice.customer.get_display_name() if invoice.customer else "unknown",
            "date": invoice.invoice_date.strftime("%Y%m%d"),
            "year": invoice.invoice_date.strftime("%Y"),
            "month": invoice.invoice_date.strftime("%m")
        }
        
        filename = pattern
        for key, value in replacements.items():
            filename = filename.replace(f"{{{key}}}", str(value))
        
        return self._make_filename_safe(filename)
    
    def _make_filename_safe(self, filename: str) -> str:
        """Macht Dateiname dateisystem-sicher"""
        # Ungültige Zeichen ersetzen
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Mehrfache Unterstriche reduzieren
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # Länge begrenzen
        if len(filename) > 100:
            filename = filename[:97] + "..."
        
        return filename.strip('_')


class DocumentAnalyzer:
    """Analysiert Dokumente und erstellt Berichte"""
    
    def analyze_invoices(self, invoices: list) -> Dict[str, Any]:
        """Erstellt umfassende Analyse der Rechnungen"""
        analysis = {
            "summary": {
                "total_count": len(invoices),
                "by_type": {},
                "by_status": {},
                "date_range": None
            },
            "financial": {
                "total_revenue": 0,
                "average_invoice_amount": 0,
                "largest_invoice": None,
                "smallest_invoice": None,
                "unpaid_amount": 0,
                "by_tax_rate": {}
            },
            "customers": {
                "top_customers": [],
                "customer_count": 0
            },
            "trends": {
                "monthly_revenue": {},
                "payment_behavior": {}
            }
        }
        
        if not invoices:
            return analysis
        
        # Grundstatistiken
        from collections import defaultdict
        import decimal
        
        type_counts = defaultdict(int)
        status_counts = defaultdict(int)
        customer_totals = defaultdict(decimal.Decimal)
        monthly_revenue = defaultdict(decimal.Decimal)
        tax_totals = defaultdict(decimal.Decimal)
        
        total_revenue = decimal.Decimal('0')
        unpaid_amount = decimal.Decimal('0')
        amounts = []
        
        dates = [inv.invoice_date for inv in invoices]
        
        for invoice in invoices:
            # Dokumenttyp
            type_counts[invoice.document_type.value] += 1
            
            # Status
            status = "Bezahlt" if invoice.is_paid else "Offen"
            status_counts[status] += 1
            
            # Finanzdaten
            amount = invoice.calculate_total_gross()
            amounts.append(amount)
            
            if invoice.document_type.value == "Rechnung":
                total_revenue += amount
                if not invoice.is_paid:
                    unpaid_amount += amount
                
                # Monatlicher Umsatz
                month_key = invoice.invoice_date.strftime("%Y-%m")
                monthly_revenue[month_key] += amount
                
                # Kundenumsatz
                if invoice.customer:
                    customer_totals[invoice.customer.get_display_name()] += amount
            
            # Steueraufteilung
            for tax_rate, tax_amount in invoice.calculate_tax_totals_by_rate().items():
                tax_totals[f"{tax_rate.value*100:.0f}%"] += tax_amount
        
        # Ergebnisse zusammenstellen
        analysis["summary"]["by_type"] = dict(type_counts)
        analysis["summary"]["by_status"] = dict(status_counts)
        analysis["summary"]["date_range"] = {
            "from": min(dates).strftime("%d.%m.%Y") if dates else None,
            "to": max(dates).strftime("%d.%m.%Y") if dates else None
        }
        
        analysis["financial"]["total_revenue"] = float(total_revenue)
        analysis["financial"]["unpaid_amount"] = float(unpaid_amount)
        analysis["financial"]["by_tax_rate"] = {k: float(v) for k, v in tax_totals.items()}
        
        if amounts:
            analysis["financial"]["average_invoice_amount"] = float(sum(amounts) / len(amounts))
            analysis["financial"]["largest_invoice"] = float(max(amounts))
            analysis["financial"]["smallest_invoice"] = float(min(amounts))
        
        # Top-Kunden
        top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        analysis["customers"]["top_customers"] = [(name, float(amount)) for name, amount in top_customers]
        analysis["customers"]["customer_count"] = len(customer_totals)
        
        # Trends
        analysis["trends"]["monthly_revenue"] = {k: float(v) for k, v in monthly_revenue.items()}
        
        return analysis
