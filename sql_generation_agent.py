import streamlit as st
import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from models import BigQuerySQL
from config import Config


class SQLGenerationAgent:
    """Handles AI-powered SQL query generation using configurable LLMs."""

    def __init__(self, schema_prefix: str):
        self.schema_prefix = schema_prefix
        self.model_name = Config.MODEL_NAME or "gemini-2.5-flash"  # Default model
        self.temperature = Config.TEMPERATURE
        self.provider = Config.LLM_PROVIDER or "google"  # Default provider

        # Validate configuration
        if not self.model_name:
            st.error("MODEL_NAME must be set in the .env file.")
            st.stop()
        
        if not self.provider:
            st.error("LLM_PROVIDER must be set in the .env file.")
            st.stop()

    def generate_sql_query(self, user_question: str, schema_text: str) -> Optional[str]:
        """Uses LangChain and a configurable LLM to generate a SQL query."""
        if not self._validate_api_key():
            return None

        # Initialize the appropriate LLM based on configuration
        llm = self._initialize_llm()

        system_message = self._create_system_message()
        human_message = self._create_human_message(user_question, schema_text)

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            HumanMessage(content=human_message),
        ])

        parser = JsonOutputParser(pydantic_object=BigQuerySQL)
        chain = prompt | llm | parser

        return self._execute_chain(chain)

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on the configured provider."""
        if self.provider == "google":
            if not Config.GEMINI_API_KEY:
                st.error("GEMINI_API_KEY must be set in the .env file for Google provider.")
                st.stop()
            return ChatGoogleGenerativeAI(
                model=self.model_name, 
                temperature=self.temperature,
                google_api_key=Config.GEMINI_API_KEY,
                transport="rest"
            )
        elif self.provider == "openai":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                st.error("OPENAI_API_KEY must be set in the .env file for OpenAI provider.")
                st.stop()
            # type: ignore
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=openai_api_key  # type: ignore
            )
        else:
            st.error(f"Unsupported LLM provider: {self.provider}. Supported providers are 'google' and 'openai'.")
            st.stop()

    def _validate_api_key(self) -> bool:
        """Validate that the required API key is set based on the provider."""
        if self.provider == "google":
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                st.error("GEMINI_API_KEY must be set in the .env file.")
                return False
            # Check if API key has the expected format (AIza followed by 33 characters)
            if not api_key.startswith("AIza") or len(api_key) < 30:
                st.error("GEMINI_API_KEY appears to be invalid.")
                return False
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("OPENAI_API_KEY must be set in the .env file.")
                return False
        else:
            st.error(f"Unsupported LLM provider: {self.provider}")
            return False
        return True

    def _create_system_message(self) -> str:
        """Create the system message for the AI agent."""
        return f"""
        You are a helpful AI assistant that writes valid SQL queries for databases.
        You will be given:
        - A user's question.
        - A list of available table names, column names, and their data types (the schema).
        Your task is to:
        1. Write a syntactically correct SQL query that best answers the user's question.
        2. Only use table and column names that appear in the provided schema — do not guess or invent names.
        3. Make the best possible guess about which table and columns to use *from the given list only*.
        4. **Crucially, ensure the table name is correctly formatted with the full schema prefix**: 
           For example, instead of `SELECT * FROM table_name`, use 
           `SELECT * FROM {self.schema_prefix}table_name`
        5. Double-check that the table name you use actually exists in the schema provided.
        6. Return your output in a strict JSON format with one key: "query".
        ⚠️ Do NOT invent table or column names.
        ⚠️ If a relevant field does not exist, make the best effort to answer with what's available, or omit that part.
        ⚠️ Do NOT include any explanation, notes, or comments — only the final JSON.
        """

    def _create_human_message(self, user_question: str, schema_text: str) -> str:
        """Create the human message containing the user question and schema."""
        return f"""
        User Question: {user_question}
        Available Table and Column Schema: 
        {schema_text}
        """

    def _execute_chain(self, chain) -> Optional[str]:
        """Execute the LangChain chain and return the generated SQL query."""
        with st.spinner("Generating SQL query..."):
            try:
                response: Dict[str, Any] = chain.invoke({})
                return response.get("query")
            except Exception as e:
                st.error(f"AI Agent failed to generate a valid SQL query. Error: {e}")
                return None