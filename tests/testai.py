import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parser import SQLParser, UnsupportedSQLError
from app.generator import PseudocodeGenerator
from app.explainer import Explainer


sql = """
SELECT department_id,
       AVG(salary)
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 50000;
"""

parser = SQLParser()
query = parser.parse(sql)

generator = PseudocodeGenerator()

print(generator.generate(query))