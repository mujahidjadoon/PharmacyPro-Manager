import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# UI Configuration
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class PharmacyPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacy Manager Pro - Billing & Ledger")
        self.geometry("1100x750")
        self.init_db()

        # Grid System
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="PHARMACY\nPRO", font=("Arial", 26, "bold")).pack(pady=30)

        ctk.CTkButton(self.sidebar, text="Add Purchase", command=self.show_purchase_entry).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Add Sale", command=self.show_sales_entry).pack(pady=10, padx=20)

        ctk.CTkLabel(self.sidebar, text="--- LEDGERS ---", font=("Arial", 12)).pack(pady=15)

        ctk.CTkButton(self.sidebar, text="Purchase Records", fg_color="#2c3e50",
                      command=self.show_purchase_ledger).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Sales Records", fg_color="#2c3e50", command=self.show_sales_ledger).pack(
            pady=10, padx=20)

        # --- Main View ---
        self.main_container = ctk.CTkFrame(self, corner_radius=15)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.show_purchase_ledger()  # Default screen

    def init_db(self):
        conn = sqlite3.connect("pharmacy_pro.db")
        cursor = conn.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS purchase (id INTEGER PRIMARY KEY, med_name TEXT, company TEXT, qty INTEGER, price REAL, date TEXT)')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, hospital TEXT, med_name TEXT, qty INTEGER, total REAL, date TEXT)')
        conn.commit()
        conn.close()

    def clear_view(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # --- PURCHASE ENTRY ---
    def show_purchase_entry(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="Stock Entry (Purchase)", font=("Arial", 20, "bold")).pack(pady=20)
        self.p_med = ctk.CTkEntry(self.main_container, placeholder_text="Medicine Name", width=350);
        self.p_med.pack(pady=10)
        self.p_com = ctk.CTkEntry(self.main_container, placeholder_text="Supplier Name", width=350);
        self.p_com.pack(pady=10)
        self.p_qty = ctk.CTkEntry(self.main_container, placeholder_text="Qty", width=350);
        self.p_qty.pack(pady=10)
        self.p_prc = ctk.CTkEntry(self.main_container, placeholder_text="Purchase Price", width=350);
        self.p_prc.pack(pady=10)
        ctk.CTkButton(self.main_container, text="Save Purchase", fg_color="green", command=self.save_purchase).pack(
            pady=20)

    def save_purchase(self):
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("pharmacy_pro.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO purchase (med_name, company, qty, price, date) VALUES (?, ?, ?, ?, ?)",
                       (self.p_med.get(), self.p_com.get(), int(self.p_qty.get()), float(self.p_prc.get()), date))
        conn.commit()
        conn.close()
        messagebox.showinfo("Done", "Purchase Added!")
        self.show_purchase_ledger()

    # --- SALES ENTRY ---
    def show_sales_entry(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="New Sale Bill", font=("Arial", 20, "bold")).pack(pady=20)
        self.s_hosp = ctk.CTkEntry(self.main_container, placeholder_text="Hospital Name", width=350);
        self.s_hosp.pack(pady=10)
        self.s_med = ctk.CTkEntry(self.main_container, placeholder_text="Medicine Name", width=350);
        self.s_med.pack(pady=10)
        self.s_qty = ctk.CTkEntry(self.main_container, placeholder_text="Qty Sold", width=350);
        self.s_qty.pack(pady=10)
        self.s_tot = ctk.CTkEntry(self.main_container, placeholder_text="Total Amount", width=350);
        self.s_tot.pack(pady=10)
        ctk.CTkButton(self.main_container, text="Generate Bill Sale", fg_color="blue", command=self.save_sale).pack(
            pady=20)

    def save_sale(self):
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("pharmacy_pro.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sales (hospital, med_name, qty, total, date) VALUES (?, ?, ?, ?, ?)",
                       (self.s_hosp.get(), self.s_med.get(), int(self.s_qty.get()), float(self.s_tot.get()), date))
        conn.commit()
        conn.close()
        messagebox.showinfo("Done", "Sale Recorded!")
        self.show_sales_ledger()

    # --- PURCHASE LEDGER VIEW ---
    def show_purchase_ledger(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="PURCHASE RECORDS", font=("Arial", 20, "bold")).pack(pady=10)

        search_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_f.pack(fill="x", padx=20)
        self.p_search = ctk.CTkEntry(search_f, placeholder_text="Search Medicine/Company...", width=300)
        self.p_search.pack(side="left", padx=10)
        ctk.CTkButton(search_f, text="Search", command=self.load_purchase).pack(side="left", padx=5)
        ctk.CTkButton(search_f, text="Print Purchase PDF", fg_color="#c0392b",
                      command=lambda: self.print_pdf("Purchase")).pack(side="left", padx=5)

        self.p_tree = ttk.Treeview(self.main_container, columns=(1, 2, 3, 4, 5), show="headings")
        for i, col in enumerate(["Date", "Supplier", "Medicine", "Qty", "Amount"], 1):
            self.p_tree.heading(i, text=col)
        self.p_tree.pack(pady=20, padx=20, fill="both", expand=True)
        self.load_purchase()

    # --- SALES LEDGER VIEW ---
    def show_sales_ledger(self):
        self.clear_view()
        ctk.CTkLabel(self.main_container, text="SALES RECORDS", font=("Arial", 20, "bold")).pack(pady=10)

        search_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_f.pack(fill="x", padx=20)
        self.s_search = ctk.CTkEntry(search_f, placeholder_text="Search Medicine/Hospital...", width=300)
        self.s_search.pack(side="left", padx=10)
        ctk.CTkButton(search_f, text="Search", command=self.load_sales).pack(side="left", padx=5)
        ctk.CTkButton(search_f, text="Print Sales PDF", fg_color="#2980b9",
                      command=lambda: self.print_pdf("Sales")).pack(side="left", padx=5)

        self.s_tree = ttk.Treeview(self.main_container, columns=(1, 2, 3, 4, 5), show="headings")
        for i, col in enumerate(["Date", "Hospital", "Medicine", "Qty", "Total Bill"], 1):
            self.s_tree.heading(i, text=col)
        self.s_tree.pack(pady=20, padx=20, fill="both", expand=True)
        self.load_sales()

    def load_purchase(self):
        q = self.p_search.get().lower()
        for r in self.p_tree.get_children(): self.p_tree.delete(r)
        conn = sqlite3.connect("pharmacy_pro.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, company, med_name, qty, price FROM purchase WHERE lower(med_name) LIKE ? OR lower(company) LIKE ? ORDER BY date DESC",
            ('%' + q + '%', '%' + q + '%'))
        for row in cursor.fetchall(): self.p_tree.insert("", "end", values=row)
        conn.close()

    def load_sales(self):
        q = self.s_search.get().lower()
        for r in self.s_tree.get_children(): self.s_tree.delete(r)
        conn = sqlite3.connect("pharmacy_pro.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, hospital, med_name, qty, total FROM sales WHERE lower(med_name) LIKE ? OR lower(hospital) LIKE ? ORDER BY date DESC",
            ('%' + q + '%', '%' + q + '%'))
        for row in cursor.fetchall(): self.s_tree.insert("", "end", values=row)
        conn.close()

    def print_pdf(self, report_type):
        filename = f"{report_type}_Ledger_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, f"PHARMACY PRO - {report_type.upper()} REPORT")
        c.setFont("Helvetica", 10)
        c.drawString(50, 780, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.line(50, 775, 550, 775)

        y = 750
        headers = "Date | Entity Name | Item Name | Qty | Total Amount"
        c.drawString(50, y, headers)
        c.line(50, y - 5, 550, y - 5)
        y -= 30

        target_tree = self.p_tree if report_type == "Purchase" else self.s_tree
        for child in target_tree.get_children():
            row = target_tree.item(child)["values"]
            text_line = f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}"
            c.drawString(50, y, text_line)
            y -= 20
            if y < 50: c.showPage(); y = 800

        c.save()
        messagebox.showinfo("Export Successful", f"{report_type} PDF has been saved as {filename}")


if __name__ == "__main__":
    app = PharmacyPro()
    app.mainloop()