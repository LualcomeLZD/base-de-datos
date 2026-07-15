# Equipo de Transmisión y Recolección Plato

**Versión actual:** `0.3.2026-07-15`

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
- Institución / puesto de trabajo
- Cargo

Los cargos disponibles son:

- Recolector
- Transmisor
- Backup
- Coordinador de puesto

La cédula no se puede repetir, para evitar registrar dos veces a la misma persona.

## Opciones de la interfaz

La aplicación abre con un menú principal lateral de botones. Desde ese menú se entra a cada sección sin que todo se muestre de golpe:

- **Integrantes**: abre el formulario para crear, editar, limpiar o eliminar integrantes. También muestra el listado completo de integrantes registrados.
- **Malla de transmisión**: muestra un informe/listado de integrantes con cargo **Transmisor**, **Backup** o **Coordinador de puesto**.
- **Malla de recolección**: muestra un informe/listado de integrantes con cargo **Recolector** o **Backup**.
- **Imprimir PDF**: exporta el listado visible de integrantes o de una malla a un archivo PDF.

Para asignar a una persona a una malla, entra a **Integrantes** y selecciona su **Cargo**. Por ejemplo, si seleccionas **Transmisor** o **Coordinador de puesto**, esa persona aparecerá en la **Malla de transmisión**. Si seleccionas **Recolector**, aparecerá en la **Malla de recolección**.

## Cómo ejecutar la aplicación

1. Instala Python 3.10 o superior.
2. Desde esta carpeta, ejecuta:

   ```bash
   python app.py
   ```

3. Usa el menú principal lateral para entrar a **Integrantes**, **Malla de transmisión** o **Malla de recolección**.

## Uso básico

- Para registrar una persona, entra a **Integrantes**, escribe nombre, cédula, teléfono, institución / puesto de trabajo y cargo, y presiona **Guardar**.
- Para editar una persona, entra a **Integrantes**, selecciónala en la tabla, cambia los datos y presiona **Guardar**.
- Para eliminar una persona, entra a **Integrantes**, selecciónala en la tabla y presiona **Eliminar**.
- Para iniciar un registro nuevo, presiona **Limpiar**.
- Para ver los informes, usa los botones **Malla de transmisión** y **Malla de recolección**.
- Para imprimir una lista, abre **Integrantes** o una malla, presiona **Imprimir PDF**, elige dónde guardar el archivo y confirma.

## Si la aplicación sigue igual después de hacer `git pull`

- Cierra completamente la ventana de la aplicación y vuelve a abrirla.
- Confirma que estás ejecutando el archivo `app.py` de esta carpeta actualizada.
- Desde la carpeta del repositorio ejecuta `python app.py` otra vez.
- La pantalla actualizada muestra debajo del título este texto: **Versión: secciones por botones + institución/puesto de trabajo**.

## Empaquetar como programa

Para convertir la aplicación en un ejecutable pequeño puedes usar PyInstaller:

```bash
python -m pip install pyinstaller
python build_app.py
```

El ejecutable queda en la carpeta `dist/` con el nombre `EquipoPlato`. En Windows normalmente será `dist\EquipoPlato.exe`.

Notas:

- El archivo `equipo_plato.db` se crea junto al ejecutable cuando se abre el programa.
- Si ya tienes datos en una base anterior, copia `equipo_plato.db` a la misma carpeta donde ejecutes el programa.
- Si PyInstaller no está instalado, `python build_app.py` te mostrará el comando para instalarlo.

## Archivo de datos

Cuando se ejecuta la aplicación, se crea automáticamente el archivo `equipo_plato.db` en esta carpeta. Ese archivo contiene la base de datos local.

Si ya tenías una base creada con una versión anterior de la aplicación, los campos **Cargo** e **Institución / puesto de trabajo** se agregan automáticamente al abrir el programa. Los integrantes existentes quedan inicialmente como **Recolector** y con la institución / puesto de trabajo vacío hasta que los edites.

## Verificación rápida de versión

Si después de hacer `git pull` la ventana se ve como la versión vieja, ejecuta este comando desde la carpeta del repositorio:

```bash
python app.py --check
```

La salida debe mostrar:

- `Versión 0.3.2026-07-15`
- La ruta exacta del archivo `app.py` que estás ejecutando.
- Los campos actuales: nombre, cédula, teléfono, institución / puesto de trabajo y cargo.
- Los botones actuales en el menú lateral: Inicio, Integrantes, Malla de transmisión y Malla de recolección.

Si esa ruta no es la carpeta donde hiciste `git pull`, entonces estás abriendo una copia vieja del programa.
