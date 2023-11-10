import cv2
import pyodbc
import tkinter as tk
from datetime import datetime

# Function to establish a database connection
def connect_to_database(server, database):
    global connection, cursor

    # Define the database connection string
    db_connection_string = f'Driver={{SQL Server}};server={server};Database={database};Trusted_connection=yes;'

    # Establish a connection to the SQL Server database
    try:
        connection = pyodbc.connect(db_connection_string)
        cursor = connection.cursor()
        print("Connected to the database successfully.")
    except pyodbc.Error as e:
        print("Database error:", str(e))

# Function to update AccessControl based on QR table
def update_access_control(qr_content):
    try:
        # Check if the QR content exists in the QR table's QrValue column
        cursor.execute("SELECT TOP 1 EnrollmentNumber, AccessStatus, AccessTimeStr, form_creation_time FROM QR WHERE CAST(QrValue AS NVARCHAR(MAX)) = ? ORDER BY form_creation_time DESC", qr_content)
        row = cursor.fetchone()

        if row:
            # Get the EnrollmentNumber, existing AccessStatus, AccessTimeStr, and form_creation_time
            enrollment_number = row.EnrollmentNumber
            existing_status = row.AccessStatus
            access_time_str = row.AccessTimeStr
            form_creation_time = row.form_creation_time

            # Get the current timestamp as a string
            current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if form_creation_time is not None:  # Check if form_creation_time is not None
                # Calculate the time difference in seconds
                time_difference = (datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S') - form_creation_time).total_seconds()

                # Check if the QR code is for the latest form submission
                latest_form_creation_time = get_latest_form_creation_time(enrollment_number)
                
                # Update the result label text on the Tkinter GUI
                if existing_status != 'Granted' and form_creation_time == latest_form_creation_time and time_difference <= 86400:
                    result_label.config(text="✅ Access Granted")

                    # Update the AccessStatus and AccessTimeStr columns in Python
                    cursor.execute("UPDATE QR SET AccessStatus = ?, AccessTimeStr = ? WHERE EnrollmentNumber = ? AND form_creation_time = ?", 'Granted', current_time_str, enrollment_number, form_creation_time)
                    connection.commit()

                    # Close the scanner window once scanned
                    cap.release()
                    root.destroy()
                else:
                    result_label.config(text="❌ Access Denied")
            else:
                result_label.config(text="❌ Form Creation Time Not Recorded")
        else:
            result_label.config(text="❌ Not Matched")
    except pyodbc.Error as e:
        print("Database error:", str(e))

# Function to get the latest form_creation_time for a given EnrollmentNumber
def get_latest_form_creation_time(enrollment_number):
    try:
        cursor.execute("SELECT MAX(form_creation_time) FROM QR WHERE EnrollmentNumber = ?", enrollment_number)
        row = cursor.fetchone()
        return row[0] if row[0] is not None else datetime(1970, 1, 1)  # Default to a very old date if no records found
    except pyodbc.Error as e:
        print("Database error:", str(e))
        return datetime(1970, 1, 1)

# Initialize the camera
cap = cv2.VideoCapture(0)

# Create a Tkinter window
root = tk.Tk()
root.title("QR Code Scanner")

# Create a label to display the result (initially empty)
result_label = tk.Label(root, text="")
result_label.pack()

# Function to handle the application exit
def exit_application():
    # Release the camera
    cap.release()

    # Close the database connection
    cursor.close()
    connection.close()

    # Close the Tkinter window
    root.destroy()

# Create an "Exit" button
exit_button = tk.Button(root, text="Exit", command=exit_application)
exit_button.pack()

# Function to start the scanner
def start_scanner():
    # Ask for database and server names
    server = server_var.get()
    database = database_var.get()

    # Establish a connection to the database
    connect_to_database(server, database)

    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()

        # Check if the frame is empty
        if not ret:
            continue

        # Initialize the QR code detector
        detector = cv2.QRCodeDetector()

        # Detect QR codes in the frame
        decoded_text, _, _ = detector.detectAndDecode(frame)

        if decoded_text:
            # Extract the scanned QR code content
            scanned_content = decoded_text
            print(f"Scanned QR Code Content: {scanned_content}")

            # Update AccessControl based on QR table
            update_access_control(scanned_content)

            root.update()

# Create variables to store input values for the database connection
server_var = tk.StringVar()
database_var = tk.StringVar()

# Create input fields for the server and database names
server_label = tk.Label(root, text="Server Name:")
server_label.pack()
server_entry = tk.Entry(root, textvariable=server_var)
server_entry.pack()

database_label = tk.Label(root, text="Database Name:")
database_label.pack()
database_entry = tk.Entry(root, textvariable=database_var)
database_entry.pack()

# Create a "Connect" button to establish a database connection and start the scanner
connect_button = tk.Button(root, text="Connect to Database and Start Scanner", command=start_scanner)
connect_button.pack()

# Define the database connection parameters
connection = None
cursor = None

# Start the Tkinter main loop
root.mainloop()
