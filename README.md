# Equipo de Transmisión y Recolección Plato

Aplicación sencilla para manejar la información de integrantes de un grupo llamado **Equipo de Transmisión y Recolección Plato**.

## Lenguaje y base de datos elegidos

Se eligió **Python** con **SQLite** porque es una combinación simple para empezar:

- Python es fácil de leer y modificar.
- SQLite guarda la información en un archivo local llamado `equipo_plato.db`.
- No se necesita instalar ni configurar un servidor de base de datos.
- La interfaz usa Tkinter, una librería gráfica incluida con Python en muchas instalaciones.

## Información que maneja

La base de datos guarda estos campos por integrante:

- Nombre
- Cédula
- Teléfono

La cédula no se puede repetir, para evitar registrar dos veces a la misma persona.

## Cómo ejecutar la aplicación

1. Instala Python 3.10 o superior.
2. Desde esta carpeta, ejecuta:

   ```bash
   python app.py
   ```

3. Usa la ventana para guardar, editar o eliminar integrantes.

## Uso básico

- Para registrar una persona, escribe nombre, cédula y teléfono, y presiona **Guardar**.
- Para editar una persona, selecciónala en la tabla, cambia los datos y presiona **Guardar**.
- Para eliminar una persona, selecciónala en la tabla y presiona **Eliminar**.
- Para iniciar un registro nuevo, presiona **Limpiar**.

## Archivo de datos

Cuando se ejecuta la aplicación, se crea automáticamente el archivo `equipo_plato.db` en esta carpeta. Ese archivo contiene la base de datos local.
