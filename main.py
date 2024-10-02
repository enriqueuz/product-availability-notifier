from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os

load_dotenv()
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_SID = os.getenv('TWILIO_SID')

def get_sms_body(iphone_searched, available_iphones):
    body = f'The {iphone_searched} is available in the following options: \n'
    for iphone in available_iphones:
        body += f'- {iphone}\n'
    return body

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
            os.rmdir('custom_temp_dir')
        
        iphone_searched = 'iPhone 14 Pro Max 128GB'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument("--remote-debugging-port=9222")
        custom_temp_dir = os.path.join(os.getcwd(), "custom_temp_dir")
        if not os.path.exists(custom_temp_dir):
            os.makedirs(custom_temp_dir)
        options.add_argument(f"--user-data-dir={custom_temp_dir}")
        driver = webdriver.Chrome(options=options)
        available_iphones = check_iphone_available(iphone_searched, driver)
            
        if available_iphones:
            print(f'The {iphone_searched} is available in the following options: ')
            for iphone in available_iphones:
                print(iphone)
            sms_body = get_sms_body(iphone_searched, available_iphones)
            notify_iphone_available(sms_body)
            time.sleep(1800)
            
        else:
            print(f'The {iphone_searched} is not available')
        
        driver.quit()
        time.sleep(30)
    
            



if __name__ == "__main__":
    main()