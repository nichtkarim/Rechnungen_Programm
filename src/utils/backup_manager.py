"""
Backup-Manager für automatische Datensicherung
"""
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import zipfile


class BackupManager:
    """Verwaltet automatische Backups der Anwendungsdaten"""
    
    def __init__(self, data_dir: str = "storage", backup_dir: str = "backups"):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Maximale Anzahl Backups (7 täglich + 4 wöchentlich + 12 monatlich)
        self.max_daily_backups = 7
        self.max_weekly_backups = 4  
        self.max_monthly_backups = 12
    
    def create_backup(self, backup_name: Optional[str] = None) -> Path:
        """Erstellt ein vollständiges Backup aller Daten"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
        
        backup_path = self.backup_dir / backup_name
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Alle JSON-Dateien hinzufügen
            for json_file in self.data_dir.glob("*.json"):
                backup_zip.write(json_file, json_file.name)
            
            # Metadaten hinzufügen
            metadata = {
                "created_at": datetime.now().isoformat(),
                "data_dir": str(self.data_dir.absolute()),
                "files_backed_up": [f.name for f in self.data_dir.glob("*.json")],
                "version": "1.0"
            }
            
            backup_zip.writestr("backup_metadata.json", 
                              json.dumps(metadata, indent=2, ensure_ascii=False))
        
        print(f"✅ Backup erstellt: {backup_path}")
        return backup_path
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Stellt ein Backup wieder her"""
        try:
            # Aktuellen Zustand sichern
            emergency_backup = self.create_backup(f"emergency_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                # Metadaten prüfen
                if "backup_metadata.json" in backup_zip.namelist():
                    metadata = json.loads(backup_zip.read("backup_metadata.json"))
                    print(f"📦 Restore Backup vom: {metadata['created_at']}")
                
                # JSON-Dateien wiederherstellen
                for file_info in backup_zip.infolist():
                    if file_info.filename.endswith('.json') and file_info.filename != 'backup_metadata.json':
                        backup_zip.extract(file_info, self.data_dir)
            
            print(f"✅ Backup wiederhergestellt aus: {backup_path}")
            print(f"🛡️ Notfall-Backup erstellt: {emergency_backup}")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Wiederherstellen: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Bereinigt alte Backups nach Retention-Policy"""
        now = datetime.now()
        backups = []
        
        # Alle Backups sammeln und kategorisieren
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            try:
                # Timestamp aus Dateiname extrahieren
                timestamp_str = backup_file.stem.split("_", 1)[1][:15]  # YYYYMMDD_HHMMSS
                backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                age_days = (now - backup_date).days
                category = self._get_backup_category(age_days)
                
                backups.append({
                    'file': backup_file,
                    'date': backup_date,
                    'age_days': age_days,
                    'category': category
                })
            except ValueError:
                # Backup mit ungültigem Dateinamen
                continue
        
        # Nach Datum sortieren (neueste zuerst)
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        # Retention-Policy anwenden
        daily_count = 0
        weekly_count = 0
        monthly_count = 0
        
        for backup in backups:
            keep = False
            
            if backup['category'] == 'daily' and daily_count < self.max_daily_backups:
                keep = True
                daily_count += 1
            elif backup['category'] == 'weekly' and weekly_count < self.max_weekly_backups:
                keep = True
                weekly_count += 1
            elif backup['category'] == 'monthly' and monthly_count < self.max_monthly_backups:
                keep = True
                monthly_count += 1
            
            if not keep:
                try:
                    backup['file'].unlink()
                    print(f"🗑️ Altes Backup gelöscht: {backup['file'].name}")
                except Exception as e:
                    print(f"⚠️ Fehler beim Löschen von {backup['file'].name}: {e}")
    
    def _get_backup_category(self, age_days: int) -> str:
        """Kategorisiert Backup basierend auf Alter"""
        if age_days <= 7:
            return 'daily'
        elif age_days <= 30:
            return 'weekly' 
        else:
            return 'monthly'
    
    def get_backup_list(self) -> List[dict]:
        """Gibt Liste aller verfügbaren Backups zurück"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("backup_*.zip"), reverse=True):
            try:
                # Metadaten aus Backup lesen
                with zipfile.ZipFile(backup_file, 'r') as backup_zip:
                    if "backup_metadata.json" in backup_zip.namelist():
                        metadata = json.loads(backup_zip.read("backup_metadata.json"))
                        
                        backups.append({
                            'file': backup_file,
                            'name': backup_file.name,
                            'size': backup_file.stat().st_size,
                            'created_at': metadata.get('created_at', 'Unbekannt'),
                            'files_count': len(metadata.get('files_backed_up', []))
                        })
            except Exception:
                # Beschädigtes Backup überspringen
                continue
        
        return backups
    
    def auto_backup_if_needed(self):
        """Erstellt automatisch Backup wenn keins vom heutigen Tag existiert"""
        today = datetime.now().strftime("%Y%m%d")
        today_backups = list(self.backup_dir.glob(f"backup_{today}_*.zip"))
        
        if not today_backups:
            self.create_backup()
            self.cleanup_old_backups()
            return True
        return False
