# BigQuery SQL Generator with AI (ADK BigQuery Tools)

This application allows you to interact with your Google BigQuery database using natural language queries. The AI agent translates your questions into SQL queries and executes them against your BigQuery dataset using Google ADK BigQuery tools for simplified database interactions.

## Architecture

The application follows a simplified architecture with Google ADK BigQuery tools for database interactions:

- **View**: Streamlit frontend
- **Controller**: SQL generation agent
- **Model**: BigQuery client with Google ADK BigQuery tools integration

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy the `.env.example` file to `.env` and set your actual values:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file with your configuration:
   - Set your Google Cloud project ID and dataset ID
   - Add your Gemini API key
   - Adjust other settings as needed

5. **Authenticate with Google Cloud:**
   Make sure you've authenticated with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

## Usage

1. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Run the application:**
   ```bash
   streamlit run main.py
   ```

3. **Open your browser:**
   Visit `http://localhost:8501` to access the application.

4. **Ask questions:**
   Type your questions about the data in the chat input and the AI agent will generate and execute SQL queries using Google ADK BigQuery tools.

## Configuration

All configuration is managed through environment variables in the `.env` file:

- `PROJECT_ID`: Your Google Cloud project ID
- `DATASET_ID`: Your BigQuery dataset ID
- `MODEL_NAME`: The specific Gemini model to use (default: gemini-2.5-flash)
- `TEMPERATURE`: The temperature setting for the LLM (default: 0)
- `GEMINI_API_KEY`: Your Gemini API key
- `SCHEMA_CACHE_TTL`: How long to cache the database schema (in seconds, default: 3600)

## Google ADK BigQuery Tools

This application uses Google ADK (Application Development Kit) BigQuery tools for database interactions, which provides:

- Simplified BigQuery operations through built-in toolset
- Built-in security features with write protection
- Context-aware query execution
- Error handling and logging

The BigQueryToolset is configured with WriteMode.BLOCKED to prevent destructive operations.

## File Structure

- `main.py` - Entry point for the Streamlit application
- `sql_generation_agent.py` - AI agent that generates SQL queries from natural language
- `mcp_client.py` - BigQuery client with ADK BigQuery tools integration
- `bigquery_tools.py` - BigQuery tools leveraging ADK BigQuery tools
- `adk_config.py` - Configuration for Google ADK tools
- `config.py` - Configuration management
- `models.py` - Data models
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create from `.env.example`)