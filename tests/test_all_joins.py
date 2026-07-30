"""
Run this locally to verify the pipeline before touching the browser at all.
No HTTP, no JSON, no shell-quoting to fight with.

Usage:  python tests/test_queries.py
(run from the project root)
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parser import SQLParser, UnsupportedSQLError
from app.generator import PseudocodeGenerator
from app.explainer import Explainer


parser = SQLParser()
generator = PseudocodeGenerator()

tests = {
    "INNER JOIN": "SELECT e.name, d.dept_name FROM employees e INNER JOIN departments d ON e.dept_id = d.id;",
    "LEFT JOIN": "SELECT e.name, d.dept_name FROM employees e LEFT JOIN departments d ON e.dept_id = d.id;",
    "RIGHT JOIN": "SELECT e.name, d.dept_name FROM employees e RIGHT JOIN departments d ON e.dept_id = d.id;",
    "FULL OUTER JOIN": "SELECT e.name, d.dept_name FROM employees e FULL OUTER JOIN departments d ON e.dept_id = d.id;",
    "LEFT JOIN + WHERE": "SELECT u.user_id, u.username, o.order_id FROM users u LEFT JOIN orders o ON u.user_id = o.user_id WHERE u.country = 'US';"
}

for name, sql in tests.items():
    print(f"\n🔹 {name}")
    print("-" * 60)
    print(sql)
    print("\nPseudocode:")
    query = parser.parse(sql)
    print(generator.generate(query))
    print("=" * 80)