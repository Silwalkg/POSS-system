import customtkinter as ctk
from tkinter import messagebox
import database as db
import auth


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("Happy Palace — Login")
        self.geometry("420x520")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._build()

    def _build(self):
        # Header
        ctk.CTkLabel(self, text="🍽️", font=("Arial", 52)).pack(pady=(50, 4))
        ctk.CTkLabel(self, text="HAPPY PALACE", font=("Arial", 26, "bold"),
                     text_color="#F4A261").pack()
        ctk.CTkLabel(self, text="Restaurant POS System", font=("Arial", 13),
                     text_color="gray").pack(pady=(2, 30))

        # Card frame
        frame = ctk.CTkFrame(self, corner_radius=16)
        frame.pack(padx=40, fill="x")

        ctk.CTkLabel(frame, text="Username", anchor="w").pack(padx=20, pady=(20, 2), fill="x")
        self.entry_user = ctk.CTkEntry(frame, placeholder_text="Enter username", height=40)
        self.entry_user.pack(padx=20, fill="x")

        ctk.CTkLabel(frame, text="Password", anchor="w").pack(padx=20, pady=(12, 2), fill="x")
        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="Enter password",
                                       show="•", height=40)
        self.entry_pass.pack(padx=20, fill="x")
        self.entry_pass.bind("<Return>", lambda e: self._login())

        self.btn_login = ctk.CTkButton(
            frame, text="Login", height=42, corner_radius=10,
            fg_color="#F4A261", hover_color="#E76F51", text_color="black",
            font=("Arial", 14, "bold"), command=self._login
        )
        self.btn_login.pack(padx=20, pady=20, fill="x")

        self.lbl_error = ctk.CTkLabel(frame, text="", text_color="#E63946", font=("Arial", 12))
        self.lbl_error.pack(pady=(0, 10))

    def _login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            self.lbl_error.configure(text="Please fill in all fields.")
            return

        user = db.login_user(username, password)
        if user:
            auth.set_user(user)
            self.destroy()
            self.on_success()
        else:
            self.lbl_error.configure(text="Invalid username or password.")
            self.entry_pass.delete(0, "end")
