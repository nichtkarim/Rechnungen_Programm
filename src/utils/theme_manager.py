"""
Theme-Manager für einheitliche UI-Darstellung
"""
import customtkinter as ctk
from typing import Optional
from src.utils.data_manager import DataManager


class ThemeManager:
    """Zentrale Theme-Verwaltung"""
    
    _instance: Optional['ThemeManager'] = None
    _data_manager: Optional[DataManager] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._current_theme = "dark"
            self._current_color_theme = "blue"
    
    def set_data_manager(self, data_manager: DataManager):
        """Setzt den DataManager für Theme-Einstellungen"""
        self._data_manager = data_manager
        self.load_theme_from_settings()
    
    def load_theme_from_settings(self):
        """Lädt Theme-Einstellungen aus den gespeicherten Settings"""
        if self._data_manager:
            try:
                settings = self._data_manager.get_settings()
                theme_mode = settings.theme_mode
                # System-Theme zu dark ändern für bessere Darstellung
                if theme_mode == "system":
                    theme_mode = "dark"
                self.apply_theme(theme_mode, "blue")
            except Exception as e:
                print(f"❌ Fehler beim Laden der Theme-Einstellungen: {e}")
                self.apply_theme("dark", "blue")
    
    def apply_theme(self, appearance_mode: str = "dark", color_theme: str = "blue"):
        """Wendet Theme auf die gesamte Anwendung an"""
        try:
            # CustomTkinter Theme setzen
            ctk.set_appearance_mode(appearance_mode)
            ctk.set_default_color_theme(color_theme)
            
            # Interne State aktualisieren
            self._current_theme = appearance_mode
            self._current_color_theme = color_theme
            
            print(f"✅ Theme angewendet: {appearance_mode} / {color_theme}")
            
            # Alle offenen Fenster aktualisieren
            self.refresh_all_windows()
            
        except Exception as e:
            print(f"❌ Fehler beim Anwenden des Themes: {e}")
    
    def refresh_all_windows(self):
        """Aktualisiert alle offenen Fenster mit dem neuen Theme"""
        try:
            # Diese Funktion wird von den Fenstern selbst aufgerufen
            # da wir keine direkte Referenz auf alle Fenster haben
            print("🔄 Theme-Refresh für alle Fenster ausgelöst")
                    
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren aller Fenster: {e}")
    
    def get_current_theme(self) -> str:
        """Gibt das aktuelle Theme zurück"""
        return self._current_theme
    
    def get_current_color_theme(self) -> str:
        """Gibt das aktuelle Farbtheme zurück"""
        return self._current_color_theme
    
    def setup_window_theme(self, window):
        """Wendet Theme-spezifische Einstellungen auf ein Fenster an"""
        try:
            # Umfassendes Theme anwenden
            self.apply_comprehensive_theme(window)
                    
        except Exception as e:
            print(f"❌ Fehler beim Setup des Fenster-Themes: {e}")
    
    def _configure_child_widgets(self, parent):
        """Konfiguriert Theme für alle Child-Widgets rekursiv"""
        try:
            colors = self.get_theme_colors()
            
            def configure_widget(widget):
                try:
                    widget_class = widget.__class__.__name__
                    
                    if hasattr(widget, 'configure'):
                        if 'Frame' in widget_class:
                            widget.configure(fg_color=colors['bg_color'])
                        elif 'Label' in widget_class:
                            widget.configure(text_color=colors['text_color'])
                        elif 'Entry' in widget_class:
                            widget.configure(
                                fg_color=colors['entry_bg'],
                                text_color=colors['text_color'],
                                border_color=colors['button_color']
                            )
                        elif 'Button' in widget_class:
                            widget.configure(
                                fg_color=colors['button_color'],
                                hover_color=colors['button_hover'],
                                text_color='white'
                            )
                        elif 'ComboBox' in widget_class or 'OptionMenu' in widget_class:
                            widget.configure(
                                fg_color=colors['entry_bg'],
                                text_color=colors['text_color'],
                                dropdown_fg_color=colors['bg_color'],
                                button_color=colors['button_color'],
                                button_hover_color=colors['button_hover']
                            )
                        elif 'CheckBox' in widget_class:
                            widget.configure(
                                text_color=colors['text_color'],
                                fg_color=colors['button_color'],
                                hover_color=colors['button_hover']
                            )
                        elif 'RadioButton' in widget_class:
                            widget.configure(
                                text_color=colors['text_color'],
                                fg_color=colors['button_color'],
                                hover_color=colors['button_hover']
                            )
                        elif 'Text' in widget_class:
                            widget.configure(
                                fg_color=colors['entry_bg'],
                                text_color=colors['text_color']
                            )
                        elif 'Scrollbar' in widget_class:
                            widget.configure(
                                fg_color=colors['bg_color'],
                                button_color=colors['button_color'],
                                button_hover_color=colors['button_hover']
                            )
                
                    # Rekursiv für alle Kinder
                    if hasattr(widget, 'winfo_children'):
                        for child in widget.winfo_children():
                            configure_widget(child)
                            
                except Exception as e:
                    pass  # Ignoriere Fehler bei einzelnen Widgets
            
            # Nach kurzer Verzögerung anwenden, damit alle Widgets geladen sind
            def apply_delayed():
                configure_widget(parent)
            
            if hasattr(parent, 'after'):
                parent.after(100, apply_delayed)
            else:
                apply_delayed()
                
        except Exception as e:
            print(f"❌ Fehler beim Konfigurieren der Child-Widgets: {e}")
    
    def get_theme_colors(self) -> dict:
        """Gibt Theme-spezifische Farben zurück"""
        # Wenn system-Theme aktiv ist, prüfe System-Einstellungen
        current_theme = self._current_theme
        if current_theme == "system":
            # Für jetzt nehmen wir dark als Standard für system
            current_theme = "dark"
        
        if current_theme == "dark":
            return {
                'bg_color': "#1a1a1a",
                'fg_color': "#ffffff",
                'entry_bg': "#2d2d2d",
                'button_color': "#0078d4",
                'button_hover': "#106ebe",
                'text_color': "#ffffff",
                'disabled_color': "#808080",
                'tab_color': "#2d2d2d",
                'tab_selected': "#0078d4",
                'scrollbar_color': "#404040",
                'border_color': "#404040"
            }
        else:  # light theme
            return {
                'bg_color': "#f5f5f5",
                'fg_color': "#000000", 
                'entry_bg': "#ffffff",
                'button_color': "#0078d4",
                'button_hover': "#106ebe",
                'text_color': "#000000",
                'disabled_color': "#666666",
                'tab_color': "#e1e1e1",
                'tab_selected': "#0078d4",
                'scrollbar_color': "#c8c8c8",
                'border_color': "#cccccc"
            }
    
    def apply_comprehensive_theme(self, window):
        """Wendet umfassendes Theme auf ein komplettes Fenster an"""
        try:
            colors = self.get_theme_colors()
            
            # Nur das Hauptfenster konfigurieren, den Rest lassen wir CustomTkinter machen
            if hasattr(window, 'configure'):
                window.configure(fg_color=colors['bg_color'])
            
            print(f"🎨 Theme angewendet auf Fenster: {colors['bg_color']}")
                
        except Exception as e:
            print(f"❌ Fehler beim umfassenden Theme-Setup: {e}")
    
    def configure_widget_theme(self, widget, widget_type: str = "default"):
        """Konfiguriert Theme für spezifische Widgets"""
        colors = self.get_theme_colors()
        
        try:
            if hasattr(widget, 'configure'):
                if widget_type == "frame":
                    widget.configure(fg_color=colors['bg_color'])
                elif widget_type == "label":
                    widget.configure(text_color=colors['text_color'])
                elif widget_type == "entry":
                    widget.configure(
                        fg_color=colors['entry_bg'],
                        text_color=colors['text_color'],
                        border_color=colors['button_color']
                    )
                elif widget_type == "button":
                    widget.configure(
                        fg_color=colors['button_color'],
                        hover_color=colors['button_hover'],
                        text_color=colors['fg_color']
                    )
                elif widget_type == "combobox":
                    widget.configure(
                        fg_color=colors['entry_bg'],
                        text_color=colors['text_color'],
                        dropdown_fg_color=colors['bg_color']
                    )
                    
        except Exception as e:
            print(f"❌ Fehler beim Konfigurieren des Widget-Themes: {e}")


# Globale Theme-Manager-Instanz
theme_manager = ThemeManager()
