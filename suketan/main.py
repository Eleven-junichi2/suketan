import typer
import json
import os

app = typer.Typer()
pattern_app = typer.Typer()
task_app = typer.Typer()
app.add_typer(pattern_app, name="pattern")
app.add_typer(task_app, name="task")

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")
DEFAULT_DAY_MINUTES = 24 * 60


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"patterns": {}, "active": None}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_active_pattern(data):
    active = data.get("active")
    if not active:
        typer.echo(
            "アクティブなパターンがありません。'use [パターン名]'で切り替えてください。"
        )
        raise typer.Exit()
    return active


# パターン操作
@pattern_app.command("create")
def create_pattern(name: str):
    """新しいスケジュールパターンを作成"""
    data = load_data()
    if name in data["patterns"]:
        typer.echo(f"パターン '{name}' は既に存在します。")
        raise typer.Exit()
    data["patterns"][name] = {"tasks": []}
    save_data(data)
    typer.echo(f"パターン '{name}' を作成しました。")


@pattern_app.command("list")
def list_patterns():
    """登録されているパターン一覧を表示"""
    data = load_data()
    for name in data["patterns"]:
        active = "(アクティブ)" if data.get("active") == name else ""
        typer.echo(f"- {name} {active}")
    if not data["patterns"]:
        typer.echo("パターンがありません。")


@pattern_app.command("delete")
def delete_pattern(name: str):
    """指定したパターンを削除"""
    data = load_data()
    if name not in data["patterns"]:
        typer.echo(f"パターン '{name}' は存在しません。")
        raise typer.Exit()
    del data["patterns"][name]
    if data.get("active") == name:
        data["active"] = None
    save_data(data)
    typer.echo(f"パターン '{name}' を削除しました。")


# パターン切り替え
@app.command("use")
def use_pattern(name: str):
    """操作対象のパターンを切り替える"""
    data = load_data()
    if name not in data["patterns"]:
        typer.echo(f"パターン '{name}' は存在しません。")
        raise typer.Exit()
    data["active"] = name
    save_data(data)
    typer.echo(f"アクティブパターンを '{name}' に切り替えました。")


# タスク操作
@task_app.command("add")
def add_task(name: str, minutes: int):
    """アクティブなパターンにタスクを追加"""
    data = load_data()
    active = get_active_pattern(data)
    pattern = data["patterns"][active]
    pattern["tasks"].append({"name": name, "minutes": minutes})
    save_data(data)
    typer.echo(f"タスク '{name}' ({minutes}分) を追加しました。")


@task_app.command("list")
def list_tasks():
    """アクティブなパターンのタスク一覧と可処分時間を表示"""
    data = load_data()
    active = get_active_pattern(data)
    pattern = data["patterns"][active]
    total = sum(t["minutes"] for t in pattern["tasks"])
    for t in pattern["tasks"]:
        typer.echo(f"- {t['name']} ({t['minutes']}分)")
    free = DEFAULT_DAY_MINUTES - total
    typer.echo(f"\n可処分時間: {free}分")


@task_app.command("remove")
def remove_task(name: str):
    """アクティブなパターンからタスクを削除"""
    data = load_data()
    active = get_active_pattern(data)
    pattern = data["patterns"][active]
    before = len(pattern["tasks"])
    pattern["tasks"] = [t for t in pattern["tasks"] if t["name"] != name]
    after = len(pattern["tasks"])
    save_data(data)
    if before == after:
        typer.echo(f"タスク '{name}' は見つかりませんでした。")
    else:
        typer.echo(f"タスク '{name}' を削除しました。")


if __name__ == "__main__":
    app()
