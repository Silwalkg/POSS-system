import customtkinter as ctk
import auth


class Dashboard(ctk.CTk):
    def __init__(self, on_logout):
        super().__init__()
        self.on_logout = on_logout
        self.title("Happy Palace — Dashboard")
        self.geometry("900x620")
        self.minsize(800, 560)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._build()

    def _build(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a1a2e")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="🍽️", font=("Arial", 36)).pack(pady=(30, 4))
        ctk.CTkLabel(sidebar, text="HAPPY PALACE", font=("Arial", 15, "bold"),
                     text_color="#F4A261").pack()
        ctk.CTkLabel(sidebar, text=f"👤 {auth.get_username()}  [{auth.get_role()}]",
                     font=("Arial", 11), text_color="gray").pack(pady=(4, 20))

        ctk.CTkFrame(sidebar, height=1, fg_color="#333").pack(fill="x", padx=16)

        self._nav_buttons(sidebar)

        # Logout at bottom
        ctk.CTkButton(
            sidebar, text="🚪  Logout", fg_color="transparent",
            hover_color="#3a0000", text_color="#E63946",
            anchor="w", command=self._logout
        ).pack(side="bottom", padx=12, pady=20, fill="x")

        # Main content area
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f0f1a")
        self.content.pack(side="left", fill="both", expand=True)

        self._show_home()

    def _nav_buttons(self, parent):
        role = auth.get_role()

        buttons = [
            ("🏠  Home",         "home",     ["admin", "cashier", "waiter"]),
            ("🛒  New Order",    "orders",   ["admin", "cashier", "waiter"]),
            ("🍜  Menu Items",   "menu",     ["admin"]),
            ("🪑  Tables",       "tables",   ["admin", "cashier"]),
            ("👥  Customers",    "customers",["admin", "cashier"]),
            ("🏷️  Discounts",    "discounts",["admin"]),
            ("📊  Reports",      "reports",  ["admin"]),
            ("👤  Users",        "users",    ["admin"]),
        ]

        for label, key, roles in buttons:
            if role in roles:
                ctk.CTkButton(
                    parent, text=label, anchor="w",
                    fg_color="transparent", hover_color="#16213e",
                    font=("Arial", 13), height=40,
                    command=lambda k=key: self._navigate(k)
                ).pack(fill="x", padx=12, pady=2)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _navigate(self, key):
        self._clear_content()
        if key == "home":
            self._show_home()
        elif key == "orders":
            from ui.orders import OrdersFrame
            OrdersFrame(self.content).pack(fill="both", expand=True)
        elif key == "menu":
            from ui.menu_mgmt import MenuFrame
            MenuFrame(self.content).pack(fill="both", expand=True)
        elif key == "tables":
            from ui.tables import TablesFrame
            TablesFrame(self.content).pack(fill="both", expand=True)
        elif key == "customers":
            from ui.customers import CustomersFrame
            CustomersFrame(self.content).pack(fill="both", expand=True)
        elif key == "discounts":
            from ui.discounts import DiscountsFrame
            DiscountsFrame(self.content).pack(fill="both", expand=True)
        elif key == "reports":
            from ui.reports import ReportsFrame
            ReportsFrame(self.content).pack(fill="both", expand=True)
        elif key == "users":
            from ui.users import UsersFrame
            UsersFrame(self.content).pack(fill="both", expand=True)

    def _show_home(self):
        ctk.CTkLabel(
            self.content, text="Welcome back,",
            font=("Arial", 16), text_color="gray"
        ).pack(pady=(60, 0))
        ctk.CTkLabel(
            self.content, text=f"{auth.get_username().title()} 👋",
            font=("Arial", 30, "bold"), text_color="#F4A261"
        ).pack()
        ctk.CTkLabel(
            self.content, text="Happy Palace Restaurant POS",
            font=("Arial", 14), text_color="gray"
        ).pack(pady=(6, 40))

        # Quick action cards
        row = ctk.CTkFrame(self.content, fg_color="transparent")
        row.pack()

        cards = [
            ("🛒", "New Order",  "orders"),
            ("🪑", "Tables",     "tables"),
            ("📊", "Reports",    "reports"),
        ]
        for icon, label, key in cards:
            card = ctk.CTkFrame(row, width=160, height=130, corner_radius=16)
            card.pack(side="left", padx=12)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=icon, font=("Arial", 34)).pack(pady=(22, 4))
            ctk.CTkLabel(card, text=label, font=("Arial", 13, "bold")).pack()
            card.bind("<Button-1>", lambda e, k=key: self._navigate(k))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, k=key: self._navigate(k))

    def _logout(self):
        auth.logout()
        self.destroy()
        self.on_logout()
