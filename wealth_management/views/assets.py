import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from theme import (
    BG, SURFACE, SURFACE2, BORDER, ACCENT, SUCCESS, DANGER, WARNING,
    TEXT, TEXT_MUTED, WHITE, CATEGORY_COLORS, CHART_COLORS,
    card_frame, fmt_currency,
)
import database as db

ASSET_CATEGORIES = [
    "Renda Fixa", "Renda Variável", "Imóveis", "Criptomoedas",
    "Internacional", "Previdência", "Emergência", "Outros",
]
CURRENCIES = ["BRL", "USD", "EUR", "BTC", "ETH"]


class AssetsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._selected_id = None
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ttk.Label(hdr, text="Gestão de Ativos", style="Title.TLabel").pack(side="left")
        ttk.Button(hdr, text="+ Novo Ativo", style="Primary.TButton",
                   command=self._open_form).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(0, 16))

        # Summary row
        self.summary_frame = ttk.Frame(self, style="TFrame")
        self.summary_frame.pack(fill="x", padx=24, pady=(0, 16))

        # Main content: table + sidebar
        content = ttk.Frame(self, style="TFrame")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Table
        table_card = card_frame(content, padding=0)
        table_card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self._build_table(table_card)

        # Detail sidebar
        self.detail_card = card_frame(content, padding=16, width=280)
        self.detail_card.pack(side="left", fill="y")
        self.detail_card.pack_propagate(False)
        ttk.Label(self.detail_card, text="Detalhes do Ativo",
                  style="CardTitle.TLabel").pack(anchor="w", pady=(0, 12))
        self._detail_placeholder()

    def _build_table(self, parent):
        cols = ("name", "category", "institution", "currency", "value")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        headers = {"name": "Ativo", "category": "Categoria",
                   "institution": "Instituição", "currency": "Moeda", "value": "Valor"}
        widths = {"name": 200, "category": 130, "institution": 130, "currency": 60, "value": 120}
        anchors = {"name": "w", "category": "w", "institution": "w",
                   "currency": "center", "value": "e"}
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor=anchors[c])

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.tag_configure("income_row", background=SURFACE)
        self.tree.tag_configure("alt_row", background=SURFACE2)

    def _detail_placeholder(self):
        for w in self.detail_card.winfo_children():
            if str(w) != str(self.detail_card.winfo_children()[0]):
                w.destroy()
        ttk.Label(self.detail_card,
                  text="Selecione um ativo\npara ver detalhes.",
                  style="CardMuted.TLabel",
                  justify="center").pack(expand=True)

    def refresh(self):
        self._refresh_summary()
        self._refresh_table()

    def _refresh_summary(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()

        assets = db.get_assets()
        total = sum(a["value"] for a in assets)
        by_cat = db.get_assets_by_category()

        self.summary_frame.columnconfigure(0, weight=1)

        tot_card = card_frame(self.summary_frame, padding=14)
        tot_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(tot_card, text="Total em Ativos", style="CardMuted.TLabel").pack(anchor="w")
        tk.Label(tot_card, text=fmt_currency(total), bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(2, 0))

        for i, (cat, val) in enumerate(by_cat[:4], start=1):
            self.summary_frame.columnconfigure(i, weight=1)
            c = card_frame(self.summary_frame, padding=14)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 4 else 0)
            color = CATEGORY_COLORS.get(cat, CHART_COLORS[i % len(CHART_COLORS)])
            pct = (val / total * 100) if total else 0
            ttk.Label(c, text=cat, style="CardMuted.TLabel").pack(anchor="w")
            tk.Label(c, text=fmt_currency(val), bg=SURFACE, fg=color,
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(2, 0))
            ttk.Label(c, text=f"{pct:.1f}% do total", style="CardMuted.TLabel").pack(anchor="w")
            bar = tk.Frame(c, bg=color, height=3)
            bar.pack(fill="x", side="bottom", pady=(6, 0))

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for i, a in enumerate(db.get_assets()):
            tag = "alt_row" if i % 2 else "income_row"
            self.tree.insert("", "end", iid=str(a["id"]),
                             values=(a["name"], a["category"], a["institution"] or "—",
                                     a["currency"], fmt_currency(a["value"])),
                             tags=(tag,))

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        self._selected_id = int(sel[0])
        assets = {a["id"]: a for a in db.get_assets()}
        asset = assets.get(self._selected_id)
        if asset:
            self._show_detail(asset)

    def _show_detail(self, asset):
        for w in list(self.detail_card.winfo_children())[1:]:
            w.destroy()

        def row(label, value, color=TEXT):
            f = ttk.Frame(self.detail_card, style="Card.TFrame")
            f.pack(fill="x", pady=3)
            ttk.Label(f, text=label, style="CardMuted.TLabel", width=14).pack(side="left")
            tk.Label(f, text=value, bg=SURFACE, fg=color,
                     font=("Segoe UI", 10, "bold")).pack(side="left")

        color = CATEGORY_COLORS.get(asset["category"], ACCENT)
        row("Nome:", asset["name"])
        row("Categoria:", asset["category"], color)
        row("Valor:", fmt_currency(asset["value"]), SUCCESS)
        row("Moeda:", asset["currency"])
        row("Instituição:", asset["institution"] or "—")
        if asset["notes"]:
            ttk.Label(self.detail_card, text="Notas:", style="CardMuted.TLabel").pack(anchor="w", pady=(8, 2))
            tk.Label(self.detail_card, text=asset["notes"], bg=SURFACE, fg=TEXT_MUTED,
                     font=("Segoe UI", 9), wraplength=240, justify="left").pack(anchor="w")

        ttk.Separator(self.detail_card, orient="horizontal").pack(fill="x", pady=10)

        btn_row = ttk.Frame(self.detail_card, style="Card.TFrame")
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Editar", style="Ghost.TButton",
                   command=lambda: self._open_form(asset)).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Excluir", style="Danger.TButton",
                   command=lambda: self._delete_asset(asset["id"])).pack(side="left")

    def _delete_asset(self, asset_id):
        if messagebox.askyesno("Confirmar", "Excluir este ativo?", parent=self):
            db.delete_asset(asset_id)
            self._detail_placeholder()
            self._selected_id = None
            self.refresh()

    def _open_form(self, asset=None):
        AssetForm(self, asset, on_save=self.refresh)


