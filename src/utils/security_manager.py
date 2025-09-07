"""
Erweiterte Sicherheits- und Compliance-Features
"""
import hashlib
import hmac
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
from pathlib import Path
from enum import Enum
import sqlite3
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class UserRole(Enum):
    """Benutzerrollen"""
    ADMIN = "Administrator"
    MANAGER = "Manager"
    USER = "Benutzer"
    READONLY = "Nur Lesen"
    AUDITOR = "Prüfer"


class Permission(Enum):
    """Berechtigungen"""
    # Kunden
    CUSTOMERS_READ = "customers.read"
    CUSTOMERS_WRITE = "customers.write"
    CUSTOMERS_DELETE = "customers.delete"
    
    # Rechnungen
    INVOICES_READ = "invoices.read"
    INVOICES_WRITE = "invoices.write"
    INVOICES_DELETE = "invoices.delete"
    INVOICES_SEND = "invoices.send"
    
    # Artikel
    ARTICLES_READ = "articles.read"
    ARTICLES_WRITE = "articles.write"
    ARTICLES_DELETE = "articles.delete"
    
    # System
    SYSTEM_SETTINGS = "system.settings"
    SYSTEM_BACKUP = "system.backup"
    SYSTEM_USERS = "system.users"
    SYSTEM_AUDIT = "system.audit"
    
    # Berichte
    REPORTS_VIEW = "reports.view"
    REPORTS_EXPORT = "reports.export"
    
    # Finanzen
    FINANCE_VIEW = "finance.view"
    FINANCE_EDIT = "finance.edit"


class SecurityLevel(Enum):
    """Sicherheitsstufen"""
    LOW = "Niedrig"
    MEDIUM = "Mittel"
    HIGH = "Hoch"
    CRITICAL = "Kritisch"


class AuditEventType(Enum):
    """Audit-Event-Typen"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    USER_CREATED = "user_created"
    USER_MODIFIED = "user_modified"
    USER_DELETED = "user_deleted"
    PASSWORD_CHANGED = "password_changed"
    PERMISSION_CHANGED = "permission_changed"
    
    DATA_READ = "data_read"
    DATA_CREATED = "data_created"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    SETTINGS_CHANGED = "settings_changed"
    SECURITY_VIOLATION = "security_violation"
    
    EMAIL_SENT = "email_sent"
    REPORT_GENERATED = "report_generated"


class User:
    """Benutzer"""
    
    def __init__(self, user_id: Optional[str] = None, username: str = "",
                 email: str = "", role: UserRole = UserRole.USER):
        self.user_id = user_id or secrets.token_hex(16)
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = ""
        self.salt = ""
        
        # Status
        self.is_active = True
        self.is_locked = False
        self.must_change_password = False
        self.failed_login_attempts = 0
        self.last_login: Optional[datetime] = None
        self.last_password_change: Optional[datetime] = None
        self.account_expires: Optional[datetime] = None
        
        # Sicherheit
        self.two_factor_enabled = False
        self.two_factor_secret = ""
        self.backup_codes: List[str] = []
        self.session_timeout_minutes = 30
        
        # Zusätzliche Berechtigungen
        self.additional_permissions: List[Permission] = []
        self.denied_permissions: List[Permission] = []
        
        # Metadaten
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.created_by = ""
        self.notes = ""
        
        # DSGVO
        self.data_processing_consent = False
        self.data_processing_consent_date: Optional[datetime] = None
    
    def set_password(self, password: str):
        """Setzt neues Passwort"""
        self.salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), self.salt).decode('utf-8')
        self.last_password_change = datetime.now()
        self.must_change_password = False
    
    def verify_password(self, password: str) -> bool:
        """Verifiziert Passwort"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def has_permission(self, permission: Permission) -> bool:
        """Prüft Berechtigung"""
        # Explizit verweigerte Berechtigung
        if permission in self.denied_permissions:
            return False
        
        # Explizit gewährte Berechtigung
        if permission in self.additional_permissions:
            return True
        
        # Rollenbasierte Berechtigung
        return self._role_has_permission(permission)
    
    def _role_has_permission(self, permission: Permission) -> bool:
        """Rollenbasierte Berechtigung prüfen"""
        role_permissions = {
            UserRole.ADMIN: list(Permission),  # Admin hat alle Rechte
            UserRole.MANAGER: [
                Permission.CUSTOMERS_READ, Permission.CUSTOMERS_WRITE,
                Permission.INVOICES_READ, Permission.INVOICES_WRITE, Permission.INVOICES_SEND,
                Permission.ARTICLES_READ, Permission.ARTICLES_WRITE,
                Permission.REPORTS_VIEW, Permission.REPORTS_EXPORT,
                Permission.FINANCE_VIEW, Permission.FINANCE_EDIT,
                Permission.SYSTEM_BACKUP
            ],
            UserRole.USER: [
                Permission.CUSTOMERS_READ, Permission.CUSTOMERS_WRITE,
                Permission.INVOICES_READ, Permission.INVOICES_WRITE,
                Permission.ARTICLES_READ, Permission.ARTICLES_WRITE,
                Permission.REPORTS_VIEW,
                Permission.FINANCE_VIEW
            ],
            UserRole.READONLY: [
                Permission.CUSTOMERS_READ,
                Permission.INVOICES_READ,
                Permission.ARTICLES_READ,
                Permission.REPORTS_VIEW,
                Permission.FINANCE_VIEW
            ],
            UserRole.AUDITOR: [
                Permission.CUSTOMERS_READ,
                Permission.INVOICES_READ,
                Permission.ARTICLES_READ,
                Permission.REPORTS_VIEW, Permission.REPORTS_EXPORT,
                Permission.FINANCE_VIEW,
                Permission.SYSTEM_AUDIT
            ]
        }
        
        return permission in role_permissions.get(self.role, [])
    
    def is_password_expired(self, max_age_days: int = 90) -> bool:
        """Prüft ob Passwort abgelaufen ist"""
        if not self.last_password_change:
            return True
        
        expiry_date = self.last_password_change + timedelta(days=max_age_days)
        return datetime.now() > expiry_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary (ohne sensible Daten)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'must_change_password': self.must_change_password,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_password_change': self.last_password_change.isoformat() if self.last_password_change else None,
            'account_expires': self.account_expires.isoformat() if self.account_expires else None,
            'two_factor_enabled': self.two_factor_enabled,
            'session_timeout_minutes': self.session_timeout_minutes,
            'additional_permissions': [p.value for p in self.additional_permissions],
            'denied_permissions': [p.value for p in self.denied_permissions],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'notes': self.notes,
            'data_processing_consent': self.data_processing_consent,
            'data_processing_consent_date': self.data_processing_consent_date.isoformat() if self.data_processing_consent_date else None
        }


