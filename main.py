from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os
import shutil
import retrying


def load_env_vars():
    load_dotenv()
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_SID = os.getenv('TWILIO_SID')
    IPHONE_SEARCHED = os.getenv('IPHONE_SEARCHED')
    
    if not TWILIO_AUTH_TOKEN or not TWILIO_SID or not IPHONE_SEARCHED:
        raise Exception(
            'Please provide the following environment variables: TWILIO_AUTH_TOKEN, TWILIO_SID, IPHONE_SEARCHED'
        )
    
    return TWILIO_AUTH_TOKEN, TWILIO_SID, IPHONE_SEARCHED


TWILIO_AUTH_TOKEN, TWILIO_SID, IPHONE_SEARCHED = load_env_vars()

def get_sms_body(iphone_searched, available_iphones):
    body = f'The {iphone_searched} is available in the following options: \n'
    for iphone in available_iphones:
        body += f'- {iphone}\n'
    return body

@retrying.retry(wait_random_min=1000, wait_random_max=10000)
def check_iphone_available(iphone_searched, driver):
    url = "https://www.apple.com/shop/refurbished/iphone/iphone-14-pro-max"

    driver.get(url)
    iphone_items = driver.find_elements(By.CLASS_NAME, 'rf-refurb-producttile')
    available_iphones = []
    for iphone_item in iphone_items:
        title_link = iphone_item.find_element(By.CLASS_NAME, 'rf-refurb-producttile-link')
        title_text = title_link.text
        if iphone_searched.lower() in title_text.lower():
            available_iphones.append(title_text)

    return available_iphones

def notify_iphone_available(sms_body):
    account_sid = TWILIO_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
    messaging_service_sid='MGd43a853886bf48f4d911cdfb0dfbffc4',
    body=sms_body,
    to='+584147027293'
    )
    print(message.sid)



def main():
    while True:
        if os.path.isdir('custom_temp_dir'):
            shutil.rmtree('custom_temp_dir')
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--remote-debugging-port=9222")
        custom_temp_dir = os.path.join(os.getcwd(), "custom_temp_dir")
        if not os.path.exists(custom_temp_dir):
            os.makedirs(custom_temp_dir)
        options.add_argument(f"--user-data-dir={custom_temp_dir}")
        driver = webdriver.Chrome(options=options)
        available_iphones = check_iphone_available(IPHONE_SEARCHED, driver)
            
        if available_iphones:
            print(f'The {IPHONE_SEARCHED} is available in the following options: ')
            for iphone in available_iphones:
                print(iphone)
            sms_body = get_sms_body(IPHONE_SEARCHED, available_iphones)
            notify_iphone_available(sms_body)
            time.sleep(1800)
            
        else:
            print(f'The {IPHONE_SEARCHED} is not available')
        
        driver.quit()
        time.sleep(30)
    
            



if __name__ == "__main__":
    main()