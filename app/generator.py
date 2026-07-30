from app.model import QueryModel
from app.helpers import loop_var


class PseudocodeGenerator:

    def generate(self, query: QueryModel, is_nested: bool = False) -> str:

        if not is_nested:
            lines = [
                "START",
                "DECLARE",
                "    List to hold result",
                "BEGIN"
            ]
        else:
            lines = []

        # CTEs
        if query.ctes:
            for cte in query.ctes:
                lines.extend(self._generate_cte(cte))

        if not query.tables:
            if not is_nested:
                lines.append("END")
            return "\n".join(lines)

        # Subqueries in FROM
        if getattr(query, "subqueries", None):
            for subq in query.subqueries:
                lines.extend(self._generate_subquery(subq))

        table = query.tables[0]
        source = table.name.upper()
        if query.dblink:
            source += f" (at {query.dblink})"

        # JOIN QUERY
        if query.joins:
            lines.append(f"    READ records from {source}")
            for join in query.joins:
                lines.append(f"    JOIN records WITH {join.table.upper()}")
                lines.append(f"        ON {join.condition}")
            if query.where:
                lines.append(f"    FILTER joined records WHERE {query.where}")
            self._emit_join_select(lines, query)

        # NORMAL QUERY
        else:
            lines.append(f"    READ records from {source}")

            if query.where:
                lines.append(f"    FILTER records WHERE {query.where}")

            if query.group_by:
                lines.append(f"    GROUP records BY {', '.join(query.group_by)}")
                group_cols = {c.upper() for c in query.group_by}

                for item in query.select:
                    expr = item.expr.strip()
                    expr_upper = expr.upper()
                    alias = item.alias or "value"

                    if "COUNT" in expr_upper:
                        lines.append(f"        CALCULATE COUNT(*) AS {alias}")
                    elif "AVG" in expr_upper:
                        lines.append(f"        CALCULATE ROUND(AVG({expr})) AS {alias}")
                    elif any(x in expr_upper for x in ["SUM", "MIN", "MAX"]):
                        lines.append(f"        CALCULATE {expr} AS {alias}")
                    else:
                        if expr_upper not in group_cols:
                            lines.append(f"        CALCULATE {expr} AS {alias}")

                if query.having:
                    lines.append(f"    KEEP groups WHERE {query.having}")

            else:
                var = loop_var(table)
                lines.append(f"    FOR EACH {var} IN {source}")
                indent = "        "

                if query.where:
                    lines.append(f"{indent}IF {query.where} THEN")
                    indent += "    "

                self._emit_select(lines, indent, query, var)

                if query.where:
                    indent = indent[:-4]
                    lines.append(f"{indent}END IF")

                lines.append("    END FOR")

        # ORDER BY
        if query.order_by:
            parts = [f"{item.expr} {'DESCENDING' if item.desc else 'ASCENDING'}" 
                     for item in query.order_by]
            lines.append(f"    SORT result BY {', '.join(parts)}")

        if not is_nested:
            lines.append("    DISPLAY result")
            lines.append("END")

        return "\n".join(lines)

    def _generate_cte(self, cte):
        lines = [f"    CREATE temporary result set '{cte.name}' as:"]

        nested = self.generate(cte.query, is_nested=True).splitlines()
        skip = {"START", "DECLARE", "BEGIN", "DISPLAY result", "END"}

        for line in nested:
            if line.strip() in skip:
                continue
            lines.append("        " + line.strip())

        lines.append(f"    STORE result AS {cte.name}")
        lines.append("")
        return lines

    def _generate_subquery(self, subq):
        lines = [f"    CREATE temporary result set '{subq.alias}' as:"]

        nested = self.generate(subq.query, is_nested=True).splitlines()
        skip = {"START", "DECLARE", "BEGIN", "DISPLAY result", "END"}

        for line in nested:
            if line.strip() in skip:
                continue
            lines.append("        " + line.strip())

        lines.append(f"    STORE result AS {subq.alias}")
        lines.append("")
        return lines

    def _emit_join_select(self, lines, query):
        if query.is_star:
            return
        cols = [item.alias if item.alias else item.expr for item in query.select]
        if cols:
            lines.append("    ADD " + ", ".join(cols))
            lines.append("        TO result")

    def _emit_select(self, lines, indent, query, loop_var_name):
        if query.is_star:
            lines.append(f"{indent}ADD {loop_var_name} TO result")
            return
        cols = [item.alias if item.alias else item.expr for item in query.select]
        if len(cols) == 1:
            lines.append(f"{indent}ADD {cols[0]} TO result")
        else:
            lines.append(f"{indent}ADD " + ", ".join(cols))
            lines.append(f"{indent}    TO result")