"""
Dashboard-Window mit Übersichten und Statistiken
"""
import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from datetime import datetime, timedelta
from typing import Dict, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from decimal import Decimal

from src.utils.data_manager import DataManager
from src.utils.pdf_preview import DocumentAnalyzer


class DashboardWindow:
    """Dashboard mit Übersichten und Statistiken"""
    
    def __init__(self, parent, data_manager: DataManager):
        self.parent = parent
        self.data_manager = data_manager
        self.analyzer = DocumentAnalyzer()
        
        # Fenster erstellen
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Dashboard & Statistiken")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        
        # Layout erstellen
        self.create_layout()
        self.refresh_data()
    
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
        self.notebook.add(self.trends_frame, text="Trends")
        self.create_trends_tab()
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        refresh_btn = ctk.CTkButton(button_frame, text="🔄 Aktualisieren", 
                                  command=self.refresh_data)
        refresh_btn.pack(side="right", padx=5)
        
        export_btn = ctk.CTkButton(button_frame, text="📊 Bericht exportieren", 
                                 command=self.export_report)
        export_btn.pack(side="right", padx=5)
    
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
            card = self.create_kpi_card(kpi_frame, title, icon, "0")
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.kpi_cards[key] = card
        
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
        """Erstellt den Trends-Tab"""
        # Matplotlib Figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        # Canvas für Matplotlib
        canvas_frame = ctk.CTkFrame(self.trends_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_kpi_card(self, parent, title: str, icon: str, value: str) -> ctk.CTkFrame:
        """Erstellt eine KPI-Karte"""
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
        
        # Referenzen speichern für Updates
        card.value_label = value_label
        
        return card
    
    def refresh_data(self):
        """Aktualisiert alle Dashboard-Daten"""
        try:
            # Daten analysieren
            invoices = self.data_manager.get_invoices()
            customers = self.data_manager.get_customers()
            analysis = self.analyzer.analyze_invoices(invoices)
            
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
            
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren des Dashboards: {e}")
    
    def update_kpi_cards(self, analysis: Dict[str, Any], customers: list):
        """Aktualisiert die KPI-Karten"""
        # Kunden
        self.kpi_cards["customers_count"].value_label.configure(text=str(len(customers)))
        
        # Rechnungen
        self.kpi_cards["invoices_count"].value_label.configure(text=str(analysis["summary"]["total_count"]))
        
        # Umsatz
        revenue = analysis["financial"]["total_revenue"]
        self.kpi_cards["total_revenue"].value_label.configure(text=f"{revenue:,.2f} €")
        
        # Offene Posten
        unpaid = analysis["financial"]["unpaid_amount"]
        self.kpi_cards["unpaid_amount"].value_label.configure(text=f"{unpaid:,.2f} €")
    
    def update_status_overview(self, analysis: Dict[str, Any]):
        """Aktualisiert die Status-Übersicht"""
        # Tabelle leeren
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        # Dokumenttypen
        doc_types = self.status_tree.insert("", "end", text="📄 Dokumenttypen", values=("",))
        for doc_type, count in analysis["summary"]["by_type"].items():
            self.status_tree.insert(doc_types, "end", text=f"  {doc_type}", values=(str(count),))
        
        # Status
        status_parent = self.status_tree.insert("", "end", text="📊 Status", values=("",))
        for status, count in analysis["summary"]["by_status"].items():
            self.status_tree.insert(status_parent, "end", text=f"  {status}", values=(str(count),))
        
        # Zeitraum
        if analysis["summary"]["date_range"]["from"]:
            date_range = f"{analysis['summary']['date_range']['from']} - {analysis['summary']['date_range']['to']}"
            self.status_tree.insert("", "end", text="📅 Zeitraum", values=(date_range,))
        
        # Expandieren
        for item in self.status_tree.get_children():
            self.status_tree.item(item, open=True)
    
    def update_financial_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die Finanz-Daten"""
        # Steuer-Tabelle
        for item in self.tax_tree.get_children():
            self.tax_tree.delete(item)
        
        total_tax = sum(analysis["financial"]["by_tax_rate"].values())
        for rate, amount in analysis["financial"]["by_tax_rate"].items():
            percentage = (amount / total_tax * 100) if total_tax > 0 else 0
            self.tax_tree.insert("", "end", values=(f"{amount:,.2f} €", f"{percentage:.1f}%"))
        
        # Zahlungsstatus
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        paid_count = analysis["summary"]["by_status"].get("Bezahlt", 0)
        unpaid_count = analysis["summary"]["by_status"].get("Offen", 0)
        
        self.payment_tree.insert("", "end", text="Bezahlt", values=(
            str(paid_count), 
            f"{analysis['financial']['total_revenue'] - analysis['financial']['unpaid_amount']:,.2f} €"
        ))
        self.payment_tree.insert("", "end", text="Offen", values=(
            str(unpaid_count), 
            f"{analysis['financial']['unpaid_amount']:,.2f} €"
        ))
    
    def update_customers_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die Kunden-Daten"""
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        for customer_name, revenue in analysis["customers"]["top_customers"]:
            # Anzahl Rechnungen für diesen Kunden ermitteln
            customer_invoices = [inv for inv in self.data_manager.get_invoices() 
                               if inv.customer and inv.customer.get_display_name() == customer_name]
            
            self.customers_tree.insert("", "end", text=customer_name, values=(
                f"{revenue:,.2f} €",
                str(len(customer_invoices))
            ))
    
    def update_trends_data(self, analysis: Dict[str, Any]):
        """Aktualisiert die Trends-Diagramme"""
        # Diagramme löschen
        self.ax1.clear()
        self.ax2.clear()
        
        # Monatlicher Umsatz
        monthly_data = analysis["trends"]["monthly_revenue"]
        if monthly_data:
            months = sorted(monthly_data.keys())
            revenues = [monthly_data[month] for month in months]
            
            self.ax1.plot(months, revenues, marker='o', linewidth=2, markersize=6)
            self.ax1.set_title("Monatlicher Umsatz", fontsize=14, fontweight='bold')
            self.ax1.set_ylabel("Umsatz (€)")
            self.ax1.grid(True, alpha=0.3)
            self.ax1.tick_params(axis='x', rotation=45)
        
        # Dokumenttypen (Kreisdiagramm)
        doc_types = analysis["summary"]["by_type"]
        if doc_types:
            labels = list(doc_types.keys())
            sizes = list(doc_types.values())
            
            self.ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            self.ax2.set_title("Verteilung Dokumenttypen", fontsize=14, fontweight='bold')
        
        # Canvas aktualisieren
        self.canvas.draw()
    
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
