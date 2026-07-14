from __future__ import annotations

import curses
from pathlib import Path

from .markdown import from_markdown, to_markdown
from .model import TodoTree
from .persistence import export_json, import_json, load, save

HELP = "j/k move  h/l fold  space done  p priority  a/c/s add  e edit  d delete  J/K move  </> out/in  u/r undo/redo  i/x import/export  q quit"

class App:
    def __init__(self):
        self.tree = load(); self.cursor = 0; self.undo_stack: list[dict] = []; self.redo_stack: list[dict] = []
    def selected(self):
        visible = self.tree.visible(); return visible[min(self.cursor, len(visible) - 1)] if visible else None
    def remember(self):
        self.undo_stack.append(self.tree.snapshot()); self.redo_stack.clear()
    def restore(self, source, target):
        if not source: return
        target.append(self.tree.snapshot()); self.tree = TodoTree.restore(source.pop()); self.cursor = min(self.cursor, max(0, len(self.tree.visible()) - 1))

    @staticmethod
    def _write(screen, row: int, text: str, width: int, attributes: int = 0) -> None:
        """Write a clipped line; curses raises if a resize invalidates a cell."""
        if width <= 0: return
        try: screen.addnstr(row, 0, text, max(0, width - 1), attributes)
        except curses.error: pass

    def prompt(self, screen, label: str) -> str:
        height, width = screen.getmaxyx()
        if height < 2 or width <= len(label): return ""
        row, column = height - 1, len(label)
        curses.echo()
        try:
            self._write(screen, row, label, width); screen.clrtoeol(); screen.refresh()
            return screen.getstr(row, column, width - column - 1).decode().strip()
        except curses.error:
            return ""
        finally:
            curses.noecho()
    def mutate(self, operation):
        self.remember(); result = operation()
        if result is False: self.undo_stack.pop()
        else: save(self.tree)
        return result

    def draw(self, screen) -> list:
        """Render against the current dimensions, including very small windows."""
        height, width = screen.getmaxyx()
        try: screen.erase()
        except curses.error: return []
        if height <= 0 or width <= 0: return []
        self._write(screen, 0, "tree-todo", width)
        visible = self.tree.visible()
        task_rows = max(0, height - 2)  # header plus a help line when possible
        for i, item in enumerate(visible[:task_rows]):
            state = {"incomplete": "[ ]", "partial": "[-]", "complete": "[x]"}[item.task.state]
            branch = "▾ " if item.task.children and item.task.id in self.tree.expanded else "▸ " if item.task.children else "  "
            prefix = ">" if i == self.cursor else " "
            priority = "!" if item.task.highlighted else " "
            attributes = curses.A_BOLD | curses.A_REVERSE if item.task.highlighted else 0
            self._write(screen, i + 1, f"{prefix}{priority}{'  ' * item.depth}{branch}{state} {item.task.title}", width, attributes)
        if height >= 2: self._write(screen, height - 1, HELP, width)
        try: screen.refresh()
        except curses.error: pass
        return visible

    def run(self, screen):
        try: curses.curs_set(0)
        except curses.error: pass
        screen.keypad(True)
        while True:
            visible = self.draw(screen)
            try: key = screen.get_wch()
            except curses.error: continue
            if key == curses.KEY_RESIZE: continue
            selected = self.selected()
            if key == 'q': return
            if key in ('j', curses.KEY_DOWN): self.cursor = min(self.cursor + 1, max(0, len(visible) - 1))
            elif key in ('k', curses.KEY_UP): self.cursor = max(0, self.cursor - 1)
            elif key == 'h' and selected: self.tree.expanded.discard(selected.task.id)
            elif key == 'l' and selected: self.tree.expanded.add(selected.task.id)
            elif key == ' ' and selected: self.mutate(lambda: self.tree.toggle(selected.task.id))
            elif key == 'p' and selected: self.mutate(lambda: self.tree.toggle_highlight(selected.task.id))
            elif key == 'a':
                if title := self.prompt(screen, "Root title: "): self.mutate(lambda: self.tree.add_root(title)); self.cursor = len(self.tree.visible()) - 1
            elif key in ('c', 's', 'e') and selected:
                action = {"c": "Child title: ", "s": "Sibling title: ", "e": "New title: "}[key]
                if title := self.prompt(screen, action):
                    self.mutate(lambda: self.tree.add_child(selected.task.id, title) if key == 'c' else self.tree.add_sibling(selected.task.id, title) if key == 's' else self.tree.edit(selected.task.id, title))
            elif key == 'd' and selected: self.mutate(lambda: self.tree.delete(selected.task.id)); self.cursor = max(0, self.cursor - 1)
            elif key in ('J', 'K', '>', '<') and selected:
                method = {'J': lambda: self.tree.move(selected.task.id, 1), 'K': lambda: self.tree.move(selected.task.id, -1), '>': lambda: self.tree.indent(selected.task.id), '<': lambda: self.tree.unindent(selected.task.id)}[key]
                self.mutate(method)
            elif key == 'u': self.restore(self.undo_stack, self.redo_stack); save(self.tree)
            elif key == 'r': self.restore(self.redo_stack, self.undo_stack); save(self.tree)
            elif key in ('i', 'x'):
                filename = self.prompt(screen, "Path: ")
                if filename:
                    path = Path(filename)
                    if key == 'i': self.remember(); self.tree = from_markdown(path.read_text()) if path.suffix.lower() in ('.md', '.markdown') else import_json(path); self.cursor = 0; save(self.tree)
                    elif path.suffix.lower() in ('.md', '.markdown'): path.write_text(to_markdown(self.tree))
                    else: export_json(self.tree, path)

def main():
    curses.wrapper(lambda screen: App().run(screen))
