from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"

    # Append the heartbeat to the log file
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message + "\n")

    # Optional: Query GraphQL hello field using gql
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        result = client.execute(query)
        print("GraphQL 'hello' query success:", result)
    except Exception as e:
        print("Error querying GraphQL hello:", str(e))


def update_low_stock():
    LOG_FILE = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mutation = gql("""
    mutation {
      updateLowStockProducts {
        success
        updatedProducts
      }
    }
    """)

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        data = client.execute(mutation)

        if "updateLowStockProducts" in data:
            updated = data["updateLowStockProducts"].get("updatedProducts", [])
            log_msg = f"{timestamp} - Updated Products:\n" + "\n".join(updated)
        else:
            log_msg = f"{timestamp} - ERROR: Unexpected response format: {data}"

    except Exception as e:
        log_msg = f"{timestamp} - EXCEPTION: {str(e)}"

    # Append to log file
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")