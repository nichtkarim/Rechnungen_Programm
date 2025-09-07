"""
Dashboard-Window mit Übersichten und Statistiken
"""
import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
import seaborn as sns
from decimal import Decimal
import threading
import time

from src.utils.data_manager import DataManager
from src.utils.pdf_preview import DocumentAnalyzer
from src.utils.theme_manager import theme_manager

# Matplotlib Style konfigurieren
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class DashboardWindow:
    """Dashboard mit Übersichten und Statistiken"""
    
    def __init__(self, parent, data_manager: DataManager):
        self.parent = parent
        self.data_manager = data_manager
        self.analyzer = DocumentAnalyzer()
        self.auto_refresh = True
        self.refresh_interval = 5  # Sekunden
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("📊 Dashboard & Live-Statistiken")
        self.window.geometry("1400x900")
        self.window.transient(parent)
        
        # Theme anwenden
        theme_manager.setup_window_theme(self.window)
        
        # Event für Window Close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Layout erstellen
        self.create_layout()
        self.refresh_data()
        
        # Auto-Refresh starten
        self.start_auto_refresh()
    
    def on_closing(self):
        """Wird beim Schließen des Fensters aufgerufen"""
        self.auto_refresh = False
        self.window.destroy()
    
    def create_layout(self):
        """Erstellt das Dashboard-Layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(main_frame, text="📊 Dashboard & Statistiken", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Übersicht Tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Übersicht")
        self.create_overview_tab()
        
        # Finanzen Tab
        self.financial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.financial_frame, text="Finanzen")
        self.create_financial_tab()
        
        # Kunden Tab
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="Kunden")
        self.create_customers_tab()
        
        # Trends Tab
        self.trends_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trends_frame, text="📈 Live-Trends")
        self.create_trends_tab()
        
        # Analytics Tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📊 Erweiterte Analyse")
        self.create_analytics_tab()
        
        # Vergleich Tab
        self.comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_frame, text="📈 Vergleiche")
        self.create_comparison_tab()
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Auto-Refresh Toggle
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        auto_refresh_cb = ctk.CTkCheckBox(button_frame, text="🔄 Auto-Refresh", 
                                        variable=self.auto_refresh_var,
                                        command=self.toggle_auto_refresh)
        auto_refresh_cb.pack(side="left", padx=5)
        
        # Refresh Interval
        interval_label = ctk.CTkLabel(button_frame, text="Intervall:")
        interval_label.pack(side="left", padx=(20, 5))
        
        self.interval_var = ctk.StringVar(value="5")
        interval_entry = ctk.CTkEntry(button_frame, textvariable=self.interval_var, width=50)
        interval_entry.pack(side="left", padx=5)
        interval_entry.bind("<Return>", self.update_refresh_interval)
        
        seconds_label = ctk.CTkLabel(button_frame, text="Sek.")
        seconds_label.pack(side="left", padx=(0, 10))
        
        refresh_btn = ctk.CTkButton(button_frame, text="🔄 Jetzt aktualisieren", 
                                  command=self.refresh_data)
        refresh_btn.pack(side="right", padx=5)
        
        export_btn = ctk.CTkButton(button_frame, text="📊 Bericht exportieren", 
                                 command=self.export_report)
        export_btn.pack(side="right", padx=5)
        
        screenshot_btn = ctk.CTkButton(button_frame, text="📸 Screenshot", 
                                     command=self.save_screenshot)
        screenshot_btn.pack(side="right", padx=5)
    
    def create_overview_tab(self):
        """Erstellt den Übersicht-Tab"""
        # KPI Cards
        kpi_frame = ctk.CTkFrame(self.overview_frame)
        kpi_frame.pack(fill="x", padx=10, pady=10)
        
        # Grid für KPI Cards
        self.kpi_cards = {}
        kpi_data = [
            ("Kunden", "👥", "customers_count"),
            ("Rechnungen", "📄", "invoices_count"),
            ("Umsatz", "💰", "total_revenue"),
            ("Offene Posten", "⏰", "unpaid_amount")
        ]
        
        for i, (title, icon, key) in enumerate(kpi_data):
            card_data = self.create_kpi_card(kpi_frame, title, icon, "0")
            card_data['frame'].grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.kpi_cards[key] = card_data
        
        # Grid konfigurieren
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        # Status Übersicht
        status_frame = ctk.CTkFrame(self.overview_frame)
        status_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        status_label = ctk.CTkLabel(status_frame, text="📋 Status Übersicht", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        status_label.pack(pady=10)
        
        # Status Tabelle
        self.status_tree = ttk.Treeview(status_frame, columns=("wert",), show="tree headings")
        self.status_tree.heading("#0", text="Kategorie")
        self.status_tree.heading("wert", text="Wert")
        self.status_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_financial_tab(self):
        """Erstellt den Finanzen-Tab"""
        # Umsatz nach Steuer
        tax_frame = ctk.CTkFrame(self.financial_frame)
        tax_frame.pack(fill="x", padx=10, pady=10)
        
        tax_label = ctk.CTkLabel(tax_frame, text="💰 Umsatz nach Steuersätzen", 
                               font=ctk.CTkFont(size=16, weight="bold"))
        tax_label.pack(pady=10)
        
        self.tax_tree = ttk.Treeview(tax_frame, columns=("betrag", "anteil"), show="headings")
        self.tax_tree.heading("betrag", text="Betrag")
        self.tax_tree.heading("anteil", text="Anteil")
        self.tax_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Zahlungsstatus
        payment_frame = ctk.CTkFrame(self.financial_frame)
        payment_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        payment_label = ctk.CTkLabel(payment_frame, text="💳 Zahlungsstatus", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        payment_label.pack(pady=10)
        
        self.payment_tree = ttk.Treeview(payment_frame, columns=("anzahl", "betrag"), show="headings")
        self.payment_tree.heading("anzahl", text="Anzahl")
        self.payment_tree.heading("betrag", text="Betrag")
        self.payment_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_customers_tab(self):
        """Erstellt den Kunden-Tab"""
        customers_label = ctk.CTkLabel(self.customers_frame, text="👥 Top Kunden", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        customers_label.pack(pady=10)
        
        # Top Kunden Tabelle
        self.customers_tree = ttk.Treeview(self.customers_frame, 
                                         columns=("umsatz", "rechnungen"), show="headings")
        self.customers_tree.heading("#0", text="Kunde")
        self.customers_tree.heading("umsatz", text="Umsatz")
        self.customers_tree.heading("rechnungen", text="Rechnungen")
        self.customers_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_trends_tab(self):
        """Erstellt den Trends-Tab mit erweiterten Grafiken"""
        # Hauptcontainer
        main_container = ctk.CTkFrame(self.trends_frame)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Control Panel
        control_panel = ctk.CTkFrame(main_container)
        control_panel.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_panel, text="📈 Live-Trends & Zeitreihen", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=10)
        
        # Zeitraum-Auswahl
        self.timerange_var = ctk.StringVar(value="12M")
        timerange_menu = ctk.CTkOptionMenu(control_panel, variable=self.timerange_var,
                                         values=["3M", "6M", "12M", "24M", "Alle"],
                                         command=self.update_timerange)
        timerange_menu.pack(side="right", padx=5)
        
        ctk.CTkLabel(control_panel, text="Zeitraum:").pack(side="right", padx=5)
        
        # Matplotlib Figure mit mehreren Subplots
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Grid Layout: 2x3
        gs = self.fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Subplots erstellen
        self.ax_revenue = self.fig.add_subplot(gs[0, :])  # Umsatz über Zeit (ganze erste Reihe)
        self.ax_pie = self.fig.add_subplot(gs[1, 0])      # Dokumenttypen Pie
        self.ax_bar = self.fig.add_subplot(gs[1, 1])      # Top Kunden Bar
        self.ax_heatmap = self.fig.add_subplot(gs[2, 0])  # Monatliche Heatmap
        self.ax_scatter = self.fig.add_subplot(gs[2, 1])  # Scatter Plot
        
        # Canvas für Matplotlib
        canvas_frame = ctk.CTkFrame(main_container)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Toolbar für Interaktivität
        from matplotlib.backends._backend_tk import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, canvas_frame)
        toolbar.update()
        
        # Style für dunkles Theme
        self.setup_matplotlib_style()
    
    def create_kpi_card(self, parent, title: str, icon: str, value: str) -> Dict[str, Any]:
        """Erstellt eine KPI-Karte und gibt Widget-Referenzen zurück"""
        card = ctk.CTkFrame(parent)
        
        # Icon
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24))
        icon_label.pack(pady=(10, 5))
        
        # Wert
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        value_label.pack()
        
        # Titel
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12))
        title_label.pack(pady=(5, 10))
        
        # Referenzen als Dictionary zurückgeben
        return {
            'frame': card,
            'value_label': value_label,
            'icon_label': icon_label,
            'title_label': title_label
        }
    
    def get_empty_analysis(self) -> Dict[str, Any]:
        """Gibt eine leere Analyse-Struktur zurück"""
        return {
            "summary": {
                "total_count": 0,
                "by_type": {},
                "by_status": {},
                "date_range": {"from": None, "to": None}
            },
            "financial": {
                "total_revenue": 0.0,
                "average_invoice_amount": 0.0,
                "largest_invoice": 0.0,
                "smallest_invoice": 0.0,
                "unpaid_amount": 0.0,
                "by_tax_rate": {}
            },
            "customers": {
                "top_customers": [],
                "customer_count": 0
            },
            "trends": {
                "monthly_revenue": {},
                "payment_behavior": {}
            }
        }
    
    def refresh_data(self):
        """Aktualisiert alle Dashboard-Daten"""
        try:
            # Daten analysieren
            invoices = self.data_manager.get_invoices() or []
            customers = self.data_manager.get_customers() or []
            analysis = self.analyzer.analyze_invoices(invoices)
            
            # Sicherstellen, dass analysis nicht None ist
            if not analysis:
                print("⚠️ Analyse-Ergebnis ist None - verwende Standard-Werte")
                analysis = self.get_empty_analysis()
            
            # KPI Cards aktualisieren
            self.update_kpi_cards(analysis, customers)
            
            # Status Übersicht
            self.update_status_overview(analysis)
            
            # Finanz-Tabs
            self.update_financial_data(analysis)
            
            # Kunden-Tab
            self.update_customers_data(analysis)
            
            # Trends-Tab
            self.update_trends_data(analysis)
            
            # Analytics-Tab
            self.update_analytics_data(analysis)
            
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren des Dashboards: {e}")
            import traceback
            traceback.print_exc()
    
    def update_kpi_cards(self, analysis: Dict[str, Any], customers: list):
        """Aktualisiert die KPI-Karten"""
        try:
            # Kunden
            self.kpi_cards["customers_count"]['value_label'].configure(text=str(len(customers or [])))
            
            # Rechnungen
            total_count = analysis.get("summary", {}).get("total_count", 0)
            self.kpi_cards["invoices_count"]['value_label'].configure(text=str(total_count))
            
            # Umsatz
            revenue = analysis.get("financial", {}).get("total_revenue", 0)
            self.kpi_cards["total_revenue"]['value_label'].configure(text=f"{revenue:,.2f} €")
            
            # Offene Posten
            unpaid = analysis.get("financial", {}).get("unpaid_amount", 0)
            self.kpi_cards["unpaid_amount"]['value_label'].configure(text=f"{unpaid:,.2f} €")
            
            # Animationseffekt für KPI-Updates
            self.animate_kpi_cards()
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der KPI-Karten: {e}")
    
    def update_status_overview(self, analysis: Dict[str, Any]):
        """Aktualisiert die Status-Übersicht"""
        try:
            # Tabelle leeren
            for item in self.status_tree.get_children():
                self.status_tree.delete(item)
            
            # Dokumenttypen
            doc_types = analysis.get("summary", {}).get("by_type", {})
            if doc_types:
                doc_types_parent = self.status_tree.insert("", "end", text="📄 Dokumenttypen", values=("",))
                for doc_type, count in doc_types.items():
                    self.status_tree.insert(doc_types_parent, "end", text=f"  {doc_type}", values=(str(count),))
            
            # Status
            by_status = analysis.get("summary", {}).get("by_status", {})
            if by_status:
                status_parent = self.status_tree.insert("", "end", text="📊 Status", values=("",))
                for status, count in by_status.items():
                    self.status_tree.insert(status_parent, "end", text=f"  {status}", values=(str(count),))
            
            # Zeitraum
            date_range = analysis.get("summary", {}).get("date_range", {})
            if date_range and date_range.get("from"):
                date_range_text = f"{date_range['from']} - {date_range['to']}"
                self.status_tree.insert("", "end", text="📅 Zeitraum", values=(date_range_text,))
            
            # Expandieren
            for item in self.status_tree.get_children():
                self.status_tree.item(item, open=True)
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Status-Übersicht: {e}")
    
    def update_financial_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die Finanz-Daten"""
        try:
            # Steuer-Tabelle
            for item in self.tax_tree.get_children():
                self.tax_tree.delete(item)
            
            by_tax_rate = analysis.get("financial", {}).get("by_tax_rate", {})
            total_tax = sum(by_tax_rate.values()) if by_tax_rate else 0
            
            for rate, amount in by_tax_rate.items():
                percentage = (amount / total_tax * 100) if total_tax > 0 else 0
                self.tax_tree.insert("", "end", values=(f"{amount:,.2f} €", f"{percentage:.1f}%"))
            
            # Zahlungsstatus
            for item in self.payment_tree.get_children():
                self.payment_tree.delete(item)
            
            by_status = analysis.get("summary", {}).get("by_status", {})
            financial = analysis.get("financial", {})
            
            paid_count = by_status.get("Bezahlt", 0)
            unpaid_count = by_status.get("Offen", 0)
            total_revenue = financial.get("total_revenue", 0)
            unpaid_amount = financial.get("unpaid_amount", 0)
            
            self.payment_tree.insert("", "end", text="Bezahlt", values=(
                str(paid_count), 
                f"{total_revenue - unpaid_amount:,.2f} €"
            ))
            self.payment_tree.insert("", "end", text="Offen", values=(
                str(unpaid_count), 
                f"{unpaid_amount:,.2f} €"
            ))
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Finanz-Daten: {e}")
    
    def update_customers_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die Kunden-Daten"""
        try:
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            
            top_customers = analysis.get("customers", {}).get("top_customers", [])
            
            for customer_name, revenue in top_customers:
                # Anzahl Rechnungen für diesen Kunden ermitteln
                customer_invoices = [inv for inv in (self.data_manager.get_invoices() or [])
                                   if inv.customer and inv.customer.get_display_name() == customer_name]
                
                self.customers_tree.insert("", "end", text=customer_name, values=(
                    f"{revenue:,.2f} €",
                    str(len(customer_invoices))
                ))
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Kunden-Daten: {e}")
    
    def update_trends_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die erweiterten Trends-Diagramme"""
        try:
            # Alle Subplots leeren
            for ax in [self.ax_revenue, self.ax_pie, self.ax_bar, self.ax_heatmap, self.ax_scatter]:
                ax.clear()
            
            # 1. Umsatz-Zeitreihe (Hauptdiagramm)
            self.create_revenue_timeline(analysis)
            
            # 2. Dokumenttypen Pie Chart
            self.create_document_types_pie(analysis)
            
            # 3. Top Kunden Bar Chart
            self.create_top_customers_bar(analysis)
            
            # 4. Monatliche Heatmap
            self.create_monthly_heatmap(analysis)
            
            # 5. Revenue vs. Customer Scatter
            self.create_revenue_scatter(analysis)
            
            # Styling anwenden
            self.apply_chart_styling()
            
            # Canvas aktualisieren
            self.canvas.draw()
            
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Trends: {e}")
            import traceback
            traceback.print_exc()
    
    def update_analytics_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die erweiterten Analytics-Daten"""
        try:
            # Tabelle leeren
            for item in self.analytics_tree.get_children():
                self.analytics_tree.delete(item)
            
            financial = analysis.get("financial", {})
            summary = analysis.get("summary", {})
            customers = analysis.get("customers", {})
            trends = analysis.get("trends", {})
            
            # Erweiterte Kennzahlen
            stats_data = [
                ("📊 Finanzielle Kennzahlen", "", ""),
                ("  Durchschnittlicher Rechnungsbetrag", f"{financial.get('average_invoice_amount', 0):,.2f} €", "📈"),
                ("  Höchste Rechnung", f"{financial.get('largest_invoice', 0):,.2f} €", "🔝"),
                ("  Niedrigste Rechnung", f"{financial.get('smallest_invoice', 0):,.2f} €", "🔻"),
            ]
            
            # Zahlungsquote berechnen
            total_revenue = financial.get('total_revenue', 0)
            unpaid_amount = financial.get('unpaid_amount', 0)
            payment_rate = ((total_revenue - unpaid_amount) / total_revenue * 100) if total_revenue > 0 else 0
            stats_data.append(("  Zahlungsquote", f"{payment_rate:.1f}%", "💳"))
            
            stats_data.extend([
                ("📈 Wachstum & Trends", "", ""),
                ("  Kunden mit Umsatz", f"{len(customers.get('top_customers', []))}", "👥"),
                ("  Dokumenttypen", f"{len(summary.get('by_type', {}))}", "📄"),
                ("  Aktive Monate", f"{len(trends.get('monthly_revenue', {}))}", "📅"),
                
                ("💰 Steuern & Compliance", "", ""),
            ])
            
            # Steueraufschlüsselung
            by_tax_rate = financial.get("by_tax_rate", {})
            for rate, amount in by_tax_rate.items():
                if amount > 0:
                    stats_data.append(("  " + f"Umsatz {rate} MwSt", f"{amount:,.2f} €", "🧾"))
            
            # Daten in TreeView einfügen
            for label, value, trend in stats_data:
                if label.startswith("📊") or label.startswith("📈") or label.startswith("💰"):
                    # Kategorie-Header
                    parent = self.analytics_tree.insert("", "end", text=label, values=("", ""))
                else:
                    # Normale Zeile
                    self.analytics_tree.insert("", "end", text=label, values=(value, trend))
            
            # Alle Kategorien expandieren
            for item in self.analytics_tree.get_children():
                self.analytics_tree.item(item, open=True)
                
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Analytics: {e}")
            import traceback
            traceback.print_exc()
    
    def create_financial_report(self, analysis: Dict[str, Any]):
        """Erstellt einen detaillierten Finanzbericht als Text"""
        report = []
        report.append("=" * 60)
        report.append("FINANZBERICHT")
        report.append("=" * 60)
        report.append(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        report.append("")
        
        # Umsatz nach Steuersätzen
        report.append("UMSATZ NACH STEUERSÄTZEN")
        report.append("-" * 30)
        total_revenue = 0
        for rate, amount in analysis["financial"]["by_tax_rate"].items():
            report.append(f"{rate}: {amount:,.2f} €")
            total_revenue += amount
        
        report.append(f"Gesamtumsatz: {total_revenue:,.2f} €")
        report.append("")
        
        # Zahlungsstatus
        report.append("ZAHLUNGSSTATUS")
        report.append("-" * 30)
        paid_count = analysis["summary"]["by_status"].get("Bezahlt", 0)
        unpaid_count = analysis["summary"]["by_status"].get("Offen", 0)
        
        report.append(f"Bezahlt: {paid_count} ({analysis['financial']['total_revenue'] - analysis['financial']['unpaid_amount']:,.2f} €)")
        report.append(f"Offen: {unpaid_count} ({analysis['financial']['unpaid_amount']:,.2f} €)")
        
        return "\n".join(report)
    
    def export_report(self):
        """Exportiert Dashboard-Bericht"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Dashboard-Bericht speichern",
                defaultextension=".txt",
                filetypes=[("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")]
            )
            
            if filename:
                # Daten sammeln
                invoices = self.data_manager.get_invoices()
                customers = self.data_manager.get_customers()
                analysis = self.analyzer.analyze_invoices(invoices)
                
                # Bericht erstellen
                report = self.generate_text_report(analysis, customers)
                
                # Speichern
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                print(f"✅ Dashboard-Bericht gespeichert: {filename}")
                
        except Exception as e:
            print(f"❌ Fehler beim Exportieren: {e}")
    
    def generate_text_report(self, analysis: Dict[str, Any], customers: list) -> str:
        """Generiert Textbericht"""
        report = []
        report.append("=" * 60)
        report.append("DASHBOARD BERICHT")
        report.append("=" * 60)
        report.append(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        report.append("")
        
        # Übersicht
        report.append("ÜBERSICHT")
        report.append("-" * 30)
        report.append(f"Anzahl Kunden: {len(customers)}")
        report.append(f"Anzahl Dokumente: {analysis['summary']['total_count']}")
        report.append(f"Gesamtumsatz: {analysis['financial']['total_revenue']:,.2f} €")
        report.append(f"Offene Posten: {analysis['financial']['unpaid_amount']:,.2f} €")
        report.append("")
        
        # Dokumenttypen
        report.append("DOKUMENTTYPEN")
        report.append("-" * 30)
        for doc_type, count in analysis["summary"]["by_type"].items():
            report.append(f"{doc_type}: {count}")
        report.append("")
        
        # Top Kunden
        report.append("TOP KUNDEN")
        report.append("-" * 30)
        for i, (customer, revenue) in enumerate(analysis["customers"]["top_customers"][:10], 1):
            report.append(f"{i:2d}. {customer}: {revenue:,.2f} €")
        report.append("")
        
        # Steuersätze
        report.append("UMSATZ NACH STEUERSÄTZEN")
        report.append("-" * 30)
        for rate, amount in analysis["financial"]["by_tax_rate"].items():
            report.append(f"{rate}: {amount:,.2f} €")
        
        return "\n".join(report)
    
    def start_auto_refresh(self):
        """Startet den automatischen Refresh in einem separaten Thread"""
        def refresh_loop():
            while self.auto_refresh:
                try:
                    if hasattr(self, 'window') and self.window.winfo_exists():
                        self.window.after(0, self.refresh_data)
                        time.sleep(self.refresh_interval)
                    else:
                        break
                except Exception as e:
                    print(f"❌ Auto-Refresh Fehler: {e}")
                    break
        
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
    
    def toggle_auto_refresh(self):
        """Schaltet Auto-Refresh ein/aus"""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
    
    def update_refresh_interval(self, event=None):
        """Aktualisiert das Refresh-Intervall"""
        try:
            new_interval = float(self.interval_var.get())
            if new_interval > 0:
                self.refresh_interval = new_interval
        except ValueError:
            self.interval_var.set(str(self.refresh_interval))
    
    def save_screenshot(self):
        """Speichert Screenshot des Dashboards"""
        try:
            from tkinter import filedialog
            import tkinter as tk
            
            filename = filedialog.asksaveasfilename(
                title="Dashboard Screenshot speichern",
                defaultextension=".png",
                filetypes=[("PNG-Dateien", "*.png"), ("Alle Dateien", "*")]
            )
            
            if filename:
                # Widget als PostScript speichern und konvertieren
                self.window.update()
                x = self.window.winfo_rootx()
                y = self.window.winfo_rooty()
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                
                # Screenshot mit PIL
                try:
                    from PIL import ImageGrab
                    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                    screenshot.save(filename)
                    print(f"✅ Screenshot gespeichert: {filename}")
                except ImportError:
                    print("⚠️ PIL nicht verfügbar - verwende Matplotlib für Screenshot")
                    self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"✅ Chart-Screenshot gespeichert: {filename}")
                    
        except Exception as e:
            print(f"❌ Fehler beim Screenshot: {e}")
    
    def setup_matplotlib_style(self):
        """Konfiguriert Matplotlib für dunkles Theme"""
        import warnings
        # Font-Warnungen für Emojis unterdrücken
        warnings.filterwarnings("ignore", message=".*Glyph.*missing from font.*")
        
        plt.rcParams.update({
            'figure.facecolor': '#2b2b2b',
            'axes.facecolor': '#1e1e1e',
            'axes.edgecolor': '#ffffff',
            'axes.labelcolor': '#ffffff',
            'text.color': '#ffffff',
            'xtick.color': '#ffffff',
            'ytick.color': '#ffffff',
            'grid.color': '#444444',
            'figure.edgecolor': '#2b2b2b',
            'font.family': ['DejaVu Sans', 'Arial', 'sans-serif']
        })
    
    def update_timerange(self, value):
        """Aktualisiert den Zeitraum für Trends"""
        self.timerange_var.set(value)
        self.refresh_data()
    
    def animate_kpi_cards(self):
        """Animiert KPI-Karten bei Updates"""
        def pulse_card(card_data, pulse_count=0):
            if pulse_count < 3:  # 3x pulsieren
                if pulse_count % 2 == 0:
                    card_data['frame'].configure(fg_color=("#3B82F6", "#1E40AF"))
                else:
                    card_data['frame'].configure(fg_color=("gray75", "gray25"))
                
                self.window.after(200, lambda: pulse_card(card_data, pulse_count + 1))
        
        for card_data in self.kpi_cards.values():
            pulse_card(card_data)
    
    def create_analytics_tab(self):
        """Erstellt den erweiterten Analytics-Tab"""
        analytics_container = ctk.CTkFrame(self.analytics_frame)
        analytics_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Titel
        title_label = ctk.CTkLabel(analytics_container, text="📊 Erweiterte Datenanalyse", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)
        
        # Statistik-Grid
        stats_frame = ctk.CTkFrame(analytics_container)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Erweiterte Statistiken
        self.analytics_tree = ttk.Treeview(stats_frame, columns=("wert", "trend"), show="tree headings")
        self.analytics_tree.heading("#0", text="Kennzahl")
        self.analytics_tree.heading("wert", text="Aktueller Wert")
        self.analytics_tree.heading("trend", text="Trend")
        self.analytics_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.analytics_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.analytics_tree.configure(yscrollcommand=scrollbar.set)
    
    def create_comparison_tab(self):
        """Erstellt den Vergleichs-Tab"""
        comparison_container = ctk.CTkFrame(self.comparison_frame)
        comparison_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Titel
        title_label = ctk.CTkLabel(comparison_container, text="📈 Zeitvergleiche & Prognosen", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)
        
        # Vergleichsoptionen
        options_frame = ctk.CTkFrame(comparison_container)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.comparison_type = ctk.StringVar(value="Vorjahr")
        comparison_menu = ctk.CTkOptionMenu(options_frame, variable=self.comparison_type,
                                          values=["Vormonat", "Vorjahr", "Quartal", "YTD"],
                                          command=self.update_comparison)
        comparison_menu.pack(side="left", padx=5)
        
        # Vergleichsdiagramm
        self.comparison_fig, self.comparison_ax = plt.subplots(figsize=(12, 6))
        self.comparison_fig.patch.set_facecolor('#2b2b2b')
        
        comparison_canvas_frame = ctk.CTkFrame(comparison_container)
        comparison_canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, comparison_canvas_frame)
        self.comparison_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_comparison(self, value):
        """Aktualisiert Vergleichsdiagramm"""
        self.comparison_type.set(value)
        self.refresh_comparison_data()
    
    def refresh_comparison_data(self):
        """Aktualisiert Vergleichsdaten"""
        try:
            self.comparison_ax.clear()
            
            # Beispiel-Vergleichsdaten
            months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun']
            current_year = [1200, 1400, 1100, 1600, 1800, 1500]
            previous_year = [1000, 1300, 1050, 1400, 1650, 1200]
            
            x = np.arange(len(months))
            width = 0.35
            
            bars1 = self.comparison_ax.bar(x - width/2, current_year, width, 
                                         label='Aktuell', color='#3B82F6', alpha=0.8)
            bars2 = self.comparison_ax.bar(x + width/2, previous_year, width, 
                                         label='Vergleichszeitraum', color='#EF4444', alpha=0.8)
            
            self.comparison_ax.set_xlabel('Monate')
            self.comparison_ax.set_ylabel('Umsatz (€)')
            self.comparison_ax.set_title(f'Umsatzvergleich - {self.comparison_type.get()}')
            self.comparison_ax.set_xticks(x)
            self.comparison_ax.set_xticklabels(months)
            self.comparison_ax.legend()
            self.comparison_ax.grid(True, alpha=0.3)
            
            # Werte auf Balken anzeigen
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    self.comparison_ax.text(bar.get_x() + bar.get_width()/2., height,
                                          f'{height:,.0f}€',
                                          ha='center', va='bottom', fontsize=9)
            
            add_value_labels(bars1)
            add_value_labels(bars2)
            
            self.comparison_canvas.draw()
            
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Vergleichsdaten: {e}")
    
    def create_revenue_timeline(self, analysis: Dict[str, Any]):
        """Erstellt erweiterte Umsatz-Zeitreihe"""
        try:
            monthly_data = analysis.get("trends", {}).get("monthly_revenue", {})
            if not monthly_data:
                self.ax_revenue.text(0.5, 0.5, 'Keine Umsatzdaten verfügbar', 
                                   ha='center', va='center', transform=self.ax_revenue.transAxes,
                                   color='white', fontsize=12)
                self.ax_revenue.set_title('📈 Umsatzentwicklung über Zeit', 
                                        fontsize=14, fontweight='bold', color='white')
                return
            
            # Daten vorbereiten
            months = sorted(monthly_data.keys())
            revenues = [monthly_data[month] for month in months]
            
            # Zeitraum-Filter anwenden
            timerange = self.timerange_var.get()
            if timerange != "Alle":
                months_to_show = int(timerange.replace('M', ''))
                months = months[-months_to_show:]
                revenues = revenues[-months_to_show:]
            
            if not months:
                self.ax_revenue.text(0.5, 0.5, 'Keine Daten für gewählten Zeitraum', 
                                   ha='center', va='center', transform=self.ax_revenue.transAxes,
                                   color='white', fontsize=12)
                self.ax_revenue.set_title('📈 Umsatzentwicklung über Zeit', 
                                        fontsize=14, fontweight='bold', color='white')
                return
            
            # Hauptlinie
            self.ax_revenue.plot(range(len(months)), revenues, marker='o', linewidth=3, markersize=8, 
                               color='#3B82F6', label='Umsatz', alpha=0.9)
            
            # Trend-Linie
            if len(revenues) > 2:
                z = np.polyfit(range(len(revenues)), revenues, 1)
                p = np.poly1d(z)
                trend_color = '#10B981' if z[0] > 0 else '#EF4444'
                self.ax_revenue.plot(range(len(revenues)), p(range(len(revenues))), "--", 
                                   color=trend_color, alpha=0.7, label='Trend')
            
            # Füllung unter der Kurve
            self.ax_revenue.fill_between(range(len(months)), revenues, alpha=0.2, color='#3B82F6')
            
            # Styling
            self.ax_revenue.set_title('📈 Umsatzentwicklung über Zeit', 
                                    fontsize=14, fontweight='bold', color='white')
            self.ax_revenue.set_ylabel('Umsatz (€)', color='white')
            self.ax_revenue.set_xticks(range(len(months)))
            self.ax_revenue.set_xticklabels([m.split('-')[1] + '/' + m.split('-')[0][-2:] for m in months], rotation=45)
            self.ax_revenue.grid(True, alpha=0.3)
            self.ax_revenue.legend()
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Umsatz-Zeitreihe: {e}")
            self.ax_revenue.text(0.5, 0.5, 'Fehler beim Laden der Daten', 
                               ha='center', va='center', transform=self.ax_revenue.transAxes,
                               color='white', fontsize=12)
    
    def create_document_types_pie(self, analysis: Dict[str, Any]):
        """Erstellt verbessertes Dokumenttypen-Diagramm"""
        try:
            doc_types = analysis.get("summary", {}).get("by_type", {})
            if not doc_types:
                self.ax_pie.text(0.5, 0.5, 'Keine Dokumente vorhanden', 
                               ha='center', va='center', color='white', fontsize=12)
                self.ax_pie.set_title('📄 Dokumenttypen-Verteilung', 
                                     fontsize=12, fontweight='bold', color='white')
                return
            
            labels = list(doc_types.keys())
            sizes = list(doc_types.values())
            
            # Farben definieren
            colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
            
            # Pie Chart mit Explosion
            explode = [0.1 if i == 0 else 0 for i in range(len(sizes))]
            
            pie_result = self.ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                       startangle=90, colors=colors[:len(sizes)],
                                       explode=explode, shadow=True)
            
            # Text-Styling
            if len(pie_result) >= 3:
                wedges, texts, autotexts = pie_result
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            self.ax_pie.set_title('📄 Dokumenttypen-Verteilung', 
                                 fontsize=12, fontweight='bold', color='white')
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Dokumenttypen-Diagramms: {e}")
            self.ax_pie.text(0.5, 0.5, 'Fehler beim Laden der Dokumenttypen', 
                           ha='center', va='center', color='white', fontsize=12)
    
    def create_top_customers_bar(self, analysis: Dict[str, Any]):
        """Erstellt Top-Kunden Balkendiagramm"""
        try:
            top_customers = analysis.get("customers", {}).get("top_customers", [])[:5]
            if not top_customers:
                self.ax_bar.text(0.5, 0.5, 'Keine Kundendaten vorhanden', 
                               ha='center', va='center', color='white', fontsize=12)
                self.ax_bar.set_title('👥 Top 5 Kunden', 
                                     fontsize=12, fontweight='bold', color='white')
                return
            
            customers = [customer[0][:15] + '...' if len(customer[0]) > 15 else customer[0] 
                        for customer in top_customers]
            revenues = [customer[1] for customer in top_customers]
            
            # Horizontales Balkendiagramm
            bars = self.ax_bar.barh(customers, revenues, color='#10B981', alpha=0.8)
            
            # Werte auf Balken
            for i, (bar, revenue) in enumerate(zip(bars, revenues)):
                width = bar.get_width()
                self.ax_bar.text(width, bar.get_y() + bar.get_height()/2, 
                               f'{revenue:,.0f}€', ha='left', va='center', 
                               fontweight='bold', color='white')
            
            self.ax_bar.set_title('👥 Top 5 Kunden', fontsize=12, fontweight='bold', color='white')
            self.ax_bar.set_xlabel('Umsatz (€)', color='white')
            self.ax_bar.grid(True, alpha=0.3, axis='x')
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Kunden-Balkendiagramms: {e}")
            self.ax_bar.text(0.5, 0.5, 'Fehler beim Laden der Kundendaten', 
                           ha='center', va='center', color='white', fontsize=12)
    
    def create_monthly_heatmap(self, analysis: Dict[str, Any]):
        """Erstellt monatliche Aktivitäts-Heatmap"""
        try:
            # Beispiel-Daten für Heatmap
            months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
            weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            
            # Zufällige Daten für Demo
            data = np.random.randint(0, 10, size=(len(weekdays), len(months)))
            
            # Heatmap erstellen
            im = self.ax_heatmap.imshow(data, cmap='Blues', aspect='auto')
            
            # Achsen beschriften
            self.ax_heatmap.set_xticks(range(len(months)))
            self.ax_heatmap.set_xticklabels(months)
            self.ax_heatmap.set_yticks(range(len(weekdays)))
            self.ax_heatmap.set_yticklabels(weekdays)
            
            # Werte in Zellen anzeigen
            for i in range(len(weekdays)):
                for j in range(len(months)):
                    text = self.ax_heatmap.text(j, i, data[i, j], ha="center", va="center")
            
            self.ax_heatmap.set_title('🗓️ Aktivitäts-Heatmap', 
                                    fontsize=12, fontweight='bold', color='white')
            
        except Exception as e:
            print(f"❌ Heatmap Fehler: {e}")
            self.ax_heatmap.text(0.5, 0.5, 'Heatmap nicht verfügbar', 
                               ha='center', va='center')
    
    def create_revenue_scatter(self, analysis: Dict[str, Any]):
        """Erstellt Scatter Plot für Umsatz vs. Anzahl Rechnungen"""
        try:
            # Daten nach Kunden aggregieren
            invoices = self.data_manager.get_invoices()
            customer_data = {}
            
            for invoice in invoices:
                if invoice.customer:
                    name = invoice.customer.get_display_name()
                    if name not in customer_data:
                        customer_data[name] = {'count': 0, 'revenue': 0}
                    customer_data[name]['count'] += 1
                    customer_data[name]['revenue'] += float(invoice.calculate_total_gross())
            
            if not customer_data:
                self.ax_scatter.text(0.5, 0.5, 'Keine Daten', ha='center', va='center')
                return
            
            counts = [data['count'] for data in customer_data.values()]
            revenues = [data['revenue'] for data in customer_data.values()]
            
            # Scatter Plot
            scatter = self.ax_scatter.scatter(counts, revenues, 
                                            s=100, c=revenues, cmap='viridis', 
                                            alpha=0.7, edgecolors='white', linewidth=1)
            
            # Trendlinie
            if len(counts) > 1:
                z = np.polyfit(counts, revenues, 1)
                p = np.poly1d(z)
                self.ax_scatter.plot(counts, p(counts), "r--", alpha=0.8)
            
            self.ax_scatter.set_xlabel('Anzahl Rechnungen', color='white')
            self.ax_scatter.set_ylabel('Umsatz (€)', color='white')
            self.ax_scatter.set_title('💰 Umsatz vs. Rechnungsanzahl', 
                                    fontsize=12, fontweight='bold', color='white')
            self.ax_scatter.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"❌ Scatter Plot Fehler: {e}")
            self.ax_scatter.text(0.5, 0.5, 'Scatter Plot nicht verfügbar', 
                               ha='center', va='center')
    
    def apply_chart_styling(self):
        """Wendet einheitliches Styling auf alle Charts an"""
        for ax in [self.ax_revenue, self.ax_pie, self.ax_bar, self.ax_heatmap, self.ax_scatter]:
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        self.fig.patch.set_facecolor('#2b2b2b')
