"""
CPU Scheduling Page - Gantt Chart
"""

import tkinter as tk
from tkinter import ttk, messagebox

import scheduling
from theme import (
    panel,
    BG_DARK, BG_PANEL, FG_TEXT, FG_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED,
    FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
)

GANTT_COLORS = ["#3b82f6", "#22c55e", "#ef4444", "#f59e0b", "#a855f7",
                "#06b6d4", "#eab308", "#a8a29e", "#64748b", "#ec4899"]


class CPUSchedulingPage(tk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self._build_layout()
        self.run_simulation()

    # ------------------------------------------------------------------
    def _build_layout(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=16, pady=14)

        # Top bar: Algorithm + Time Quantum + Run button
        top_bar = tk.Frame(content, bg=BG_DARK)
        top_bar.pack(fill="x", pady=(0, 12))

        algo_box = tk.Frame(top_bar, bg=BG_DARK)
        algo_box.pack(side="left")
        tk.Label(algo_box, text="Algorithm", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.algo_var = tk.StringVar(value="Round Robin")
        algo_combo = ttk.Combobox(algo_box, textvariable=self.algo_var, state="readonly", width=18,
                                   values=["FCFS", "SJF", "Round Robin", "Priority"])
        algo_combo.pack(anchor="w")
        algo_combo.bind("<<ComboboxSelected>>", lambda e: self._on_algo_change())

        quantum_box = tk.Frame(top_bar, bg=BG_DARK)
        quantum_box.pack(side="left", padx=20)
        tk.Label(quantum_box, text="Time Quantum", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.quantum_var = tk.StringVar(value="2")
        self.quantum_entry = ttk.Entry(quantum_box, textvariable=self.quantum_var, width=8)
        self.quantum_entry.pack(anchor="w")

        run_btn = tk.Button(top_bar, text="Run", bg=ACCENT_BLUE, fg="white", font=FONT_NORMAL,
                             relief="flat", padx=20, pady=6, command=self.run_simulation, cursor="hand2")
        run_btn.pack(side="right")

        # Two-column layout: process table (left), gantt+metrics (right)
        main_row = tk.Frame(content, bg=BG_DARK)
        main_row.pack(fill="both", expand=True)

        # ---- Left: Process table panel ----
        left_panel = panel(main_row, padx=12, pady=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left_panel, text="Process Table", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        columns = ("pid", "arrival", "burst", "priority")
        headings = ["PID", "Arrival Time", "Burst Time", "Priority"]
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings", height=8)
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, anchor="center", width=90)
        self.tree.pack(fill="both", expand=True, pady=(6, 8))
        self.tree.bind("<Double-1>", self._edit_cell)

        default_procs = [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 2},
            {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
            {"pid": "P3", "arrival": 2, "burst": 8, "priority": 3},
            {"pid": "P4", "arrival": 3, "burst": 6, "priority": 2},
            {"pid": "P5", "arrival": 4, "burst": 4, "priority": 1},
        ]
        for p in default_procs:
            self._insert_process(p)

        btn_row = tk.Frame(left_panel, bg=BG_PANEL)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="Add Process", bg=ACCENT_GREEN, fg="white", relief="flat",
                  padx=10, pady=4, command=self.add_process, cursor="hand2").pack(side="left", padx=(0, 6))
        tk.Button(btn_row, text="Remove", bg=ACCENT_RED, fg="white", relief="flat",
                  padx=10, pady=4, command=self.remove_process, cursor="hand2").pack(side="left", padx=6)
        tk.Button(btn_row, text="Reset", bg="#374151", fg="white", relief="flat",
                  padx=10, pady=4, command=self.reset_processes, cursor="hand2").pack(side="left", padx=6)

        tk.Label(left_panel, text="Tip: double-click a cell to edit its value.",
                 bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL).pack(anchor="w", pady=(6, 0))

        # ---- Right: Gantt chart + metrics ----
        right_panel = tk.Frame(main_row, bg=BG_DARK)
        right_panel.pack(side="left", fill="both", expand=True)

        gantt_panel = panel(right_panel, padx=12, pady=10)
        gantt_panel.pack(fill="x")
        tk.Label(gantt_panel, text="Gantt Chart", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        self.gantt_canvas = tk.Canvas(gantt_panel, height=70, bg=BG_PANEL, highlightthickness=0)
        hbar = ttk.Scrollbar(gantt_panel, orient="horizontal", command=self.gantt_canvas.xview)
        self.gantt_canvas.configure(xscrollcommand=hbar.set)
        self.gantt_canvas.pack(fill="x", pady=(6, 0))
        hbar.pack(fill="x")

        metrics_panel = panel(right_panel, padx=12, pady=10)
        metrics_panel.pack(fill="both", expand=True, pady=(10, 0))
        tk.Label(metrics_panel, text="Metrics", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        self.metrics_frame = tk.Frame(metrics_panel, bg=BG_PANEL)
        self.metrics_frame.pack(fill="x", pady=(8, 0), anchor="w")

        self.metric_labels = {}
        for key, label in [("avg_wt", "Average Waiting Time"),
                            ("avg_tat", "Average Turnaround Time"),
                            ("cpu_util", "CPU Utilization"),
                            ("throughput", "Throughput")]:
            row = tk.Frame(self.metrics_frame, bg=BG_PANEL)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=BG_PANEL, fg=FG_MUTED, font=FONT_NORMAL, width=24, anchor="w").pack(side="left")
            val = tk.Label(row, text="--", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE, anchor="e")
            val.pack(side="left")
            self.metric_labels[key] = val

        self._on_algo_change()

    # ------------------------------------------------------------------
    def _on_algo_change(self):
        if self.algo_var.get() == "Round Robin":
            self.quantum_entry.configure(state="normal")
        else:
            self.quantum_entry.configure(state="disabled")

    # ------------------------------------------------------------------
    def _insert_process(self, p):
        self.tree.insert("", "end", values=(p["pid"], p["arrival"], p["burst"], p["priority"]))

    def add_process(self):
        n = len(self.tree.get_children()) + 1
        self._insert_process({"pid": f"P{n}", "arrival": 0, "burst": 1, "priority": 1})

    def remove_process(self):
        sel = self.tree.selection()
        if sel:
            self.tree.delete(sel[0])
        else:
            children = self.tree.get_children()
            if children:
                self.tree.delete(children[-1])

    def reset_processes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        default_procs = [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 2},
            {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
            {"pid": "P3", "arrival": 2, "burst": 8, "priority": 3},
            {"pid": "P4", "arrival": 3, "burst": 6, "priority": 2},
            {"pid": "P5", "arrival": 4, "burst": 4, "priority": 1},
        ]
        for p in default_procs:
            self._insert_process(p)
        self.run_simulation()

    def _edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace("#", "")) - 1
        col_name = self.tree["columns"][col_index]

        x, y, w, h = self.tree.bbox(item, column)
        value = self.tree.set(item, col_name)

        edit_var = tk.StringVar(value=value)
        entry = ttk.Entry(self.tree, textvariable=edit_var)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus()
        entry.select_range(0, tk.END)

        def save_edit(event=None):
            new_val = edit_var.get()
            if col_name != "pid":
                try:
                    new_val = int(new_val)
                except ValueError:
                    new_val = value
            self.tree.set(item, col_name, new_val)
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    # ------------------------------------------------------------------
    def _read_processes(self):
        processes = []
        for item in self.tree.get_children():
            pid, arrival, burst, priority = self.tree.item(item, "values")
            try:
                processes.append({
                    "pid": str(pid),
                    "arrival": int(arrival),
                    "burst": int(burst),
                    "priority": int(priority),
                })
            except ValueError:
                raise ValueError(f"Invalid numeric value in row for {pid}")
        return processes

    # ------------------------------------------------------------------
    def run_simulation(self):
        try:
            processes = self._read_processes()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        if not processes:
            messagebox.showerror("Input Error", "Add at least one process.")
            return

        algo = self.algo_var.get()
        if algo == "FCFS":
            gantt, result = scheduling.fcfs(processes)
        elif algo == "SJF":
            gantt, result = scheduling.sjf_non_preemptive(processes)
        elif algo == "Round Robin":
            try:
                q = int(self.quantum_var.get())
                if q <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error", "Time quantum must be a positive integer.")
                return
            gantt, result = scheduling.round_robin(processes, q)
        elif algo == "Priority":
            gantt, result = scheduling.priority_scheduling(processes)
        else:
            return

        self._draw_gantt(gantt)

        avg_wt, avg_tat = scheduling.calculate_averages(result)
        total_time = gantt[-1][2] if gantt else 1
        busy_time = sum(end - start for _, start, end in gantt)
        cpu_util = busy_time / total_time * 100 if total_time else 0
        throughput = len(processes) / total_time if total_time else 0

        self.metric_labels["avg_wt"].configure(text=f"{avg_wt:.2f}")
        self.metric_labels["avg_tat"].configure(text=f"{avg_tat:.2f}")
        self.metric_labels["cpu_util"].configure(text=f"{cpu_util:.2f}%")
        self.metric_labels["throughput"].configure(text=f"{throughput:.2f} process/unit time")

    def _draw_gantt(self, gantt):
        self.gantt_canvas.delete("all")
        if not gantt:
            return

        scale = 30
        x = 10
        y_top = 8
        height = 40
        color_map = {}

        for pid, start, end in gantt:
            width = (end - start) * scale
            if pid not in color_map:
                color_map[pid] = GANTT_COLORS[len(color_map) % len(GANTT_COLORS)]
            self.gantt_canvas.create_rectangle(x, y_top, x + width, y_top + height,
                                                fill=color_map[pid], outline=BG_PANEL, width=2)
            self.gantt_canvas.create_text(x + width / 2, y_top + height / 2, text=str(pid),
                                           fill="white", font=FONT_NORMAL)
            self.gantt_canvas.create_text(x, y_top + height + 10, text=str(start),
                                           fill=FG_MUTED, font=FONT_SMALL)
            x += width

        self.gantt_canvas.create_text(x, y_top + height + 10, text=str(gantt[-1][2]),
                                       fill=FG_MUTED, font=FONT_SMALL)
        self.gantt_canvas.configure(scrollregion=(0, 0, x + 30, y_top + height + 20))
