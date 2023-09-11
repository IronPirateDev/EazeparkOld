'''import mysql.connector as ms
import pytesseract
import cv2
import re
import time
import datetime
pytesseract.pytesseract.tesseract_cmd = r'C:\\Tesseract\\tesseract.exe'
db=ms.connect(
    host='localhost',
    user='root',
    password='dpsbn',
    database='cars'
)
dbno=[]
def extract_car_number(frame):
    # Convert the frame to grayscale for better OCR results
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to enhance text visibility
    thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Perform OCR using Tesseract
    car_number = pytesseract.image_to_string(thresholded)

    return car_number.strip()

def calculate_charges(timestamp):
    # Calculate the time difference between the current timestamp and the given timestamp
    current_time = datetime.now()
    time_difference = current_time - timestamp

    # Calculate the total number of hours (rounded up)
    total_hours = int((time_difference.total_seconds() + 3599) / 3600)

    # Calculate the charges based on the rate: 2 hours = 30 Rs, additional hour = 10 Rs
    base_charge = 30
    additional_charge_per_hour = 10
    total_charge = base_charge + max(total_hours - 2, 0) * additional_charge_per_hour

    return total_hours, total_charge

car_number_detected = False

# Define a dictionary with state codes and their corresponding regular expressions
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

# Create combined patterns for validation
all_states_pattern = '|'.join(state_patterns.values())
all_regex = re.compile(all_states_pattern)

# Open a video capture object (0 indicates the default camera)
# Open a video capture object (0 indicates the default camera)
#cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # Display the frame in a window
    cv2.imshow('Camera Preview', frame)
    
    # Extract car number from the frame
    car_number = extract_car_number(frame)
    
    # Print the OCR output for debugging
    print("OCR Output:", car_number)
car_number=input("Enter")
# If car number is detected and valid, save to the 'car_no' table and calculate charges
if car_number and all_regex.match(car_number):
    cursor=db.cursor()
    cursor.execute('select * from car_no')
    a = cursor.fetchall()
    # Break out of the loop once a car number is detected
    #break
    
    # Wait for a key event and check if it's the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and destroy all windows
cap.release()
cv2.destroyAllWindows()
for i in a:
    for j in i:
        print(j)
        dbno.append(j)
        break
if car_number not in dbno:
    print('Retrying')'''
import qrcode
from urllib.parse import quote

def generate_qr_code(car_number, money):
    # Encode car number and money as URL parameters
    car_number_encoded = quote(car_number)
    money_encoded = quote(money)
    url = f'https://eazepark.repl.co/?car_number={car_number_encoded}&money={money_encoded}'

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to file
    img.save('qr_code.png')

if __name__ == "__main__":
    car_number = "KA 04 MG 2455"
    money = "30"
    generate_qr_code(car_number, money)
