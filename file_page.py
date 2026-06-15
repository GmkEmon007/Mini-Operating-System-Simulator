"""
File Management Page - Allocation (Sequential / Linked / Indexed)
"""

import tkinter as tk
from tkinter import ttk, messagebox

import file_management as fm
from theme import (
    panel,
    BG_DARK, BG_PANEL, FG_TEXT, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED,
    FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL,
)

FILE_COLORS = ["#22c55e", "#3b82f6", "#f59e0b", "#a855f7", "#ec4899",
               "#06b6d4", "#eab308", "#64748b"]

DEFAULT_FILES = [
    {"name": "File1.txt", "size": 3},
    {"name": "File2.pdf", "size": 5},
    {"name": "Image.png", "size": 2},
    {"name": "Doc.docx", "size": 4},
]


class FileManagementPage(tk.Frame):
    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG_DARK)
        self.app = app
        self._build_layout()
        self.run_allocation()

    # ------------------------------------------------------------------
    def _build_layout(self):
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=16, pady=14)

        # Top bar
        top_bar = tk.Frame(content, bg=BG_DARK)
        top_bar.pack(fill="x", pady=(0, 12))

        method_box = tk.Frame(top_bar, bg=BG_DARK)
        method_box.pack(side="left")
        tk.Label(method_box, text="Allocation Method", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.method_var = tk.StringVar(value="Indexed Allocation")
        method_combo = ttk.Combobox(method_box, textvariable=self.method_var, state="readonly", width=20,
                                     values=["Sequential Allocation", "Linked Allocation", "Indexed Allocation"])
        method_combo.pack(anchor="w")
        method_combo.bind("<<ComboboxSelected>>", lambda e: self._on_method_change())

        disk_box = tk.Frame(top_bar, bg=BG_DARK)
        disk_box.pack(side="left", padx=20)
        tk.Label(disk_box, text="Disk Size (blocks)", bg=BG_DARK, fg=FG_TEXT, font=FONT_SMALL).pack(anchor="w")
        self.disk_size_var = tk.StringVar(value="24")
        ttk.Entry(disk_box, textvariable=self.disk_size_var, width=8).pack(anchor="w")

        tk.Button(top_bar, text="Run", bg=ACCENT_BLUE, fg="white", font=FONT_NORMAL,
                  relief="flat", padx=20, pady=6, command=self.run_allocation, cursor="hand2").pack(side="right")

        # Main row: Directory/File table (left) + allocation-specific table (right)
        main_row = tk.Frame(content, bg=BG_DARK)
        main_row.pack(fill="x")

        dir_panel = panel(main_row, padx=12, pady=10)
        dir_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(dir_panel, text="Directory", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")

        columns = ("name", "start", "size")
        headings = ["File Name", "Start / Index Block", "File Size (blocks)"]
        self.dir_tree = ttk.Treeview(dir_panel, columns=columns, show="headings", height=6)
        for col, head in zip(columns, headings):
            self.dir_tree.heading(col, text=head)
            self.dir_tree.column(col, anchor="center", width=130)
        self.dir_tree.pack(fill="both", expand=True, pady=(6, 8))
        self.dir_tree.bind("<Double-1>", self._edit_cell)

        for f in DEFAULT_FILES:
            self.dir_tree.insert("", "end", values=(f["name"], "-", f["size"]))

        btn_row = tk.Frame(dir_panel, bg=BG_PANEL)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="Add File", bg=ACCENT_GREEN, fg="white", relief="flat",
                  padx=10, pady=4, command=self.add_file, cursor="hand2").pack(side="left", padx=(0, 6))
        tk.Button(btn_row, text="Remove", bg=ACCENT_RED, fg="white", relief="flat",
                  padx=10, pady=4, command=self.remove_file, cursor="hand2").pack(side="left", padx=6)

        # Right: allocation table (changes based on method)
        self.alloc_panel = panel(main_row, padx=12, pady=10)
        self.alloc_panel.pack(side="left", fill="both", expand=True)
        self.alloc_title = tk.Label(self.alloc_panel, text="Allocation Table", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE)
        self.alloc_title.pack(anchor="w")
        self.alloc_table_frame = tk.Frame(self.alloc_panel, bg=BG_PANEL)
        self.alloc_table_frame.pack(fill="both", expand=True, pady=(6, 0))

        # Disk blocks visualization
        disk_panel = panel(content, padx=12, pady=10)
        disk_panel.pack(fill="x", pady=(10, 0))
        tk.Label(disk_panel, text="Disk Blocks", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SUBTITLE).pack(anchor="w")
        self.disk_canvas = tk.Canvas(disk_panel, height=70, bg=BG_PANEL, highlightthickness=0)
        self.disk_canvas.pack(fill="x", pady=(6, 6))

        self.legend_frame = tk.Frame(disk_panel, bg=BG_PANEL)
        self.legend_frame.pack(anchor="w")

        self._on_method_change()

    def _on_method_change(self):
        method = self.method_var.get()
        if method == "Sequential Allocation":
            self.alloc_title.configure(text="Sequential Allocation Table")
        elif method == "Linked Allocation":
            self.alloc_title.configure(text="Linked Allocation (Block Chains)")
        else:
            self.alloc_title.configure(text="Index Block Table")

    # ------------------------------------------------------------------
    def _edit_cell(self, event):
        item = self.dir_tree.identify_row(event.y)
        column = self.dir_tree.identify_column(event.x)
        if not item or not column:
            return
        col_index = int(column.replace("#", "")) - 1
        col_name = self.dir_tree["columns"][col_index]
        if col_name in ("start",):
            return  # computed, not editable

        x, y, w, h = self.dir_tree.bbox(item, column)
        value = self.dir_tree.set(item, col_name)

        edit_var = tk.StringVar(value=value)
        entry = ttk.Entry(self.dir_tree, textvariable=edit_var)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus()
        entry.select_range(0, tk.END)

        def save_edit(event=None):
            new_val = edit_var.get()
            if col_name == "size":
                try:
                    new_val = int(new_val)
                    if new_val <= 0:
                        new_val = value
                except ValueError:
                    new_val = value
            self.dir_tree.set(item, col_name, new_val)
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    def add_file(self):
        n = len(self.dir_tree.get_children()) + 1
        self.dir_tree.insert("", "end", values=(f"NewFile{n}.dat", "-", 2))

    def remove_file(self):
        sel = self.dir_tree.selection()
        if sel:
            self.dir_tree.delete(sel[0])
        else:
            children = self.dir_tree.get_children()
            if children:
                self.dir_tree.delete(children[-1])

    # ------------------------------------------------------------------
    def _read_files(self):
        files = []
        for item in self.dir_tree.get_children():
            name, _start, size = self.dir_tree.item(item, "values")
            files.append({"name": str(name), "size": int(size)})
        return files

    def run_allocation(self):
        try:
            files = self._read_files()
            disk_size = int(self.disk_size_var.get())
            if disk_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Disk size must be a positive integer and file sizes must be integers.")
            return

        method = self.method_var.get()

        if method == "Sequential Allocation":
            table, disk_map = fm.sequential_allocation(files, disk_size)
            self._render_sequential_table(table)
        elif method == "Linked Allocation":
            table, disk_map = fm.linked_allocation(files, disk_size)
            self._render_linked_table(table)
        else:
            table, disk_map = fm.indexed_allocation(files, disk_size)
            self._render_indexed_table(table)

        # Update Directory table's "Start / Index Block" column
        for item, t in zip(self.dir_tree.get_children(), table):
            if method == "Indexed Allocation":
                start_val = t.get("index_block")
            else:
                start_val = t.get("start")
            self.dir_tree.set(item, "start", start_val if start_val is not None else "N/A")

        self._draw_disk_blocks(disk_map, files)

    # ------------------------------------------------------------------
    def _clear_alloc_table(self):
        for widget in self.alloc_table_frame.winfo_children():
            widget.destroy()

    def _render_sequential_table(self, table):
        self._clear_alloc_table()
        headers = ["File Name", "Start Block", "Length", "End Block", "Status"]
        for c, h in enumerate(headers):
            tk.Label(self.alloc_table_frame, text=h, bg="#1f2937", fg=FG_TEXT,
                     font=("Segoe UI", 9, "bold"), padx=8, pady=4).grid(row=0, column=c, sticky="ew")

        for r, t in enumerate(table, start=1):
            status = "OK" if t["ok"] else "FAILED"
            color = ACCENT_GREEN if t["ok"] else ACCENT_RED
            vals = [t["name"], t["start"] if t["ok"] else "-", t["length"], t["end"] if t["ok"] else "-"]
            for c, v in enumerate(vals):
                tk.Label(self.alloc_table_frame, text=str(v), bg="#2a3447", fg=FG_TEXT,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=c, sticky="ew")
            tk.Label(self.alloc_table_frame, text=status, bg="#2a3447", fg=color,
                     font=("Segoe UI", 9, "bold"), padx=8, pady=4).grid(row=r, column=len(vals), sticky="ew")

        for c in range(len(headers)):
            self.alloc_table_frame.grid_columnconfigure(c, weight=1)

    def _render_linked_table(self, table):
        self._clear_alloc_table()
        headers = ["File Name", "Start Block", "Block Chain (block→next)"]
        for c, h in enumerate(headers):
            tk.Label(self.alloc_table_frame, text=h, bg="#1f2937", fg=FG_TEXT,
                     font=("Segoe UI", 9, "bold"), padx=8, pady=4).grid(row=0, column=c, sticky="ew")

        for r, t in enumerate(table, start=1):
            if not t["ok"]:
                tk.Label(self.alloc_table_frame, text=t["name"], bg="#2a3447", fg=FG_TEXT,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=0, sticky="ew")
                tk.Label(self.alloc_table_frame, text="-", bg="#2a3447", fg=FG_TEXT,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=1, sticky="ew")
                tk.Label(self.alloc_table_frame, text="FAILED - not enough free blocks", bg="#2a3447", fg=ACCENT_RED,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=2, sticky="ew")
                continue

            chain_str = " → ".join(
                f"{b}" + ("" if t["links"][b] == -1 else "") for b in t["blocks"]
            )
            chain_str += " → END"

            tk.Label(self.alloc_table_frame, text=t["name"], bg="#2a3447", fg=FG_TEXT,
                     font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=0, sticky="ew")
            tk.Label(self.alloc_table_frame, text=str(t["start"]), bg="#2a3447", fg=FG_TEXT,
                     font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=1, sticky="ew")
            tk.Label(self.alloc_table_frame, text=chain_str, bg="#2a3447", fg=FG_TEXT,
                     font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=2, sticky="w")

        for c in range(len(headers)):
            self.alloc_table_frame.grid_columnconfigure(c, weight=1)

    def _render_indexed_table(self, table):
        self._clear_alloc_table()
        headers = ["File Name", "Index Block", "Data Block Pointers"]
        for c, h in enumerate(headers):
            tk.Label(self.alloc_table_frame, text=h, bg="#1f2937", fg=FG_TEXT,
                     font=("Segoe UI", 9, "bold"), padx=8, pady=4).grid(row=0, column=c, sticky="ew")

        for r, t in enumerate(table, start=1):
            if not t["ok"]:
                tk.Label(self.alloc_table_frame, text=t["name"], bg="#2a3447", fg=FG_TEXT,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=0, sticky="ew")
                tk.Label(self.alloc_table_frame, text="-", bg="#2a3447", fg=FG_TEXT,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=1, sticky="ew")
                tk.Label(self.alloc_table_frame, text="FAILED - not enough free blocks", bg="#2a3447", fg=ACCENT_RED,
                         font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=2, sticky="ew")
                continue

            pointers_str = " | ".join(str(b) for b in t["data_blocks"])

            tk.Label(self.alloc_table_frame, text=t["name"], bg="#2a3447", fg=FG_TEXT,
                     font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=0, sticky="ew")
            tk.Label(self.alloc_table_frame, text=str(t["index_block"]), bg="#2a3447", fg=FG_TEXT,
                     font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=1, sticky="ew")
            tk.Label(self.alloc_table_frame, text=pointers_str, bg="#2a3447", fg=FG_TEXT,
                     font=FONT_SMALL, padx=8, pady=4).grid(row=r, column=2, sticky="w")

        for c in range(len(headers)):
            self.alloc_table_frame.grid_columnconfigure(c, weight=1)

    # ------------------------------------------------------------------
    def _draw_disk_blocks(self, disk_map, files):
        canvas = self.disk_canvas
        canvas.delete("all")

        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        color_map = {}
        for i, f in enumerate(files):
            color_map[f["name"]] = FILE_COLORS[i % len(FILE_COLORS)]

        cell = 32
        x, y = 6, 6

        for i, block in enumerate(disk_map):
            if block is None:
                color = "#374151"
            else:
                base_name = block.rstrip("*")
                color = color_map.get(base_name, "#6b7280")

            canvas.create_rectangle(x, y, x + cell, y + cell, fill=color, outline=BG_PANEL, width=1)
            canvas.create_text(x + cell / 2, y + cell / 2, text=str(i), fill="white", font=("Segoe UI", 8))
            x += cell + 4

        canvas.configure(scrollregion=(0, 0, x + 10, cell + 12))

        # Legend
        tk.Label(self.legend_frame, text="●", bg=BG_PANEL, fg="#374151", font=FONT_NORMAL).pack(side="left")
        tk.Label(self.legend_frame, text=" Free Block", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SMALL).pack(side="left", padx=(0, 12))
        for f in files:
            color = color_map[f["name"]]
            tk.Label(self.legend_frame, text="●", bg=BG_PANEL, fg=color, font=FONT_NORMAL).pack(side="left")
            tk.Label(self.legend_frame, text=f" {f['name']}", bg=BG_PANEL, fg=FG_TEXT, font=FONT_SMALL).pack(side="left", padx=(0, 12))
