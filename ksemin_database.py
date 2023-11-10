import tkinter as tk
import tkinter.ttk as ttk
import pyodbc
import uuid
from datetime import datetime

# Function to establish a database connection
def connect_to_database():
    global connection, cursor
    server = server_var.get()
    database = database_var.get()

    # Define the database connection string
    db_connection_string = f'Driver={{SQL Server}};server={server};Database={database};Trusted_connection=yes;'

    # Establish a connection to the SQL Server database
    try:
        connection = pyodbc.connect(db_connection_string)
        cursor = connection.cursor()
        print("Connected to the database successfully.")
    except pyodbc.Error as e:
        print("Database error:", str(e))

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

# Create the main Tkinter window
root = tk.Tk()
root.title("Data Entry Form")

# Create variables to store input values
enrollment_var = tk.StringVar()
user_name_var = tk.StringVar()
designation_var = tk.StringVar()
server_var = tk.StringVar()
database_var = tk.StringVar()

# Create input fields in the main window
server_label = ttk.Label(root, text="SQL Server:", font=("Arial", 16))
server_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
server_entry = ttk.Entry(root, textvariable=server_var, font=("Arial", 16))
server_entry.grid(row=0, column=1, padx=10, pady=10)

database_label = ttk.Label(root, text="Database Name:", font=("Arial", 16))
database_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
database_entry = ttk.Entry(root, textvariable=database_var, font=("Arial", 16))
database_entry.grid(row=1, column=1, padx=10, pady=10)

enrollment_label = ttk.Label(root, text="Enrollment Number:", font=("Arial", 16))
enrollment_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
enrollment_entry = ttk.Entry(root, textvariable=enrollment_var, font=("Arial", 16))
enrollment_entry.grid(row=2, column=1, padx=10, pady=10)

user_name_label = ttk.Label(root, text="User Name:", font=("Arial", 16))
user_name_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
user_name_entry = ttk.Entry(root, textvariable=user_name_var, font=("Arial", 16))
user_name_entry.grid(row=3, column=1, padx=10, pady=10)

designation_label = ttk.Label(root, text="Designation:", font=("Arial", 16))
designation_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
designation_entry = ttk.Entry(root, textvariable=designation_var, font=("Arial", 16))
designation_entry.grid(row=4, column=1, padx=10, pady=10)

# Create a "Connect" button to establish a database connection
connect_button = ttk.Button(root, text="Connect to Database", command=connect_to_database, style="TButton")
connect_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

# Create a frame for buttons
button_frame = ttk.Frame(root)
button_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="n")

# Create a "Save" button to save data to the database
save_button = ttk.Button(button_frame, text="Save", command=lambda: save_to_database(
    enrollment_var.get(), user_name_var.get(), designation_var.get()), style="TButton")
save_button.grid(row=0, column=0, padx=10, pady=10)

# Create a "New Form" button to open a new data entry form
new_form_button = ttk.Button(button_frame, text="New Form", command=open_new_form, style="TButton")
new_form_button.grid(row=0, column=1, padx=10, pady=10)

# Create a "Clear QR Table" button to execute the DELETE query
clear_button = ttk.Button(root, text="Clear QR Table", command=clear_qr_table, style="TButton")
clear_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# Define the database connection parameters
connection = None
cursor = None

# Start the main Tkinter loop
root.mainloop()
