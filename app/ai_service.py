import os
import logging

logger = logging.getLogger(__name__)

MODEL = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")


def _get_client():
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not groq_key and not openai_key:
        return None

    try:
        from openai import OpenAI
        if groq_key:
            return OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        return OpenAI(api_key=openai_key)
    except ImportError:
        logger.warning("`openai` package not installed — AI features disabled.")
        return None


def is_available() -> bool:
    return _get_client() is not None


def explain_with_ai(sql: str):
    client = _get_client()
    if client is None:
        return None
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Explain the given SQL query in plain English as 3-6 short bullet points. No preamble, no markdown headers, just the bullets."},
                {"role": "user", "content": sql},
            ],
        )
        text = resp.choices[0].message.content or ""
        bullets = [l.lstrip("-*• ").strip() for l in text.splitlines() if l.strip()]
        return bullets or None
    except Exception:
        logger.exception("AI explanation call failed")
        return None


def generate_pseudocode_with_ai(sql: str):
    client = _get_client()
    if client is None:
        return None
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": """
You are a strict, precise Oracle SQL pseudocode generator.

Rules - Follow exactly:
- Output ONLY pseudocode. No extra words, no explanations.
- Use this exact structure:

START
DECLARE
    List to hold result
BEGIN

    CREATE temporary result set 'name' as:   (for CTEs and subqueries)
    READ records from TABLE
    FILTER records WHERE condition
    JOIN records WITH TABLE ON condition
    GROUP records BY column
    CALCULATE COUNT(*) AS alias
    CALCULATE ROUND(AVG(...)) AS alias
    CALCULATE SUM(...) AS alias
    SORT result BY column DESCENDING
    DISPLAY result
END

Guidelines:
• CTE or Subquery → Always use "CREATE temporary result set 'name' as:"
• JOIN → "JOIN records WITH TABLE ON condition"
• GROUP BY → "GROUP records BY column"
• WHERE → "FILTER records WHERE condition"
• @dblink → include in READ line like "READ records from TABLE (at dblink)"
• Use "DESCENDING" not "descending order"
• Be concise and consistent with rule-based output
• For subqueries: use "CREATE temporary result set 'alias' as:"

Return ONLY the pseudocode.
"""
                },
                {"role": "user", "content": sql},
            ],
        )
        return (resp.choices[0].message.content or "").strip() or None
    except Exception:
        logger.exception("AI pseudocode fallback call failed")
        return None


class AIService:
    def generate(self, query):
        if hasattr(query, "original_sql"):
            sql = query.original_sql
        elif isinstance(query, str):
            sql = query
        else:
            sql = str(query)

        return generate_pseudocode_with_ai(sql)