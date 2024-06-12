from dotenv import load_dotenv
import os

load_dotenv()

user_id = os.getenv("USER_ID")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
totp_key = os.getenv("TOTP_KEY")
redirect_url = os.getenv("R-URL")
pin = os.getenv("PIN")
mobile = os.getenv("MOBILE")