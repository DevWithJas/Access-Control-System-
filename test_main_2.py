import cv2
import pyodbc
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import qrcode
from PIL import Image
import os
import uuid
import subprocess  # Added for printing

# Function to establish a database connection
def connect_to_database():
    global connection, cursor
    server = server_var.get()
    database = database_var.get()

    # Define the database connection string
    db_connection_string = f'Driver={{SQL Server}};server={server};Database={database};Trusted_connection=yes;'

    try:
        connection = pyodbc.connect(db_connection_string)
        cursor = connection.cursor()
        print("Connected to the database successfully.")
    except pyodbc.Error as e:
        print("Database error:", str(e))

# Function to generate QR codes and save them to the specified folder
def generate_qr_codes():
    # Get the selected output folder
    output_folder = folder_var.get()

    # Get the database server and database name
    server = server_var.get()
    database = database_var.get()

    # Define the database connection string
    db_connection_string = f'Driver={{SQL Server}};server={server};Database={database};Trusted_connection=yes;'

    try:
        connection = pyodbc.connect(db_connection_string)
        cursor = connection.cursor()

        # Execute a SQL query to select unique QRValues from the QR table
        query = "SELECT DISTINCT CAST(QrValue AS NVARCHAR(MAX)) FROM QR WHERE AccessStatus IS NULL OR AccessStatus <> 'Granted'"

        cursor.execute(query)

        # Fetch all the unique QRValue values from the result set
        qr_code_contents = [row[0] for row in cursor.fetchall()]

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Generate QR codes for each unique QRValue and save them as image files in the specified folder
        for content in qr_code_contents:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(os.path.join(output_folder, f"{content}.png"))

        print("QR codes generated successfully.")

        # Ask the user if they want to print the QR codes
        response = tk.messagebox.askyesno("Print QR Codes", "Do you want to print the generated QR codes?")
        if response:
            print_qr_codes(output_folder)

    except pyodbc.Error as e:
        print("Database error:", str(e))

    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()

# Function to generate QR value with a UUID
def generate_qr_value(enrollment_number, user_name, designation):
    # Generate a UUID
    unique_id = uuid.uuid4()

    # Combine the components to create the QR value
    qr_value = f"{unique_id}-{enrollment_number}-{user_name}-{designation}"

    return qr_value

# Function to save data to the SQL table
def save_to_database(enrollment_number, user_name, designation):
    # Generate QR value
    qr_value = generate_qr_value(enrollment_number, user_name, designation)
    
    # Get the current timestamp as a string
    form_creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the data into the SQL table
    try:
        cursor.execute("INSERT INTO QR (EnrollmentNumber, UserName, Designation, QrValue, form_creation_time) VALUES (?, ?, ?, ?, ?)",
                       enrollment_number, user_name, designation, qr_value, form_creation_time)
        connection.commit()
        print("Data saved to the database successfully.")
    except pyodbc.Error as e:
        print("Database error:", str(e))

# Function to open a new data entry form
def open_new_form():
    def save_new_data():
        new_enrollment_number = new_enrollment_var.get()
        new_user_name = new_user_name_var.get()
        new_designation = new_designation_var.get()
        save_to_database(new_enrollment_number, new_user_name, new_designation)
        new_form.destroy()  # Close the new form after saving data

    new_form = tk.Toplevel(root)
    new_form.title("Data Entry Form")

    # Create variables to store input values for the new form
    new_enrollment_var = tk.StringVar()
    new_user_name_var = tk.StringVar()
    new_designation_var = tk.StringVar()

    # Create input fields in the new form
    enrollment_label = ttk.Label(new_form, text="Enrollment Number:", font=("Arial", 16))
    enrollment_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    enrollment_entry = ttk.Entry(new_form, textvariable=new_enrollment_var, font=("Arial", 16))
    enrollment_entry.grid(row=0, column=1, padx=10, pady=10)

    user_name_label = ttk.Label(new_form, text="User Name:", font=("Arial", 16))
    user_name_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    user_name_entry = ttk.Entry(new_form, textvariable=new_user_name_var, font=("Arial", 16))
    user_name_entry.grid(row=1, column=1, padx=10, pady=10)

    designation_label = ttk.Label(new_form, text="Designation:", font=("Arial", 16))
    designation_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    designation_entry = ttk.Entry(new_form, textvariable=new_designation_var, font=("Arial", 16))
    designation_entry.grid(row=2, column=1, padx=10, pady=10)

    # Create a "Save" button in the new form
    save_button = ttk.Button(new_form, text="Save", command=save_new_data, style="TButton")
    save_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Function to clear the QR table
