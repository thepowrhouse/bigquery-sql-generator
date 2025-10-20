# BigQuery SQL Generator with AI

This application allows you to interact with your Google BigQuery database using natural language queries. The AI agent translates your questions into SQL queries and executes them against your BigQuery dataset.

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
   - Add your Gemini API key (or OpenAI API key if using OpenAI)
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
   Type your questions about the data in the chat input and the AI agent will generate and execute SQL queries.

## Configuration

All configuration is managed through environment variables in the `.env` file:

- `PROJECT_ID`: Your Google Cloud project ID
- `DATASET_ID`: Your BigQuery dataset ID
- `LLM_PROVIDER`: The LLM provider to use (`google` or `openai`)
- `MODEL_NAME`: The specific model to use
- `TEMPERATURE`: The temperature setting for the LLM
- `GEMINI_API_KEY`: Your Gemini API key (if using Google)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `SCHEMA_CACHE_TTL`: How long to cache the database schema (in seconds)

## LLM Providers

The application supports multiple LLM providers:

### Google Gemini
- Set `LLM_PROVIDER=google`
- Set `MODEL_NAME` to a Gemini model (e.g., `gemini-2.5-flash`)
- Add your `GEMINI_API_KEY`

### OpenAI
- Set `LLM_PROVIDER=openai`
- Set `MODEL_NAME` to an OpenAI model (e.g., `gpt-4-turbo`)
- Add your `OPENAI_API_KEY`

## Troubleshooting

If you encounter any issues, make sure you have all the required dependencies installed:
- `db-dtypes` - Required for BigQuery to work properly with pandas DataFrames
- `google-cloud-bigquery-storage` - Optional but recommended for better performance when fetching large amounts of data from BigQuery

## File Structure

- `main.py` - Entry point for the Streamlit application
- `sql_generation_agent.py` - AI agent that generates SQL queries from natural language
- `bigquery_client.py` - Handles communication with Google BigQuery
- `config.py` - Configuration management
- `models.py` - Data models
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create from `.env.example`)