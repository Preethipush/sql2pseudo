from app.model import QueryModel
from app.helpers import loop_var


class Explainer:

    def explain(self, query: QueryModel) -> list:
        base = query.tables[0]
        var = loop_var(base)
        bullets = [f"First, the system reads the {base.name.upper()} table."]

        for join in query.joins:
            bullets.append(f"For each record, it looks up matching rows in {join.table.upper()} "
                            f"({join.type} JOIN, matched where {join.condition}).")

        if query.where:
            bullets.append(f"It keeps only the records where {query.where}.")

        if query.is_star:
            bullets.append(f"It collects every field of each matching {var}.")
        else:
            names = [item.alias if item.alias else item.expr for item in query.select]
            bullets.append("It collects " + ", ".join(names) + ".")

        if query.order_by:
            parts = [f'{o.expr} ({"descending" if o.desc else "ascending"})' for o in query.order_by]
            bullets.append("Finally, it sorts the results by " + ", ".join(parts) + " and displays them.")
        else:
            bullets.append("Finally, it displays the collected results.")

        return bullets
