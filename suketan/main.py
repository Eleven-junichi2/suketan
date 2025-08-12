from pathlib import Path

import typer

APP_NAME = "Suketan"

app = typer.Typer()
pattern_app = typer.Typer()
task_app = typer.Typer()
app.add_typer(pattern_app, name="pattern")
app.add_typer(task_app, name="task")

current_pattern = None
schedule_patterns: dict[str, dict[str, str]] = {}

schedule_patterns_path = Path(typer.get_app_dir(APP_NAME)) / "schedule_patterns.json"
# print(f"Schedule patterns will be stored in: {schedule_pattern_data_path}")


@pattern_app.command("create")
def create_pattern(name: str):
    global current_pattern
    if current_pattern is None:
        current_pattern = name
    schedule_patterns[name] = {}
    typer.echo(f"Creating a schedule pattern: {name}")

@pattern_app.command("list")
def list_patterns():
    for name in schedule_patterns.keys():
        typer.echo(f"- {name}")

@pattern_app.command("delete")
def delete_pattern(name: str):
    global current_pattern
    if current_pattern == name:
        current_pattern = None
    schedule_patterns.pop(name, None)
    typer.echo(f"Deleted schedule pattern: {name}")

@app.command("use")
def use_pattern(name: str):
    global current_pattern
    current_pattern = name
    typer.echo(f"Using schedule pattern: {name}")

@app.command("show")
def show_pattern(name: str = typer.Argument(None)):
    if name is None:
        if current_pattern:
            typer.echo(f"Current schedule pattern: {current_pattern}")
        else:
            typer.echo("No schedule pattern is currently set.")
    else:
        data = schedule_patterns.get(name)
        if data:
            typer.echo(f"Schedule pattern '{name}':")
            for key, value in data.items():
                typer.echo(f"  {key}: {value}")
        else:
            typer.echo(f"Schedule pattern not found: {name}")

@task_app.command("add")
def add_task(name: str, time: str):
    global current_pattern
    if current_pattern is None:
        typer.echo("No schedule pattern is currently set.")
        return
    schedule_patterns[current_pattern][name] = time
    typer.echo(f"Adding task '{name}' to schedule pattern: {current_pattern}")

@task_app.command("remove")
def remove_task(name: str):
    global current_pattern
    if current_pattern is None:
        typer.echo("No schedule pattern is currently set.")
        return
    if name in schedule_patterns[current_pattern]:
        del schedule_patterns[current_pattern][name]
        typer.echo(f"Removing task '{name}' from schedule pattern: {current_pattern}")
    else:
        typer.echo(f"Task '{name}' not found in schedule pattern: {current_pattern}")

@task_app.command("list")
def list_tasks():
    global current_pattern
    if current_pattern is None:
        typer.echo("No schedule pattern is currently set.")
        return
    tasks = schedule_patterns.get(current_pattern, {})
    if not tasks:
        typer.echo(f"No tasks found in schedule pattern: {current_pattern}")
    for name, time in tasks.items():
        typer.echo(f"  {name}: {time}")

def main():
    app()


if __name__ == "__main__":
    main()
