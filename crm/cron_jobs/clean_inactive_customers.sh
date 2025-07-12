#!/bin/bash

# Get the absolute path of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Go to the root of the Django project (assumed to be 2 levels up)
cd "$SCRIPT_DIR/../.."

# Check if we're in the right place (look for manage.py)
if [ ! -f "manage.py" ]; then
    echo "manage.py not found. Are you in the correct directory?"
    exit 1
fi

# Log file
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run the cleanup via Django shell
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

# Log the result with timestamp
echo "$(date): Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"

