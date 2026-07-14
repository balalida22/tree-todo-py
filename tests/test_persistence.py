from tree_todo.model import TodoTree
from tree_todo.persistence import load, save

def test_save_load_round_trip(tmp_path):
    tree = TodoTree(); root = tree.add_root("root"); child = tree.add_child(root.id, "child")
    tree.toggle_highlight(child.id)
    path = save(tree, tmp_path / "tasks-v1.json")
    restored = load(path)
    assert restored.snapshot() == tree.snapshot()

def test_version_is_validated(tmp_path):
    path = tmp_path / "tasks.json"; path.write_text('{"version": 99}')
    try: load(path)
    except ValueError: pass
    else: assert False, "expected incompatible version"
