import customtkinter as ctk
from tkinter import messagebox
import database as db
import auth


class UsersFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="👤  User Management", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)

        # List
        left = ctk.CTkFrame(body, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ctk.CTkLabel(left, text="System Users", font=("Arial", 14, "bold")).pack(
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
        ctk.CTkLabel(parent, text="Add New User",
                     font=("Arial", 14, "bold")).pack(padx=16, pady=(16, 10))

        ctk.CTkLabel(parent, text="Username *", anchor="w").pack(fill="x", padx=16)
        self.entry_user = ctk.CTkEntry(parent, height=36)
        self.entry_user.pack(fill="x", padx=16, pady=(2, 10))

        ctk.CTkLabel(parent, text="Password *", anchor="w").pack(fill="x", padx=16)
        self.entry_pass = ctk.CTkEntry(parent, show="•", height=36)
        self.entry_pass.pack(fill="x", padx=16, pady=(2, 10))

        ctk.CTkLabel(parent, text="Role *", anchor="w").pack(fill="x", padx=16)
        self.role_var = ctk.StringVar(value="cashier")
        ctk.CTkOptionMenu(parent, variable=self.role_var,
                          values=["admin", "cashier", "waiter"],
                          height=36).pack(fill="x", padx=16, pady=(2, 14))

        ctk.CTkButton(parent, text="💾  Create User", height=40,
                      fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                      command=self._create).pack(fill="x", padx=16)

    def _load(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for u in db.get_all_users():
            row = ctk.CTkFrame(self.list_frame, corner_radius=8, fg_color="#1a1a2e")
            row.pack(fill="x", pady=3, padx=4)

            role_colors = {"admin": "#E63946", "cashier": "#F4A261", "waiter": "#2ec4b6"}
            color = role_colors.get(u["role"], "gray")

            ctk.CTkLabel(row, text=u["username"], font=("Arial", 12, "bold"),
                         anchor="w", width=130).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=u["role"].title(), text_color=color,
                         font=("Arial", 11), width=80).pack(side="left")
            ctk.CTkLabel(row, text=u["created_at"][:10], font=("Arial", 10),
                         text_color="gray").pack(side="left", padx=6)

            # Prevent deleting yourself
            if u["username"] != auth.get_username():
                ctk.CTkButton(row, text="Del", width=46, height=28,
                              fg_color="transparent", hover_color="#3a0000",
                              text_color="#E63946",
                              command=lambda uid=u["id"]: self._delete(uid)).pack(
                    side="right", padx=8)

    def _create(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning("Validation", "Username and password are required.")
            return
        if len(password) < 6:
            messagebox.showwarning("Validation", "Password must be at least 6 characters.")
            return
        try:
            db.create_user(username, password, role)
            self.entry_user.delete(0, "end")
            self.entry_pass.delete(0, "end")
            self._load()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create user:\n{e}")

    def _delete(self, uid):
        if messagebox.askyesno("Delete", "Delete this user?"):
            db.delete_user(uid)
            self._load()
