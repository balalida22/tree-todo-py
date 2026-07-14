from tree_todo.markdown import from_markdown, to_markdown

def test_markdown_round_trip_and_completion():
    tree = from_markdown("- [x] Done\n  - [ ] Later\n- [ ] Next\n")
    assert [task.title for task in tree.roots] == ["Done", "Next"]
    # Parent checkboxes are derived from their children, not independently mutable.
    assert tree.roots[0].state == "incomplete"
    assert to_markdown(tree) == "- [ ] Done\n  - [ ] Later\n- [ ] Next\n"
