"""
Hauptstartdatei für das Rechnungs-Tool
"""
import sys
import os
from pathlib import Path

# Absoluten Pfad zum Projektverzeichnis ermitteln
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"

# Nur hinzufügen wenn nicht bereits vorhanden
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.gui.main_window import MainWindow


def main():
    """Startet die Anwendung"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {e}")
        input("Drücken Sie Enter zum Beenden...")


if __name__ == "__main__":
    main()
