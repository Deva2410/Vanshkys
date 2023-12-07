import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Create SQLite database
conn = sqlite3.connect('car_rental.db')
c = conn.cursor()

# Create users table
c.execute('''
          CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY,
              username TEXT,
              password TEXT
          )
          ''')

# Create cars table
c.execute('''
          CREATE TABLE IF NOT EXISTS cars (
              id INTEGER PRIMARY KEY,
              brand TEXT,
              model TEXT,
              year INTEGER,
              available INTEGER,
              rate_per_hour REAL
          )
          ''')

# Create inventory table
c.execute('''
          CREATE TABLE IF NOT EXISTS inventory (
              id INTEGER PRIMARY KEY,
              brand TEXT,
              model TEXT,
              quantity INTEGER,
              rate_per_hour REAL
          )
          ''')

# Insert sample data
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))
c.execute("INSERT INTO cars (brand, model, year, available, rate_per_hour) VALUES (?, ?, ?, ?, ?)",
          ('Toyota', 'Camry', 2022, 1, 10.0))
c.execute("INSERT INTO cars (brand, model, year, available, rate_per_hour) VALUES (?, ?, ?, ?, ?)",
          ('Honda', 'Accord', 2022, 1, 12.5))
c.execute("INSERT INTO inventory (brand, model, quantity, rate_per_hour) VALUES (?, ?, ?, ?)",
          ('Toyota', 'Camry', 5, 10.0))
c.execute("INSERT INTO inventory (brand, model, quantity, rate_per_hour) VALUES (?, ?, ?, ?)",
          ('Honda', 'Accord', 3, 12.5))
conn.commit()

# Close the database connection
conn.close()


class CarRentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Los Pollos Hermanos Rentals')
        self.root.geometry('500x400')

        self.style = {'fg': 'black', 'font': ('Helvetica', 12, 'bold')}
        self.background_color = '#2E2E2E'

        self.create_widgets()
        self.animate(0)

    def create_widgets(self):
        style = ttk.Style()
        style.configure('TNotebook', background=self.background_color, foreground=self.style['fg'])
        style.configure('TFrame', background=self.background_color, foreground=self.style['fg'])

        notebook = ttk.Notebook(self.root, style='TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True)

        home_frame = ttk.Frame(notebook, style='TFrame')
        login_frame = ttk.Frame(notebook, style='TFrame')
        rentals_frame = ttk.Frame(notebook, style='TFrame')
        inventory_frame = ttk.Frame(notebook, style='TFrame')

        notebook.add(home_frame, text='Home')
        notebook.add(login_frame, text='Login')
        notebook.add(rentals_frame, text='Car Rentals')
        notebook.add(inventory_frame, text='Inventory')

        self.create_home_page(home_frame)
        self.create_login_page(login_frame)
        self.create_rentals_page(rentals_frame)
        self.create_inventory_page(inventory_frame)

    def create_home_page(self, frame):
        tk.Label(frame, text='Welcome to Los Pollos Hermanos Rentals', bg=self.background_color, **self.style, pady=20).pack()

    def create_login_page(self, frame):
        tk.Label(frame, text='Login', bg=self.background_color, **self.style, pady=20).pack()

        tk.Label(frame, text='Username:', bg=self.background_color, **self.style).pack()

        username_entry = tk.Entry(frame, **self.style)
        username_entry.pack(pady=10)

        tk.Label(frame, text='Password:', bg=self.background_color, **self.style).pack()

        password_entry = tk.Entry(frame, show='*', **self.style)
        password_entry.pack(pady=10)

        login_button = tk.Button(frame, text='Login', command=lambda: self.login(username_entry.get(), password_entry.get()),
                                 bg='black', fg='white', activebackground='dark grey', padx=10)
        login_button.pack(pady=10)

        gmail_sign_in_button = tk.Button(frame, text='Sign in with Gmail', command=self.sign_in_with_gmail,
                                         bg='black', fg='white', activebackground='dark grey', padx=10)
        gmail_sign_in_button.pack(pady=10)

    def create_rentals_page(self, frame):
        tk.Label(frame, text='Car Rentals', bg=self.background_color, **self.style, pady=20).pack()

        conn = sqlite3.connect('car_rental.db')
        c = conn.cursor()

        c.execute("SELECT * FROM cars WHERE available=1")
        cars = c.fetchall()

        for car in cars:
            button_text = f"{car[1]} {car[2]} ({car[3]})"
            car_button = tk.Button(frame, text=button_text, command=lambda c=car: self.show_car_details(c),
                                   bg='black', fg='white', activebackground='dark grey', padx=10)
            car_button.pack(pady=5)

        conn.close()

    def login(self, username, password):
        # Check credentials against the database
        conn = sqlite3.connect('car_rental.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            messagebox.showinfo('Success', 'Login successful!')
        else:
            messagebox.showerror('Error', 'Invalid credentials')

    def show_car_details(self, car):
        details_window = tk.Toplevel(self.root)
        details_window.title('Car Details')
        details_window.geometry('300x200')
        details_window.configure(bg=self.background_color)

        tk.Label(details_window, text=f"{car[1]} {car[2]} ({car[3]})", bg=self.background_color, **self.style, pady=10).pack()
        tk.Label(details_window, text=f"Availability: {'Available' if car[4] == 1 else 'Not Available'}",
                 bg=self.background_color, **self.style).pack(pady=5)
        tk.Label(details_window, text=f"Rate per Hour: ${car[5]:.2f}", bg=self.background_color, **self.style).pack(pady=5)

    def sign_in_with_gmail(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',  # Replace with your credentials file
            scopes=['https://www.googleapis.com/auth/drive.metadata.readonly']  # Replace with required scopes
        )

        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        messagebox.showinfo('Gmail Sign-in', 'Sign-in with Gmail successful!')

    def create_inventory_page(self, frame):
        tk.Label(frame, text='Car Inventory Management', bg=self.background_color, **self.style, pady=20).pack()

        conn = sqlite3.connect('car_rental.db')
        c = conn.cursor()

        c.execute('''
                  CREATE TABLE IF NOT EXISTS inventory (
                      id INTEGER PRIMARY KEY,
                      brand TEXT,
                      model TEXT,
                      quantity INTEGER,
                      rate_per_hour REAL
                  )
                  ''')

        conn.commit()

        # Insert sample inventory data if not already present
        c.execute("INSERT INTO inventory (brand, model, quantity, rate_per_hour) VALUES (?, ?, ?, ?)",
                  ('Toyota', 'Camry', 5, 10.0))
        c.execute("INSERT INTO inventory (brand, model, quantity, rate_per_hour) VALUES (?, ?, ?, ?)",
                  ('Honda', 'Accord', 3, 12.5))
        conn.commit()

        c.execute("SELECT * FROM inventory")
        inventory = c.fetchall()

        for item in inventory:
            label_text = f"{item[1]} {item[2]} - Quantity: {item[3]} - Rate per Hour: ${item[4]:.2f}"
            inventory_label = tk.Label(frame, text=label_text, bg='black', fg='white', pady=5)
            inventory_label.pack(pady=5)

        conn.close()

    def update_color(self, step):
        r_diff, g_diff, b_diff = 5, 5, 5  # Set your desired color change speed
        r_value = max(0, min(255, int(self.background_color[1:3], 16) + int(r_diff * step)))
        g_value = max(0, min(255, int(self.background_color[3:5], 16) + int(g_diff * step)))
        b_value = max(0, min(255, int(self.background_color[5:], 16) + int(b_diff * step)))

        self.background_color = f'#{r_value:02X}{g_value:02X}{b_value:02X}'

        style = ttk.Style()
        style.configure('TNotebook', background=self.background_color)

    def animate(self, step):
        self.update_color(step)
        self.root.after(20, lambda: self.animate(step + 1))


if __name__ == "__main__":
    root = tk.Tk()

    app = CarRentalApp(root)
    root.mainloop()
