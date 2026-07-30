import logging

import sqlglot
from sqlglot import exp

from app.model import (
    QueryModel,
    Table,
    Join,
    OrderItem,
    SelectItem,
    CTE,
    Subquery,
)

logger = logging.getLogger(__name__)


class UnsupportedSQLError(Exception):
    pass


class SQLParser:

    def parse(self, sql: str) -> QueryModel:

        sql = (sql or "").strip()
        if not sql:
            raise UnsupportedSQLError("No SQL provided.")

        parsed = sqlglot.parse_one(sql)

        if isinstance(parsed, exp.With):
            parsed = parsed.this

        if not isinstance(parsed, exp.Select):
            raise UnsupportedSQLError(
                f"Only SELECT queries are supported right now (got {type(parsed).__name__})."
            )

        query = QueryModel()

        # -------------------------------------------------
        # WITH (CTE)
        # -------------------------------------------------
        with_clause = parsed.args.get("with")
        if with_clause:
            for cte in with_clause.expressions:
                try:
                    cte_name = cte.alias
                    cte_query = self.parse(cte.this.sql())
                    query.ctes.append(CTE(name=cte_name, query=cte_query))
                except Exception:
                    logger.exception("Skipping a CTE.")

        # -------------------------------------------------
        # FROM (with dblink)
        # -------------------------------------------------
        from_clause = parsed.args.get("from_") or parsed.args.get("from")
        if not from_clause:
            raise UnsupportedSQLError("Could not find a FROM clause.")

        table_expr = from_clause.this

        if isinstance(table_expr, exp.Subquery):
            subq_alias = table_expr.alias or "subquery"
            subq_model = self.parse(table_expr.this.sql())
            query.tables.append(Table(name=subq_alias, alias=subq_alias))
            query.subqueries.append(Subquery(alias=subq_alias, query=subq_model))
        else:
            name = getattr(table_expr, "name", None) or str(table_expr)
            alias = table_expr.alias or name

            # Handle database link
            if "@" in name:
                table_name, dblink = name.split("@", 1)
                query.tables.append(Table(name=table_name.strip(), alias=alias))
                query.dblink = dblink.strip()
            else:
                query.tables.append(Table(name=name, alias=alias))

        # -------------------------------------------------
        # JOINS (very tolerant dblink handling)
        # -------------------------------------------------
        joins = parsed.args.get("joins") or []
        for join in joins:
            try:
                jt_expr = join.this
                raw_name = str(jt_expr).strip()

                # Handle database link in JOIN
                if "@" in raw_name:
                    # Split on @ to get table and dblink
                    parts = raw_name.split("@", 1)
                    jname = parts[0].strip()
                    dblink = parts[1].strip() if len(parts) > 1 else None
                    if dblink:
                        query.dblink = dblink
                else:
                    jname = getattr(jt_expr, "name", None) or raw_name

                if isinstance(jt_expr, exp.Subquery):
                    jname = jt_expr.alias or "subquery"
                    subq_model = self.parse(jt_expr.this.sql())
                    query.subqueries.append(Subquery(alias=jname, query=subq_model))
                elif not jname:
                    continue

                jalias = jt_expr.alias or jname
                side = join.args.get("side")
                join_type = str(side).upper() if side else "INNER"

                on_clause = join.args.get("on")
                condition = on_clause.sql() if on_clause else "TRUE"

                query.tables.append(Table(name=jname, alias=jalias))
                query.joins.append(
                    Join(type=join_type, table=jname, alias=jalias, condition=condition)
                )
            except Exception as e:
                logger.exception(f"Skipping a JOIN clause: {e}")

        # -------------------------------------------------
        # SELECT
        # -------------------------------------------------
        select_exprs = parsed.expressions or []
        if len(select_exprs) == 1 and isinstance(select_exprs[0], exp.Star):
            query.is_star = True
        else:
            for expr in select_exprs:
                try:
                    alias_name = None
                    inner = expr
                    if isinstance(inner, exp.Alias):
                        alias_name = inner.alias
                        inner = inner.this
                    query.select.append(
                        SelectItem(expr=inner.sql(), alias=alias_name)
                    )
                except Exception:
                    logger.exception("Skipping SELECT item.")

        # -------------------------------------------------
        # WHERE, GROUP BY, HAVING, ORDER BY
        # -------------------------------------------------
        if where := parsed.args.get("where"):
            query.where = where.this.sql()

        if group := parsed.args.get("group"):
            query.group_by = [expr.sql() for expr in group.expressions]

        if having := parsed.args.get("having"):
            query.having = having.this.sql()

        if order := parsed.args.get("order"):
            for item in order.expressions:
                try:
                    query.order_by.append(
                        OrderItem(
                            expr=item.this.sql(),
                            desc=bool(item.args.get("desc")),
                        )
                    )
                except Exception:
                    logger.exception("Skipping ORDER BY item.")

        return query