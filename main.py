
    import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import os
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Theme settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class PharmacyProFinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacy Pro - Ultimate Intelligence Edition")
        self.geometry("1300x900")
        self.db_name = "pharmacy_pro_v5.db"  # Version updated to avoid column errors
        self.init_db()
        self.setup_ui()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS purchase 
            (id INTEGER PRIMARY KEY, med_name TEXT, company TEXT, qty INTEGER, p_price REAL, total_p REAL, expiry TEXT, date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales 
            (id INTEGER PRIMARY KEY, hospital TEXT, med_name TEXT, qty INTEGER, s_price REAL, total REAL, date TEXT)''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="PHARMACY\nULTIMATE", font=("Arial", 28, "bold")).pack(pady=40)

        ctk.CTkButton(self.sidebar, text="📊 Analytics Dashboard", command=self.show_dashboard).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="➕ Add Stock", command=self.show_stock_entry).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="🧾 Generate Sale", command=self.show_sale_entry).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="📂 Purchase Ledger", fg_color="#34495e",
                      command=self.show_purchase_ledger).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="💰 Sales Ledger", fg_color="#34495e", command=self.show_sales_ledger).pack(
            pady=10, padx=20)

        self.main_container = ctk.CTkFrame(self, corner_radius=15)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="BUSINESS INTELLIGENCE DASHBOARD", font=("Arial", 24, "bold")).pack(
            pady=10)

        # --- TOP BOXES: TODAY'S MONEY ---
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_p) FROM purchase WHERE date LIKE ?", (today + '%',))
        today_p = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(total) FROM sales WHERE date LIKE ?", (today + '%',))
        today_s = cursor.fetchone()[0] or 0
        conn.close()

        box_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        box_frame.pack(pady=10)

        b1 = ctk.CTkFrame(box_frame, width=280, height=100, fg_color="#e74c3c", corner_radius=10)
        b1.grid(row=0, column=0, padx=15)
        ctk.CTkLabel(b1, text="TODAY'S PURCHASE", text_color="white").place(relx=0.5, rely=0.3, anchor="center")
        ctk.CTkLabel(b1, text=f"PKR {today_p:,.0f}", font=("Arial", 20, "bold"), text_color="white").place(relx=0.5,
                                                                                                           rely=0.7,
                                                                                                           anchor="center")

        b2 = ctk.CTkFrame(box_frame, width=280, height=100, fg_color="#27ae60", corner_radius=10)
        b2.grid(row=0, column=1, padx=15)
        ctk.CTkLabel(b2, text="TODAY'S SALES", text_color="white").place(relx=0.5, rely=0.3, anchor="center")
        ctk.CTkLabel(b2, text=f"PKR {today_s:,.0f}", font=("Arial", 20, "bold"), text_color="white").place(relx=0.5,
                                                                                                           rely=0.7,
                                                                                                           anchor="center")

        ctk.CTkButton(self.main_container, text="Print Today's Financial Report",
                      command=lambda: self.print_daily_report(today)).pack(pady=5)

        # --- GRAPH: LAST 7 DAYS ---
        fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
        days, sales_vals = [], []
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            days.append(d[5:])  # MM-DD
            cursor.execute("SELECT SUM(total) FROM sales WHERE date LIKE ?", (d + '%',))
            sales_vals.append(cursor.fetchone()[0] or 0)
        conn.close()

        ax.bar(days, sales_vals, color='#3498db')
        ax.set_title("Sales Performance (Last 7 Days)")
        ax.set_ylabel("PKR Amount")

        canvas_graph = FigureCanvasTkAgg(fig, master=self.main_container)
        canvas_graph.draw()
        canvas_graph.get_tk_widget().pack(pady=10, padx=20, fill="both", expand=True)

    def print_daily_report(self, t_date):
        filename = f"Daily_Report_{t_date}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, f"DAILY CLOSING REPORT - {t_date}")
        c.setFont("Helvetica", 10)
        c.line(50, 785, 550, 785)

        y = 760
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        c.drawString(50, y, "SALES SUMMARY:");
        y -= 20
        cursor.execute("SELECT med_name, qty, total FROM sales WHERE date LIKE ?", (t_date + '%',))
        ts = 0
        for n, q, t in cursor.fetchall():
            c.drawString(70, y, f"{n} - Qty: {q} - Rs.{t}");
            y -= 15;
            ts += t

        y -= 20;
        c.drawString(50, y, "PURCHASE SUMMARY:");
        y -= 20
        cursor.execute("SELECT med_name, qty, total_p FROM purchase WHERE date LIKE ?", (t_date + '%',))
        tp = 0
        for n, q, t in cursor.fetchall():
            c.drawString(70, y, f"{n} - Qty: {q} - Rs.{t}");
            y -= 15;
            tp += t

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 100, f"TOTAL SALES: PKR {ts}")
        c.drawString(50, 80, f"TOTAL PURCHASE: PKR {tp}")
        conn.close()
        c.save()
        messagebox.showinfo("Success", f"PDF Report generated: {filename}")

    # --- INPUT LOGIC ---
    def show_stock_entry(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="Stock Entry", font=("Arial", 22, "bold")).pack(pady=20)
        self.p_med = ctk.CTkEntry(self.main_container, placeholder_text="Medicine Name", width=400);
        self.p_med.pack(pady=10)
        self.p_com = ctk.CTkEntry(self.main_container, placeholder_text="Company", width=400);
        self.p_com.pack(pady=10)
        self.p_qty = ctk.CTkEntry(self.main_container, placeholder_text="Qty", width=400);
        self.p_qty.pack(pady=10)
        self.p_prc = ctk.CTkEntry(self.main_container, placeholder_text="Purchase Price", width=400);
        self.p_prc.pack(pady=10)
        self.p_exp = ctk.CTkEntry(self.main_container, placeholder_text="Expiry (MM-YYYY)", width=400);
        self.p_exp.pack(pady=10)
        ctk.CTkButton(self.main_container, text="Save Stock", fg_color="green", command=self.save_p).pack(pady=20)

    def save_p(self):
        try:
            qty, prc = int(self.p_qty.get()), float(self.p_prc.get())
            tot = qty * prc
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO purchase (med_name, company, qty, p_price, total_p, expiry, date) VALUES (?,?,?,?,?,?,?)",
                (self.p_med.get(), self.p_com.get(), qty, prc, tot, self.p_exp.get(), date))
            conn.commit();
            conn.close()
            messagebox.showinfo("Saved", "Stock Added!")
            self.show_dashboard()
        except:
            messagebox.showerror("Error", "Check Inputs!")

    def show_sale_entry(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="Generate Sale", font=("Arial", 22, "bold")).pack(pady=20)
        self.s_hosp = ctk.CTkEntry(self.main_container, placeholder_text="Hospital Name", width=400);
        self.s_hosp.pack(pady=10)
        self.s_med = ctk.CTkEntry(self.main_container, placeholder_text="Medicine Name", width=400);
        self.s_med.pack(pady=10)
        self.s_qty = ctk.CTkEntry(self.main_container, placeholder_text="Qty", width=400);
        self.s_qty.pack(pady=10)
        self.s_prc = ctk.CTkEntry(self.main_container, placeholder_text="Sale Price", width=400);
        self.s_prc.pack(pady=10)
        ctk.CTkButton(self.main_container, text="Complete Sale", fg_color="blue", command=self.save_s).pack(pady=20)

    def save_s(self):
        try:
            qty, prc = int(self.s_qty.get()), float(self.s_prc.get())
            tot = qty * prc
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sales (hospital, med_name, qty, s_price, total, date) VALUES (?,?,?,?,?,?)",
                           (self.s_hosp.get(), self.s_med.get(), qty, prc, tot, date))
            conn.commit();
            conn.close()
            messagebox.showinfo("Saved", "Sale Done!")
            self.show_dashboard()
        except:
            messagebox.showerror("Error", "Check Inputs!")

    def show_purchase_ledger(self):
        self.clear_view()
        tree = ttk.Treeview(self.main_container, columns=(1, 2, 3, 4, 5), show="headings")
        for i, col in enumerate(["Date", "Supplier", "Medicine", "Qty", "Total"], 1): tree.heading(i, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=20)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT date, company, med_name, qty, total_p FROM purchase ORDER BY date DESC")
        for row in cursor.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def show_sales_ledger(self):
        self.clear_view()
        tree = ttk.Treeview(self.main_container, columns=(1, 2, 3, 4, 5), show="headings")
        for i, col in enumerate(["Date", "Hospital", "Medicine", "Qty", "Total"], 1): tree.heading(i, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=20)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT date, hospital, med_name, qty, total FROM sales ORDER BY date DESC")
        for row in cursor.fetchall(): tree.insert("", "end", values=row)
        conn.close()

    def clear_view(self):
        for widget in self.main_container.winfo_children(): widget.destroy()


if __name__ == "__main__":
    app = PharmacyProFinal()
    app.mainloop()
