"""
E-Mail Manager für automatischen Versand von Rechnungen und Dokumenten
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
import os
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import json
from pathlib import Path

from src.utils.data_manager import DataManager


class EmailConfig:
    """E-Mail Konfiguration"""
    
    def __init__(self):
        self.smtp_server = ""
        self.smtp_port = 587
        self.use_tls = True
        self.username = ""
        self.password = ""
        self.sender_name = ""
        self.sender_email = ""
        self.signature = ""
        self.auto_send_invoices = False
        self.send_reminders = False
        self.reminder_days = [7, 14, 30]
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary"""
        return {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'use_tls': self.use_tls,
            'username': self.username,
            'password': self.password,  # In Produktion: verschlüsselt speichern!
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'signature': self.signature,
            'auto_send_invoices': self.auto_send_invoices,
            'send_reminders': self.send_reminders,
            'reminder_days': self.reminder_days
        }
    
    def from_dict(self, data: Dict):
        """Lädt aus Dictionary"""
        self.smtp_server = data.get('smtp_server', '')
        self.smtp_port = data.get('smtp_port', 587)
        self.use_tls = data.get('use_tls', True)
        self.username = data.get('username', '')
        self.password = data.get('password', '')
        self.sender_name = data.get('sender_name', '')
        self.sender_email = data.get('sender_email', '')
        self.signature = data.get('signature', '')
        self.auto_send_invoices = data.get('auto_send_invoices', False)
        self.send_reminders = data.get('send_reminders', False)
        self.reminder_days = data.get('reminder_days', [7, 14, 30])


class EmailTemplate:
    """E-Mail Vorlage"""
    
    def __init__(self, name: str, subject: str, body: str, template_type: str = "invoice"):
        self.name = name
        self.subject = subject
        self.body = body
        self.template_type = template_type  # invoice, reminder, quote, etc.
        self.created_at = datetime.now()
        self.variables = self.extract_variables()
    
    def extract_variables(self) -> List[str]:
        """Extrahiert Variablen aus dem Template"""
        import re
        variables = re.findall(r'\{(\w+)\}', self.subject + self.body)
        return list(set(variables))
    
    def render(self, **kwargs) -> Tuple[str, str]:
        """Rendert Template mit gegebenen Variablen"""
        try:
            subject = self.subject.format(**kwargs)
            body = self.body.format(**kwargs)
            return subject, body
        except KeyError as e:
            raise ValueError(f"Fehlende Variable für Template: {e}")


class EmailManager:
    """Manager für E-Mail Funktionalität"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.config = EmailConfig()
        self.templates: Dict[str, EmailTemplate] = {}
        self.email_history: List[Dict] = []
        
        # Konfiguration und Vorlagen laden
        self.load_config()
        self.load_templates()
        self.load_history()
        
        # Standard-Templates erstellen wenn nicht vorhanden
        self.create_default_templates()
    
    def load_config(self):
        """Lädt E-Mail Konfiguration"""
        try:
            config_file = Path("data/email_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config.from_dict(data)
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der E-Mail Konfiguration: {e}")
    
    def save_config(self):
        """Speichert E-Mail Konfiguration"""
        try:
            config_file = Path("data/email_config.json")
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Fehler beim Speichern der E-Mail Konfiguration: {e}")
    
    def load_templates(self):
        """Lädt E-Mail Vorlagen"""
        try:
            templates_file = Path("data/email_templates.json")
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, template_data in data.items():
                        template = EmailTemplate(
                            name=template_data['name'],
                            subject=template_data['subject'],
                            body=template_data['body'],
                            template_type=template_data.get('template_type', 'invoice')
                        )
                        self.templates[name] = template
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der E-Mail Vorlagen: {e}")
    
    def save_templates(self):
        """Speichert E-Mail Vorlagen"""
        try:
            templates_file = Path("data/email_templates.json")
            templates_file.parent.mkdir(exist_ok=True)
            
            data = {}
            for name, template in self.templates.items():
                data[name] = {
                    'name': template.name,
                    'subject': template.subject,
                    'body': template.body,
                    'template_type': template.template_type
                }
            
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Fehler beim Speichern der E-Mail Vorlagen: {e}")
    
    def load_history(self):
        """Lädt E-Mail Historie"""
        try:
            history_file = Path("data/email_history.json")
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.email_history = json.load(f)
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der E-Mail Historie: {e}")
    
    def save_history(self):
        """Speichert E-Mail Historie"""
        try:
            history_file = Path("data/email_history.json")
            history_file.parent.mkdir(exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.email_history, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"❌ Fehler beim Speichern der E-Mail Historie: {e}")
    
    def create_default_templates(self):
        """Erstellt Standard-E-Mail Vorlagen"""
        if "rechnung_standard" not in self.templates:
            self.templates["rechnung_standard"] = EmailTemplate(
                name="Rechnung Standard",
                subject="Rechnung {invoice_number} - {company_name}",
                body="""Sehr geehrte Damen und Herren,

