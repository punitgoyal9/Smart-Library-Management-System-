# ==============================================================================
# SMART LIBRARY MANAGEMENT SYSTEM (Venom Tech-Matrix Edition)
# Python + Tkinter + Oracle Database + PL/SQL
# ==============================================================================

from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv
import oracledb

load_dotenv()

class LibraryApp:
    # Cyber Obsidian & Venom Web Palette
    BG = "#050811"             # Deep Obsidian Dark Background
    CARD_BG = "#0D1322"        # High-contrast Slate Dark Surface
    SURFACE = "#151D30"        # Elevated Dark Surface
    PRIMARY = "#00F0FF"        # Electric Hologram Cyan
    PRIMARY_HOVER = "#0088FF"
    SECONDARY = "#FF007F"      # Hologram Magenta Accent
    SUCCESS = "#00FF88"        # Hologram Mint Green
    INFO = "#3B82F6"           # Hologram Blue
    WARNING = "#FFB703"        # Hologram Amber
    DANGER = "#FF2E93"         # Hologram Crimson
    
    # Venom Web Special Colors
    VENOM_DARK = "#090D16"     # Deep Black/Charcoal Web Core
    VENOM_WEB = "#1C263B"      # Dark Web Border Matrix
    
    TEXT = "#F1F5F9"           # Bright Crisp White
    MUTED = "#64748B"          # Muted Slate Gray
    BORDER = "#1E293B"         # Subtle Border

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Library Management System - Venom Edition")
        self.root.geometry("920x720")
        self.root.minsize(820, 640)
        self.root.configure(bg=self.BG)

        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("TEntry", 
                        fieldbackground=self.SURFACE, 
                        foreground=self.PRIMARY, 
                        insertcolor=self.PRIMARY, 
                        padding=10, 
                        font=("Consolas", 10, "bold"))
        
        style.configure("Vertical.TScrollbar", 
                        background=self.SURFACE, 
                        troughcolor=self.BG, 
                        bordercolor=self.BORDER, 
                        arrowcolor=self.PRIMARY)

    def build_ui(self):
        # Main Scrollable Container
        self.canvas = tk.Canvas(self.root, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview, style="Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.main = tk.Frame(self.canvas, bg=self.BG, padx=20, pady=20)
        self.window_id = self.canvas.create_window((0, 0), window=self.main, anchor="nw")

        self.main.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.window_id, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))

        # Header Section
        header = tk.Frame(self.main, bg=self.CARD_BG, padx=20, pady=16, highlightbackground=self.PRIMARY, highlightthickness=1)
        header.pack(fill="x", pady=(0, 20))

        tk.Label(header, text="⚡ SMART LIBRARY MANAGEMENT SYSTEM", font=("Segoe UI", 16, "bold"), bg=self.CARD_BG, fg=self.PRIMARY).pack(anchor="w")
        tk.Label(header, text="Venom Web Interactive Interface • Oracle PL/SQL Powered", font=("Segoe UI", 9), bg=self.CARD_BG, fg=self.MUTED).pack(anchor="w", pady=(2, 0))

        # ==========================================
        # SPLIT CONTAINER (Left: Inputs | Right: Actions)
        # ==========================================
        split_container = tk.Frame(self.main, bg=self.BG)
        split_container.pack(fill="both", expand=True, pady=(0, 16))
        split_container.columnconfigure(0, weight=1)
        split_container.columnconfigure(1, weight=1)

        # ------------------------------------------
        # LEFT SIDE: INPUT & TRANSACTION DETAILS
        # ------------------------------------------
        left_frame = tk.Frame(split_container, bg=self.CARD_BG, padx=16, pady=16, highlightbackground=self.BORDER, highlightthickness=1)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left_frame, text="📝 Transaction Parameters", font=("Segoe UI", 11, "bold"), bg=self.CARD_BG, fg=self.PRIMARY).pack(anchor="w", pady=(0, 10))

        self.member_entry = self.create_input(left_frame, "Member ID")
        self.book_entry = self.create_input(left_frame, "Book ID")

        # Issue Date with automatic tracking
        tk.Label(left_frame, text="Issue Date (YYYY-MM-DD)", font=("Segoe UI", 9, "bold"), bg=self.CARD_BG, fg=self.TEXT).pack(anchor="w", pady=(6, 2))
        self.issue_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.issue_date_var.trace_add("write", self.update_due_date)
        self.issue_entry = ttk.Entry(left_frame, textvariable=self.issue_date_var)
        self.issue_entry.pack(fill="x", pady=(0, 8))

        # Due Date (Read-Only)
        tk.Label(left_frame, text="Due Date (Auto: +15 Days)", font=("Segoe UI", 9, "bold"), bg=self.CARD_BG, fg=self.TEXT).pack(anchor="w", pady=(6, 2))
        self.due_date_var = tk.StringVar()
        self.due_entry = ttk.Entry(left_frame, textvariable=self.due_date_var, state="readonly")
        self.due_entry.pack(fill="x", pady=(0, 8))
        self.update_due_date()

        # System Reset inside Left Pane (Bottom)
        reset_box = tk.Frame(left_frame, bg=self.SURFACE, padx=10, pady=10, highlightbackground=self.DANGER, highlightthickness=1)
        reset_box.pack(fill="x", pady=(20, 0))
        tk.Label(reset_box, text="⚠️ Danger Zone", font=("Segoe UI", 9, "bold"), bg=self.SURFACE, fg=self.DANGER).pack(anchor="w")
        self.make_venom_button(reset_box, "Reset Database Data", self.reset_database_data, self.DANGER).pack(fill="x", pady=(6, 0))


        # ------------------------------------------
        # RIGHT SIDE: LIBRARY OPERATIONS & ACTIONS
        # ------------------------------------------
        right_frame = tk.Frame(split_container, bg=self.CARD_BG, padx=16, pady=16, highlightbackground=self.BORDER, highlightthickness=1)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(right_frame, text="⚡ Quick Operations", font=("Segoe UI", 11, "bold"), bg=self.CARD_BG, fg=self.PRIMARY).pack(anchor="w", pady=(0, 14))

        # Action Buttons with Venom Web Effect
        self.styled_action_row(right_frame, "📗 Issue Book (PL/SQL)", "Execute book checkout procedure", self.issue_book, self.SUCCESS)
        self.styled_action_row(right_frame, "💰 Calculate Fine", "Check overdue penalty charges", self.calculate_fine, self.INFO)
        self.styled_action_row(right_frame, "🔎 View Issued Books", "Search active transactions", self.view_issued_books_smart, self.PRIMARY)
        self.styled_action_row(right_frame, "📚 Catalogue Details", "View all library inventory", self.show_books_details, self.WARNING)
        self.styled_action_row(right_frame, "📘 Advanced Management", "All issued records & pagination", self.open_issued_books_window, self.SECONDARY)

        # Footer note
        tk.Label(self.main, text="Powered by Python, Tkinter & Oracle PL/SQL (Venom Web Edition)", font=("Segoe UI", 8), bg=self.BG, fg=self.MUTED).pack(pady=10)

    def update_due_date(self, *args):
        try:
            issue_date_str = self.issue_date_var.get().strip()
            issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d")
            due_date = issue_date + timedelta(days=15)
            
            self.due_entry.config(state="normal")
            self.due_date_var.set(due_date.strftime("%Y-%m-%d"))
            self.due_entry.config(state="readonly")
        except ValueError:
            self.due_entry.config(state="normal")
            self.due_date_var.set("Invalid format")
            self.due_entry.config(state="readonly")

    def create_input(self, parent, label):
        tk.Label(parent, text=label, font=("Segoe UI", 9, "bold"), bg=self.CARD_BG, fg=self.TEXT).pack(anchor="w", pady=(4, 2))
        entry = ttk.Entry(parent)
        entry.pack(fill="x", pady=(0, 6))
        return entry

    def styled_action_row(self, parent, title, subtitle, command, color):
        row_card = tk.Frame(parent, bg=self.SURFACE, padx=10, pady=8, highlightbackground=self.BORDER, highlightthickness=1)
        row_card.pack(fill="x", pady=6)
        
        text_frame = tk.Frame(row_card, bg=self.SURFACE)
        text_frame.pack(side="left", fill="x", expand=True)

        tk.Label(text_frame, text=title, font=("Segoe UI", 9, "bold"), bg=self.SURFACE, fg=self.TEXT).pack(anchor="w")
        tk.Label(text_frame, text=subtitle, font=("Segoe UI", 8), bg=self.SURFACE, fg=self.MUTED).pack(anchor="w")

        btn = self.make_venom_button(row_card, "Execute ➔", command, color)
        btn.pack(side="right", padx=(8, 0))

    def make_venom_button(self, parent, text, command, base_color):
        """Creates a custom button with Venom Web Black Matrix hover simulation."""
        btn = tk.Button(
            parent, text=text, command=command,
            bg=self.VENOM_DARK, fg=base_color,
            activebackground=base_color, activeforeground="#000000",
            font=("Segoe UI", 9, "bold"), relief="solid", bd=1,
            highlightbackground=self.VENOM_WEB, cursor="hand2", padx=10, pady=5
        )
        
        # Venom Web Hover Effect: Black Web core expanding to colored neon aura
        def on_enter(e):
            btn.config(bg=base_color, fg=self.VENOM_DARK, relief="raised", highlightbackground=base_color)
            
        def on_leave(e):
            btn.config(bg=self.VENOM_DARK, fg=base_color, relief="solid", highlightbackground=self.VENOM_WEB)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def connect_db(self):
        return oracledb.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), dsn=os.getenv("DB_DSN"))

    def issue_book(self):
        m_id, b_id = self.member_entry.get().strip(), self.book_entry.get().strip()
        issue_str = self.issue_date_var.get().strip()
        due_str = self.due_date_var.get().strip()

        if not m_id or not b_id:
            messagebox.showerror("Input Error", "Enter both Member ID and Book ID.")
            return

        try:
            member_id, book_id = int(m_id), int(b_id)
            issue_date_obj = datetime.strptime(issue_str, "%Y-%m-%d")
            due_date_obj = datetime.strptime(due_str, "%Y-%m-%d")

            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT title, available_copies FROM books WHERE book_id = :1", [book_id])
                    book = cursor.fetchone()

                    if not book:
                        messagebox.showwarning("Book Not Found", "This Book ID does not exist in the library.")
                        return

                    title, copies = book
                    if not copies or copies <= 0:
                        messagebox.showinfo("Book Unavailable", f"📚 {title}\n\nThis book is currently out of stock.")
                        return

                    out_msg = cursor.var(oracledb.STRING)
                    cursor.callproc("issue_book_proc", [member_id, book_id, issue_date_obj, due_date_obj, out_msg])
                    messagebox.showinfo("Result", out_msg.getvalue())

        except ValueError:
            messagebox.showerror("Format Error", "IDs must be valid numbers and dates must be in YYYY-MM-DD format.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def calculate_fine(self):
        m_id = self.member_entry.get().strip()
        if not m_id:
            messagebox.showerror("Input Error", "Enter Member ID to check fine.")
            return

        try:
            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """SELECT t.book_id, b.title, t.issue_date, t.due_date
                            FROM library_transactions t JOIN books b ON t.book_id = b.book_id
                            WHERE t.member_id = :1 AND t.status = 'ISSUED'""",
                        [int(m_id)]
                    )
                    rows = cursor.fetchall()

            if not rows:
                self.show_scrollable_popup("Fine & Status Details", f"Member ID {m_id} has no active issued books.")
                return

            today, report, total_fine, has_overdue = datetime.now().date(), f"FINE & ISSUED BOOKS | MEMBER {m_id}\n\n", 0, False
            for b_id, title, issue_dt, due_dt in rows:
                due = due_dt.date() if hasattr(due_dt, "date") else due_dt
                if today > due:
                    days_late = (today - due).days
                    fine = days_late * 10
                    total_fine += fine
                    has_overdue = True
                    status = f"OVERDUE | Rs. {fine} ({days_late} days)"
                else:
                    status = "ON TIME | No Charge"

                report += f"Book ID: {b_id} | Title: {title}\nIssue Date: {issue_dt:%Y-%m-%d}\nDue Date: {due_dt:%Y-%m-%d}\nStatus: {status}\n{'-'*45}\n"

            report += f"\nTotal Overdue Fine: Rs. {total_fine}" if has_overdue else "\nAll books are on time. No charge!"
            self.show_scrollable_popup("Fine & Status Details", report)

        except ValueError:
            messagebox.showerror("Format Error", "Member ID must be numeric.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def view_issued_books_smart(self):
        m_id, b_id = self.member_entry.get().strip(), self.book_entry.get().strip()
        if not m_id and not b_id:
            messagebox.showerror("Input Error", "Enter Member ID or Book ID.")
            return

        try:
            if m_id: int(m_id)
            if b_id: int(b_id)

            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    if b_id and not m_id:
                        cursor.execute(
                            """SELECT t.member_id, m.name, t.book_id, b.title, t.issue_date, t.due_date
                                FROM library_transactions t JOIN members m ON t.member_id = m.member_id
                                JOIN books b ON t.book_id = b.book_id WHERE t.book_id = :1 AND t.status = 'ISSUED'""",
                            [int(b_id)]
                        )
                        rows = cursor.fetchall()
                        report = f"ISSUED RECORDS | BOOK {b_id}\n\n"
                        if not rows:
                            report = f"Book ID {b_id} has no active issue records."
                        else:
                            today = datetime.now().date()
                            for mem_id, name, bk_id, title, issue_dt, due_dt in rows:
                                due = due_dt.date() if hasattr(due_dt, "date") else due_dt
                                fine = (today - due).days * 10 if today > due else 0
                                report += f"Member ID: {mem_id} | Name: {name}\nBook: {title}\nDue Date: {due_dt:%Y-%m-%d}\nFine: Rs. {fine}\n{'-'*45}\n"
                    elif b_id:
                        cursor.execute(
                            """SELECT t.book_id, b.title, t.issue_date, t.due_date, t.status
                                FROM library_transactions t JOIN books b ON t.book_id = b.book_id
                                WHERE t.member_id = :1 AND t.book_id = :2 AND t.status = 'ISSUED'""",
                            [int(m_id), int(b_id)]
                        )
                        rows = cursor.fetchall()
                        report = self.format_member_rows(rows, f"MEMBER {m_id} | BOOK {b_id}\n\n")
                    else:
                        cursor.execute(
                            """SELECT t.book_id, b.title, t.issue_date, t.due_date, t.status
                                FROM library_transactions t JOIN books b ON t.book_id = b.book_id
                                WHERE t.member_id = :1 AND t.status = 'ISSUED'""",
                            [int(m_id)]
                        )
                        rows = cursor.fetchall()
                        report = self.format_member_rows(rows, f"ISSUED BOOKS | MEMBER {m_id}\n\n")

            self.show_scrollable_popup("Issued Books Records", report)

        except ValueError:
            messagebox.showerror("Format Error", "IDs must be valid numeric values.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def format_member_rows(self, rows, report):
        if not rows:
            return report + "No active issued books found."
        today = datetime.now().date()
        for bk_id, title, issue_dt, due_dt, status in rows:
            due = due_dt.date() if hasattr(due_dt, "date") else due_dt
            fine = (today - due).days * 10 if today > due else 0
            report += f"Book ID: {bk_id}\nTitle: {title}\nIssue Date: {issue_dt:%Y-%m-%d}\nDue Date: {due_dt:%Y-%m-%d}\nFine: Rs. {fine}\n{'-'*45}\n"
        return report

    def show_books_details(self):
        try:
            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT book_id, title, author, available_copies FROM books ORDER BY book_id ASC")
                    rows = cursor.fetchall()

            report = "📚 ALL LIBRARY BOOKS CATALOGUE\n" + "="*45 + "\n\n"
            if rows:
                for b_id, title, author, copies in rows:
                    report += f"Book ID: {b_id}\nTitle: {title}\nAuthor: {author}\nAvailable Copies: {copies}\n{'-'*45}\n"
            else:
                report = "No books found in the library database."

            self.show_scrollable_popup("Books Catalogue", report)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def reset_database_data(self):
        if not messagebox.askyesno("Confirm Reset", "Delete transaction data and reset stock?"):
            return
        try:
            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    out_msg = cursor.var(oracledb.STRING)
                    cursor.callproc("reset_library_data", [out_msg])
                    messagebox.showinfo("Reset Status", out_msg.getvalue())
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def show_scrollable_popup(self, title_text, info_text):
        popup = tk.Toplevel(self.root)
        popup.title(title_text)
        popup.geometry("520x420")
        popup.minsize(360, 280)
        popup.configure(bg=self.BG)

        header = tk.Frame(popup, bg=self.CARD_BG, padx=16, pady=12, highlightbackground=self.PRIMARY, highlightthickness=1)
        header.pack(fill="x")
        tk.Label(header, text="📋 " + title_text, font=("Segoe UI", 11, "bold"), bg=self.CARD_BG, fg=self.PRIMARY).pack(anchor="w")

        content = tk.Frame(popup, bg=self.CARD_BG, padx=8, pady=8, highlightbackground=self.BORDER, highlightthickness=1)
        content.pack(fill="both", expand=True, padx=12, pady=12)

        text = tk.Text(content, wrap="word", font=("Consolas", 10), bg=self.CARD_BG, fg=self.PRIMARY, relief="flat", padx=8, pady=8, insertbackground=self.PRIMARY)
        scroll = ttk.Scrollbar(content, orient="vertical", command=text.yview, style="Vertical.TScrollbar")
        text.configure(yscrollcommand=scroll.set)
        
        scroll.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        text.insert(tk.END, info_text)
        text.config(state="disabled")

        self.make_venom_button(popup, "Close Report", popup.destroy, self.PRIMARY).pack(pady=(0, 12))

    def open_issued_books_window(self):
        win = tk.Toplevel(self.root)
        win.title("All Issued Books Management - Venom View")
        win.geometry("920x650")
        win.configure(bg=self.BG)

        # Top Search Frame
        search_frame = tk.Frame(win, bg=self.CARD_BG, padx=12, pady=12, highlightbackground=self.PRIMARY, highlightthickness=1)
        search_frame.pack(fill="x", padx=16, pady=16)

        tk.Label(search_frame, text="Search by Member ID or Member Name:", font=("Segoe UI", 9, "bold"), bg=self.CARD_BG, fg=self.TEXT).pack(side="left", padx=(0, 8))
        
        search_var = tk.StringVar()
        search_entry_box = ttk.Entry(search_frame, textvariable=search_var, width=25)
        search_entry_box.pack(side="left", padx=(0, 8))

        def on_search():
            self.load_issued_page(win, container_frame, pagination_frame, search_var.get().strip(), page=1)

        self.make_venom_button(search_frame, "Search", on_search, self.PRIMARY).pack(side="left")

        # Pagination Footer Frame
        pagination_frame = tk.Frame(win, bg=self.BG, pady=10)
        pagination_frame.pack(side="bottom", fill="x", padx=16)

        # Scrollable Container for List
        container_outer = tk.Frame(win, bg=self.BG)
        container_outer.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        canvas = tk.Canvas(container_outer, bg=self.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_outer, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        container_frame = tk.Frame(canvas, bg=self.BG)
        window_id = canvas.create_window((0, 0), window=container_frame, anchor="nw")

        container_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))

        self.load_issued_page(win, container_frame, pagination_frame, "", page=1)

    def load_issued_page(self, win, list_frame, pagination_frame, search_query, page):
        for widget in list_frame.winfo_children():
            widget.destroy()
        for widget in pagination_frame.winfo_children():
            widget.destroy()

        try:
            offset_val = (page - 1) * 10

            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    if search_query:
                        if search_query.isdigit():
                            count_sql = "SELECT COUNT(*) FROM library_transactions WHERE status = 'ISSUED' AND member_id = :1"
                            cursor.execute(count_sql, [int(search_query)])
                        else:
                            count_sql = """SELECT COUNT(*) FROM library_transactions t 
                                        JOIN members m ON t.member_id = m.member_id 
                                        WHERE t.status = 'ISSUED' AND LOWER(m.name) LIKE LOWER(:1)"""
                            cursor.execute(count_sql, [f"%{search_query}%"])
                    else:
                        count_sql = "SELECT COUNT(*) FROM library_transactions WHERE status = 'ISSUED'"
                        cursor.execute(count_sql)

                    res_count = cursor.fetchone()
                    total_records = res_count[0] if res_count else 0

                    if search_query:
                        if search_query.isdigit():
                            sql = """
                                SELECT t.transaction_id, t.book_id, b.title, b.author, 
                                    t.member_id, m.name, t.issue_date, t.due_date
                                FROM library_transactions t
                                JOIN books b ON t.book_id = b.book_id
                                JOIN members m ON t.member_id = m.member_id
                                WHERE t.status = 'ISSUED' AND t.member_id = :1
                                ORDER BY t.issue_date DESC
                                OFFSET :2 ROWS FETCH NEXT 10 ROWS ONLY
                            """
                            cursor.execute(sql, [int(search_query), offset_val])
                        else:
                            sql = """
                                SELECT t.transaction_id, t.book_id, b.title, b.author, 
                                    t.member_id, m.name, t.issue_date, t.due_date
                                FROM library_transactions t
                                JOIN books b ON t.book_id = b.book_id
                                JOIN members m ON t.member_id = m.member_id
                                WHERE t.status = 'ISSUED' AND LOWER(m.name) LIKE LOWER(:1)
                                ORDER BY t.issue_date DESC
                                OFFSET :2 ROWS FETCH NEXT 10 ROWS ONLY
                            """
                            cursor.execute(sql, [f"%{search_query}%", offset_val])
                    else:
                        sql = """
                            SELECT t.transaction_id, t.book_id, b.title, b.author, 
                                t.member_id, m.name, t.issue_date, t.due_date
                            FROM library_transactions t
                            JOIN books b ON t.book_id = b.book_id
                            JOIN members m ON t.member_id = m.member_id
                            WHERE t.status = 'ISSUED'
                            ORDER BY t.issue_date DESC
                            OFFSET :1 ROWS FETCH NEXT 10 ROWS ONLY
                        """
                        cursor.execute(sql, [offset_val])

                    rows = cursor.fetchall()

                if not rows:
                    tk.Label(list_frame, text="No active issued books found.", font=("Segoe UI", 10), bg=self.BG, fg=self.MUTED).pack(pady=20)
                    return

                # Table Header
                hdr = tk.Frame(list_frame, bg=self.SURFACE, padx=8, pady=8, highlightbackground=self.BORDER, highlightthickness=1)
                hdr.pack(fill="x", pady=(0, 4))
                
                headers = ["Book ID", "Title & Author", "Member", "Issue / Due", "Fine Status", "Action"]
                for h in headers:
                    tk.Label(hdr, text=h, font=("Segoe UI", 9, "bold"), bg=self.SURFACE, fg=self.PRIMARY, width=12, anchor="w").pack(side="left", padx=2)

                # Rows Rendering
                today = datetime.now().date()
                for row in rows:
                    trans_id, b_id, title, author, m_id, m_name, issue_dt, due_dt = row
                    due = due_dt.date() if hasattr(due_dt, "date") else due_dt
                    
                    days_late = (today - due).days if today > due else 0
                    fine = days_late * 10

                    row_card = tk.Frame(list_frame, bg=self.CARD_BG, padx=8, pady=6, highlightbackground=self.BORDER, highlightthickness=1)
                    row_card.pack(fill="x", pady=2)

                    tk.Label(row_card, text=str(b_id), font=("Segoe UI", 9), bg=self.CARD_BG, fg=self.TEXT, width=12, anchor="w").pack(side="left", padx=2)
                    
                    book_info = f"{title}\nBy {author}"
                    tk.Label(row_card, text=book_info, font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.TEXT, width=25, anchor="w", justify="left").pack(side="left", padx=2)
                    
                    mem_info = f"ID: {m_id}\n{m_name}"
                    tk.Label(row_card, text=mem_info, font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.TEXT, width=18, anchor="w", justify="left").pack(side="left", padx=2)
                    
                    dates_info = f"Iss: {issue_dt:%Y-%m-%d}\nDue: {due_dt:%Y-%m-%d}"
                    tk.Label(row_card, text=dates_info, font=("Segoe UI", 8), bg=self.CARD_BG, fg=self.MUTED, width=18, anchor="w", justify="left").pack(side="left", padx=2)
                    
                    fine_txt = f"Rs. {fine}\n({days_late}d late)" if fine > 0 else "On Time (₹0)"
                    fine_color = self.DANGER if fine > 0 else self.SUCCESS
                    tk.Label(row_card, text=fine_txt, font=("Segoe UI", 8, "bold"), bg=self.CARD_BG, fg=fine_color, width=15, anchor="w", justify="left").pack(side="left", padx=2)

                    # Done Button (Return Book)
                    def return_action(t_id=trans_id):
                        if messagebox.askyesno("Confirm Return", "Has the user returned this book?"):
                            try:
                                with self.connect_db() as connection:
                                    with connection.cursor() as cursor:
                                        out_msg = cursor.var(oracledb.STRING)
                                        cursor.callproc("return_book_proc", [t_id, out_msg])
                                        messagebox.showinfo("Result", out_msg.getvalue())
                                        self.load_issued_page(win, list_frame, pagination_frame, search_query, page)
                            except Exception as ex:
                                messagebox.showerror("Database Error", str(ex))

                    self.make_venom_button(row_card, "Done", return_action, self.SUCCESS).pack(side="left", padx=2)

                # Pagination Footer Controls
                total_pages = max(1, (total_records + 9) // 10)
                
                tk.Label(pagination_frame, text=f"Page {page} of {total_pages} (Total Records: {total_records})", font=("Segoe UI", 9, "bold"), bg=self.BG, fg=self.TEXT).pack(side="left", padx=4)

                pages_container = tk.Frame(pagination_frame, bg=self.BG)
                pages_container.pack(side="right")

                for p in range(1, total_pages + 1):
                    btn_bg = self.PRIMARY if p == page else self.CARD_BG
                    btn_fg = "#000000" if p == page else self.TEXT
                    
                    def create_page_handler(target_page=p):
                        return lambda: self.load_issued_page(win, list_frame, pagination_frame, search_query, target_page)

                    p_btn = tk.Button(
                        pages_container, text=str(p), command=create_page_handler(),
                        bg=btn_bg, fg=btn_fg, font=("Segoe UI", 9, "bold"), relief="flat", padx=8, pady=2, cursor="hand2"
                    )
                    p_btn.pack(side="left", padx=2)

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
