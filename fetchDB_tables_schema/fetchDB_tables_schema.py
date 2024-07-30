#This code reads the connected SQL Server DB via ODBC connector 17,
# fetches the databases, their tables and the table schemas when selected_db
# in the dropdown table. And stores it as a txt file.

import tkinter as tk
from tkinter import messagebox
import pyodbc
import logging
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(filename='db_activity.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def read_credentials():
    tree = ET.parse('config.xml')
    root = tree.getroot()
    driver = root.find('DRIVER').text
    server = root.find('SERVER').text
    database = root.find('DATABASE').text
    return driver, server, database

def connect_to_db():
    try:
        uid = 'your_db_username'
        pwd = 'your_db_pwd'
        driver, server, database = read_credentials()
        conn = pyodbc.connect(f'DRIVER={{{driver}}};'
                              f'SERVER={server};'
                              f'DATABASE={database};'
                              f'UID={uid};'
                              f'PWD={pwd}')
        logging.info("Connected to database")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        messagebox.showerror("Error", f"Failed to connect to the database: {e}")
        return None

def fetch_databases():
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.databases")
            databases = cursor.fetchall()
            return [db[0] for db in databases]
        except Exception as e:
            logging.error(f"Failed to fetch databases: {e}")
            messagebox.showerror("Error", "Failed to fetch databases.")
        finally:
            conn.close()
            logging.info("Closed database connection")
    return []

def fetch_tables():
    selected_db = db_var.get()
    if not selected_db:
        messagebox.showwarning("Warning", "Please select a database.")
        return
    
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"USE {selected_db}")
            cursor.execute("SELECT name FROM sys.tables")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            table_var.set("Select a Table")
            table_menu['menu'].delete(0, 'end')
            for table in table_names:
                table_menu['menu'].add_command(label=table, command=tk._setit(table_var, table))
            logging.info(f"Fetched tables for database: {selected_db}")
            messagebox.showinfo("Success", f"Table information saved to {selected_db}_tables.txt")
        except Exception as e:
            logging.error(f"Failed to fetch tables for database {selected_db}: {e}")
            messagebox.showerror("Error", f"Failed to fetch tables for database {selected_db}.")
        finally:
            conn.close()
            logging.info("Closed database connection")

def fetch_table_details():
    selected_db = db_var.get()
    selected_table = table_var.get()
    if not selected_db or not selected_table:
        messagebox.showwarning("Warning", "Please select a database and a table.")
        return
    
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"USE {selected_db}")
            cursor.execute(f"EXEC sp_columns '{selected_table}'")
            columns = cursor.fetchall()
            with open(f"{selected_table}_details.txt", "w") as file:
                file.write(f"Table: {selected_table}\n")
                for column in columns:
                    file.write(f"  Column: {column.COLUMN_NAME}, Type: {column.TYPE_NAME}, Size: {column.LENGTH}\n")
            logging.info(f"Fetched details for table: {selected_table}")
            messagebox.showinfo("Success", f"Table details saved to {selected_table}_details.txt")
        except Exception as e:
            logging.error(f"Failed to fetch details for table {selected_table}: {e}")
            messagebox.showerror("Error", f"Failed to fetch details for table {selected_table}.")
        finally:
            conn.close()
            logging.info("Closed database connection")

# Create Tkinter GUI
root = tk.Tk()
root.title("SQL Server Database Info")

tk.Label(root, text="Server: DESKTOP-741O8M1").grid(row=0, column=0, columnspan=2)

databases = fetch_databases()
db_var = tk.StringVar(root)
db_var.set("Select a Database")

tk.OptionMenu(root, db_var, *databases).grid(row=1, column=0, columnspan=2)
tk.Button(root, text="See Tables", command=fetch_tables).grid(row=2, column=0, columnspan=2)

table_var = tk.StringVar(root)
table_var.set("Select a Table")
table_menu = tk.OptionMenu(root, table_var, "")
table_menu.grid(row=3, column=0, columnspan=2)

tk.Button(root, text="See Table Details", command=fetch_table_details).grid(row=4, column=0, columnspan=2)

root.mainloop()
