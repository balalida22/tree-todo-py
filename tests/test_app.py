from tree_todo.app import App
from tree_todo.model import TodoTree


class FakeScreen:
    def __init__(self, height, width): self.height, self.width, self.lines = height, width, []
    def getmaxyx(self): return self.height, self.width
    def erase(self): pass
    def addnstr(self, row, column, text, count):
        assert 0 <= row < self.height
        assert count >= 0
        self.lines.append((row, text[:count]))
    def refresh(self): pass


def test_draw_handles_shrunk_terminal_dimensions():
    app = App.__new__(App); app.tree = TodoTree(); app.cursor = 0
    app.tree.add_root("A task")
    assert app.draw(FakeScreen(1, 1))
    assert app.draw(FakeScreen(2, 12))
