"""
Process Synchronization Page - Dining Philosophers
"""

import tkinter as tk
from tkinter import ttk
import math
import queue

from theme import (
    panel,
    BG_DARK, BG_PANEL, FG_TEXT, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_RED,
    FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
)
from synchronization import DiningPhilosophers, THINKING, HUNGRY, EATING

STATE_COLORS = {
    THINKING: ACCENT_GREEN,
    HUNGRY: ACCENT_ORANGE,
    EATING: ACCENT_RED,
}


class SynchronizationPage(tk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self.sim = None
        self.log_queue = queue.Queue()
        self._running = False

        self._build_layout()
        self._poll_log()

    # ------------------------------------------------------------------
    def _build_layout(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=16, pady=14)

        # Main row: visualization (left) + log (right)
        main_row = tk.Frame(content, bg=BG_DARK)
        main_row.pack(fill="both", expand=True)

        viz_panel = panel(main_row, padx=12, pady=10)
        viz_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        legend_row = tk.Frame(viz_panel, bg=BG_PANEL)
        legend_row.pack(anchor="e", fill="x")
        for label, color in [("Thinking", ACCENT_GREEN), ("Hungry", ACCENT_ORANGE), ("Eating", ACCENT_RED)]:
            box = tk.Frame(legend_row, bg=BG_PANEL)
            box.pack(side="left", padx=8)
            tk.Label(box, text="●", bg=BG_PANEL, fg=color, font=FONT_NORMAL).pack(side="left")
            tk.Label(box, text=f" {label}", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SMALL).pack(side="left")

        self.table_canvas = tk.Canvas(viz_panel, bg=BG_PANEL, highlightthickness=0, width=520, height=400)
        self.table_canvas.pack(fill="both", expand=True, pady=(6, 0))

        log_panel = panel(main_row, padx=12, pady=10, width=260)
        log_panel.pack(side="left", fill="y")
        tk.Label(log_panel, text="Log", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        self.log_text = tk.Text(log_panel, width=32, height=22, bg="#2a3447", fg=FG_TEXT,
                                 relief="flat", font=("Consolas", 9), insertbackground=FG_TEXT)
        self.log_text.pack(fill="both", expand=True, pady=(6, 0))
        self.log_text.tag_configure("hungry", foreground=ACCENT_ORANGE)
        self.log_text.tag_configure("eating", foreground=ACCENT_RED)
        self.log_text.tag_configure("thinking", foreground=ACCENT_GREEN)
        self.log_text.configure(state="disabled")

        # Controls row
        controls = tk.Frame(content, bg=BG_DARK)
        controls.pack(fill="x", pady=(10, 0))

        num_box = tk.Frame(controls, bg=BG_DARK)
        num_box.pack(side="left")
        tk.Label(num_box, text="Number of Philosophers", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.num_phil_var = tk.StringVar(value="5")
        ttk.Combobox(num_box, textvariable=self.num_phil_var, state="readonly", width=6,
                     values=["3", "4", "5", "6", "7", "8"]).pack(anchor="w")

        speed_box = tk.Frame(controls, bg=BG_DARK)
        speed_box.pack(side="left", padx=20, fill="x", expand=True)
        tk.Label(speed_box, text="Simulation Speed", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.speed_var = tk.DoubleVar(value=1.0)
        ttk.Scale(speed_box, from_=0.2, to=3.0, variable=self.speed_var, orient="horizontal").pack(fill="x")

        btn_box = tk.Frame(controls, bg=BG_DARK)
        btn_box.pack(side="left")
        self.start_btn = tk.Button(btn_box, text="Start", bg=ACCENT_GREEN, fg="white", relief="flat",
                                    padx=16, pady=6, command=self.start_sim, cursor="hand2")
        self.start_btn.pack(side="left", padx=4)
        self.pause_btn = tk.Button(btn_box, text="Pause", bg=ACCENT_ORANGE, fg="white", relief="flat",
                                    padx=16, pady=6, command=self.pause_sim, cursor="hand2")
        self.pause_btn.pack(side="left", padx=4)
        tk.Button(btn_box, text="Reset", bg="#374151", fg="white", relief="flat",
                  padx=16, pady=6, command=self.reset_sim, cursor="hand2").pack(side="left", padx=4)

        self._draw_table([THINKING] * int(self.num_phil_var.get()))

    # ------------------------------------------------------------------
    def start_sim(self):
        if self.sim and self._running:
            return

        if self.sim is None:
            n = int(self.num_phil_var.get())
            self.sim = DiningPhilosophers(num_philosophers=n, speed=self.speed_var.get(),
                                           log_callback=self._log_callback)
            self.sim.start()
        else:
            self.sim.resume()

        self._running = True
        self._animate()

    def pause_sim(self):
        if self.sim:
            self.sim.pause()
        self._running = False

    def reset_sim(self):
        if self.sim:
            self.sim.stop()
        self.sim = None
        self._running = False
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        n = int(self.num_phil_var.get())
        self._draw_table([THINKING] * n)

    # ------------------------------------------------------------------
    def _log_callback(self, message):
        self.log_queue.put(message)

    def _poll_log(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self._append_log(message)
        except queue.Empty:
            pass
        self.after(150, self._poll_log)

    def _append_log(self, message):
        self.log_text.configure(state="normal")
        tag = None
        if "Hungry" in message:
            tag = "hungry"
        elif "Eating" in message or "eating" in message:
            tag = "eating"
        elif "Thinking" in message:
            tag = "thinking"

        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    # ------------------------------------------------------------------
    def _animate(self):
        if self.sim and self._running:
            self._draw_table(self.sim.get_states())
            self.after(300, self._animate)

    def _draw_table(self, states):
        canvas = self.table_canvas
        canvas.delete("all")
        canvas.update_idletasks()
        w = canvas.winfo_width() or 520
        h = canvas.winfo_height() or 400

        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 70
        n = len(states)

        # central table
        canvas.create_oval(cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4,
                            fill="#374151", outline=BG_PANEL)

        for i, state in enumerate(states):
            angle = -math.pi / 2 + 2 * math.pi * i / n
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)

            color = STATE_COLORS.get(state, "#6b7280")
            canvas.create_oval(x - 26, y - 26, x + 26, y + 26, fill=color, outline=BG_PANEL, width=2)
            canvas.create_text(x, y, text=f"P{i + 1}", fill="white", font=("Segoe UI", 10, "bold"))
            canvas.create_text(x, y + 40, text=state, fill=FG_TEXT, font=FONT_SMALL)

            # fork between this philosopher and the next
            angle2 = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
            fx = cx + (r * 0.65) * math.cos(angle2)
            fy = cy + (r * 0.65) * math.sin(angle2)
            canvas.create_text(fx, fy, text="🍴", font=("Segoe UI", 14))

    # ------------------------------------------------------------------
    def on_show(self):
        """Called when this page is raised; redraw to fit current canvas size."""
        self._draw_table(self.sim.get_states() if self.sim else [THINKING] * int(self.num_phil_var.get()))
