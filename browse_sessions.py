#!/usr/bin/env python3
"""
Simple Tkinter app to browse conference sessions stored in SQLite.
"""
import os
import sqlite3
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "conference_sessions.db")

class SessionBrowser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conference Session Browser")
        self.geometry("800x600")

        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

        self.create_widgets()
        self.load_sessions()

    def create_widgets(self):
        # Filter frame
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(filter_frame, text="Search sessions by title or date (partial, case-insensitive):").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        # Automatically update session list as user types in filter
        try:
            # Python 3.6+ tkinter
            self.filter_var.trace_add('write', lambda *args: self.on_search())
        except AttributeError:
            # Older tkinter fallback
            self.filter_var.trace('w', lambda *args: self.on_search())
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Search", command=self.on_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Reset", command=self.on_reset).pack(side=tk.LEFT, padx=5)

        # Day filter frame
        day_frame = ttk.Frame(self)
        day_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(day_frame, text="Filter by day:").pack(side=tk.LEFT)
        
        self.selected_day = tk.StringVar()
        days = [("All", ""), ("Mon", "Monday"), ("Tue", "Tuesday"), ("Wed", "Wednesday"), ("Thu", "Thursday")]
        for display_name, day_value in days:
            ttk.Radiobutton(
                day_frame, 
                text=display_name, 
                variable=self.selected_day, 
                value=day_value,
                command=self.on_day_filter
            ).pack(side=tk.LEFT, padx=5)
        
        self.selected_day.set("")  # Default to "All"

        # Treeview frame
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("title", "date", "session_code")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("title", text="Title")
        self.tree.heading("date", text="Date")
        self.tree.heading("session_code", text="Code")
        self.tree.column("title", width=400)
        self.tree.column("date", width=200)
        self.tree.column("session_code", width=80, anchor=tk.CENTER)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Detail frame
        detail_frame = ttk.LabelFrame(self, text="Session Details")
        detail_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        self.detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        self.detail_text.configure(state=tk.DISABLED)

    def load_sessions(self, filter_text=None, day_filter=None):
        """
        Load sessions into the treeview. If filter_text is provided, perform
        a partial, case-insensitive match against title or date.
        If day_filter is provided, filter by day of week.
        """
        self.tree.delete(*self.tree.get_children())
        cursor = self.conn.cursor()
        
        query = "SELECT rowid, title, date, session_code FROM sessions"
        params = []
        where_clauses = []
        
        if filter_text:
            pat = f"%{filter_text.lower()}%"
            where_clauses.append("(lower(date) LIKE ? OR lower(title) LIKE ?)")
            params.extend([pat, pat])
            
        if day_filter:
            where_clauses.append("date LIKE ?")
            params.append(f"{day_filter}%")
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY date"
        
        cursor.execute(query, params)
        for row in cursor.fetchall():
            self.tree.insert(
                "", tk.END, iid=row["rowid"],
                values=(row["title"], row["date"], row["session_code"] or "")
            )

    def on_search(self):
        """Callback for search field changes."""
        text = self.filter_var.get().strip()
        day = self.selected_day.get() if hasattr(self, 'selected_day') else None
        self.load_sessions(filter_text=text, day_filter=day)

    def on_day_filter(self):
        """Callback for day filter changes."""
        text = self.filter_var.get().strip()
        day = self.selected_day.get()
        self.load_sessions(filter_text=text, day_filter=day)

    def on_reset(self):
        self.filter_var.set("")
        self.selected_day.set("")
        self.load_sessions()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        rowid = sel[0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE rowid=?", (rowid,))
        record = cursor.fetchone()
        if record:
            self.detail_text.configure(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            lines = []
            for key in record.keys():
                lines.append(f"{key.capitalize()}: {record[key]}")
            self.detail_text.insert(tk.END, "\n".join(lines))
            self.detail_text.configure(state=tk.DISABLED)

if __name__ == "__main__":
    app = SessionBrowser()
    app.mainloop()