# 📄 Professionelles Rechnungs-Tool

Ein umfassendes, deutsches Rechnungs- und Dokumenten-Management-Tool mit moderner GUI und professionellen Features für kleine und mittelständische Unternehmen.

![Python](https://img.shields.io/badge/Python-3.13+-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 **Neue Features (v2.0)**

### 🔒 **Automatische Backup-Funktionen**
- Tägliche, wöchentliche und monatliche Backups
- Automatische Bereinigung alter Backups
- Ein-Klick Backup-Wiederherstellung
- Komprimierte ZIP-Archive mit Metadaten

### ✅ **Erweiterte Datenvalidierung** 
- IBAN/BIC-Prüfung für deutsche Bankverbindungen
- USt-IdNr. und Steuernummer-Validierung
- Plausibilitätsprüfungen für Geschäftsdaten
- Datenintegritäts-Checker für Inkonsistenzen

### 👁️ **PDF-Vorschau & Massen-Export**
- Sofortige PDF-Vorschau ohne Speichern
- Massen-Export nach Kunde oder Zeitraum
- Flexible Dateinamen-Muster
- Bulk-Operationen für große Datenmengen

### 📊 **Umfassendes Dashboard**
- Interaktive Statistiken und KPIs
- Umsatz-Trends und Kundenanalysen
- Grafische Auswertungen (Matplotlib)
- Exportierbare Berichte

### 🎛️ **Erweiterte Benutzeroberfläche**
- Moderne Menüleiste mit allen Funktionen
- Verbesserte Toolbar mit Icon-Buttons
- Kontextmenüs und Tastenkürzel
- Responsive Layout-Design

## 📊 **Übersicht der Hauptfunktionen**

### 🏢 **Stammdaten-Verwaltung**
- Vollständige Firmenstammdaten mit Bankverbindung
- Kleinunternehmer-Regelung (§19 UStG) unterstützt
- Logo-Integration für Corporate Identity
- Automatische Plausibilitätsprüfung

### 👥 **Professionelle Kundenverwaltung**
- Automatische Kundennummerierung
- Separate Rechnungs- und Lieferadressen
- USt-IdNr. für EU-Geschäfte (Reverse Charge)
- Import/Export-Funktionen

### 📄 **Dokumenten-Erstellung**
- **Angebote** mit Umwandlung zu Rechnungen
- **Rechnungen** mit allen deutschen Pflichtangaben
- **Gutschriften** mit Referenz zur Originalrechnung
- **Storno-Belege** für Korrekturen

### 💰 **Präzise Berechnungen**
- Decimal-Arithmetik (keine Rundungsfehler)
- Deutsche Steuersätze: 0%, 7%, 19%
- Reverse Charge für EU-Geschäfte
- Skonto und Zahlungskonditionen

### 📋 **PDF-Export & Vorschau**
- Professionelle PDF-Layouts nach deutschen Standards
- Sofortige Vorschau vor dem Speichern
- Anpassbare Corporate Colors
- Batch-Export für mehrere Dokumente

### 🎨 **Moderne GUI**
- CustomTkinter für native Windows-Optik
- Dark/Light/System Theme-Unterstützung
- Responsive Design
- Intuitive Bedienung

### 💾 **Sichere Datenhaltung**
- JSON-basierte Offline-Speicherung
- Automatische Backups mit Retention-Policy
- Datenvalidierung und Integritätsprüfung
- Export/Import für Datenmigration

## 🚀 **Installation & Einrichtung**

### Voraussetzungen
- Python 3.13+ (empfohlen)
- Windows 10/11 (primär getestet)
- ca. 50 MB freier Speicherplatz

### Installation

1. **Repository klonen oder herunterladen:**
```bash
git clone https://github.com/ihr-repo/rechnungs-tool.git
cd rechnungs-tool
```

2. **Virtuelle Umgebung erstellen:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. **Abhängigkeiten installieren:**
```bash
pip install -r requirements.txt
```

4. **Anwendung starten:**
```bash
python main.py
```

### Automatisierte Einrichtung (VS Code)
Falls Sie VS Code verwenden, nutzen Sie einfach:
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Rechnungs-Tool starten"

## 📚 **Erste Schritte**

### 1. Firmendaten einrichten
- Öffnen Sie "Firma" → "Stammdaten"
- Tragen Sie alle relevanten Unternehmensdaten ein
- Aktivieren Sie bei Bedarf "Kleinunternehmer (§19 UStG)"

### 2. Ersten Kunden anlegen
- Klicken Sie "Kunde" in der Toolbar
- Füllen Sie die Pflichtfelder aus
- Die Kundennummer wird automatisch vergeben

### 3. Erste Rechnung erstellen
- Klicken Sie "Rechnung" in der Toolbar
- Wählen Sie den Kunden aus
- Fügen Sie Positionen hinzu
- Nutzen Sie "👁️ Vorschau" vor dem Export

### 4. Backup einrichten
- "Datei" → "Backup erstellen" für manuelles Backup
- Automatische Backups werden täglich erstellt
- Backups finden Sie im `backups/` Ordner

## 🛠️ **Erweiterte Funktionen**

### Dashboard & Statistiken
- "Extras" → "Dashboard" für umfassende Übersichten
- Monatliche Umsatztrends visualisieren
- Top-Kunden und Zahlungsverhalten analysieren
- Berichte als Text exportieren

### Datenvalidierung
- "Extras" → "Datenvalidierung" für Konsistenzprüfung
- Automatische Erkennung von Duplikaten
- Plausibilitätsprüfungen für alle Eingaben
- Korrekturvorschläge bei Fehlern

### Massen-Export
- "Extras" → "Massen-Export" für Batch-Operationen
- Export nach Kunde, Zeitraum oder Dokumenttyp
- Flexible Dateinamen-Muster
- Automatische Ordner-Strukturierung

### Backup & Wiederherstellung
- Automatische tägliche Backups
- Backup-Retention: 7 täglich, 4 wöchentlich, 12 monatlich
- Ein-Klick Wiederherstellung mit Sicherheits-Backup
- ZIP-komprimiert mit Metadaten

## 📁 **Projektstruktur**

```
Rechnungs-Tool/
├── main.py                 # Startdatei
├── requirements.txt        # Python-Abhängigkeiten
├── README.md              # Diese Dokumentation
├── src/                   # Quellcode
│   ├── models/           # Datenmodelle
│   ├── gui/              # GUI-Komponenten
│   └── utils/            # Hilfsfunktionen
├── storage/              # JSON-Datenspeicher
├── backups/              # Automatische Backups
└── .vscode/              # VS Code Konfiguration
```

### Kern-Module

**Datenmodelle (`src/models/`):**
- `CompanyData` - Firmenstammdaten
- `Customer` - Kundendaten mit Lieferadressen  
- `Invoice` - Rechnungen/Dokumente mit Positionen
- `AppSettings` - Anwendungseinstellungen

**GUI (`src/gui/`):**
- `MainWindow` - Hauptfenster mit Navigation
- `DashboardWindow` - Statistiken und Analysen
- `InvoiceEditWindow` - Dokumenten-Editor
- `CustomerEditWindow` - Kunden-Editor

**Utilities (`src/utils/`):**
- `DataManager` - Zentrale Datenverwaltung
- `PDFGenerator` - PDF-Erstellung und Export
- `BackupManager` - Automatische Backups
- `BusinessValidator` - Erweiterte Validierung

## ⚙️ **Konfiguration**

### Anwendungseinstellungen (`storage/settings.json`)
```json
{
  "theme_mode": "system",
  "invoice_number_format": "R{year}-{counter:04d}",
  "default_payment_terms": 14,
  "default_tax_rate": "0.19",
  "pdf_company_color": "#2E86AB"
}
```

### Backup-Konfiguration
- **Tägliche Backups**: 7 Tage aufbewahren
- **Wöchentliche Backups**: 4 Wochen aufbewahren  
- **Monatliche Backups**: 12 Monate aufbewahren
- **Automatische Bereinigung**: Bei jedem Start

## 🔧 **Anpassungen & Erweiterungen**

### Rechnungsnummern-Format ändern
```python
# In den Einstellungen
"invoice_number_format": "R{year}-{counter:04d}"
# Erzeugt: R2025-0001, R2025-0002, ...

"invoice_number_format": "{year}{month}{counter:03d}"  
# Erzeugt: 2025090001, 2025090002, ...
```

### PDF-Layout anpassen
```python
# In PDFGenerator-Klasse
self.pdf_color = HexColor("#2E86AB")  # Firmenfarbe
self.font_size = 10                   # Schriftgröße
```

### Neue Dokumenttypen hinzufügen
```python
# In models/__init__.py
class DocumentType(Enum):
    ANGEBOT = "Angebot"
    RECHNUNG = "Rechnung"
    GUTSCHRIFT = "Gutschrift"
    LIEFERSCHEIN = "Lieferschein"  # Neu
```

## 🐛 **Troubleshooting**

### Häufige Probleme

**Anwendung startet nicht:**
```bash
# Python-Version prüfen
python --version  # Sollte 3.13+ sein

# Abhängigkeiten neu installieren
pip install -r requirements.txt --upgrade
```

**Backup-Fehler:**
- Prüfen Sie Schreibrechte im `backups/` Ordner
- Stellen Sie sicher, dass genügend Speicherplatz vorhanden ist

**PDF-Export funktioniert nicht:**
```bash
# ReportLab neu installieren
pip install reportlab --upgrade
```

**Dashboard zeigt keine Diagramme:**
```bash
# Matplotlib installieren
pip install matplotlib
```

### Log-Dateien
Debug-Ausgaben finden Sie in der Konsole. Bei Problemen starten Sie die Anwendung über die Kommandozeile:
```bash
python main.py
```

## 🔐 **Datenschutz & Sicherheit**

### Lokale Datenhaltung
- Alle Daten werden lokal im `storage/` Ordner gespeichert
- Keine Cloud-Verbindung oder externe Server
- JSON-Format für Transparenz und Portabilität

### Backup-Sicherheit
- Automatische Verschlüsselung der Backup-Archive (geplant)
- Sichere Löschung alter Backups
- Integritätsprüfung bei Wiederherstellung

### DSGVO-Konformität
- Vollständige Kontrolle über Kundendaten
- Export/Import für Datenübertragbarkeit
- Sichere Löschung bei Deinstallation

## 📈 **Roadmap & Geplante Features**

### Version 2.1 (Q1 2025)
- [ ] Datenbankanbindung (SQLite/PostgreSQL)
- [ ] Multi-Mandanten-Fähigkeit
- [ ] E-Mail-Integration für Rechnungsversand
- [ ] Mahnsystem mit automatischen Erinnerungen

### Version 2.2 (Q2 2025)
- [ ] Web-Interface für mobile Zugriffe
- [ ] REST-API für Drittanbieter-Integration
- [ ] Erweiterte Berichtsfunktionen
- [ ] Buchhaltungs-Export (DATEV, CSV)

### Version 2.3 (Q3 2025)
- [ ] Lagerverwaltung und Produktkatalog
- [ ] Angebots-Nachverfolgung
- [ ] Kundenkommunikation-Historie
- [ ] Mobile Apps (Android/iOS)

## 🤝 **Beitragen & Support**

### Entwicklung
Beiträge sind willkommen! Für größere Änderungen erstellen Sie bitte zuerst ein Issue.

```bash
# Entwicklungsumgebung einrichten
git clone https://github.com/ihr-repo/rechnungs-tool.git
cd rechnungs-tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Entwicklungstools
```

### Support
- 📧 E-Mail: support@rechnungs-tool.de
- 💬 GitHub Issues für Bug-Reports
- 📖 Wiki für Dokumentation

## 📄 **Lizenz**

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

---

**Entwickelt mit ❤️ für deutsche Unternehmen**

*Ein modernes, sicheres und benutzerfreundliches Tool für die tägliche Büroarbeit.*
