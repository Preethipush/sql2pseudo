# SQL2PSEUDO

SQL to Pseudocode Converter with Plain English Explanation

A lightweight, fast, and intelligent tool that converts Oracle-style SQL queries into readable business pseudocode and plain English explanations.

---

## Features

- Converts SQL → Structured Pseudocode
- Generates Plain English Bullet Points
- Hybrid Engine: Rule-based (fast) + AI fallback (for complex queries)
- Clean Web UI (FastAPI + HTML/JS)
- Supports Oracle SQL syntax

---

 
| SQL Feature                    | Supported | Notes |
|-------------------------------|-----------|-------|
| SELECT                     | Yes | Perfect |
| Column lists with aliases     | Yes | Perfect |
| WHERE clause                | Yes | Perfect |
| ORDER BY (ASC/DESC)         | Yes | Perfect |
| INNER / LEFT / RIGHT / FULL JOIN | Yes | Excellent |
| GROUP BY + Aggregates       | Yes | COUNT, SUM, AVG, MIN, MAX |
| HAVING clause               | Yes | Good |
| Subqueries in FROM        | Yes | Clean temporary result set |
| Subqueries in WHERE (IN) | Yes | Clean temporary result set |
| Database Links (@dblink)    | Yes | Shown in READ line |

Complex SQL (UNION, CTE, EXISTS, Window functions) → Uses AI fallback

---


### Basic SELECT
sql
SELECT  FROM employees;

JOIN + WHERE + ORDER BY

SELECT e.name, d.dept_name 
FROM employees e 
LEFT JOIN departments d ON e.dept_id = d.id 
WHERE e.salary > 50000 
ORDER BY e.salary DESC;

GROUP BY + HAVING
SELECT department_id, COUNT() as emp_count 
FROM employees 
GROUP BY department_id 
HAVING COUNT() > 5 AND AVG(salary) > 60000;

Subquery in FROM
SELECT e.name, sub.dept_name 
FROM employees e 
JOIN (SELECT id, dept_name FROM departments WHERE active = 'Y') sub 
ON e.dept_id = sub.id;

Subquery in WHERE
SELECT name FROM employees 
WHERE dept_id IN (SELECT id FROM departments WHERE location = 'NY');

How to Run
Bashcd sql2pseudo_modified
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
Open: http://localhost:8003

Tech Stack

FastAPI + Uvicorn
sqlglot (SQL parsing)
Groq + OpenAI (AI fallback)
Pure HTML + CSS + JS frontend