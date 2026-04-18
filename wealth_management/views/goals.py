import tkinter as tk
from tkinter import ttk, messagebox

from theme import (
    BG, SURFACE, SURFACE2, BORDER, ACCENT, ACCENT2, SUCCESS, DANGER, WARNING,
    TEXT, TEXT_MUTED, WHITE, CHART_COLORS, card_frame, fmt_currency, fmt_pct,
)
import database as db

GOAL_CATEGORIES = [
    "Aposentadoria", "Emergência", "Viagem", "Imóvel",
    "Veículo", "Educação", "Investimento", "Outros",
]


class GoalsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self._build()
        self.refresh()

    def _build(self):
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ttk.Label(hdr, text="Metas Financeiras", style="Title.TLabel").pack(side="left")
        ttk.Button(hdr, text="+ Nova Meta", style="Primary.TButton",
                   command=self._open_form).pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=(0, 16))

        self.scroll_canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.goals_frame = ttk.Frame(self.scroll_canvas, style="TFrame")
        self._win = self.scroll_canvas.create_window((0, 0), window=self.goals_frame, anchor="nw")

        self.goals_frame.bind("<Configure>", self._on_frame_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, _):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.scroll_canvas.itemconfig(self._win, width=event.width)

    def _on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh(self):
        for w in self.goals_frame.winfo_children():
            w.destroy()
        goals = db.get_goals()
        if not goals:
            ttk.Label(self.goals_frame, text="Nenhuma meta cadastrada ainda.",
                      style="Muted.TLabel").pack(pady=40)
            return

        # Summary row
        sum_frame = ttk.Frame(self.goals_frame, style="TFrame")
        sum_frame.pack(fill="x", padx=24, pady=(8, 16))
        total_target = sum(g["target_amount"] for g in goals)
        total_current = sum(g["current_amount"] for g in goals)
        overall_pct = (total_current / total_target * 100) if total_target else 0

        for i, (label, val, color) in enumerate([
            ("Total de Metas", str(len(goals)), ACCENT),
            ("Total Almejado", fmt_currency(total_target), TEXT),
            ("Total Acumulado", fmt_currency(total_current), SUCCESS),
            ("Progresso Geral", fmt_pct(overall_pct), ACCENT2),
        ]):
            sum_frame.columnconfigure(i, weight=1)
            c = card_frame(sum_frame, padding=14)
            c.grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 3 else 0)
            ttk.Label(c, text=label, style="CardMuted.TLabel").pack(anchor="w")
            tk.Label(c, text=val, bg=SURFACE, fg=color,
                     font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(2, 0))

        # Goal cards grid (2 columns)
        grid = ttk.Frame(self.goals_frame, style="TFrame")
        grid.pack(fill="both", expand=True, padx=24)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for idx, goal in enumerate(goals):
            row, col = divmod(idx, 2)
            self._make_goal_card(grid, goal, row, col)

    def _make_goal_card(self, parent, goal, row, col):
        card = card_frame(parent, padding=18)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        pct = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] else 0
        pct = min(pct, 100)
        color = CHART_COLORS[row * 2 + col % len(CHART_COLORS)]

        # Title row
        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.pack(fill="x", pady=(0, 4))
        tk.Label(title_row, text=goal["name"], bg=SURFACE, fg=WHITE,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        if goal["category"]:
            tk.Label(title_row, text=goal["category"], bg=ACCENT2, fg=WHITE,
                     font=("Segoe UI", 8, "bold"), padx=6, pady=2).pack(side="right")

        # Deadline
        if goal["deadline"]:
            ttk.Label(card, text=f"Prazo: {goal['deadline']}", style="CardMuted.TLabel").pack(anchor="w")

        # Values
        val_row = ttk.Frame(card, style="Card.TFrame")
        val_row.pack(fill="x", pady=8)
        tk.Label(val_row, text=fmt_currency(goal["current_amount"]),
                 bg=SURFACE, fg=color, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(val_row, text=f" / {fmt_currency(goal['target_amount'])}",
                 bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 11)).pack(side="left", pady=4)

        # Progress bar
        bar_bg = tk.Frame(card, bg=SURFACE2, height=10)
        bar_bg.pack(fill="x", pady=(0, 4))
        bar_bg.update_idletasks()
        bar_fill = tk.Frame(bar_bg, bg=color, height=10)
        bar_fill.place(x=0, y=0, relwidth=pct/100, height=10)

        pct_label = f"{pct:.1f}% concluído"
        if pct >= 100:
            pct_label = "Meta atingida!"
        ttk.Label(card, text=pct_label, style="CardMuted.TLabel").pack(anchor="w")

        # Notes
        if goal["notes"]:
            ttk.Separator(card, orient="horizontal").pack(fill="x", pady=8)
            tk.Label(card, text=goal["notes"], bg=SURFACE, fg=TEXT_MUTED,
                     font=("Segoe UI", 9), wraplength=280, justify="left").pack(anchor="w")

        # Action buttons
        btn_row = ttk.Frame(card, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Editar", style="Ghost.TButton",
                   command=lambda g=goal: self._open_form(g)).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Excluir", style="Danger.TButton",
                   command=lambda g=goal: self._delete(g["id"])).pack(side="left")

    def _delete(self, goal_id):
        if messagebox.askyesno("Confirmar", "Excluir esta meta?", parent=self):
            db.delete_goal(goal_id)
            self.refresh()

    def _open_form(self, goal=None):
        GoalForm(self, goal, on_save=self.refresh)


