"""CLI behavior tests: global flags, JSON mode, exit codes, confirmation gating."""

import json

import pytest
from typer.testing import CliRunner

from linkcovery.cli import cli_app
from linkcovery.cli.cli_state import state

runner = CliRunner()


def _stdout(result) -> str:
    """Isolated stdout text (click 8.2+ separates stdout from stderr)."""
    return result.stdout


@pytest.fixture(autouse=True)
def _isolated_env(tmp_path, monkeypatch):
    """Point every test at a throwaway home + database."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("LINKCOVERY_DB", str(tmp_path / "links.db"))
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr("typer.testing.CliRunner.env", {"NO_COLOR": "1"}, raising=False)
    # Reset global singletons + flags between tests
    monkeypatch.setattr("linkcovery.core.config._config_manager", None)
    monkeypatch.setattr("linkcovery.services.link_service._link_service", None)
    monkeypatch.setattr("linkcovery.core.database._db_service", None)
    state.json_mode = False
    state.no_color = False
    yield


def _add(url: str = "https://example.com") -> None:
    result = runner.invoke(cli_app, ["add", url, "--no-fetch"])
    assert result.exit_code == 0, result.output


def test_version_flag_prints_version_and_exits_zero():
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert "1.7.8" in _stdout(result)
    assert "██" not in _stdout(result)  # no banner


def test_version_stdout_is_clean():
    result = runner.invoke(cli_app, ["--version"])
    lines = [line for line in _stdout(result).splitlines() if line.strip()]
    assert lines == ["linkcovery 1.7.8"]


def test_help_has_no_banner():
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    assert "██" not in _stdout(result)
    assert "\x1b[" not in _stdout(result)  # no ANSI escapes when piped


def test_help_mentions_global_flags():
    result = runner.invoke(cli_app, ["--help"])
    for flag in ("--json", "--no-color", "--version"):
        assert flag in _stdout(result)


def test_json_list_outputs_valid_json_array():
    _add("https://a.example.com")
    _add("https://b.example.com")
    result = runner.invoke(cli_app, ["--json", "list"])
    assert result.exit_code == 0
    payload = json.loads(_stdout(result))
    assert isinstance(payload, list)
    assert {link["url"] for link in payload} == {"https://a.example.com", "https://b.example.com"}
    for link in payload:
        assert {"id", "url", "domain", "description", "tag", "is_read"} <= set(link)


def test_json_error_stdout_empty_exit_one():
    """show 999 in json mode: rc=1, stdout stays clean (error JSON on stderr)."""
    result = runner.invoke(cli_app, ["--json", "show", "999"])
    assert result.exit_code == 1
    assert _stdout(result) == ""
    stderr = json.loads(result.stderr)
    assert stderr["error"] == "Link with ID 999 not found"
    assert "hint" in stderr


def test_show_missing_link_stderr_and_exit_code():
    result = runner.invoke(cli_app, ["show", "999"])
    assert result.exit_code == 1
    assert _stdout(result) == ""  # stdout clean
    assert "999" in result.stderr
    assert "Hint" in result.stderr


def test_mark_missing_link_exits_one():
    _add()
    result = runner.invoke(cli_app, ["mark", "999"])
    assert result.exit_code == 1


def test_mark_partial_failure_still_processes_rest():
    _add("https://ok.example.com")
    result = runner.invoke(cli_app, ["mark", "999", "1"])
    assert result.exit_code == 1  # one item failed


def test_mark_all_success_exits_zero():
    _add("https://one.example.com")
    _add("https://two.example.com")
    result = runner.invoke(cli_app, ["mark", "1", "2"])
    assert result.exit_code == 0


def test_search_without_query_or_filters_exits_one():
    _add()
    result = runner.invoke(cli_app, ["search"])
    assert result.exit_code == 1


def test_search_with_tag_only_works():
    _add()
    result = runner.invoke(cli_app, ["search", "--tag", "python"])
    assert result.exit_code == 0


def test_normalize_all_requires_confirmation():
    _add("https://www.example.com")
    result = runner.invoke(cli_app, ["normalize", "--all"], input="n\n")
    assert result.exit_code == 0
    # no mutation: url untouched
    listing = runner.invoke(cli_app, ["--json", "list"])
    payload = json.loads(_stdout(listing))
    assert payload[0]["url"] == "https://www.example.com"


def test_normalize_all_with_yes_flag_mutates():
    _add("http://www.example.com/")
    result = runner.invoke(cli_app, ["normalize", "--all", "-y"])
    assert result.exit_code == 0
    listing = runner.invoke(cli_app, ["--json", "list"])
    payload = json.loads(_stdout(listing))
    # www stripped, trailing slash removed (scheme is preserved, not upgraded)
    assert payload[0]["url"] == "http://example.com"


def test_normalize_specific_missing_link_exits_one():
    _add()
    result = runner.invoke(cli_app, ["normalize", "999"])
    assert result.exit_code == 1


def test_normalize_no_args_exits_one():
    result = runner.invoke(cli_app, ["normalize"])
    assert result.exit_code == 1


def test_hidden_aliases_still_work():
    _add("https://alias.example.com")
    assert runner.invoke(cli_app, ["ls"]).exit_code == 0
    assert runner.invoke(cli_app, ["find", "alias"]).exit_code == 0
    assert runner.invoke(cli_app, ["new", "https://new.example.com", "--no-fetch"]).exit_code == 0
    assert runner.invoke(cli_app, ["rm", "1", "-f"]).exit_code == 0


def test_random_reads_and_marks():
    _add("https://random.example.com")
    result = runner.invoke(cli_app, ["random", "--number", "1"])
    assert result.exit_code == 0
    help_result = runner.invoke(cli_app, ["--help"])
    assert "read-random" not in _stdout(help_result)
    assert "random" in _stdout(help_result)


def test_open_opens_links(monkeypatch):
    monkeypatch.setattr("webbrowser.open", lambda url: True)
    _add()
    assert runner.invoke(cli_app, ["open", "1"]).exit_code == 0


def test_import_chrome_flag_exists():
    result = runner.invoke(cli_app, ["import", "--help"])
    assert result.exit_code == 0
    assert "--chrome" in _stdout(result)


def test_export_format_md_and_html(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _add()
    assert runner.invoke(cli_app, ["export", "out.md"]).exit_code == 0
    assert runner.invoke(cli_app, ["export", "out.html"]).exit_code == 0
    assert (tmp_path / "out.md").exists()
    assert (tmp_path / "out.html").exists()


def test_help_resolves_topics():
    assert runner.invoke(cli_app, ["help"]).exit_code == 0
    assert "Usage" in _stdout(runner.invoke(cli_app, ["help", "list"]))
    assert "Usage" in _stdout(runner.invoke(cli_app, ["help", "config", "show"]))
    bad = runner.invoke(cli_app, ["help", "nope"])
    assert bad.exit_code == 1
    assert "nope" in bad.stderr


def test_chrome_bookmarks_json_imports(tmp_path):
    import json as _json

    raw = {"roots": {"bookmark_bar": {"children": [{"type": "url", "url": "https://c.example.com"}]}}}
    f = tmp_path / "Bookmarks"
    f.write_text(_json.dumps(raw))
    assert runner.invoke(cli_app, ["import", str(f), "-y"]).exit_code == 0
    assert _listing()[0]["url"] == "https://c.example.com"


def test_delete_accepts_yes_flag():
    _add()
    result = runner.invoke(cli_app, ["delete", "1", "-y"])
    assert result.exit_code == 0


def test_confirm_interrupt_propagates(monkeypatch):
    """Ctrl-C inside confirm must raise, not silently return False."""

    def raise_interrupt(message, default=False):
        raise KeyboardInterrupt

    monkeypatch.setattr("rich.prompt.Confirm.ask", staticmethod(raise_interrupt))
    _add()
    result = runner.invoke(cli_app, ["delete", "1"])
    assert result.exit_code == 130


def test_env_db_overrides_config_file(tmp_path, monkeypatch):
    """Precedence: LINKCOVERY_DB env > config-file database_path."""
    from linkcovery.core.config import ConfigManager

    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr("linkcovery.core.config._config_manager", None)

    manager = ConfigManager()
    manager.set("database_path", str(tmp_path / "ignored.db"))

    env_db = tmp_path / "env-links.db"
    monkeypatch.setenv("LINKCOVERY_DB", str(env_db))

    assert manager.config.get_database_path() == str(env_db)
    assert manager.config.database_path_source() == "env"
    assert manager.value_source("database_path") == "env"


def test_config_show_json_has_sources():
    result = runner.invoke(cli_app, ["--json", "config", "show"])
    assert result.exit_code == 0
    payload = json.loads(_stdout(result))
    assert "app_name" in payload
    assert payload["app_name"]["source"] in ("env", "file", "default")


def test_import_missing_file_exits_one():
    result = runner.invoke(cli_app, ["import", "/nonexistent.json"])
    assert result.exit_code == 1


def test_no_color_flag_accepted():
    _add()
    result = runner.invoke(cli_app, ["--no-color", "list"])
    assert result.exit_code == 0


def _stub_fetch(monkeypatch, description: str = "Stubbed description") -> None:
    """Replace the CLI-module fetch_description with a network-free stub."""

    async def fake(url: str, timeout: int = 10, show_spinner: bool = True) -> str:
        return description

    monkeypatch.setattr("linkcovery.cli.links.fetch_description", fake)


def _listing() -> list[dict]:
    result = runner.invoke(cli_app, ["--json", "list"])
    return json.loads(_stdout(result))


def test_describe_fills_missing_only(monkeypatch):
    _add("https://a.example.com")
    _add("https://b.example.com")
    runner.invoke(cli_app, ["edit", "1", "--desc", "Existing description"])
    _stub_fetch(monkeypatch)
    result = runner.invoke(cli_app, ["describe"])
    assert result.exit_code == 0
    payload = {link["id"]: link["description"] for link in _listing()}
    assert payload[1] == "Existing description"
    assert payload[2] == "Stubbed description"


def test_describe_all_requires_confirmation(monkeypatch):
    _add("https://www.example.com")
    result = runner.invoke(cli_app, ["describe", "--all"], input="n\n")
    assert result.exit_code == 0
    assert _listing()[0]["description"] == ""


def test_describe_all_with_yes_overwrites(monkeypatch):
    _add("https://www.example.com")
    runner.invoke(cli_app, ["edit", "1", "--desc", "Old description"])
    _stub_fetch(monkeypatch)
    result = runner.invoke(cli_app, ["describe", "--all", "-y"])
    assert result.exit_code == 0
    assert _listing()[0]["description"] == "Stubbed description"


def test_describe_specific_ids(monkeypatch):
    _add("https://a.example.com")
    _add("https://b.example.com")
    _stub_fetch(monkeypatch)
    result = runner.invoke(cli_app, ["describe", "1", "2"])
    assert result.exit_code == 0
    payload = {link["id"]: link["description"] for link in _listing()}
    assert payload[1] == "Stubbed description"
    assert payload[2] == "Stubbed description"


def test_describe_missing_id_fails():
    _add()
    result = runner.invoke(cli_app, ["describe", "999"])
    assert result.exit_code == 1


def test_describe_no_candidates_succeeds():
    _add("https://a.example.com")
    runner.invoke(cli_app, ["edit", "1", "--desc", "Existing description"])
    result = runner.invoke(cli_app, ["describe"])
    assert result.exit_code == 0




def test_describe_empty_fetch_result_skipped(monkeypatch):
    _add("https://a.example.com")
    runner.invoke(cli_app, ["edit", "1", "--desc", "Keep me"])
    _add("https://b.example.com")
    _stub_fetch(monkeypatch, description="")
    result = runner.invoke(cli_app, ["describe"])
    assert result.exit_code == 0
    payload = {link["id"]: link["description"] for link in _listing()}
    assert payload[1] == "Keep me"
    assert payload[2] == ""