def clear_qr_table():
    try:
        cursor.execute("DELETE FROM QR;")
        connection.commit()
        print("QR table cleared.")
    except pyodbc.Error as e:
        print("Database error:", str(e))

# Function to browse for the output folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_var.set(folder_selected)

# Function to print QR codes using system default printer
def print_qr_codes(folder_path):
    try:
        # List all the image files in the specified folder
        image_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.png')]

        # Print each image file using the system default printer
        for image_file in image_files:
            subprocess.Popen(['print', image_file], shell=True)

        print("QR codes printed successfully.")
    except Exception as e:
        print("Error printing QR codes:", str(e))

# Create the main Tkinter window
root = tk.Tk()
root.title("Combined QR Code Generator and Data Entry")

# Create a Notebook (Tabbed Interface)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create tabs for QR Code Generation and Data Entry
qr_tab = ttk.Frame(notebook)
data_entry_tab = ttk.Frame(notebook)

notebook.add(qr_tab, text='QR Code Generation')
notebook.add(data_entry_tab, text='Data Entry')

# Create variables to store input values
server_var = tk.StringVar()
database_var = tk.StringVar()

# Label and Entry for the database server (QR Tab)
server_label_qr = ttk.Label(qr_tab, text="Database Server:", font=("Arial", 16))
server_label_qr.grid(row=0, column=0, padx=10, pady=10, sticky="w")
server_entry_qr = ttk.Entry(qr_tab, textvariable=server_var, font=("Arial", 16))
server_entry_qr.grid(row=0, column=1, padx=10, pady=10)

# Label and Entry for the database name (QR Tab)
database_label_qr = ttk.Label(qr_tab, text="Database Name:", font=("Arial", 16))
database_label_qr.grid(row=1, column=0, padx=10, pady=10, sticky="w")
database_entry_qr = ttk.Entry(qr_tab, textvariable=database_var, font=("Arial", 16))
database_entry_qr.grid(row=1, column=1, padx=10, pady=10)

# Button to generate QR codes (QR Tab)
generate_button = ttk.Button(qr_tab, text="Generate QR Codes", command=generate_qr_codes)
generate_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Label and Entry for the output folder (QR Tab)
folder_var = tk.StringVar()

folder_label = ttk.Label(qr_tab, text="Output Folder:", font=("Arial", 16))
folder_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
folder_entry = ttk.Entry(qr_tab, textvariable=folder_var, font=("Arial", 16))
folder_entry.grid(row=3, column=1, padx=10, pady=10)
browse_button = ttk.Button(qr_tab, text="Browse", command=browse_folder)
browse_button.grid(row=3, column=2, padx=10, pady=10)

# Label and Entry for the database server (Data Entry Tab)
server_label_data_entry = ttk.Label(data_entry_tab, text="Database Server:", font=("Arial", 16))
server_label_data_entry.grid(row=0, column=0, padx=10, pady=10, sticky="w")
server_entry_data_entry = ttk.Entry(data_entry_tab, textvariable=server_var, font=("Arial", 16))
server_entry_data_entry.grid(row=0, column=1, padx=10, pady=10)

# Label and Entry for the database name (Data Entry Tab)
database_label_data_entry = ttk.Label(data_entry_tab, text="Database Name:", font=("Arial", 16))
database_label_data_entry.grid(row=1, column=0, padx=10, pady=10, sticky="w")
database_entry_data_entry = ttk.Entry(data_entry_tab, textvariable=database_var, font=("Arial", 16))
database_entry_data_entry.grid(row=1, column=1, padx=10, pady=10)

# Button to connect to the database (Data Entry Tab)
connect_button = ttk.Button(data_entry_tab, text="Connect to Database", command=connect_to_database, style="TButton")
connect_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Button to open a new data entry form (Data Entry Tab)
new_form_button = ttk.Button(data_entry_tab, text="Open New Form", command=open_new_form, style="TButton")
new_form_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Button to clear the QR table (Data Entry Tab)
clear_button = ttk.Button(data_entry_tab, text="Clear QR Table", command=clear_qr_table, style="TButton")
clear_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Define the database connection parameters
connection = None
cursor = None

# Start the main Tkinter loop
root.mainloop()
