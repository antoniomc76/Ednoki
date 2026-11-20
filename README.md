# ENICON

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

**[English](#english) | [Español](#español)**

---

## English

**ENICON** is a lightweight, open-source desktop application designed to easily edit the internal names and comments of Nikon Custom Picture Control files (`.np3`, `.np2`, and `.ncp`). 

If you have ever struggled to identify your custom recipes in Nikon NX Studio or your camera because they all have generic names, ENICON allows you to rename them, add descriptive comments, and manage your collection with a clean and intuitive interface.

### Features

*   **Read & Edit:** Opens `.np3`, `.np2`, and `.ncp` files to edit internal names and comments (comments are only available for `.np3` files).
*   **Batch Editing:** Apply prefixes, suffixes, find & replace, or numbering to multiple files at once.
*   **Safe Saving:** The original files are never modified unless you explicitly choose to do so. When overwriting, it creates automatic backups.
*   **CSV Export:** Export a detailed log of all the changes you have made.
*   **Bilingual Interface:** Switch between Spanish and English on the fly.
*   **Portable:** Available as a standalone `.exe` file. No Python installation required.

### Download & Installation

1. Go to the **[Releases](../../releases)** section of this repository.
2. Download the latest `enicon_v1.2.exe` file.
3. Move the `.exe` file to any folder on your computer and double-click it to run.

> **Windows SmartScreen Warning:**
> Because this is an open-source application without a paid digital signature, Windows Defender or SmartScreen might show a blue warning saying "Windows protected your PC". This is a standard false positive for apps created with PyInstaller.
> **How to run it:** Click on "More info" and then click "Run anyway".

### How to Use

1. Click on "Open folder" and select the folder containing your `.np3`, `.np2`, or `.ncp` files.
2. Double-click on the **Internal Name** or **Comment** columns to edit them individually, or use the **Batch Edit** section at the bottom to modify multiple files at once.
3. Click on "Save copies to..." to export the modified files to a new folder (or overwrite the originals if you wish).
4. Import the new files into Nikon NX Studio or copy them to your camera's memory card.

*(For more detailed instructions, open the application and go to `Help -> How to install the files`)*

### Disclaimer & License

This is an independent, unofficial tool. It is **not affiliated with, endorsed, or supported by Nikon Corporation**. Nikon, Picture Control, and NX Studio are trademarks or registered trademarks of Nikon Corporation.
The software is provided "as is", without warranty of any kind. Use it at your own risk.

This project is free software distributed under the terms of the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for more details.

---
---

## Español

**ENICON** es una aplicación de escritorio ligera y de código abierto diseñada para editar fácilmente los nombres internos y los comentarios de los archivos Custom Picture Control de Nikon (`.np3`, `.np2` y `.ncp`).

Si alguna vez has tenido problemas para identificar tus recetas personalizadas en Nikon NX Studio o en tu cámara porque todas tienen nombres genéricos, ENICON te permite renombrarlas, añadir comentarios descriptivos y gestionar tu colección con una interfaz limpia e intuitiva.

### Características

*   **Lectura y edición:** Abre archivos `.np3`, `.np2` y `.ncp` para editar nombres internos y comentarios (los comentarios solo están disponibles en archivos `.np3`).
*   **Edición por lotes:** Aplica prefijos, sufijos, buscar y reemplazar, o numeración a varios archivos a la vez.
*   **Guardado seguro:** Los archivos originales nunca se modifican a menos que tú lo elijas explícitamente. Al sobrescribir, se crean copias de seguridad automáticas.
*   **Exportación a CSV:** Exporta un registro detallado de todos los cambios que has realizado.
*   **Interfaz bilingüe:** Cambia entre español e inglés sobre la marcha.
*   **Portátil:** Disponible como un archivo `.exe` independiente. No requiere instalación de Python.

### Descarga e Instalación

1. Ve a la sección de **[Releases](../../releases)** de este repositorio.
2. Descarga el último archivo `enicon_v1.2.exe`.
3. Mueve el archivo `.exe` a cualquier carpeta de tu ordenador y haz doble clic para ejecutarlo.

> **Aviso de Windows SmartScreen:**
> Debido a que es una aplicación de código abierto sin una firma digital de pago, es posible que Windows Defender o SmartScreen muestren un aviso azul diciendo "Windows protegió tu PC". Es un falso positivo habitual en aplicaciones creadas con PyInstaller.
> **Cómo ejecutarlo:** Haz clic en "Más información" y luego en "Ejecutar de todas formas".

### Cómo usar

1. Haz clic en "Abrir carpeta" y selecciona la carpeta que contiene tus archivos `.np3`, `.np2` o `.ncp`.
2. Haz doble clic en las columnas **Nombre interno** o **Comentario** para editarlos individualmente, o usa la sección de **Edición por lotes** en la parte inferior para modificar varios archivos a la vez.
3. Haz clic en "Guardar copias en..." para exportar los archivos modificados a una nueva carpeta (o sobrescribir los originales si así lo deseas).
4. Importa los nuevos archivos en Nikon NX Studio o cópialos en la tarjeta de memoria de tu cámara.

*(Para instrucciones más detalladas, abre la aplicación y ve a `Ayuda -> Cómo instalar los archivos`)*

### Descargo de responsabilidad y Licencia

Esta es una herramienta independiente y no oficial. **No está afiliada, respaldada ni soportada por Nikon Corporation**. Nikon, Picture Control y NX Studio son marcas comerciales o marcas registradas de Nikon Corporation.
El software se proporciona "tal cual", sin garantía de ningún tipo. Úsalo bajo tu propia responsabilidad.

Este proyecto es software libre distribuido bajo los términos de la **GNU General Public License v3.0 (GPLv3)**. Consulta el archivo [LICENSE](LICENSE) para obtener más detalles.

---
*Created by Antonio Martínez Corral (with the assistance of AI).*
