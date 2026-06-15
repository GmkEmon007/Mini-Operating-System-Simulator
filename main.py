"""
Mini Operating System Simulator - Single Window Application

This is the entry point. A single main window contains a persistent left
sidebar and a content area. Clicking a sidebar item swaps the visible page
in place (no extra windows are opened).
"""

import tkinter as tk

from theme import apply_dark_style, Sidebar, MODULE_LIST, BG_DARK

from dashboard_page import DashboardPage
from cpu_page import CPUSchedulingPage
from memory_page import MemoryManagementPage
from sync_page import SynchronizationPage
from deadlock_page import DeadlockPage
from file_page import FileManagementPage


class OSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Operating System Simulator")
        self.geometry("1200x720")
        apply_dark_style(self)
        self.configure(bg=BG_DARK)

        root = tk.Frame(self, bg=BG_DARK)
        root.pack(fill="both", expand=True)

        # Sidebar (persistent)
        self.sidebar = Sidebar(root, MODULE_LIST, on_select=self.show_page,
                                active_key="dashboard", footer_text="System Ready")
        self.sidebar.pack(side="left", fill="y")

        # Content area
        self.content = tk.Frame(root, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Instantiate all pages once (kept alive, just hidden/shown)
        self.pages = {}
        for key, cls in [
            ("dashboard", DashboardPage),
            ("cpu", CPUSchedulingPage),
            ("memory", MemoryManagementPage),
            ("sync", SynchronizationPage),
            ("deadlock", DeadlockPage),
            ("file", FileManagementPage),
        ]:
            page = cls(self.content, app=self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = page

        self.show_page("dashboard")

    def show_page(self, key):
        page = self.pages.get(key)
        if page is None:
            return
        page.tkraise()
        if hasattr(page, "on_show"):
            page.on_show()


if __name__ == "__main__":
    app = OSimulatorApp()
    app.mainloop()
