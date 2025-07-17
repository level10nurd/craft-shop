import os
from dotenv import load_dotenv
from lightspeed_x import LightspeedX

load_dotenv()

lightspeed = LightspeedX(
    base_url=os.getenv("base_url"),
    bearer_token=os.getenv("bearer_token"),
)

response = lightspeed.get("2.0/sales/ed290b30-16d8-8911-11ee-0edea74af4f9")
print(response)