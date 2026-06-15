"""
Shared dark theme constants and helper functions/widgets for the
Mini OS Simulator (Tkinter).
"""

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Color palette (inspired by the dashboard mockup)
# ---------------------------------------------------------------------------
BG_DARK = "#1b2330"        # main background
BG_PANEL = "#232c3d"       # card / panel background
BG_SIDEBAR = "#1b2330"     # sidebar background
BG_SIDEBAR_ACTIVE = "#2f3b52"
FG_TEXT = "#e6e9ef"
FG_MUTED = "#9aa5b6"

ACCENT_BLUE = "#3b82f6"
ACCENT_GREEN = "#22c55e"
ACCENT_ORANGE = "#f59e0b"
ACCENT_PURPLE = "#a855f7"
ACCENT_RED = "#ef4444"

CARD_COLORS = {
    "blue": "#2563eb",
    "green": "#16a34a",
    "orange": "#ea580c",
    "purple": "#9333ea",
}

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SUBTITLE = ("Segoe UI", 11, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BIG_NUM = ("Segoe UI", 22, "bold")


def apply_dark_style(root):
    """Configure ttk styles for a dark theme. Call once on the root window."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=BG_DARK)

    style.configure("TFrame", background=BG_DARK)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("Sidebar.TFrame", background=BG_SIDEBAR)

    style.configure("TLabel", background=BG_DARK, foreground=FG_TEXT, font=FONT_NORMAL)
    style.configure("Panel.TLabel", background=BG_PANEL, foreground=FG_TEXT, font=FONT_NORMAL)
    style.configure("Muted.TLabel", background=BG_DARK, foreground=FG_MUTED, font=FONT_SMALL)
    style.configure("PanelMuted.TLabel", background=BG_PANEL, foreground=FG_MUTED, font=FONT_SMALL)
    style.configure("Title.TLabel", background=BG_DARK, foreground=FG_TEXT, font=FONT_TITLE)
    style.configure("PanelTitle.TLabel", background=BG_PANEL, foreground=FG_TEXT, font=FONT_SUBTITLE)
    style.configure("Sidebar.TLabel", background=BG_SIDEBAR, foreground=FG_TEXT, font=FONT_NORMAL)
    style.configure("BigNum.TLabel", background=BG_PANEL, foreground="white", font=FONT_BIG_NUM)

    style.configure("TButton", font=FONT_NORMAL, padding=6)
    style.configure("Accent.TButton", background=ACCENT_BLUE, foreground="white")
    style.map("Accent.TButton", background=[("active", "#2563eb")])

    style.configure("Success.TButton", background=ACCENT_GREEN, foreground="white")
    style.map("Success.TButton", background=[("active", "#16a34a")])

    style.configure("Danger.TButton", background=ACCENT_RED, foreground="white")
    style.map("Danger.TButton", background=[("active", "#dc2626")])

    style.configure("Warning.TButton", background=ACCENT_ORANGE, foreground="white")
    style.map("Warning.TButton", background=[("active", "#d97706")])

    style.configure("TEntry", fieldbackground="#2a3447", foreground=FG_TEXT,
                     insertcolor=FG_TEXT, borderwidth=0)
    style.configure("TCombobox", fieldbackground="#2a3447", background="#2a3447",
                     foreground=FG_TEXT, arrowcolor=FG_TEXT)
    style.map("TCombobox", fieldbackground=[("readonly", "#2a3447")],
              foreground=[("readonly", FG_TEXT)])

    style.configure("Treeview", background="#2a3447", fieldbackground="#2a3447",
                     foreground=FG_TEXT, rowheight=24, font=FONT_SMALL)
    style.configure("Treeview.Heading", background="#1f2937", foreground=FG_TEXT,
                     font=FONT_SUBTITLE)
    style.map("Treeview", background=[("selected", ACCENT_BLUE)])

    style.configure("TNotebook", background=BG_DARK, borderwidth=0)
    style.configure("TNotebook.Tab", background="#1f2937", foreground=FG_TEXT,
                     padding=(12, 6), font=FONT_NORMAL)
    style.map("TNotebook.Tab", background=[("selected", BG_PANEL)],
              foreground=[("selected", "white")])

    style.configure("Horizontal.TScale", background=BG_PANEL)
    style.configure("TScrollbar", background="#2a3447", troughcolor=BG_DARK)

    return style


def make_card(parent, value_text, label_text, color_key, detail_text="View Details"):
    """Create a colored summary card (used on the dashboard)."""
    color = CARD_COLORS.get(color_key, ACCENT_BLUE)
    card = tk.Frame(parent, bg=color, padx=14, pady=10)
    tk.Label(card, text=value_text, bg=color, fg="white", font=FONT_BIG_NUM).pack(anchor="w")
    tk.Label(card, text=label_text, bg=color, fg="white", font=FONT_NORMAL).pack(anchor="w")
    tk.Label(card, text=detail_text, bg=color, fg="#e5e7eb", font=FONT_SMALL).pack(anchor="w", pady=(6, 0))
    return card


def panel(parent, **kwargs):
    """Create a panel/card frame with the panel background color."""
    f = tk.Frame(parent, bg=BG_PANEL, **kwargs)
    return f


class Sidebar(tk.Frame):
    """
    Reusable left navigation sidebar.
    items: list of (key, label) tuples
    on_select: callback(key) when an item is clicked
    active_key: currently highlighted item key
    """

    def __init__(self, parent, items, on_select=None, active_key=None, footer_text=None):
        super().__init__(parent, bg=BG_SIDEBAR, width=190)
        self.items = items
        self.on_select = on_select
        self.active_key = active_key
        self.buttons = {}

        for key, label in items:
            btn = tk.Label(self, text=f"  {label}", anchor="w", bg=BG_SIDEBAR, fg=FG_TEXT,
                            font=FONT_NORMAL, padx=12, pady=8, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, k=key: self._handle_click(k))
            self.buttons[key] = btn

        if footer_text:
            spacer = tk.Frame(self, bg=BG_SIDEBAR)
            spacer.pack(fill="both", expand=True)
            footer = tk.Frame(self, bg=BG_SIDEBAR)
            footer.pack(fill="x", pady=10)
            tk.Label(footer, text="●", bg=BG_SIDEBAR, fg=ACCENT_GREEN, font=FONT_NORMAL).pack(side="left", padx=(12, 4))
            tk.Label(footer, text=footer_text, bg=BG_SIDEBAR, fg=FG_MUTED, font=FONT_SMALL).pack(side="left")

        self._refresh_highlight()

    def _handle_click(self, key):
        self.active_key = key
        self._refresh_highlight()
        if self.on_select:
            self.on_select(key)

    def _refresh_highlight(self):
        for key, btn in self.buttons.items():
            if key == self.active_key:
                btn.configure(bg=BG_SIDEBAR_ACTIVE, fg="white")
            else:
                btn.configure(bg=BG_SIDEBAR, fg=FG_TEXT)


# Standard module list used across module windows for sidebar navigation
MODULE_LIST = [
    ("dashboard", "📊  Dashboard"),
    ("cpu", "🖥️  CPU Scheduling"),
    ("memory", "💾  Memory Management"),
    ("sync", "🔄  Process Synchronization"),
    ("deadlock", "⚠️  Deadlock Handling"),
    ("file", "📁  File Management"),
]
