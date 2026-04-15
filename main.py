import sys
import os

# Ensure imports resolve from this directory
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
import database as db
from ui.login import LoginWindow
from ui.dashboard import Dashboard


def launch_login():
    app = LoginWindow(on_success=launch_dashboard)
    app.mainloop()


def launch_dashboard():
    app = Dashboard(on_logout=launch_login)
    app.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    db.init_db()
    launch_login()
