import requests
from pyotp import TOTP
import logging
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

USER_ID='298738'
API_KEY='c69b3814-0a8f-4274-9283-cd0bdff674d8'
API_SECRET='v5zgx41g62'
REDIRECT_URI = 'https://127.0.0.1/'
TOTP_KEY='Z2RCAR2OZIX5GOVR436OHVRESYNFN3U'
PIN='444444'
MOBILE='8897877531'

ACCESS_TOKEN_FILE = 'access_token.txt'
AUTH_URL = f'https://api.upstox.com/v2/login/authorization/dialog?client_id={API_KEY}&redirect_uri={REDIRECT_URI}'
SELENIUM_TIMEOUT = 2  # Increased timeout to 30 seconds
SLEEP_INTERVAL = 1     # Increased sleep interval to 2 seconds


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')  # Uncomment this line to run headless
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def navigate_to_auth(driver):
    logging.info('Navigating to authentication URL...')
    driver.get(AUTH_URL)
    sleep(SLEEP_INTERVAL)

def enter_mobile_number(driver):
    logging.info('Entering mobile number...')
    try:
        wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
        mobile_input = wait.until(EC.presence_of_element_located((By.ID, 'mobileNum')))
        mobile_input.send_keys(MOBILE)
        get_otp_button = wait.until(EC.element_to_be_clickable((By.ID, 'getOtp')))
        get_otp_button.click()
    except Exception as e:
        logging.error(f'Error entering mobile number: {e}')
        raise

def enter_otp(driver):
    logging.info('Entering OTP...')
    try:
      totp = TOTP(TOTP_KEY).now()
      sleep(SLEEP_INTERVAL)
      wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
      wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="otpNum"]'))).send_keys(totp)
      wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="continueBtn"]'))).click()

    except Exception as e:
        logging.error(f'Error entering OTP: {e}')
        raise

def enter_pin(driver):
    logging.info('Entering PIN...')
    try:

      sleep(SLEEP_INTERVAL)
      wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
      wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="pinCode"]'))).send_keys(pin)
      wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pinContinueBtn"]'))).click()

    except Exception as e:
        logging.error(f'Error entering PIN: {e}')
        raise

def fetch_authorization_code(driver):
    logging.info('Fetching authorization code...')
    try:
        sleep(SLEEP_INTERVAL)
        token_url = driver.current_url
        parsed = urlparse.urlparse(token_url)
        return urlparse.parse_qs(parsed.query).get('code', [None])[0]
    except Exception as e:
        logging.error(f'Error fetching authorization code: {e}')
        raise

def exchange_code_for_token(code):
    url = 'https://api.upstox.com/v2/login/authorization/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    data = {
        'code': code,
        'client_id': API_KEY,
        'client_secret': API_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    logging.info('Exchanging authorization code for access token...')
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def save_access_token(data):
    if 'access_token' in data:
        with open(ACCESS_TOKEN_FILE, 'w') as file:
            file.write(data['access_token'])
        logging.info('Access token saved successfully.')
    else:
        logging.error(f"Error in response data: {data}")

def auto_login():
    logging.info('Auto Login Started...')
    driver = get_webdriver()
    try:
        navigate_to_auth(driver)
        enter_mobile_number(driver)
        enter_otp(driver)
        enter_pin(driver)
        code = fetch_authorization_code(driver)
        if not code:
            raise Exception("Authorization code not found in the response.")
        token_data = exchange_code_for_token(code)
        save_access_token(token_data)
        logging.info('Auto Login Completed.')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
# Uncomment the following line to run the auto_login function directly
if __name__ == '__main__':
    auto_login()