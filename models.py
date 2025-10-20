from pydantic import BaseModel, Field


class BigQuerySQL(BaseModel):
    """JSON structure for the generated BigQuery SQL query."""
    query: str = Field(description="The syntactically correct BigQuery SQL query, with no other text.")