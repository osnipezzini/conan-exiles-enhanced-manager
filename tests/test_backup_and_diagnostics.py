from __future__ import annotations

from pathlib import Path

from conan_manager.core.backup_manager import BackupManager
from conan_manager.core.discovery import discover_all
from conan_manager.core.support_diagnostics import SupportDiagnosticsService, redact_sensitive_text

from .conftest import create_fake_conan_library


def test_backup_configs_and_saves_copies_expected_files(tmp_path) -> None:
    steamapps = create_fake_conan_library(tmp_path)
    paths = discover_all(extra_steamapps_dirs=[steamapps])
    backup = BackupManager(tmp_path / "backups")

    records = backup.backup_configs_and_saves(paths)

    assert len(records) == 5
    assert all(Path(record.backup_path).is_file() for record in records)
    assert len(backup.list_backups("configs")) == 3
    assert len(backup.list_backups("saves")) == 2


def test_support_diagnostics_redacts_sensitive_fields(tmp_path) -> None:
    steamapps = create_fake_conan_library(tmp_path)
    paths = discover_all(extra_steamapps_dirs=[steamapps])
    service = SupportDiagnosticsService()

    report = service.build_report(paths=paths, data_dir=tmp_path / "data", backup_root=tmp_path / "backups")

    assert "Conan Exiles Enhanced Manager support info" in report
    assert "23086684" in report
    assert "password=<redacted>" == redact_sensitive_text("password=secret-value")
