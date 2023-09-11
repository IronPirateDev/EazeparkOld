import cv2
import pytesseract
import mysql.connector
import re
from datetime import datetime, timedelta
import subprocess as s
import webbrowser
import time
import pyautogui
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading
from selenium import webdriver
import psutil
import pygetwindow as gw

# Path to the Tesseract executable (change this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Tesseract\\tesseract.exe'
money = False
# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dpsbn",
    database="cars"
)
import qrcode
from urllib.parse import urlencode, quote

def generate_qr_code(car_number, money):
    # Encode car number and money as URL parameters
    params = {'car_number': car_number, 'money': money}
    url = 'https://eazepark.repl.co/?' + urlencode(params, quote_via=quote)

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
    img.save('C:\EazePark\Sign_Out\qr.png')

dbno=[]
payment_event=False
def delete_car_number(car_number):
    cursor = db.cursor()
    query = "DELETE FROM car_no WHERE car_number = %s"
    cursor.execute(query, (car_number,))
    db.commit()
def is_edge_running():
    payment_confirmation_windows = [window for window in gw.getWindowsWithTitle('') if 'Payment Confirmation' in window.title]
    return len(payment_confirmation_windows) > 0
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
cap = cv2.VideoCapture(0)

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
    
    # If car number is detected and valid, save to the 'car_no' table and calculate charges
    if car_number and all_regex.match(car_number):
        cursor = db.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "SELECT * from car_no where car_number=%s"
        cursor.execute(query, (car_number,))
        result = cursor.fetchone()
        payment_confirmation_event = threading.Event()
        if result:
            print("Detected Car Number:", car_number)
               
            # Get the timestamp from the database result
            db_timestamp = result[1]
                
            # Calculate total hours and charges
            total_hours, total_charge = calculate_charges(db_timestamp)
              
            print(f"Total Hours: {total_hours}")
            print(f"Total Charges: {total_charge} Rs")
        # Break out of the loop once a car number is detected
        break
    
    # Wait for a key event and check if it's the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and destroy all windows
cap.release()
cv2.destroyAllWindows()
cursor.execute('select * from car_no')
a = cursor.fetchall()
for i in a:
    for j in i:
        dbno.append(j)
        break
if car_number not in dbno:
    s.run(["python","C:\\EazePark\\Sign_Out\\Sign_Out.py"])
money=str(total_charge)
generate_qr_code(car_number, money)
#subprocess.run(["python", "F:\\Project-Aira\\new_pro\\testsign.py"])
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Payment Confirmation</title>
    <link rel="icon" href="static/favicon.ico">
    <style>
        body {{
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            font-size: 24px;
        }}
        p {{
            font-size: 18px;
        }}
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .content {{
            max-width: 80%;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin-top: 20px;
        }}
        button#confirmBtn {{
            background-color: blue;
            color: white;
            font-size: 20px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h1>Car Number and Charges</h1>
            <p>Car Number: {car_number}</p>
            <p>Total Charges: {total_charge} Rs</p>
            <img src="qr.png" alt="Car Image">
        </div>
        <button id="confirmBtn">Yes, Payment Made</button>
    </div>
<script>
    document.getElementById("confirmBtn").addEventListener("click", function() {{
        // Close the HTML file after confirmation
        window.close();
        // Set the 'money' variable to True
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/payment_status", true);
        xhr.send();
    }});

    // Add an event listener for when the window is closed
    window.addEventListener("beforeunload", function() {{
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/stop_server", true);
        xhr.send();
    }});
