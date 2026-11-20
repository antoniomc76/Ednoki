# ENICON

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

**[English](#english) | [Español](#español)**

---

## English

**ENICON** is a lightweight, open-source desktop application designed to easily edit the internal names and comments of Nikon Custom Picture Control files (`.np3`, `.np2` and `.ncp`). 

If you have ever struggled to identify your custom recipes in Nikon NX Studio or your camera because they all have generic names, ENICON allows you to rename them, add descriptive comments, and manage your collection with a clean and intuitive interface.

### Features

*   **Read & Edit:** Opens `.np3` and `.ncp` files to edit internal names and comments (comments are only available for `.np3` files).
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
> **How to run it:** Click on **"More info"** and then click **"Run anyway"**.

### How to Use

1. Click on **"Open folder"** and select the folder containing your `.np3` or `.ncp` files.
2. Double-click on the **Internal Name** or **Comment** columns to edit them individually, or use the **Batch Edit** section at the bottom to modify multiple files at once.
3. Click on **"Save copies to..."** to export the modified files to a new folder (or overwrite the originals if you wish).
4. Import the new files into Nikon NX Studio or copy them to your camera's memory card.

*(For more detailed instructions, open the application and go to `Help -> How to install the files`)*
