#!/bin/bash

# Log file path
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils.timezone import now
from crm.models import Customer

one_year_ago = now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(last_order_date__lt=one_year_ago)
deleted_count = inactive_customers.count()
inactive_customers.delete()
print(deleted_count)
EOF
)

# Log with timestamp
echo "\$(date): Deleted \$DELETED_COUNT inactive customers" >> \$LOG_FILE
