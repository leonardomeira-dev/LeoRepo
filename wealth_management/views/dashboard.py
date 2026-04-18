import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from theme import (
    BG, SURFACE, SURFACE2, BORDER, ACCENT, ACCENT2, SUCCESS, DANGER,
    WARNING, TEXT, TEXT_MUTED, WHITE, CHART_COLORS, CATEGORY_COLORS,
    card_frame, fmt_currency, fmt_pct,
)
import database as db


class DashboardView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ttk.Label(hdr, text="Dashboard", style="Title.TLabel").pack(side="left")
        now = datetime.now().strftime("%d de %B de %Y")
        ttk.Label(hdr, text=now, style="Muted.TLabel").pack(side="right", pady=8)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(0, 16))

        # KPI row
        self.kpi_frame = ttk.Frame(self, style="TFrame")
        self.kpi_frame.pack(fill="x", padx=24, pady=(0, 16))

        # Charts row
        charts_row = ttk.Frame(self, style="TFrame")
        charts_row.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.pie_frame = card_frame(charts_row, padding=12)
        self.pie_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.bar_frame = card_frame(charts_row, padding=12)
        self.bar_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

    def refresh(self):
        self._refresh_kpis()
        self._refresh_charts()

    def _refresh_kpis(self):
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        net_worth = db.get_net_worth()
        now = datetime.now()
        income, expense = db.get_monthly_summary(now.year, now.month)
        balance = income - expense
        assets = db.get_assets()
        asset_count = len(assets)

        kpis = [
            ("Patrimônio Líquido", fmt_currency(net_worth), ACCENT, "▲ Atualizado hoje"),
            ("Receita do Mês", fmt_currency(income), SUCCESS, f"{now.strftime('%B %Y')}"),
            ("Despesa do Mês", fmt_currency(expense), DANGER, f"{now.strftime('%B %Y')}"),
            ("Saldo Mensal", fmt_currency(balance),
             SUCCESS if balance >= 0 else DANGER,
             "Receitas - Despesas"),
            ("Total de Ativos", str(asset_count), ACCENT2, "Cadastrados"),
        ]

        for i, (label, value, color, sub) in enumerate(kpis):
            self.kpi_frame.columnconfigure(i, weight=1)
            card = card_frame(self.kpi_frame, padding=16)
            card.grid(row=0, column=i, padx=(0, 8) if i < len(kpis)-1 else 0, sticky="nsew")

            ttk.Label(card, text=label, style="CardMuted.TLabel").pack(anchor="w")
            val_lbl = tk.Label(card, text=value, bg=SURFACE, fg=color,
                               font=("Segoe UI", 20, "bold"))
            val_lbl.pack(anchor="w", pady=(4, 2))
            ttk.Label(card, text=sub, style="CardMuted.TLabel").pack(anchor="w")

            # accent bar at bottom
            bar = tk.Frame(card, bg=color, height=3)
            bar.pack(fill="x", side="bottom", pady=(8, 0))

    def _refresh_charts(self):
        for w in self.pie_frame.winfo_children():
            w.destroy()
        for w in self.bar_frame.winfo_children():
            w.destroy()

        self._build_pie_chart()
        self._build_bar_chart()

    def _build_pie_chart(self):
        ttk.Label(self.pie_frame, text="Alocação por Categoria",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        data = db.get_assets_by_category()
        fig = Figure(figsize=(4.5, 3.2), dpi=100, facecolor=SURFACE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(SURFACE)

        if data:
            labels = [d[0] for d in data]
            values = [d[1] for d in data]
            total = sum(values)
            colors = [CATEGORY_COLORS.get(l, CHART_COLORS[i % len(CHART_COLORS)])
                      for i, l in enumerate(labels)]
            wedges, _ = ax.pie(
                values, colors=colors, startangle=90,
                wedgeprops=dict(width=0.55, edgecolor=SURFACE, linewidth=2),
            )
            # center label
            ax.text(0, 0, fmt_currency(total), ha="center", va="center",
                    color=WHITE, fontsize=11, fontweight="bold",
                    fontfamily="Segoe UI")
            ax.text(0, -0.18, "Patrimônio Total", ha="center", va="center",
                    color=TEXT_MUTED, fontsize=8, fontfamily="Segoe UI")

            patches = [mpatches.Patch(color=colors[i], label=f"{labels[i]}  {fmt_pct(values[i]/total*100)}")
                       for i in range(len(labels))]
            ax.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.18),
                      ncol=2, frameon=False,
                      fontsize=7.5, labelcolor=TEXT_MUTED)
        else:
            ax.text(0.5, 0.5, "Nenhum ativo cadastrado", ha="center", va="center",
                    color=TEXT_MUTED, fontsize=10, transform=ax.transAxes)
            ax.set_visible(False)

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_bar_chart(self):
        ttk.Label(self.bar_frame, text="Fluxo de Caixa Mensal",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        data = db.get_monthly_cashflow(6)
        fig = Figure(figsize=(5, 3.2), dpi=100, facecolor=SURFACE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(SURFACE)

        if data:
            months   = [d[0][5:] for d in data]  # "MM"
            incomes  = [d[1] for d in data]
            expenses = [d[2] for d in data]
            x = range(len(months))
            w = 0.38
            ax.bar([i - w/2 for i in x], incomes,  width=w, color=SUCCESS,
                   alpha=0.85, label="Receita")
            ax.bar([i + w/2 for i in x], expenses, width=w, color=DANGER,
                   alpha=0.85, label="Despesa")
            ax.set_xticks(list(x))
            ax.set_xticklabels(months, color=TEXT_MUTED, fontsize=9)
            ax.tick_params(colors=TEXT_MUTED, length=0)
            ax.yaxis.set_tick_params(labelcolor=TEXT_MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_axisbelow(True)
            ax.yaxis.grid(True, color=BORDER, linewidth=0.5)
            ax.legend(frameon=False, labelcolor=TEXT_MUTED, fontsize=8)
        else:
            ax.text(0.5, 0.5, "Nenhuma transação registrada", ha="center", va="center",
                    color=TEXT_MUTED, fontsize=10, transform=ax.transAxes)

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasTkAgg(fig, master=self.bar_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
