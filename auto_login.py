import logging
from utils.config import user_id, totp_key, api_key, api_secret, redirect_url, pin, mobile
import urllib.parse as urlparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pyotp import TOTP
import requests as rq

# Constants
REQUEST_TOKEN_FILE = 'request_token.txt'
ACCESS_TOKEN_FILE = 'access_token.txt'
AUTH_URL = f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={api_key}&redirect_uri={redirect_url}'
SELENIUM_TIMEOUT = 2
SLEEP_INTERVAL = 1

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def navigate_to_auth(driver):
    logging.info('Navigating to authentication URL...')
    driver.get(AUTH_URL)
    sleep(SLEEP_INTERVAL)

def enter_mobile_number(driver):
    logging.info('Entering mobile number...')
    wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mobileNum"]'))).send_keys(mobile)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="getOtp"]'))).click()

def enter_otp(driver):
    logging.info('Entering OTP...')
    totp = TOTP(totp_key).now()
    sleep(SLEEP_INTERVAL)
    wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="otpNum"]'))).send_keys(totp)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="continueBtn"]'))).click()

def enter_pin(driver):
    logging.info('Entering PIN...')
    sleep(SLEEP_INTERVAL)
    wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="pinCode"]'))).send_keys(pin)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pinContinueBtn"]'))).click()

def fetch_authorization_code(driver):
    logging.info('Fetching authorization code...')
    sleep(SLEEP_INTERVAL)
    token_url = driver.current_url
    parsed = urlparse.urlparse(token_url)
    return urlparse.parse_qs(parsed.query)['code'][0]

def exchange_code_for_token(code):
    url = 'https://api.upstox.com/v2/login/authorization/token'
    headers = {
        'accept': 'application/json',
        'Api-Version': '2.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'code': code,
        'client_id': api_key,
        'client_secret': api_secret,
        'redirect_uri': redirect_url,
        'grant_type': 'authorization_code'
    }
    logging.info('Exchanging code for token...')
    response = rq.post(url, headers=headers, data=data)
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
    logging.info(f'Auth URL: {AUTH_URL}')
    logging.info(f'Redirect URI: {redirect_url}')

    driver = get_webdriver()
    try:
        navigate_to_auth(driver)
        enter_mobile_number(driver)
        enter_otp(driver)
        enter_pin(driver)
        code = fetch_authorization_code(driver)
        token_data = exchange_code_for_token(code)
        save_access_token(token_data)
        logging.info('Auto Login Completed.')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()


# this def is used to run the auto_login function directly
if __name__ == '__main__':
    auto_login()
