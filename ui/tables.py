import customtkinter as ctk
from tkinter import messagebox
import database as db

STATUS_COLORS = {
    "free":     "#2ec4b6",
    "occupied": "#E63946",
    "reserved": "#F4A261",
}


class TablesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🪑  Table Management", font=("Arial", 20, "bold"),
                     text_color="#F4A261").pack(anchor="w", padx=24, pady=(20, 4))

        # Add table row
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(0, 12))
        self.entry_num = ctk.CTkEntry(top, placeholder_text="Table number", width=140, height=36)
        self.entry_num.pack(side="left", padx=(0, 8))
        ctk.CTkButton(top, text="➕ Add Table", height=36,
                      fg_color="#F4A261", hover_color="#E76F51", text_color="black",
                      command=self._add_table).pack(side="left")

        # Legend
        leg = ctk.CTkFrame(self, fg_color="transparent")
        leg.pack(anchor="w", padx=20, pady=(0, 8))
        for status, color in STATUS_COLORS.items():
            ctk.CTkLabel(leg, text=f"● {status.title()}", text_color=color,
                         font=("Arial", 12)).pack(side="left", padx=8)

        # Grid of tables
        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self._load_tables()

    def _load_tables(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        tables = db.get_tables()
        for idx, t in enumerate(tables):
            color = STATUS_COLORS.get(t["status"], "gray")
            card = ctk.CTkFrame(self.grid_frame, width=130, height=120,
                                corner_radius=14, fg_color="#1a1a2e",
                                border_color=color, border_width=2)
            card.grid(row=idx // 5, column=idx % 5, padx=10, pady=10)
            card.pack_propagate(False)

            ctk.CTkLabel(card, text=f"Table {t['number']}",
                         font=("Arial", 14, "bold")).pack(pady=(18, 2))
            ctk.CTkLabel(card, text=t["status"].title(),
                         text_color=color, font=("Arial", 11)).pack()

            # Status change buttons
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(pady=6)
            for s in ["free", "occupied", "reserved"]:
                if s != t["status"]:
                    ctk.CTkButton(
                        btn_row, text=s[:3].title(), width=36, height=24,
                        fg_color="#333", hover_color=STATUS_COLORS[s],
                        font=("Arial", 9),
                        command=lambda tid=t["id"], st=s: self._set_status(tid, st)
                    ).pack(side="left", padx=2)

            ctk.CTkButton(card, text="🗑", width=28, height=24,
                          fg_color="transparent", hover_color="#3a0000",
                          text_color="#E63946", font=("Arial", 11),
                          command=lambda tid=t["id"]: self._delete_table(tid)
                          ).place(relx=1.0, rely=0.0, anchor="ne", x=-4, y=4)

    def _set_status(self, table_id, status):
        db.set_table_status(table_id, status)
        self._load_tables()

    def _add_table(self):
        num_str = self.entry_num.get().strip()
        if not num_str.isdigit():
            messagebox.showwarning("Validation", "Enter a valid table number.")
            return
        try:
            db.add_table(int(num_str))
            self.entry_num.delete(0, "end")
            self._load_tables()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_table(self, table_id):
        if messagebox.askyesno("Delete", "Delete this table?"):
            db.delete_table(table_id)
            self._load_tables()
