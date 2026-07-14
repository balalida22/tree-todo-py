# tree-todo

A minimal, dependency-free Ubuntu terminal todo app.

## Quick start

Clone and run the project:

```bash
git clone https://github.com/YOUR-USERNAME/tree-todo.git
cd tree-todo
uv run tree-todo
```

### Use the app

Keys: `j`/`k` move, `h`/`l` collapse/expand, Space toggles leaf tasks, `a` adds a
root, `c` a child, `s` a sibling, `e` edits, `d` deletes, `J`/`K` moves,
`>`/`<` indents/unindents, `u` undo, `r` redo, `i` imports JSON or Markdown,
`x` exports JSON or Markdown, and `q` quits.

Data is automatically saved to `$XDG_DATA_HOME/tree-todo/tasks-v1.json`
(or `~/.local/share/tree-todo/tasks-v1.json`).

### Import and export

Press `i` to import or `x` to export, then enter a file path. Files ending in
`.md` or `.markdown` use Markdown checklists; all other names use the
versioned JSON format.

## Development

Run the test suite with:

```bash
uv run pytest
```
