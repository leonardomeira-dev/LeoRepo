#!/usr/bin/env python3
"""
Wealth Management System — entry point.
"""
import sys
import os

# Add parent dir so sibling imports work when run as a script
sys.path.insert(0, os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk

import database as db
from theme import (
    apply_theme,
    BG, SURFACE, SURFACE2, BORDER, ACCENT, ACCENT2,
    TEXT, TEXT_MUTED, WHITE,
)
from views.dashboard    import DashboardView
from views.assets       import AssetsView
from views.transactions import TransactionsView
from views.goals        import GoalsView
from views.reports      import ReportsView


NAV_ITEMS = [
    ("dashboard",    "Dashboard",    "📊"),
    ("assets",       "Ativos",       "💼"),
    ("transactions", "Transações",   "💸"),
    ("goals",        "Metas",        "🎯"),
    ("reports",      "Relatórios",   "📈"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        db.initialize_db()
        self._seed_demo_data()

        self.title("Wealth Manager")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=BG)
        apply_theme(self)

        self._active_page = tk.StringVar(value="dashboard")
        self._nav_buttons: dict[str, tk.Label] = {}
        self._pages: dict[str, ttk.Frame] = {}

        self._build_layout()
        self._show_page("dashboard")

    def _build_layout(self):
        # ── Sidebar ────────────────────────────────────────────────────────────
        sidebar = tk.Frame(self, bg=SURFACE2, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo / brand
        brand = tk.Frame(sidebar, bg=SURFACE2)
        brand.pack(fill="x", pady=(24, 4), padx=16)
        tk.Label(brand, text="💰", bg=SURFACE2, fg=ACCENT,
                 font=("Segoe UI", 28)).pack(side="left")
        brand_txt = tk.Frame(brand, bg=SURFACE2)
        brand_txt.pack(side="left", padx=8)
        tk.Label(brand_txt, text="Wealth", bg=SURFACE2, fg=WHITE,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(brand_txt, text="Manager", bg=SURFACE2, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=16)

        # Nav items
        for key, label, icon in NAV_ITEMS:
            btn = self._make_nav_btn(sidebar, key, label, icon)
            self._nav_buttons[key] = btn

        # Footer
        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=16, side="bottom")
        tk.Label(sidebar, text="v1.0  •  2026", bg=SURFACE2, fg=TEXT_MUTED,
                 font=("Segoe UI", 8)).pack(side="bottom", pady=(0, 12))

        # ── Content area ───────────────────────────────────────────────────────
        self._content = tk.Frame(self, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

    def _make_nav_btn(self, sidebar, key, label, icon):
        frame = tk.Frame(sidebar, bg=SURFACE2, cursor="hand2")
        frame.pack(fill="x", padx=8, pady=2)

        inner = tk.Frame(frame, bg=SURFACE2)
        inner.pack(fill="x", padx=8, pady=6)

        icon_lbl = tk.Label(inner, text=icon, bg=SURFACE2, fg=TEXT_MUTED,
                            font=("Segoe UI", 14))
        icon_lbl.pack(side="left", padx=(4, 10))

        text_lbl = tk.Label(inner, text=label, bg=SURFACE2, fg=TEXT_MUTED,
                            font=("Segoe UI", 10), anchor="w")
        text_lbl.pack(side="left", fill="x", expand=True)

        def on_click(_e=None, k=key):
            self._show_page(k)

        for widget in (frame, inner, icon_lbl, text_lbl):
            widget.bind("<Button-1>", on_click)
            widget.configure(cursor="hand2")

        frame._inner   = inner
        frame._icon    = icon_lbl
        frame._text    = text_lbl
        return frame

    def _show_page(self, key: str):
        # Update nav highlight
        prev = self._active_page.get()
        if prev in self._nav_buttons:
            btn = self._nav_buttons[prev]
            btn.configure(bg=SURFACE2)
            btn._inner.configure(bg=SURFACE2)
            btn._icon.configure(bg=SURFACE2, fg=TEXT_MUTED)
            btn._text.configure(bg=SURFACE2, fg=TEXT_MUTED,
                                font=("Segoe UI", 10))

        self._active_page.set(key)
        btn = self._nav_buttons[key]
        btn.configure(bg=ACCENT)
        btn._inner.configure(bg=ACCENT)
        btn._icon.configure(bg=ACCENT, fg=WHITE)
        btn._text.configure(bg=ACCENT, fg=WHITE, font=("Segoe UI", 10, "bold"))

        # Show page
        for page in self._pages.values():
            page.pack_forget()

        if key not in self._pages:
            page_cls = {
                "dashboard":    DashboardView,
                "assets":       AssetsView,
                "transactions": TransactionsView,
                "goals":        GoalsView,
                "reports":      ReportsView,
            }[key]
            page = page_cls(self._content)
            self._pages[key] = page
        else:
            page = self._pages[key]
            if hasattr(page, "refresh"):
                page.refresh()

        page.pack(fill="both", expand=True)

    def _seed_demo_data(self):
        """Insert sample data only on first run (empty DB)."""
        if db.get_assets():
            return

        assets = [
            ("Tesouro Selic 2029",    "Renda Fixa",     85000, "BRL", "Tesouro Direto"),
            ("CDB Nubank 120% CDI",   "Renda Fixa",     35000, "BRL", "Nubank"),
            ("PETR4 – Petrobras",     "Renda Variável", 22000, "BRL", "XP Investimentos"),
            ("VALE3 – Vale",          "Renda Variável", 18500, "BRL", "XP Investimentos"),
            ("IVVB11 – S&P 500 ETF",  "Internacional",  14000, "BRL", "Rico"),
            ("Bitcoin",               "Criptomoedas",    9500, "BRL", "Binance"),
            ("Ethereum",              "Criptomoedas",    4200, "BRL", "Binance"),
            ("Apartamento SP",        "Imóveis",       320000, "BRL", "Próprio"),
            ("Previdência PGBL",      "Previdência",    28000, "BRL", "Bradesco"),
            ("Reserva Emergência",    "Emergência",     24000, "BRL", "Nubank"),
        ]
        for name, cat, val, cur, inst in assets:
            db.add_asset(name, cat, val, cur, inst)

        from datetime import date, timedelta
        today = date.today()
        transactions = [
            ("income",  "Salário",      "Salário Junho",        12500, str(today.replace(day=5))),
            ("income",  "Dividendos",   "Dividendos PETR4",      820,  str(today.replace(day=12))),
            ("income",  "Rendimento",   "Rendimento CDB",        420,  str(today.replace(day=15))),
            ("expense", "Moradia",      "Aluguel",              2200,  str(today.replace(day=10))),
            ("expense", "Alimentação",  "Supermercado",          680,  str(today.replace(day=8))),
            ("expense", "Transporte",   "Combustível",           350,  str(today.replace(day=14))),
            ("expense", "Saúde",        "Plano de Saúde",        480,  str(today.replace(day=5))),
            ("expense", "Lazer",        "Netflix + Spotify",      75,  str(today.replace(day=1))),
            ("expense", "Educação",     "Curso Python",          299,  str(today.replace(day=3))),
            ("income",  "Freelance",    "Projeto React",        3500,  str((today - timedelta(days=30)).replace(day=20))),
            ("expense", "Alimentação",  "Restaurantes",          520,  str((today - timedelta(days=30)).replace(day=22))),
            ("expense", "Vestuário",    "Roupas",                430,  str((today - timedelta(days=30)).replace(day=18))),
            ("income",  "Salário",      "Salário Maio",         12500, str((today - timedelta(days=30)).replace(day=5))),
        ]
        for tx_type, cat, desc, amt, dt in transactions:
            db.add_transaction(tx_type, cat, desc, amt, dt)

        goals = [
            ("Aposentadoria Antecipada", 2000000, 614700, "2045-12-31", "Aposentadoria",
             "FIRE aos 50 anos"),
            ("Reserva de Emergência",     36000,   24000, "2025-12-31", "Emergência",
             "6 meses de despesas"),
            ("Viagem para Europa",        25000,    8500, "2026-06-30", "Viagem",
             "Portugal e Espanha"),
            ("Novo Apartamento",         150000,   42000, "2030-01-01", "Imóvel",
             "Entrada do financiamento"),
        ]
        for name, target, current, deadline, cat, notes in goals:
            db.add_goal(name, target, current, deadline, cat, notes)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
