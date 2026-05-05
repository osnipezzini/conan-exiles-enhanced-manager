"""Dedicated Server operations tab."""
from __future__ import annotations

from pathlib import Path

import customtkinter as ctk


class ServerTab(ctk.CTkFrame):
    def __init__(self, master, *, app):
        super().__init__(master)
        self.app = app
        self._value_labels: dict[str, ctk.CTkLabel] = {}
        self._launch_args_var = ctk.StringVar(value=self.app.preferences.dedicated_server_launch_args)
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
            text="Dedicated Server",
            font=self.app.ui_font("page_title"),
            text_color="#f1e7d0",
        ).grid(row=0, column=0, sticky="w")
        self._status_label = ctk.CTkLabel(
            header,
            text="",
            font=self.app.ui_font("small"),
            text_color="#b9aa92",
            anchor="w",
        )
        self._status_label.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        body = ctk.CTkScrollableFrame(self, fg_color="#101010")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        self._status_card = self._make_card(body, row=0, column=0, title="Status")
        self._paths_card = self._make_card(body, row=0, column=1, title="Paths")
        self._config_card = self._make_card(body, row=1, column=0, title="Server Config")
        self._launch_card = self._make_card(body, row=1, column=1, title="Launch")
        self._logs_card = self._make_card(body, row=2, column=0, title="Logs", columnspan=2)

        self._build_rows(
            self._status_card,
            [
                ("runtime", "Runtime"),
                ("restart", "Restart"),
                ("build", "Steam Build"),
            ],
        )
        self._build_rows(
            self._paths_card,
            [
                ("root", "Root"),
                ("config", "Config"),
                ("saves", "Saves"),
                ("logs", "Logs"),
            ],
        )
        self._build_rows(
            self._config_card,
            [
                ("server_name", "Server Name"),
                ("ports", "Ports"),
                ("password", "Server Password"),
                ("admin", "Admin Password"),
                ("max_players", "Max Players"),
                ("pvp", "PVP"),
                ("battleye", "BattlEye"),
                ("server_mod_list", "ServerModList"),
            ],
        )

        ctk.CTkLabel(
            self._launch_card,
            text="Launch Args",
            font=self.app.ui_font("body"),
            text_color="#b9aa92",
        ).grid(row=1, column=0, sticky="w", padx=12, pady=4)
        self._launch_args_entry = ctk.CTkEntry(
            self._launch_card,
            textvariable=self._launch_args_var,
            font=self.app.ui_font("body"),
            fg_color="#101010",
            border_color="#3a3028",
            text_color="#f1e7d0",
        )
        self._launch_args_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=4)
        ctk.CTkButton(
            self._launch_card,
            text="Save Args",
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#3a3028",
            hover_color="#4a3c31",
            command=lambda: self.app.update_dedicated_server_launch_args(self._launch_args_var.get()),
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 10))
        ctk.CTkButton(
            self._launch_card,
            text="Start Server",
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#7d4429",
            hover_color="#925333",
            command=self.app.launch_dedicated_server_from_ui,
        ).grid(row=2, column=1, sticky="ew", padx=12, pady=(6, 10))

        controls = ctk.CTkFrame(self._logs_card, fg_color="transparent")
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        controls.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            controls,
            text="Refresh Status",
            width=130,
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#3a3028",
            hover_color="#4a3c31",
            command=self.refresh,
        ).grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(
            controls,
            text="Open Server Folder",
            width=160,
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#3a3028",
            hover_color="#4a3c31",
            command=lambda: self.app.open_path(self.app.paths.dedicated_server_root),
        ).grid(row=0, column=2, padx=(8, 0))
        ctk.CTkButton(
            controls,
            text="Open Logs Folder",
            width=150,
            height=self.app.ui_tokens.compact_button_height,
            font=self.app.ui_font("body"),
            fg_color="#3a3028",
            hover_color="#4a3c31",
            command=lambda: self.app.open_path(self.app.paths.dedicated_server_log_dir),
        ).grid(row=0, column=3, padx=(8, 0))

        self._log_text = ctk.CTkTextbox(
            self._logs_card,
            height=300,
            font=self.app.ui_font("mono"),
            fg_color="#101010",
            text_color="#f1e7d0",
            border_width=1,
            border_color="#3a3028",
            wrap="none",
        )
        self._log_text.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))

    def _make_card(self, body, *, row: int, column: int, title: str, columnspan: int = 1) -> ctk.CTkFrame:
        card = ctk.CTkFrame(body, fg_color="#191715", border_width=1, border_color="#3a3028")
        padx = 8 if columnspan > 1 else (8 if column == 0 else (4, 8))
        card.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=padx, pady=(0, 8))
        card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card, text=title, font=self.app.ui_font("card_title"), text_color="#d3a15f").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=12,
            pady=(10, 8),
        )
        return card

    def _build_rows(self, card: ctk.CTkFrame, rows: list[tuple[str, str]]) -> None:
        for index, (key, label) in enumerate(rows, start=1):
            ctk.CTkLabel(card, text=label, font=self.app.ui_font("body"), text_color="#b9aa92").grid(
                row=index,
                column=0,
                sticky="w",
                padx=12,
                pady=3,
            )
            value = ctk.CTkLabel(
                card,
                text="",
                font=self.app.ui_font("body"),
                text_color="#f1e7d0",
                justify="right",
                anchor="e",
                wraplength=self.app.ui_tokens.panel_wrap,
            )
            value.grid(row=index, column=1, sticky="e", padx=12, pady=3)
            self._value_labels[key] = value

    def refresh(self) -> None:
        status = self.app.dedicated_server_status()
        config = self.app.dedicated_server_config()
        logs = self.app.dedicated_server_log_snapshot()
        paths = self.app.paths

        self._set("runtime", status.summary, ok=status.running)
        restart_text = (
            f"Recommended: {self.app.server_runtime.restart_reason}"
            if self.app.server_runtime.restart_recommended
            else "No pending restart note"
        )
        self._set("restart", restart_text, ok=not self.app.server_runtime.restart_recommended)
        self._set("build", paths.dedicated_server_manifest.buildid if paths.dedicated_server_manifest else "Unknown")
        self._set("root", _path_label(paths.dedicated_server_root))
        self._set("config", _path_label(paths.dedicated_server_config_dir))
        self._set("saves", _path_label(paths.dedicated_server_save_root))
        self._set("logs", _path_label(paths.dedicated_server_log_dir))
        self._set("server_name", config.server_name or "Not set")
        self._set("ports", config.port_summary)
        self._set("password", "Set" if config.server_password_set else "Not set")
        self._set("admin", "Set" if config.admin_password_set else "Not set")
        self._set("max_players", config.max_players or "Not set")
        self._set("pvp", config.pvp_enabled or "Not set")
        self._set("battleye", config.battleye_enabled or "Not set")
        self._set("server_mod_list", "Set" if config.server_mod_list else "Empty")
        self._status_label.configure(text=f"{status.summary} | {restart_text}")
        self._launch_args_var.set(self.app.preferences.dedicated_server_launch_args)

        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        if logs.log_path:
            filtered = logs.filtered or "(no mod/error/warning lines in current tail)"
            self._log_text.insert("1.0", f"Latest log: {logs.log_path}\n\nFiltered lines:\n{filtered}\n\nTail:\n{logs.tail}")
        else:
            self._log_text.insert("1.0", "No dedicated server log file found.")
        self._log_text.configure(state="disabled")

    def _set(self, key: str, value: str, *, ok: bool | None = None) -> None:
        label = self._value_labels.get(key)
        if not label:
            return
        color = "#f1e7d0"
        if ok is True:
            color = "#74ad7f"
        elif ok is False:
            color = "#c98a2e"
        label.configure(text=value, text_color=color)


def _path_label(path: Path | None) -> str:
    return str(path) if path else "Not configured"
