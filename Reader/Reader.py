import cv2
import pytesseract
import mysql.connector
import re
from datetime import datetime
import subprocess as s
import pyautogui as p
import time
pytesseract.pytesseract.tesseract_cmd = r'C:\\Tesseract\\tesseract.exe'
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dpsbn",
    database="cars"
)
from selenium import webdriver
import time
dri=webdriver.Chrome()
dri.get('file:///C:/EazePark/Reader/templates/some.html')
import pygetwindow as gw
# Assuming 'Your Window Title' is the title of the window you want to maximize
window = gw.getWindowsWithTitle('Eazepark - Park with Ease - Google Chrome')[0]
window.maximize()
def extract_car_number(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    car_number = pytesseract.image_to_string(thresholded)
    return car_number.strip()
car_number_detected = False
state_patterns = {
    'AN': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Andaman and Nicobar Islands
    'AP': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Andhra Pradesh
    'AR': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Arunachal Pradesh
    'AS': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Assam
    'BR': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Bihar
    'CH': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Chandigarh
    'CT': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Chhattisgarh
    'DD': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Dadra and Nagar Haveli and Daman and Diu
    'DL': r'^[A-Z]{2}\s\d{1,2}\s[A-Z]{1,2}\s\d{4}$',  # Delhi
    'DN': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Dadra and Nagar Haveli and Daman and Diu
    'GA': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Goa
    'GJ': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Gujarat
    'HP': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Himachal Pradesh
    'HR': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Haryana
    'JH': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Jharkhand
    'JK': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Jammu and Kashmir
    'KA': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Karnataka
    'KL': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Kerala
    'LA': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Ladakh
    'LD': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Lakshadweep
    'MH': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Maharashtra
    'ML': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Meghalaya
    'MN': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Manipur
    'MP': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Madhya Pradesh
    'MZ': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Mizoram
    'NL': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Nagaland
    'OD': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Odisha
    'PB': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Punjab
    'PY': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Puducherry
    'RJ': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Rajasthan
    'SK': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Sikkim
    'TN': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Tamil Nadu
    'TR': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Tripura
    'TS': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Telangana
    'UK': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Uttarakhand
    'UP': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Uttar Pradesh
    'WB': r'^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # West Bengal
}
all_states_pattern = '|'.join(state_patterns.values())
all_regex = re.compile(all_states_pattern)
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()    
    if not ret:
        break
    car_number = extract_car_number(frame)
    print("OCR Output:", car_number)
    if car_number and all_regex.match(car_number):
        cursor = db.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO car_no (car_number, timestamp) VALUES (%s, %s)"
        values = (car_number, timestamp)
        cursor.execute(query, values)
        db.commit()
        print("Detected Car Number:", car_number)
        print("Timestamp:", timestamp)
        car_number_detected = True
        if car_number_detected:
            dri.quit()
            from selenium import webdriver
            import time
            driver=webdriver.Chrome()
            driver.get('file:///C:/EazePark/Reader/templates/thank_you.html')
            import pygetwindow as gw
            # Assuming 'Your Window Title' is the title of the window you want to maximize
            window = gw.getWindowsWithTitle('Thank You - Google Chrome')[0]
            window.maximize()
            time.sleep(5)
            driver.quit()
            break
    cv2.imshow('Car Number Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q') or car_number_detected:
        break
cap.release()
cv2.destroyAllWindows()
s.run(["python","C:\\EazePark\\Reader\\Reader.py"]) 