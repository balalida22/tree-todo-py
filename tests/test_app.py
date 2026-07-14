from tree_todo.app import App
from tree_todo.model import TodoTree


class FakeScreen:
    def __init__(self, height, width): self.height, self.width, self.lines = height, width, []
    def getmaxyx(self): return self.height, self.width
    def erase(self): pass
    def addnstr(self, row, column, text, count, attributes=0):
        assert 0 <= row < self.height
        assert count >= 0
        self.lines.append((row, text[:count], attributes))
    def refresh(self): pass


def test_draw_handles_shrunk_terminal_dimensions():
    app = App.__new__(App); app.tree = TodoTree(); app.cursor = 0
    app.tree.add_root("A task")
    assert app.draw(FakeScreen(1, 1))
    assert app.draw(FakeScreen(2, 12))


def test_draw_highlights_priority_task():
    app = App.__new__(App); app.tree = TodoTree(); app.cursor = 0
    task = app.tree.add_root("Urgent"); app.tree.toggle_highlight(task.id)
    screen = FakeScreen(3, 40); app.draw(screen)
    task_line = next(line for line in screen.lines if line[0] == 1)
    assert "!" in task_line[1]
    assert task_line[2]
