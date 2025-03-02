# GitHub Copilot Metrics API Aggregation

This Flask application fetches GitHub Copilot metrics data daily and stores it in Azure Blob Storage. It also provides an API to retrieve aggregated metrics data based on date range.

## Features

1. **Data Collection**
   - Automatically fetches GitHub Copilot metrics data every day at 12 PM
   - Stores each day's data as a separate JSON file in Azure Blob Storage
   - For the most recent 3 days, overwrites existing data if present
   - For older data, only stores if not already present

2. **Data Retrieval**
   - Provides an API endpoint to retrieve metrics data for a specific date range
   - Aggregates data from multiple daily files into a single response

## Setup

### Prerequisites

- Python 3.7+
- Azure Storage Account
- GitHub Organization with Copilot enabled
- GitHub Personal Access Token with appropriate permissions

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd github-copilot-metrics-api-aggregation
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   # GitHub API settings
   GITHUB_API_TOKEN=your_github_api_token
   GITHUB_ORG=your_organization_name

   # Azure Blob Storage settings
   AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
   AZURE_CONTAINER_NAME=copilot-metrics

   # App settings
   FLASK_APP=app.py
   FLASK_ENV=development
   PORT=8000
   ```

### Running the Application

Run the application with the following command:

```
python app.py
```

The application will start a Flask server and a background scheduler thread that will fetch metrics data daily at 12 PM.

## API Endpoints

### GET /api/metrics

Retrieve metrics data for a specific date range.

**Parameters:**
- `start_date` (required) - Start date in YYYY-MM-DD format
- `end_date` (required) - End date in YYYY-MM-DD format

**Example:**
```
GET /api/metrics?start_date=2024-06-01&end_date=2024-06-10
```

**Response:**
JSON array containing metrics data for each day in the specified range.

### POST /api/trigger-fetch

Manually trigger a fetch of metrics data.

**Example:**
```
POST /api/trigger-fetch
```

**Response:**
```json
{
  "status": "success",
  "message": "Metrics fetch triggered"
}
```

## Data Format

The metrics data format follows the GitHub Copilot metrics API response format. See `example-response.json` for a sample.