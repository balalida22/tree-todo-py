from __future__ import annotations

import curses
from pathlib import Path

from .markdown import from_markdown, to_markdown
from .model import TodoTree
from .persistence import export_json, import_json, load, save

HELP = "j/k move  h/l fold  space toggle  a/c/s add  e edit  d delete  J/K move  </> out/in  u/r undo/redo  i/x import/export  q quit"

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
    def prompt(self, screen, label: str) -> str:
        curses.echo(); screen.addstr(curses.LINES - 1, 0, label); screen.clrtoeol(); screen.refresh()
        value = screen.getstr(curses.LINES - 1, len(label)).decode().strip(); curses.noecho(); return value
    def mutate(self, operation):
        self.remember(); result = operation()
        if result is False: self.undo_stack.pop()
        else: save(self.tree)
        return result
    def run(self, screen):
        curses.curs_set(0); screen.keypad(True)
        while True:
            screen.erase(); screen.addnstr(0, 0, "tree-todo", curses.COLS - 1)
            visible = self.tree.visible()
            for i, item in enumerate(visible[:curses.LINES - 3]):
                state = {"incomplete": "[ ]", "partial": "[-]", "complete": "[x]"}[item.task.state]
                branch = "▾ " if item.task.children and item.task.id in self.tree.expanded else "▸ " if item.task.children else "  "
                prefix = ">" if i == self.cursor else " "
                screen.addnstr(i + 1, 0, f"{prefix}{'  ' * item.depth}{branch}{state} {item.task.title}", curses.COLS - 1)
            screen.addnstr(curses.LINES - 2, 0, HELP, curses.COLS - 1); screen.refresh()
            key = screen.get_wch(); selected = self.selected()
            if key == 'q': return
            if key in ('j', curses.KEY_DOWN): self.cursor = min(self.cursor + 1, max(0, len(visible) - 1))
            elif key in ('k', curses.KEY_UP): self.cursor = max(0, self.cursor - 1)
            elif key == 'h' and selected: self.tree.expanded.discard(selected.task.id)
            elif key == 'l' and selected: self.tree.expanded.add(selected.task.id)
            elif key == ' ' and selected: self.mutate(lambda: self.tree.toggle(selected.task.id))
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
