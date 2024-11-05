import os
from dotenv import load_dotenv 

load_dotenv()

DOMAIN = os.environ.get('DOMAIN', 'http://127.0.0.1:8080')
PORT = os.environ.get('PORT', 8000)
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'Email_here')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'Password')
