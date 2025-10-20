import streamlit as st
from google.cloud import bigquery
import pandas as pd
from typing import Optional
from config import Config


class BigQueryClient:
    """Handles BigQuery database operations."""

    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        # Fixed the schema prefix - removed the duplicate IndianAPI
        self.schema_prefix = f"`{project_id}.{dataset_id}."
        self.client = self._initialize_client()

    def _initialize_client(self) -> Optional[bigquery.Client]:
        """Initialize BigQuery client with error handling."""
        try:
            return bigquery.Client(project=self.project_id)
        except Exception as e:
            st.error(
                f"Failed to initialize BigQuery client. Ensure you are authenticated "
                f"and have set the correct project ID. Error: {e}"
            )
            st.stop()
            return None

    def get_schema(self) -> str:
        """Fetches table, column names, and data types from BigQuery."""
        return get_bigquery_schema_cached(self.client, self.project_id, self.dataset_id)

    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Runs the generated SQL query against BigQuery."""
        if not sql_query:
            return None

        st.info(f"Executing Query: ```sql\n{sql_query}\n```")
        with st.spinner("Running query against BigQuery..."):
            try:
                df = self.client.query(sql_query).to_dataframe()
                return df
            except Exception as e:
                st.error(
                    f"BigQuery Execution Failed. The query was invalid or timed out. "
                    f"Please try to rephrase your question. Error: {e}"
                )
                return None


@st.cache_data(ttl=Config.SCHEMA_CACHE_TTL)
def get_bigquery_schema_cached(_client, project_id: str, dataset_id: str) -> str:
    """Cached function to fetch table, column names, and data types from BigQuery."""
    st.write("Fetching database schema...")
    sql_query = f"""
    SELECT 
      table_name,
      column_name,
      data_type
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    """
    try:
        query_job = _client.query(sql_query)
        schema_data = [dict(row) for row in query_job]
        return "\n".join([str(item) for item in schema_data])
    except Exception as e:
        st.error(f"Could not fetch schema from BigQuery. Error: {e}")
        return ""