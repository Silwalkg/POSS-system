import customtkinter as ctk
from tkinter import messagebox
import database as db


class CustomersFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="👥  Customers", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # List
        left = ctk.CTkFrame(body, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(left, text="Customer List", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=16, pady=(14, 6))
        self.list_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Form
        right = ctk.CTkFrame(body, width=260, corner_radius=12)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_form(right)

        self._load_customers()

    def _build_form(self, parent):
        ctk.CTkLabel(parent, text="Add Customer",
                     font=("Arial", 14, "bold")).pack(padx=16, pady=(16, 10))

        for label, attr, ph in [
            ("Name *", "entry_name", "Full name"),
            ("Phone", "entry_phone", "07X XXXXXXX"),
            ("Email", "entry_email", "email@example.com"),
        ]:
            ctk.CTkLabel(parent, text=label, anchor="w").pack(fill="x", padx=16)
            entry = ctk.CTkEntry(parent, placeholder_text=ph, height=36)
            entry.pack(fill="x", padx=16, pady=(2, 10))
            setattr(self, attr, entry)

        ctk.CTkButton(parent, text="💾  Save Customer", height=40,
                      fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                      command=self._save_customer).pack(fill="x", padx=16, pady=(4, 0))

    def _load_customers(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for c in db.get_customers():
            row = ctk.CTkFrame(self.list_frame, corner_radius=8, fg_color="#1a1a2e")
            row.pack(fill="x", pady=3, padx=4)
            ctk.CTkLabel(row, text=c["name"], font=("Arial", 12, "bold"),
                         anchor="w", width=140).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=c["phone"] or "—", font=("Arial", 11),
                         text_color="gray", width=110).pack(side="left")
            ctk.CTkLabel(row, text=c["email"] or "—", font=("Arial", 11),
                         text_color="gray").pack(side="left", padx=6)
            ctk.CTkButton(row, text="Del", width=46, height=28,
                          fg_color="transparent", hover_color="#3a0000", text_color="#E63946",
                          command=lambda cid=c["id"]: self._delete(cid)).pack(
                side="right", padx=8)

    def _save_customer(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Name is required.")
            return
        try:
            db.add_customer(name, phone, email)
            for e in [self.entry_name, self.entry_phone, self.entry_email]:
                e.delete(0, "end")
            self._load_customers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self, cid):
        if messagebox.askyesno("Delete", "Delete this customer?"):
            db.delete_customer(cid)
            self._load_customers()
