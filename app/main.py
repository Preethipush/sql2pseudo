import logging
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import ConvertRequest, ConvertResponse, DetectedObjects
from app.parser import SQLParser, UnsupportedSQLError
from app.generator import PseudocodeGenerator
from app.explainer import Explainer
from app import ai_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("sql2pseudo")


app = FastAPI(
    title="SQL2PSEUDO",
    version="0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8003",
        "http://127.0.0.1:8003",
    ],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

parser = SQLParser()
generator = PseudocodeGenerator()
explainer = Explainer()


# ==========================================================
# Queries that should be handled directly by the LLM
# ==========================================================

COMPLEX_SQL = (
    "GROUP BY",
    "HAVING",
    "UNION",
    "UNION ALL",
    "INTERSECT",
    "MINUS",
    "WITH ",
    "CONNECT BY",
    "START WITH",
    "PIVOT",
    "UNPIVOT",
    "OVER(",
    "PARTITION BY",
    "MODEL",
    "MERGE",
    "MATCH_RECOGNIZE",
)


@app.post("/api/convert", response_model=ConvertResponse)
def convert(request: ConvertRequest) -> ConvertResponse:

    sql = (request.sql or "").strip()

    if not sql:
        return ConvertResponse(
            status="error",
            message="Please enter a SQL query.",
        )

    try:

        ####################################################
        # Use AI first for complex SQL
        ####################################################

        upper_sql = sql.upper()

        if any(keyword in upper_sql for keyword in COMPLEX_SQL):

            logger.info("Complex SQL detected -> Using AI")

            ai_pseudo = ai_service.generate_pseudocode_with_ai(sql)

            if ai_pseudo:

                return ConvertResponse(
                    status="success",
                    pseudo_code=ai_pseudo,
                    explanation=ai_service.explain_with_ai(sql) or [],
                    detected=DetectedObjects(
                        tables=[],
                        joins=[],
                        conditions=[],
                        order_by=[],
                    ),
                    source="ai",
                    message="Generated using AI.",
                )

        ####################################################
        # Rule-based parser
        ####################################################

        query = parser.parse(sql)

        pseudo_code = generator.generate(query)

        explanation = explainer.explain(query)

        ai_bullets = ai_service.explain_with_ai(sql)

        if ai_bullets:
            explanation = ai_bullets

        detected = DetectedObjects(
            tables=[t.name for t in query.tables],
            joins=[
                f"{j.type} JOIN ({j.table} ON {j.condition})"
                for j in query.joins
            ],
            conditions=[query.where] if query.where else [],
            order_by=[
                f'{o.expr} {"DESC" if o.desc else "ASC"}'
                for o in query.order_by
            ],
        )

        return ConvertResponse(
            status="success",
            pseudo_code=pseudo_code,
            explanation=explanation,
            detected=detected,
            source="ai" if ai_bullets else "rule",
        )

    ####################################################
    # Unsupported SQL
    ####################################################

    except UnsupportedSQLError as e:

        logger.info("Unsupported SQL: %s", e)

        ai_pseudo = ai_service.generate_pseudocode_with_ai(sql)

        if ai_pseudo:

            return ConvertResponse(
                status="success",
                pseudo_code=ai_pseudo,
                explanation=ai_service.explain_with_ai(sql) or [],
                message="Rule-based parser doesn't support this yet. Generated using AI.",
                source="ai",
            )

        return ConvertResponse(
            status="error",
            message=str(e),
        )

    ####################################################
    # Any other error
    ####################################################

    except Exception:

        tb = traceback.format_exc()

        logger.error("Conversion failed:\n%s", tb)

        ai_pseudo = ai_service.generate_pseudocode_with_ai(sql)

        if ai_pseudo:

            return ConvertResponse(
                status="success",
                pseudo_code=ai_pseudo,
                explanation=ai_service.explain_with_ai(sql) or [],
                message="Generated using AI after parser failure.",
                source="ai",
            )

        return ConvertResponse(
            status="error",
            message="Could not parse this SQL. Check server logs.",
        )


app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend",
)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")