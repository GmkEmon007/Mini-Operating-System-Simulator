"""
Dashboard Page
"""

import tkinter as tk
from tkinter import ttk
import random

from theme import (
    make_card, panel,
    BG_DARK, BG_PANEL, FG_TEXT, FG_MUTED, ACCENT_GREEN, ACCENT_ORANGE,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
)


def draw_line_chart(canvas, values, width, height, color="#3b82f6"):
    canvas.delete("all")
    if len(values) < 2:
        return
    pad = 24
    max_v = max(values) if max(values) > 0 else 1
    min_v = min(values)
    span = max(max_v - min_v, 1)

    points = []
    for i, v in enumerate(values):
        x = pad + i * (width - 2 * pad) / (len(values) - 1)
        y = height - pad - (v - min_v) / span * (height - 2 * pad)
        points.append((x, y))

    for frac, label in [(0, "0%"), (0.5, "50%"), (1, "100%")]:
        y = height - pad - frac * (height - 2 * pad)
        canvas.create_line(pad, y, width - pad, y, fill="#374151", dash=(2, 2))
        canvas.create_text(8, y, text=label, fill="#9aa5b6", font=("Segoe UI", 7), anchor="w")

    for i in range(len(points) - 1):
        canvas.create_line(*points[i], *points[i + 1], fill=color, width=2, smooth=True)


def draw_pie_chart(canvas, data, width, height):
    """data: list of (label, value, color)"""
    canvas.delete("all")
    total = sum(v for _, v, _ in data)
    if total == 0:
        return

    cx, cy = width // 2 - 10, height // 2
    r = min(width, height) // 2 - 10

    start_angle = 0
    for label, value, color in data:
        extent = 360 * value / total
        canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                           start=start_angle, extent=extent, fill=color, outline=BG_PANEL, width=2)
        start_angle += extent


class DashboardPage(tk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self._build_layout()
        self._animate_chart()

    def _build_layout(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(content, text="Dashboard", bg=BG_DARK, fg=FG_TEXT, font=FONT_TITLE).pack(anchor="w", pady=(0, 12))

        # Summary cards
        cards_row = tk.Frame(content, bg=BG_DARK)
        cards_row.pack(fill="x")

        make_card(cards_row, "5", "Total Processes", "blue").pack(side="left", padx=(0, 10), fill="x", expand=True)
        make_card(cards_row, "2", "Running Processes", "green").pack(side="left", padx=10, fill="x", expand=True)
        make_card(cards_row, "3", "Waiting Processes", "orange").pack(side="left", padx=10, fill="x", expand=True)
        make_card(cards_row, "65%", "CPU Utilization", "purple").pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Charts row
        charts_row = tk.Frame(content, bg=BG_DARK)
        charts_row.pack(fill="both", expand=False, pady=14)

        cpu_panel = panel(charts_row, padx=12, pady=10)
        cpu_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(cpu_panel, text="CPU Utilization", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")
        self.cpu_canvas = tk.Canvas(cpu_panel, width=420, height=140, bg=BG_PANEL, highlightthickness=0)
        self.cpu_canvas.pack(pady=6)
        tk.Label(cpu_panel, text="Time (s)", bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL).pack()

        status_panel = panel(charts_row, padx=12, pady=10)
        status_panel.pack(side="left", fill="both", expand=True)
        tk.Label(status_panel, text="Process Status", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        pie_row = tk.Frame(status_panel, bg=BG_PANEL)
        pie_row.pack(fill="x", pady=6)
        self.pie_canvas = tk.Canvas(pie_row, width=140, height=130, bg=BG_PANEL, highlightthickness=0)
        self.pie_canvas.pack(side="left")

        legend = tk.Frame(pie_row, bg=BG_PANEL)
        legend.pack(side="left", padx=20, anchor="center")
        for label, color, count in [("Running (2)", ACCENT_GREEN, 2),
                                     ("Waiting (3)", ACCENT_ORANGE, 3),
                                     ("Terminated (0)", "#6b7280", 0)]:
            row = tk.Frame(legend, bg=BG_PANEL)
            row.pack(anchor="w", pady=2)
            tk.Label(row, text="●", bg=BG_PANEL, fg=color, font=FONT_NORMAL).pack(side="left")
            tk.Label(row, text=f" {label}", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SMALL).pack(side="left")

        draw_pie_chart(self.pie_canvas, [("Running", 2, ACCENT_GREEN),
                                          ("Waiting", 3, ACCENT_ORANGE),
                                          ("Terminated", 0.001, "#6b7280")], 140, 130)

        # Recent processes table
        table_panel = panel(content, padx=12, pady=10)
        table_panel.pack(fill="both", expand=True)
        tk.Label(table_panel, text="Recent Processes", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        columns = ("pid", "name", "status", "arrival", "burst", "priority")
        headings = ["PID", "Process Name", "Status", "Arrival Time", "Burst Time", "Priority"]
        tree = ttk.Treeview(table_panel, columns=columns, show="headings", height=5)
        for col, head in zip(columns, headings):
            tree.heading(col, text=head)
            tree.column(col, anchor="center", width=120)
        tree.pack(fill="both", expand=True, pady=(6, 0))

        sample = [
            ("P1", "Process 1", "Running", 0, 10, 2),
            ("P2", "Process 2", "Waiting", 1, 5, 1),
            ("P3", "Process 3", "Running", 2, 8, 3),
            ("P4", "Process 4", "Waiting", 3, 6, 2),
            ("P5", "Process 5", "Waiting", 4, 4, 1),
        ]
        for row in sample:
            tree.insert("", "end", values=row)

    def _animate_chart(self):
        if not hasattr(self, "_cpu_history"):
            self._cpu_history = [random.randint(30, 90) for _ in range(20)]

        self._cpu_history.append(max(10, min(100, self._cpu_history[-1] + random.randint(-15, 15))))
        self._cpu_history = self._cpu_history[-20:]

        draw_line_chart(self.cpu_canvas, self._cpu_history, 420, 140)
        self.after(1500, self._animate_chart)
