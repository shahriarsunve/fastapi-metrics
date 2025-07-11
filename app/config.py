import os
from dotenv import load_dotenv

load_dotenv()  # reads .env

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

# any other config (e.g. Prometheus buckets, collection intervals)
