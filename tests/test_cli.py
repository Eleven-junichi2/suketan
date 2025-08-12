from typer.testing import CliRunner
from suketan.main import app

runner = CliRunner()




def test_pattern_create_and_list(tmp_path):
    import suketan.main as main_mod
    main_mod.config["schedule_patterns_dir"] = tmp_path
    main_mod.config["schedule_patterns_filename"] = "schedule_patterns.json"

    result = runner.invoke(app, ["pattern", "create", "testpat"])
    assert result.exit_code == 0
    assert "作成しました" in result.output

    result = runner.invoke(app, ["pattern", "list"])
    assert result.exit_code == 0
    assert "testpat" in result.output

    # アクティブ切り替え
    result = runner.invoke(app, ["use", "testpat"])
    assert result.exit_code == 0
    assert "切り替えました" in result.output

    # タスク追加
    result = runner.invoke(app, ["task", "add", "仕事", "120"])
    assert result.exit_code == 0
    assert "追加しました" in result.output

    # タスク一覧と可処分時間
    result = runner.invoke(app, ["task", "list"])
    assert result.exit_code == 0
    assert "仕事" in result.output
    assert "可処分時間" in result.output

    # タスク削除
    result = runner.invoke(app, ["task", "remove", "仕事"])
    assert result.exit_code == 0
    assert "削除しました" in result.output

    # パターン削除
    result = runner.invoke(app, ["pattern", "delete", "testpat"])
    assert result.exit_code == 0
    assert "削除しました" in result.output
