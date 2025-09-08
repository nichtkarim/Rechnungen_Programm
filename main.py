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
# Neu: einfacher Update-Checker
from src.core.simple_update import async_check, schedule_periodic, UpdateResult

AKTUELLE_VERSION = "2.1.1"  # Bei Release erhöhen


def main():
    """Startet die Anwendung"""
    try:
        app = MainWindow()

        # Callback für Update-Ergebnisse
        def handle_update(res: UpdateResult):
            if res.status in ("none", "error"):
                return
            # Dynamisch GUI Hinweis anzeigen – Methoden später in MainWindow ergänzen
            try:
                if res.status == "optional":
                    # Erwartete Methode (muss in MainWindow implementiert werden)
                    if hasattr(app, "show_update_banner"):
                        text = f"Neue Version {res.remote_version} verfügbar"
                        if res.days_left is not None:
                            text += f" – Pflicht in {res.days_left} Tagen"
                        app.show_update_banner(text, res)
                elif res.status == "forced":
                    if hasattr(app, "show_forced_update_dialog"):
                        app.show_forced_update_dialog(
                            f"Update auf Version {res.remote_version} ist jetzt verpflichtend.", res
                        )
            except Exception as e:
                print(f"Update-Hinweis Fehler: {e}")

        # Erste Prüfung leicht verzögert
        async_check(AKTUELLE_VERSION, handle_update, delay_sec=2.5)
        # Periodisch alle 30 Minuten
        schedule_periodic(AKTUELLE_VERSION, handle_update, interval_sec=1800)

        app.run()
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {e}")
        input("Drücken Sie Enter zum Beenden...")


if __name__ == "__main__":
    main()
