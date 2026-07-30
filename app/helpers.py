def singularize(name: str) -> str:
    """Very small heuristic: employees -> employee. Not linguistically
    complete, just enough for readable pseudocode variable names."""
    lower = name.lower()
    if lower.endswith("ies"):
        return lower[:-3] + "y"
    if lower.endswith("ses") or lower.endswith("xes") or lower.endswith("ches"):
        return lower[:-2]
    if lower.endswith("s") and not lower.endswith("ss"):
        return lower[:-1]
    return lower


def loop_var(table) -> str:
    if table.alias and table.alias.lower() != table.name.lower():
        return table.alias
    return singularize(table.name)
