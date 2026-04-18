"""
Centralized color palette and widget style helpers.
"""
import tkinter as tk
from tkinter import ttk

# ── Palette ────────────────────────────────────────────────────────────────────
BG        = "#0F1117"   # page background
SURFACE   = "#1A1D27"   # card / panel background
SURFACE2  = "#222534"   # slightly lighter surface
BORDER    = "#2E3247"   # subtle borders
ACCENT    = "#4F8EF7"   # primary blue
ACCENT2   = "#7C5CFC"   # purple accent
SUCCESS   = "#2DD4BF"   # teal / positive
DANGER    = "#F87171"   # red / negative
WARNING   = "#FBBF24"   # yellow / caution
TEXT      = "#E8EAF0"   # primary text
TEXT_MUTED= "#8B90A8"   # secondary / placeholder text
WHITE     = "#FFFFFF"

# Chart palette
CHART_COLORS = [
    "#4F8EF7", "#7C5CFC", "#2DD4BF", "#FBBF24",
    "#F87171", "#34D399", "#F472B6", "#60A5FA",
]

# Category → color quick-lookup
CATEGORY_COLORS = {
    "Renda Fixa":       "#2DD4BF",
    "Renda Variável":   "#4F8EF7",
    "Imóveis":          "#FBBF24",
    "Criptomoedas":     "#7C5CFC",
    "Internacional":    "#60A5FA",
    "Previdência":      "#34D399",
    "Emergência":       "#F472B6",
    "Outros":           "#8B90A8",
}


def apply_theme(root: tk.Tk):
    """Configure ttk styles for the whole application."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── General ──────────────────────────────────────────────────────────────
    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))

    # ── Frame / LabelFrame ────────────────────────────────────────────────────
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=SURFACE)
    style.configure("Surface2.TFrame", background=SURFACE2)

    style.configure("TLabelframe", background=SURFACE, foreground=TEXT_MUTED,
                    bordercolor=BORDER, lightcolor=SURFACE, darkcolor=SURFACE)
    style.configure("TLabelframe.Label", background=SURFACE, foreground=TEXT_MUTED,
                    font=("Segoe UI", 9, "bold"))

    # ── Label ─────────────────────────────────────────────────────────────────
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Card.TLabel", background=SURFACE, foreground=TEXT)
    style.configure("Muted.TLabel", background=BG, foreground=TEXT_MUTED,
                    font=("Segoe UI", 9))
    style.configure("CardMuted.TLabel", background=SURFACE, foreground=TEXT_MUTED,
                    font=("Segoe UI", 9))
    style.configure("Title.TLabel", background=BG, foreground=WHITE,
                    font=("Segoe UI", 22, "bold"))
    style.configure("CardTitle.TLabel", background=SURFACE, foreground=WHITE,
                    font=("Segoe UI", 13, "bold"))
    style.configure("Heading.TLabel", background=BG, foreground=WHITE,
                    font=("Segoe UI", 14, "bold"))
    style.configure("KPI.TLabel", background=SURFACE, foreground=WHITE,
                    font=("Segoe UI", 24, "bold"))
    style.configure("KPISmall.TLabel", background=SURFACE, foreground=TEXT_MUTED,
                    font=("Segoe UI", 10))
    style.configure("Success.TLabel", background=SURFACE, foreground=SUCCESS,
                    font=("Segoe UI", 11, "bold"))
    style.configure("Danger.TLabel", background=SURFACE, foreground=DANGER,
                    font=("Segoe UI", 11, "bold"))
    style.configure("Accent.TLabel", background=BG, foreground=ACCENT,
                    font=("Segoe UI", 10, "bold"))
    style.configure("SidebarTitle.TLabel", background=SURFACE2, foreground=WHITE,
                    font=("Segoe UI", 14, "bold"))
    style.configure("SidebarItem.TLabel", background=SURFACE2, foreground=TEXT_MUTED,
                    font=("Segoe UI", 10))
    style.configure("SidebarItemActive.TLabel", background=ACCENT, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"))

    # ── Button ────────────────────────────────────────────────────────────────
    style.configure("Primary.TButton",
                    background=ACCENT, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0, focusthickness=0, padding=(14, 6))
    style.map("Primary.TButton",
              background=[("active", "#3A75E0"), ("disabled", BORDER)],
              foreground=[("disabled", TEXT_MUTED)])

    style.configure("Danger.TButton",
                    background=DANGER, foreground=WHITE,
                    font=("Segoe UI", 10, "bold"),
                    borderwidth=0, focusthickness=0, padding=(14, 6))
    style.map("Danger.TButton",
              background=[("active", "#E05555")])

    style.configure("Ghost.TButton",
                    background=SURFACE2, foreground=TEXT,
                    font=("Segoe UI", 10),
                    borderwidth=0, focusthickness=0, padding=(14, 6))
    style.map("Ghost.TButton",
              background=[("active", BORDER)])

    # ── Entry ─────────────────────────────────────────────────────────────────
    style.configure("TEntry",
                    fieldbackground=SURFACE2, foreground=TEXT,
                    bordercolor=BORDER, insertcolor=TEXT,
                    padding=(8, 6))
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    # ── Combobox ──────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    fieldbackground=SURFACE2, foreground=TEXT,
                    background=SURFACE2, bordercolor=BORDER,
                    arrowcolor=TEXT_MUTED, padding=(8, 6))
    style.map("TCombobox",
              fieldbackground=[("readonly", SURFACE2)],
              foreground=[("readonly", TEXT)])

    # ── Treeview ─────────────────────────────────────────────────────────────
    style.configure("Treeview",
                    background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE,
                    bordercolor=BORDER, rowheight=32,
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
                    background=SURFACE2, foreground=TEXT_MUTED,
                    font=("Segoe UI", 9, "bold"),
                    bordercolor=BORDER, relief="flat")
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", WHITE)])
    style.map("Treeview.Heading",
              background=[("active", BORDER)])

    # ── Scrollbar ────────────────────────────────────────────────────────────
    style.configure("Vertical.TScrollbar",
                    background=SURFACE2, troughcolor=SURFACE,
                    bordercolor=SURFACE, arrowcolor=TEXT_MUTED,
                    relief="flat")
    style.configure("Horizontal.TScrollbar",
                    background=SURFACE2, troughcolor=SURFACE,
                    bordercolor=SURFACE, arrowcolor=TEXT_MUTED,
                    relief="flat")

    # ── Notebook ─────────────────────────────────────────────────────────────
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=SURFACE2, foreground=TEXT_MUTED,
                    font=("Segoe UI", 10),
                    padding=(16, 8))
    style.map("TNotebook.Tab",
              background=[("selected", SURFACE)],
              foreground=[("selected", WHITE)])

    # ── Separator ────────────────────────────────────────────────────────────
    style.configure("TSeparator", background=BORDER)

    # ── Progressbar ──────────────────────────────────────────────────────────
    style.configure("TProgressbar",
                    background=ACCENT, troughcolor=SURFACE2,
                    bordercolor=SURFACE2, lightcolor=ACCENT, darkcolor=ACCENT)

    # ── Spinbox ──────────────────────────────────────────────────────────────
    style.configure("TSpinbox",
                    fieldbackground=SURFACE2, foreground=TEXT,
                    bordercolor=BORDER, arrowcolor=TEXT_MUTED, padding=(8, 6))


def card_frame(parent, **kwargs):
    """Return a Surface-colored frame with rounded look."""
    f = ttk.Frame(parent, style="Card.TFrame", **kwargs)
    return f


def fmt_currency(value: float, symbol="R$") -> str:
    return f"{symbol} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"
