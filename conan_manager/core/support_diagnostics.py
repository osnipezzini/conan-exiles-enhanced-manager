"""Redacted support report generation."""
from __future__ import annotations

import os
import platform
import re
import sys
from pathlib import Path
from typing import Iterable

from .. import __app_name__, __version__
from ..models.activity import ActivityRecord
from ..models.app_paths import ConanAppPaths
from ..models.hosted import HostedProfile

SENSITIVE_FIELD_PATTERN = re.compile(
    r"(?i)\b(password|pass|token|api[_-]?key|private[_-]?key|secret)\b\s*[:=]\s*([^\r\n|]+)"
)


def redact_sensitive_text(text: str, *, secrets: Iterable[str] = ()) -> str:
    redacted = str(text or "")
    for secret in secrets:
        if secret:
            redacted = redacted.replace(str(secret), "<redacted>")
    redacted = SENSITIVE_FIELD_PATTERN.sub(lambda match: f"{match.group(1)}=<redacted>", redacted)
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    if username:
        redacted = re.sub(
            rf"(?i)([A-Z]:\\Users\\){re.escape(username)}(?=\\)",
            r"\1<user>",
            redacted,
        )
        redacted = re.sub(
            rf"(?i)([A-Z]:/Users/){re.escape(username)}(?=/)",
            r"\1<user>",
            redacted,
        )
    return redacted


def redact_path(path: Path | str | None) -> str:
    if not path:
        return "Not configured"
    return redact_sensitive_text(str(path))


class SupportDiagnosticsService:
    """Builds a copy/paste-friendly diagnostics report."""

    def build_report(
        self,
        *,
        paths: ConanAppPaths,
        data_dir: Path,
        backup_root: Path,
        hosted_profiles: Iterable[HostedProfile] = (),
        activity_records: Iterable[ActivityRecord] = (),
        log_tail_lines: int = 80,
    ) -> str:
        sections = [
            self._header(),
            self._steam_summary(paths),
            self._target_summary(paths),
            self._hosted_summary(hosted_profiles),
            self._activity_summary(activity_records),
            self._storage_summary(data_dir, backup_root),
            self._log_tail(data_dir / "manager.log", log_tail_lines),
        ]
        return redact_sensitive_text("\n\n".join(sections))

    @staticmethod
    def _header() -> str:
        frozen = bool(getattr(sys, "frozen", False))
        return "\n".join(
            [
                "Conan Exiles Enhanced Manager support info",
                f"App: {__app_name__} v{__version__}",
                f"Build: {'frozen exe' if frozen else 'source/dev'}",
                f"Python: {platform.python_version()}",
                f"OS: {platform.platform()}",
            ]
        )

    @staticmethod
    def _steam_summary(paths: ConanAppPaths) -> str:
        client = paths.client_manifest
        server = paths.dedicated_server_manifest
        rows = ["Steam:"]
        rows.append(f"- Steam libraries: {len(paths.steamapps_dirs)}")
        rows.append(f"- Client app: {client.name if client else 'missing'} | build {client.buildid if client else 'unknown'}")
        rows.append(
            f"- Dedicated server app: {server.name if server else 'missing'} | "
            f"build {server.buildid if server else 'unknown'}"
        )
        rows.append(f"- Workshop content: {redact_path(paths.workshop_content_dir)}")
        return "\n".join(rows)

    @staticmethod
    def _activity_summary(records: Iterable[ActivityRecord]) -> str:
        rows = ["Recent activity:"]
        record_list = list(records)[:20]
        if not record_list:
            rows.append("- none")
            return "\n".join(rows)
        for record in record_list:
            rows.append(f"- {record.summary}")
        return "\n".join(rows)

    @staticmethod
    def _target_summary(paths: ConanAppPaths) -> str:
        rows = ["Targets:"]
        targets = [
            ("Client Root", paths.client_root),
            ("Client Config", paths.client_config_dir),
            ("Client Saves", paths.client_save_root),
            ("Client Logs", paths.client_log_dir),
            ("Dedicated Server Root", paths.dedicated_server_root),
            ("Dedicated Server Config", paths.dedicated_server_config_dir),
            ("Dedicated Server Saves", paths.dedicated_server_save_root),
            ("Dedicated Server Logs", paths.dedicated_server_log_dir),
        ]
        for label, path in targets:
            exists = "exists" if path and Path(path).exists() else "not found"
            rows.append(f"- {label}: {exists}; {redact_path(path)}")
        rows.append(f"- Client save DBs: {len(paths.client_save_databases())}")
        rows.append(f"- Dedicated server save DBs: {len(paths.dedicated_server_save_databases())}")
        return "\n".join(rows)

    @staticmethod
    def _hosted_summary(profiles: Iterable[HostedProfile]) -> str:
        profile_list = [profile.normalized() for profile in profiles]
        rows = ["Hosted profiles:"]
        rows.append(f"- Count: {len(profile_list)}")
        for profile in profile_list:
            redacted = profile.to_redacted_dict()
            rows.append(
                "- "
                f"{redacted['name']} | {redacted['protocol'].upper()} "
                f"{redacted['host']}:{redacted['port']} | user {redacted['username'] or 'not set'} | "
                f"server folder {redacted['server_folder']}"
            )
        return "\n".join(rows)

    @staticmethod
    def _storage_summary(data_dir: Path, backup_root: Path) -> str:
        return "\n".join(
            [
                "Storage:",
                f"- Data dir: {redact_path(data_dir)}",
                f"- Backup root: {redact_path(backup_root)}",
            ]
        )

    @staticmethod
    def _log_tail(log_path: Path, line_count: int) -> str:
        if not log_path.is_file():
            return "Recent log tail: log file not found"
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return f"Recent log tail: could not read log ({exc})"
        return "Recent log tail:\n" + "\n".join(lines[-line_count:])
