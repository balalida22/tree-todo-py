from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Task:
    title: str
    completed: bool = False
    children: list[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    highlighted: bool = False

    @property
    def state(self) -> str:
        if not self.children:
            return "complete" if self.completed else "incomplete"
        child_states = [child.state for child in self.children]
        return "complete" if all(state == "complete" for state in child_states) else "partial" if any(state != "incomplete" for state in child_states) else "incomplete"

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "completed": self.completed,
                "highlighted": self.highlighted,
                "children": [child.to_dict() for child in self.children]}

    @classmethod
    def from_dict(cls, value: dict) -> Task:
        return cls(value["title"], value.get("completed", False),
                   [cls.from_dict(child) for child in value.get("children", [])],
                   value.get("id", str(uuid4())), value.get("highlighted", False))


@dataclass(frozen=True)
class VisibleTask:
    task: Task
    depth: int
    parent: Task | None


class TodoTree:
    def __init__(self, roots: list[Task] | None = None, expanded: set[str] | None = None):
        self.roots = roots or []
        self.expanded = expanded if expanded is not None else {task.id for task in self.walk() if task.children}

    def walk(self, tasks: list[Task] | None = None):
        for task in self.roots if tasks is None else tasks:
            yield task
            yield from self.walk(task.children)

    def find(self, task_id: str) -> Task | None:
        return next((task for task in self.walk() if task.id == task_id), None)

    def location(self, task_id: str) -> tuple[list[Task], int, Task | None]:
        def visit(items: list[Task], parent: Task | None):
            for index, task in enumerate(items):
                if task.id == task_id:
                    return items, index, parent
                found = visit(task.children, task)
                if found:
                    return found
            return None
        found = visit(self.roots, None)
        if not found:
            raise KeyError(task_id)
        return found

    def visible(self) -> list[VisibleTask]:
        result: list[VisibleTask] = []
        def visit(items: list[Task], depth: int, parent: Task | None):
            for task in items:
                result.append(VisibleTask(task, depth, parent))
                if task.id in self.expanded:
                    visit(task.children, depth + 1, task)
        visit(self.roots, 0, None)
        return result

    def add_root(self, title: str) -> Task:
        task = Task(title); self.roots.append(task); return task

    def add_child(self, parent_id: str, title: str) -> Task:
        parent = self.find(parent_id)
        if not parent: raise KeyError(parent_id)
        task = Task(title); parent.children.append(task); self.expanded.add(parent.id); return task

    def add_sibling(self, task_id: str, title: str) -> Task:
        items, index, _ = self.location(task_id)
        task = Task(title); items.insert(index + 1, task); return task

    def delete(self, task_id: str) -> Task:
        items, index, _ = self.location(task_id)
        task = items.pop(index); self.expanded.discard(task.id); return task

    def edit(self, task_id: str, title: str) -> None: self.find(task_id).title = title

    def toggle(self, task_id: str) -> None:
        task = self.find(task_id)
        if not task or task.children: return
        task.completed = not task.completed
        for candidate in self.walk():
            if candidate.state == "complete": candidate.highlighted = False

    def toggle_highlight(self, task_id: str) -> None:
        task = self.find(task_id)
        if not task or task.state == "complete": return
        task.highlighted = not task.highlighted

    def move(self, task_id: str, direction: int) -> bool:
        items, index, _ = self.location(task_id); other = index + direction
        if not 0 <= other < len(items): return False
        items[index], items[other] = items[other], items[index]; return True

    def indent(self, task_id: str) -> bool:
        items, index, _ = self.location(task_id)
        if index == 0: return False
        task = items.pop(index); new_parent = items[index - 1]
        new_parent.children.append(task); self.expanded.add(new_parent.id); return True

    def unindent(self, task_id: str) -> bool:
        items, index, parent = self.location(task_id)
        if parent is None: return False
        grand_items, parent_index, _ = self.location(parent.id)
        task = items.pop(index); grand_items.insert(parent_index + 1, task); return True

    def snapshot(self) -> dict:
        return {"tasks": [task.to_dict() for task in self.roots], "expanded": sorted(self.expanded)}

    @classmethod
    def restore(cls, snapshot: dict) -> TodoTree:
        return cls([Task.from_dict(task) for task in snapshot.get("tasks", [])], set(snapshot.get("expanded", [])))