class GoalForm(tk.Toplevel):
    def __init__(self, parent, goal=None, on_save=None):
        super().__init__(parent)
        self._goal = goal
        self._on_save = on_save
        self.title("Editar Meta" if goal else "Nova Meta")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if goal:
            self._fill(goal)
        self.update_idletasks()
        self._center()

    def _center(self):
        self.geometry(f"+{self.winfo_screenwidth()//2 - 210}+"
                      f"{self.winfo_screenheight()//2 - 280}")

    def _build(self):
        pad = {"padx": 28, "pady": 4}
        ttk.Label(self, text="Editar Meta" if self._goal else "Nova Meta",
                  style="Heading.TLabel").pack(pady=(20, 4), padx=28, anchor="w")
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=28, pady=4)

        ttk.Label(self, text="Nome da meta", style="Muted.TLabel").pack(anchor="w", **pad)
        self._name = ttk.Entry(self, width=36)
        self._name.pack(**pad)

        ttk.Label(self, text="Categoria", style="Muted.TLabel").pack(anchor="w", **pad)
        self._cat = ttk.Combobox(self, values=GOAL_CATEGORIES, state="readonly", width=34)
        self._cat.pack(**pad)
        self._cat.current(0)

        ttk.Label(self, text="Valor alvo (R$)", style="Muted.TLabel").pack(anchor="w", **pad)
        self._target = ttk.Entry(self, width=36)
        self._target.pack(**pad)

        ttk.Label(self, text="Valor acumulado (R$)", style="Muted.TLabel").pack(anchor="w", **pad)
        self._current = ttk.Entry(self, width=36)
        self._current.insert(0, "0")
        self._current.pack(**pad)

        ttk.Label(self, text="Prazo (AAAA-MM-DD)", style="Muted.TLabel").pack(anchor="w", **pad)
        self._deadline = ttk.Entry(self, width=36)
        self._deadline.pack(**pad)

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

    def _fill(self, g):
        self._name.insert(0, g["name"])
        if g["category"] in GOAL_CATEGORIES:
            self._cat.current(GOAL_CATEGORIES.index(g["category"]))
        self._target.insert(0, str(g["target_amount"]))
        self._current.delete(0, "end")
        self._current.insert(0, str(g["current_amount"]))
        self._deadline.insert(0, g["deadline"] or "")
        if g["notes"]:
            self._notes.insert("1.0", g["notes"])

    def _save(self):
        name = self._name.get().strip()
        cat  = self._cat.get()
        dl   = self._deadline.get().strip()
        notes = self._notes.get("1.0", "end").strip()

        try:
            target = float(self._target.get().replace(",", "."))
            current = float(self._current.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido.", parent=self)
            return

        if not name:
            messagebox.showerror("Erro", "Informe o nome da meta.", parent=self)
            return

        if self._goal:
            db.update_goal(self._goal["id"], name, target, current, dl, cat, notes)
        else:
            db.add_goal(name, target, current, dl, cat, notes)

        if self._on_save:
            self._on_save()
        self.destroy()
