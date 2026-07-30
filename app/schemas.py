from pydantic import BaseModel


class ConvertRequest(BaseModel):
    sql: str


class DetectedObjects(BaseModel):
    tables: list = []
    joins: list = []
    conditions: list = []
    order_by: list = []


class ConvertResponse(BaseModel):
    status: str                # "success" | "error"
    pseudo_code: str = ""
    explanation: list = []
    detected: DetectedObjects = DetectedObjects()
    message: str = ""
    source: str = "rule"       # "rule" | "ai"
