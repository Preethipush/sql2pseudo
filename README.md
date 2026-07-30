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

## Supported SQL Features

| SQL Feature                  | Supported | Notes                          |
|-----------------------------|-----------|--------------------------------|
| SELECT                      | Yes       | Perfect                        |
| Column lists with aliases   | Yes       | Perfect                        |
| WHERE clause                | Yes       | Perfect                        |
| ORDER BY (ASC/DESC)         | Yes       | Perfect                        |
| INNER / LEFT / RIGHT / FULL JOIN | Yes  | Excellent                      |
| GROUP BY + Aggregates       | Yes       | COUNT, SUM, AVG, MIN, MAX      |
| HAVING clause               | Yes       | Good                           |
| Subqueries in FROM          | Yes       | Clean temporary result set     |
| Subqueries in WHERE (IN)    | Yes       | Clean temporary result set     |
| Complex SQL (UNION, CTE, EXISTS, Window functions) | Yes | Uses AI fallback |

---

## How to Run

```bash
cd sql2pseudo
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
