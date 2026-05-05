from __future__ import annotations

from conan_manager.core.project_links import GITHUB_REPO, GITHUB_URL, KOFI_URL, PATREON_URL
from conan_manager.core.update_checker import (
    ReleaseAsset,
    is_newer_version,
    pick_preferred_asset,
    release_info_from_api,
)
from conan_manager.models.app_preferences import AppPreferences


def test_preferences_roundtrip_release_settings() -> None:
    preferences = AppPreferences(
        ui_size="large",
        dedicated_server_launch_args="-Messaging -log",
        confirmation_mode="none",
        show_result_popups=False,
        auto_check_updates=True,
    )

    loaded = AppPreferences.from_dict(preferences.to_dict())

    assert loaded.ui_size == "large"
    assert loaded.confirmation_mode == "none"
    assert loaded.show_result_popups is False
    assert loaded.auto_check_updates is True


def test_preferences_normalize_invalid_release_settings() -> None:
    preferences = AppPreferences(ui_size="tiny", confirmation_mode="everything").normalized()

    assert preferences.ui_size == "default"
    assert preferences.confirmation_mode == "destructive_only"


def test_update_checker_version_comparison() -> None:
    assert is_newer_version("v0.8.1", "0.8.0")
    assert is_newer_version("1.0.0", "0.9.9")
    assert not is_newer_version("0.8.0", "0.8.0")
    assert not is_newer_version("0.7.9", "0.8.0")
    assert not is_newer_version("preview", "0.8.0")


def test_update_checker_release_api_parsing_and_asset_choice() -> None:
    release = release_info_from_api(
        {
            "tag_name": "v0.8.2",
            "html_url": "https://example.invalid/releases/v0.8.2",
            "assets": [
                {"name": "checksums.txt", "browser_download_url": "https://example.invalid/checksums.txt"},
                {"name": "ConanManager.zip", "browser_download_url": "https://example.invalid/app.zip", "size": 42},
            ],
        }
    )

    assert release.version == "0.8.2"
    assert release.preferred_asset is not None
    assert release.preferred_asset.name == "ConanManager.zip"


def test_update_checker_ignores_checksum_assets() -> None:
    asset = pick_preferred_asset(
        [
            ReleaseAsset("release.sha256", "https://example.invalid/release.sha256"),
            ReleaseAsset("portable.exe", "https://example.invalid/portable.exe"),
        ]
    )

    assert asset is not None
    assert asset.name == "portable.exe"


def test_public_project_links_are_conan_specific() -> None:
    assert GITHUB_REPO == "Vercadi/conan-exiles-enhanced-manager"
    assert GITHUB_URL.endswith("/conan-exiles-enhanced-manager")
    assert "ko-fi.com/vercadi" in KOFI_URL
    assert "Vercadi" in PATREON_URL

