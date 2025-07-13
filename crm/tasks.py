from celery import shared_task
from datetime import datetime
import requests

@shared_task
def generate_crm_report():
    query = """
    query {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    """
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )
        data = response.json()["data"]

        customer_count = data["allCustomers"]["totalCount"]
        orders = data["allOrders"]
        order_count = orders["totalCount"]
        total_revenue = sum(
            float(edge["node"]["totalAmount"]) for edge in orders["edges"]
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: {customer_count} customers, {order_count} orders, {total_revenue:.2f} revenue"

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(log_line + "\n")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(f"ERROR: {e}\n")
