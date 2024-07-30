import tkinter as tk
from tkinter import messagebox
import pyodbc
import logging

# Set up logging
logging.basicConfig(filename='db_activity.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_db():
    try:
        # Database connection
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                              'SERVER=your_server_name_here;'
                              'DATABASE=master;'
                              'UID=your_db_username_here;'
                              'PWD=yoour_db_pwd_here')
        logging.info("Connected to database")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        messagebox.showerror("Error", f"Failed to connect to the database: {e}")
        return None

def fetch_db_info():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.databases")
            databases = cursor.fetchall()
            with open("database_info.txt", "w") as file:
                for db in databases:
                    db_name = db[0]
                    file.write(f"Database: {db_name}\n")
                    logging.info(f"Fetching tables for database: {db_name}")
                    
                    cursor.execute(f"USE {db_name}")
                    cursor.execute("SELECT name FROM sys.tables")
                    tables = cursor.fetchall()
                    for table in tables:
                        file.write(f"  Table: {table[0]}\n")
            logging.info("Fetched database and table information")
            messagebox.showinfo("Success", "Database information saved to database_info.txt")
        except Exception as e:
            logging.error(f"Failed to fetch database information: {e}")
            messagebox.showerror("Error", "Failed to fetch database information.")
        finally:
            conn.close()
            logging.info("Closed database connection")

# Create Tkinter GUI
root = tk.Tk()
root.title("SQL Server Database Info")

tk.Label(root, text="Server: your_server_name_here").grid(row=0, column=0, columnspan=2)
tk.Label(root, text="Login: your_db_username_here").grid(row=1, column=0, columnspan=2)
tk.Label(root, text="Password: yoour_db_pwd_here").grid(row=2, column=0, columnspan=2)

tk.Button(root, text="Fetch DB Info", command=fetch_db_info).grid(row=3, column=0, columnspan=2)

root.mainloop()
