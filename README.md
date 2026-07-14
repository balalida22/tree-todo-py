# tree-todo

A minimal, dependency-free Ubuntu terminal todo app.

## Quick start

### Install uv (Ubuntu)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal (or reload its shell profile), then clone and run the
project:

```bash
git clone https://github.com/YOUR-USERNAME/tree-todo.git
cd tree-todo
uv run tree-todo
```

`uv` creates the Python environment and installs the application automatically.
No system-wide Python packages are required.

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

## Publish to GitHub

Create an empty `tree-todo` repository on GitHub, then run these commands from
this project directory (replace `YOUR-USERNAME`):

```bash
git init
git add README.md pyproject.toml uv.lock tree_todo tests traces.json
git commit -m "Initial tree-todo release"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/tree-todo.git
git push -u origin main
```
