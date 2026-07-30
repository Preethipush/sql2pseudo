from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Table:
    name: str
    alias: str


@dataclass
class Join:
    type: str
    table: str
    alias: str
    condition: str


@dataclass
class OrderItem:
    expr: str
    desc: bool = False


@dataclass
class SelectItem:
    expr: str
    alias: str | None = None


@dataclass
class CTE:
    name: str
    query: "QueryModel"


@dataclass
class Subquery:
    """Represents a subquery in FROM clause (NEW)"""
    alias: str
    query: "QueryModel"


@dataclass
class QueryModel:
    tables: list[Table] = field(default_factory=list)
    joins: list[Join] = field(default_factory=list)

    ctes: list[CTE] = field(default_factory=list)
    subqueries: list[Subquery] = field(default_factory=list)   # <-- NEW

    is_star: bool = False
    select: list[SelectItem] = field(default_factory=list)

    where: str | None = None
    group_by: list[str] = field(default_factory=list)
    having: str | None = None
    order_by: list[OrderItem] = field(default_factory=list)

    dblink: str | None = None