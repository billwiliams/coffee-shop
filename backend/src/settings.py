from dotenv import load_dotenv
import os
load_dotenv()
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
ALGORITHMS = os.environ.get("ALGORITHMS")
API_AUDIENCE = os.environ.get("API_AUDIENCE")

DATABASE_FILENAME = os.environ.get("DATABASE_FILENAME")
