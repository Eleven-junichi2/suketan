# TODO: スケジュールパターンデータの保存・読み込みのタイミングを、SchedulePatternManagerクラスではなく、コマンド実行部分の処理に移動する（テストの実装をしやすくするため）
from pathlib import Path
import json

import typer

APP_NAME = "Suketan"

app = typer.Typer()
pattern_app = typer.Typer()
task_app = typer.Typer()
app.add_typer(pattern_app, name="pattern")
app.add_typer(task_app, name="task")

# --prepare application data directory--
if not Path(typer.get_app_dir(APP_NAME)).exists():
    Path(typer.get_app_dir(APP_NAME)).mkdir(parents=False, exist_ok=True)
# ----

# --prepare config--
config = {
    "schedule_patterns_dir": Path(typer.get_app_dir(APP_NAME)),
    "schedule_patterns_filename": "schedule_patterns.json",
}
if not (Path(typer.get_app_dir(APP_NAME)) / "config.json").exists():
    with open(Path(typer.get_app_dir(APP_NAME)) / "config.json", "w") as f:
        json.dump(config, f)
with open(Path(typer.get_app_dir(APP_NAME)) / "config.json", "r") as f:
    config.update(json.load(f))
# ----


class SchedulePatternManager:
    def __init__(self):
        self.current_pattern = None
        self._schedule_patterns: dict[str, dict[str, str]] = {}

    @property
    def schedule_patterns(self):
        return self._schedule_patterns

    @schedule_patterns.setter
    def schedule_patterns(self, value: dict[str, dict[str, str]]):
        self._schedule_patterns = value

    def create_pattern(self, name: str):
        if self.current_pattern is None:
            self.current_pattern = name
        self.schedule_patterns[name] = {}
        typer.echo(f"Creating a schedule pattern: {name}")

    def list_patterns(self):
        if not self.schedule_patterns:
            typer.echo("No schedule patterns found.")
            return
        typer.echo("Schedule patterns:")
        for name in self.schedule_patterns.keys():
            typer.echo(f" - {name}")

    def delete_pattern(self, name: str):
        if name not in self.schedule_patterns:
            typer.echo(f"Schedule pattern not found: {name}")
            return
        del self.schedule_patterns[name]
        typer.echo(f"Deleted schedule pattern: {name}")

    def use_pattern(self, name: str):
        if name not in self.schedule_patterns:
            typer.echo(f"Schedule pattern not found: {name}")
            return
        self.current_pattern = name
        typer.echo(f"Using schedule pattern: {name}")

    def show_pattern(self, name: str | None = None):
        if name is None:
            if self.current_pattern:
                typer.echo(f"Current schedule pattern: {self.current_pattern}")
            else:
                typer.echo("No schedule pattern is currently set.")
        else:
            data = self.schedule_patterns.get(name)
            if data:
                typer.echo(f"Schedule pattern '{name}':")
                for key, value in data.items():
                    typer.echo(f"  {key}: {value}")
            else:
                typer.echo(f"Schedule pattern not found: {name}")

    def add_task(self, name: str, time: str):
        if self.current_pattern is None:
            typer.echo("No schedule pattern is currently set.")
            return
        self.schedule_patterns[self.current_pattern][name] = time
        typer.echo(f"Adding task '{name}' to schedule pattern: {self.current_pattern}")

    def remove_task(self, name: str):
        if self.current_pattern is None:
            typer.echo("No schedule pattern is currently set.")
            return
        if name in self.schedule_patterns[self.current_pattern]:
            del self.schedule_patterns[self.current_pattern][name]
            typer.echo(
                f"Removing task '{name}' from schedule pattern: {self.current_pattern}"
            )
        else:
            typer.echo(
                f"Task '{name}' not found in schedule pattern: {self.current_pattern}"
            )

    def list_tasks(self):
        if self.current_pattern is None:
            typer.echo("No schedule pattern is currently set.")
            return
        tasks = self.schedule_patterns[self.current_pattern]
        if not tasks:
            typer.echo("No tasks found in schedule pattern.")
            return
        typer.echo("Tasks in schedule pattern:")
        for name, time in tasks.items():
            typer.echo(f" - {name}: {time}")

    # def load_data(self):
    #     if config["schedule_patterns_dir"].exists():
    #         with open(
    #             config["schedule_patterns_dir"] / config["schedule_patterns_filename"],
    #             "r",
    #         ) as f:
    #             self.schedule_patterns = json.load(f)
    #             # typer.echo("Loaded schedule patterns from file.")


def save_schedule_patterns(schedule_patterns: dict[str, dict[str, str]]):
    with open(
        config["schedule_patterns_dir"] / config["schedule_patterns_filename"], "w"
    ) as f:
        json.dump(schedule_patterns, f)
        # typer.echo("Saved schedule patterns to file.")


manager = SchedulePatternManager()
# manager.load_data()


@pattern_app.command("create")
def create_pattern(name: str):
    manager.create_pattern(name)


@pattern_app.command("list")
def list_patterns():
    manager.list_patterns()


@pattern_app.command("delete")
def delete_pattern(name: str):
    manager.delete_pattern(name)


@app.command("use")
def use_pattern(name: str):
    manager.use_pattern(name)


@app.command("show")
def show_pattern(name: str = typer.Argument(None)):
    manager.show_pattern(name)


@task_app.command("add")
def add_task(name: str, time: str):
    manager.add_task(name, time)


@task_app.command("remove")
def remove_task(name: str):
    manager.remove_task(name)


@task_app.command("list")
def list_tasks():
    manager.list_tasks()


def main():
    app()


if __name__ == "__main__":
    main()
