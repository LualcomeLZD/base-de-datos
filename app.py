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
APP_VERSION = "Versión: secciones por botones + institución/puesto de trabajo"
DB_PATH = Path(__file__).with_name("equipo_plato.db")
CARGOS = ("Recolector", "Transmisor", "Backup", "Coordinador de puesto")
MALLA_TRANSMISION_CARGOS = ("Transmisor", "Backup", "Coordinador de puesto")
MALLA_RECOLECCION_CARGOS = ("Recolector", "Backup")
TABLE_COLUMNS = ("nombre", "cedula", "telefono", "puesto_trabajo", "cargo")
COLUMN_TITLES = {
    "nombre": "Nombre",
    "cedula": "Cédula",
    "telefono": "Teléfono",
    "puesto_trabajo": "Institución / puesto de trabajo",
    "cargo": "Cargo",
}


class MemberDatabase:
    """Capa pequeña para crear y consultar la base de datos SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._create_table()
        self._ensure_column(
            "cargo", "ALTER TABLE integrantes ADD COLUMN cargo TEXT NOT NULL DEFAULT 'Recolector'"
        )
        self._ensure_column(
            "puesto_trabajo",
            "ALTER TABLE integrantes ADD COLUMN puesto_trabajo TEXT NOT NULL DEFAULT ''",
        )
        self._migrate_legacy_voting_place_data()

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
                    puesto_trabajo TEXT NOT NULL DEFAULT '',
                    cargo TEXT NOT NULL DEFAULT 'Recolector'
                )
                """
            )

    def _ensure_column(self, column_name: str, alter_statement: str) -> None:
        """Agrega una columna si la base ya existía con una versión anterior."""

        with self._connect() as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(integrantes)").fetchall()
            }
            if column_name not in columns:
                connection.execute(alter_statement)

    def _migrate_legacy_voting_place_data(self) -> None:
        """Copia datos guardados antes como lugar_votacion al nuevo campo puesto_trabajo."""

        with self._connect() as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(integrantes)").fetchall()
            }
            if "lugar_votacion" in columns and "puesto_trabajo" in columns:
                connection.execute(
                    """
                    UPDATE integrantes
                    SET puesto_trabajo = lugar_votacion
                    WHERE puesto_trabajo = '' AND lugar_votacion <> ''
                    """
                )

    def list_members(
        self, cargos: tuple[str, ...] | None = None
    ) -> list[tuple[int, str, str, str, str, str]]:
        with self._connect() as connection:
            if cargos is None:
                return connection.execute(
                    """
                    SELECT id, nombre, cedula, telefono, puesto_trabajo, cargo
                    FROM integrantes
                    ORDER BY nombre
                    """
                ).fetchall()

            placeholders = ",".join("?" for _cargo in cargos)
            return connection.execute(
                f"""
                SELECT id, nombre, cedula, telefono, puesto_trabajo, cargo
                FROM integrantes
                WHERE cargo IN ({placeholders})
                ORDER BY cargo, nombre
                """,
                cargos,
            ).fetchall()

    def add_member(
        self, nombre: str, cedula: str, telefono: str, puesto_trabajo: str, cargo: str
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO integrantes (nombre, cedula, telefono, puesto_trabajo, cargo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nombre, cedula, telefono, puesto_trabajo, cargo),
            )

    def update_member(
        self,
        member_id: int,
        nombre: str,
        cedula: str,
        telefono: str,
        puesto_trabajo: str,
        cargo: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE integrantes
                SET nombre = ?, cedula = ?, telefono = ?, puesto_trabajo = ?, cargo = ?
                WHERE id = ?
                """,
                (nombre, cedula, telefono, puesto_trabajo, cargo, member_id),
            )

    def delete_member(self, member_id: int) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM integrantes WHERE id = ?", (member_id,))


class TeamApp(tk.Tk):
    """Interfaz con menú de botones para integrantes y reportes por malla."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x660")
        self.minsize(920, 580)
        self.database = MemberDatabase()
        self.selected_member_id: int | None = None

        self.nombre_var = tk.StringVar()
        self.cedula_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.puesto_trabajo_var = tk.StringVar()
        self.cargo_var = tk.StringVar(value=CARGOS[0])

        self._build_layout()
        self.show_home()

    def _build_layout(self) -> None:
        title = ttk.Label(self, text=APP_TITLE, font=("Arial", 18, "bold"))
        title.pack(pady=(16, 4))
        ttk.Label(self, text=APP_VERSION, font=("Arial", 10, "italic")).pack(pady=(0, 8))

        menu = ttk.Frame(self)
        menu.pack(fill="x", padx=16, pady=(0, 10))
        ttk.Button(menu, text="Inicio", command=self.show_home).pack(side="left", padx=4)
        ttk.Button(menu, text="Integrantes", command=self.show_integrantes).pack(side="left", padx=4)
        ttk.Button(menu, text="Malla de transmisión", command=self.show_malla_transmision).pack(
            side="left", padx=4
        )
        ttk.Button(menu, text="Malla de recolección", command=self.show_malla_recoleccion).pack(
            side="left", padx=4
        )

        self.content = ttk.Frame(self)
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.home_frame = ttk.Frame(self.content)
        self.integrantes_frame = ttk.Frame(self.content)
        self.report_frame = ttk.Frame(self.content)
        for frame in (self.home_frame, self.integrantes_frame, self.report_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self._build_home_frame()
        self._build_integrantes_frame()
        self._build_report_frame()

    def _build_home_frame(self) -> None:
        self.home_frame.columnconfigure(0, weight=1)
        ttk.Label(
            self.home_frame,
            text="Seleccione una opción para continuar",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, pady=(36, 16))
        ttk.Button(self.home_frame, text="Integrantes", command=self.show_integrantes).grid(
            row=1, column=0, pady=8, ipadx=50, ipady=10
        )
        ttk.Button(
            self.home_frame, text="Malla de transmisión", command=self.show_malla_transmision
        ).grid(row=2, column=0, pady=8, ipadx=50, ipady=10)
        ttk.Button(
            self.home_frame, text="Malla de recolección", command=self.show_malla_recoleccion
        ).grid(row=3, column=0, pady=8, ipadx=50, ipady=10)

    def _build_integrantes_frame(self) -> None:
        self.integrantes_frame.rowconfigure(1, weight=1)
        self.integrantes_frame.columnconfigure(0, weight=1)

        form = ttk.LabelFrame(self.integrantes_frame, text="Datos del integrante")
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
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

        ttk.Label(form, text="Institución / puesto de trabajo").grid(
            row=1, column=2, padx=8, pady=8, sticky="w"
        )
        ttk.Entry(form, textvariable=self.puesto_trabajo_var).grid(
            row=1, column=3, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Cargo").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.cargo_var,
            values=CARGOS,
            state="readonly",
        ).grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        buttons = ttk.Frame(form)
        buttons.grid(row=3, column=0, columnspan=4, padx=8, pady=(4, 10), sticky="e")
        ttk.Button(buttons, text="Guardar", command=self.save_member).pack(side="left", padx=4)
        ttk.Button(buttons, text="Limpiar", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(buttons, text="Eliminar", command=self.delete_selected_member).pack(
            side="left", padx=4
        )

        table_frame = ttk.LabelFrame(self.integrantes_frame, text="Integrantes registrados")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.members_table = self._create_table(table_frame)
        self.members_table.bind("<<TreeviewSelect>>", self.load_selected_member)

    def _build_report_frame(self) -> None:
        self.report_frame.rowconfigure(1, weight=1)
        self.report_frame.columnconfigure(0, weight=1)
        self.report_title = ttk.Label(self.report_frame, font=("Arial", 14, "bold"))
        self.report_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
        table_frame = ttk.LabelFrame(self.report_frame, text="Listado")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.report_table = self._create_table(table_frame)

    def _create_table(self, parent: ttk.Frame) -> ttk.Treeview:
        table = ttk.Treeview(parent, columns=TABLE_COLUMNS, show="headings", height=14)
        widths = {
            "nombre": 220,
            "cedula": 130,
            "telefono": 130,
            "puesto_trabajo": 230,
            "cargo": 180,
        }
        for column in TABLE_COLUMNS:
            table.heading(column, text=COLUMN_TITLES[column])
            table.column(column, width=widths[column])

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        return table

    def show_home(self) -> None:
        self.clear_form()
        self.home_frame.tkraise()

    def show_integrantes(self) -> None:
        self.integrantes_frame.tkraise()
        self.refresh_members_table()

    def show_malla_transmision(self) -> None:
        self._show_report(
            "Malla de transmisión: transmisores, backup y coordinadores de puesto",
            MALLA_TRANSMISION_CARGOS,
        )

    def show_malla_recoleccion(self) -> None:
        self._show_report("Malla de recolección: recolectores y backup", MALLA_RECOLECCION_CARGOS)

    def _show_report(self, title: str, cargos: tuple[str, ...]) -> None:
        self.clear_form()
        self.report_title.configure(text=title)
        self.refresh_table(self.report_table, cargos)
        self.report_frame.tkraise()

    def refresh_members_table(self) -> None:
        self.refresh_table(self.members_table)

    def refresh_table(self, table: ttk.Treeview, cargos: tuple[str, ...] | None = None) -> None:
        for item in table.get_children():
            table.delete(item)

        for member_id, nombre, cedula, telefono, puesto_trabajo, cargo in self.database.list_members(
            cargos
        ):
            table.insert(
                "",
                "end",
                iid=str(member_id),
                values=(nombre, cedula, telefono, puesto_trabajo, cargo),
            )

    def _validated_inputs(self) -> tuple[str, str, str, str, str] | None:
        nombre = self.nombre_var.get().strip()
        cedula = self.cedula_var.get().strip()
        telefono = self.telefono_var.get().strip()
        puesto_trabajo = self.puesto_trabajo_var.get().strip()
        cargo = self.cargo_var.get().strip()

        if not nombre or not cedula or not telefono or not puesto_trabajo or not cargo:
            messagebox.showwarning(
                "Campos incompletos",
                "Complete nombre, cédula, teléfono, institución / puesto de trabajo y cargo.",
            )
            return None

        if cargo not in CARGOS:
            messagebox.showwarning("Cargo inválido", "Seleccione un cargo válido de la lista.")
            return None

        return nombre, cedula, telefono, puesto_trabajo, cargo

    def save_member(self) -> None:
        values = self._validated_inputs()
        if values is None:
            return

        nombre, cedula, telefono, puesto_trabajo, cargo = values
        try:
            if self.selected_member_id is None:
                self.database.add_member(nombre, cedula, telefono, puesto_trabajo, cargo)
                messagebox.showinfo("Guardado", "Integrante registrado correctamente.")
            else:
                self.database.update_member(
                    self.selected_member_id,
                    nombre,
                    cedula,
                    telefono,
                    puesto_trabajo,
                    cargo,
                )
                messagebox.showinfo("Actualizado", "Integrante actualizado correctamente.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Cédula duplicada", "Ya existe un integrante con esa cédula.")
            return

        self.clear_form()
        self.refresh_members_table()

    def load_selected_member(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.members_table.selection()
        if not selected:
            return

        self.selected_member_id = int(selected[0])
        nombre, cedula, telefono, puesto_trabajo, cargo = self.members_table.item(
            selected[0], "values"
        )
        self.nombre_var.set(nombre)
        self.cedula_var.set(cedula)
        self.telefono_var.set(telefono)
        self.puesto_trabajo_var.set(puesto_trabajo)
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
        self.refresh_members_table()
        messagebox.showinfo("Eliminado", "Integrante eliminado correctamente.")

    def clear_form(self) -> None:
        self.selected_member_id = None
        self.nombre_var.set("")
        self.cedula_var.set("")
        self.telefono_var.set("")
        self.puesto_trabajo_var.set("")
        self.cargo_var.set(CARGOS[0])
        if hasattr(self, "members_table"):
            self.members_table.selection_remove(self.members_table.selection())


def main() -> None:
    app = TeamApp()
    app.mainloop()


if __name__ == "__main__":
    main()
