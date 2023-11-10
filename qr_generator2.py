import pyodbc
import qrcode
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog

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

    except pyodbc.Error as e:
        print("Database error:", str(e))

    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()

# Create a Tkinter window
root = tk.Tk()
root.title("QR Code Generator")

# Create and set variables to store folder path, server, and database
folder_var = tk.StringVar()
server_var = tk.StringVar()
database_var = tk.StringVar()

# Function to browse for the output folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_var.set(folder_selected)

# Label and Entry for the output folder
folder_label = tk.Label(root, text="Output Folder:")
folder_label.pack()
folder_entry = tk.Entry(root, textvariable=folder_var)
folder_entry.pack()
browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.pack()

# Label and Entry for the database server
server_label = tk.Label(root, text="Database Server:")
server_label.pack()
server_entry = tk.Entry(root, textvariable=server_var)
server_entry.pack()

# Label and Entry for the database name
database_label = tk.Label(root, text="Database Name:")
database_label.pack()
database_entry = tk.Entry(root, textvariable=database_var)
database_entry.pack()

# Button to generate QR codes
generate_button = tk.Button(root, text="Generate QR Codes", command=generate_qr_codes)
generate_button.pack()

root.mainloop()
