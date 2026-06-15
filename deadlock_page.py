"""
Deadlock Handling Page - Banker's Algorithm
"""

import tkinter as tk
from tkinter import ttk, messagebox

import deadlock
from theme import (
    panel,
    BG_DARK, BG_PANEL, FG_TEXT, FG_MUTED, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED,
    FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
)

DEFAULT_MAX = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
DEFAULT_ALLOC = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
DEFAULT_AVAILABLE = [3, 3, 2]
DEFAULT_TOTAL = [10, 5, 7]
RESOURCE_LABELS = ["A", "B", "C"]


class DeadlockPage(tk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self.n = len(DEFAULT_MAX)
        self.m = len(DEFAULT_MAX[0])

        self._build_layout()
        self.check_safe_state()

    # ------------------------------------------------------------------
    def _build_layout(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=16, pady=14)

        main_row = tk.Frame(content, bg=BG_DARK)
        main_row.pack(fill="both", expand=True)

        # ---- Left: Available resources ----
        avail_panel = panel(main_row, padx=12, pady=10, width=200)
        avail_panel.pack(side="left", fill="y", padx=(0, 10))
        tk.Label(avail_panel, text="Available Resources", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        avail_table = tk.Frame(avail_panel, bg=BG_PANEL)
        avail_table.pack(fill="x", pady=(8, 0))
        for col, head in enumerate(["Resource", "Total", "Available"]):
            tk.Label(avail_table, text=head, bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 9, "bold"), width=9).grid(row=0, column=col, padx=2, pady=2)

        self.available_entries = []
        for i, label in enumerate(RESOURCE_LABELS):
            tk.Label(avail_table, text=label, bg=BG_PANEL, fg=FG_TEXT, font=FONT_NORMAL, width=9).grid(row=i + 1, column=0)
            tk.Label(avail_table, text=str(DEFAULT_TOTAL[i]), bg=BG_PANEL, fg=FG_TEXT, font=FONT_NORMAL, width=9).grid(row=i + 1, column=1)
            var = tk.StringVar(value=str(DEFAULT_AVAILABLE[i]))
            entry = ttk.Entry(avail_table, textvariable=var, width=7)
            entry.grid(row=i + 1, column=2, padx=2, pady=2)
            self.available_entries.append(var)

        # ---- Right: Process table (Max / Allocation / Need) ----
        table_panel = panel(main_row, padx=12, pady=10)
        table_panel.pack(side="left", fill="both", expand=True)
        tk.Label(table_panel, text="Process Table", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        grid = tk.Frame(table_panel, bg=BG_PANEL)
        grid.pack(fill="x", pady=(8, 0))

        # Header row
        tk.Label(grid, text="Process", bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 9, "bold"), width=8).grid(row=0, column=0, rowspan=2)
        col = 1
        for group in ["Max", "Allocation", "Need"]:
            tk.Label(grid, text=group, bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=col, columnspan=self.m)
            for j in range(self.m):
                tk.Label(grid, text=RESOURCE_LABELS[j], bg=BG_PANEL, fg=FG_MUTED, font=("Segoe UI", 8)).grid(row=1, column=col + j)
            col += self.m

        self.max_entries = []
        self.alloc_entries = []
        self.need_labels = []

        for i in range(self.n):
            r = i + 2
            tk.Label(grid, text=f"P{i}", bg=BG_PANEL, fg=FG_TEXT, font=FONT_NORMAL, width=8).grid(row=r, column=0)

            max_row = []
            for j in range(self.m):
                var = tk.StringVar(value=str(DEFAULT_MAX[i][j]))
                entry = ttk.Entry(grid, textvariable=var, width=4)
                entry.grid(row=r, column=1 + j, padx=1, pady=1)
                max_row.append(var)
            self.max_entries.append(max_row)

            alloc_row = []
            for j in range(self.m):
                var = tk.StringVar(value=str(DEFAULT_ALLOC[i][j]))
                entry = ttk.Entry(grid, textvariable=var, width=4)
                entry.grid(row=r, column=1 + self.m + j, padx=1, pady=1)
                alloc_row.append(var)
            self.alloc_entries.append(alloc_row)

            need_row = []
            for j in range(self.m):
                need_val = DEFAULT_MAX[i][j] - DEFAULT_ALLOC[i][j]
                lbl = tk.Label(grid, text=str(need_val), bg="#2a3447", fg=FG_TEXT, font=FONT_NORMAL, width=4)
                lbl.grid(row=r, column=1 + 2 * self.m + j, padx=1, pady=1)
                need_row.append(lbl)
            self.need_labels.append(need_row)

        # ---- Bottom: safe sequence result ----
        result_panel = panel(content, padx=12, pady=10)
        result_panel.pack(fill="x", pady=(10, 0))
        tk.Label(result_panel, text="Safe Sequence", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        result_row = tk.Frame(result_panel, bg=BG_PANEL)
        result_row.pack(fill="x", pady=(8, 0))

        self.seq_label = tk.Label(result_row, text="", bg=BG_PANEL, fg=FG_TEXT, font=("Segoe UI", 11, "bold"))
        self.seq_label.pack(side="left")

        self.status_label = tk.Label(result_row, text="", bg=BG_PANEL, fg=ACCENT_GREEN, font=("Segoe UI", 10, "bold"))
        self.status_label.pack(side="right")

        btn_row = tk.Frame(result_panel, bg=BG_PANEL)
        btn_row.pack(fill="x", pady=(10, 0))
        tk.Button(btn_row, text="Check Safe State", bg=ACCENT_BLUE, fg="white", relief="flat",
                  padx=16, pady=6, command=self.check_safe_state, cursor="hand2").pack(side="left")
        tk.Button(btn_row, text="Reset", bg="#374151", fg="white", relief="flat",
                  padx=16, pady=6, command=self.reset_defaults, cursor="hand2").pack(side="left", padx=8)

        # ---- Request simulation ----
        req_panel = panel(content, padx=12, pady=10)
        req_panel.pack(fill="x", pady=(10, 0))
        tk.Label(req_panel, text="Resource Request Simulation", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        req_row = tk.Frame(req_panel, bg=BG_PANEL)
        req_row.pack(fill="x", pady=(8, 0))

        tk.Label(req_row, text="Process ID (0-indexed)", bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL).grid(row=0, column=0, sticky="w")
        self.req_pid_var = tk.StringVar(value="1")
        ttk.Entry(req_row, textvariable=self.req_pid_var, width=6).grid(row=1, column=0, sticky="w", padx=(0, 12))

        tk.Label(req_row, text=f"Request Vector ({','.join(RESOURCE_LABELS)})", bg=BG_PANEL, fg=FG_MUTED, font=FONT_SMALL).grid(row=0, column=1, sticky="w")
        self.req_vector_var = tk.StringVar(value="1,0,2")
        ttk.Entry(req_row, textvariable=self.req_vector_var, width=12).grid(row=1, column=1, sticky="w", padx=(0, 12))

        tk.Button(req_row, text="Submit Request", bg=ACCENT_GREEN, fg="white", relief="flat",
                  padx=16, pady=6, command=self.submit_request, cursor="hand2").grid(row=1, column=2, padx=8)

        self.req_result_label = tk.Label(req_panel, text="", bg=BG_PANEL, fg=FG_TEXT, font=FONT_NORMAL,
                                          wraplength=750, justify="left")
        self.req_result_label.pack(anchor="w", pady=(8, 0))

    # ------------------------------------------------------------------
    def _read_matrices(self):
        max_matrix = [[int(v.get()) for v in row] for row in self.max_entries]
        alloc_matrix = [[int(v.get()) for v in row] for row in self.alloc_entries]
        available = [int(v.get()) for v in self.available_entries]
        return max_matrix, alloc_matrix, available

    def _update_need_labels(self, max_matrix, alloc_matrix):
        need = deadlock.calculate_need(max_matrix, alloc_matrix)
        for i in range(self.n):
            for j in range(self.m):
                self.need_labels[i][j].configure(text=str(need[i][j]))

    # ------------------------------------------------------------------
    def check_safe_state(self):
        try:
            max_matrix, alloc_matrix, available = self._read_matrices()
        except ValueError:
            messagebox.showerror("Input Error", "All matrix and availability values must be integers.")
            return

        self._update_need_labels(max_matrix, alloc_matrix)

        safe, sequence = deadlock.is_safe_state(available, max_matrix, alloc_matrix)

        if safe:
            seq_str = "  →  ".join(f"P{i}" for i in sequence)
            self.seq_label.configure(text=seq_str)
            self.status_label.configure(text="✓  System is in Safe State", fg=ACCENT_GREEN)
        else:
            self.seq_label.configure(text="No safe sequence found")
            self.status_label.configure(text="✗  Deadlock Detected (Unsafe State)", fg=ACCENT_RED)

    def reset_defaults(self):
        for i in range(self.n):
            for j in range(self.m):
                self.max_entries[i][j].set(str(DEFAULT_MAX[i][j]))
                self.alloc_entries[i][j].set(str(DEFAULT_ALLOC[i][j]))
        for j in range(self.m):
            self.available_entries[j].set(str(DEFAULT_AVAILABLE[j]))
        self.req_result_label.configure(text="")
        self.check_safe_state()

    def submit_request(self):
        try:
            max_matrix, alloc_matrix, available = self._read_matrices()
            pid = int(self.req_pid_var.get())
            request = [int(x.strip()) for x in self.req_vector_var.get().split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Input Error", "All values must be integers.")
            return

        if not (0 <= pid < self.n):
            messagebox.showerror("Input Error", "Invalid process ID.")
            return
        if len(request) != self.m:
            messagebox.showerror("Input Error", f"Request vector must have {self.m} values ({','.join(RESOURCE_LABELS)}).")
            return

        granted, message, new_avail, new_alloc, sequence = deadlock.request_resources(
            pid, request, available, max_matrix, alloc_matrix)

        if granted:
            for i in range(self.n):
                for j in range(self.m):
                    self.alloc_entries[i][j].set(str(new_alloc[i][j]))
            for j in range(self.m):
                self.available_entries[j].set(str(new_avail[j]))
            self._update_need_labels(max_matrix, new_alloc)

            seq_str = "  →  ".join(f"P{i}" for i in sequence)
            self.seq_label.configure(text=seq_str)
            self.status_label.configure(text="✓  System is in Safe State", fg=ACCENT_GREEN)
            self.req_result_label.configure(
                text=f"Request from P{pid} = {request}: GRANTED. {message}",
                fg=ACCENT_GREEN)
        else:
            self.req_result_label.configure(
                text=f"Request from P{pid} = {request}: DENIED. {message}",
                fg=ACCENT_RED)
