"""
AI Fallback Test Suite - Complex SQL
These queries should trigger AI generation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parser import SQLParser, UnsupportedSQLError
from app import ai_service

# Test complex SQL that should use AI
complex_queries = {
    "CTE (WITH)": """
        WITH dept_stats AS (
            SELECT department_id, COUNT(*) as emp_count 
            FROM employees 
            GROUP BY department_id
        )
        SELECT e.name, ds.emp_count 
        FROM employees e 
        JOIN dept_stats ds ON e.department_id = ds.department_id;
    """,

    "UNION": """
        SELECT name, salary FROM employees WHERE department_id = 10
        UNION
        SELECT name, salary FROM contractors WHERE active = 'Y';
    """,

    "EXISTS Subquery": """
        SELECT name FROM employees e 
        WHERE EXISTS (
            SELECT 1 FROM departments d 
            WHERE d.id = e.dept_id AND d.location = 'NY'
        );
    """,

    "Correlated Subquery": """
        SELECT name, salary FROM employees e 
        WHERE salary > (
            SELECT AVG(salary) FROM employees 
            WHERE department_id = e.department_id
        );
    """,

    "Window Function": """
        SELECT name, salary, 
               RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank
        FROM employees;
    """,

    "PIVOT (Oracle)": """
        SELECT * FROM (
            SELECT department_id, salary 
            FROM employees
        ) PIVOT (
            AVG(salary) FOR department_id IN (10, 20, 30)
        );
    """
}

print("🚀 Testing AI Fallback for Complex SQL\n")

for name, sql in complex_queries.items():
    print("=" * 80)
    print(f"TEST: {name}")
    print("-" * 80)
    print(f"SQL:\n{sql.strip()}")
    print("\nAI PSEUDOCODE:")

    try:
        # Force AI fallback
        ai_result = ai_service.generate_pseudocode_with_ai(sql)
        if ai_result:
            print(ai_result)
        else:
            print("❌ AI returned nothing (check API keys)")
    except Exception as e:
        print(f"ERROR: {e}")

    print("=" * 80 + "\n")

print("✅ AI Fallback Test Completed!")