"""
Hauptstartdatei für das Rechnungs-Tool
"""
import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

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
