"""
SQL to Pseudocode - Comprehensive Test Suite
Run this file to test all major features.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parser import SQLParser
from app.generator import PseudocodeGenerator

parser = SQLParser()
generator = PseudocodeGenerator()

def test_query(name: str, sql: str):
    print("=" * 80)
    print(f"TEST: {name}")
    print("-" * 80)
    print(f"SQL:\n{sql}")
    print("\nPSEUDOCODE:")
    try:
        query = parser.parse(sql)
        pseudo = generator.generate(query)
        print(pseudo)
    except Exception as e:
        print(f"ERROR: {e}")
    print("=" * 80 + "\n")

# ===================================================================
# 1. Basic SELECT, WHERE, ORDER BY
# ===================================================================
test_query("Basic SELECT", 
    "SELECT * FROM employees;")

test_query("Column List + Aliases", 
    "SELECT e.name AS employee_name, e.salary FROM employees e;")

test_query("WHERE Clause", 
    "SELECT name, salary FROM employees WHERE salary > 50000 AND department_id = 10;")

test_query("ORDER BY", 
    "SELECT name, salary FROM employees ORDER BY salary DESC, name ASC;")

# ===================================================================
# 2. All Types of JOINs
# ===================================================================
test_query("INNER JOIN", 
    "SELECT e.name, d.dept_name FROM employees e INNER JOIN departments d ON e.dept_id = d.id;")

test_query("LEFT JOIN", 
    "SELECT e.name, d.dept_name FROM employees e LEFT JOIN departments d ON e.dept_id = d.id WHERE e.salary > 40000;")

test_query("RIGHT JOIN", 
    "SELECT e.name, d.dept_name FROM employees e RIGHT JOIN departments d ON e.dept_id = d.id;")

test_query("FULL OUTER JOIN", 
    "SELECT e.name, d.dept_name FROM employees e FULL OUTER JOIN departments d ON e.dept_id = d.id;")

# ===================================================================
# 3. GROUP BY + Aggregates + HAVING
# ===================================================================
test_query("GROUP BY + Aggregates", 
    "SELECT department_id, COUNT(*) as emp_count, AVG(salary) as avg_salary, SUM(salary) as total FROM employees GROUP BY department_id;")

test_query("GROUP BY + HAVING", 
    "SELECT department_id, COUNT(*) as count FROM employees GROUP BY department_id HAVING COUNT(*) > 5 AND AVG(salary) > 60000;")

# ===================================================================
# 4. Subqueries in FROM
# ===================================================================
test_query("Subquery in FROM", 
    "SELECT e.name, sub.dept_name FROM employees e JOIN (SELECT id, dept_name FROM departments WHERE active = 'Y') sub ON e.dept_id = sub.id;")

# ===================================================================
# 5. Subqueries in WHERE (IN)
# ===================================================================
test_query("Subquery in WHERE (IN)", 
    "SELECT name, salary FROM employees WHERE dept_id IN (SELECT id FROM departments WHERE location = 'New York');")

# ===================================================================
# 6. Database Links (@dblink)
# ===================================================================
test_query("Database Link", 
    "SELECT * FROM employees@remote_db;")

test_query("JOIN with Database Link", 
    "SELECT e.name, d.dept_name FROM employees@hq e INNER JOIN departments@remote d ON e.dept_id = d.id;")

print("✅ All tests completed!")