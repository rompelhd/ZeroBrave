"""Tests for ZeroBrave TUI module."""

import pytest

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui import TUI, CATEGORIES, PROFILES


class TestTUIInitialization:
    """Tests for TUI initialization."""
    
    def test_creates_tui_instance(self):
        """Should create TUI instance without errors."""
        tui = TUI(dry_run=True)
        assert tui is not None
        assert tui.dry_run is True
    
    def test_all_categories_enabled_by_default(self):
        """All categories should be enabled initially."""
        tui = TUI()
        assert all(tui.enabled.values())
        assert len(tui.enabled) == 8
    
    def test_default_profile_is_strict(self):
        """Default profile should be 'strict'."""
        tui = TUI()
        assert tui.current_profile == "strict"
    
    def test_changes_counter_starts_at_zero(self):
        """Changes counter should start at 0."""
        tui = TUI()
        assert tui.changes_made == 0


class TestCategories:
    """Tests for policy categories."""
    
    def test_has_eight_categories(self):
        """Should have exactly 8 categories."""
        assert len(CATEGORIES) == 8
    
    def test_categories_have_correct_structure(self):
        """Each category should have key, tag, name, desc, help, policies."""
        for cat in CATEGORIES:
            assert len(cat) == 6
            key, tag, name, desc, help_text, policies = cat
            assert isinstance(key, str)
            assert isinstance(tag, str)
            assert tag.startswith("[") and tag.endswith("]")
            assert isinstance(name, str)
            assert isinstance(desc, str)
            assert isinstance(help_text, str)
            assert isinstance(policies, dict)
            assert len(policies) > 0
    
    def test_category_keys_are_unique(self):
        """Category keys should be unique."""
        keys = [cat[0] for cat in CATEGORIES]
        assert len(keys) == len(set(keys))


class TestProfiles:
    """Tests for predefined profiles."""
    
    def test_has_three_profiles(self):
        """Should have exactly 3 profiles."""
        assert len(PROFILES) == 3
    
    def test_profile_names(self):
        """Should have strict, balanced, minimal profiles."""
        assert "strict" in PROFILES
        assert "balanced" in PROFILES
        assert "minimal" in PROFILES
    
    def test_strict_has_all_categories(self):
        """Strict profile should include all categories."""
        strict = PROFILES["strict"]
        assert len(strict["categories"]) == 8
    
    def test_minimal_has_fewer_categories(self):
        """Minimal profile should have fewer categories than strict."""
        strict_count = len(PROFILES["strict"]["categories"])
        minimal_count = len(PROFILES["minimal"]["categories"])
        assert minimal_count < strict_count


class TestApplyProfile:
    """Tests for profile application."""
    
    def test_apply_strict_enables_all(self):
        """Applying strict should enable all categories."""
        tui = TUI()
        tui.enabled = {cat[0]: False for cat in CATEGORIES}
        tui.apply_profile("strict")
        assert all(tui.enabled.values())
    
    def test_apply_minimal_enables_subset(self):
        """Applying minimal should enable only a subset."""
        tui = TUI()
        tui.apply_profile("minimal")
        enabled_count = sum(1 for v in tui.enabled.values() if v)
        assert enabled_count == len(PROFILES["minimal"]["categories"])
    
    def test_apply_profile_updates_current_profile(self):
        """Current profile should be updated."""
        tui = TUI()
        tui.apply_profile("balanced")
        assert tui.current_profile == "balanced"
    
    def test_apply_profile_tracks_changes(self):
        """Changes counter should increase when profile changes."""
        tui = TUI()
        tui.apply_profile("minimal")
        assert tui.changes_made > 0


class TestBuildPolicies:
    """Tests for policy building."""
    
    def test_builds_dict_from_enabled(self):
        """Should build a dict of enabled policies."""
        tui = TUI()
        policies = tui.build_policies()
        assert isinstance(policies, dict)
        assert len(policies) > 0
    
    def test_empty_when_all_disabled(self):
        """Should return empty dict when all disabled."""
        tui = TUI()
        tui.enabled = {cat[0]: False for cat in CATEGORIES}
        policies = tui.build_policies()
        assert policies == {}
    
    def test_strict_has_most_policies(self):
        """Strict profile should have the most policies."""
        tui = TUI()
        tui.apply_profile("strict")
        strict_count = len(tui.build_policies())
        
        tui.apply_profile("minimal")
        minimal_count = len(tui.build_policies())
        
        assert strict_count > minimal_count


class TestCountEnabled:
    """Tests for counting enabled policies."""
    
    def test_counts_all_when_strict(self):
        """Should count all categories and policies for strict."""
        tui = TUI()
        tui.apply_profile("strict")
        cats, policies = tui.count_enabled()
        assert cats == 8
        assert policies > 50  # We have 61 policies
    
    def test_counts_zero_when_all_disabled(self):
        """Should return 0 when all disabled."""
        tui = TUI()
        tui.enabled = {cat[0]: False for cat in CATEGORIES}
        cats, policies = tui.count_enabled()
        assert cats == 0
        assert policies == 0


class TestToggle:
    """Tests for toggle functionality."""
    
    def test_toggle_changes_state(self):
        """Toggle should flip the enabled state."""
        tui = TUI()
        initial = tui.enabled["ai"]
        tui.toggle_with_feedback(1)  # AI is category 1
        assert tui.enabled["ai"] != initial
    
    def test_toggle_increments_changes(self):
        """Toggle should increment changes counter."""
        tui = TUI()
        initial_changes = tui.changes_made
        tui.toggle_with_feedback(1)
        assert tui.changes_made == initial_changes + 1
    
    def test_toggle_sets_custom_profile(self):
        """Toggle should set profile to 'custom'."""
        tui = TUI()
        tui.toggle_with_feedback(1)
        assert tui.current_profile == "custom"
