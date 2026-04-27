"""Tests for the --verbose CLI flag."""

import logging
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from hyperextract.cli.cli import app

runner = CliRunner()


class TestVerboseFlag:
    """Test that --verbose enables logging."""

    def test_verbose_flag_shows_in_help(self):
        """--verbose appears in top-level help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.output

    def test_verbose_flag_default_false(self):
        """Without --verbose, logging stays at WARNING level (default)."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # No log output should appear in help mode
        assert result.output.count("INFO") == 0

    def test_verbose_flag_with_version(self):
        """--verbose combined with --version exits cleanly."""
        result = runner.invoke(app, ["--verbose", "--version"])
        assert result.exit_code == 0
        assert "Hyper-Extract CLI" in result.output

    def test_verbose_sets_debug_log_level(self):
        """When --verbose is passed, root logger level is set to DEBUG."""
        result = runner.invoke(app, ["--verbose", "--version"])
        assert result.exit_code == 0
        root_logger = logging.getLogger()
        # After --verbose, the root logger should be at DEBUG level
        assert root_logger.level == logging.DEBUG

    def test_verbose_before_subcommand(self):
        """--verbose works when placed before a subcommand: he --verbose info --help."""
        result = runner.invoke(app, ["--verbose", "info", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_parse_help(self):
        """he --verbose parse --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "parse", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_search_help(self):
        """he --verbose search --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "search", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_talk_help(self):
        """he --verbose talk --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "talk", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_feed_help(self):
        """he --verbose feed --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "feed", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_build_index_help(self):
        """he --verbose build-index --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "build-index", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_show_help(self):
        """he --verbose show --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "show", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_list_template_help(self):
        """he --verbose list template --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "list", "template", "--help"])
        assert result.exit_code == 0

    def test_verbose_before_config_help(self):
        """he --verbose config --help exits cleanly."""
        result = runner.invoke(app, ["--verbose", "config", "--help"])
        assert result.exit_code == 0

    def test_verbose_info_missing_ka_exits_with_error(self):
        """he --verbose info <nonexistent> exits with error (verbose logging enabled)."""
        result = runner.invoke(app, ["--verbose", "info", "/nonexistent/path"])
        # Should exit with error code (path doesn't exist)
        assert result.exit_code != 0
