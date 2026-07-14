from tree_todo.model import TodoTree

def test_visible_tree_and_mutations():
    tree = TodoTree(); a = tree.add_root("A"); b = tree.add_root("B")
    child = tree.add_child(a.id, "child")
    assert [(x.task.title, x.depth) for x in tree.visible()] == [("A", 0), ("child", 1), ("B", 0)]
    assert tree.indent(b.id); assert tree.find(b.id) in a.children
    assert tree.unindent(b.id); assert tree.move(b.id, -1)
    assert tree.add_sibling(child.id, "sibling").title == "sibling"
    assert tree.delete(child.id).title == "child"

def test_completion_propagation_is_derived():
    tree = TodoTree(); parent = tree.add_root("parent"); one = tree.add_child(parent.id, "one"); two = tree.add_child(parent.id, "two")
    assert parent.state == "incomplete"
    tree.toggle(one.id); assert parent.state == "partial"
    tree.toggle(two.id); assert parent.state == "complete"
    tree.toggle(one.id); assert parent.state == "partial"

def test_only_leaves_can_be_toggled():
    tree = TodoTree(); parent = tree.add_root("parent"); tree.add_child(parent.id, "child")
    tree.toggle(parent.id)
    assert parent.state == "incomplete"

def test_partial_state_propagates_through_nested_parents():
    tree = TodoTree(); root = tree.add_root("root"); parent = tree.add_child(root.id, "parent"); leaf = tree.add_child(parent.id, "leaf")
    tree.toggle(leaf.id)
    assert parent.state == root.state == "complete"
    tree.add_child(parent.id, "another leaf")
    assert parent.state == root.state == "partial"

def test_highlight_can_be_cancelled_and_is_removed_when_finished():
    tree = TodoTree(); task = tree.add_root("urgent")
    tree.toggle_highlight(task.id); assert task.highlighted
    tree.toggle_highlight(task.id); assert not task.highlighted
    tree.toggle_highlight(task.id); tree.toggle(task.id)
    assert task.state == "complete" and not task.highlighted

def test_completed_parent_loses_highlight():
    tree = TodoTree(); parent = tree.add_root("parent"); child = tree.add_child(parent.id, "child")
    tree.toggle_highlight(parent.id); tree.toggle(child.id)
    assert parent.state == "complete" and not parent.highlighted
