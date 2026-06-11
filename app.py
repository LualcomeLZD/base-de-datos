"""Aplicación de escritorio para gestionar el Equipo de Transmisión y Recolección Plato.

La aplicación usa SQLite como base de datos local porque no requiere servidor y
Tkinter para la interfaz porque viene incluido con Python en la mayoría de
instalaciones.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_TITLE = "Equipo de Transmisión y Recolección Plato"
DB_PATH = Path(__file__).with_name("equipo_plato.db")
CARGOS = ("Recolector", "Transmisor", "Backup", "Coordinador de puesto")
MALLA_TRANSMISION_CARGOS = ("Transmisor", "Backup", "Coordinador de puesto")
MALLA_RECOLECCION_CARGOS = ("Recolector", "Backup", "Coordinador de puesto")


class MemberDatabase:
    """Capa pequeña para crear y consultar la base de datos SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._create_table()
        self._ensure_cargo_column()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS integrantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cedula TEXT NOT NULL UNIQUE,
                    telefono TEXT NOT NULL,
                    cargo TEXT NOT NULL DEFAULT 'Recolector'
                )
                """
            )

    def _ensure_cargo_column(self) -> None:
        """Agrega la columna cargo si la base ya existía con la versión anterior."""

        with self._connect() as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(integrantes)").fetchall()
            }
            if "cargo" not in columns:
                connection.execute(
                    "ALTER TABLE integrantes ADD COLUMN cargo TEXT NOT NULL DEFAULT 'Recolector'"
                )

    def list_members(
        self, cargos: tuple[str, ...] | None = None
    ) -> list[tuple[int, str, str, str, str]]:
        with self._connect() as connection:
            if cargos is None:
                return connection.execute(
                    "SELECT id, nombre, cedula, telefono, cargo FROM integrantes ORDER BY nombre"
                ).fetchall()

            placeholders = ",".join("?" for _cargo in cargos)
            return connection.execute(
                f"""
                SELECT id, nombre, cedula, telefono, cargo
                FROM integrantes
                WHERE cargo IN ({placeholders})
                ORDER BY cargo, nombre
                """,
                cargos,
            ).fetchall()

    def add_member(self, nombre: str, cedula: str, telefono: str, cargo: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO integrantes (nombre, cedula, telefono, cargo)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, cedula, telefono, cargo),
            )

    def update_member(
        self, member_id: int, nombre: str, cedula: str, telefono: str, cargo: str
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE integrantes
                SET nombre = ?, cedula = ?, telefono = ?, cargo = ?
                WHERE id = ?
                """,
                (nombre, cedula, telefono, cargo, member_id),
            )

    def delete_member(self, member_id: int) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM integrantes WHERE id = ?", (member_id,))


