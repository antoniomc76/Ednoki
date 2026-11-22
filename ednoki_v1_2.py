#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2026 Antonio Martínez Corral
# Developed with the assistance of Artificial Intelligence (AI).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# DISCLAIMER: This is an independent, unofficial tool. It is not affiliated
# with, endorsed, or supported by Nikon Corporation. Nikon, Picture Control,
# and NX Studio are trademarks or registered trademarks of Nikon Corporation.
"""Ednoki v1.2: editor de Custom Picture Controls de Nikon (.np3 / .ncp).

Solo guarda COPIAS en otra carpeta: los originales nunca se modifican
(salvo que el usuario lo elija explícitamente en el diálogo de guardado; en ese caso la
escritura es atómica y, por defecto, con copia de seguridad previa).
Idiomas: español (es) / inglés (en). Cambio en caliente desde Archivo > Idioma / Language.
"""
import csv
import json
import os
import re
import shutil
import string
import struct
import sys
import tkinter as tk
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

# Atajos de teclado: Command (⌘) en macOS, Control en el resto de sistemas.
IS_MAC = sys.platform == "darwin"
MOD = "Command" if IS_MAC else "Control"      # para self.root.bind("<MOD-x>")
MOD_LABEL = "\u2318" if IS_MAC else "Ctrl+"   # para textos y accelerator de menús

# =========================================================== i18n
APP_VERSION = "1.2"
__version__ = APP_VERSION
__author__ = "Antonio Martínez Corral"
__license__ = "GPL-3.0-or-later"

# Páginas HTML que se abren en el navegador (se elige la del idioma actual).
# Están en la subcarpeta HTML_DIR (junto al programa); al empaquetar con PyInstaller hay que
# incluir esa carpeta entera con --add-data ("html;html" en Windows, "html:html" en macOS/Linux).
HTML_DIR = "html"
HTML_PAGES = {
    "help":  {"es": "ayuda.html",  "en": "help.html"},
    "about": {"es": "acerca.html", "en": "about.html"},
}

