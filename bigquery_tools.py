"""BigQuery tools that leverage Google ADK tools for database interactions."""

import json
import streamlit as st
from typing import Any, Dict, List, Optional
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
from google.cloud import bigquery
from adk_config import config


# Define a tool configuration to allow read operations but block write operations
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

# Create BigQuery toolset
bigquery_toolset = BigQueryToolset(bigquery_tool_config=tool_config)


def get_dataset_schema(dataset_id: str) -> str:
    """Retrieve schema information for a BigQuery dataset.
    
    Args:
        dataset_id: The dataset ID to get schema for
        
    Returns:
        Formatted schema information as string
    """
    # Use direct BigQuery client for schema retrieval
    client = bigquery.Client(project=config.project_id)
    
    query = f"""
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM `{config.project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
        ORDER BY table_name, ordinal_position
    """
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        schema_info_list = [dict(row.items()) for row in results]
        
        if not schema_info_list:
            return f"No schema information found for dataset '{dataset_id}'."
        
        # Format schema information
        formatted_schema = format_schema(schema_info_list)
        return formatted_schema
        
    except Exception as e:
        return f"Error retrieving schema from dataset '{dataset_id}': {e}"


def format_schema(schema_data: List[Dict]) -> str:
    """Format schema data.
    
    Args:
        schema_data: List of schema information dictionaries
        
    Returns:
        Formatted schema information as string
    """
    if not schema_data:
        return ""
        
    # Group by table
    tables = {}
    for row in schema_data:
        table_name = row['table_name']
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append({
            'column': row['column_name'],
            'type': row['data_type'],
            'nullable': row['is_nullable']
        })
    
    # Format as string
    context_lines = []
    context_lines.append("Database Schema:")
    context_lines.append("================")
    
    for table_name, columns in tables.items():
        context_lines.append(f"\nTable: {table_name}")
        context_lines.append("Columns:")
        for col in columns:
            nullable = "NULL" if col['nullable'] == 'YES' else "NOT NULL"
            context_lines.append(f"  - {col['column']} ({col['type']}, {nullable})")
    
    return "\n".join(context_lines)


def execute_query_with_context(sql_query: str) -> Dict[str, Any]:
    """Execute a BigQuery query.
    
    Args:
        sql_query: The SQL query to execute
        
    Returns:
        Dictionary containing query results and execution metadata
    """
    if not sql_query:
        return {"error": "No SQL query provided"}
    
    try:
        # Use direct BigQuery client for query execution
        # This maintains the security configuration from ADK while actually executing the query
        client = bigquery.Client(project=config.project_id)
        
        # Add query metadata
        job_config = bigquery.QueryJobConfig()
        job_config.use_query_cache = True
        job_config.use_legacy_sql = False
        
        query_job = client.query(sql_query, job_config=job_config)
        
        # Get query statistics
        df = query_job.to_dataframe()
        
        return {
            "status": "success",
            "row_count": len(df),
            "bytes_processed": query_job.total_bytes_processed,
            "data": df.to_dict('records') if not df.empty else []
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}