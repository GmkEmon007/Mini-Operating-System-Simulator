"""
Memory Management Page - Paging + Block Allocation
"""

import tkinter as tk
from tkinter import ttk, messagebox

import memory
import page_replacement
from theme import (
    panel,
    BG_DARK, BG_PANEL, FG_TEXT, FG_MUTED, ACCENT_BLUE,
    FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
)

FRAME_COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#a855f7", "#ec4899",
                "#06b6d4", "#eab308", "#64748b"]


class MemoryManagementPage(tk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self._build_layout()
        self.run_paging()

    # ------------------------------------------------------------------
    def _build_layout(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=16, pady=14)

        notebook = ttk.Notebook(content)
        notebook.pack(fill="both", expand=True)

        paging_tab = tk.Frame(notebook, bg=BG_DARK)
        allocation_tab = tk.Frame(notebook, bg=BG_DARK)
        notebook.add(paging_tab, text="Paging / Page Replacement")
        notebook.add(allocation_tab, text="Block Allocation (Fit Strategies)")

        self._build_paging_tab(paging_tab)
        self._build_allocation_tab(allocation_tab)

    # ------------------------------------------------------------------
    # Paging tab
    # ------------------------------------------------------------------
    def _build_paging_tab(self, parent):
        top_bar = tk.Frame(parent, bg=BG_DARK)
        top_bar.pack(fill="x", pady=(10, 12))

        frames_box = tk.Frame(top_bar, bg=BG_DARK)
        frames_box.pack(side="left")
        tk.Label(frames_box, text="Total Frames", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.frames_var = tk.StringVar(value="8")
        ttk.Entry(frames_box, textvariable=self.frames_var, width=8).pack(anchor="w")

        algo_box = tk.Frame(top_bar, bg=BG_DARK)
        algo_box.pack(side="left", padx=20)
        tk.Label(algo_box, text="Page Replacement", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.algo_var = tk.StringVar(value="LRU")
        ttk.Combobox(algo_box, textvariable=self.algo_var, state="readonly", width=12,
                     values=["FIFO", "LRU", "Optimal"]).pack(anchor="w")

        tk.Button(top_bar, text="Run", bg=ACCENT_BLUE, fg="white", font=FONT_NORMAL,
                  relief="flat", padx=20, pady=6, command=self.run_paging, cursor="hand2").pack(side="right")

        # Reference string
        ref_panel = panel(parent, padx=12, pady=10)
        ref_panel.pack(fill="x")
        tk.Label(ref_panel, text="Reference String", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")
        self.refs_var = tk.StringVar(value="7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1")
        ttk.Entry(ref_panel, textvariable=self.refs_var, width=80).pack(anchor="w", pady=(6, 0))

        # Main row: frame table (left) + statistics (right)
        main_row = tk.Frame(parent, bg=BG_DARK)
        main_row.pack(fill="both", expand=True, pady=(10, 0))

        table_panel = panel(main_row, padx=12, pady=10)
        table_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(table_panel, text="Page Frames", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        self.frame_canvas = tk.Canvas(table_panel, bg=BG_PANEL, highlightthickness=0)
        vbar = ttk.Scrollbar(table_panel, orient="vertical", command=self.frame_canvas.yview)
        hbar = ttk.Scrollbar(table_panel, orient="horizontal", command=self.frame_canvas.xview)
        self.frame_canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        self.frame_canvas.pack(side="left", fill="both", expand=True, pady=(6, 0))
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")

        tk.Label(table_panel, text="Page Faults", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w", pady=(8, 0))
        self.faults_canvas = tk.Canvas(table_panel, height=40, bg=BG_PANEL, highlightthickness=0)
        self.faults_canvas.pack(fill="x", pady=(4, 0))

        # Statistics panel
        stats_panel = panel(main_row, padx=12, pady=10, width=220)
        stats_panel.pack(side="left", fill="y")
        tk.Label(stats_panel, text="Statistics", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        self.stat_labels = {}
        for key, label in [("total_ref", "Total References"),
                            ("faults", "Page Faults"),
                            ("fault_rate", "Page Fault Rate"),
                            ("hits", "Hits"),
                            ("hit_rate", "Hit Rate")]:
            row = tk.Frame(stats_panel, bg=BG_PANEL)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=BG_PANEL, fg=FG_MUTED, font=FONT_NORMAL, width=16, anchor="w").pack(side="left")
            val = tk.Label(row, text="--", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE, anchor="e")
            val.pack(side="left")
            self.stat_labels[key] = val

    def run_paging(self):
        try:
            pages = [int(x.strip()) for x in self.refs_var.get().split(",") if x.strip()]
            num_frames = int(self.frames_var.get())
            if num_frames <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Reference string must be comma-separated integers; frames must be a positive integer.")
            return

        algo = self.algo_var.get()
        if algo == "FIFO":
            history, faults, hit_ratio = page_replacement.fifo_page_replacement(pages, num_frames)
        elif algo == "LRU":
            history, faults, hit_ratio = page_replacement.lru_page_replacement(pages, num_frames)
        else:
            history, faults, hit_ratio = page_replacement.optimal_page_replacement(pages, num_frames)

        self._draw_frame_table(pages, history, num_frames)
        self._draw_fault_row(pages, history)

        hits = len(pages) - faults
        self.stat_labels["total_ref"].configure(text=str(len(pages)))
        self.stat_labels["faults"].configure(text=str(faults))
        self.stat_labels["fault_rate"].configure(text=f"{faults / len(pages) * 100:.2f}%")
        self.stat_labels["hits"].configure(text=str(hits))
        self.stat_labels["hit_rate"].configure(text=f"{hit_ratio * 100:.2f}%")

    def _draw_frame_table(self, pages, history, num_frames):
        canvas = self.frame_canvas
        canvas.delete("all")
        cell_w, cell_h = 36, 26
        x0, y0 = 50, 10

        for i, page in enumerate(pages):
            canvas.create_rectangle(x0 + i * cell_w, y0, x0 + (i + 1) * cell_w, y0 + cell_h,
                                     fill="#374151", outline=BG_PANEL)
            canvas.create_text(x0 + i * cell_w + cell_w / 2, y0 + cell_h / 2, text=str(page),
                                fill="white", font=FONT_SMALL)
        canvas.create_text(x0 // 2, y0 + cell_h / 2, text="Ref", fill=FG_TEXT, font=FONT_SMALL)

        for f in range(num_frames):
            row_y = y0 + (f + 1) * cell_h
            canvas.create_text(x0 // 2, row_y + cell_h / 2, text=str(f), fill=FG_TEXT, font=FONT_SMALL)
            for i, state in enumerate(history):
                val = state[f] if f < len(state) else None

                is_fault = False
                if i == 0:
                    is_fault = val is not None
                else:
                    prev = history[i - 1][f] if f < len(history[i - 1]) else None
                    if val != prev:
                        is_fault = True

                color = "#7f1d1d" if (is_fault and val is not None) else "#2a3447"
                canvas.create_rectangle(x0 + i * cell_w, row_y, x0 + (i + 1) * cell_w, row_y + cell_h,
                                         outline=BG_PANEL, fill=color)
                if val is not None:
                    canvas.create_text(x0 + i * cell_w + cell_w / 2, row_y + cell_h / 2, text=str(val),
                                        fill="white", font=FONT_SMALL)

        total_w = x0 + len(pages) * cell_w + 20
        total_h = y0 + (num_frames + 1) * cell_h + 20
        canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _draw_fault_row(self, pages, history):
        canvas = self.faults_canvas
        canvas.delete("all")
        cell_w, cell_h = 36, 26
        x0, y0 = 50, 4

        for i in range(len(pages)):
            prev_set = set(history[i - 1]) if i > 0 else set()
            fault = pages[i] not in prev_set if i > 0 else True
            if i > 0 and pages[i] in history[i - 1]:
                fault = False

            label = "F" if fault else "-"
            color = "#7f1d1d" if fault else "#14532d"
            canvas.create_rectangle(x0 + i * cell_w, y0, x0 + (i + 1) * cell_w, y0 + cell_h,
                                     outline=BG_PANEL, fill=color)
            canvas.create_text(x0 + i * cell_w + cell_w / 2, y0 + cell_h / 2, text=label,
                                fill="white", font=FONT_SMALL)

        canvas.configure(scrollregion=(0, 0, x0 + len(pages) * cell_w + 20, y0 + cell_h + 10))

    # ------------------------------------------------------------------
    # Allocation tab (First/Best/Worst Fit)
    # ------------------------------------------------------------------
    def _build_allocation_tab(self, parent):
        top_bar = tk.Frame(parent, bg=BG_DARK)
        top_bar.pack(fill="x", pady=(10, 12))

        blocks_box = tk.Frame(top_bar, bg=BG_DARK)
        blocks_box.pack(side="left")
        tk.Label(blocks_box, text="Memory Blocks (sizes)", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.blocks_var = tk.StringVar(value="100,500,200,300,600")
        ttk.Entry(blocks_box, textvariable=self.blocks_var, width=28).pack(anchor="w")

        procs_box = tk.Frame(top_bar, bg=BG_DARK)
        procs_box.pack(side="left", padx=20)
        tk.Label(procs_box, text="Process Sizes", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.procs_var = tk.StringVar(value="212,417,112,426")
        ttk.Entry(procs_box, textvariable=self.procs_var, width=28).pack(anchor="w")

        strat_box = tk.Frame(top_bar, bg=BG_DARK)
        strat_box.pack(side="left", padx=20)
        tk.Label(strat_box, text="Strategy", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.strategy_var = tk.StringVar(value="First Fit")
        ttk.Combobox(strat_box, textvariable=self.strategy_var, state="readonly", width=12,
                     values=["First Fit", "Best Fit", "Worst Fit"]).pack(anchor="w")

        tk.Button(top_bar, text="Run", bg=ACCENT_BLUE, fg="white", font=FONT_NORMAL,
                  relief="flat", padx=20, pady=6, command=self.run_allocation, cursor="hand2").pack(side="right")

        viz_panel = panel(parent, padx=12, pady=10)
        viz_panel.pack(fill="x", pady=(0, 10))
        tk.Label(viz_panel, text="Memory Block Visualization", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")
        self.mem_canvas = tk.Canvas(viz_panel, height=110, bg=BG_PANEL, highlightthickness=0)
        self.mem_canvas.pack(fill="x", pady=(6, 0))

        report_panel = panel(parent, padx=12, pady=10)
        report_panel.pack(fill="both", expand=True)
        tk.Label(report_panel, text="Allocation & Fragmentation Report", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")
        self.alloc_text = tk.Text(report_panel, height=12, bg="#2a3447", fg=FG_TEXT, relief="flat",
                                   font=("Consolas", 10), insertbackground=FG_TEXT)
        self.alloc_text.pack(fill="both", expand=True, pady=(6, 0))

        self.run_allocation()

    def run_allocation(self):
        try:
            blocks = [int(x.strip()) for x in self.blocks_var.get().split(",") if x.strip()]
            procs = [int(x.strip()) for x in self.procs_var.get().split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Input Error", "Block and process sizes must be comma-separated integers.")
            return

        strategy_key = {"First Fit": "first", "Best Fit": "best", "Worst Fit": "worst"}[self.strategy_var.get()]
        allocation, _ = memory.fixed_partition_allocation(blocks, procs, strategy_key)
        internal_frag, external_frag = memory.fragmentation_report(blocks, procs, allocation)

        self._draw_memory_blocks(blocks, procs, allocation)

        self.alloc_text.delete("1.0", tk.END)
        self.alloc_text.insert(tk.END, f"Strategy: {self.strategy_var.get()}\n\n")
        self.alloc_text.insert(tk.END, "Allocation:\n")
        for i, b in allocation.items():
            if b is not None:
                self.alloc_text.insert(tk.END, f"  Process P{i} (size={procs[i]}) -> Block {b} (size={blocks[b]})\n")
            else:
                self.alloc_text.insert(tk.END, f"  Process P{i} (size={procs[i]}) -> NOT ALLOCATED (no fit)\n")

        self.alloc_text.insert(tk.END, "\nInternal Fragmentation per Process:\n")
        for i, frag in internal_frag.items():
            self.alloc_text.insert(tk.END, f"  P{i}: {frag}\n")

        self.alloc_text.insert(tk.END, f"\nTotal External Fragmentation (unused blocks): {external_frag}\n")

    def _draw_memory_blocks(self, blocks, procs, allocation):
        canvas = self.mem_canvas
        canvas.delete("all")
        x = 10
        for j, size in enumerate(blocks):
            width = max(50, size // 4)
            assigned = [i for i, b in allocation.items() if b == j]
            if assigned:
                pid = assigned[0]
                color = FRAME_COLORS[pid % len(FRAME_COLORS)]
                label = f"B{j} ({size})\nP{pid} ({procs[pid]})"
            else:
                color = "#374151"
                label = f"B{j} ({size})\nFree"
            canvas.create_rectangle(x, 10, x + width, 90, fill=color, outline=BG_PANEL, width=2)
            canvas.create_text(x + width / 2, 50, text=label, fill="white", font=FONT_SMALL)
            x += width + 10
        canvas.configure(scrollregion=(0, 0, x + 20, 100))
