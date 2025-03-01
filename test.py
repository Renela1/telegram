
from datetime import datetime, timedelta
now = datetime.utcnow()

# Add 3 months (approx. 90 days)
expiry_time_3 = now + timedelta(days=90)

# Convert to timestamp (milliseconds)
expiry_timestamp_3 = int(expiry_time_3.timestamp() * 1000)

print(expiry_timestamp_3)  # Use this value in your payload

expiry_time_2 = now + timedelta(days=60)

# Convert to timestamp (milliseconds)
expiry_timestamp_2 = int(expiry_time_2.timestamp() * 1000)

print(expiry_timestamp_2)  # Use this value in your payload

expiry_time_1 = now + timedelta(days=30)

# Convert to timestamp (milliseconds)
expiry_timestamp_1 = int(expiry_time_1.timestamp() * 1000)

print(expiry_timestamp_1)  # Use this value in your payload