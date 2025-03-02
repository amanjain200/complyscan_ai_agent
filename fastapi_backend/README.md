### Backend

1. Navigate to the backend folder and install the Python dependencies using Poetry:

    ```bash
    cd fastapi_backend
    poetry install
    ```

2. Create a `.env` file in the backend folder copying the `.env.example` file provided and set the required environment variable:
    - `OPENAI_API_KEY`: Your OpenAI API key.
  
3. The application uses Pydantic Settings for configuration management. You can adjust the configuration defaults in `fastapi_backend/app/config.py`, or set the configuration variables directly using environment variables.

4. Start the backend server in this way:

    ```bash
    cd fastapi_backend
    poetry shell
    fastapi dev app/main.py
    ```