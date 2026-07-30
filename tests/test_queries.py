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

SAMPLES = {
    "Star select": "SELECT * FROM employees",
    "Column list": "SELECT name, salary FROM employees",
    "With alias": "SELECT e.name, e.salary FROM employees e",
    "Where clause": "SELECT * FROM employees WHERE salary > 50000",
    "Join": "SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id",
    "Order by": "SELECT * FROM employees ORDER BY salary DESC",
    "Combined": (
        "SELECT e.name, d.dept_name FROM employees e "
        "JOIN departments d ON e.dept_id = d.id "
        "WHERE e.salary > 50000 ORDER BY e.salary DESC"
    ),
}

if __name__ == "__main__":
    parser = SQLParser()
    generator = PseudocodeGenerator()
    explainer = Explainer()

    for label, sql in SAMPLES.items():
        print("=" * 90)
        print(f"[{label}]\n{sql}\n")
        try:
            query = parser.parse(sql)
            print(generator.generate(query))
            print("\n-- explanation --")
            for b in explainer.explain(query):
                print("-", b)
        except UnsupportedSQLError as e:
            print("UNSUPPORTED:", e)
        except Exception:
            traceback.print_exc()
        print()
