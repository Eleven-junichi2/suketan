import pytest
from suketan.main import SchedulePatternManager


@pytest.fixture
def manager():
    return SchedulePatternManager()


def test_create_pattern(manager):
    manager.create_pattern("pattern1")
    assert "pattern1" in manager.patterns
    assert manager.current_pattern == "pattern1"


def test_list_patterns_empty(manager):
    manager.list_patterns()
    assert manager.patterns == {}


def test_list_patterns_nonempty(manager):
    manager.create_pattern("pattern1")
    manager.create_pattern("pattern2")
    manager.list_patterns()
    assert set(manager.patterns.keys()) == {"pattern1", "pattern2"}


def test_delete_pattern(manager):
    manager.create_pattern("pattern1")
    manager.delete_pattern("pattern1")
    assert "pattern1" not in manager.patterns


def test_delete_pattern_not_found(manager):
    # 存在しないパターン削除してもエラーにならないことを確認
    before = dict(manager.patterns)
    manager.delete_pattern("notfound")
    assert manager.patterns == before


def test_use_pattern(manager):
    manager.create_pattern("pattern1")
    manager.use_pattern("pattern1")
    assert manager.current_pattern == "pattern1"


def test_use_pattern_not_found(manager):
    manager.create_pattern("pattern1")
    before = manager.current_pattern
    manager.use_pattern("notfound")
    # current_patternは変化しない
    assert manager.current_pattern == before


def test_show_pattern_current(manager):
    manager.create_pattern("pattern1")
    manager.add_task("task1", "1:00")
    manager.show_pattern()
    assert manager.patterns["pattern1"]["task1"] == "1:00"


def test_show_pattern_none(manager):
    # current_patternがNoneのときshow_patternしてもエラーにならない
    manager.show_pattern()
    assert manager.current_pattern is None


def test_show_pattern_by_name(manager):
    manager.create_pattern("pattern1")
    manager.add_task("task1", "2:30")
    manager.show_pattern("pattern1")
    assert manager.patterns["pattern1"]["task1"] == "2:30"


def test_show_pattern_not_found(manager):
    # 存在しないパターン名を指定してもエラーにならない
    before = dict(manager.patterns)
    manager.show_pattern("notfound")
    assert manager.patterns == before


def test_add_task(manager):
    manager.create_pattern("pattern1")
    manager.add_task("task1", "10:00")
    assert manager.patterns["pattern1"]["task1"] == "10:00"


def test_add_task_no_pattern(manager):
    # current_patternがNoneのときadd_taskしてもエラーにならない
    before = dict(manager.patterns)
    manager.add_task("task1", "10:00")
    assert manager.patterns == before


def test_remove_task(manager):
    manager.create_pattern("pattern1")
    manager.add_task("task1", "10:00")
    manager.remove_task("task1")
    assert "task1" not in manager.patterns["pattern1"]


def test_remove_task_not_found(manager):
    manager.create_pattern("pattern1")
    before = dict(manager.patterns["pattern1"])
    manager.remove_task("notfound")
    assert manager.patterns["pattern1"] == before


def test_remove_task_no_pattern(manager):
    # current_patternがNoneのときremove_taskしてもエラーにならない
    before = dict(manager.patterns)
    manager.remove_task("task1")
    assert manager.patterns == before


def test_list_tasks_empty(manager):
    manager.create_pattern("pattern1")
    manager.list_tasks()
    assert manager.patterns["pattern1"] == {}


def test_list_tasks_nonempty(manager):
    manager.create_pattern("pattern1")
    manager.add_task("task1", "1h20m")
    manager.add_task("task2", "45")
    manager.list_tasks()
    assert manager.patterns["pattern1"]["task1"] == "1h20m"
    assert manager.patterns["pattern1"]["task2"] == "45"


def test_list_tasks_no_pattern(manager):
    # current_patternがNoneのときlist_tasksしてもエラーにならない
    before = dict(manager.patterns)
    manager.list_tasks()
    assert manager.patterns == before