class TeamApp(tk.Tk):
    """Interfaz gráfica sencilla para registrar, editar y borrar integrantes."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("940x620")
        self.minsize(860, 560)
        self.database = MemberDatabase()
        self.selected_member_id: int | None = None

        self.nombre_var = tk.StringVar()
        self.cedula_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.cargo_var = tk.StringVar(value=CARGOS[0])
        self.current_view = "integrantes"

        self._build_layout()
        self.show_integrantes()

    def _build_layout(self) -> None:
        title = ttk.Label(self, text=APP_TITLE, font=("Arial", 18, "bold"))
        title.pack(pady=(16, 8))

        menu = ttk.Frame(self)
        menu.pack(fill="x", padx=16, pady=(0, 8))
        ttk.Button(menu, text="Integrantes", command=self.show_integrantes).pack(side="left", padx=4)
        ttk.Button(menu, text="Malla de transmisión", command=self.show_malla_transmision).pack(
            side="left", padx=4
        )
        ttk.Button(menu, text="Malla de recolección", command=self.show_malla_recoleccion).pack(
            side="left", padx=4
        )

        form = ttk.LabelFrame(self, text="Datos del integrante")
        form.pack(fill="x", padx=16, pady=8)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        ttk.Label(form, text="Nombre").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.nombre_var).grid(
            row=0, column=1, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Cédula").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.cedula_var).grid(
            row=0, column=3, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Teléfono").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.telefono_var).grid(
            row=1, column=1, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Cargo").grid(row=1, column=2, padx=8, pady=8, sticky="w")
        cargo_select = ttk.Combobox(
            form,
            textvariable=self.cargo_var,
            values=CARGOS,
            state="readonly",
        )
        cargo_select.grid(row=1, column=3, padx=8, pady=8, sticky="ew")

        buttons = ttk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=4, padx=8, pady=(4, 10), sticky="e")
        ttk.Button(buttons, text="Guardar", command=self.save_member).pack(side="left", padx=4)
        ttk.Button(buttons, text="Limpiar", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(buttons, text="Eliminar", command=self.delete_selected_member).pack(
            side="left", padx=4
        )

        table_frame = ttk.LabelFrame(self, text="Integrantes registrados")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(4, 16))
        self.table_frame = table_frame

        columns = ("nombre", "cedula", "telefono", "cargo")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.table.heading("nombre", text="Nombre")
        self.table.heading("cedula", text="Cédula")
        self.table.heading("telefono", text="Teléfono")
        self.table.heading("cargo", text="Cargo")
        self.table.column("nombre", width=260)
        self.table.column("cedula", width=150)
        self.table.column("telefono", width=150)
        self.table.column("cargo", width=190)
        self.table.bind("<<TreeviewSelect>>", self.load_selected_member)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_integrantes(self) -> None:
        self.current_view = "integrantes"
        self.table_frame.configure(text="Integrantes registrados")
        self.refresh_members()

    def show_malla_transmision(self) -> None:
        self.current_view = "transmision"
        self.table_frame.configure(text="Malla de transmisión")
        self.refresh_members(MALLA_TRANSMISION_CARGOS)

    def show_malla_recoleccion(self) -> None:
        self.current_view = "recoleccion"
        self.table_frame.configure(text="Malla de recolección")
        self.refresh_members(MALLA_RECOLECCION_CARGOS)

    def refresh_members(self, cargos: tuple[str, ...] | None = None) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for member_id, nombre, cedula, telefono, cargo in self.database.list_members(cargos):
            self.table.insert(
                "", "end", iid=str(member_id), values=(nombre, cedula, telefono, cargo)
            )

    def refresh_current_view(self) -> None:
        if self.current_view == "transmision":
            self.show_malla_transmision()
        elif self.current_view == "recoleccion":
            self.show_malla_recoleccion()
        else:
            self.show_integrantes()

    def _validated_inputs(self) -> tuple[str, str, str, str] | None:
        nombre = self.nombre_var.get().strip()
        cedula = self.cedula_var.get().strip()
        telefono = self.telefono_var.get().strip()
        cargo = self.cargo_var.get().strip()

        if not nombre or not cedula or not telefono or not cargo:
            messagebox.showwarning(
                "Campos incompletos", "Complete nombre, cédula, teléfono y cargo."
            )
            return None

        if cargo not in CARGOS:
            messagebox.showwarning("Cargo inválido", "Seleccione un cargo válido de la lista.")
            return None

        return nombre, cedula, telefono, cargo

    def save_member(self) -> None:
        values = self._validated_inputs()
        if values is None:
            return

        nombre, cedula, telefono, cargo = values
        try:
            if self.selected_member_id is None:
                self.database.add_member(nombre, cedula, telefono, cargo)
                messagebox.showinfo("Guardado", "Integrante registrado correctamente.")
            else:
                self.database.update_member(
                    self.selected_member_id, nombre, cedula, telefono, cargo
                )
                messagebox.showinfo("Actualizado", "Integrante actualizado correctamente.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Cédula duplicada", "Ya existe un integrante con esa cédula.")
            return

        self.clear_form()
        self.refresh_current_view()

    def load_selected_member(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.table.selection()
        if not selected:
            return

        self.selected_member_id = int(selected[0])
        nombre, cedula, telefono, cargo = self.table.item(selected[0], "values")
        self.nombre_var.set(nombre)
        self.cedula_var.set(cedula)
        self.telefono_var.set(telefono)
        self.cargo_var.set(cargo)

    def delete_selected_member(self) -> None:
        if self.selected_member_id is None:
            messagebox.showwarning("Sin selección", "Seleccione un integrante de la tabla.")
            return

        confirmed = messagebox.askyesno("Confirmar eliminación", "¿Desea eliminar este integrante?")
        if not confirmed:
            return

        self.database.delete_member(self.selected_member_id)
        self.clear_form()
        self.refresh_current_view()
        messagebox.showinfo("Eliminado", "Integrante eliminado correctamente.")

    def clear_form(self) -> None:
        self.selected_member_id = None
        self.nombre_var.set("")
        self.cedula_var.set("")
        self.telefono_var.set("")
        self.cargo_var.set(CARGOS[0])
        self.table.selection_remove(self.table.selection())


def main() -> None:
    app = TeamApp()
    app.mainloop()


if __name__ == "__main__":
    main()
