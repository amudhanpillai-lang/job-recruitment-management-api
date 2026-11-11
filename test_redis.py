
from app.core.redis import redis_client
import json

jobs_data = []

result = redis_client.setex(
    "jobs:all",
    300,
    json.dumps(jobs_data)
)

print("SETEX result:", result)
print("Stored value:", redis_client.get("jobs:all"))
print("Key exists:", redis_client.exists("jobs:all"))
print("Remaining TTL:", redis_client.ttl("jobs:all"))
