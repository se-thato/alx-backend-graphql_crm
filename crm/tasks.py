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
        response = requests.post("http://localhost:8000/graphql", json={"query": query})
        data = response.json()["data"]

        customer_count = data["allCustomers"]["totalCount"]
        order_count = data["allOrders"]["totalCount"]
        total_revenue = sum(
            float(edge["node"]["totalAmount"]) for edge in data["allOrders"]["edges"]
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Report: {customer_count} customers, {order_count} orders, {total_revenue:.2f} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(log_entry)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{datetime.now()} - ERROR: {str(e)}\n")