class AssetForm(tk.Toplevel):
    def __init__(self, parent, asset=None, on_save=None):
        super().__init__(parent)
        self._asset = asset
        self._on_save = on_save
        self.title("Editar Ativo" if asset else "Novo Ativo")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if asset:
            self._fill(asset)
        self.update_idletasks()
        self._center()

    def _center(self):
        self.geometry(f"+{self.winfo_screenwidth()//2 - 220}+"
                      f"{self.winfo_screenheight()//2 - 240}")

    def _field(self, parent, label):
        ttk.Label(parent, text=label, style="Muted.TLabel").pack(anchor="w", pady=(8, 2))

    def _build(self):
        pad = {"padx": 28, "pady": 4}
        ttk.Label(self, text="Editar Ativo" if self._asset else "Novo Ativo",
                  style="Heading.TLabel").pack(pady=(20, 4), padx=28, anchor="w")
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=28, pady=4)

        self._field(self, "Nome do ativo")
        self._name = ttk.Entry(self, width=36)
        self._name.pack(**pad)

        self._field(self, "Categoria")
        self._cat = ttk.Combobox(self, values=ASSET_CATEGORIES, state="readonly", width=34)
        self._cat.pack(**pad)
        self._cat.current(0)

        self._field(self, "Valor atual")
        self._val = ttk.Entry(self, width=36)
        self._val.pack(**pad)

        self._field(self, "Moeda")
        self._cur = ttk.Combobox(self, values=CURRENCIES, state="readonly", width=34)
        self._cur.pack(**pad)
        self._cur.current(0)

        self._field(self, "Instituição / Corretora")
        self._inst = ttk.Entry(self, width=36)
        self._inst.pack(**pad)

        self._field(self, "Notas (opcional)")
        self._notes = tk.Text(self, width=34, height=3, bg=SURFACE2, fg=TEXT,
                              insertbackground=TEXT, font=("Segoe UI", 10),
                              relief="flat", bd=6)
        self._notes.pack(**pad)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=28, pady=12)

        btn_row = ttk.Frame(self, style="TFrame")
        btn_row.pack(padx=28, pady=(0, 20), anchor="e")
        ttk.Button(btn_row, text="Cancelar", style="Ghost.TButton",
                   command=self.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Salvar", style="Primary.TButton",
                   command=self._save).pack(side="left")

    def _fill(self, a):
        self._name.insert(0, a["name"])
        if a["category"] in ASSET_CATEGORIES:
            self._cat.current(ASSET_CATEGORIES.index(a["category"]))
        self._val.delete(0, "end")
        self._val.insert(0, str(a["value"]))
        if a["currency"] in CURRENCIES:
            self._cur.current(CURRENCIES.index(a["currency"]))
        self._inst.insert(0, a["institution"] or "")
        if a["notes"]:
            self._notes.insert("1.0", a["notes"])

    def _save(self):
        name = self._name.get().strip()
        cat  = self._cat.get()
        inst = self._inst.get().strip()
        notes = self._notes.get("1.0", "end").strip()
        cur  = self._cur.get()

        try:
            val = float(self._val.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.", parent=self)
            return

        if not name:
            messagebox.showerror("Erro", "Informe o nome do ativo.", parent=self)
            return

        if self._asset:
            db.update_asset(self._asset["id"], name, cat, val, cur, inst, notes)
        else:
            db.add_asset(name, cat, val, cur, inst, notes)

        if self._on_save:
            self._on_save()
        self.destroy()
