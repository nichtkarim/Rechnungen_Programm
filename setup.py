"""
Setup-Skript für das Rechnungs-Tool
Führt alle notwendigen Installationen und Tests durch
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Führt einen Befehl aus und gibt das Ergebnis zurück"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} erfolgreich")
            return True
        else:
            print(f"❌ {description} fehlgeschlagen:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Fehler bei {description}: {e}")
        return False

def main():
    print("🚀 Rechnungs-Tool Setup")
    print("=" * 50)
    
    # Python-Version prüfen
    python_version = sys.version_info
    print(f"📋 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 oder höher ist erforderlich!")
        return False
    
    # Arbeitsverzeichnis prüfen
    current_dir = os.getcwd()
    print(f"📁 Arbeitsverzeichnis: {current_dir}")
    
    # Projektstruktur prüfen
    required_files = ['main.py', 'requirements.txt', 'src/models/__init__.py']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fehlende Dateien: {', '.join(missing_files)}")
        return False
    
    print("✅ Projektstruktur vollständig")
    
    # Virtual Environment prüfen
    venv_python = ".venv/Scripts/python.exe" if os.name == 'nt' else ".venv/bin/python"
    
    if not os.path.exists(venv_python):
        print("⚠️  Virtual Environment nicht gefunden")
        print("🔧 Erstelle Virtual Environment...")
        
        if not run_command("python -m venv .venv", "Virtual Environment erstellen"):
            return False
    
    # Abhängigkeiten installieren
    if not run_command(f"{venv_python} -m pip install --upgrade pip", "Pip aktualisieren"):
        return False
    
    if not run_command(f"{venv_python} -m pip install -r requirements.txt", "Abhängigkeiten installieren"):
        return False
    
    # Imports testen
    print("\n🧪 Teste Imports...")
    test_imports = [
        "import customtkinter",
        "import reportlab",
        "from PIL import Image",
        "from tkcalendar import DateEntry"
    ]
    
    for import_test in test_imports:
        if not run_command(f"{venv_python} -c \"{import_test}\"", f"Import Test: {import_test}"):
            return False
    
    # Projektimports testen
    test_cmd = f"{venv_python} -c \"import sys; sys.path.append('src'); from models import CompanyData; from utils.data_manager import DataManager; from gui.main_window import MainWindow; print('Alle Projektmodule verfügbar')\""
    
    if not run_command(test_cmd, "Projektmodule testen"):
        return False
    
    # Data-Ordner erstellen
    if not os.path.exists('data'):
        os.makedirs('data')
        print("✅ Data-Ordner erstellt")
    
    print("\n🎉 Setup erfolgreich abgeschlossen!")
    print("\n📋 Nächste Schritte:")
    print("1. Starten Sie das Tool mit: python main.py")
    print("2. Oder verwenden Sie VS Code Task: Ctrl+Shift+P > Tasks: Run Task > 'Rechnungs-Tool starten'")
    print("3. Konfigurieren Sie zuerst Ihre Firmendaten (Einstellungen > Firma)")
    print("4. Legen Sie Ihren ersten Kunden an")
    print("5. Erstellen Sie Ihre erste Rechnung")
    
    print("\n📚 Weitere Informationen:")
    print("- README.md für detaillierte Anweisungen")
    print("- data/ Ordner für alle Daten (JSON-Format)")
    print("- Backup: Kopieren Sie den data/ Ordner regelmäßig")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup fehlgeschlagen!")
        input("Drücken Sie Enter zum Beenden...")
        sys.exit(1)
    else:
        print("\n✅ Setup erfolgreich!")
        
        # Optional: Tool direkt starten
        start_now = input("\nMöchten Sie das Rechnungs-Tool jetzt starten? (j/n): ").lower()
        if start_now in ['j', 'ja', 'y', 'yes']:
            venv_python = ".venv/Scripts/python.exe" if os.name == 'nt' else ".venv/bin/python"
            subprocess.run([venv_python, "main.py"])