STRINGS = {
    'es': {
        'app_title': "Ednoki: Editor de nombres internos y comentarios para Nikon. (v.{ver})",
        'no_folder': "Ninguna carpeta cargada",
        'files_loaded': "{n} archivos cargados · {c} modificados · {e} con errores",
        'files_one_folder': "{path}  ({n} archivos)",
        'files_n_folders': "{n} carpetas · {m} archivos",
        'files_n_folders_tip': "{n} carpetas de origen:\n{folders}",

        'open_folder': "📂 Abrir carpeta…",
        'add': "➕ Añadir",
        'add_files': "Archivos…",
        'add_folder': "Carpeta…",
        'clear_list': "🗑 Vaciar lista",
        'save_copies': "💾 Guardar copias en…",

        'menu_file': "Archivo",
        'menu_help': "Ayuda",
        'menu_about_top': "Acerca",
        'menu_open_folder': "Abrir carpeta…",
        'menu_add': "Añadir",
        'menu_add_files': "Archivos…",
        'menu_add_folder': "Carpeta…",
        'menu_export_csv': "Exportar registro CSV…",
        'menu_clear_list': "Vaciar lista",
        'menu_language': "Idioma / language",
        'menu_exit': "Salir",
        'menu_help_install': "Cómo instalar los archivos",
        'menu_about': "Acerca de Ednoki",

        'folder_label': "📁 Carpeta:",
        'filter_label': "🔍 Filtrar:",
        'field_label': "Campo:",
        'op_label': "Operación:",
        'target_name': "Nombre",
        'target_comment': "Comentario",
        'col_file': "Archivo",
        'col_name': "Nombre interno",
        'col_comment': "Comentario",
        'col_status': "Estado",
        'rename_check': "Renombrar también el archivo en disco",
        'hint_double_click': "💡 Doble clic en Nombre o Comentario para editar. Clic en las cabeceras para ordenar.",

        'batch_group': " Edición por lotes (sobre filas seleccionadas; si no hay ninguna, sobre todas) ",
        'op_apply': "Aplicar",
        'op_undo': f"Deshacer ({MOD_LABEL}Z)",
        'op_reset': "Restablecer selección",

        'op_add_prefix': "Añadir prefijo",
        'op_add_suffix': "Añadir sufijo",
        'op_find_replace': "Buscar y reemplazar",
        'op_upper': "Mayúsculas",
        'op_lower': "Minúsculas",
        'op_title': "Tipo título",
        'op_number': "Numerar al final",
        'op_set': "Establecer texto",
        'op_lbl_prefix': "Prefijo:",
        'op_lbl_suffix': "Sufijo:",
        'op_lbl_find': "Buscar:",
        'op_lbl_replace': "Reemplazar por:",
        'op_lbl_start': "Empezar en:",
        'op_lbl_digits': "Dígitos:",
        'op_lbl_text': "Texto:",

        'modified': "Modificado",
        'comment_added_suffix': " · comentario añadido",
        'name_repeated': "nombre de archivo repetido",
        'err_empty': "vacío",
        'err_too_long': "demasiado largo ({n}/{max}{unit})",
        'err_unit_chars': " caracteres",
        'err_unit_bytes': " bytes",
        'err_not_ascii': "carácter no permitido (solo ASCII)",
        'err_control': "caracteres de control no permitidos",
        'no_comment_ncp': "(no disponible en .ncp)",
        'no_comment_np3': "(estructura de este .np3 no reconocida: comentario no editable)",
        'no_comment_add': "(sin comentario · doble clic para añadir)",

        'confirm_unsaved_title': "Cambios sin guardar",
        'confirm_unsaved_msg': "Hay {n} archivo(s) con cambios pendientes.\n¿{action} y descartar esos cambios?\n\n(Los archivos originales en disco no se tocan.)",
        'action_replace': "Reemplazar la lista",
        'action_clear': "Vaciar la lista",
        'skipped_title': "Formato no reconocido",
        'skipped_msg': "Se omitieron archivos:\n{list}",

        'export_none_title': "Sin archivos",
        'export_none_msg': "No hay archivos cargados para exportar.",
        'export_nochg_title': "Sin cambios",
        'export_nochg_msg': "No hay cambios registrados todavía.\n¿Exportar un CSV vacío igualmente?",
        'export_dialog_title': "Guardar registro de cambios",
        'export_ok_title': "Registro exportado",
        'export_ok_msg': "Se han exportado {n} cambios a:\n{path}",
        'export_hint': "CSV con {n} cambios exportado",
        'export_initial': "registro_cambios.csv",

        'save_dialog_title': "Carpeta de salida",
        'overwrite_title': "Sobrescribir originales",
        'overwrite_msg': "Has seleccionado la carpeta de origen como destino.\nSe sobrescribirán {n} archivos originales.\n\n¿Continuar?",
        'err_read_folder': "No se puede leer la carpeta",
        'confirm_reset_title': "Restablecer",
        'confirm_reset_msg': "No hay filas seleccionadas. ¿Restablecer TODAS?",
        'err_number_title': "Valor no válido",
        'err_number_msg': "«Empezar en» y «Dígitos» deben ser números enteros.",
        'hint_undo': "Acción deshecha",
        'hint_added_files': "Añadidos {n} archivos nuevos",
        'hint_batch': "{n} campos modificados por lotes",
        'save_ok_title': "Resultado",
        'save_ok_msg': "{n} archivos guardados en:\n{path}",
        'save_added_msg': "\n\n{added} con comentario AÑADIDO (experimental): pruébalos en NX Studio.",
        'save_skipped_msg': "\n\n{skipped} omitidos por conflicto de nombre.",
        'save_overwritten_msg': "\n\n{overwritten} sobrescritos.",
        'save_errors_msg': "\n\n{count} con error:\n{list}",
        'save_cancelled': "Guardado cancelado.",
        'conflict_title': "Conflicto de nombre",
        'conflict_msg': "Ya existe un archivo con el nombre:\n\n    {file}\n\n¿Qué desea hacer?",
        'conflict_overwrite': "Sobrescribir",
        'conflict_skip': "Omitir",
        'conflict_rename': "Renombrar _1",
        'conflict_cancel': "Cancelar",
        'conflict_apply_all': "Aplicar esta decisión a todos los conflictos restantes",

        'lang_es': "Español",
        'lang_en': "English",

        'help_err_title': "No se puede abrir la ayuda",
        'help_err_msg': "No se encontró el archivo:\n{path}\n\nColócalo en la misma carpeta que el programa.",

        'edit_name_label': "Nombre",
        'edit_comment_label': "Comentario",
        'edit_name_count': "{label}: {n}/{max} caracteres",
        'edit_comment_count': "{label}: {n}/{max} caracteres · {b}/{bmax} bytes",

        'menu_backup': "Copia de seguridad al sobrescribir originales",
        'all_files': "Todos los archivos",
        'name_repeated_note': " · nombre de archivo repetido (se añadirá _1)",
        'files_visible_suffix': " · {v} visibles",
        'overwrite_backup_note': "\n\nSe guardará antes una copia de seguridad de los originales.",
        'overwrite_nobackup_note': "\n\nLa copia de seguridad está desactivada: esta acción no se puede deshacer.",
        'save_backup_msg': "\n\n{n} originales respaldados en:\n{path}",
        'save_autorenamed_msg': "\n\n{n} guardados con sufijo _1 por nombre de archivo repetido.",
        'err_backup': "no se pudo guardar la copia de seguridad ({e}); el original no se ha tocado",
        'err_write': "no se pudo escribir ({e}); el destino no se ha modificado",
        'verify_failed': "la verificación falló; el destino no se ha modificado",
        'no_files_title': "Sin archivos",
        'no_files_msg': "No se encontraron archivos .np3 / .ncp en:\n{path}",
        'error_title': "Error",
        'unexpected_error_title': "Error inesperado",
        'lang_rebuild_error': "No se pudo reconstruir la interfaz al cambiar de idioma.",
        'export_status_saved': "guardado",
        'export_status_pending': "pendiente",
    },
    'en': {
        'app_title': "Ednoki: Internal name and comment editor for Nikon. (v.{ver})",
        'no_folder': "No folder loaded",
        'files_loaded': "{n} files loaded · {c} modified · {e} with errors",
        'files_one_folder': "{path}  ({n} files)",
        'files_n_folders': "{n} folders · {m} files",
        'files_n_folders_tip': "{n} source folders:\n{folders}",

        'open_folder': "📂 Open folder…",
        'add': "➕ Add",
        'add_files': "Files…",
        'add_folder': "Folder…",
        'clear_list': "🗑 Clear list",
        'save_copies': "💾 Save copies to…",

        'menu_file': "File",
        'menu_help': "Help",
        'menu_about_top': "About",
        'menu_open_folder': "Open folder…",
        'menu_add': "Add",
        'menu_add_files': "Files…",
        'menu_add_folder': "Folder…",
        'menu_export_csv': "Export change log (CSV)…",
        'menu_clear_list': "Clear list",
        'menu_language': "Language / Idioma",
        'menu_exit': "Exit",
        'menu_help_install': "How to install the files",
        'menu_about': "About Ednoki",

        'folder_label': "📁 Folder:",
        'filter_label': "🔍 Filter:",
        'field_label': "Field:",
        'op_label': "Operation:",
        'target_name': "Name",
        'target_comment': "Comment",
        'col_file': "File",
        'col_name': "Internal name",
        'col_comment': "Comment",
        'col_status': "Status",
        'rename_check': "Also rename the file on disk",
        'hint_double_click': "💡 Double-click Name or Comment to edit. Click column headers to sort.",

        'batch_group': " Batch edit (on selected rows; if none, on all) ",
        'op_apply': "Apply",
        'op_undo': f"Undo ({MOD_LABEL}Z)",
        'op_reset': "Reset selection",

        'op_add_prefix': "Add prefix",
        'op_add_suffix': "Add suffix",
        'op_find_replace': "Find & replace",
        'op_upper': "Uppercase",
        'op_lower': "Lowercase",
        'op_title': "Title Case",
        'op_number': "Number at end",
        'op_set': "Set text",
        'op_lbl_prefix': "Prefix:",
        'op_lbl_suffix': "Suffix:",
        'op_lbl_find': "Find:",
        'op_lbl_replace': "Replace with:",
        'op_lbl_start': "Start at:",
        'op_lbl_digits': "Digits:",
        'op_lbl_text': "Text:",

        'modified': "Modified",
        'comment_added_suffix': " · comment added",
        'name_repeated': "duplicate filename",
        'err_empty': "empty",
        'err_too_long': "too long ({n}/{max}{unit})",
        'err_unit_chars': " chars",
        'err_unit_bytes': " bytes",
        'err_not_ascii': "character not allowed (ASCII only)",
        'err_control': "control characters not allowed",
        'no_comment_ncp': "(not available in .ncp)",
        'no_comment_np3': "(unrecognized .np3 structure: comment not editable)",
        'no_comment_add': "(no comment · double-click to add)",

        'confirm_unsaved_title': "Unsaved changes",
        'confirm_unsaved_msg': "{n} file(s) have unsaved changes.\nContinue and discard them?\n\n(The original files on disk are never touched.)",
        'action_replace': "Replace the list",
        'action_clear': "Clear the list",
        'skipped_title': "Unrecognized format",
        'skipped_msg': "Skipped files:\n{list}",

        'export_none_title': "No files",
        'export_none_msg': "No files loaded to export.",
        'export_nochg_title': "No changes",
        'export_nochg_msg': "No changes recorded yet.\nExport an empty CSV anyway?",
        'export_dialog_title': "Save change log",
        'export_ok_title': "Log exported",
        'export_ok_msg': "Exported {n} changes to:\n{path}",
        'export_hint': "CSV with {n} changes exported",
        'export_initial': "change_log.csv",

        'save_dialog_title': "Output folder",
        'overwrite_title': "Overwrite originals",
        'overwrite_msg': "You have selected the source folder as destination.\n{n} original files will be overwritten.\n\nContinue?",
        'err_read_folder': "Cannot read the folder",
        'confirm_reset_title': "Reset",
        'confirm_reset_msg': "No rows selected. Reset ALL?",
        'err_number_title': "Invalid value",
        'err_number_msg': "\"Start at\" and \"Digits\" must be integers.",
        'hint_undo': "Action undone",
        'hint_added_files': "Added {n} new files",
        'hint_batch': "{n} fields modified in batch",
        'save_ok_title': "Result",
        'save_ok_msg': "{n} files saved to:\n{path}",
        'save_added_msg': "\n\n{added} with ADDED comment (experimental): test them in NX Studio.",
        'save_skipped_msg': "\n\n{skipped} skipped due to name conflict.",
        'save_overwritten_msg': "\n\n{overwritten} overwritten.",
        'save_errors_msg': "\n\n{count} with error:\n{list}",
        'save_cancelled': "Save cancelled.",
        'conflict_title': "Name conflict",
        'conflict_msg': "A file with this name already exists:\n\n    {file}\n\nWhat would you like to do?",
        'conflict_overwrite': "Overwrite",
        'conflict_skip': "Skip",
        'conflict_rename': "Rename _1",
        'conflict_cancel': "Cancel",
        'conflict_apply_all': "Apply this choice to all remaining conflicts",

        'lang_es': "Español",
        'lang_en': "English",

        'help_err_title': "Cannot open help",
        'help_err_msg': "File not found:\n{path}\n\nPlace it in the same folder as the program.",

        'edit_name_label': "Name",
        'edit_comment_label': "Comment",
        'edit_name_count': "{label}: {n}/{max} chars",
        'edit_comment_count': "{label}: {n}/{max} chars · {b}/{bmax} bytes",

        'menu_backup': "Back up originals when overwriting",
        'all_files': "All files",
        'name_repeated_note': " · duplicate filename (_1 will be added)",
        'files_visible_suffix': " · {v} visible",
        'overwrite_backup_note': "\n\nA backup of the originals will be made first.",
        'overwrite_nobackup_note': "\n\nBackup is turned off: this action cannot be undone.",
        'save_backup_msg': "\n\n{n} originals backed up to:\n{path}",
        'save_autorenamed_msg': "\n\n{n} saved with a _1 suffix because of duplicate filenames.",
        'err_backup': "could not back up the original ({e}); the original was not touched",
        'err_write': "could not write ({e}); the destination was not modified",
        'verify_failed': "verification failed; the destination was not modified",
        'no_files_title': "No files",
        'no_files_msg': "No .np3 / .ncp files found in:\n{path}",
        'error_title': "Error",
        'unexpected_error_title': "Unexpected error",
        'lang_rebuild_error': "Could not rebuild the interface after changing language.",
        'export_status_saved': "saved",
        'export_status_pending': "pending",
    },
}

