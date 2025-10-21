import streamlit as st
import pandas as pd
from typing import Optional, List, Tuple, Dict
from bigquery_tools import get_dataset_schema, execute_query_with_context
import re


class BigQueryClient:
    """BigQuery client for database operations using Google ADK tools."""

    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.schema_prefix = f"`{project_id}.{dataset_id}."

    def get_schema(self) -> str:
        """Get the database schema using ADK BigQuery tools."""
        st.write("Fetching database schema...")
        return get_dataset_schema(self.dataset_id)

    def get_table_list(self) -> List[str]:
        """Get list of available tables in the dataset."""
        # Use direct BigQuery client to get table list
        from google.cloud import bigquery
        from adk_config import config
        
        try:
            client = bigquery.Client(project=config.project_id)
            dataset_ref = client.dataset(self.dataset_id)
            tables = list(client.list_tables(dataset_ref))
            return [table.table_id for table in tables]
        except Exception as e:
            st.error(f"Error fetching table list: {e}")
            return []

    def extract_tables_from_schema(self, schema_text: str) -> List[str]:
        """Extract table names from schema text."""
        # Look for table names in the schema text
        table_pattern = r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        table_matches = re.findall(table_pattern, schema_text)
        return table_matches

    def validate_table_name(self, sql_query: str) -> Tuple[bool, str]:
        """Validate if table names in SQL query exist in the dataset.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Extract table names from SQL query
        # This is a simplified regex - in production, you might want to use a proper SQL parser
        table_pattern = rf'`?{self.project_id}\.{self.dataset_id}\.([a-zA-Z_][a-zA-Z0-9_]*)`?'
        table_matches = re.findall(table_pattern, sql_query)
        
        if not table_matches:
            # Try to find table names without full path
            simple_table_pattern = r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            simple_matches = re.findall(simple_table_pattern, sql_query, re.IGNORECASE)
            if simple_matches:
                return False, f"Table names should include full path. Available tables: {', '.join(self.get_table_list())}"
            return False, "No valid table names found in query"
        
        # Get actual table list
        actual_tables = self.get_table_list()
        
        # Check if all tables in query exist
        for table_name in table_matches:
            if table_name not in actual_tables:
                return False, f"Table '{table_name}' does not exist. Available tables: {', '.join(actual_tables)}"
        
        return True, ""

    def execute_query(self, sql_query: str) -> Optional[pd.DataFrame]:
        """Execute a SQL query using ADK BigQuery tools."""
        if not sql_query:
            return None

        # Validate table names before execution
        is_valid, error_message = self.validate_table_name(sql_query)
        if not is_valid:
            st.error(f"Table validation failed: {error_message}")
            return None

        st.info(f"Executing Query: ```sql\n{sql_query}\n```")
        with st.spinner("Running query against BigQuery..."):
            result = execute_query_with_context(sql_query)
            
            if result.get("status") == "success":
                st.write(f"Query executed successfully. Returned {result.get('row_count', 0)} rows.")
                st.write(f"Processed {result.get('bytes_processed', 0)} bytes.")
                
                # Convert to DataFrame
                data = result.get("data", [])
                if data:
                    df = pd.DataFrame(data)
                    return df
                else:
                    return pd.DataFrame()
            else:
                error = result.get("error", "Unknown error")
                st.error(
                    f"BigQuery Execution Failed. The query was invalid or timed out. "
                    f"Please try to rephrase your question. Error: {error}"
                )
                return None