from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import schedule
import time
import threading
from azure.storage.blob import BlobServiceClient, ContentSettings
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress Azure Storage logging
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

app = Flask(__name__)

# Environment variables
GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')
GITHUB_ORG = os.getenv('GITHUB_ORG')
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

# Initialize Azure Blob Storage client
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
    # Create container if it doesn't exist
    if not container_client.exists():
        container_client.create_container()
        logger.info(f"Container {AZURE_CONTAINER_NAME} created")
except Exception as e:
    logger.error(f"Error initializing Azure Blob Storage: {str(e)}")

def fetch_copilot_metrics():
    """
    Fetch Copilot metrics from GitHub API and store in Azure Blob Storage
    """
    try:
        logger.info("Fetching Copilot metrics...")
        
        # GitHub API headers
        headers = {
            "Authorization": f"token {GITHUB_API_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # API endpoint
        endpoint = f"https://api.github.com/orgs/{GITHUB_ORG}/copilot/metrics"
        
        # Make API request
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            metrics_data = response.json()
            
            # Process each data block by date
            for data_block in metrics_data:
                if "date" in data_block:
                    date_str = data_block["date"]
                    blob_name = f"{date_str}.json"
                    
                    # Check if we should overwrite the data
                    current_date = datetime.now().date()
                    data_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    days_difference = (current_date - data_date).days
                    
                    # Only upload if it's within the last 3 days or doesn't exist yet
                    if days_difference <= 3:
                        upload_to_blob_storage(blob_name, json.dumps(data_block))
                        logger.info(f"Uploaded metrics data for {date_str}")
                    else:
                        # Check if file already exists
                        blob_client = container_client.get_blob_client(blob_name)
                        if not blob_client.exists():
                            upload_to_blob_storage(blob_name, json.dumps(data_block))
                            logger.info(f"Uploaded metrics data for {date_str} (new data)")
                        else:
                            logger.info(f"Skipped uploading metrics data for {date_str} (older data)")
        else:
            logger.error(f"Failed to fetch metrics data: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error in fetch_copilot_metrics: {str(e)}")

def upload_to_blob_storage(blob_name, content):
    """
    Upload content to Azure Blob Storage
    """
    try:
        content_settings = ContentSettings(content_type='application/json')
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(content, overwrite=True, content_settings=content_settings)
        return True
    except Exception as e:
        logger.error(f"Error uploading to blob storage: {str(e)}")
        return False

def schedule_metrics_fetch():
    """
    Schedule metrics fetch to run at 12:00 AM daily
    """
    schedule.every().day.at("00:00").do(fetch_copilot_metrics)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# if start_date and end_date parameters are missing, then return all data
# if start_date and end_date are provided, then return data between those dates
# if start_date is provided while end_date is not provided, then return data from that date to today
# if end_date is provided while start_date is not provided, then return data from the beginning to that date
@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get metrics data for a given date range:
    - No dates: return all data
    - start_date only: from start_date to today
    - end_date only: from earliest data to end_date
    - both dates: data between dates
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        print(f"Received request for metrics from {start_date} to {end_date}")

        today = datetime.now().date()
        
        # Set end date
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                if end.date() > today:
                    end = datetime.combine(today, datetime.min.time())
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        else:
            end = datetime.combine(today, datetime.min.time())
        
        # Set start date
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                if start.date() > today:
                    return jsonify({"error": "start_date cannot be in the future"}), 400
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        else:
            # Try to find earliest data by listing all blobs
            try:
                blobs = list(container_client.list_blobs())
                if not blobs:
                    return jsonify([])
                earliest_blob = min(blobs, key=lambda b: b.name)
                start = datetime.strptime(earliest_blob.name.split('.')[0], "%Y-%m-%d")
            except Exception as e:
                logger.error(f"Error finding earliest date: {str(e)}")
                start = end - timedelta(days=30)  # Default to last 30 days
        
        if end < start:
            return jsonify({"error": "end_date must be after start_date"}), 400
        
        print(f"Fetching metrics from {start} to {end}")
        
        # Get all blobs between start and end dates
        aggregated_data = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            blob_name = f"{date_str}.json"
            
            try:
                blob_client = container_client.get_blob_client(blob_name)
                if blob_client.exists():
                    blob_data = blob_client.download_blob()
                    content = blob_data.readall()
                    metric_data = json.loads(content)
                    aggregated_data.append(metric_data)
                else:
                    logger.info(f"Blob {blob_name} not found")
            except Exception as e:
                logger.error(f"Error retrieving blob {blob_name}: {str(e)}")
            
            current_date += timedelta(days=1)
        
        return jsonify(aggregated_data)
    except Exception as e:
        logger.error(f"Error in get_metrics: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/trigger-fetch', methods=['POST'])
def trigger_fetch():
    """
    Manually trigger metrics fetch
    """
    try:
        fetch_copilot_metrics()
        return jsonify({"status": "success", "message": "Metrics fetch triggered"})
    except Exception as e:
        logger.error(f"Error triggering metrics fetch: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_metrics_fetch, daemon=True)
    scheduler_thread.start()
    
    # Start Flask app
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)