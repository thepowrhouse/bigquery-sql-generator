import streamlit as st
import pandas as pd
from bigquery_client import BigQueryClient
from sql_generation_agent import SQLGenerationAgent
from config import Config


def initialize_chat_history():
    """Initialize chat history in session state."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


def display_chat_history():
    """Display the chat history."""
    for role, content in st.session_state.chat_history:
        with st.chat_message(role):
            if isinstance(content, pd.DataFrame):
                st.dataframe(content)
            else:
                st.markdown(content)


def add_to_chat_history(role: str, content):
    """Add message to chat history."""
    st.session_state.chat_history.append((role, content))


def handle_query_result(query_result_df: pd.DataFrame):
    """Handle and display query results."""
    with st.chat_message("assistant"):
        if query_result_df is not None:
            if not query_result_df.empty:
                st.success("Query successful! Here are the results:")
                st.dataframe(query_result_df)
                add_to_chat_history("assistant", query_result_df)
            else:
                message = "Query executed successfully, but returned no rows."
                st.warning(message)
                add_to_chat_history("assistant", message)
        else:
            add_to_chat_history("assistant", "That query didn't work. Try another question.")


def main():
    # Page configuration
    st.title("Chat with your BQ Database")
    st.caption("Ask questions about your BigQuery data. An AI agent will generate and execute the SQL.")
    st.divider()

    # Configuration validation
    if not Config.PROJECT_ID or not Config.DATASET_ID:
        st.error("PROJECT_ID and DATASET_ID must be set in the .env file.")
        st.stop()

    # Configuration
    PROJECT_ID = Config.PROJECT_ID
    DATASET_ID = Config.DATASET_ID

    # Initialize components
    bigquery_client = BigQueryClient(PROJECT_ID, DATASET_ID)
    sql_agent = SQLGenerationAgent(bigquery_client.schema_prefix)

    # Fetch schema
    schema_text = bigquery_client.get_schema()
    if not schema_text:
        st.warning("Cannot proceed without a valid BigQuery schema.")
        st.stop()

    # Initialize chat interface
    initialize_chat_history()
    user_question = st.chat_input("Ask a question about your data...")

    # Display chat history
    display_chat_history()

    # Handle user input
    if user_question:
        # Add user question to history and display
        add_to_chat_history("user", user_question)
        with st.chat_message("user"):
            st.markdown(user_question)

        # Generate and execute SQL
        generated_sql = sql_agent.generate_sql_query(user_question, schema_text)
        if generated_sql:
            query_result_df = bigquery_client.execute_query(generated_sql)
            handle_query_result(query_result_df)


if __name__ == "__main__":
    main()