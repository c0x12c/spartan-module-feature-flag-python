# Basic Usage Example

## Set Up Environment

- Ensure you have Python installed.
- Install dependencies by navigating to the examples/basic-usage directory and running:

```bash
pip install -r requirements.txt
```

## Run Redis and PostgreSQL

- Make sure you have Redis and PostgreSQL running, or use Docker to spin them up:

```bash
docker run -d -p 6379:6379 redis
docker run -d -p 5432:5432 -e POSTGRES_USER=local -e POSTGRES_PASSWORD=local -e POSTGRES_DB=local postgres
```

- We can also use the prepared docker-compose file to run both services:

```bash
docker-compose -f docker-compose.ci.yml up -d
``` 

## Set Environment Variable

Export the `SLACK_WEBHOOK_URL` environment variable before running the FastAPI app. Replace `your_webhook_url` with your
actual Slack Webhook URL:

```bash
export SLACK_WEBHOOK_URL=your_webhook_url
```

## Run the FastAPI App

Navigate to `examples/basic-usage` and run the application with:

```bash
uvicorn app:app --reload
```

## Access the API

Visit http://127.0.0.1:8000/docs in your browser to interact with the API using Swagger UI.
