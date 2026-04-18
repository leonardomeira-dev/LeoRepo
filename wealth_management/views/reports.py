import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as mticker

from theme import (
    BG, SURFACE, SURFACE2, BORDER, ACCENT, ACCENT2, SUCCESS, DANGER, WARNING,
    TEXT, TEXT_MUTED, WHITE, CHART_COLORS, CATEGORY_COLORS,
    card_frame, fmt_currency,
)
import database as db


class ReportsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build()
        self.refresh()

    def _build(self):
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ttk.Label(hdr, text="Relatórios & Análises", style="Title.TLabel").pack(side="left")
        ttk.Button(hdr, text="Atualizar", style="Ghost.TButton",
                   command=self.refresh).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(0, 16))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self._patrimônio_frame = ttk.Frame(nb, style="TFrame")
        self._categoria_frame  = ttk.Frame(nb, style="TFrame")
        self._cashflow_frame   = ttk.Frame(nb, style="TFrame")
        self._expense_frame    = ttk.Frame(nb, style="TFrame")

        nb.add(self._patrimônio_frame, text="  Patrimônio  ")
        nb.add(self._categoria_frame,  text="  Por Categoria  ")
        nb.add(self._cashflow_frame,   text="  Fluxo de Caixa  ")
        nb.add(self._expense_frame,    text="  Despesas  ")

        self._nb = nb

    def refresh(self):
        self._build_patrimônio_tab()
        self._build_categoria_tab()
        self._build_cashflow_tab()
        self._build_expense_tab()

    # ── Tab 1: Net Worth breakdown ────────────────────────────────────────────
    def _build_patrimônio_tab(self):
        for w in self._patrimônio_frame.winfo_children():
            w.destroy()

        assets = db.get_assets()
        net_worth = sum(a["value"] for a in assets)

        top = ttk.Frame(self._patrimônio_frame, style="TFrame")
        top.pack(fill="x", padx=16, pady=12)

        for i, (label, val, color) in enumerate([
            ("Patrimônio Líquido", fmt_currency(net_worth), ACCENT),
            ("Quantidade de Ativos", str(len(assets)), ACCENT2),
            ("Maior Posição", fmt_currency(max((a["value"] for a in assets), default=0)), SUCCESS),
        ]):
            top.columnconfigure(i, weight=1)
            c = card_frame(top, padding=16)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 2 else 0)
            ttk.Label(c, text=label, style="CardMuted.TLabel").pack(anchor="w")
            tk.Label(c, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(4, 0))

        # Horizontal bar chart of individual assets
        chart_card = card_frame(self._patrimônio_frame, padding=16)
        chart_card.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        ttk.Label(chart_card, text="Valor por Ativo",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        sorted_assets = sorted(assets, key=lambda a: a["value"], reverse=True)[:15]
        fig = Figure(figsize=(10, max(3, len(sorted_assets) * 0.45)), dpi=96,
                     facecolor=SURFACE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(SURFACE)

        if sorted_assets:
            names  = [a["name"] for a in sorted_assets]
            values = [a["value"] for a in sorted_assets]
            colors = [CATEGORY_COLORS.get(a["category"],
                      CHART_COLORS[i % len(CHART_COLORS)])
                      for i, a in enumerate(sorted_assets)]
            y = range(len(names))
            bars = ax.barh(list(y), values, color=colors, alpha=0.85, height=0.6)

            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + net_worth * 0.005, bar.get_y() + bar.get_height()/2,
                        fmt_currency(val), va="center", color=TEXT_MUTED, fontsize=8)

            ax.set_yticks(list(y))
            ax.set_yticklabels(names, color=TEXT_MUTED, fontsize=9)
            ax.tick_params(colors=TEXT_MUTED, length=0)
            ax.xaxis.set_major_formatter(
                mticker.FuncFormatter(lambda x, _: f"R$ {x/1000:.0f}k" if x >= 1000 else f"R$ {x:.0f}")
            )
            ax.xaxis.set_tick_params(labelcolor=TEXT_MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.xaxis.grid(True, color=BORDER, linewidth=0.5)
            ax.set_axisbelow(True)
        else:
            ax.text(0.5, 0.5, "Nenhum ativo", ha="center", va="center",
                    color=TEXT_MUTED, fontsize=12, transform=ax.transAxes)

        fig.tight_layout(pad=0.8)
        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ── Tab 2: Category breakdown ──────────────────────────────────────────────
    def _build_categoria_tab(self):
        for w in self._categoria_frame.winfo_children():
            w.destroy()

        data = db.get_assets_by_category()
        total = sum(d[1] for d in data)

        fig = Figure(figsize=(9, 4.5), dpi=96, facecolor=SURFACE)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        for ax in (ax1, ax2):
            ax.set_facecolor(SURFACE)

        if data:
            labels = [d[0] for d in data]
            values = [d[1] for d in data]
            colors = [CATEGORY_COLORS.get(l, CHART_COLORS[i % len(CHART_COLORS)])
                      for i, l in enumerate(labels)]

            # Donut
            wedges, texts, autotexts = ax1.pie(
                values, colors=colors, startangle=90,
                wedgeprops=dict(width=0.6, edgecolor=SURFACE, linewidth=2),
                autopct="%1.1f%%", pctdistance=0.75,
            )
            for t in autotexts:
                t.set_color(WHITE)
                t.set_fontsize(8)
            ax1.set_title("Distribuição por Categoria", color=TEXT_MUTED,
                          fontsize=10, pad=10)

            # Bar
            x = range(len(labels))
            ax2.bar(x, values, color=colors, alpha=0.85)
            ax2.set_xticks(list(x))
            ax2.set_xticklabels(labels, rotation=30, ha="right",
                                color=TEXT_MUTED, fontsize=8)
            ax2.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f"R$ {v/1000:.0f}k" if v >= 1000 else f"R$ {v:.0f}")
            )
            ax2.tick_params(colors=TEXT_MUTED, length=0)
            ax2.yaxis.set_tick_params(labelcolor=TEXT_MUTED, labelsize=8)
            for spine in ax2.spines.values():
                spine.set_visible(False)
            ax2.yaxis.grid(True, color=BORDER, linewidth=0.5)
            ax2.set_axisbelow(True)
            ax2.set_title("Valor por Categoria (R$)", color=TEXT_MUTED,
                          fontsize=10, pad=10)
        else:
            for ax in (ax1, ax2):
                ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                        color=TEXT_MUTED, fontsize=11, transform=ax.transAxes)

        fig.tight_layout(pad=1)
        card = card_frame(self._categoria_frame, padding=16)
        card.pack(fill="both", expand=True, padx=16, pady=12)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Table below chart
        tbl_card = card_frame(self._categoria_frame, padding=12)
        tbl_card.pack(fill="x", padx=16, pady=(0, 12))
        ttk.Label(tbl_card, text="Resumo por Categoria",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        for cat, val in data:
            row = ttk.Frame(tbl_card, style="Card.TFrame")
            row.pack(fill="x", pady=2)
            color = CATEGORY_COLORS.get(cat, ACCENT)
            dot = tk.Frame(row, bg=color, width=10, height=10)
            dot.pack(side="left", padx=(0, 8), pady=4)
            dot.pack_propagate(False)
            tk.Label(row, text=cat, bg=SURFACE, fg=TEXT,
                     font=("Segoe UI", 10), width=18, anchor="w").pack(side="left")
            pct = (val / total * 100) if total else 0
            tk.Label(row, text=f"{pct:.1f}%", bg=SURFACE, fg=TEXT_MUTED,
                     font=("Segoe UI", 10), width=7, anchor="e").pack(side="right")
            tk.Label(row, text=fmt_currency(val), bg=SURFACE, fg=color,
                     font=("Segoe UI", 10, "bold"), width=18, anchor="e").pack(side="right")

    # ── Tab 3: Cash flow ───────────────────────────────────────────────────────
    def _build_cashflow_tab(self):
        for w in self._cashflow_frame.winfo_children():
            w.destroy()

        data = db.get_monthly_cashflow(12)
        fig = Figure(figsize=(10, 4), dpi=96, facecolor=SURFACE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(SURFACE)

        if data:
            months   = [d[0] for d in data]
            incomes  = [d[1] for d in data]
            expenses = [d[2] for d in data]
            balances = [i - e for i, e in zip(incomes, expenses)]
            x = range(len(months))
            w = 0.32

            ax.bar([i - w for i in x], incomes,  width=w, color=SUCCESS, alpha=0.85, label="Receita")
            ax.bar([i     for i in x], expenses, width=w, color=DANGER,  alpha=0.85, label="Despesa")
            ax.bar([i + w for i in x], balances, width=w,
                   color=[SUCCESS if b >= 0 else DANGER for b in balances],
                   alpha=0.7, label="Saldo")
            ax.plot([i + w for i in x], balances, color=WARNING, linewidth=1.5,
                    marker="o", markersize=4, label="Saldo (linha)")

            ax.set_xticks(list(x))
            ax.set_xticklabels(months, color=TEXT_MUTED, fontsize=8, rotation=30, ha="right")
            ax.tick_params(colors=TEXT_MUTED, length=0)
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f"R$ {v/1000:.0f}k" if abs(v) >= 1000 else f"R$ {v:.0f}")
            )
            ax.yaxis.set_tick_params(labelcolor=TEXT_MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.yaxis.grid(True, color=BORDER, linewidth=0.5)
            ax.set_axisbelow(True)
            ax.axhline(0, color=BORDER, linewidth=1)
            ax.legend(frameon=False, labelcolor=TEXT_MUTED, fontsize=8, loc="upper left")
            ax.set_title("Fluxo de Caixa Mensal (últimos 12 meses)", color=TEXT_MUTED,
                         fontsize=10, pad=10)
        else:
            ax.text(0.5, 0.5, "Nenhuma transação registrada", ha="center", va="center",
                    color=TEXT_MUTED, fontsize=12, transform=ax.transAxes)

        fig.tight_layout(pad=0.8)
        card = card_frame(self._cashflow_frame, padding=16)
        card.pack(fill="both", expand=True, padx=16, pady=12)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ── Tab 4: Expense breakdown ───────────────────────────────────────────────
    def _build_expense_tab(self):
        for w in self._expense_frame.winfo_children():
            w.destroy()

        txs = db.get_transactions(limit=1000, tx_type="expense")
        by_cat: dict = {}
        for tx in txs:
            by_cat[tx["category"]] = by_cat.get(tx["category"], 0) + tx["amount"]

        data = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
        total = sum(v for _, v in data)

        fig = Figure(figsize=(9, 4), dpi=96, facecolor=SURFACE)
        ax = fig.add_subplot(111)
        ax.set_facecolor(SURFACE)

        if data:
            labels = [d[0] for d in data]
            values = [d[1] for d in data]
            colors = CHART_COLORS[:len(labels)]
            x = range(len(labels))
            bars = ax.bar(x, values, color=colors, alpha=0.85)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + total*0.005,
                        fmt_currency(val), ha="center", va="bottom",
                        color=TEXT_MUTED, fontsize=7.5)
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, color=TEXT_MUTED, fontsize=9, rotation=20, ha="right")
            ax.tick_params(colors=TEXT_MUTED, length=0)
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda v, _: f"R$ {v/1000:.0f}k" if v >= 1000 else f"R$ {v:.0f}")
            )
            ax.yaxis.set_tick_params(labelcolor=TEXT_MUTED, labelsize=8)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.yaxis.grid(True, color=BORDER, linewidth=0.5)
            ax.set_axisbelow(True)
            ax.set_title("Despesas por Categoria (todos os períodos)", color=TEXT_MUTED,
                         fontsize=10, pad=10)
        else:
            ax.text(0.5, 0.5, "Nenhuma despesa registrada", ha="center", va="center",
                    color=TEXT_MUTED, fontsize=12, transform=ax.transAxes)

        fig.tight_layout(pad=0.8)
        card = card_frame(self._expense_frame, padding=16)
        card.pack(fill="both", expand=True, padx=16, pady=12)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
