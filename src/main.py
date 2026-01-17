#!/usr/bin/env python3
"""
ZeroBrave - Privacy-focused policy configurator for Brave Browser.

This tool downloads and applies privacy-enhancing policies to Brave Browser,
disabling telemetry, AI features, and other privacy-invasive functionality.
"""

import argparse
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import urllib.error
import urllib.request

__version__ = "1.1.2"

SOURCE_URL = "https://raw.githubusercontent.com/rompelhd/ZeroBrave/refs/heads/main/policies.json"
REQUEST_TIMEOUT = 10  # seconds until the request times out

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def get_policy_paths() -> dict[str, Path]:
    """
    Get the policy file paths for all supported operating systems.
    
    Returns:
        Dictionary mapping OS names to their policy paths.
    """
    return {
        "windows": Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\policy\managed\policies.json"),
        "linux": Path("/etc/brave/policies/managed/policies.json"),
        "darwin": Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser/policies/managed/policies.json",
    }

def is_brave_flatpak() -> bool:
    try:
        result = subprocess.run(
            ["flatpak", "info", "com.brave.Browser"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def ask_yes_no(msg: str) -> bool:
    """Ask user a yes/no question via input and return True for 'y'."""
    response = input(f"{msg} [y/N]: ").strip().lower()
    if response == "y":
        logger.debug(f"User answered YES to: {msg}")
    else:
        logger.debug(f"User answered NO to: {msg}")
    return response == "y"

def grant_flatpak_permission():
    """Grant Brave Flatpak access to /etc/brave using flatpak override."""
    logger.info("Applying Flatpak override for Brave...")
    subprocess.run(
        [
            "flatpak",
            "override",
            "--system",
            "com.brave.Browser",
            "--filesystem=/etc/brave",
        ],
        check=True,
    )
    logger.info("Flatpak permission granted.")

def get_policy_path() -> Path:
    """
    Get the policy file path for the current operating system.
    
    Returns:
        Path to the policies.json file.
        
    Raises:
        RuntimeError: If the OS is not supported.
    """
    system = platform.system().lower()
    paths = get_policy_paths()
    
    if system not in paths:
        raise RuntimeError(
            f"Unsupported operating system: {system}. "
            f"Supported: {', '.join(paths.keys())}"
        )
    
    return paths[system]


def check_permissions() -> bool:
    """
    Check if the script has sufficient permissions to write policies.
    
    Returns:
        True if permissions are sufficient, False otherwise.
    """
    system = platform.system().lower()
    
    if system == "windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        # Linux/macOS: check if running as root
        return os.geteuid() == 0


def is_brave_installed() -> bool:
    """
    Check if Brave browser is installed on the system.
    
    Returns:
        - True if Brave appears to be installed
        - False otherwise
    """
    system = platform.system().lower()
    
    brave_paths = {
        "windows": [
            Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
            Path(r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ],
        "linux": [
            Path("/usr/bin/brave"),
            Path("/usr/bin/brave-browser"),
            Path("/snap/bin/brave"),
            Path("/opt/brave.com/brave/brave"),
        ],
        "darwin": [
            Path("/Applications/Brave Browser.app"),
            Path.home() / "Applications/Brave Browser.app",
        ],
    }
    
    paths = brave_paths.get(system, [])
    return any(p.exists() for p in paths)


def strip_json_comments(json_str: str) -> str:
    """
    Remove JavaScript-style comments from a JSON string (JSONC support).
    
    Handles both single-line (//) and multi-line (/* */) comments,
    while preserving strings that contain comment-like patterns.
    
    Args:
        json_str: JSON string potentially containing comments.
        
    Returns:
        Clean JSON string without comments.
    """
    # Pattern to match strings, single-line comments, or multi-line comments
    pattern = r'("(?:[^"\\]|\\.)*")|//[^\n]*|/\*[\s\S]*?\*/'
    
    def replacer(match: re.Match) -> str:
        # If it's a string (group 1), keep it
        if match.group(1):
            return match.group(1)
        # Otherwise it's a comment, remove it
        return ''
    
    return re.sub(pattern, replacer, json_str)


def ensure_dir(path: Path) -> None:
    """Create parent directories for a path if they don't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def create_backup(path: Path) -> Optional[Path]:
    """
    Create a backup of an existing policy file.
    
    Args:
        path: Path to the file to backup.
        
    Returns:
        Path to the backup file, or None if no backup was created.
    """
    if not path.exists():
        logger.info("No existing policies file to backup")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".backup_{timestamp}")
    
    shutil.copy2(path, backup_path)
    logger.info(f"Backup created: {backup_path}")
    return backup_path


def find_latest_backup(path: Path) -> Optional[Path]:
    """
    Find the most recent backup file for a policy file.
    
    Args:
        path: Path to the original policy file.
        
    Returns:
        Path to the latest backup, or None if no backups exist.
    """
    backup_pattern = f"{path.stem}.backup_*"
    backups = sorted(path.parent.glob(backup_pattern), reverse=True)
    return backups[0] if backups else None


def restore_backup(path: Path) -> bool:
    """
    Restore the most recent backup of the policy file.
    
    Args:
        path: Path to the policy file location.
        
    Returns:
        True if restore was successful, False otherwise.
    """
    backup = find_latest_backup(path)
    
    if not backup:
        logger.error("No backup found to restore")
        return False
    
    shutil.copy2(backup, path)
    logger.info(f"Restored from: {backup}")
    return True


def download_json(url: str) -> dict:
    """
    Download and parse JSON from a URL.
    
    Args:
        url: URL to download from.
        
    Returns:
        Parsed JSON as a dictionary.
        
    Raises:
        RuntimeError: If download fails.
    """
    try:
        with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Download failed: HTTP {resp.status}")
            data = resp.read()
        # Strip comments for JSONC support (JSON does not support comments by default)
        clean_json = strip_json_comments(data.decode("utf-8"))
        return json.loads(clean_json)
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP error {e.code}: {e.reason}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {e}")


def load_local_json(path: Path) -> dict:
    """
    Load and parse JSON/JSONC from a local file.
    
    Supports JSONC (JSON with Comments) format.
    
    Args:
        path: Path to the JSON file.
        
    Returns:
        Parsed JSON as a dictionary.
        
    Raises:
        RuntimeError: If loading fails.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            content = f.read()
        # Strip comments for JSONC support (JSON does not support comments by default)
        clean_json = strip_json_comments(content)
        return json.loads(clean_json)
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}")


def validate_policies(policies: dict) -> list[str]:
    """
    Validate the structure of policies JSON.
    
    Args:
        policies: Dictionary of policies to validate.
        
    Returns:
        List of warning messages (empty if valid).
    """
    warnings = []
    
    if not isinstance(policies, dict):
        warnings.append("Policies must be a JSON object")
        return warnings
    
    # Expected types for known policies
    expected_types = {
        # Booleans
        "BraveAIChatEnabled": bool,
        "BlockThirdPartyCookies": bool,
        "MetricsReportingEnabled": bool,
        "SyncDisabled": bool,
        "PasswordManagerEnabled": bool,
        "TranslateEnabled": bool,
        "SpellcheckEnabled": bool,
        "QuicAllowed": bool,
        "AutoplayAllowed": bool,
        "ComponentUpdatesEnabled": bool,
        # Integers
        "SafeBrowsingProtectionLevel": int,
        "HelpMeWriteSettings": int,
        "GeminiSettings": int,
        "GenAiDefaultSettings": int,
        "DefaultCookiesSetting": int,
        "DefaultGeolocationSetting": int,
        "DefaultNotificationsSetting": int,
        "BrowserSignin": int,
        "DiskCacheSize": int,
        # Strings
        "WebRtcIPHandling": str,
        "DnsOverHttpsMode": str,
        # Lists
        "CookiesSessionOnlyForUrls": list,
    }
    
    # Validate types for known policies
    for key, expected_type in expected_types.items():
        if key in policies:
            value = policies[key]
            if not isinstance(value, expected_type):
                warnings.append(
                    f"'{key}' should be {expected_type.__name__}, got {type(value).__name__}"
                )
    
    # Check for potentially dangerous settings
    if policies.get("ComponentUpdatesEnabled") is False:
        warnings.append(
            "ComponentUpdatesEnabled=false may prevent security updates"
        )
    
    return warnings


def write_json(path: Path, data: dict, dry_run: bool = False) -> None:
    """
    Write JSON data to a file.
    
    Args:
        path: Path to write to.
        data: Dictionary to write as JSON.
        dry_run: If True, only simulate the write.
    """
    if dry_run:
        logger.info(f"[DRY-RUN] Would write to: {path}")
        logger.info(f"[DRY-RUN] Content preview:\n{json.dumps(data, indent=2)[:500]}...")
        return
    
    ensure_dir(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Policies written to: {path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="zerobrave",
        description="Privacy-focused policy configurator for Brave Browser",
        epilog="For more info: https://github.com/rompelhd/ZeroBrave"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    parser.add_argument(
        "-b", "--backup",
        action="store_true",
        help="Create backup of existing policies before overwriting"
    )
    
    parser.add_argument(
        "-r", "--restore",
        action="store_true",
        help="Restore the most recent backup"
    )
    
    parser.add_argument(
        "-l", "--local",
        type=Path,
        metavar="FILE",
        help="Use a local JSON file instead of downloading"
    )
    
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip permission and installation checks"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-error output"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for ZeroBrave.
    
    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    try:
        target_path = get_policy_path()
        logger.debug(f"Target path: {target_path}")
        
        # Handle restore mode
        if args.restore:
            if not args.skip_checks and not check_permissions():
                logger.error("Insufficient permissions. Run with sudo/admin rights.")
                return 1
            
            if restore_backup(target_path):
                logger.info("Backup restored successfully!")
                return 0
            return 1
        
        # Pre-flight checks
        if not args.skip_checks:
            if not check_permissions():
                logger.error("Insufficient permissions. Run with sudo/admin rights.")
                return 1
            
            if not is_brave_installed():
                logger.warning("Brave browser not detected. Proceeding anyway...")
        
        # Load policies
        if args.local:
            logger.info(f"Loading policies from: {args.local}")
            policies = load_local_json(args.local)
        else:
            logger.info(f"Downloading policies from: {SOURCE_URL}")
            policies = download_json(SOURCE_URL)
        
        # Validate policies
        warnings = validate_policies(policies)
        for warning in warnings:
            logger.warning(warning)
        
        # Create backup if requested
        if args.backup and not args.dry_run:
            create_backup(target_path)
        
        # Write policies
        write_json(target_path, policies, dry_run=args.dry_run)
        
        # Flatpak support (Linux only)
        if platform.system().lower() == "linux" and is_brave_flatpak():
            logger.info("Brave is installed as a Flatpak.")
            if ask_yes_no("Grant Flatpak access to /etc/brave so policies can be applied?"):
                grant_flatpak_permission()
                logger.info("Please restart Brave for changes to take effect.")
            else:
                logger.warning(
                    "Without this permission, Brave Flatpak will not read system policies."
                )
        
        if not args.dry_run:
            logger.info("✓ Policies applied successfully!")
            logger.info("→ Restart Brave browser for changes to take effect.")
        
        return 0
        
    except RuntimeError as e:
        logger.error(str(e))
        return 1
    except PermissionError:
        logger.error("Permission denied. Run with sudo/admin rights.")
        return 1
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled.")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
