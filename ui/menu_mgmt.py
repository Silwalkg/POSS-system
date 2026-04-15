import customtkinter as ctk
from tkinter import messagebox
import database as db


class MenuFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🍜  Menu Management", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # Left: item list
        left = ctk.CTkFrame(body, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ctk.CTkLabel(left, text="Items", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=16, pady=(14, 6))

        self.items_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.items_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Right: form
        right = ctk.CTkFrame(body, width=280, corner_radius=12)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_form(right)

        self._load_items()

    def _build_form(self, parent):
        ctk.CTkLabel(parent, text="Add / Edit Item",
                     font=("Arial", 14, "bold")).pack(padx=16, pady=(16, 10))

        self.edit_id = None

        ctk.CTkLabel(parent, text="Name", anchor="w").pack(fill="x", padx=16)
        self.entry_name = ctk.CTkEntry(parent, height=36)
        self.entry_name.pack(fill="x", padx=16, pady=(2, 10))

        ctk.CTkLabel(parent, text="Category", anchor="w").pack(fill="x", padx=16)
        self.cats = db.get_categories()
        cat_names = [c["name"] for c in self.cats]
        self.cat_var = ctk.StringVar(value=cat_names[0] if cat_names else "")
        self.cat_menu = ctk.CTkOptionMenu(parent, variable=self.cat_var,
                                          values=cat_names, height=36)
        self.cat_menu.pack(fill="x", padx=16, pady=(2, 10))

        ctk.CTkLabel(parent, text="Price (LKR)", anchor="w").pack(fill="x", padx=16)
        self.entry_price = ctk.CTkEntry(parent, height=36)
        self.entry_price.pack(fill="x", padx=16, pady=(2, 10))

        self.avail_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(parent, text="Available", variable=self.avail_var).pack(
            anchor="w", padx=16, pady=(0, 14))

        ctk.CTkButton(parent, text="💾  Save Item", height=40,
                      fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                      command=self._save_item).pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkButton(parent, text="➕  New (clear)", height=36,
                      fg_color="transparent", hover_color="#16213e",
                      command=self._clear_form).pack(fill="x", padx=16)

        # Category management
        ctk.CTkFrame(parent, height=1, fg_color="#333").pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(parent, text="Add Category", anchor="w",
                     font=("Arial", 12, "bold")).pack(fill="x", padx=16)
        self.entry_cat = ctk.CTkEntry(parent, placeholder_text="Category name", height=36)
        self.entry_cat.pack(fill="x", padx=16, pady=(4, 6))
        ctk.CTkButton(parent, text="Add Category", height=34,
                      fg_color="#16213e", command=self._add_category).pack(
            fill="x", padx=16)

    def _load_items(self):
        for w in self.items_list.winfo_children():
            w.destroy()
        items = db.get_menu_items(available_only=False)
        for item in items:
            row = ctk.CTkFrame(self.items_list, corner_radius=8, fg_color="#1a1a2e")
            row.pack(fill="x", pady=3, padx=4)

            status = "✅" if item["available"] else "❌"
            ctk.CTkLabel(row, text=f"{status} {item['name']}",
                         font=("Arial", 12), anchor="w", width=160).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=item.get("category_name", ""),
                         font=("Arial", 11), text_color="gray", width=100).pack(side="left")
            ctk.CTkLabel(row, text=f"LKR {item['price']:,.2f}",
                         text_color="#F4A261", font=("Arial", 11), width=90).pack(side="left")

            ctk.CTkButton(row, text="Edit", width=50, height=28,
                          fg_color="#16213e", hover_color="#F4A261",
                          command=lambda i=item: self._edit_item(i)).pack(side="right", padx=4)
            ctk.CTkButton(row, text="Del", width=46, height=28,
                          fg_color="transparent", hover_color="#3a0000", text_color="#E63946",
                          command=lambda i=item: self._delete_item(i)).pack(side="right", padx=2)

    def _edit_item(self, item):
        self.edit_id = item["id"]
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, item["name"])
        self.entry_price.delete(0, "end")
        self.entry_price.insert(0, str(item["price"]))
        self.avail_var.set(bool(item["available"]))
        cat = next((c for c in self.cats if c["id"] == item["category_id"]), None)
        if cat:
            self.cat_var.set(cat["name"])

    def _save_item(self):
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        cat_name = self.cat_var.get()

        if not name or not price_str:
            messagebox.showwarning("Validation", "Name and price are required.")
            return
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Enter a valid positive price.")
            return

        cat = next((c for c in self.cats if c["name"] == cat_name), None)
        cat_id = cat["id"] if cat else None

        if self.edit_id:
            db.update_menu_item(self.edit_id, name, cat_id, price, int(self.avail_var.get()))
        else:
            db.add_menu_item(name, cat_id, price)

        self._clear_form()
        self._load_items()

    def _delete_item(self, item):
        if messagebox.askyesno("Delete", f"Delete '{item['name']}'?"):
            db.delete_menu_item(item["id"])
            self._load_items()

    def _clear_form(self):
        self.edit_id = None
        self.entry_name.delete(0, "end")
        self.entry_price.delete(0, "end")
        self.avail_var.set(True)

    def _add_category(self):
        name = self.entry_cat.get().strip()
        if not name:
            return
        try:
            db.add_category(name)
            self.entry_cat.delete(0, "end")
            self.cats = db.get_categories()
            self.cat_menu.configure(values=[c["name"] for c in self.cats])
        except Exception as e:
            messagebox.showerror("Error", str(e))