</script>
</body>
</html>
"""
import threading

def website():
    global money
    with open("C:\\EazePark\\Sign_Out\\payment_confirmation.html", "w") as html_file:
        html_file.write(html_content)
    time.sleep(3)
    import http.server
    import socketserver
    import webbrowser

    # Set the initial value of money variable
    money = False

    class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            global money
            if "/payment_status" in self.path:
                money = True
                self.send_response(200)
                self.end_headers()
                return
            elif "/stop_server" in self.path:
                self.send_response(200)
                self.end_headers()
                self.server.shutdown()  # Stop the server
            else:
                # Serve files from the specified directory
                self.directory = "C:\\EazePark\\Sign_Out"
                super().do_GET()

    # Create a server that uses the custom request handler
    handler = MyRequestHandler

    # Use a random port (you can specify a specific port if needed)
    port = 8080
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")

        # Open the browser with the HTML page
        webbrowser.open(f"http://localhost:8080/payment_confirmation.html")
        
        # Set the 'money' variable to True

        
        # Start the server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.start()
        # Wait for user input to stop the server
        time.sleep(10)
        while is_edge_running():
            pass            
        else:
            httpd.shutdown()
            money = True
    # This will only run after the server is stopped
    print(money)
website()
def payment_verification():
    global car_number_em
    global money_paid
    import imaplib
    import email
    import re

    # Gmail IMAP settings
    username = "ineazepark@gmail.com"
    password = "hqkoabclvofhqlxt"

    # Connect to Gmail's IMAP server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)

    # Select the mailbox you want to read emails from (e.g., "inbox")
    mailbox = "inbox"
    mail.select(mailbox)

    # Search for all emails in the selected mailbox
    status, email_ids = mail.search(None, "ALL")

    # Get a list of email IDs and reverse the order to get the latest email first
    email_id_list = email_ids[0].split()[::-1]

    # Function to extract "Car Number" and "Money Paid" values
    def extract_car_number_and_money_paid(email_content):
        car_number_em = ""
        money_paid = ""
        
        car_number_match = re.search(r"Car Number: ([\w\s]+)(?=\s*Money Paid:|$)", email_content)
        money_paid_match = re.search(r"Money Paid: (\d+)", email_content)
        
        if car_number_match:
            car_number_em = car_number_match.group(1)
        
        if money_paid_match:
            money_paid = money_paid_match.group(1)
        
        return car_number_em.strip(), money_paid.strip()

    # Iterate through the email IDs and fetch the emails (latest first)
    for email_id in email_id_list:
        # Fetch the email using its unique ID
        status, email_data = mail.fetch(email_id, "(BODY[TEXT])")
        
        # Parse the email content
        email_message = email.message_from_bytes(email_data[0][1])
        
        # Extract "Car Number" and "Money Paid" as separate strings
        email_content = email_message.get_payload()
        car_number_em, money_paid = extract_car_number_and_money_paid(email_content)
        print(car_number_em,money_paid)
        print(car_number,total_charge)
        # Print the extracted values
        break
    # Logout and close the connection
    mail.logout()
if money:
    time.sleep(5)
    payment_verification()
    if car_number_em==car_number and int(money_paid)==total_charge:
        payment_event=True
        driver=webdriver.Chrome()
        driver.get('file:///C:/EazePark/Sign_Out/templates/thank_you.html')
        import pygetwindow as gw
        # Assuming 'Your Window Title' is the title of the window you want to maximize
        window = gw.getWindowsWithTitle('Thank You - Google Chrome')[0]
        window.maximize()
        time.sleep(5)
        driver.quit()
    elif car_number_em==car_number and int(money_paid)!=total_charge:
        driver=webdriver.Chrome()
        driver.get('file:///C:/EazePark/Sign_Out/templates/moneyerr.html')
        import pygetwindow as gw
        # Assuming 'Your Window Title' is the title of the window you want to maximize
        window = gw.getWindowsWithTitle('Payment Error - Google Chrome')[0]
        window.maximize()
        time.sleep(20)
        driver.quit()
        website()
        payment_verification()
    elif car_number_em!=car_number:
        website()
        payment_verification()
    if payment_event:
        delete_car_number(car_number)
        s.run(["python","C:\\EazePark\\Sign_Out\\Sign_Out.py"])
    else:
        website()
        payment_verification()