class Session:
    """Benutzersitzung"""
    
    def __init__(self, user: User, session_id: Optional[str] = None):
        self.session_id = session_id or secrets.token_hex(32)
        self.user = user
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=user.session_timeout_minutes)
        self.ip_address = ""
        self.user_agent = ""
        self.is_active = True
    
    def is_expired(self) -> bool:
        """Prüft ob Session abgelaufen ist"""
        return datetime.now() > self.expires_at
    
    def refresh(self):
        """Erneuert Session"""
        self.last_activity = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=self.user.session_timeout_minutes)
    
    def invalidate(self):
        """Invalidiert Session"""
        self.is_active = False


class AuditEvent:
    """Audit-Event"""
    
    def __init__(self, event_type: AuditEventType, user_id: str = "",
                 description: str = "", details: Optional[Dict[str, Any]] = None):
        self.event_id = secrets.token_hex(16)
        self.event_type = event_type
        self.user_id = user_id
        self.timestamp = datetime.now()
        self.description = description
        self.details = details or {}
        self.ip_address = ""
        self.user_agent = ""
        self.session_id = ""
        self.severity = SecurityLevel.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'severity': self.severity.value
        }


class SecurityManager:
    """Sicherheits-Manager"""
    
    def __init__(self, data_directory: str = "data"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # In-Memory Stores
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.audit_events: List[AuditEvent] = []
        
        # Sicherheitseinstellungen
        self.settings = {
            'password_min_length': 8,
            'password_require_uppercase': True,
            'password_require_lowercase': True,
            'password_require_numbers': True,
            'password_require_special': True,
            'password_max_age_days': 90,
            'max_failed_login_attempts': 5,
            'account_lockout_duration_minutes': 30,
            'session_timeout_minutes': 30,
            'require_two_factor': False,
            'audit_retention_days': 365,
            'data_encryption_enabled': True,
            'backup_encryption_enabled': True
        }
        
        # Verschlüsselung
        self.encryption_key: Optional[bytes] = None
        self._init_encryption()
        
        # Datenbank für Audit-Log
        self._init_audit_db()
        
        # Lock für Thread-Sicherheit
        self._lock = threading.Lock()
        
        # Standardbenutzer erstellen falls keine vorhanden
        self.load_users()
        if not self.users:
            self._create_default_admin()
    
    def _init_encryption(self):
        """Initialisiert Verschlüsselung"""
        try:
            key_file = self.data_directory / "encryption.key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Neuen Schlüssel generieren
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                
                # Datei-Berechtigungen setzen (nur Owner lesen/schreiben)
                os.chmod(key_file, 0o600)
                
        except Exception as e:
            self.logger.error(f"Fehler bei Verschlüsselungs-Initialisierung: {e}")
            self.encryption_key = Fernet.generate_key()
    
    def _init_audit_db(self):
        """Initialisiert Audit-Datenbank"""
        try:
            db_file = self.data_directory / "audit.db"
            
            with sqlite3.connect(db_file) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_events (
                        event_id TEXT PRIMARY KEY,
                        event_type TEXT NOT NULL,
                        user_id TEXT,
                        timestamp TEXT NOT NULL,
                        description TEXT,
                        details TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        session_id TEXT,
                        severity TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                    ON audit_events(timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_user 
                    ON audit_events(user_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_audit_event_type 
                    ON audit_events(event_type)
                """)
                
        except Exception as e:
            self.logger.error(f"Fehler bei Audit-DB Initialisierung: {e}")
    
    def _create_default_admin(self):
        """Erstellt Standard-Administrator"""
        try:
            admin = User(
                username="admin",
                email="admin@example.com",
                role=UserRole.ADMIN
            )
            admin.set_password("admin123!")  # Muss beim ersten Login geändert werden
            admin.must_change_password = True
            
            self.users[admin.user_id] = admin
            self.save_users()
            
            # Audit-Event
            event = AuditEvent(
                event_type=AuditEventType.USER_CREATED,
                description="Standard-Administrator erstellt"
            )
            self.log_audit_event(event)
            
            self.logger.info("Standard-Administrator erstellt")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Standard-Administrators: {e}")
    
    def encrypt_data(self, data: str) -> str:
        """Verschlüsselt Daten"""
        if not self.settings['data_encryption_enabled'] or not self.encryption_key:
            return data
        
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Verschlüsselungsfehler: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Entschlüsselt Daten"""
        if not self.settings['data_encryption_enabled'] or not self.encryption_key:
            return encrypted_data
        
        try:
            fernet = Fernet(self.encryption_key)
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Entschlüsselungsfehler: {e}")
            return encrypted_data
    
    def create_user(self, username: str, email: str, password: str,
                   role: UserRole = UserRole.USER, creator_user_id: str = "") -> Tuple[bool, str, Optional[User]]:
        """Erstellt neuen Benutzer"""
        try:
            # Validierungen
            if not username or not email or not password:
                return False, "Benutzername, E-Mail und Passwort sind erforderlich", None
            
            # Prüfen ob Benutzername bereits existiert
            for user in self.users.values():
                if user.username.lower() == username.lower():
                    return False, "Benutzername bereits vergeben", None
                if user.email.lower() == email.lower():
                    return False, "E-Mail-Adresse bereits vergeben", None
            
            # Passwort validieren
            is_valid, password_message = self.validate_password(password)
            if not is_valid:
                return False, password_message, None
            
            # Benutzer erstellen
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            user.created_by = creator_user_id
            
            self.users[user.user_id] = user
            self.save_users()
            
            # Audit-Event
            event = AuditEvent(
                event_type=AuditEventType.USER_CREATED,
                user_id=creator_user_id,
                description=f"Benutzer '{username}' erstellt",
                details={'new_user_id': user.user_id, 'role': role.value}
            )
            self.log_audit_event(event)
            
            return True, "Benutzer erfolgreich erstellt", user
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Benutzers: {e}")
            return False, f"Fehler beim Erstellen: {str(e)}", None
    
    def authenticate_user(self, username: str, password: str,
                         ip_address: str = "", user_agent: str = "") -> Tuple[bool, str, Optional[Session]]:
        """Authentifiziert Benutzer"""
        try:
            # Benutzer finden
            user = None
            for u in self.users.values():
                if u.username.lower() == username.lower():
                    user = u
                    break
            
            if not user:
                # Audit-Event für fehlgeschlagenen Login
                event = AuditEvent(
                    event_type=AuditEventType.LOGIN_FAILED,
                    description=f"Login fehlgeschlagen: Unbekannter Benutzer '{username}'",
                    details={'username': username, 'reason': 'user_not_found'}
                )
                event.ip_address = ip_address
                event.user_agent = user_agent
                self.log_audit_event(event)
                
                return False, "Benutzername oder Passwort ungültig", None
            
            # Konto-Status prüfen
            if not user.is_active:
                event = AuditEvent(
                    event_type=AuditEventType.LOGIN_FAILED,
                    user_id=user.user_id,
                    description=f"Login fehlgeschlagen: Konto inaktiv",
                    details={'username': username, 'reason': 'account_inactive'}
                )
                event.ip_address = ip_address
                event.user_agent = user_agent
                self.log_audit_event(event)
                
                return False, "Konto ist deaktiviert", None
            
            if user.is_locked:
                event = AuditEvent(
                    event_type=AuditEventType.LOGIN_FAILED,
                    user_id=user.user_id,
                    description=f"Login fehlgeschlagen: Konto gesperrt",
                    details={'username': username, 'reason': 'account_locked'}
                )
                event.ip_address = ip_address
                event.user_agent = user_agent
                self.log_audit_event(event)
                
                return False, "Konto ist gesperrt", None
            
            # Passwort prüfen
            if not user.verify_password(password):
                user.failed_login_attempts += 1
                
                # Konto sperren bei zu vielen fehlgeschlagenen Versuchen
                if user.failed_login_attempts >= self.settings['max_failed_login_attempts']:
                    user.is_locked = True
                    self.save_users()
                    
                    event = AuditEvent(
                        event_type=AuditEventType.SECURITY_VIOLATION,
                        user_id=user.user_id,
                        description=f"Konto gesperrt nach {user.failed_login_attempts} fehlgeschlagenen Anmeldeversuchen",
                        details={'username': username, 'failed_attempts': user.failed_login_attempts}
                    )
                    event.severity = SecurityLevel.HIGH
                    event.ip_address = ip_address
                    event.user_agent = user_agent
                    self.log_audit_event(event)
                    
                    return False, "Konto wurde nach zu vielen fehlgeschlagenen Anmeldeversuchen gesperrt", None
                
                self.save_users()
                
                event = AuditEvent(
                    event_type=AuditEventType.LOGIN_FAILED,
                    user_id=user.user_id,
                    description=f"Login fehlgeschlagen: Falsches Passwort (Versuch {user.failed_login_attempts})",
                    details={'username': username, 'failed_attempts': user.failed_login_attempts}
                )
                event.ip_address = ip_address
                event.user_agent = user_agent
                self.log_audit_event(event)
                
                return False, "Benutzername oder Passwort ungültig", None
            
            # Erfolgreiches Login
            user.failed_login_attempts = 0
            user.last_login = datetime.now()
            self.save_users()
            
            # Session erstellen
            session = Session(user)
            session.ip_address = ip_address
            session.user_agent = user_agent
            
            with self._lock:
                self.sessions[session.session_id] = session
            
            # Audit-Event
            event = AuditEvent(
                event_type=AuditEventType.LOGIN,
                user_id=user.user_id,
                description=f"Erfolgreiche Anmeldung",
                details={'username': username, 'session_id': session.session_id}
            )
            event.ip_address = ip_address
            event.user_agent = user_agent
            event.session_id = session.session_id
            self.log_audit_event(event)
            
            return True, "Anmeldung erfolgreich", session
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Authentifizierung: {e}")
            return False, f"Authentifizierungsfehler: {str(e)}", None
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[Session]]:
        """Validiert Session"""
        try:
            with self._lock:
                session = self.sessions.get(session_id)
            
            if not session:
                return False, None
            
            if not session.is_active or session.is_expired():
                with self._lock:
                    if session_id in self.sessions:
                        del self.sessions[session_id]
                return False, None
            
            # Session erneuern
            session.refresh()
            
            return True, session
            
        except Exception as e:
            self.logger.error(f"Fehler bei Session-Validierung: {e}")
            return False, None
    
    def logout_user(self, session_id: str) -> bool:
        """Meldet Benutzer ab"""
        try:
            with self._lock:
                session = self.sessions.get(session_id)
                if session:
                    session.invalidate()
                    del self.sessions[session_id]
                    
                    # Audit-Event
                    event = AuditEvent(
                        event_type=AuditEventType.LOGOUT,
                        user_id=session.user.user_id,
                        description="Benutzer abgemeldet",
                        details={'session_id': session_id}
                    )
                    event.session_id = session_id
                    self.log_audit_event(event)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abmelden: {e}")
            return False
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validiert Passwort-Richtlinien"""
        if len(password) < self.settings['password_min_length']:
            return False, f"Passwort muss mindestens {self.settings['password_min_length']} Zeichen lang sein"
        
        if self.settings['password_require_uppercase'] and not any(c.isupper() for c in password):
            return False, "Passwort muss mindestens einen Großbuchstaben enthalten"
        
        if self.settings['password_require_lowercase'] and not any(c.islower() for c in password):
            return False, "Passwort muss mindestens einen Kleinbuchstaben enthalten"
        
        if self.settings['password_require_numbers'] and not any(c.isdigit() for c in password):
            return False, "Passwort muss mindestens eine Zahl enthalten"
        
        if self.settings['password_require_special']:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Passwort muss mindestens ein Sonderzeichen enthalten"
        
        return True, "Passwort ist gültig"
    
    def log_audit_event(self, event: AuditEvent):
        """Loggt Audit-Event"""
        try:
            # In-Memory hinzufügen
            self.audit_events.append(event)
            
            # In Datenbank speichern
            db_file = self.data_directory / "audit.db"
            with sqlite3.connect(db_file) as conn:
                conn.execute("""
                    INSERT INTO audit_events 
                    (event_id, event_type, user_id, timestamp, description, details, 
                     ip_address, user_agent, session_id, severity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.event_type.value,
                    event.user_id,
                    event.timestamp.isoformat(),
                    event.description,
                    json.dumps(event.details),
                    event.ip_address,
                    event.user_agent,
                    event.session_id,
                    event.severity.value
                ))
            
            # Alte Events bereinigen (nur In-Memory, DB bleibt für Compliance)
            if len(self.audit_events) > 1000:
                self.audit_events = self.audit_events[-1000:]
                
        except Exception as e:
            self.logger.error(f"Fehler beim Loggen des Audit-Events: {e}")
    
    def get_audit_events(self, user_id: Optional[str] = None, event_type: Optional[AuditEventType] = None,
                        date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
                        limit: int = 100) -> List[AuditEvent]:
        """Holt Audit-Events aus der Datenbank"""
        try:
            db_file = self.data_directory / "audit.db"
            
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)
            
            if date_from:
                query += " AND timestamp >= ?"
                params.append(date_from.isoformat())
            
            if date_to:
                query += " AND timestamp <= ?"
                params.append(date_to.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            events = []
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                
                for row in cursor.fetchall():
                    event = AuditEvent(
                        event_type=AuditEventType(row['event_type']),
                        user_id=row['user_id'] or "",
                        description=row['description'] or ""
                    )
                    event.event_id = row['event_id']
                    event.timestamp = datetime.fromisoformat(row['timestamp'])
                    event.details = json.loads(row['details'] or '{}')
                    event.ip_address = row['ip_address'] or ""
                    event.user_agent = row['user_agent'] or ""
                    event.session_id = row['session_id'] or ""
                    event.severity = SecurityLevel(row['severity'])
                    
                    events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Audit-Events: {e}")
            return []
    
    def save_users(self):
        """Speichert Benutzer"""
        try:
            users_data = {}
            for user_id, user in self.users.items():
                user_dict = user.to_dict()
                # Sensible Daten hinzufügen
                user_dict['password_hash'] = user.password_hash
                user_dict['salt'] = user.salt.decode('utf-8') if isinstance(user.salt, bytes) else user.salt
                user_dict['two_factor_secret'] = user.two_factor_secret
                user_dict['backup_codes'] = user.backup_codes
                user_dict['failed_login_attempts'] = user.failed_login_attempts
                
                users_data[user_id] = user_dict
            
            # Verschlüsselt speichern
            json_data = json.dumps(users_data, indent=2, default=str)
            encrypted_data = self.encrypt_data(json_data)
            
            users_file = self.data_directory / "users.dat"
            with open(users_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            # Datei-Berechtigungen setzen
            os.chmod(users_file, 0o600)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Benutzer: {e}")
    
    def load_users(self):
        """Lädt Benutzer"""
        try:
            users_file = self.data_directory / "users.dat"
            if not users_file.exists():
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            # Entschlüsseln
            json_data = self.decrypt_data(encrypted_data)
            users_data = json.loads(json_data)
            
            for user_id, user_dict in users_data.items():
                user = User(
                    user_id=user_dict['user_id'],
                    username=user_dict['username'],
                    email=user_dict['email'],
                    role=UserRole(user_dict['role'])
                )
                
                # Zusätzliche Daten laden
                user.password_hash = user_dict.get('password_hash', '')
                salt_data = user_dict.get('salt', '')
                user.salt = salt_data.encode('utf-8') if isinstance(salt_data, str) else salt_data
                user.is_active = user_dict.get('is_active', True)
                user.is_locked = user_dict.get('is_locked', False)
                user.must_change_password = user_dict.get('must_change_password', False)
                user.failed_login_attempts = user_dict.get('failed_login_attempts', 0)
                
                if user_dict.get('last_login'):
                    user.last_login = datetime.fromisoformat(user_dict['last_login'])
                if user_dict.get('last_password_change'):
                    user.last_password_change = datetime.fromisoformat(user_dict['last_password_change'])
                if user_dict.get('account_expires'):
                    user.account_expires = datetime.fromisoformat(user_dict['account_expires'])
                
                user.two_factor_enabled = user_dict.get('two_factor_enabled', False)
                user.two_factor_secret = user_dict.get('two_factor_secret', '')
                user.backup_codes = user_dict.get('backup_codes', [])
                user.session_timeout_minutes = user_dict.get('session_timeout_minutes', 30)
                
                # Berechtigungen
                additional_perms = user_dict.get('additional_permissions', [])
                user.additional_permissions = [Permission(p) for p in additional_perms]
                denied_perms = user_dict.get('denied_permissions', [])
                user.denied_permissions = [Permission(p) for p in denied_perms]
                
                user.created_at = datetime.fromisoformat(user_dict['created_at'])
                user.updated_at = datetime.fromisoformat(user_dict['updated_at'])
                user.notes = user_dict.get('notes', '')
                
                self.users[user_id] = user
                
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Benutzer: {e}")
    
    def cleanup_expired_sessions(self):
        """Bereinigt abgelaufene Sessions"""
        try:
            with self._lock:
                expired_sessions = [sid for sid, session in self.sessions.items() 
                                  if session.is_expired() or not session.is_active]
                
                for session_id in expired_sessions:
                    del self.sessions[session_id]
                
                if expired_sessions:
                    self.logger.info(f"Bereinigt {len(expired_sessions)} abgelaufene Sessions")
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Bereinigen der Sessions: {e}")
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Erstellt Sicherheitsstatistiken"""
        try:
            # Aktuelle Sessions
            active_sessions = len([s for s in self.sessions.values() if s.is_active and not s.is_expired()])
            
            # Benutzerstatistiken
            total_users = len(self.users)
            active_users = len([u for u in self.users.values() if u.is_active])
            locked_users = len([u for u in self.users.values() if u.is_locked])
            
            # Audit-Statistiken (letzte 24 Stunden)
            yesterday = datetime.now() - timedelta(hours=24)
            recent_events = self.get_audit_events(date_from=yesterday, limit=1000)
            
            failed_logins_24h = len([e for e in recent_events if e.event_type == AuditEventType.LOGIN_FAILED])
            successful_logins_24h = len([e for e in recent_events if e.event_type == AuditEventType.LOGIN])
            security_violations_24h = len([e for e in recent_events if e.event_type == AuditEventType.SECURITY_VIOLATION])
            
            return {
                'active_sessions': active_sessions,
                'total_users': total_users,
                'active_users': active_users,
                'locked_users': locked_users,
                'failed_logins_24h': failed_logins_24h,
                'successful_logins_24h': successful_logins_24h,
                'security_violations_24h': security_violations_24h,
                'encryption_enabled': self.settings['data_encryption_enabled'],
                'two_factor_enabled_users': len([u for u in self.users.values() if u.two_factor_enabled]),
                'password_expires_soon': len([u for u in self.users.values() 
                                            if u.last_password_change and 
                                            (datetime.now() - u.last_password_change).days > (self.settings['password_max_age_days'] - 7)]),
                'audit_events_total': len(recent_events)
            }
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Sicherheitsstatistiken: {e}")
            return {}
