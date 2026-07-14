from __future__ import annotations

import re
from .model import Task, TodoTree

LINE = re.compile(r"^(?P<indent>\s*)[-*+]\s+\[(?P<check>[ xX])\]\s+(?P<title>.*)$")

def to_markdown(tree: TodoTree) -> str:
    def lines(tasks: list[Task], depth: int):
        result = []
        for task in tasks:
            mark = "x" if task.state == "complete" else " "
            result.append(f"{'  ' * depth}- [{mark}] {task.title}")
            result.extend(lines(task.children, depth + 1))
        return result
    return "\n".join(lines(tree.roots, 0)) + ("\n" if tree.roots else "")

def from_markdown(text: str) -> TodoTree:
    roots: list[Task] = []; stack: list[tuple[int, Task]] = []
    for raw in text.splitlines():
        match = LINE.match(raw)
        if not match: continue
        depth = len(match["indent"].expandtabs(2)) // 2
        task = Task(match["title"], match["check"].lower() == "x")
        while stack and stack[-1][0] >= depth: stack.pop()
        if stack: stack[-1][1].children.append(task)
        else: roots.append(task)
        stack.append((depth, task))
    return TodoTree(roots)
