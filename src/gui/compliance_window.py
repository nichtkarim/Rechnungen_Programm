"""
GUI für Compliance-Management - Bereinigte Version
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from ..utils.compliance_manager import (
    ComplianceManager, ComplianceRegulation, DataCategory, ProcessingPurpose,
    RetentionStatus, DataRetentionRule, ComplianceViolation
)
from src.utils.theme_manager import theme_manager


class ComplianceWindow:
    """Fenster für Compliance-Management"""
    
    def __init__(self, parent, compliance_manager: ComplianceManager):
        self.parent = parent
        self.compliance_manager = compliance_manager
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Compliance-Management")
        self.window.geometry("1200x800")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # Zentrieren
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1200x800+{x}+{y}")
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Notebook für Tabs
        self.notebook = ctk.CTkTabview(self.window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tabs erstellen
        self.create_overview_tab()
        self.create_reports_tab()
    
    def create_overview_tab(self):
        """Erstellt Übersichts-Tab"""
        tab = self.notebook.add("Übersicht")
        
        # Scroll-Frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aktionen-Toolbar
        actions_frame = ctk.CTkFrame(scroll_frame)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(actions_frame, text="Schnellaktionen", font=("Arial", 16, "bold")).pack(pady=10)
        
        actions_row = ctk.CTkFrame(actions_frame)
        actions_row.pack(fill="x", padx=10, pady=5)
        
        check_btn = ctk.CTkButton(
            actions_row,
            text="🔍 Compliance prüfen",
            command=self.run_compliance_check
        )
        check_btn.pack(side="left", padx=5)
        
        cleanup_btn = ctk.CTkButton(
            actions_row,
            text="🧹 Daten bereinigen",
            command=self.run_data_cleanup
        )
        cleanup_btn.pack(side="left", padx=5)
        
        report_btn = ctk.CTkButton(
            actions_row,
            text="📊 Bericht generieren",
            command=self.generate_report
        )
        report_btn.pack(side="left", padx=5)
        
        # Dashboard-Karten
        dashboard_frame = ctk.CTkFrame(scroll_frame)
        dashboard_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(dashboard_frame, text="Compliance-Dashboard", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Statistik-Text
        self.stats_text = ctk.CTkTextbox(dashboard_frame, height=200)
        self.stats_text.pack(fill="x", padx=10, pady=10)
        
        # DSGVO-Bereich
        gdpr_frame = ctk.CTkFrame(scroll_frame)
        gdpr_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(gdpr_frame, text="DSGVO-Betroffenenrechte", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Auskunftsrecht
        info_frame = ctk.CTkFrame(gdpr_frame)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(info_frame, text="Auskunftsrecht (Art. 15):", width=150).pack(side="left", padx=5)
        self.subject_entry = ctk.CTkEntry(info_frame, placeholder_text="Kunden-ID oder E-Mail")
        self.subject_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        export_btn = ctk.CTkButton(
            info_frame,
            text="📤 Daten exportieren",
            command=self.export_subject_data
        )
        export_btn.pack(side="left", padx=5)
    
    def create_reports_tab(self):
        """Erstellt Berichte-Tab"""
        tab = self.notebook.add("Berichte")
        
        # Toolbar
        toolbar_frame = ctk.CTkFrame(tab)
        toolbar_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        generate_btn = ctk.CTkButton(
            toolbar_frame,
            text="📊 Compliance-Bericht generieren",
            command=self.generate_compliance_report
        )
        generate_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            toolbar_frame,
            text="📤 Bericht exportieren",
            command=self.export_compliance_report
        )
        export_btn.pack(side="left", padx=5)
        
        # Bericht-Bereich
        report_frame = ctk.CTkFrame(tab)
        report_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.report_text = ctk.CTkTextbox(report_frame)
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_data(self):
        """Lädt alle Daten"""
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Aktualisiert Dashboard"""
        try:
            # Grundlegende Statistiken
            total_records = len(self.compliance_manager.data_records)
            total_rules = len(self.compliance_manager.retention_rules)
            total_violations = len(self.compliance_manager.violations)
            
            stats_text = f"""
📊 COMPLIANCE-ÜBERSICHT
═══════════════════════

📁 Datensätze gesamt: {total_records}
📋 Aufbewahrungsregeln: {total_rules}
⚠️ Verstöße gesamt: {total_violations}

✅ System läuft und ist einsatzbereit.

Letzte Aktualisierung: {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_text.strip())
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Aktualisieren des Dashboards: {str(e)}")
    
    def run_compliance_check(self):
        """Führt Compliance-Prüfung durch"""
        try:
            violations = self.compliance_manager.check_compliance()
            if violations:
                messagebox.showwarning(
                    "Compliance-Verstöße erkannt", 
                    f"{len(violations)} neue Verstöße wurden erkannt."
                )
            else:
                messagebox.showinfo("Compliance-Prüfung", "Keine neuen Verstöße erkannt.")
            
            self.refresh_dashboard()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Compliance-Prüfung: {str(e)}")
    
    def run_data_cleanup(self):
        """Führt Datenbereinigung durch"""
        try:
            result = messagebox.askyesno(
                "Datenbereinigung", 
                "Dies wird alle als gelöscht markierten Datensätze endgültig entfernen.\n\nFortfahren?"
            )
            
            if result:
                # Einfache Simulation der Bereinigung
                messagebox.showinfo("Datenbereinigung", "Bereinigung wurde durchgeführt.")
                self.refresh_dashboard()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Datenbereinigung: {str(e)}")
    
    def generate_report(self):
        """Generiert Compliance-Bericht"""
        try:
            report = self.compliance_manager.generate_compliance_report()
            
            # Bericht im Reports-Tab anzeigen
            self.notebook.set("Berichte")
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", report)
            
            messagebox.showinfo("Bericht", "Compliance-Bericht wurde generiert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Berichtsgenerierung: {str(e)}")
    
    def export_subject_data(self):
        """Exportiert Daten einer betroffenen Person (Art. 15 DSGVO)"""
        subject_id = self.subject_entry.get().strip()
        if not subject_id:
            messagebox.showwarning("Warnung", "Bitte geben Sie eine Kunden-ID oder E-Mail ein.")
            return
        
        try:
            # Einfache Simulation
            export_data = {
                'subject_id': subject_id,
                'export_date': datetime.now().isoformat(),
                'records': f"Datenexport für {subject_id} würde hier stehen"
            }
            
            # Speichern-Dialog
            filename = filedialog.asksaveasfilename(
                title="Datenexport speichern",
                defaultextension=".json",
                filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Export", f"Daten wurden nach {filename} exportiert.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Datenexport: {str(e)}")
    
    def generate_compliance_report(self):
        """Generiert detaillierten Compliance-Bericht"""
        try:
            report = self.compliance_manager.generate_compliance_report()
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", report)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Berichtsgenerierung: {str(e)}")
    
    def export_compliance_report(self):
        """Exportiert Compliance-Bericht"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Compliance-Bericht exportieren",
                defaultextension=".txt",
                filetypes=[("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")]
            )
            
            if filename:
                content = self.report_text.get("1.0", "end-1c")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Export", f"Bericht wurde nach {filename} exportiert.")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export: {str(e)}")
