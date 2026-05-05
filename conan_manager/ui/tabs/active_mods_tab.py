"""Active Mods tab for v0.2 local modlist management."""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from ...models.modlist import TARGET_BOTH, TARGET_CLIENT, TARGET_DEDICATED_SERVER
from ...core.list_formatting import format_active_mod_row
from ...core.modlist_service import missing_entries


TARGET_CHOICES = {
    "Client": TARGET_CLIENT,
    "Dedicated Server": TARGET_DEDICATED_SERVER,
    "Both": TARGET_BOTH,
}


class ActiveModsTab(ctk.CTkFrame):
    def __init__(self, master, *, app):
        super().__init__(master)
        self.app = app
        self._target_var = ctk.StringVar(value="Both")
        self._selected_index: int | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="#101010")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Active Mods",
            font=self.app.ui_font("page_title"),
            text_color="#f1e7d0",
        ).grid(row=0, column=0, sticky="w")
        self._parity_label = ctk.CTkLabel(
            header,
            text="",
            font=self.app.ui_font("small"),
            text_color="#b9aa92",
            anchor="w",
        )
        self._parity_label.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        body = ctk.CTkFrame(self, fg_color="#191715", border_width=1, border_color="#3a3028")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(body, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        for col in range(9):
            toolbar.grid_columnconfigure(col, weight=0)
        toolbar.grid_columnconfigure(8, weight=1)

        self._button(toolbar, "Add .pak", self._add_paks, column=0)
        self._button(toolbar, "Import File", self._import_modlist_file, column=1)
        self._button(toolbar, "Load Client", self._load_client_modlist, column=2)
        self._button(toolbar, "Load Server", self._load_server_modlist, column=3)
        self._button(toolbar, "Up", self._move_up, column=4)
        self._button(toolbar, "Down", self._move_down, column=5)
        self._button(toolbar, "Remove", self._remove_selected, column=6)

        self._target_menu = ctk.CTkOptionMenu(
            toolbar,
            variable=self._target_var,
            values=list(TARGET_CHOICES.keys()),
            width=150,
            height=self.app.ui_tokens.compact_button_height,
            fg_color="#3a3028",
            button_color="#5d3424",
            button_hover_color="#70402c",
            font=self.app.ui_font("body"),
        )
        self._target_menu.grid(row=0, column=7, padx=(8, 0))

        list_frame = ctk.CTkFrame(body, fg_color="#101010", border_width=1, border_color="#3a3028")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        self._listbox = tk.Listbox(
            list_frame,
            bg="#101010",
            fg="#f1e7d0",
            selectbackground="#7d4429",
            selectforeground="#ffffff",
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
            font=("Cascadia Mono", self.app.ui_tokens.mono),
        )
        self._listbox.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self._listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8)
        self._listbox.configure(yscrollcommand=scrollbar.set)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        footer = ctk.CTkFrame(self, fg_color="#101010")
        footer.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 10))
        footer.grid_columnconfigure(0, weight=1)
        self._status_label = ctk.CTkLabel(
            footer,
            text="",
            font=self.app.ui_font("small"),
            text_color="#b9aa92",
            anchor="w",
        )
        self._status_label.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            footer,
            text="Restore Previous",
            width=150,
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#3a3028",
            hover_color="#4a3c31",
            command=self._restore_selected_target,
        ).grid(row=0, column=1, padx=(8, 8))
        ctk.CTkButton(
            footer,
            text="Preview Apply",
            width=140,
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#7d4429",
            hover_color="#925333",
            command=self._preview_apply,
        ).grid(row=0, column=2)

    def _button(self, parent, text: str, command, *, column: int) -> None:
        ctk.CTkButton(
            parent,
            text=text,
            width=100,
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#3a3028",
            hover_color="#4a3c31",
            command=command,
        ).grid(row=0, column=column, padx=(0, 8))

    def refresh(self, *, selected_index: int | None = None) -> None:
        if selected_index is not None:
            self._selected_index = selected_index
        entries = self.app.active_mods
        self._listbox.delete(0, tk.END)
        missing = set(missing_entries(entries))
        for index, entry in enumerate(entries, start=1):
            self._listbox.insert(tk.END, format_active_mod_row(index, entry, missing=entry.normalized_value in missing))
        if self._selected_index is not None and 0 <= self._selected_index < len(entries):
            self._listbox.selection_set(self._selected_index)
            self._listbox.see(self._selected_index)
        else:
            self._selected_index = None
        self._parity_label.configure(text=self.app.parity_summary())
        if entries:
            self._status_label.configure(
                text=f"{len(entries)} active mod(s). Entries marked ! point to missing .pak files."
            )
        else:
            self._status_label.configure(text="No active mods yet. Add .pak files or import an existing modlist.txt.")

    def _on_select(self, _event=None) -> None:
        selection = self._listbox.curselection()
        self._selected_index = int(selection[0]) if selection else None

    def _target_value(self) -> str:
        return TARGET_CHOICES.get(self._target_var.get(), TARGET_BOTH)

    def _add_paks(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select Conan .pak files",
            filetypes=[("Conan pak files", "*.pak"), ("All files", "*.*")],
        )
        if not paths:
            return
        added = self.app.add_local_pak_paths([Path(path) for path in paths])
        if added == 0:
            self.app.notify_info("No Mods Added", "No new .pak files were added.")

    def _import_modlist_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Import modlist.txt",
            filetypes=[("Conan modlist", "modlist.txt"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self._replace_from_modlist(Path(path))

    def _load_client_modlist(self) -> None:
        path = self.app.paths.client_modlist_path
        if not path or not path.is_file():
            self.app.notify_warning("Client Modlist Missing", "Client modlist.txt does not exist yet.")
            return
        self._replace_from_modlist(path)

    def _load_server_modlist(self) -> None:
        path = self.app.paths.dedicated_server_modlist_path
        if not path or not path.is_file():
            self.app.notify_warning("Server Modlist Missing", "Dedicated server modlist.txt does not exist yet.")
            return
        self._replace_from_modlist(path)

    def _replace_from_modlist(self, path: Path) -> None:
        if self.app.active_mods:
            ok = self.app.confirm_action(
                "bulk",
                "Replace Active Mods",
                "Importing a modlist replaces the current active list in the manager. Continue?",
            )
            if not ok:
                return
        count = self.app.replace_active_mods_from_modlist(path)
        self.app.notify_info("Modlist Imported", f"Imported {count} modlist entr{'y' if count == 1 else 'ies'}.")

    def _move_up(self) -> None:
        if self._selected_index is None:
            return
        self._selected_index = self.app.move_active_mod(self._selected_index, -1)

    def _move_down(self) -> None:
        if self._selected_index is None:
            return
        self._selected_index = self.app.move_active_mod(self._selected_index, 1)

    def _remove_selected(self) -> None:
        if self._selected_index is None:
            return
        self.app.remove_active_mod_at(self._selected_index)

    def _preview_apply(self) -> None:
        self.app.preview_apply_modlist(self._target_value())

    def _restore_selected_target(self) -> None:
        self.app.restore_selected_modlist(self._target_value())
