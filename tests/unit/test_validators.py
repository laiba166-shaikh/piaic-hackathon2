"""Unit tests for validation functions"""
import pytest


class TestParseTagsFunction:
    """Unit tests for parse_tags() function (US6-005)"""

    def test_parse_tags_comma_separated(self) -> None:
        """Test parse_tags with simple comma-separated tags"""
        from src.core.validators import parse_tags

        result = parse_tags("work,urgent,personal")

        assert result == ["work", "urgent", "personal"]

    def test_parse_tags_with_spaces(self) -> None:
        """Test parse_tags trims spaces around tags"""
        from src.core.validators import parse_tags

        result = parse_tags("work, urgent , personal")

        assert result == ["work", "urgent", "personal"]

    def test_parse_tags_with_multiword_tags(self) -> None:
        """Test parse_tags handles multi-word tags with quotes (FR-016)"""
        from src.core.validators import parse_tags

        # Multi-word tags without special quoting (simple space handling)
        result = parse_tags("work,high priority,meeting")

        # Should split by comma and trim spaces
        assert result == ["work", "high priority", "meeting"]

    def test_parse_tags_empty_string(self) -> None:
        """Test parse_tags with empty string returns empty list"""
        from src.core.validators import parse_tags

        result = parse_tags("")

        assert result == []

    def test_parse_tags_single_tag(self) -> None:
        """Test parse_tags with single tag"""
        from src.core.validators import parse_tags

        result = parse_tags("work")

        assert result == ["work"]

    def test_parse_tags_removes_empty_tags(self) -> None:
        """Test parse_tags removes empty tags from result"""
        from src.core.validators import parse_tags

        result = parse_tags("work,,urgent,  ,personal")

        # Should skip empty strings and whitespace-only strings
        assert result == ["work", "urgent", "personal"]

    def test_parse_tags_strips_whitespace(self) -> None:
        """Test parse_tags strips leading/trailing whitespace from each tag"""
        from src.core.validators import parse_tags

        result = parse_tags("  work  ,  urgent  ,  personal  ")

        assert result == ["work", "urgent", "personal"]
