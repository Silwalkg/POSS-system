import customtkinter as ctk
from datetime import date
import database as db

CURRENCY = "LKR"


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📊  Reports", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        # Date filter
        filter_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_row.pack(fill="x", padx=20, pady=(0, 12))

        today = date.today().isoformat()
        ctk.CTkLabel(filter_row, text="From:").pack(side="left", padx=(0, 4))
        self.entry_from = ctk.CTkEntry(filter_row, width=120, height=34)
        self.entry_from.insert(0, today)
        self.entry_from.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(filter_row, text="To:").pack(side="left", padx=(0, 4))
        self.entry_to = ctk.CTkEntry(filter_row, width=120, height=34)
        self.entry_to.insert(0, today)
        self.entry_to.pack(side="left", padx=(0, 12))

        ctk.CTkButton(filter_row, text="🔍 Generate", height=34,
                      fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                      command=self._generate).pack(side="left")

        # Summary cards
        self.summary_row = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_row.pack(fill="x", padx=20, pady=(0, 12))

        # Orders table
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Top items
        self.top_frame = ctk.CTkFrame(self, corner_radius=12)
        self.top_frame.pack(fill="x", padx=16, pady=(0, 12))

        self._generate()

    def _generate(self):
        date_from = self.entry_from.get().strip()
        date_to = self.entry_to.get().strip()

        # Summary
        for w in self.summary_row.winfo_children():
            w.destroy()
        summary = db.get_report_summary(date_from, date_to)
        cards = [
            ("Orders",    str(summary["total_orders"]),          "#2ec4b6"),
            ("Gross",     f"{CURRENCY} {summary['gross']:,.2f}", "#F4A261"),
            ("Discounts", f"{CURRENCY} {summary['discounts']:,.2f}", "#E63946"),
            ("Net Total", f"{CURRENCY} {summary['net']:,.2f}",   "#2ec4b6"),
        ]
        for label, value, color in cards:
            card = ctk.CTkFrame(self.summary_row, corner_radius=12, fg_color="#1a1a2e",
                                width=170, height=80)
            card.pack(side="left", padx=8)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=label, font=("Arial", 11),
                         text_color="gray").pack(pady=(12, 0))
            ctk.CTkLabel(card, text=value, font=("Arial", 14, "bold"),
                         text_color=color).pack()

        # Orders list
        for w in self.table_frame.winfo_children():
            w.destroy()

        # Header
        header = ctk.CTkFrame(self.table_frame, fg_color="#16213e", corner_radius=6)
        header.pack(fill="x", pady=(0, 4))
        for col, w in [("Order #", 70), ("Date/Time", 150), ("Cashier", 100),
                       ("Table", 60), ("Customer", 120),
                       ("Subtotal", 100), ("Discount", 90), ("Total", 100)]:
            ctk.CTkLabel(header, text=col, font=("Arial", 11, "bold"),
                         width=w, anchor="w").pack(side="left", padx=6, pady=6)

        orders = db.get_sales_report(date_from, date_to)
        for o in orders:
            row = ctk.CTkFrame(self.table_frame, corner_radius=6, fg_color="#1a1a2e")
            row.pack(fill="x", pady=2)
            vals = [
                (f"#{o['id']}", 70),
                (o["created_at"][:16], 150),
                (o["cashier"], 100),
                (str(o["table_number"] or "—"), 60),
                (o["customer_name"] or "—", 120),
                (f"{CURRENCY} {o['subtotal']:,.2f}", 100),
                (f"{CURRENCY} {o['discount_amount']:,.2f}", 90),
                (f"{CURRENCY} {o['total']:,.2f}", 100),
            ]
            for val, w in vals:
                ctk.CTkLabel(row, text=val, font=("Arial", 11),
                             width=w, anchor="w").pack(side="left", padx=6, pady=5)

        # Top items
        for w in self.top_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.top_frame, text="🏆 Top Selling Items",
                     font=("Arial", 13, "bold")).pack(anchor="w", padx=16, pady=(12, 6))
        top_items = db.get_top_items(date_from, date_to)
        if top_items:
            for i, item in enumerate(top_items, 1):
                row = ctk.CTkFrame(self.top_frame, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(row, text=f"{i}. {item['name']}",
                             font=("Arial", 12), anchor="w", width=200).pack(side="left")
                ctk.CTkLabel(row, text=f"Qty: {item['qty']}",
                             text_color="#2ec4b6", width=80).pack(side="left")
                ctk.CTkLabel(row, text=f"{CURRENCY} {item['revenue']:,.2f}",
                             text_color="#F4A261").pack(side="left")
        else:
            ctk.CTkLabel(self.top_frame, text="No data for selected period.",
                         text_color="gray").pack(pady=8)
        ctk.CTkFrame(self.top_frame, height=8, fg_color="transparent").pack()
