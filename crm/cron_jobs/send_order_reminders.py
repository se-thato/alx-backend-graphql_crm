#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import logging

# Setup log file
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

# GraphQL endpoint setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# Calculate date range: orders within the last 7 days
seven_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()

# GraphQL query (you may need to adjust field names)
query = gql(f"""
query {{
  allOrders(orderDate_Gte: "{seven_days_ago}") {{
    edges {{
      node {{
        id
        customer {{
          email
        }}
        orderDate
      }}
    }}
  }}
}}
""")

# Run the query and log the results
try:
    result = client.execute(query)
    orders = result["allOrders"]["edges"]

    for order in orders:
        order_id = order["node"]["id"]
        email = order["node"]["customer"]["email"]
        log_msg = f"{datetime.now()}: Order ID {order_id}, Email {email}"
        logging.info(log_msg)

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"{datetime.now()}: Error - {e}")
    print("Failed to process order reminders.")
