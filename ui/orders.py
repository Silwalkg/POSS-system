import customtkinter as ctk
from tkinter import messagebox
import database as db
import auth

CURRENCY = "LKR"


class OrdersFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.cart = []          # list of {menu_item_id, name, price, quantity}
        self.selected_table = None
        self.selected_customer = None
        self.applied_discount = None
        self._build()

    def _build(self):
        # Title
        ctk.CTkLabel(self, text="🛒  New Order", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # Left: menu panel
        left = ctk.CTkFrame(body, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._build_menu_panel(left)

        # Right: cart panel
        right = ctk.CTkFrame(body, width=320, corner_radius=12)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_cart_panel(right)

    # ── Menu Panel ────────────────────────────────────────────────────────────

    def _build_menu_panel(self, parent):
        ctk.CTkLabel(parent, text="Menu", font=("Arial", 15, "bold")).pack(
            anchor="w", padx=16, pady=(14, 6))

        # Category filter
        cats = [{"id": None, "name": "All"}] + db.get_categories()
        self.cat_var = ctk.StringVar(value="All")
        cat_row = ctk.CTkFrame(parent, fg_color="transparent")
        cat_row.pack(fill="x", padx=12, pady=(0, 8))
        for c in cats:
            ctk.CTkButton(
                cat_row, text=c["name"], width=90, height=30,
                fg_color="#16213e", hover_color="#F4A261",
                command=lambda cid=c["id"]: self._load_items(cid)
            ).pack(side="left", padx=4)

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_items())
        ctk.CTkEntry(parent, textvariable=self.search_var,
                     placeholder_text="🔍 Search item...", height=36).pack(
            fill="x", padx=12, pady=(0, 8))

        # Items grid (scrollable)
        self.items_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.items_scroll.columnconfigure((0, 1, 2), weight=1)
        self.items_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.all_items = []
        self._load_items(None)

    def _load_items(self, category_id):
        self.all_items = db.get_menu_items(category_id=category_id)
        self._render_items(self.all_items)

    def _filter_items(self):
        q = self.search_var.get().lower()
        filtered = [i for i in self.all_items if q in i["name"].lower()]
        self._render_items(filtered)

    def _render_items(self, items):
        for w in self.items_scroll.winfo_children():
            w.destroy()
        for idx, item in enumerate(items):
            card = ctk.CTkFrame(self.items_scroll, corner_radius=10, fg_color="#1a1a2e")
            card.grid(row=idx // 3, column=idx % 3, padx=6, pady=6, sticky="nsew")
            ctk.CTkLabel(card, text=item["name"], font=("Arial", 12, "bold"),
                         wraplength=110).pack(pady=(12, 2), padx=8)
            ctk.CTkLabel(card, text=f"{CURRENCY} {item['price']:,.2f}",
                         text_color="#F4A261", font=("Arial", 11)).pack()
            ctk.CTkButton(card, text="+ Add", height=28, width=80,
                          fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                          command=lambda i=item: self._add_to_cart(i)).pack(pady=(6, 10))

    # ── Cart Panel ────────────────────────────────────────────────────────────

    def _build_cart_panel(self, parent):
        ctk.CTkLabel(parent, text="Order Summary", font=("Arial", 15, "bold")).pack(
            anchor="w", padx=16, pady=(14, 6))

        # Table & Customer
        info = ctk.CTkFrame(parent, fg_color="transparent")
        info.pack(fill="x", padx=12)

        tables = db.get_tables()
        table_opts = ["No Table"] + [f"Table {t['number']}" for t in tables]
        self._tables_data = {f"Table {t['number']}": t["id"] for t in tables}
        self.table_var = ctk.StringVar(value="No Table")
        ctk.CTkOptionMenu(info, variable=self.table_var, values=table_opts,
                          width=130, height=32).pack(side="left", padx=(0, 6))

        self.cust_entry = ctk.CTkEntry(info, placeholder_text="Customer phone",
                                       width=130, height=32)
        self.cust_entry.pack(side="left")
        self.cust_entry.bind("<Return>", lambda e: self._lookup_customer())

        # Cart list
        self.cart_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=220)
        self.cart_scroll.pack(fill="x", padx=8, pady=8)

        # Discount
        disc_row = ctk.CTkFrame(parent, fg_color="transparent")
        disc_row.pack(fill="x", padx=12, pady=(0, 6))
        self.disc_entry = ctk.CTkEntry(disc_row, placeholder_text="Discount code",
                                       height=32)
        self.disc_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(disc_row, text="Apply", width=70, height=32,
                      fg_color="#16213e", command=self._apply_discount).pack(side="left")

        self.lbl_discount = ctk.CTkLabel(parent, text="", text_color="#2ec4b6",
                                         font=("Arial", 11))
        self.lbl_discount.pack(anchor="w", padx=14)

        # Totals
        totals = ctk.CTkFrame(parent, corner_radius=10, fg_color="#16213e")
        totals.pack(fill="x", padx=12, pady=8)
        self.lbl_subtotal = ctk.CTkLabel(totals, text="Subtotal:  LKR 0.00",
                                          font=("Arial", 12))
        self.lbl_subtotal.pack(anchor="w", padx=14, pady=(10, 2))
        self.lbl_disc_amt = ctk.CTkLabel(totals, text="Discount:  LKR 0.00",
                                          font=("Arial", 12), text_color="#2ec4b6")
        self.lbl_disc_amt.pack(anchor="w", padx=14, pady=2)
        self.lbl_total = ctk.CTkLabel(totals, text="TOTAL:  LKR 0.00",
                                       font=("Arial", 15, "bold"), text_color="#F4A261")
        self.lbl_total.pack(anchor="w", padx=14, pady=(2, 10))

        # Place order
        ctk.CTkButton(
            parent, text="✅  Place Order", height=44,
            fg_color="#F4A261", hover_color="#E76F51", text_color="black",
            font=("Arial", 14, "bold"), command=self._place_order
        ).pack(fill="x", padx=12, pady=(4, 6))

        ctk.CTkButton(
            parent, text="🗑️  Clear Cart", height=34,
            fg_color="transparent", hover_color="#3a0000", text_color="#E63946",
            command=self._clear_cart
        ).pack(fill="x", padx=12, pady=(0, 10))

    def _add_to_cart(self, item):
        for c in self.cart:
            if c["menu_item_id"] == item["id"]:
                c["quantity"] += 1
                self._refresh_cart()
                return
        self.cart.append({
            "menu_item_id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": 1
        })
        self._refresh_cart()

    def _refresh_cart(self):
        for w in self.cart_scroll.winfo_children():
            w.destroy()

        for item in self.cart:
            row = ctk.CTkFrame(self.cart_scroll, corner_radius=8, fg_color="#1a1a2e")
            row.pack(fill="x", pady=3, padx=4)

            ctk.CTkLabel(row, text=item["name"], font=("Arial", 11),
                         anchor="w", width=110).pack(side="left", padx=8)

            # Qty controls
            ctk.CTkButton(row, text="−", width=26, height=26,
                          fg_color="#333", hover_color="#555",
                          command=lambda i=item: self._change_qty(i, -1)).pack(side="left")
            ctk.CTkLabel(row, text=str(item["quantity"]), width=28,
                         font=("Arial", 12, "bold")).pack(side="left")
            ctk.CTkButton(row, text="+", width=26, height=26,
                          fg_color="#333", hover_color="#555",
                          command=lambda i=item: self._change_qty(i, 1)).pack(side="left")

            ctk.CTkLabel(row, text=f"{CURRENCY} {item['price']*item['quantity']:,.2f}",
                         font=("Arial", 11), text_color="#F4A261",
                         width=90, anchor="e").pack(side="right", padx=8)

        self._update_totals()

    def _change_qty(self, item, delta):
        item["quantity"] += delta
        if item["quantity"] <= 0:
            self.cart.remove(item)
        self._refresh_cart()

    def _update_totals(self):
        subtotal = sum(i["price"] * i["quantity"] for i in self.cart)
        disc_pct = self.applied_discount["percentage"] if self.applied_discount else 0
        disc_amt = subtotal * disc_pct / 100
        total = subtotal - disc_amt

        self.lbl_subtotal.configure(text=f"Subtotal:  {CURRENCY} {subtotal:,.2f}")
        self.lbl_disc_amt.configure(text=f"Discount:  {CURRENCY} {disc_amt:,.2f}")
        self.lbl_total.configure(text=f"TOTAL:  {CURRENCY} {total:,.2f}")

    def _apply_discount(self):
        code = self.disc_entry.get().strip()
        if not code:
            return
        disc = db.get_discount_by_code(code)
        if disc:
            self.applied_discount = disc
            self.lbl_discount.configure(
                text=f"✓ {disc['percentage']}% discount applied")
            self._update_totals()
        else:
            self.applied_discount = None
            self.lbl_discount.configure(text="✗ Invalid or inactive code",
                                         text_color="#E63946")
            self._update_totals()

    def _lookup_customer(self):
        phone = self.cust_entry.get().strip()
        cust = db.search_customer_by_phone(phone)
        if cust:
            self.selected_customer = cust
            messagebox.showinfo("Customer Found", f"Customer: {cust['name']}")
        else:
            self.selected_customer = None

    def _place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items before placing an order.")
            return

        table_sel = self.table_var.get()
        table_id = self._tables_data.get(table_sel)
        customer_id = self.selected_customer["id"] if self.selected_customer else None

        subtotal = sum(i["price"] * i["quantity"] for i in self.cart)
        disc_pct = self.applied_discount["percentage"] if self.applied_discount else 0
        disc_amt = subtotal * disc_pct / 100
        total = subtotal - disc_amt
        disc_id = self.applied_discount["id"] if self.applied_discount else None

        try:
            order_id = db.place_order(
                table_id=table_id,
                customer_id=customer_id,
                cashier=auth.get_username(),
                discount_id=disc_id,
                subtotal=subtotal,
                discount_amount=disc_amt,
                total=total,
                items=self.cart
            )
            messagebox.showinfo(
                "Order Placed",
                f"Order #{order_id} placed successfully!\n\nTotal: {CURRENCY} {total:,.2f}"
            )
            self._clear_cart()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order:\n{e}")

    def _clear_cart(self):
        self.cart.clear()
        self.applied_discount = None
        self.selected_customer = None
        self.lbl_discount.configure(text="")
        self.disc_entry.delete(0, "end")
        self.cust_entry.delete(0, "end")
        self._refresh_cart()
