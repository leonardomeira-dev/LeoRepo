import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from theme import (
    BG, SURFACE, SURFACE2, BORDER, ACCENT, SUCCESS, DANGER,
    TEXT, TEXT_MUTED, WHITE, card_frame, fmt_currency,
)
import database as db

INCOME_CATEGORIES = [
    "Salário", "Freelance", "Dividendos", "Aluguel",
    "Rendimento", "Bônus", "Restituição", "Outros",
]
EXPENSE_CATEGORIES = [
    "Moradia", "Alimentação", "Transporte", "Saúde",
    "Educação", "Lazer", "Vestuário", "Serviços",
    "Investimento", "Impostos", "Viagem", "Outros",
]


class TransactionsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._filter_type = tk.StringVar(value="all")
        self._build()
        self.refresh()

    def _build(self):
        # Header
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ttk.Label(hdr, text="Transações", style="Title.TLabel").pack(side="left")
        ttk.Button(hdr, text="+ Nova Transação", style="Primary.TButton",
                   command=self._open_form).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(0, 12))

        # Summary cards
        self.summary_frame = ttk.Frame(self, style="TFrame")
        self.summary_frame.pack(fill="x", padx=24, pady=(0, 12))

        # Filter bar
        flt = ttk.Frame(self, style="TFrame")
        flt.pack(fill="x", padx=24, pady=(0, 8))

        ttk.Label(flt, text="Filtrar:", style="Muted.TLabel").pack(side="left", padx=(0, 8))
        for text, val in [("Todas", "all"), ("Receitas", "income"), ("Despesas", "expense")]:
            rb = tk.Radiobutton(flt, text=text, variable=self._filter_type, value=val,
                                bg=BG, fg=TEXT_MUTED, selectcolor=BG,
                                activebackground=BG, activeforeground=TEXT,
                                font=("Segoe UI", 10), cursor="hand2",
                                command=self._refresh_table)
            rb.pack(side="left", padx=4)

        # Search
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_table())
        ttk.Entry(flt, textvariable=self._search_var, width=24).pack(side="right")
        ttk.Label(flt, text="Buscar:", style="Muted.TLabel").pack(side="right", padx=(0, 4))

        # Table
        table_card = card_frame(self, padding=0)
        table_card.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        self._build_table(table_card)

    def _build_table(self, parent):
        cols = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        headers = {"date": "Data", "type": "Tipo", "category": "Categoria",
                   "description": "Descrição", "amount": "Valor"}
        widths = {"date": 100, "type": 90, "category": 130,
                  "description": 260, "amount": 120}
        anchors = {"date": "center", "type": "center", "category": "w",
                   "description": "w", "amount": "e"}

        for c in cols:
            self.tree.heading(c, text=headers[c],
                              command=lambda col=c: self._sort_by(col))
            self.tree.column(c, width=widths[c], anchor=anchors[c])

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("income", foreground=SUCCESS)
        self.tree.tag_configure("expense", foreground=DANGER)
        self.tree.tag_configure("alt", background=SURFACE2)

        self.tree.bind("<Delete>", lambda _: self._delete_selected())
        self.tree.bind("<Double-1>", lambda _: self._delete_confirm())

        # Right-click menu
        self._ctx_menu = tk.Menu(self, tearoff=0, bg=SURFACE2, fg=TEXT,
                                 font=("Segoe UI", 10))
        self._ctx_menu.add_command(label="Excluir", command=self._delete_confirm)
        self.tree.bind("<Button-3>", self._show_ctx)

        self._all_rows = []
        self._sort_col = "date"
        self._sort_rev = True

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self._refresh_table()

    def _show_ctx(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.tree.selection_set(row)
            self._ctx_menu.post(event.x_root, event.y_root)

    def refresh(self):
        self._all_rows = db.get_transactions(limit=500)
        self._refresh_summary()
        self._refresh_table()

    def _refresh_summary(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()
        now = datetime.now()
        income, expense = db.get_monthly_summary(now.year, now.month)
        balance = income - expense

        items = [
            ("Receita Total (mês)", fmt_currency(income), SUCCESS),
            ("Despesa Total (mês)", fmt_currency(expense), DANGER),
            ("Saldo do Mês", fmt_currency(balance), SUCCESS if balance >= 0 else DANGER),
            ("Total de Registros", str(len(self._all_rows)), ACCENT),
        ]
        for i, (label, val, color) in enumerate(items):
            self.summary_frame.columnconfigure(i, weight=1)
            c = card_frame(self.summary_frame, padding=14)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 3 else 0)
            ttk.Label(c, text=label, style="CardMuted.TLabel").pack(anchor="w")
            tk.Label(c, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(2, 0))

    def _refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        ftype  = self._filter_type.get()
        search = self._search_var.get().lower()

        rows = self._all_rows
        if ftype != "all":
            rows = [r for r in rows if r["type"] == ftype]
        if search:
            rows = [r for r in rows if
                    search in r["description"].lower() or
                    search in r["category"].lower()]

        key_map = {"date": "date", "type": "type", "category": "category",
                   "description": "description", "amount": "amount"}
        col = key_map.get(self._sort_col, "date")
        rows = sorted(rows, key=lambda r: r[col], reverse=self._sort_rev)

        for i, tx in enumerate(rows):
            tag = tx["type"]
            if i % 2:
                tag = (tag, "alt")
            type_label = "Receita" if tx["type"] == "income" else "Despesa"
            self.tree.insert("", "end", iid=str(tx["id"]),
                             values=(tx["date"], type_label, tx["category"],
                                     tx["description"], fmt_currency(tx["amount"])),
                             tags=tag)

    def _delete_confirm(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Confirmar", "Excluir esta transação?", parent=self):
            db.delete_transaction(int(sel[0]))
            self.refresh()

    def _delete_selected(self):
        self._delete_confirm()

    def _open_form(self):
        TransactionForm(self, on_save=self.refresh)


class TransactionForm(tk.Toplevel):
    def __init__(self, parent, on_save=None):
        super().__init__(parent)
        self._on_save = on_save
        self.title("Nova Transação")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._type_var = tk.StringVar(value="income")
        self._build()
        self._update_categories()
        self.update_idletasks()
        self._center()

    def _center(self):
        self.geometry(f"+{self.winfo_screenwidth()//2 - 210}+"
                      f"{self.winfo_screenheight()//2 - 270}")

    def _build(self):
        pad = {"padx": 28, "pady": 4}
        ttk.Label(self, text="Nova Transação", style="Heading.TLabel").pack(
            pady=(20, 4), padx=28, anchor="w")
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=28, pady=4)

        # Type radio
        type_row = ttk.Frame(self, style="TFrame")
        type_row.pack(fill="x", **pad)
        ttk.Label(type_row, text="Tipo:", style="Muted.TLabel").pack(side="left", padx=(0, 12))
        for text, val, color in [("Receita", "income", SUCCESS), ("Despesa", "expense", DANGER)]:
            rb = tk.Radiobutton(type_row, text=text, variable=self._type_var, value=val,
                                bg=BG, fg=color, selectcolor=BG,
                                activebackground=BG, activeforeground=color,
                                font=("Segoe UI", 11, "bold"), cursor="hand2",
                                command=self._update_categories)
            rb.pack(side="left", padx=8)

        ttk.Label(self, text="Categoria", style="Muted.TLabel").pack(anchor="w", **pad)
        self._cat = ttk.Combobox(self, state="readonly", width=34)
        self._cat.pack(**pad)

        ttk.Label(self, text="Descrição", style="Muted.TLabel").pack(anchor="w", **pad)
        self._desc = ttk.Entry(self, width=36)
        self._desc.pack(**pad)

        ttk.Label(self, text="Valor (R$)", style="Muted.TLabel").pack(anchor="w", **pad)
        self._amount = ttk.Entry(self, width=36)
        self._amount.pack(**pad)

        ttk.Label(self, text="Data", style="Muted.TLabel").pack(anchor="w", **pad)
        self._date = ttk.Entry(self, width=36)
        self._date.insert(0, date.today().strftime("%Y-%m-%d"))
        self._date.pack(**pad)

        ttk.Label(self, text="Notas (opcional)", style="Muted.TLabel").pack(anchor="w", **pad)
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

    def _update_categories(self):
        cats = INCOME_CATEGORIES if self._type_var.get() == "income" else EXPENSE_CATEGORIES
        self._cat["values"] = cats
        self._cat.current(0)

    def _save(self):
        tx_type = self._type_var.get()
        cat     = self._cat.get()
        desc    = self._desc.get().strip()
        dt      = self._date.get().strip()
        notes   = self._notes.get("1.0", "end").strip()

        try:
            amt = float(self._amount.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.", parent=self)
            return

        if not desc:
            messagebox.showerror("Erro", "Informe a descrição.", parent=self)
            return

        try:
            datetime.strptime(dt, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato AAAA-MM-DD.", parent=self)
            return

        db.add_transaction(tx_type, cat, desc, amt, dt, notes)
        if self._on_save:
            self._on_save()
        self.destroy()