anbei erhalten Sie die Rechnung {invoice_number} vom {invoice_date}.

Rechnungsbetrag: {total_amount} €
Zahlungsziel: {due_date}

Bitte überweisen Sie den Betrag unter Angabe der Rechnungsnummer auf unser Konto.

Bei Fragen stehen wir Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen
{sender_name}

{signature}""",
                template_type="invoice"
            )
        
        if "mahnung_1" not in self.templates:
            self.templates["mahnung_1"] = EmailTemplate(
                name="1. Mahnung",
                subject="1. Mahnung - Rechnung {invoice_number}",
                body="""Sehr geehrte Damen und Herren,

unsere Rechnung {invoice_number} vom {invoice_date} über {total_amount} € ist noch nicht bei uns eingegangen.

Sollte sich Ihre Zahlung mit diesem Schreiben überschnitten haben, betrachten Sie diese Mahnung als gegenstandslos.

Andernfalls bitten wir Sie, den offenen Betrag binnen 7 Tagen zu begleichen.

Mit freundlichen Grüßen
{sender_name}

{signature}""",
                template_type="reminder"
            )
        
        if "angebot_standard" not in self.templates:
            self.templates["angebot_standard"] = EmailTemplate(
                name="Angebot Standard",
                subject="Angebot {quote_number} - {company_name}",
                body="""Sehr geehrte Damen und Herren,

vielen Dank für Ihre Anfrage. Anbei erhalten Sie unser Angebot {quote_number}.

Das Angebot ist gültig bis: {valid_until}
Gesamtbetrag: {total_amount} €

Bei Fragen oder Rücksprache stehen wir Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen
{sender_name}

