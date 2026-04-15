import customtkinter as ctk
from tkinter import messagebox
import database as db


class DiscountsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🏷️  Discounts", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # List
        left = ctk.CTkFrame(body, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(left, text="Discount Codes", font=("Arial", 14, "bold")).pack(
            anchor="w", padx=16, pady=(14, 6))
        self.list_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Form
        right = ctk.CTkFrame(body, width=260, corner_radius=12)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_form(right)

        self._load()

    def _build_form(self, parent):
        ctk.CTkLabel(parent, text="Add / Edit Discount",
                     font=("Arial", 14, "bold")).pack(padx=16, pady=(16, 10))
        self.edit_id = None

        ctk.CTkLabel(parent, text="Code *", anchor="w").pack(fill="x", padx=16)
        self.entry_code = ctk.CTkEntry(parent, placeholder_text="e.g. HAPPY10", height=36)
        self.entry_code.pack(fill="x", padx=16, pady=(2, 10))

        ctk.CTkLabel(parent, text="Percentage (%) *", anchor="w").pack(fill="x", padx=16)
        self.entry_pct = ctk.CTkEntry(parent, placeholder_text="e.g. 10", height=36)
        self.entry_pct.pack(fill="x", padx=16, pady=(2, 10))

        self.active_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(parent, text="Active", variable=self.active_var).pack(
            anchor="w", padx=16, pady=(0, 14))

        ctk.CTkButton(parent, text="💾  Save", height=40,
                      fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                      command=self._save).pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkButton(parent, text="➕  New", height=34,
                      fg_color="transparent", hover_color="#16213e",
                      command=self._clear_form).pack(fill="x", padx=16)

    def _load(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for d in db.get_discounts():
            row = ctk.CTkFrame(self.list_frame, corner_radius=8, fg_color="#1a1a2e")
            row.pack(fill="x", pady=3, padx=4)
            status = "✅" if d["active"] else "❌"
            ctk.CTkLabel(row, text=f"{status} {d['code']}",
                         font=("Arial", 12, "bold"), anchor="w", width=120).pack(
                side="left", padx=10)
            ctk.CTkLabel(row, text=f"{d['percentage']}%",
                         text_color="#F4A261", font=("Arial", 12), width=60).pack(side="left")
            ctk.CTkButton(row, text="Edit", width=50, height=28,
                          fg_color="#16213e", hover_color="#F4A261",
                          command=lambda disc=d: self._edit(disc)).pack(side="right", padx=4)
            ctk.CTkButton(row, text="Del", width=46, height=28,
                          fg_color="transparent", hover_color="#3a0000", text_color="#E63946",
                          command=lambda did=d["id"]: self._delete(did)).pack(
                side="right", padx=2)

    def _edit(self, d):
        self.edit_id = d["id"]
        self.entry_code.delete(0, "end")
        self.entry_code.insert(0, d["code"])
        self.entry_pct.delete(0, "end")
        self.entry_pct.insert(0, str(d["percentage"]))
        self.active_var.set(bool(d["active"]))

    def _save(self):
        code = self.entry_code.get().strip().upper()
        pct_str = self.entry_pct.get().strip()
        if not code or not pct_str:
            messagebox.showwarning("Validation", "Code and percentage are required.")
            return
        try:
            pct = float(pct_str)
            if not (0 < pct <= 100):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Percentage must be between 1 and 100.")
            return
        try:
            if self.edit_id:
                db.update_discount(self.edit_id, code, pct, int(self.active_var.get()))
            else:
                db.add_discount(code, pct)
            self._clear_form()
            self._load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self, did):
        if messagebox.askyesno("Delete", "Delete this discount?"):
            db.delete_discount(did)
            self._load()

    def _clear_form(self):
        self.edit_id = None
        self.entry_code.delete(0, "end")
        self.entry_pct.delete(0, "end")
        self.active_var.set(True)