_LANG = 'es'

# Los emojis de color pueden dar problemas con Tk en algunos Linux: solo en Windows/macOS.
EMOJI = sys.platform in ("win32", "darwin") or os.environ.get("Ednoki_EMOJI") == "1"
_EMOJI_RE = re.compile(r"^[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF][\uFE0F\u200d]*\s*")
_FONT_FAMILY = "Segoe UI" if sys.platform == "win32" else None


def F(size=9, style=""):
    """Fuente de la interfaz: Segoe UI en Windows y la fuente por defecto del sistema en el resto."""
    global _FONT_FAMILY
    if _FONT_FAMILY is None:
        try:
            _FONT_FAMILY = tkfont.nametofont("TkDefaultFont").actual("family")
        except Exception:
            _FONT_FAMILY = "TkDefaultFont"
    return (_FONT_FAMILY, size, style) if style else (_FONT_FAMILY, size)


def tr(key, **kw):
    s = STRINGS.get(_LANG, STRINGS['es']).get(key) or key
    if not EMOJI:
        s = _EMOJI_RE.sub("", s)
    if kw:
        try:
            return s.format(**kw)
        except (KeyError, IndexError):
            return s
    return s


def set_lang(code):
    global _LANG
    if code in STRINGS:
        _LANG = code


# =========================================================== resource / prefs
ICON_FILE = "app_icon.ico"   # junto al programa; con PyInstaller: --add-data "app_icon.ico;."


def set_app_icon(root) -> None:
    """Pone el icono del programa (ventana y barra de tareas) en lugar de la pluma de Tk.
    Con default=... lo heredan también los diálogos. Solo Windows (.ico); si falla, queda el de Tk."""
    if sys.platform != "win32":
        return
    try:
        root.iconbitmap(default=str(resource_path(ICON_FILE)))
    except Exception:
        pass