{signature}""",
                template_type="quote"
            )
        
        # Vorlagen speichern
        self.save_templates()
    
    def test_connection(self) -> Tuple[bool, str]:
        """Testet die E-Mail Verbindung"""
        try:
            if not self.config.smtp_server or not self.config.username:
                return False, "SMTP-Server oder Benutzername nicht konfiguriert"
            
            # SMTP-Verbindung testen
            if self.config.use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
            
            server.login(self.config.username, self.config.password)
            server.quit()
            
            return True, "Verbindung erfolgreich"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentifizierung fehlgeschlagen - Benutzername/Passwort prüfen"
        except smtplib.SMTPServerDisconnected:
            return False, "Server-Verbindung unterbrochen"
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}"
    
    def send_invoice_email(self, invoice, pdf_path: Optional[str] = None, template_name: str = "rechnung_standard", 
                          custom_recipient: Optional[str] = None) -> Tuple[bool, str]:
        """Sendet Rechnung per E-Mail"""
        try:
            # Empfänger bestimmen
            if custom_recipient:
                recipient_email = custom_recipient
                recipient_name = custom_recipient
            elif invoice.customer and hasattr(invoice.customer, 'email') and invoice.customer.email:
                recipient_email = invoice.customer.email
                recipient_name = invoice.customer.get_display_name()
            else:
                return False, "Keine E-Mail-Adresse für Kunden verfügbar"
            
            # Template laden
            if template_name not in self.templates:
                return False, f"Template '{template_name}' nicht gefunden"
            
            template = self.templates[template_name]
            
            # Company-Daten laden
            company_data = self.data_manager.get_company_data()
            
            # Template-Variablen vorbereiten
            template_vars = {
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date.strftime('%d.%m.%Y') if invoice.invoice_date else '',
                'due_date': (invoice.invoice_date + timedelta(days=14)).strftime('%d.%m.%Y') if invoice.invoice_date else '',
                'total_amount': f"{invoice.calculate_total_gross():.2f}",
                'customer_name': recipient_name,
                'company_name': company_data.name if company_data else '',
                'sender_name': self.config.sender_name or (company_data.name if company_data else ''),
                'signature': self.config.signature
            }
            
            # E-Mail rendern
            subject, body = template.render(**template_vars)
            
            # E-Mail senden
            success, message = self._send_email(
                to_email=recipient_email,
                to_name=recipient_name,
                subject=subject,
                body=body,
                attachments=[pdf_path] if pdf_path else []
            )
            
            # Historie speichern
            if success:
                self._add_to_history({
                    'type': 'invoice',
                    'invoice_number': invoice.invoice_number,
                    'recipient': recipient_email,
                    'subject': subject,
                    'sent_at': datetime.now(),
                    'template_used': template_name,
                    'success': True
                })
            
            return success, message
            
        except Exception as e:
            return False, f"Fehler beim Senden der Rechnung: {str(e)}"
    
    def send_reminder_email(self, invoice, reminder_level: int = 1) -> Tuple[bool, str]:
        """Sendet Mahnung per E-Mail"""
        template_name = f"mahnung_{reminder_level}"
        if template_name not in self.templates:
            template_name = "mahnung_1"  # Fallback
        
        return self.send_invoice_email(invoice, template_name=template_name)
    
    def send_quote_email(self, quote, pdf_path: Optional[str] = None) -> Tuple[bool, str]:
        """Sendet Angebot per E-Mail"""
        # Ähnlich wie send_invoice_email, aber für Angebote
        return self.send_invoice_email(quote, pdf_path, template_name="angebot_standard")
    
    def _send_email(self, to_email: str, to_name: str, subject: str, body: str, 
                   attachments: Optional[List[str]] = None) -> Tuple[bool, str]:
        """Sendet tatsächlich die E-Mail"""
        try:
            # E-Mail-Message erstellen
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg['To'] = f"{to_name} <{to_email}>"
            msg['Subject'] = subject
            
            # Text-Teil hinzufügen
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Anhänge hinzufügen
            if attachments:
                for file_path in attachments:
                    if file_path and os.path.exists(file_path):
                        self._attach_file(msg, file_path)
            
            # SMTP-Verbindung und Versand
            if self.config.use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
            
            server.login(self.config.username, self.config.password)
            
            # E-Mail senden
            text = msg.as_string()
            server.sendmail(self.config.sender_email, to_email, text)
            server.quit()
            
            return True, "E-Mail erfolgreich gesendet"
            
        except Exception as e:
            return False, f"Fehler beim E-Mail-Versand: {str(e)}"
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Fügt Datei als Anhang hinzu"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            print(f"❌ Fehler beim Anhängen der Datei {file_path}: {e}")
    
    def _add_to_history(self, entry: Dict):
        """Fügt Eintrag zur E-Mail Historie hinzu"""
        self.email_history.append(entry)
        
        # Historie auf 1000 Einträge begrenzen
        if len(self.email_history) > 1000:
            self.email_history = self.email_history[-1000:]
        
        self.save_history()
    
    def get_pending_reminders(self) -> List[Dict]:
        """Ermittelt fällige Mahnungen"""
        try:
            pending_reminders = []
            invoices = self.data_manager.get_invoices()
            
            for invoice in invoices:
                if hasattr(invoice, 'payment_status') and invoice.payment_status == "Offen" and invoice.invoice_date:
                    days_overdue = (datetime.now().date() - invoice.invoice_date).days
                    
                    # Prüfen ob Mahnung fällig
                    for reminder_day in self.config.reminder_days:
                        if days_overdue >= reminder_day:
                            # Prüfen ob bereits gemahnt
                            last_reminder = self._get_last_reminder(invoice.invoice_number)
                            if not last_reminder or last_reminder['level'] < self._get_reminder_level(reminder_day):
                                pending_reminders.append({
                                    'invoice': invoice,
                                    'days_overdue': days_overdue,
                                    'reminder_level': self._get_reminder_level(reminder_day)
                                })
                                break
            
            return pending_reminders
            
        except Exception as e:
            print(f"❌ Fehler beim Ermitteln fälliger Mahnungen: {e}")
            return []
    
    def _get_last_reminder(self, invoice_number: str) -> Optional[Dict]:
        """Ermittelt letzte Mahnung für Rechnung"""
        reminders = [entry for entry in self.email_history 
                    if entry.get('type') == 'reminder' 
                    and entry.get('invoice_number') == invoice_number]
        
        if reminders:
            return max(reminders, key=lambda x: x.get('sent_at', ''))
        return None
    
    def _get_reminder_level(self, days: int) -> int:
        """Ermittelt Mahnstufe basierend auf Tagen"""
        if days >= 30:
            return 3
        elif days >= 14:
            return 2
        else:
            return 1
    
    def send_automatic_reminders(self) -> Tuple[int, List[str]]:
        """Sendet automatische Mahnungen"""
        if not self.config.send_reminders:
            return 0, ["Automatische Mahnungen sind deaktiviert"]
        
        pending = self.get_pending_reminders()
        sent_count = 0
        errors = []
        
        for reminder_info in pending:
            try:
                success, message = self.send_reminder_email(
                    reminder_info['invoice'], 
                    reminder_info['reminder_level']
                )
                
                if success:
                    sent_count += 1
                    # Historie aktualisieren
                    self._add_to_history({
                        'type': 'reminder',
                        'invoice_number': reminder_info['invoice'].invoice_number,
                        'recipient': reminder_info['invoice'].customer.email if reminder_info['invoice'].customer else '',
                        'level': reminder_info['reminder_level'],
                        'sent_at': datetime.now(),
                        'automatic': True,
                        'success': True
                    })
                else:
                    errors.append(f"Rechnung {reminder_info['invoice'].invoice_number}: {message}")
                    
            except Exception as e:
                errors.append(f"Rechnung {reminder_info['invoice'].invoice_number}: {str(e)}")
        
        return sent_count, errors
    
    def get_email_statistics(self) -> Dict:
        """Erstellt E-Mail Statistiken"""
        try:
            total_emails = len(self.email_history)
            successful_emails = len([e for e in self.email_history if e.get('success', False)])
            
            # Nach Typ gruppieren
            by_type = {}
            for entry in self.email_history:
                email_type = entry.get('type', 'unknown')
                by_type[email_type] = by_type.get(email_type, 0) + 1
            
            # Letzte 30 Tage
            from datetime import timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_emails = [e for e in self.email_history 
                           if isinstance(e.get('sent_at'), datetime) and e['sent_at'] > thirty_days_ago]
            
            return {
                'total_emails': total_emails,
                'successful_emails': successful_emails,
                'success_rate': (successful_emails / total_emails * 100) if total_emails > 0 else 0,
                'by_type': by_type,
                'last_30_days': len(recent_emails),
                'pending_reminders': len(self.get_pending_reminders())
            }
            
        except Exception as e:
            print(f"❌ Fehler bei E-Mail Statistiken: {e}")
            return {}
