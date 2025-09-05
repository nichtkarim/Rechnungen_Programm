# Rechnungs-Tool

Ein modernes Python-Tool zur Erstellung, Verwaltung und PDF-Export von Rechnungen mit professioneller GUI.

## Features

### 🏢 Stammdaten-Verwaltung
- Umfassende Firmendaten (Name, Adresse, Kontakt)
- Steuernummer und USt-IdNr.
- Bankverbindung (IBAN/BIC)
- Logo-Integration
- Kleinunternehmer-Regelung (§19 UStG)

### 👥 Kundenverwaltung
- Vollständige Kundendaten
- Separate Rechnungs- und Lieferadressen
- Automatische Kundennummern-Vergabe
- Suchfunktion

### 📄 Dokument-Erstellung
- **Dokumenttypen**: Angebot, Rechnung, Gutschrift, Storno
- Fortlaufende Nummernkreise (konfigurierbar)
- Automatische Datums-Verwaltung
- Flexible Positionsverwaltung
- Mehrere Steuersätze (0%, 7%, 19%)
- Rabatte und Mengenkalkulationen
- Reverse-Charge-Verfahren

### 💰 Korrekte Berechnungen
- Präzise Decimal-Arithmetik
- Korrekte Rundung (2 Nachkommastellen)
- Mehrfach-Steuersätze pro Dokument
- Automatische Summenbildung
- Netto/Brutto-Berechnungen

### 📋 PDF-Export
- Professionelles DIN A4 Layout
- Corporate Identity-Farben
- Logo-Integration
- Tabellenlayout für Positionen
- Vollständige Steueraufschlüsselung
- Compliance mit deutschen Rechnungsvorschriften

### 🎨 Moderne GUI
- CustomTkinter für moderne Optik
- Hell/Dunkel-Modus
- Intuitive Bedienung
- Übersichtliche Dokumentenliste
- Such- und Filterfunktionen
- Tabbed Interface

### 💾 Datenhaltung
- JSON-basierte Speicherung im `storage/` Ordner
- Offline-fähig (keine Cloud-Abhängigkeit)
- Automatisches Speichern aller Änderungen
- Separate Dateien für verschiedene Datentypen:
  - `storage/company.json` - Firmendaten
  - `storage/customers.json` - Kundendaten  
  - `storage/invoices.json` - Rechnungen/Dokumente
  - `storage/settings.json` - Anwendungseinstellungen
- Import/Export-Funktionen
- Automatisches Backup

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- Windows, macOS oder Linux

### Setup
1. Repository klonen oder ZIP herunterladen
2. Virtuelle Umgebung erstellen (empfohlen):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux  
   source .venv/bin/activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

### Abhängigkeiten
- `customtkinter>=5.2.0` - Moderne GUI-Komponenten
- `reportlab>=4.0.0` - PDF-Generierung
- `Pillow>=10.0.0` - Bildverarbeitung für Logos
- `tkcalendar>=1.6.0` - Datums-Auswahl

## Verwendung

### Erste Schritte
1. Anwendung starten:
   ```bash
   python main.py
   ```
2. Firmendaten einrichten (Einstellungen > Firma)
3. Ersten Kunden anlegen
4. Erste Rechnung erstellen

### Dokumenten-Workflow
1. **Angebot erstellen** → Kunde auswählen → Positionen hinzufügen → PDF exportieren
2. **Angebot zu Rechnung** → Angebotsnummer in Rechnung referenzieren
3. **Gutschrift erstellen** → Referenz-Rechnung angeben
4. **Status verwalten** → Rechnung als bezahlt markieren

### Nummernkreise
- Automatische Vergabe nach konfigurierbaren Formaten
- Standard: `R2024-0001`, `A2024-0001`, `G2024-0001`
- Anpassbar in den Einstellungen
- Jahresweise Zählung möglich

### PDF-Export
- Professionelles Layout nach deutschen Standards
- Automatische Steueraufschlüsselung
- Kleinunternehmer-Hinweise
- Reverse-Charge-Texte
- Corporate Design-Integration

## Projektstruktur

```
Rechnungen/
├── main.py                 # Hauptstart-Datei
├── requirements.txt        # Python-Abhängigkeiten
├── storage/                # JSON-Datenspeicher (automatisch erstellt)
│   ├── company.json       # Firmendaten
│   ├── customers.json     # Kundendaten
│   ├── invoices.json      # Rechnungen/Dokumente
│   └── settings.json      # Anwendungseinstellungen
└── src/
    ├── models/            # Datenmodelle
    │   └── __init__.py    # Alle Datenklassen
    ├── utils/             # Hilfsfunktionen
    │   ├── data_manager.py    # Datenverwaltung
    │   └── pdf_generator.py   # PDF-Export
    └── gui/               # Benutzeroberfläche
        ├── main_window.py         # Hauptfenster
        ├── invoice_edit_window.py # Rechnungsbearbeitung
        ├── customer_edit_window.py# Kundenbearbeitung
        ├── company_settings_window.py # Firmeneinstellungen
        └── app_settings_window.py    # App-Einstellungen
```

## Rechtliche Hinweise

### Compliance
- ✅ Alle Pflichtangaben nach UStG
- ✅ Korrekte Steuerberechnung
- ✅ Kleinunternehmer-Regelung (§19 UStG)
- ✅ Reverse-Charge-Verfahren
- ✅ Fortlaufende Rechnungsnummern
- ✅ Aufbewahrung in unveränderlicher Form (JSON)

### Haftungsausschluss
Dieses Tool dient der Unterstützung bei der Rechnungserstellung. Für die rechtliche und steuerliche Korrektheit der erstellten Dokumente ist der Anwender selbst verantwortlich. Es wird empfohlen, die Konfiguration mit einem Steuerberater abzustimmen.

## Entwicklung

### Architektur
- **MVC-Pattern**: Klare Trennung von Datenmodell, Logik und GUI
- **Modularer Aufbau**: Unabhängige Komponenten
- **Type Hints**: Vollständige Typisierung für bessere Wartbarkeit
- **Decimal-Arithmetik**: Präzise Geldberechnungen
- **JSON-Persistierung**: Einfache, lesbare Datenhaltung

### Erweiterungen
Das System ist für Erweiterungen konzipiert:
- Neue Dokumenttypen
- Zusätzliche Steuerarten
- Weitere Export-Formate
- Datenbankanbindung
- Multi-Mandanten-Fähigkeit

## Support

Bei Fragen oder Problemen:
1. README und Code-Kommentare prüfen
2. JSON-Dateien bei Problemen sichern
3. Mit Standard-Einstellungen neu starten

## Lizenz

Dieses Projekt steht unter einer freien Lizenz zur Verfügung. Details siehe LICENSE-Datei.

---

**Entwickelt mit ❤️ für deutsche Rechnungsanforderungen**