def resource_path(name: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / name
    return Path(__file__).resolve().parent / name


def prefs_path(app_dir: str = "Ednoki") -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / app_dir / "prefs.json"


def load_prefs() -> dict:
    for app_dir in ("Ednoki", "ENICON", "NikonPCEditor"):  # los dos últimos son nombres antiguos (migración de preferencias)
        try:
            return json.loads(prefs_path(app_dir).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def system_lang() -> str:
    """'en' si el sistema está en inglés, 'es' en cualquier otro caso (sin locale.getdefaultlocale,
    obsoleto desde Python 3.11)."""
    try:
        import ctypes
        return "en" if (ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF) == 0x09 else "es"
    except Exception:
        pass
    code = (os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES")
            or os.environ.get("LANG") or "").lower()
    return "en" if code.startswith("en") else "es"


def save_prefs(data: dict) -> None:
    try:
        p = prefs_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


# =========================================================== formato de archivo
def parse_fields(d: bytes):
    if d[:4] != b"NCP\x00":
        return None
    if d[16:20] == b"\x00\x00\x02\x00":  # NP3
        if len(d) < 24:
            return None
        n = struct.unpack(">I", d[20:24])[0]
        if not (0 < n <= 64 and 24 + n <= len(d)):
            return None
        comment, p, last = None, 24 + n, b"\x00\x00\x02\x00"
        while p + 8 <= len(d):
            tag, ln = d[p:p + 4], struct.unpack(">I", d[p + 4:p + 8])[0]
            if tag[0] != 0 or tag[3] != 0 or ln > 2048 or p + 8 + ln > len(d):
                break
            if tag == b"\x00\x01\x01\x00":
                comment = (p + 8, ln)
                break
            last = tag
            p += 8 + ln
        insert_at = None
        if comment is None and last == b"\x00\x00\x20\x00" and (
                d[p:p + 4] == b"\x00\x00\x00\x02" or d[p:] == b"\x00\x00\x00\x00"):
            insert_at = p
        return {"fmt": "NP3", "name": (24, n), "comment": comment, "insert_at": insert_at}
    if d[8:12] == b"\x00\x00\x00\x24":  # NCP
        return {"fmt": "NCP", "name": (16, 20), "comment": None, "insert_at": None}
    return None


def get_text(d: bytes, loc, enc: str = "latin-1") -> str:
    off, n = loc
    raw = d[off:off + n].split(b"\x00", 1)[0]
    if enc == "utf-8":
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1")


def put_text(d: bytes, loc, text: str, enc: str = "ascii") -> bytes:
    off, n = loc
    raw = text.encode(enc)
    if len(raw) > n - 1:
        raise ValueError("text too long")
    return d[:off] + raw.ljust(n, b"\x00") + d[off + n:]


def build_comment_record(text: str) -> bytes:
    raw = text.encode("utf-8")
    n = (len(raw) + 2) // 2 * 2
    return b"\x00\x01\x01\x00" + struct.pack(">I", n) + raw.ljust(n, b"\x00")


def insert_comment(d: bytes, at: int, text: str) -> bytes:
    return d[:at] + build_comment_record(text) + d[at:]


def replace_comment(d: bytes, comment_loc: tuple, text: str) -> bytes:
    """Reemplaza el bloque TLV del comentario, expandiéndolo o contrayéndolo."""
    start = comment_loc[0] - 8
    old_data_len = comment_loc[1]
    old_total_len = old_data_len + 8
    new_record = build_comment_record(text)
    return d[:start] + new_record + d[start + old_total_len:]


MAX_COMMENT_CHARS = 256  # límite documentado por Nikon para el comentario
MAX_COMMENT_BYTES = 510  # límite en bytes del texto UTF-8: el lector acepta registros de hasta 2048 B


def check_text(text: str, maxlen: int, required: bool, ascii_only: bool = True):
    """Nombre: ASCII y caracteres. Comentario: UTF-8, caracteres Y bytes."""
    if required and not text.strip():
        return tr("err_empty")
    if len(text) > maxlen:
        return tr("err_too_long", n=len(text), max=maxlen, unit=tr("err_unit_chars"))
    if ascii_only:
        if any(ord(c) < 32 or ord(c) > 126 for c in text):
            return tr("err_not_ascii")
    else:
        nbytes = len(text.encode("utf-8", "replace"))
        if nbytes > MAX_COMMENT_BYTES:
            return tr("err_too_long", n=nbytes, max=MAX_COMMENT_BYTES, unit=tr("err_unit_bytes"))
        if any(ord(c) < 32 for c in text):
            return tr("err_control")
    return None


def safe_filename(name: str, suffix: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", name) + suffix


def natural_key(text: str):
    """Orden natural: 'receta 2' antes que 'receta 10'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", text)]


# =========================================================== operaciones por lotes
OPS = [
    ("add_prefix", "op_lbl_prefix", ""),
    ("add_suffix", "op_lbl_suffix", ""),
    ("find_replace", "op_lbl_find", "op_lbl_replace"),
    ("upper", "", ""),
    ("lower", "", ""),
    ("title", "", ""),
    ("number", "op_lbl_start", "op_lbl_digits"),
    ("set", "op_lbl_text", ""),
]


def transform(op_id: str, text: str, a: str, b: str, i: int) -> str:
    if op_id == "add_prefix":
        return a + text
    if op_id == "add_suffix":
        return text + a
    if op_id == "find_replace":
        return text.replace(a, b) if a else text
    if op_id == "upper":
        return text.upper()
    if op_id == "lower":
        return text.lower()
    if op_id == "title":
        return string.capwords(text)
    if op_id == "number":
        return f"{text} {int(a or 1) + i:0{int(b or 2)}d}"
    if op_id == "set":
        return a
    return text


# =========================================================== modelo
ADD_MAX = MAX_COMMENT_CHARS
BG_MAIN = "#f5f5f5"
BG_ODD = "#f0f0f0"
BG_EVEN = "#ffffff"
BG_CHG = "#fff3bf"
BG_ERR = "#f8d7da"


@dataclass
class Row:
    path: Path
    fmt: str
    name_loc: tuple
    comment_loc: object
    name0: str
    comment0: object
    name: str
    comment: object
    insert_at: object = None

    @property
    def name_max(self):
        return self.name_loc[1] - 1

    @property
    def comment_max(self):
        if self.comment_loc:
            return ADD_MAX
        return ADD_MAX if self.insert_at is not None else 0

    @property
    def name_changed(self):
        return self.name != self.name0

    @property
    def comment_changed(self):
        return self.comment is not None and self.comment != self.comment0

    @property
    def changed(self):
        return self.name_changed or self.comment_changed


class ToolTip:
    def __init__(self, widget, text_func):
        self.widget = widget
        self.text_func = text_func
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip, add="+")
        widget.bind("<Leave>", self.hide_tip, add="+")

    def show_tip(self, event=None):
        text = self.text_func()
        if not text or self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=text, justify="left", background="#ffffe0",
                 relief="solid", borderwidth=1, font=F(9),
                 padx=6, pady=4).pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# =========================================================== App
class App:
    def __init__(self, root: tk.Tk, prefs: dict):
        self.root = root
        self.prefs = prefs

        default_lang = system_lang()
        set_lang(prefs.get("language", default_lang))

        root.title(tr("app_title", ver=APP_VERSION))
        root.geometry(self._safe_geometry(prefs.get("geometry")))
        root.minsize(1150, 720)
        root.configure(bg=BG_MAIN)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure(".", background=BG_MAIN)
        style.configure("TFrame", background=BG_MAIN)
        style.configure("TLabelframe", background=BG_MAIN)
        style.configure("TLabelframe.Label", background=BG_MAIN,
                        font=F(9, "bold"))
        style.configure("TLabel", background=BG_MAIN)
        style.configure("TCheckbutton", background=BG_MAIN)
        style.configure("TButton", font=F(9))
        style.configure("Treeview", rowheight=38, font='TkFixedFont',
                        background=BG_EVEN, fieldbackground=BG_EVEN)
        style.configure("Treeview.Heading", font=F(10, "bold"))

        self.rows = {}
        self.undo_stack = []
        self.added = 0
        self._sort = None          # (columna, descendente) o None
        self._next_id = 0          # identificadores de fila propios (no dependen de la ruta)
        self.session_log = []      # cambios ya guardados, para el registro CSV
        self._backup_var = tk.BooleanVar(value=bool(self.prefs.get("backup_originals", True)))

        self.rename_files = tk.BooleanVar(value=False)
        self.summary = tk.StringVar(value="")
        self.hint = tk.StringVar(value="")
        self.full_path_str = tr("no_folder")
        self.path_var = tk.StringVar(value=self.full_path_str)
        self.filter_var = tk.StringVar(value="")

        self.op = tk.StringVar()
        self.target = tk.StringVar()
        self.a_var = tk.StringVar()
        self.b_var = tk.StringVar()
        self.a_lbl = tk.StringVar()
        self.b_lbl = tk.StringVar()
        self._lang_var = tk.StringVar(value=self.prefs.get("language", _LANG))

        self.filter_var.trace_add("write", self._on_filter_change)

        self._op_label_to_id = {}
        self._op_id_to_label = {}

        self._build_menubar()
        self._build()
        self._bind_shortcuts()
        self.refresh_all()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        if IS_MAC:
            self.root.createcommand("tk::mac::Quit", self._on_close)

    # ---------- utilidades
    def _safe_geometry(self, g, default="1300x820"):
        """Recorta la geometría guardada si ya no cabe en la pantalla actual."""
        m = re.match(r"^(\d+)x(\d+)(?:([+-]-?\d+)([+-]-?\d+))?$", g or "")
        if not m:
            return default
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(int(m[1]), sw), min(int(m[2]), sh)
        if m[3] is None:
            return f"{w}x{h}"
        x, y = int(m[3]), int(m[4])
        if x < -50 or y < -50 or x > sw - 150 or y > sh - 150:
            return f"{w}x{h}"
        return f"{w}x{h}{m[3]}{m[4]}"

    @staticmethod
    def _same_file(a: Path, b: Path) -> bool:
        try:
            if a.exists() and b.exists():
                return os.path.samefile(a, b)
        except OSError:
            pass
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))

    def _on_backup_toggle(self):
        self.prefs["backup_originals"] = bool(self._backup_var.get())
        save_prefs(self.prefs)

    def _on_ctrl_z(self, event=None):
        """Ctrl+Z (⌘Z en macOS) deshace la tabla, salvo que se esté escribiendo en un campo de texto."""
        try:
            w = self.root.focus_get()
        except (KeyError, tk.TclError):
            w = None
        if isinstance(w, (tk.Entry, ttk.Entry, ttk.Combobox)):
            return None
        self.undo()
        return "break"

    def _sort_value(self, col, r, st):
        if col == "archivo":
            return natural_key(r.path.name)
        if col == "nombre":
            return natural_key(r.name)
        if col == "comentario":
            return natural_key(r.comment or "")
        return natural_key(st)

    def _update_headings(self):
        for c, key in self._col_keys.items():
            arrow = ""
            if self._sort and self._sort[0] == c:
                arrow = " ▼" if self._sort[1] else " ▲"
            self.tree.heading(c, text=tr(key) + arrow)

    # ---------- callbacks persistentes
    def _on_filter_change(self, *args):
        tree = getattr(self, "tree", None)
        if tree is None:
            return
        try:
            if tree.winfo_exists():
                self.refresh_all()
        except tk.TclError:
            pass

    def _on_close(self):
        if getattr(self, "_closing", False):
            return
        self._closing = True
        self.prefs["geometry"] = self.root.geometry()
        try:
            self.prefs["last_op"] = self._current_op_id()
        except Exception:
            pass
        save_prefs(self.prefs)
        self.root.destroy()

    def _bind_shortcuts(self):
        self.root.bind(f"<{MOD}-z>", self._on_ctrl_z)
        self.root.bind(f"<{MOD}-o>", lambda e: self.ask_folder())
        self.root.bind(f"<{MOD}-e>", lambda e: self.ask_export_csv())
        self.root.bind(f"<{MOD}-s>", lambda e: self.ask_save())
        self.root.bind(f"<{MOD}-q>", lambda e: self._on_close())

    # ---------- cambio de idioma
    def _change_language(self, code):
        if code == self.prefs.get("language", _LANG):
            return
        self.prefs["language"] = code
        try:
            self.prefs["last_op"] = self._current_op_id()
        except Exception:
            self.prefs["last_op"] = OPS[0][0]
        save_prefs(self.prefs)
        self.root.after_idle(lambda: self._apply_language(code))

    def _apply_language(self, code):
        try:
            target_id = ("name" if self.target.get() == tr("target_name")
                         else "comment")
        except tk.TclError:
            target_id = "name"
        try:
            selection = tuple(self.tree.selection())
        except (tk.TclError, AttributeError):
            selection = ()

        try:
            set_lang(code)
            self._lang_var.set(code)
            self._rebuild_ui()
        except Exception:
            import traceback
            err = traceback.format_exc()
            try:
                set_lang("es")
                self._lang_var.set("es")
                self._rebuild_ui()
            except Exception:
                pass
            messagebox.showerror(
                tr("error_title"),
                tr("lang_rebuild_error") + "\n\n" + err[-800:])
            return

        self.target.set(tr("target_name") if target_id == "name"
                        else tr("target_comment"))
        self._update_path_display()
        self.refresh_all()
        if selection:
            valid = [iid for iid in selection if iid in self.rows]
            if valid:
                self.tree.selection_set(valid)
        self.root.update_idletasks()

    def _rebuild_ui(self):
        self.root.title(tr("app_title", ver=APP_VERSION))   # el título también cambia de idioma
        for child in list(self.root.winfo_children()):
            if not isinstance(child, tk.Toplevel):
                try:
                    child.destroy()
                except Exception:
                    pass
        self._build_menubar()
        self._build()

    # ---------- menú
    def _build_menubar(self):
        menubar = tk.Menu(self.root)

        fm = tk.Menu(menubar, tearoff=0)
        fm.add_command(label=tr("menu_open_folder"), accelerator=f"{MOD_LABEL}O",
                       command=self.ask_folder)
        add_m = tk.Menu(fm, tearoff=0)
        add_m.add_command(label=tr("menu_add_files"), command=self.ask_add_files)
        add_m.add_command(label=tr("menu_add_folder"), command=self.ask_add_folder)
        fm.add_cascade(label=tr("menu_add"), menu=add_m)
        fm.add_separator()
        fm.add_command(label=tr("menu_export_csv"), accelerator=f"{MOD_LABEL}E",
                       command=self.ask_export_csv)
        fm.add_separator()
        fm.add_command(label=tr("menu_clear_list"), command=self.clear_list)
        fm.add_separator()
        fm.add_checkbutton(label=tr("menu_backup"), variable=self._backup_var,
                           command=self._on_backup_toggle)
        fm.add_separator()

        lang_m = tk.Menu(fm, tearoff=0)
        lang_m.add_radiobutton(label=tr("lang_es"), variable=self._lang_var,
                               value="es",
                               command=lambda: self._change_language("es"))
        lang_m.add_radiobutton(label=tr("lang_en"), variable=self._lang_var,
                               value="en",
                               command=lambda: self._change_language("en"))
        fm.add_cascade(label=tr("menu_language"), menu=lang_m)
        fm.add_separator()
        fm.add_command(label=tr("menu_exit"), accelerator=f"{MOD_LABEL}Q",
                       command=self._on_close)
        menubar.add_cascade(label=tr("menu_file"), menu=fm)

        hm = tk.Menu(menubar, tearoff=0)
        hm.add_command(label=tr("menu_help_install"),
                       command=lambda: self._show_html("help"))
        menubar.add_cascade(label=tr("menu_help"), menu=hm)

        cm = tk.Menu(menubar, tearoff=0)
        cm.add_command(label=tr("menu_about"),
                       command=lambda: self._show_html("about"))
        menubar.add_cascade(label=tr("menu_about_top"), menu=cm)

        self.root.config(menu=menubar)

    # ---------- UI principal
    def _build(self):
        root = self.root
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

        top = ttk.Frame(root, padding=(12, 10, 12, 4))
        top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text=tr("open_folder"),
                   command=self.ask_folder).pack(side="left", padx=(0, 6))

        # Botón "Añadir" sin la flecha de texto (ttk.Menubutton ya incluye una)
        add_btn = ttk.Menubutton(top, text=tr("add"))
        add_menu = tk.Menu(add_btn, tearoff=0)
        add_menu.add_command(label=tr("add_files"), command=self.ask_add_files)
        add_menu.add_command(label=tr("add_folder"), command=self.ask_add_folder)
        add_btn["menu"] = add_menu
        add_btn.pack(side="left", padx=6)

        info = ttk.Frame(root, padding=(12, 0, 12, 4))
        info.grid(row=1, column=0, sticky="ew")
        ttk.Label(info, text=tr("folder_label"),
                  font=F(9, "bold")).pack(side="left")
        self.path_lbl = ttk.Label(info, textvariable=self.path_var,
                                  foreground="#0a58ca", font=F(9))
        self.path_lbl.pack(side="left", padx=6)
        ToolTip(self.path_lbl, lambda: self.full_path_str)

        ttk.Label(info, text=tr("filter_label"),
                  foreground="#555").pack(side="right", padx=(15, 4))
        ttk.Entry(info, textvariable=self.filter_var, width=26).pack(side="right")

        mid = ttk.Frame(root, padding=(12, 2, 12, 6))
        mid.grid(row=2, column=0, sticky="nsew")
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=1)

        cols = ("archivo", "nombre", "comentario", "estado")
        self.tree = ttk.Treeview(mid, columns=cols, show="headings",
                                 selectmode="extended", height=8)
        self._col_keys = {}
        for c, w, key in (("archivo", 200, "col_file"),
                          ("nombre", 200, "col_name"),
                          ("comentario", 480, "col_comment"),
                          ("estado", 220, "col_status")):
            self._col_keys[c] = key
            self.tree.heading(c, text=tr(key),
                              command=lambda col=c: self.sort_column(col))
            self.tree.column(c, width=w, anchor="w")
        sb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        self.tree.tag_configure("even", background=BG_EVEN)
        self.tree.tag_configure("odd", background=BG_ODD)
        self.tree.tag_configure("changed", background=BG_CHG)
        self.tree.tag_configure("error", background=BG_ERR, foreground="#7a1c24")
        self.tree.bind("<Double-1>", self.on_double_click)

        tip = ttk.Frame(root, padding=(12, 0, 12, 2))
        tip.grid(row=3, column=0, sticky="ew")
        ttk.Label(tip, text=tr("hint_double_click"),
                  foreground="#666",
                  font=F(9, "italic")).pack(side="left")
        ttk.Button(tip, text=tr("clear_list"),
                   command=self.clear_list).pack(side="right")

        batch = ttk.LabelFrame(root, text=tr("batch_group"), padding=10)
        batch.grid(row=4, column=0, sticky="ew", padx=12, pady=(6, 6))

        self._op_label_to_id = {tr(f"op_{o[0]}"): o[0] for o in OPS}
        self._op_id_to_label = {o[0]: tr(f"op_{o[0]}") for o in OPS}

        last_op = self.prefs.get("last_op") or OPS[0][0]
        if last_op not in [o[0] for o in OPS]:
            last_op = OPS[0][0]

        self.op.set(self._op_id_to_label[last_op])
        self.target.set(tr("target_name"))

        ttk.Label(batch, text=tr("field_label")).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Combobox(batch, textvariable=self.target,
                     values=[tr("target_name"), tr("target_comment")],
                     state="readonly", width=12).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(batch, text=tr("op_label")).grid(row=0, column=2, padx=(10, 0), pady=2)
        cb = ttk.Combobox(batch, textvariable=self.op,
                          values=list(self._op_label_to_id.keys()),
                          state="readonly", width=22)
        cb.grid(row=0, column=3, padx=4, pady=2)
        cb.bind("<<ComboboxSelected>>", lambda e: self.update_op_labels())

        self.a_lbl_w = ttk.Label(batch, textvariable=self.a_lbl)
        self.a_lbl_w.grid(row=0, column=4, padx=(10, 0), pady=2)
        self.a_ent = ttk.Entry(batch, textvariable=self.a_var, width=16)
        self.a_ent.grid(row=0, column=5, padx=4, pady=2)

        self.b_lbl_w = ttk.Label(batch, textvariable=self.b_lbl)
        self.b_lbl_w.grid(row=0, column=6, padx=(10, 0), pady=2)
        self.b_ent = ttk.Entry(batch, textvariable=self.b_var, width=16)
        self.b_ent.grid(row=0, column=7, padx=4, pady=2)

        btns = ttk.Frame(batch)
        btns.grid(row=1, column=0, columnspan=8, sticky="w", pady=(8, 0))
        ttk.Button(btns, text=tr("op_apply"),
                   command=self.ask_apply_batch).pack(side="left")
        ttk.Button(btns, text=tr("op_undo"),
                   command=self.undo).pack(side="left", padx=8)
        ttk.Button(btns, text=tr("op_reset"),
                   command=self.ask_reset).pack(side="left")

        a_saved, b_saved = self.a_var.get(), self.b_var.get()
        self._update_op_labels_from_label()
        self.a_var.set(a_saved)
        self.b_var.set(b_saved)

        bot = ttk.Frame(root, padding=(12, 4, 12, 8))
        bot.grid(row=5, column=0, sticky="ew")
        ttk.Checkbutton(bot, text=tr("rename_check"),
                        variable=self.rename_files,
                        command=self.refresh_all).pack(side="left")

        if IS_MAC:
            # En macOS tk.Button es un botón nativo que ignora bg/fg (saldría blanco con
            # texto blanco). Con el tema "clam", un ttk.Button con estilo propio sí
            # respeta los colores.
            style = ttk.Style()
            style.configure("Save.TButton", background="#0d6efd", foreground="white",
                            font=F(10, "bold"), padding=(14, 4),
                            bordercolor="#0b5ed7", lightcolor="#0d6efd",
                            darkcolor="#0b5ed7", focuscolor="#0d6efd")
            style.map("Save.TButton",
                      background=[("pressed", "#0a58ca"), ("active", "#0b5ed7")],
                      foreground=[("disabled", "#cfe2ff")])
            save_btn = ttk.Button(bot, text=tr("save_copies"), command=self.ask_save,
                                  style="Save.TButton", cursor="hand2")
        else:
            save_btn = tk.Button(bot, text=tr("save_copies"),
                                 command=self.ask_save, bg="#0d6efd", fg="white",
                                 font=F(10, "bold"),
                                 padx=14, pady=4, relief="raised", cursor="hand2",
                                 activebackground="#0b5ed7", activeforeground="white")
        save_btn.pack(side="right", padx=4)
        ttk.Label(bot, textvariable=self.hint, foreground="#0a58ca",
                  font=F(9, "bold")).pack(side="right", padx=10)

        ttk.Label(root, textvariable=self.summary, relief="sunken",
                  anchor="w", padding=(8, 4)).grid(row=6, column=0, sticky="ew")

    # ---------- helpers
    def _current_op_id(self):
        label = self.op.get()
        return self._op_label_to_id.get(label, OPS[0][0])

    def _update_op_labels_from_label(self):
        op_id = self._current_op_id()
        _, key_a, key_b = next(o for o in OPS if o[0] == op_id)
        self.a_lbl.set(tr(key_a) if key_a else "")
        self.b_lbl.set(tr(key_b) if key_b else "")
        # Se muestra solo el campo que la operación necesita (grid_remove conserva su posición)
        for lbl_w, ent, key in ((self.a_lbl_w, self.a_ent, key_a), (self.b_lbl_w, self.b_ent, key_b)):
            if key:
                lbl_w.grid()
                ent.grid()
            else:
                lbl_w.grid_remove()
                ent.grid_remove()
        if op_id == "number":
            self.a_var.set(self.a_var.get() or "1")
            self.b_var.set(self.b_var.get() or "2")
        elif op_id != "find_replace":
            self.b_var.set("")

    def update_op_labels(self):
        self._update_op_labels_from_label()

    def _truncate(self, text, n=60):
        return text if len(text) <= n else "…" + text[-(n - 1):]

    def _update_path_display(self):
        folders = sorted({str(r.path.parent) for r in self.rows.values()})
        if not folders:
            self.full_path_str = tr("no_folder")
            self.path_var.set(self.full_path_str)
        elif len(folders) == 1:
            self.full_path_str = tr("files_one_folder", path=folders[0], n=len(self.rows))
            self.path_var.set(self._truncate(self.full_path_str))
        else:
            self.full_path_str = tr("files_n_folders_tip",
                                    n=len(folders), folders="\n".join(folders[:15]))
            self.path_var.set(tr("files_n_folders",
                                 n=len(folders), m=len(self.rows)))

    # ---------- carga / añadir / vaciar
    def _puede_descartar_cambios(self, action_key):
        changed = [r for r in self.rows.values() if r.changed]
        if not changed:
            return True
        return messagebox.askokcancel(
            tr("confirm_unsaved_title"),
            tr("confirm_unsaved_msg", n=len(changed), action=tr(action_key)))

    def ask_folder(self):
        if not self._puede_descartar_cambios("action_replace"):
            return
        f = filedialog.askdirectory(title=tr("open_folder"))
        if f:
            self.rows.clear()
            self.undo_stack.clear()
            self._add_folder(Path(f), quiet_empty=True)
            self._update_path_display()
            self.refresh_all()

    def ask_add_files(self):
        paths = filedialog.askopenfilenames(
            title=tr("add_files"),
            filetypes=[("Nikon Picture Controls", ("*.np3", "*.NP3", "*.ncp", "*.NCP")),
                       (tr("all_files"), "*.*")])
        if paths:
            self._add_paths([Path(p) for p in paths])

    def ask_add_folder(self):
        f = filedialog.askdirectory(title=tr("add_folder"))
        if f:
            self._add_folder(Path(f))

    def clear_list(self):
        if not self.rows:
            return
        if not self._puede_descartar_cambios("action_clear"):
            return
        self.rows.clear()
        self.undo_stack.clear()
        self._update_path_display()
        self.refresh_all()

    def _add_folder(self, folder: Path, quiet_empty=False):
        if not folder.is_dir():
            messagebox.showerror(tr("err_read_folder"), str(folder))
            return
        try:
            items = sorted(folder.iterdir(), key=lambda x: x.name.lower())
        except OSError as e:
            messagebox.showerror(tr("err_read_folder"), str(e))
            return
        found = [p for p in items if p.suffix.lower() in {".np3", ".ncp"} and p.is_file()]
        if not found:
            messagebox.showinfo(tr("no_files_title"), tr("no_files_msg", path=str(folder)))
            return
        self._add_paths(found, quiet_empty=quiet_empty)

    def _add_paths(self, paths, quiet_empty=False):
        existing = {r.path.resolve() for r in self.rows.values()}
        skipped, added = [], 0
        for p in paths:
            if p.resolve() in existing:
                continue
            res = self._read_file_item(p)
            if res is None:
                skipped.append(p.name)
                continue
            iid, row_obj = res
            self.rows[iid] = row_obj
            existing.add(p.resolve())
            added += 1
        self._update_path_display()
        self.refresh_all()
        if added and not quiet_empty:
            self.hint.set(tr("hint_added_files", n=added))
        if skipped:
            messagebox.showwarning(tr("skipped_title"),
                                   tr("skipped_msg", list="\n".join(skipped[:15])))

    def _read_file_item(self, p: Path):
        try:
            d = p.read_bytes()
        except OSError:
            return None
        f = parse_fields(d)
        if f is None:
            return None
        name = get_text(d, f["name"])
        com = (get_text(d, f["comment"], "utf-8") if f["comment"]
               else ("" if f["insert_at"] is not None else None))
        iid = f"r{self._next_id}"
        self._next_id += 1
        return iid, Row(p, f["fmt"], f["name"], f["comment"],
                        name, com, name, com, f["insert_at"])

    # ---------- ordenación / estado
    def sort_column(self, col):
        """Ordena por columna (clic de nuevo = invertir). El orden se conserva al refrescar."""
        if self._sort and self._sort[0] == col:
            self._sort = (col, not self._sort[1])
        else:
            self._sort = (col, False)
        self.refresh_all()

    def target_filename(self, r: Row):
        if self.rename_files.get() and r.name_changed:
            return safe_filename(r.name, r.path.suffix)
        return r.path.name

    def compute_status(self):
        """Devuelve (errores, avisos) por fila. Los avisos no bloquean el guardado."""
        counts = {}
        for r in self.rows.values():
            if r.changed:
                k = self.target_filename(r).lower()
                counts[k] = counts.get(k, 0) + 1
        errors, notes = {}, {}
        for iid, r in self.rows.items():
            errs = []
            if r.name_changed:
                e = check_text(r.name, r.name_max, True, ascii_only=True)
                if e:
                    errs.append(f"{tr('col_name')}: {e}")
            if r.comment_changed:
                e = check_text(r.comment, MAX_COMMENT_CHARS, False, ascii_only=False)
                if e:
                    errs.append(f"{tr('col_comment')}: {e}")
            errors[iid] = errs
            notes[iid] = bool(r.changed and counts.get(self.target_filename(r).lower(), 0) > 1)
        return errors, notes

    def comment_cell(self, r: Row) -> str:
        if r.comment is not None:
            if r.comment == "" and r.comment_loc is None and r.insert_at is not None:
                return tr("no_comment_add")
            return r.comment.replace("\n", " ").replace("\r", " ")
        return tr("no_comment_ncp") if r.fmt == "NCP" else tr("no_comment_np3")

    def refresh_all(self):
        tree = self.tree
        prev_sel = list(tree.selection())
        errors, notes = self.compute_status()
        filter_text = self.filter_var.get().lower().strip()
        total_changed = sum(1 for r in self.rows.values() if r.changed)
        total_err = sum(1 for e in errors.values() if e)

        entries = []
        for iid, r in self.rows.items():
            if (filter_text
                    and filter_text not in r.path.name.lower()
                    and filter_text not in r.name.lower()
                    and filter_text not in (r.comment or "").lower()):
                continue
            errs = errors[iid]
            if errs:
                st, tag = "; ".join(errs), "error"
            elif r.changed:
                st, tag = tr("modified"), "changed"
                if r.comment_changed and r.comment_loc is None:
                    st += tr("comment_added_suffix")
                if notes[iid]:
                    st += tr("name_repeated_note")
            else:
                st, tag = "", ""
            entries.append((iid, r, st, tag))
        if self._sort:
            col, rev = self._sort
            entries.sort(key=lambda e: self._sort_value(col, e[1], e[2]), reverse=rev)

        tree.delete(*tree.get_children())
        for idx, (iid, r, st, tag) in enumerate(entries):
            tags = (tag,) if tag else (("even",) if idx % 2 == 0 else ("odd",))
            tree.insert("", "end", iid=iid,
                        values=(r.path.name, r.name, self.comment_cell(r), st), tags=tags)
        keep = [i for i in prev_sel if tree.exists(i)]
        if keep:
            tree.selection_set(keep)
        self._update_headings()

        summary = tr("files_loaded", n=len(self.rows), c=total_changed, e=total_err)
        if filter_text:
            summary += tr("files_visible_suffix", v=len(entries))
        self.summary.set(summary)

    # ---------- edición individual
    def on_double_click(self, ev):
        if self.tree.identify("region", ev.x, ev.y) != "cell":
            return
        col, iid = self.tree.identify_column(ev.x), self.tree.identify_row(ev.y)
        if not iid or col not in ("#2", "#3"):
            return
        key = "name" if col == "#2" else "comment"
        r = self.rows[iid]
        if key == "comment" and r.comment is None:
            return
        self.begin_edit(iid, key, col)

    def begin_edit(self, iid, key, col):
        r = self.rows[iid]
        bbox = self.tree.bbox(iid, col)
        if not bbox:
            return
        x, y, w, h = bbox
        var = tk.StringVar(value=getattr(r, key))
        ent = ttk.Entry(self.tree, textvariable=var)
        ent.place(x=x, y=y, width=w, height=h)
        ent.focus_set()
        ent.select_range(0, "end")
        maxlen = r.name_max if key == "name" else MAX_COMMENT_CHARS
        label = tr("edit_name_label") if key == "name" else tr("edit_comment_label")

        def upd(*_):
            v = var.get()
            if key == "comment":
                self.hint.set(tr("edit_comment_count", label=label, n=len(v), max=maxlen,
                                 b=len(v.encode("utf-8", "replace")), bmax=MAX_COMMENT_BYTES))
            else:
                self.hint.set(tr("edit_name_count", label=label, n=len(v), max=maxlen))
        var.trace_add("write", upd)
        upd()
        done = []

        def finish(commit):
            if done:
                return
            done.append(1)
            if commit and var.get() != getattr(r, key):
                self.push_undo()
                setattr(r, key, var.get())
            ent.destroy()
            self.hint.set("")
            self.refresh_all()

        ent.bind("<Return>", lambda e: finish(True))
        ent.bind("<Escape>", lambda e: finish(False))
        ent.bind("<FocusOut>", lambda e: finish(True))

    # ---------- deshacer / reset / lotes
    def push_undo(self):
        self.undo_stack.append({i: (r.name, r.comment) for i, r in self.rows.items()})
        del self.undo_stack[:-50]

    def undo(self):
        if not self.undo_stack:
            return
        for i, (n, c) in self.undo_stack.pop().items():
            self.rows[i].name, self.rows[i].comment = n, c
        self.refresh_all()
        self.hint.set(tr("hint_undo"))

    def ask_reset(self):
        sel = self.tree.selection()
        if not sel:
            if not messagebox.askyesno(tr("confirm_reset_title"),
                                       tr("confirm_reset_msg")):
                return
            sel = list(self.rows)
        self.push_undo()
        for iid in sel:
            r = self.rows[iid]
            r.name, r.comment = r.name0, r.comment0
        self.refresh_all()

    def ask_apply_batch(self):
        if not self.rows:
            return
        op_id = self._current_op_id()
        if op_id == "number":
            try:
                int(self.a_var.get() or 1)
                int(self.b_var.get() or 2)
            except ValueError:
                messagebox.showerror(tr("err_number_title"), tr("err_number_msg"))
                return
        target_id = self.target.get()
        key = "name" if target_id == tr("target_name") else "comment"
        a, b = self.a_var.get(), self.b_var.get()
        visible = list(self.tree.get_children())        # filtro y orden tal como se ven
        chosen = set(self.tree.selection())
        iids = [i for i in visible if i in chosen] or visible
        self.push_undo()
        changed = 0
        for i, iid in enumerate(iids):
            r = self.rows.get(iid)
            if not r:
                continue
            cur = getattr(r, key)
            if cur is None:
                continue
            new = transform(op_id, cur, a, b, i)
            if new != cur:
                setattr(r, key, new)
                changed += 1
        self.refresh_all()
        self.hint.set(tr("hint_batch", n=changed))

    # ---------- exportar CSV
    def _log_entries(self):
        """Cambios ya guardados (sesión) + cambios pendientes."""
        out = [dict(e, estado=tr("export_status_saved")) for e in self.session_log]
        for r in self.rows.values():
            if r.changed:
                out.append({
                    "archivo": r.path.name, "carpeta": str(r.path.parent), "guardado_como": "",
                    "nombre_original": r.name0,
                    "nombre_nuevo": r.name if r.name_changed else "",
                    "comentario_original": r.comment0 if r.comment0 is not None else "",
                    "comentario_nuevo": r.comment if r.comment_changed else "",
                    "estado": tr("export_status_pending")})
        return out

    def ask_export_csv(self):
        if not self.rows and not self.session_log:
            messagebox.showinfo(tr("export_none_title"), tr("export_none_msg"))
            return
        entries = self._log_entries()
        if not entries:
            if not messagebox.askyesno(tr("export_nochg_title"), tr("export_nochg_msg")):
                return
        p = filedialog.asksaveasfilename(
            title=tr("export_dialog_title"),
            defaultextension=".csv",
            initialfile=tr("export_initial"),
            filetypes=[("CSV", "*.csv")])
        if not p:
            return
        cols = ["archivo", "nombre_original", "nombre_nuevo", "comentario_original",
                "comentario_nuevo", "carpeta", "guardado_como", "estado"]
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(cols)
            for e in entries:
                w.writerow([e.get(c, "") for c in cols])
        messagebox.showinfo(tr("export_ok_title"),
                            tr("export_ok_msg", n=len(entries), path=p))
        self.hint.set(tr("export_hint", n=len(entries)))

    # ---------- guardar con conflictos
    def _find_free_name(self, target: Path) -> Path:
        base, suffix, i = target.stem, target.suffix, 1
        while True:
            candidate = target.with_name(f"{base}_{i}{suffix}")
            if not candidate.exists():
                return candidate
            i += 1

    def _ask_conflict(self, filename: str):
        result = {"decision": "cancel", "all": False}
        dlg = tk.Toplevel(self.root)
        dlg.title(tr("conflict_title"))
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg=BG_MAIN)

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text=tr("conflict_msg", file=filename),
                  font=F(10)).pack(anchor="w")

        all_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text=tr("conflict_apply_all"),
                        variable=all_var).pack(anchor="w", pady=(10, 12))

        btns = ttk.Frame(frm)
        btns.pack(fill="x")

        def choose(dec):
            result["decision"] = dec
            result["all"] = all_var.get()
            dlg.destroy()

        ttk.Button(btns, text=tr("conflict_overwrite"),
                   command=lambda: choose("overwrite")).pack(side="left", padx=2)
        ttk.Button(btns, text=tr("conflict_skip"),
                   command=lambda: choose("skip")).pack(side="left", padx=2)
        ttk.Button(btns, text=tr("conflict_rename"),
                   command=lambda: choose("rename")).pack(side="left", padx=2)
        ttk.Button(btns, text=tr("conflict_cancel"),
                   command=lambda: choose("cancel")).pack(side="right", padx=2)

        dlg.wait_window()
        return result["decision"], result["all"]

    def save_copies(self, outdir: Path, overwrite_self: bool = False):
        """Guarda los archivos modificados en outdir. Devuelve un dict con el resumen.

        - Escribe en un temporal, lo verifica y solo entonces lo mueve a su sitio (os.replace):
          un fallo NUNCA borra ni deja a medias un archivo que ya existía.
        - overwrite_self=True: el usuario ya ha confirmado sobrescribir los propios originales.
        - Si se sobrescribe y la copia de seguridad está activada, el archivo previo se copia
          antes a <outdir>/_backup_originales/<fecha>/.
        """
        st_err, _notes = self.compute_status()
        res = dict(ok=0, errors=[], skipped=0, overwritten=0, added=0, auto_renamed=0,
                   backed_up=0, backup_dir=None, cancelled=False)
        outdir.mkdir(parents=True, exist_ok=True)
        backup_on = bool(self._backup_var.get())
        backup_dir = outdir / "_backup_originales" / datetime.now().strftime("%Y%m%d_%H%M%S")
        sticky, written = None, set()

        for iid, r in self.rows.items():
            if not r.changed:
                continue
            if st_err[iid]:
                res["errors"].append(f"{r.path.name}: {'; '.join(st_err[iid])}")
                continue
            target = outdir / self.target_filename(r)
            replacing = False
            if os.path.normcase(str(target.resolve())) in written:
                target = self._find_free_name(target)       # colisión dentro de este mismo guardado
                res["auto_renamed"] += 1
            elif target.exists():
                if overwrite_self and self._same_file(target, r.path):
                    replacing = True                        # ya confirmado en ask_save
                else:
                    policy = sticky
                    if policy is None:
                        decision, apply_all = self._ask_conflict(target.name)
                        if decision == "cancel":
                            res["cancelled"] = True
                            return res
                        policy = decision
                        if apply_all:
                            sticky = decision
                    if policy == "skip":
                        res["skipped"] += 1
                        continue
                    if policy == "rename":
                        target = self._find_free_name(target)
                    elif policy == "overwrite":
                        replacing = True

            tmp = target.with_name(target.name + ".tmp")
            try:
                d = r.path.read_bytes()
                if r.name_changed:
                    d = put_text(d, r.name_loc, r.name)
                before, adding = d, (r.comment_changed and r.comment_loc is None)
                if adding:
                    d = insert_comment(d, r.insert_at, r.comment)
                elif r.comment_changed:
                    d = replace_comment(d, r.comment_loc, r.comment)

                tmp.write_bytes(d)
                chk = tmp.read_bytes()
                f = parse_fields(chk)
                good = (f is not None and chk == d
                        and get_text(chk, f["name"]) == r.name
                        and (not r.comment_changed or (
                            f["comment"] is not None
                            and get_text(chk, f["comment"], "utf-8") == r.comment)))
                if good and adding:      # solo se ha insertado el registro: el resto, intacto
                    k = len(d) - len(before)
                    good = (d[:r.insert_at] == before[:r.insert_at]
                            and d[r.insert_at + k:] == before[r.insert_at:])
                elif good and r.comment_changed:   # solo se ha sustituido el registro de comentario
                    start, old_total = r.comment_loc[0] - 8, r.comment_loc[1] + 8
                    new_total = len(build_comment_record(r.comment))
                    good = (d[:start] == before[:start]
                            and d[start + new_total:] == before[start + old_total:])
                if not good:
                    tmp.unlink(missing_ok=True)
                    res["errors"].append(f"{r.path.name}: {tr('verify_failed')}")
                    continue

                if replacing and backup_on:
                    try:
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(target, backup_dir / target.name)
                    except OSError as e:
                        tmp.unlink(missing_ok=True)
                        res["errors"].append(f"{r.path.name}: {tr('err_backup', e=e)}")
                        continue
                    res["backed_up"] += 1
                    res["backup_dir"] = backup_dir
                os.replace(tmp, target)
            except (OSError, ValueError) as e:
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                res["errors"].append(f"{r.path.name}: {tr('err_write', e=e)}")
                continue

            # --- éxito: registro de sesión y actualización del estado de la fila ---
            written.add(os.path.normcase(str(target.resolve())))
            res["ok"] += 1
            res["added"] += bool(adding)
            res["overwritten"] += bool(replacing)
            self.session_log.append({
                "archivo": r.path.name, "carpeta": str(r.path.parent),
                "guardado_como": target.name,
                "nombre_original": r.name0,
                "nombre_nuevo": r.name if r.name_changed else "",
                "comentario_original": r.comment0 if r.comment0 is not None else "",
                "comentario_nuevo": r.comment if r.comment_changed else ""})
            r.path = target
            r.fmt = f["fmt"]
            r.name_loc = f["name"]
            r.comment_loc = f["comment"]
            r.insert_at = f["insert_at"]
            r.name0 = r.name
            r.comment0 = r.comment
        return res

    def ask_save(self):
        if not self.rows:
            return
        initial = self.prefs.get("last_output") or ""
        out = filedialog.askdirectory(title=tr("save_dialog_title"), initialdir=initial)
        if not out:
            return
        outdir = Path(out)

        # Solo cuentan los archivos que realmente se sobrescribirían (misma carpeta Y mismo nombre)
        affected = [r for r in self.rows.values()
                    if r.changed and self._same_file(outdir / self.target_filename(r), r.path)]
        if affected:
            msg = tr("overwrite_msg", n=len(affected))
            msg += tr("overwrite_backup_note" if self._backup_var.get()
                      else "overwrite_nobackup_note")
            if not messagebox.askyesno(tr("overwrite_title"), msg, icon="warning"):
                return

        self.prefs["last_output"] = str(outdir)
        save_prefs(self.prefs)

        res = self.save_copies(outdir, overwrite_self=bool(affected))
        self._update_path_display()
        self.refresh_all()
        if res["cancelled"]:
            self.hint.set(tr("save_cancelled"))
            return

        msg = tr("save_ok_msg", n=res["ok"], path=outdir)
        if res["added"]:
            msg += tr("save_added_msg", added=res["added"])
        if res["overwritten"]:
            msg += tr("save_overwritten_msg", overwritten=res["overwritten"])
        if res["backed_up"]:
            msg += tr("save_backup_msg", n=res["backed_up"], path=res["backup_dir"])
        if res["auto_renamed"]:
            msg += tr("save_autorenamed_msg", n=res["auto_renamed"])
        if res["skipped"]:
            msg += tr("save_skipped_msg", skipped=res["skipped"])
        if res["errors"]:
            msg += tr("save_errors_msg", count=len(res["errors"]),
                      list="\n".join(res["errors"][:12]))
        (messagebox.showwarning if res["errors"] else messagebox.showinfo)(
            tr("save_ok_title"), msg)

    # ---------- ayuda / créditos
    def _show_html(self, kind: str):
        """Abre la página 'help' o 'about' en el navegador, en el idioma actual.
        Si falta la de ese idioma, abre la del otro antes de avisar del error."""
        names = HTML_PAGES[kind]
        order = [names[_LANG]] + [n for lang, n in names.items() if lang != _LANG]
        for name in order:
            path = resource_path(str(Path(HTML_DIR) / name))
            if path.is_file():
                webbrowser.open(path.as_uri())
                return
        expected = resource_path(str(Path(HTML_DIR) / names[_LANG]))
        messagebox.showerror(tr("help_err_title"), tr("help_err_msg", path=str(expected)))


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    prefs = load_prefs()
    root = tk.Tk()
    set_app_icon(root)

    def _tk_exception(exc, val, tb):
        import traceback
        tb_txt = "".join(traceback.format_exception(exc, val, tb))
        try:
            messagebox.showerror(tr("unexpected_error_title"), tb_txt[-1500:])
        except Exception:
            pass
    root.report_callback_exception = _tk_exception

    app = App(root, prefs)
    if len(sys.argv) > 1 and Path(sys.argv[1]).is_dir():
        app._add_folder(Path(sys.argv[1]))
    root.mainloop()


if __name__ == "__main__":
    main()