"""Tests for ZeroBrave main module."""

import json
import platform
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import (
    get_policy_path,
    get_policy_paths,
    validate_policies,
    is_brave_installed,
    find_latest_backup,
    strip_json_comments,
)


class TestGetPolicyPaths:
    """Tests for policy path detection."""
    
    def test_returns_dict_with_all_platforms(self):
        """Should return paths for all supported platforms."""
        paths = get_policy_paths()
        
        assert "windows" in paths
        assert "linux" in paths
        assert "darwin" in paths
    
    def test_paths_are_path_objects(self):
        """All paths should be Path objects."""
        paths = get_policy_paths()
        
        for path in paths.values():
            assert isinstance(path, Path)


class TestGetPolicyPath:
    """Tests for current system policy path."""
    
    def test_returns_path_for_current_system(self):
        """Should return a Path for the current OS."""
        path = get_policy_path()
        
        assert isinstance(path, Path)
        assert "policies.json" in str(path)
    
    @patch("platform.system")
    def test_raises_for_unsupported_os(self, mock_system):
        """Should raise RuntimeError for unsupported OS."""
        mock_system.return_value = "FreeBSD"
        
        with pytest.raises(RuntimeError, match="Unsupported operating system"):
            get_policy_path()


class TestValidatePolicies:
    """Tests for policy validation."""
    
    def test_valid_policies_no_warnings(self):
        """Valid policies should return empty warning list."""
        policies = {
            "BraveAIChatEnabled": False,
            "MetricsReportingEnabled": False,
        }
        
        warnings = validate_policies(policies)
        
        assert warnings == []
    
    def test_warns_on_disabled_component_updates(self):
        """Should warn when ComponentUpdatesEnabled is False."""
        policies = {"ComponentUpdatesEnabled": False}
        
        warnings = validate_policies(policies)
        
        assert len(warnings) == 1
        assert "security updates" in warnings[0]
    
    def test_warns_on_non_dict_input(self):
        """Should warn if policies is not a dict."""
        warnings = validate_policies("not a dict")
        
        assert len(warnings) == 1
        assert "JSON object" in warnings[0]
    
    def test_warns_on_wrong_bool_type(self):
        """Should warn when a boolean policy has wrong type."""
        policies = {"BraveAIChatEnabled": "false"}  # string instead of bool
        
        warnings = validate_policies(policies)
        
        assert len(warnings) == 1
        assert "BraveAIChatEnabled" in warnings[0]
        assert "bool" in warnings[0]
        assert "str" in warnings[0]
    
    def test_warns_on_wrong_int_type(self):
        """Should warn when an integer policy has wrong type."""
        policies = {"SafeBrowsingProtectionLevel": "2"}  # string instead of int
        
        warnings = validate_policies(policies)
        
        assert len(warnings) == 1
        assert "SafeBrowsingProtectionLevel" in warnings[0]
        assert "int" in warnings[0]
    
    def test_warns_on_wrong_string_type(self):
        """Should warn when a string policy has wrong type."""
        policies = {"WebRtcIPHandling": 123}  # int instead of string
        
        warnings = validate_policies(policies)
        
        assert len(warnings) == 1
        assert "WebRtcIPHandling" in warnings[0]
        assert "str" in warnings[0]
    
    def test_warns_on_wrong_list_type(self):
        """Should warn when a list policy has wrong type."""
        policies = {"CookiesSessionOnlyForUrls": "*"}  # string instead of list
        
        warnings = validate_policies(policies)
        
        assert len(warnings) == 1
        assert "CookiesSessionOnlyForUrls" in warnings[0]
        assert "list" in warnings[0]
    
    def test_multiple_type_errors(self):
        """Should return multiple warnings for multiple type errors."""
        policies = {
            "BraveAIChatEnabled": "false",
            "SafeBrowsingProtectionLevel": "2",
        }
        
        warnings = validate_policies(policies)
        
        assert len(warnings) == 2


class TestFindLatestBackup:
    """Tests for backup file discovery."""
    
    def test_returns_none_when_no_backups(self, tmp_path):
        """Should return None when no backups exist."""
        policy_path = tmp_path / "policies.json"
        
        result = find_latest_backup(policy_path)
        
        assert result is None
    
    def test_finds_latest_backup(self, tmp_path):
        """Should return the most recent backup file."""
        policy_path = tmp_path / "policies.json"
        
        # Create some backup files
        backup1 = tmp_path / "policies.backup_20240101_120000"
        backup2 = tmp_path / "policies.backup_20240102_120000"
        backup1.touch()
        backup2.touch()
        
        result = find_latest_backup(policy_path)
        
        # Should find the later one (alphabetically last)
        assert result is not None
        assert "20240102" in str(result)


class TestPoliciesJsonValidity:
    """Tests for the policies.json file."""
    
    def test_policies_json_is_valid(self):
        """policies.json (JSONC) should be valid after stripping comments."""
        policies_path = Path(__file__).parent.parent / "policies.json"
        
        with open(policies_path) as f:
            content = f.read()
        
        # Strip comments before parsing
        clean_json = strip_json_comments(content)
        data = json.loads(clean_json)
        
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_policies_json_has_expected_keys(self):
        """policies.json should contain expected privacy settings."""
        policies_path = Path(__file__).parent.parent / "policies.json"
        
        with open(policies_path) as f:
            content = f.read()
        
        # Strip comments before parsing
        clean_json = strip_json_comments(content)
        data = json.loads(clean_json)
        
        expected_keys = [
            "BraveAIChatEnabled",
            "MetricsReportingEnabled",
            "BlockThirdPartyCookies",
        ]
        
        for key in expected_keys:
            assert key in data, f"Missing expected key: {key}"


class TestStripJsonComments:
    """Tests for JSONC comment stripping."""
    
    def test_strips_single_line_comments(self):
        """Should remove // comments."""
        jsonc = '{"key": "value"} // comment'
        result = strip_json_comments(jsonc)
        assert json.loads(result) == {"key": "value"}
    
    def test_preserves_url_in_string(self):
        """Should not strip // inside strings (URLs)."""
        jsonc = '{"url": "https://example.com"}'
        result = strip_json_comments(jsonc)
        assert json.loads(result) == {"url": "https://example.com"}
    
    def test_strips_multiline_comments(self):
        """Should remove /* */ comments."""
        jsonc = '{"key": /* comment */ "value"}'
        result = strip_json_comments(jsonc)
        assert json.loads(result) == {"key": "value"}

