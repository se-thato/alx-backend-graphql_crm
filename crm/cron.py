from datetime import datetime
import requests

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"

    # Append the heartbeat to the log file
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message + "\n")

    # Optional: Query GraphQL hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            print("GraphQL 'hello' query success:", response.json())
        else:
            print("GraphQL 'hello' query failed:", response.status_code)
    except Exception as e:
        print("Error querying GraphQL hello:", str(e))




def update_low_stock():
    LOG_FILE = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mutation = """
    mutation {
      updateLowStockProducts {
        success
        updatedProducts
      }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": mutation},
            timeout=10
        )
        data = response.json()

        if "errors" in data:
            log_msg = f"{timestamp} - ERROR: {data['errors']}"
        else:
            updated = data["data"]["updateLowStockProducts"]["updatedProducts"]
            log_msg = f"{timestamp} - Updated Products:\n" + "\n".join(updated)

    except Exception as e:
        log_msg = f"{timestamp} - EXCEPTION: {str(e)}"

    # Append to log file
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")
