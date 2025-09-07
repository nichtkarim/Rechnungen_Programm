"""
Compliance-Manager für DSGVO, GoBD und weitere Vorschriften
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from enum import Enum
import hashlib
import threading
from dataclasses import dataclass, asdict
import sqlite3


class ComplianceRegulation(Enum):
    """Compliance-Vorschriften"""
    GDPR = "DSGVO"  # Datenschutz-Grundverordnung
    GOBD = "GoBD"   # Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern
    HGB = "HGB"     # Handelsgesetzbuch
    AO = "AO"       # Abgabenordnung
    BDSG = "BDSG"   # Bundesdatenschutzgesetz


class DataCategory(Enum):
    """Datenkategorien"""
    PERSONAL_DATA = "Personenbezogene Daten"
    FINANCIAL_DATA = "Finanzdaten"
    BUSINESS_DATA = "Geschäftsdaten"
    COMMUNICATION_DATA = "Kommunikationsdaten"
    TECHNICAL_DATA = "Technische Daten"
    METADATA = "Metadaten"


class ProcessingPurpose(Enum):
    """Verarbeitungszwecke"""
    CONTRACT_FULFILLMENT = "Vertragserfüllung"
    ACCOUNTING = "Buchhaltung"
    MARKETING = "Marketing"
    ANALYTICS = "Analyse"
    LEGAL_OBLIGATION = "Rechtliche Verpflichtung"
    LEGITIMATE_INTEREST = "Berechtigtes Interesse"
    CONSENT = "Einwilligung"


class RetentionStatus(Enum):
    """Aufbewahrungsstatus"""
    ACTIVE = "Aktiv"
    ARCHIVED = "Archiviert"
    MARKED_FOR_DELETION = "Zur Löschung vorgemerkt"
    DELETED = "Gelöscht"
    LEGALLY_BLOCKED = "Rechtlich gesperrt"


@dataclass
class DataRetentionRule:
    """Aufbewahrungsregel"""
    regulation: ComplianceRegulation
    data_category: DataCategory
    retention_period_years: int
    purpose: ProcessingPurpose
    legal_basis: str
    deletion_criteria: str
    exceptions: List[str]
    
    def __post_init__(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


@dataclass
class DataRecord:
    """Datenaufzeichnung"""
    record_id: str
    data_category: DataCategory
    purpose: ProcessingPurpose
    subject_id: str  # Betroffene Person/Entität
    created_at: datetime
    last_accessed: Optional[datetime]
    retention_until: datetime
    status: RetentionStatus
    legal_basis: str
    processing_activities: List[str]
    consent_given: bool
    consent_date: Optional[datetime]
    consent_withdrawn: bool
    consent_withdrawal_date: Optional[datetime]
    
    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.retention_until, str):
            self.retention_until = datetime.fromisoformat(self.retention_until)
        if self.last_accessed and isinstance(self.last_accessed, str):
            self.last_accessed = datetime.fromisoformat(self.last_accessed)
        if self.consent_date and isinstance(self.consent_date, str):
            self.consent_date = datetime.fromisoformat(self.consent_date)
        if self.consent_withdrawal_date and isinstance(self.consent_withdrawal_date, str):
            self.consent_withdrawal_date = datetime.fromisoformat(self.consent_withdrawal_date)


@dataclass
class ComplianceViolation:
    """Compliance-Verletzung"""
    violation_id: str
    regulation: ComplianceRegulation
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime]
    resolution_notes: str
    affected_records: List[str]
    remediation_actions: List[str]
    
    def __post_init__(self):
        if isinstance(self.detected_at, str):
            self.detected_at = datetime.fromisoformat(self.detected_at)
        if self.resolved_at and isinstance(self.resolved_at, str):
            self.resolved_at = datetime.fromisoformat(self.resolved_at)


class ComplianceManager:
    """Compliance-Manager"""
    
    def __init__(self, data_directory: str = "data"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Datenstrukturen
        self.retention_rules: Dict[str, DataRetentionRule] = {}
        self.data_records: Dict[str, DataRecord] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        
        # Thread-Lock
        self._lock = threading.Lock()
        
        # Datenbank initialisieren
        self._init_database()
        
        # Standard-Regeln laden
        self._load_default_rules()
        
        # Bestehende Daten laden
        self.load_data()
    
    def _init_database(self):
        """Initialisiert Compliance-Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            
            with sqlite3.connect(db_file) as conn:
                # Aufbewahrungsregeln
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS retention_rules (
                        rule_id TEXT PRIMARY KEY,
                        regulation TEXT NOT NULL,
                        data_category TEXT NOT NULL,
                        retention_period_years INTEGER NOT NULL,
                        purpose TEXT NOT NULL,
                        legal_basis TEXT NOT NULL,
                        deletion_criteria TEXT,
                        exceptions TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Datenaufzeichnungen
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS data_records (
                        record_id TEXT PRIMARY KEY,
                        data_category TEXT NOT NULL,
                        purpose TEXT NOT NULL,
                        subject_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT,
                        retention_until TEXT NOT NULL,
                        status TEXT NOT NULL,
                        legal_basis TEXT NOT NULL,
                        processing_activities TEXT,
                        consent_given BOOLEAN,
                        consent_date TEXT,
                        consent_withdrawn BOOLEAN,
                        consent_withdrawal_date TEXT
                    )
                """)
                
                # Compliance-Verletzungen
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS violations (
                        violation_id TEXT PRIMARY KEY,
                        regulation TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        description TEXT NOT NULL,
                        detected_at TEXT NOT NULL,
                        resolved_at TEXT,
                        resolution_notes TEXT,
                        affected_records TEXT,
                        remediation_actions TEXT
                    )
                """)
                
                # Indizes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_records_subject ON data_records(subject_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_records_category ON data_records(data_category)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_records_retention ON data_records(retention_until)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_violations_regulation ON violations(regulation)")
                
        except Exception as e:
            self.logger.error(f"Fehler bei Datenbank-Initialisierung: {e}")
    
    def _load_default_rules(self):
        """Lädt Standard-Aufbewahrungsregeln"""
        default_rules = [
            # DSGVO-Regeln
            DataRetentionRule(
                regulation=ComplianceRegulation.GDPR,
                data_category=DataCategory.PERSONAL_DATA,
                retention_period_years=3,
                purpose=ProcessingPurpose.CONTRACT_FULFILLMENT,
                legal_basis="Art. 6 Abs. 1 lit. b DSGVO",
                deletion_criteria="Nach Vertragsbeendigung + 3 Jahre",
                exceptions=["Rechtliche Streitigkeiten", "Steuerprüfung"]
            ),
            
            # GoBD-Regeln
            DataRetentionRule(
                regulation=ComplianceRegulation.GOBD,
                data_category=DataCategory.FINANCIAL_DATA,
                retention_period_years=10,
                purpose=ProcessingPurpose.ACCOUNTING,
                legal_basis="§ 147 AO",
                deletion_criteria="Nach 10 Jahren ab Geschäftsjahresende",
                exceptions=["Laufende Verfahren", "Betriebsprüfung"]
            ),
            
            DataRetentionRule(
                regulation=ComplianceRegulation.GOBD,
                data_category=DataCategory.BUSINESS_DATA,
                retention_period_years=6,
                purpose=ProcessingPurpose.ACCOUNTING,
                legal_basis="§ 257 HGB",
                deletion_criteria="Nach 6 Jahren ab Entstehung",
                exceptions=["Handelsrechtliche Aufbewahrung"]
            ),
            
            # HGB-Regeln
            DataRetentionRule(
                regulation=ComplianceRegulation.HGB,
                data_category=DataCategory.BUSINESS_DATA,
                retention_period_years=10,
                purpose=ProcessingPurpose.ACCOUNTING,
                legal_basis="§ 257 HGB",
                deletion_criteria="Nach 10 Jahren (Bücher, Inventare)",
                exceptions=["Laufende Geschäfte"]
            ),
            
            # Kommunikationsdaten
            DataRetentionRule(
                regulation=ComplianceRegulation.GDPR,
                data_category=DataCategory.COMMUNICATION_DATA,
                retention_period_years=1,
                purpose=ProcessingPurpose.LEGITIMATE_INTEREST,
                legal_basis="Art. 6 Abs. 1 lit. f DSGVO",
                deletion_criteria="Nach 1 Jahr oder Widerruf",
                exceptions=["Rechtliche Dokumentation"]
            ),
            
            # Technische Daten/Logs
            DataRetentionRule(
                regulation=ComplianceRegulation.GDPR,
                data_category=DataCategory.TECHNICAL_DATA,
                retention_period_years=1,
                purpose=ProcessingPurpose.LEGITIMATE_INTEREST,
                legal_basis="Art. 6 Abs. 1 lit. f DSGVO",
                deletion_criteria="Nach 1 Jahr automatisch",
                exceptions=["Sicherheitsvorfälle", "Forensik"]
            )
        ]
        
        for rule in default_rules:
            rule_id = self._generate_rule_id(rule)
            if rule_id not in self.retention_rules:
                self.retention_rules[rule_id] = rule
        
        self.save_retention_rules()
    
    def _generate_rule_id(self, rule: DataRetentionRule) -> str:
        """Generiert eindeutige Regel-ID"""
        content = f"{rule.regulation.value}_{rule.data_category.value}_{rule.purpose.value}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _generate_record_id(self) -> str:
        """Generiert eindeutige Datensatz-ID"""
        import secrets
        return f"rec_{secrets.token_hex(12)}"
    
    def _generate_violation_id(self) -> str:
        """Generiert eindeutige Verletzungs-ID"""
        import secrets
        return f"vio_{secrets.token_hex(12)}"
    
    def add_retention_rule(self, rule: DataRetentionRule) -> str:
        """Fügt Aufbewahrungsregel hinzu"""
        try:
            with self._lock:
                rule_id = self._generate_rule_id(rule)
                rule.updated_at = datetime.now()
                self.retention_rules[rule_id] = rule
                
                # In Datenbank speichern
                self._save_rule_to_db(rule_id, rule)
                
                self.logger.info(f"Aufbewahrungsregel hinzugefügt: {rule_id}")
                return rule_id
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der Regel: {e}")
            raise
    
    def add_data_record(self, data_category: DataCategory, purpose: ProcessingPurpose,
                       subject_id: str, legal_basis: str, processing_activities: List[str],
                       consent_given: bool = False) -> str:
        """Fügt Datenaufzeichnung hinzu"""
        try:
            with self._lock:
                # Passende Aufbewahrungsregel finden
                retention_rule = self._find_retention_rule(data_category, purpose)
                if not retention_rule:
                    raise ValueError(f"Keine Aufbewahrungsregel für {data_category.value}/{purpose.value}")
                
                # Aufbewahrungszeit berechnen
                retention_until = datetime.now() + timedelta(days=retention_rule.retention_period_years * 365)
                
                record = DataRecord(
                    record_id=self._generate_record_id(),
                    data_category=data_category,
                    purpose=purpose,
                    subject_id=subject_id,
                    created_at=datetime.now(),
                    last_accessed=None,
                    retention_until=retention_until,
                    status=RetentionStatus.ACTIVE,
                    legal_basis=legal_basis,
                    processing_activities=processing_activities,
                    consent_given=consent_given,
                    consent_date=datetime.now() if consent_given else None,
                    consent_withdrawn=False,
                    consent_withdrawal_date=None
                )
                
                self.data_records[record.record_id] = record
                
                # In Datenbank speichern
                self._save_record_to_db(record)
                
                self.logger.info(f"Datenaufzeichnung hinzugefügt: {record.record_id}")
                return record.record_id
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der Datenaufzeichnung: {e}")
            raise
    
    def _find_retention_rule(self, data_category: DataCategory, purpose: ProcessingPurpose) -> Optional[DataRetentionRule]:
        """Findet passende Aufbewahrungsregel"""
        for rule in self.retention_rules.values():
            if rule.data_category == data_category and rule.purpose == purpose:
                return rule
        
        # Fallback: Allgemeine Regel für Kategorie
        for rule in self.retention_rules.values():
            if rule.data_category == data_category:
                return rule
        
        return None
    
    def access_data_record(self, record_id: str):
        """Registriert Datenzugriff"""
        try:
            with self._lock:
                if record_id in self.data_records:
                    self.data_records[record_id].last_accessed = datetime.now()
                    self._save_record_to_db(self.data_records[record_id])
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Registrieren des Datenzugriffs: {e}")
    
    def withdraw_consent(self, subject_id: str, data_category: Optional[DataCategory] = None) -> List[str]:
        """Widerruft Einwilligung"""
        try:
            with self._lock:
                affected_records = []
                
                for record in self.data_records.values():
                    if (record.subject_id == subject_id and 
                        record.consent_given and 
                        not record.consent_withdrawn and
                        (data_category is None or record.data_category == data_category)):
                        
                        record.consent_withdrawn = True
                        record.consent_withdrawal_date = datetime.now()
                        
                        # Status auf Löschung setzen wenn keine andere Rechtsgrundlage
                        if "Einwilligung" in record.legal_basis:
                            record.status = RetentionStatus.MARKED_FOR_DELETION
                        
                        self._save_record_to_db(record)
                        affected_records.append(record.record_id)
                
                self.logger.info(f"Einwilligung widerrufen für {subject_id}, {len(affected_records)} Datensätze betroffen")
                return affected_records
                
        except Exception as e:
            self.logger.error(f"Fehler beim Widerruf der Einwilligung: {e}")
            raise
    
    def request_data_deletion(self, subject_id: str, reason: str = "Betroffenenrecht") -> List[str]:
        """Beantragt Datenlöschung"""
        try:
            with self._lock:
                affected_records = []
                
                for record in self.data_records.values():
                    if record.subject_id == subject_id and record.status == RetentionStatus.ACTIVE:
                        # Prüfen ob Löschung möglich (keine rechtliche Aufbewahrungspflicht)
                        if self._can_delete_record(record):
                            record.status = RetentionStatus.MARKED_FOR_DELETION
                            self._save_record_to_db(record)
                            affected_records.append(record.record_id)
                        else:
                            # Datensatz rechtlich gesperrt
                            record.status = RetentionStatus.LEGALLY_BLOCKED
                            self._save_record_to_db(record)
                
                self.logger.info(f"Löschantrag für {subject_id}, {len(affected_records)} Datensätze zur Löschung vorgemerkt")
                return affected_records
                
        except Exception as e:
            self.logger.error(f"Fehler beim Löschantrag: {e}")
            raise
    
    def _can_delete_record(self, record: DataRecord) -> bool:
        """Prüft ob Datensatz gelöscht werden kann"""
        # Rechtliche Aufbewahrungspflichten prüfen
        if record.purpose in [ProcessingPurpose.ACCOUNTING, ProcessingPurpose.LEGAL_OBLIGATION]:
            return datetime.now() > record.retention_until
        
        # Bei Einwilligung als einziger Rechtsgrundlage: Löschung möglich
        if record.consent_given and not record.consent_withdrawn:
            return False  # Einwilligung noch aktiv
        
        if record.consent_withdrawn and "Einwilligung" in record.legal_basis:
            return True  # Einwilligung widerrufen
        
        # Andere Rechtsgrundlagen: Aufbewahrungszeit prüfen
        return datetime.now() > record.retention_until
    
    def get_subject_data(self, subject_id: str) -> Dict[str, Any]:
        """Liefert alle Daten zu einer betroffenen Person (Auskunftsrecht)"""
        try:
            subject_records = []
            
            for record in self.data_records.values():
                if record.subject_id == subject_id:
                    # Zugriff registrieren
                    self.access_data_record(record.record_id)
                    
                    subject_records.append({
                        'record_id': record.record_id,
                        'data_category': record.data_category.value,
                        'purpose': record.purpose.value,
                        'created_at': record.created_at.isoformat(),
                        'retention_until': record.retention_until.isoformat(),
                        'status': record.status.value,
                        'legal_basis': record.legal_basis,
                        'processing_activities': record.processing_activities,
                        'consent_given': record.consent_given,
                        'consent_date': record.consent_date.isoformat() if record.consent_date else None,
                        'consent_withdrawn': record.consent_withdrawn,
                        'consent_withdrawal_date': record.consent_withdrawal_date.isoformat() if record.consent_withdrawal_date else None
                    })
            
            return {
                'subject_id': subject_id,
                'data_exported_at': datetime.now().isoformat(),
                'total_records': len(subject_records),
                'records': subject_records
            }
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Betroffenendaten: {e}")
            raise
    
    def check_compliance(self) -> List[ComplianceViolation]:
        """Prüft Compliance-Verstöße"""
        violations = []
        
        try:
            # Aufbewahrungszeiten prüfen
            violations.extend(self._check_retention_violations())
            
            # Einwilligungen prüfen
            violations.extend(self._check_consent_violations())
            
            # Datenschutz-Grundsätze prüfen
            violations.extend(self._check_data_protection_principles())
            
            # Neue Verstöße speichern
            for violation in violations:
                if violation.violation_id not in self.violations:
                    self.violations[violation.violation_id] = violation
                    self._save_violation_to_db(violation)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Fehler bei Compliance-Prüfung: {e}")
            return []
    
    def _check_retention_violations(self) -> List[ComplianceViolation]:
        """Prüft Verstöße gegen Aufbewahrungszeiten"""
        violations = []
        now = datetime.now()
        
        for record in self.data_records.values():
            # Überaufbewahrung prüfen
            if (record.status == RetentionStatus.ACTIVE and 
                now > record.retention_until and
                not record.consent_given):
                
                violation = ComplianceViolation(
                    violation_id=self._generate_violation_id(),
                    regulation=ComplianceRegulation.GDPR,
                    severity="HIGH",
                    description=f"Überaufbewahrung von Daten: {record.record_id}",
                    detected_at=now,
                    resolved_at=None,
                    resolution_notes="",
                    affected_records=[record.record_id],
                    remediation_actions=["Daten löschen oder archivieren", "Rechtsgrundlage prüfen"]
                )
                violations.append(violation)
        
        return violations
    
    def _check_consent_violations(self) -> List[ComplianceViolation]:
        """Prüft Verstöße bei Einwilligungen"""
        violations = []
        
        for record in self.data_records.values():
            # Widerrufene Einwilligung aber Daten noch aktiv
            if (record.consent_withdrawn and 
                record.status == RetentionStatus.ACTIVE and
                "Einwilligung" in record.legal_basis):
                
                violation = ComplianceViolation(
                    violation_id=self._generate_violation_id(),
                    regulation=ComplianceRegulation.GDPR,
                    severity="CRITICAL",
                    description=f"Datenverarbeitung nach Einwilligungswiderruf: {record.record_id}",
                    detected_at=datetime.now(),
                    resolved_at=None,
                    resolution_notes="",
                    affected_records=[record.record_id],
                    remediation_actions=["Sofortige Löschung", "Alternative Rechtsgrundlage prüfen"]
                )
                violations.append(violation)
        
        return violations
    
    def _check_data_protection_principles(self) -> List[ComplianceViolation]:
        """Prüft Datenschutz-Grundsätze"""
        violations = []
        
        # Zweckbindung prüfen
        purpose_count = {}
        for record in self.data_records.values():
            key = (record.subject_id, record.data_category)
            if key not in purpose_count:
                purpose_count[key] = set()
            purpose_count[key].add(record.purpose)
        
        # Zu viele verschiedene Zwecke für gleiche Daten
        for (subject_id, data_category), purposes in purpose_count.items():
            if len(purposes) > 3:  # Schwellwert
                violation = ComplianceViolation(
                    violation_id=self._generate_violation_id(),
                    regulation=ComplianceRegulation.GDPR,
                    severity="MEDIUM",
                    description=f"Möglicher Verstoß gegen Zweckbindung: {subject_id}/{data_category.value}",
                    detected_at=datetime.now(),
                    resolved_at=None,
                    resolution_notes="",
                    affected_records=[],
                    remediation_actions=["Zwecke überprüfen", "Datenminimierung anwenden"]
                )
                violations.append(violation)
        
        return violations
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """Bereinigt abgelaufene Daten"""
        try:
            cleanup_stats = {
                'deleted': 0,
                'archived': 0,
                'errors': 0
            }
            
            now = datetime.now()
            
            for record in list(self.data_records.values()):
                try:
                    # Zur Löschung vorgemerkte Daten
                    if record.status == RetentionStatus.MARKED_FOR_DELETION:
                        del self.data_records[record.record_id]
                        self._delete_record_from_db(record.record_id)
                        cleanup_stats['deleted'] += 1
                        continue
                    
                    # Abgelaufene Aufbewahrungszeit
                    if (record.status == RetentionStatus.ACTIVE and 
                        now > record.retention_until and
                        self._can_delete_record(record)):
                        
                        # Archivieren statt löschen für wichtige Geschäftsdaten
                        if record.data_category in [DataCategory.FINANCIAL_DATA, DataCategory.BUSINESS_DATA]:
                            record.status = RetentionStatus.ARCHIVED
                            self._save_record_to_db(record)
                            cleanup_stats['archived'] += 1
                        else:
                            del self.data_records[record.record_id]
                            self._delete_record_from_db(record.record_id)
                            cleanup_stats['deleted'] += 1
                
                except Exception as e:
                    self.logger.error(f"Fehler beim Bereinigen von Record {record.record_id}: {e}")
                    cleanup_stats['errors'] += 1
            
            self.logger.info(f"Datenbereinigung: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Fehler bei Datenbereinigung: {e}")
            return {'deleted': 0, 'archived': 0, 'errors': 1}
    
    def generate_compliance_report(self) -> str:  # override vorherige falls dict
        """Erzeugt einen formatierten Compliance-Bericht als Text"""
        stats = self.get_compliance_stats()
        lines = [
            'COMPLIANCE-BERICHT', '='*60, '',
            f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}", '',
            'KENNZAHLEN', '-'*30,
            f"Gesamte Datensätze: {stats['total_records']}",
            f"Aktive Verstöße: {stats['active_violations']}",
            f"Aufbewahrungsregeln: {stats['retention_rules']}",
            f"Ablaufende Datensätze (30 Tage): {stats['expiring_records']}", '',
            'VERSTÖSSE NACH SCHWERE', '-'*30,
            f"Kritisch: {stats['critical_violations']}",
            f"Hoch: {stats['high_violations']}",
            f"Mittel: {stats['medium_violations']}",
            f"Niedrig: {stats['low_violations']}", '',
            'EMPFEHLUNGEN', '-'*30
        ]
        if stats['active_violations'] > 0:
            lines.append('• Offene Verstöße priorisiert bearbeiten')
        if stats['expiring_records'] > 0:
            lines.append('• Ablaufende Datensätze für Bereinigung prüfen')
        lines.extend([
            '• Regelmäßige Compliance-Prüfung durchführen',
            '• Aufbewahrungsregeln dokumentieren', '',
            'ENDE DES BERICHTS'
        ])
        return '\n'.join(lines)
    
    def get_retention_rules(self) -> List[DataRetentionRule]:
        """Gibt alle Aufbewahrungsregeln als Liste zurück"""
        return list(self.retention_rules.values())
    
    def get_active_violations(self) -> List[ComplianceViolation]:
        """Aktive (nicht gelöste) Verstöße"""
        return [v for v in self.violations.values() if v.resolved_at is None]
    
    def get_data_records(self) -> List[Dict[str, Any]]:
        """Gibt Datenaufzeichnungen als dict-Liste zurück (GUI-kompatibel)"""
        records = []
        for rec in self.data_records.values():
            records.append({
                'id': rec.record_id,
                'type': rec.data_category.value,
                'subject_id': rec.subject_id,
                'created_at': rec.created_at,
                'retention_until': rec.retention_until,
                'status': rec.status.value,
            })
        return records
    
    def get_compliance_stats(self) -> Dict[str, Any]:
        """Aggregierte Kennzahlen für Dashboard"""
        active_violations = self.get_active_violations()
        critical = len([v for v in active_violations if v.severity.upper() == 'CRITICAL'])
        high = len([v for v in active_violations if v.severity.upper() == 'HIGH'])
        medium = len([v for v in active_violations if v.severity.upper() == 'MEDIUM'])
        low = len([v for v in active_violations if v.severity.upper() == 'LOW'])
        expiring = len([r for r in self.data_records.values() if (r.retention_until - datetime.now()).days <= 30 and r.status == RetentionStatus.ACTIVE])
        return {
            'total_records': len(self.data_records),
            'active_violations': len(active_violations),
            'retention_rules': len(self.retention_rules),
            'expiring_records': expiring,
            'critical_violations': critical,
            'high_violations': high,
            'medium_violations': medium,
            'low_violations': low,
            'last_check': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'next_cleanup': (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')
        }
    
    # Datenbank-Methoden
    def _save_rule_to_db(self, rule_id: str, rule: DataRetentionRule):
        """Speichert Regel in Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            with sqlite3.connect(db_file) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO retention_rules 
                    (rule_id, regulation, data_category, retention_period_years, purpose, 
                     legal_basis, deletion_criteria, exceptions, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule_id,
                    rule.regulation.value,
                    rule.data_category.value,
                    rule.retention_period_years,
                    rule.purpose.value,
                    rule.legal_basis,
                    rule.deletion_criteria,
                    json.dumps(rule.exceptions),
                    rule.created_at.isoformat(),
                    rule.updated_at.isoformat()
                ))
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Regel in DB: {e}")
    
    def _save_record_to_db(self, record: DataRecord):
        """Speichert Datensatz in Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            with sqlite3.connect(db_file) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO data_records 
                    (record_id, data_category, purpose, subject_id, created_at, last_accessed,
                     retention_until, status, legal_basis, processing_activities, consent_given,
                     consent_date, consent_withdrawn, consent_withdrawal_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.record_id,
                    record.data_category.value,
                    record.purpose.value,
                    record.subject_id,
                    record.created_at.isoformat(),
                    record.last_accessed.isoformat() if record.last_accessed else None,
                    record.retention_until.isoformat(),
                    record.status.value,
                    record.legal_basis,
                    json.dumps(record.processing_activities),
                    record.consent_given,
                    record.consent_date.isoformat() if record.consent_date else None,
                    record.consent_withdrawn,
                    record.consent_withdrawal_date.isoformat() if record.consent_withdrawal_date else None
                ))
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern des Datensatzes in DB: {e}")
    
    def _save_violation_to_db(self, violation: ComplianceViolation):
        """Speichert Verstoß in Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            with sqlite3.connect(db_file) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO violations 
                    (violation_id, regulation, severity, description, detected_at, resolved_at,
                     resolution_notes, affected_records, remediation_actions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    violation.violation_id,
                    violation.regulation.value,
                    violation.severity,
                    violation.description,
                    violation.detected_at.isoformat(),
                    violation.resolved_at.isoformat() if violation.resolved_at else None,
                    violation.resolution_notes,
                    json.dumps(violation.affected_records),
                    json.dumps(violation.remediation_actions)
                ))
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern des Verstoßes in DB: {e}")
    
    def _delete_record_from_db(self, record_id: str):
        """Löscht Datensatz aus Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            with sqlite3.connect(db_file) as conn:
                conn.execute("DELETE FROM data_records WHERE record_id = ?", (record_id,))
        except Exception as e:
            self.logger.error(f"Fehler beim Löschen des Datensatzes aus DB: {e}")
    
    def save_data(self):
        """Speichert alle Daten"""
        self.save_retention_rules()
        # Datensätze und Verstöße werden direkt in DB gespeichert
    
    def save_retention_rules(self):
        """Speichert Aufbewahrungsregeln in JSON"""
        try:
            rules_data = {}
            for rule_id, rule in self.retention_rules.items():
                rules_data[rule_id] = asdict(rule)
                # Enums zu Strings konvertieren
                rules_data[rule_id]['regulation'] = rule.regulation.value
                rules_data[rule_id]['data_category'] = rule.data_category.value
                rules_data[rule_id]['purpose'] = rule.purpose.value
                # Datetimes zu Strings
                rules_data[rule_id]['created_at'] = rule.created_at.isoformat()
                rules_data[rule_id]['updated_at'] = rule.updated_at.isoformat()
            
            rules_file = self.data_directory / "retention_rules.json"
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Regeln: {e}")
    
    def load_data(self):
        """Lädt alle Daten"""
        self.load_retention_rules()
        self.load_data_records()
        self.load_violations()
    
    def load_retention_rules(self):
        """Lädt Aufbewahrungsregeln"""
        try:
            rules_file = self.data_directory / "retention_rules.json"
            if not rules_file.exists():
                return
            
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            for rule_id, rule_dict in rules_data.items():
                rule = DataRetentionRule(
                    regulation=ComplianceRegulation(rule_dict['regulation']),
                    data_category=DataCategory(rule_dict['data_category']),
                    retention_period_years=rule_dict['retention_period_years'],
                    purpose=ProcessingPurpose(rule_dict['purpose']),
                    legal_basis=rule_dict['legal_basis'],
                    deletion_criteria=rule_dict['deletion_criteria'],
                    exceptions=rule_dict['exceptions']
                )
                rule.created_at = datetime.fromisoformat(rule_dict['created_at'])
                rule.updated_at = datetime.fromisoformat(rule_dict['updated_at'])
                
                self.retention_rules[rule_id] = rule
                
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Regeln: {e}")
    
    def load_data_records(self):
        """Lädt Datenaufzeichnungen aus Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            if not db_file.exists():
                return
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM data_records")
                
                for row in cursor.fetchall():
                    record = DataRecord(
                        record_id=row['record_id'],
                        data_category=DataCategory(row['data_category']),
                        purpose=ProcessingPurpose(row['purpose']),
                        subject_id=row['subject_id'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None,
                        retention_until=datetime.fromisoformat(row['retention_until']),
                        status=RetentionStatus(row['status']),
                        legal_basis=row['legal_basis'],
                        processing_activities=json.loads(row['processing_activities'] or '[]'),
                        consent_given=bool(row['consent_given']),
                        consent_date=datetime.fromisoformat(row['consent_date']) if row['consent_date'] else None,
                        consent_withdrawn=bool(row['consent_withdrawn']),
                        consent_withdrawal_date=datetime.fromisoformat(row['consent_withdrawal_date']) if row['consent_withdrawal_date'] else None
                    )
                    
                    self.data_records[record.record_id] = record
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Datensätze: {e}")
    
    def load_violations(self):
        """Lädt Compliance-Verstöße aus Datenbank"""
        try:
            db_file = self.data_directory / "compliance.db"
            if not db_file.exists():
                return
            
            with sqlite3.connect(db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM violations")
                
                for row in cursor.fetchall():
                    violation = ComplianceViolation(
                        violation_id=row['violation_id'],
                        regulation=ComplianceRegulation(row['regulation']),
                        severity=row['severity'],
                        description=row['description'],
                        detected_at=datetime.fromisoformat(row['detected_at']),
                        resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
                        resolution_notes=row['resolution_notes'] or '',
                        affected_records=json.loads(row['affected_records'] or '[]'),
                        remediation_actions=json.loads(row['remediation_actions'] or '[]')
                    )
                    
                    self.violations[violation.violation_id] = violation
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Verstöße: {e}")
