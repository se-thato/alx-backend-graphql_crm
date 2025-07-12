#!/bin/bash

LOG_FILE="/tmp/customer_cleanup_log.txt"

DELETED_COUNT=$(
./manage.py shell <<EOF
from datetime import timedelta
from django.utils.timezone import now
from crm.models import Customer

one_year_ago = now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(last_order_date__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

echo "$(date): Deleted $DELETED_COUNT inactive customers" >> $LOG_FILE
