from pathlib import Path
import json

import functools

import typer

APP_NAME = "Suketan"


# --prepare application data directory--
if not Path(typer.get_app_dir(APP_NAME)).exists():
    Path(typer.get_app_dir(APP_NAME)).mkdir(parents=False, exist_ok=True)
# ----


# --prepare config--
config = {
    "schedule_patterns_dir": Path(typer.get_app_dir(APP_NAME)).as_posix(),
    "schedule_patterns_filename": "schedule_patterns.json",
    "language": "ja",  # デフォルトは日本語
}


def save_config():
    with open(Path(typer.get_app_dir(APP_NAME)) / "config.json", "w") as f:
        json.dump(config, f, indent=4)


def load_config():
    with open(Path(typer.get_app_dir(APP_NAME)) / "config.json", "r") as f:
        config.update(json.load(f))


if not (Path(typer.get_app_dir(APP_NAME)) / "config.json").exists():
    save_config()
load_config()
# ----


# ローカライズメッセージ取得関数
@functools.lru_cache()
def get_locale_messages():
    lang = config.get("language", "ja")
    path = Path(__file__).parent / "locale" / f"locale_{lang}.json"
    if not path.exists():
        raise FileNotFoundError(f"Locale file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


msg = get_locale_messages()
app = typer.Typer(help=msg["app_help"])
pattern_app = typer.Typer(help=msg["pattern_help"])
task_app = typer.Typer(help=msg["task_help"])
app.add_typer(pattern_app, name="pattern")
app.add_typer(task_app, name="task")


class SchedulePatternManager:
    def __init__(self, data: dict | None = None):
        # data: {"current_pattern": str, "patterns": {pattern_name: {task_name: duration, ...}, ...}}
        if data is None:
            self.current_pattern = None
            self.patterns = {}
        else:
            self.current_pattern = data.get("current_pattern")
            self.patterns = data.get("patterns", {})

    def to_dict(self) -> dict:
        return {
            "current_pattern": self.current_pattern,
            "patterns": self.patterns,
        }

    def create_pattern(self, name: str):
        msg = get_locale_messages()
        if name in self.patterns:
            typer.echo(msg["pattern_already_exists"].format(name=name))
            return
        self.patterns[name] = {}
        self.current_pattern = name
        typer.echo(msg["created_pattern"].format(name=name))

    def list_patterns(self):
        msg = get_locale_messages()
        if not self.patterns:
            typer.echo(msg["no_patterns"])
            return
        typer.echo(msg["schedule_patterns"])
        for name in self.patterns.keys():
            typer.echo(f" - {name}")

    def delete_pattern(self, name: str):
        msg = get_locale_messages()
        if name not in self.patterns:
            typer.echo(msg["pattern_not_found"].format(name=name))
            return
        del self.patterns[name]
        if self.current_pattern == name:
            self.current_pattern = None
        typer.echo(msg["deleted_pattern"].format(name=name))
        typer.echo(msg["using_pattern"].format(name=name))

    def use_pattern(self, name: str):
        msg = get_locale_messages()
        if name not in self.patterns:
            typer.echo(msg["pattern_not_found"].format(name=name))
            return
        self.current_pattern = name
        typer.echo(msg["using_pattern"].format(name=name))
        typer.echo(msg["schedule_pattern"].format(name=name))

    def show_pattern(self, name: str | None = None):
        msg = get_locale_messages()
        if name is None:
            name = self.current_pattern
        if not name or name not in self.patterns:
            typer.echo(msg["no_pattern_set"])
            return
        typer.echo(msg["schedule_pattern"].format(name=name))
        tasks = self.patterns[name]
        total_minutes = 0
        for task, duration in tasks.items():
            typer.echo(f"  {task}: {duration}")
            total_minutes += self._parse_duration(duration)
        free_minutes = 24 * 60 - total_minutes
        h, m = divmod(free_minutes, 60)
        typer.echo(msg["free_time"].format(h=h, m=m))

    def add_task(self, task_name: str, duration: str):
        msg = get_locale_messages()
        if not self.current_pattern or self.current_pattern not in self.patterns:
            typer.echo(msg["no_pattern_set"])
            return
        self.patterns[self.current_pattern][task_name] = duration
        typer.echo(
            msg["added_task"].format(
                task=task_name, duration=duration, pattern=self.current_pattern
            )
        )

    def remove_task(self, task_name: str):
        msg = get_locale_messages()
        if not self.current_pattern or self.current_pattern not in self.patterns:
            typer.echo(msg["no_pattern_set"])
            return
        if task_name not in self.patterns[self.current_pattern]:
            typer.echo(
                msg["task_not_found"].format(
                    task=task_name, pattern=self.current_pattern
                )
            )
            return
        del self.patterns[self.current_pattern][task_name]
        typer.echo(
            msg["removed_task"].format(task=task_name, pattern=self.current_pattern)
        )

    def list_tasks(self):
        msg = get_locale_messages()
        if not self.current_pattern or self.current_pattern not in self.patterns:
            typer.echo(msg["no_pattern_set"])
            return
        tasks = self.patterns[self.current_pattern]
        if not tasks:
            typer.echo(msg["no_tasks"])
            return
        typer.echo(msg["tasks_in_pattern"].format(pattern=self.current_pattern))
        total_minutes = 0
        for name, duration in tasks.items():
            typer.echo(f" - {name}: {duration}")
            total_minutes += self._parse_duration(duration)
        free_minutes = 24 * 60 - total_minutes
        h, m = divmod(free_minutes, 60)
        typer.echo(msg["free_time"].format(h=h, m=m))

    @staticmethod
    def _parse_duration(duration: str) -> int:
        """
        "2:30"→150, "45"→45, "1h20m"→80 のように`時間:分`表記を`分`に変換
        """
        import re

        duration = duration.strip()
        if re.match(r"^\d+$", duration):
            return int(duration)
        if re.match(r"^\d{1,2}:\d{2}$", duration):
            h, m = map(int, duration.split(":"))
            return h * 60 + m
        m = re.match(r"^(?:(\d+)h)?(?:(\d+)m)?$", duration)
        if m:
            h = int(m.group(1) or 0)
            mi = int(m.group(2) or 0)
            return h * 60 + mi
        return 0


def save_manager_data(manager: SchedulePatternManager):
    with open(
        Path(config["schedule_patterns_dir"]) / config["schedule_patterns_filename"],
        "w",
    ) as f:
        json.dump(manager.to_dict(), f, ensure_ascii=False, indent=2)


def load_manager_data() -> dict:
    path = Path(config["schedule_patterns_dir"]) / config["schedule_patterns_filename"]
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


manager = SchedulePatternManager(load_manager_data())


@pattern_app.command("create", help=msg["pattern_create_help"])
def create_pattern(
    name: str = typer.Argument(..., help=msg["pattern_create_arg_name_help"]),
):
    manager.create_pattern(name)
    save_manager_data(manager)


@pattern_app.command("list", help=msg["pattern_list_help"])
def list_patterns():
    manager.list_patterns()


@pattern_app.command("delete", help=msg["pattern_delete_help"])
def delete_pattern(
    name: str = typer.Argument(..., help=msg["pattern_delete_arg_name_help"]),
):
    manager.delete_pattern(name)
    save_manager_data(manager)


@app.command("use", help=msg["use_help"])
def use_pattern(name: str = typer.Argument(..., help=msg["use_arg_name_help"])):
    manager.use_pattern(name)
    config["current_pattern"] = name


@app.command("show", help=msg["show_help"])
def show_pattern(name: str = typer.Argument(None, help=msg["show_arg_name_help"])):
    manager.show_pattern(name)


@task_app.command("add", help=msg["task_add_help"])
def add_task(
    name: str = typer.Argument(..., help=msg["task_add_arg_name_help"]),
    time: str = typer.Argument(..., help=msg["task_add_arg_time_help"]),
):
    manager.add_task(name, time)
    save_manager_data(manager)


@task_app.command("remove", help=msg["task_remove_help"])
def remove_task(name: str = typer.Argument(..., help=msg["task_remove_arg_name_help"])):
    manager.remove_task(name)
    save_manager_data(manager)


@task_app.command("list", help=msg["task_list_help"])
def list_tasks():
    manager.list_tasks()


def main():
    app()


if __name__ == "__main__":
    main()
