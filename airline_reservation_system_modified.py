import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os


# =========================================================
# AIRLINE RESERVATION SYSTEM
# Python + SQLite + Tkinter
# =========================================================

DB_NAME = "airline_reservation.db"

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")


# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():

    cursor.executescript("""

    DROP TABLE IF EXISTS Payment;
    DROP TABLE IF EXISTS Booking;
    DROP TABLE IF EXISTS Trip;
    DROP TABLE IF EXISTS Flight;
    DROP TABLE IF EXISTS Aircraft;
    DROP TABLE IF EXISTS Passenger;
    DROP TABLE IF EXISTS Airport;

    -- Airport
    CREATE TABLE Airport (
        airport_code VARCHAR(10) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        city VARCHAR(50) NOT NULL,
        country VARCHAR(50) NOT NULL
    );

    -- Passenger
    CREATE TABLE Passenger (
        passenger_id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        dob DATE,
        passport_number VARCHAR(30) UNIQUE,
        contact_info VARCHAR(100)
    );

    -- Aircraft
    CREATE TABLE Aircraft (
        aircraft_id INTEGER PRIMARY KEY,
        model VARCHAR(50) NOT NULL,
        total_seating_capacity INTEGER NOT NULL
    );

    -- Flight
    CREATE TABLE Flight (
        flight_id INTEGER PRIMARY KEY,
        flight_number VARCHAR(20) UNIQUE NOT NULL,
        source_airport_code VARCHAR(10) NOT NULL,
        destination_airport_code VARCHAR(10) NOT NULL,
        departure_time DATETIME NOT NULL,
        arrival_time DATETIME NOT NULL,
        aircraft_id INTEGER NOT NULL,

        FOREIGN KEY (source_airport_code)
            REFERENCES Airport(airport_code),

        FOREIGN KEY (destination_airport_code)
            REFERENCES Airport(airport_code),

        FOREIGN KEY (aircraft_id)
            REFERENCES Aircraft(aircraft_id),

        CHECK (source_airport_code <> destination_airport_code)
    );

    -- Trip / Itinerary
    CREATE TABLE Trip (
        trip_id INTEGER PRIMARY KEY,
        itinerary_name VARCHAR(100)
    );

    -- Booking
    CREATE TABLE Booking (
        booking_id INTEGER PRIMARY KEY,
        booking_reference VARCHAR(20) UNIQUE NOT NULL,
        passenger_id INTEGER NOT NULL,
        flight_id INTEGER NOT NULL,
        trip_id INTEGER,
        seat_number VARCHAR(10) NOT NULL,
        class VARCHAR(20) NOT NULL,
        booking_date DATE NOT NULL,
        fare DECIMAL(10,2) NOT NULL,

        FOREIGN KEY (passenger_id)
            REFERENCES Passenger(passenger_id),

        FOREIGN KEY (flight_id)
            REFERENCES Flight(flight_id),

        FOREIGN KEY (trip_id)
            REFERENCES Trip(trip_id),

        UNIQUE (flight_id, seat_number)
    );

    -- Payment
    CREATE TABLE Payment (
        payment_id INTEGER PRIMARY KEY,
        booking_id INTEGER UNIQUE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        mode VARCHAR(20) NOT NULL,
        status VARCHAR(20) NOT NULL,

        FOREIGN KEY (booking_id)
            REFERENCES Booking(booking_id)
    );

    """)

    conn.commit()


# =========================================================
# INSERT SAMPLE DATA
# =========================================================

def insert_sample_data():

    airports = [
        ("IXE", "Mangalore International Airport", "Mangalore", "India"),
        ("BLR", "Kempegowda International Airport", "Bangalore", "India"),
        ("BOM", "Chhatrapati Shivaji Maharaj Airport", "Mumbai", "India"),
        ("DEL", "Indira Gandhi International Airport", "Delhi", "India"),
        ("MAA", "Chennai International Airport", "Chennai", "India"),
        ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "India")
    ]

    cursor.executemany("""
        INSERT INTO Airport
        VALUES (?, ?, ?, ?)
    """, airports)

    passengers = [
        (1, "Arjun Kumar", "2002-01-10", "P10001", "9876543210"),
        (2, "Rahul Sharma", "2001-03-15", "P10002", "9876543211"),
        (3, "Priya Nair", "2003-05-20", "P10003", "9876543212"),
        (4, "Ananya Rao", "2002-07-12", "P10004", "9876543213"),
        (5, "Rohan Shetty", "2001-09-25", "P10005", "9876543214"),
        (6, "Sneha Pai", "2003-11-18", "P10006", "9876543215"),
        (7, "Vikram Singh", "2000-02-22", "P10007", "9876543216"),
        (8, "Neha Joshi", "2002-04-14", "P10008", "9876543217"),
        (9, "Karan Mehta", "2001-06-30", "P10009", "9876543218"),
        (10, "Meera Das", "2003-08-05", "P10010", "9876543219"),
        (11, "Aditya Rao", "2002-10-11", "P10011", "9876543220"),
        (12, "Pooja Shah", "2001-12-01", "P10012", "9876543221"),
        (13, "Nikhil Kumar", "2003-01-17", "P10013", "9876543222"),
        (14, "Divya Menon", "2002-03-29", "P10014", "9876543223"),
        (15, "Sanjay Bhat", "2000-05-09", "P10015", "9876543224")
    ]

    cursor.executemany("""
        INSERT INTO Passenger
        VALUES (?, ?, ?, ?, ?)
    """, passengers)

    aircraft = [
        (1, "Airbus A320", 180),
        (2, "Boeing 737", 160),
        (3, "Airbus A321", 220),
        (4, "Boeing 787", 250)
    ]

    cursor.executemany("""
        INSERT INTO Aircraft
        VALUES (?, ?, ?)
    """, aircraft)

    flights = [
        (1, "AI101", "IXE", "BLR",
         "2026-10-01 08:00", "2026-10-01 09:15", 1),

        (2, "AI102", "BLR", "DEL",
         "2026-10-01 11:00", "2026-10-01 13:45", 2),

        (3, "AI103", "DEL", "BOM",
         "2026-10-01 15:00", "2026-10-01 17:15", 3),

        (4, "AI104", "BOM", "IXE",
         "2026-10-02 09:00", "2026-10-02 10:45", 1),

        (5, "AI105", "IXE", "MAA",
         "2026-10-02 12:00", "2026-10-02 13:30", 2),

        (6, "AI106", "MAA", "DEL",
         "2026-10-02 15:00", "2026-10-02 18:00", 3),

        (7, "AI107", "BLR", "HYD",
         "2026-10-03 08:30", "2026-10-03 10:00", 1),

        (8, "AI108", "HYD", "BOM",
         "2026-10-03 12:00", "2026-10-03 13:30", 2),

        (9, "AI109", "BOM", "DEL",
         "2026-10-04 14:00", "2026-10-04 16:00", 4),

        (10, "AI110", "DEL", "BLR",
         "2026-10-04 18:00", "2026-10-04 20:30", 3)
    ]

    cursor.executemany("""
        INSERT INTO Flight
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, flights)

    trips = [
        (1, "Mangalore to Delhi via Bangalore"),
        (2, "Mangalore to Mumbai via Delhi"),
        (3, "Bangalore to Mumbai via Hyderabad"),
        (4, "Mumbai to Bangalore via Delhi")
    ]

    cursor.executemany("""
        INSERT INTO Trip
        VALUES (?, ?)
    """, trips)

    bookings = [
        (1, "BK001", 1, 1, None, "12A", "Economy",
         "2026-09-20", 3500),

        (2, "BK002", 2, 1, None, "12B", "Economy",
         "2026-09-20", 3500),

        (3, "BK003", 3, 1, 1, "14A", "Economy",
         "2026-09-20", 3500),

        (4, "BK004", 3, 2, 1, "15A", "Economy",
         "2026-09-20", 6500),

        (5, "BK005", 4, 1, 2, "16A", "Business",
         "2026-09-20", 7000),

        (6, "BK006", 4, 2, 2, "16B", "Business",
         "2026-09-20", 9000),

        (7, "BK007", 5, 3, None, "20A", "Economy",
         "2026-09-20", 8000),

        (8, "BK008", 6, 4, None, "21A", "Economy",
         "2026-09-20", 5000),

        (9, "BK009", 7, 5, None, "22A", "Economy",
         "2026-09-20", 4000),

        (10, "BK010", 8, 6, None, "23A", "Business",
         "2026-09-20", 10000),

        (11, "BK011", 9, 7, 3, "24A", "Economy",
         "2026-09-20", 4500),

        (12, "BK012", 9, 8, 3, "24B", "Economy",
         "2026-09-20", 5500),

        (13, "BK013", 10, 9, None, "25A", "Economy",
         "2026-09-20", 6000),

        (14, "BK014", 11, 9, 4, "26A", "Business",
         "2026-09-20", 9000),

        (15, "BK015", 11, 10, 4, "26B", "Business",
         "2026-09-20", 8500),

        (16, "BK016", 12, 10, None, "27A", "Economy",
         "2026-09-20", 5000),

        (17, "BK017", 13, 3, None, "28A", "Economy",
         "2026-09-20", 7500),

        (18, "BK018", 14, 4, None, "29A", "Economy",
         "2026-09-20", 5000),

        (19, "BK019", 15, 5, None, "30A", "Economy",
         "2026-09-20", 4000)
    ]

    cursor.executemany("""
        INSERT INTO Booking
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, bookings)

    payments = [
        (1, 1, 3500, "UPI", "Paid"),
        (2, 2, 3500, "Card", "Paid"),
        (3, 3, 3500, "UPI", "Paid"),
        (4, 4, 6500, "UPI", "Paid"),
        (5, 5, 7000, "Card", "Paid"),
        (6, 6, 9000, "Card", "Paid"),
        (7, 7, 8000, "UPI", "Paid"),
        (8, 8, 5000, "Cash", "Paid"),
        (9, 9, 4000, "UPI", "Paid"),
        (10, 10, 10000, "Card", "Paid"),
        (11, 11, 4500, "UPI", "Paid"),
        (12, 12, 5500, "UPI", "Paid"),
        (13, 13, 6000, "Card", "Paid"),
        (14, 14, 9000, "Card", "Paid"),
        (15, 15, 8500, "UPI", "Paid"),
        (16, 16, 5000, "UPI", "Paid"),
        (17, 17, 7500, "Card", "Paid"),
        (18, 18, 5000, "Cash", "Paid"),
        (19, 19, 4000, "UPI", "Paid")
    ]

    cursor.executemany("""
        INSERT INTO Payment
        VALUES (?, ?, ?, ?, ?)
    """, payments)

    conn.commit()


# =========================================================
# TKINTER APPLICATION
# =========================================================

root = tk.Tk()
root.title("Airline Reservation System")
root.geometry("1000x650")
root.resizable(False, False)

# -------------------------
# UI THEME
# -------------------------
BG = "#eef3f7"
DARK = "#111111"
WHITE = "#ffffff"
TEXT = "#1f2937"
ACCENT = "#d9e7f2"

root.configure(bg=BG)

style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "Treeview",
    background=WHITE,
    fieldbackground=WHITE,
    foreground=TEXT,
    rowheight=28
)
style.configure(
    "Treeview.Heading",
    background=DARK,
    foreground=WHITE,
    font=("Arial", 10, "bold")
)
style.map(
    "Treeview",
    background=[("selected", "#d9d9d9")],
    foreground=[("selected", DARK)]
)
style.configure(
    "TCombobox",
    fieldbackground=WHITE,
    background=WHITE,
    foreground=TEXT
)

# Tkinter Button does not support true rounded corners.
# These Canvas buttons provide rounded corners while remaining simple.
def rounded_button(parent, text, command, width=180, height=42,
                   bg=DARK, fg=WHITE, radius=18, font=("Arial", 11, "bold")):
    canvas = tk.Canvas(
        parent, width=width, height=height,
        bg=parent.cget("bg"), highlightthickness=0, bd=0
    )

    def draw(fill=bg):
        canvas.delete("all")
        canvas.create_round_rect = None
        # Smooth rounded rectangle using overlapping rectangles/ovals.
        canvas.create_rectangle(
            radius, 0, width-radius, height,
            fill=fill, outline=fill
        )
        canvas.create_rectangle(
            0, radius, width, height-radius,
            fill=fill, outline=fill
        )
        canvas.create_oval(
            0, 0, radius*2, radius*2,
            fill=fill, outline=fill
        )
        canvas.create_oval(
            width-radius*2, 0, width, radius*2,
            fill=fill, outline=fill
        )
        canvas.create_oval(
            0, height-radius*2, radius*2, height,
            fill=fill, outline=fill
        )
        canvas.create_oval(
            width-radius*2, height-radius*2, width, height,
            fill=fill, outline=fill
        )
        canvas.create_text(
            width//2, height//2,
            text=text, fill=fg, font=font
        )

    draw()

    canvas.bind("<Button-1>", lambda e: command())
    canvas.bind("<Enter>", lambda e: draw("#333333"))
    canvas.bind("<Leave>", lambda e: draw(bg))
    return canvas


def add_title(parent, title, subtitle=None):
    tk.Label(
        parent, text=title, bg=parent.cget("bg"),
        fg=TEXT, font=("Arial", 20, "bold")
    ).pack(pady=(15, 4))

    if subtitle:
        tk.Label(
            parent, text=subtitle, bg=parent.cget("bg"),
            fg="#5b6573", font=("Arial", 10)
        ).pack(pady=(0, 12))


def get_all_flight_numbers():
    cursor.execute(
        "SELECT flight_number FROM Flight ORDER BY flight_number"
    )
    return [row[0] for row in cursor.fetchall()]


def get_fare(flight_id, seat_class):
    """
    Fare is calculated from the existing Economy fare for the selected
    flight. Business is 2x Economy. This keeps the fare automatic
    without changing the database schema.
    """
    cursor.execute("""
        SELECT MIN(fare)
        FROM Booking
        WHERE flight_id = ? AND class = 'Economy'
    """, (flight_id,))
    row = cursor.fetchone()

    if row and row[0] is not None:
        economy_fare = float(row[0])
    else:
        # Base fares for flights with no Economy booking yet.
        base_fares = {
            1: 3500, 2: 6500, 3: 8000, 4: 5000, 5: 4000,
            6: 7500, 7: 4500, 8: 5500, 9: 6000, 10: 5000
        }
        economy_fare = float(base_fares.get(flight_id, 5000))

    return economy_fare if seat_class == "Economy" else economy_fare * 2


# =========================================================
# BOOKING WINDOW
# =========================================================

def add_booking_window(prefill=None):
    prefill = prefill or {}

    window = tk.Toplevel(root)
    window.title("Book Flight")
    window.geometry("540x650")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(
        window,
        "BOOK YOUR FLIGHT",
        "Passenger and fare details are filled automatically"
    )

    form = tk.Frame(window, bg=BG)
    form.pack(pady=5)

    def field(label, row):
        tk.Label(
            form, text=label, bg=BG, fg=TEXT,
            font=("Arial", 10, "bold")
        ).grid(row=row, column=0, sticky="w", padx=10, pady=8)

    # Passenger ID
    field("Passenger ID:", 0)
    passenger_combo = ttk.Combobox(
        form, width=25, state="readonly",
        values=[
            str(x[0]) for x in
            cursor.execute(
                "SELECT passenger_id FROM Passenger ORDER BY passenger_id"
            ).fetchall()
        ]
    )
    passenger_combo.grid(row=0, column=1, padx=10)
    passenger_combo.set(str(prefill.get("passenger_id", 1)))

    # Flight ID
    field("Flight ID:", 1)
    flight_id_var = tk.StringVar(value=str(prefill.get("flight_id", "")))
    flight_id_entry = tk.Entry(
        form, textvariable=flight_id_var, width=28,
        state="readonly", readonlybackground=WHITE
    )
    flight_id_entry.grid(row=1, column=1, padx=10)

    # Flight Number
    field("Flight Number:", 2)
    flight_no_var = tk.StringVar(value=prefill.get("flight_number", ""))
    flight_no_label = tk.Entry(
        form, textvariable=flight_no_var, width=28,
        state="readonly", readonlybackground=WHITE
    )
    flight_no_label.grid(row=2, column=1, padx=10)

    # Trip ID
    field("Trip ID:", 3)
    trip_var = tk.StringVar(value=str(prefill.get("trip_id", "")))
    trip_entry = tk.Entry(
        form, textvariable=trip_var, width=28,
        state="readonly", readonlybackground=WHITE
    )
    trip_entry.grid(row=3, column=1, padx=10)

    # Seat
    field("Seat Number:", 4)
    seat_entry = tk.Entry(form, width=28)
    seat_entry.grid(row=4, column=1, padx=10)

    # Class
    field("Class:", 5)
    class_var = tk.StringVar(value=prefill.get("class", "Economy"))
    class_combo = ttk.Combobox(
        form, textvariable=class_var,
        values=["Economy", "Business"],
        state="readonly", width=25
    )
    class_combo.grid(row=5, column=1, padx=10)

    # Fare
    field("Fare:", 6)
    fare_var = tk.StringVar(value="")
    fare_entry = tk.Entry(
        form, textvariable=fare_var, width=28,
        state="readonly", readonlybackground=WHITE
    )
    fare_entry.grid(row=6, column=1, padx=10)

    def update_fare(*args):
        try:
            flight_id = int(flight_id_var.get())
            fare_var.set(f"₹ {get_fare(flight_id, class_var.get()):,.2f}")
        except (ValueError, TypeError):
            fare_var.set("")

    class_combo.bind("<<ComboboxSelected>>", update_fare)
    update_fare()

    result = tk.Label(
        window, text="", bg=BG, fg=TEXT,
        font=("Arial", 10, "bold")
    )
    result.pack(pady=12)

    def save_booking():
        try:
            passenger_id = int(passenger_combo.get())
            flight_id = int(flight_id_var.get())
            trip_text = trip_var.get().strip()
            trip_id = None if trip_text == "" else int(trip_text)
            seat = seat_entry.get().strip()
            seat_class = class_var.get()
            fare = get_fare(flight_id, seat_class)

            if not seat:
                messagebox.showerror("Invalid Input", "Enter a seat number.")
                return

            cursor.execute(
                "SELECT 1 FROM Passenger WHERE passenger_id = ?",
                (passenger_id,)
            )
            if cursor.fetchone() is None:
                messagebox.showerror("Error", "Passenger ID not found.")
                return

            cursor.execute(
                "SELECT 1 FROM Flight WHERE flight_id = ?",
                (flight_id,)
            )
            if cursor.fetchone() is None:
                messagebox.showerror("Error", "Flight ID not found.")
                return

            cursor.execute(
                "SELECT 1 FROM Booking WHERE flight_id = ? AND seat_number = ?",
                (flight_id, seat)
            )
            if cursor.fetchone():
                messagebox.showerror(
                    "Seat Unavailable",
                    f"Seat {seat} is already booked on this flight."
                )
                return

            cursor.execute(
                "SELECT COALESCE(MAX(booking_id), 0) + 1 FROM Booking"
            )
            booking_id = cursor.fetchone()[0]
            booking_reference = "BK" + str(booking_id).zfill(3)
            booking_date = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO Booking
                (booking_id, booking_reference, passenger_id, flight_id,
                 trip_id, seat_number, class, booking_date, fare)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id, booking_reference, passenger_id, flight_id,
                trip_id, seat, seat_class, booking_date, fare
            ))

            # Create a payment record automatically.
            payment_id = cursor.execute(
                "SELECT COALESCE(MAX(payment_id), 0) + 1 FROM Payment"
            ).fetchone()[0]

            cursor.execute("""
                INSERT INTO Payment
                (payment_id, booking_id, amount, mode, status)
                VALUES (?, ?, ?, ?, ?)
            """, (payment_id, booking_id, fare, "UPI", "Pending"))

            conn.commit()

            result.config(
                text=f"Booking Successful!\nReference: {booking_reference}"
            )
            messagebox.showinfo(
                "Success",
                f"Booking created successfully!\n\n"
                f"Booking Reference: {booking_reference}\n"
                f"Fare: ₹ {fare:,.2f}"
            )

        except sqlite3.IntegrityError as e:
            messagebox.showerror("Booking Failed", str(e))
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid values."
            )

    rounded_button(
        window, "CONFIRM BOOKING", save_booking,
        width=230, height=45
    ).pack(pady=8)


# =========================================================
# SEARCH FLIGHTS
# =========================================================

def search_flights_window():
    window = tk.Toplevel(root)
    window.title("Search Flights")
    window.geometry("900x600")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(
        window,
        "SEARCH FLIGHTS",
        "Select a flight and continue directly to booking"
    )

    form = tk.Frame(window, bg=BG)
    form.pack(pady=5)

    tk.Label(
        form, text="Source Airport:", bg=BG, fg=TEXT,
        font=("Arial", 10, "bold")
    ).grid(row=0, column=0, padx=8, pady=8)

    source = ttk.Combobox(form, width=18, state="readonly")
    source.grid(row=0, column=1, padx=8)

    tk.Label(
        form, text="Destination Airport:", bg=BG, fg=TEXT,
        font=("Arial", 10, "bold")
    ).grid(row=0, column=2, padx=8, pady=8)

    destination = ttk.Combobox(form, width=18, state="readonly")
    destination.grid(row=0, column=3, padx=8)

    cursor.execute("SELECT airport_code FROM Airport ORDER BY airport_code")
    airport_codes = [row[0] for row in cursor.fetchall()]
    source["values"] = airport_codes
    destination["values"] = airport_codes

    columns = (
        "Flight ID", "Flight", "Source",
        "Destination", "Departure", "Arrival"
    )

    table = ttk.Treeview(
        window, columns=columns, show="headings", height=11
    )

    widths = {
        "Flight ID": 80, "Flight": 80, "Source": 90,
        "Destination": 100, "Departure": 180, "Arrival": 180
    }

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=widths[col], anchor="center")

    table.pack(pady=15)

    def search():
        for item in table.get_children():
            table.delete(item)

        cursor.execute("""
            SELECT f.flight_id, f.flight_number,
                   f.source_airport_code, f.destination_airport_code,
                   f.departure_time, f.arrival_time
            FROM Flight f
            WHERE f.source_airport_code = ?
              AND f.destination_airport_code = ?
            ORDER BY f.departure_time
        """, (source.get(), destination.get()))

        rows = cursor.fetchall()

        for row in rows:
            table.insert("", tk.END, values=row)

        if not rows:
            messagebox.showinfo("Search Result", "No flights found.")

    def open_selected_booking(event=None):
        selected = table.selection()
        if not selected:
            messagebox.showwarning(
                "Select Flight",
                "Please click a flight first."
            )
            return

        values = table.item(selected[0], "values")
        flight_id = int(values[0])
        flight_number = values[1]

        # Trip ID is selected from existing trips that contain this flight
        # where possible; otherwise the booking can use no trip.
        cursor.execute("""
            SELECT DISTINCT trip_id
            FROM Booking
            WHERE flight_id = ? AND trip_id IS NOT NULL
            ORDER BY trip_id
            LIMIT 1
        """, (flight_id,))
        trip_row = cursor.fetchone()
        trip_id = trip_row[0] if trip_row else ""

        window.destroy()

        # Directly open the booking interface.
        add_booking_window({
            "flight_id": flight_id,
            "flight_number": flight_number,
            "trip_id": trip_id,
            "passenger_id": 1,
            "class": "Economy"
        })

    rounded_button(
        form, "SEARCH", search, width=150, height=40
    ).grid(row=0, column=4, padx=15)

    tk.Label(
        window,
        text="Double-click a flight to open the booking interface",
        bg=BG, fg="#5b6573",
        font=("Arial", 9, "italic")
    ).pack()

    table.bind("<Double-1>", open_selected_booking)


# =========================================================
# AVAILABLE SEATS
# =========================================================

def available_seats_window():
    window = tk.Toplevel(root)
    window.title("Available Seats")
    window.geometry("500x370")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(
        window,
        "CHECK AVAILABLE SEATS",
        "Choose a flight from the searched flights list"
    )

    tk.Label(
        window, text="Flight Number:", bg=BG, fg=TEXT,
        font=("Arial", 10, "bold")
    ).pack(pady=(8, 3))

    flight_combo = ttk.Combobox(
        window, width=25, state="readonly"
    )
    flight_combo.pack(pady=8)

    # Dropdown is populated from flights found in the database.
    flight_combo["values"] = get_all_flight_numbers()

    result_label = tk.Label(
        window, text="", bg=BG, fg=TEXT,
        font=("Arial", 11, "bold")
    )
    result_label.pack(pady=20)

    def check():
        flight_no = flight_combo.get().strip().upper()

        if not flight_no:
            messagebox.showwarning(
                "Select Flight", "Please select a flight number."
            )
            return

        cursor.execute("""
            SELECT a.total_seating_capacity
            FROM Flight f
            JOIN Aircraft a ON f.aircraft_id = a.aircraft_id
            WHERE f.flight_number = ?
        """, (flight_no,))

        result = cursor.fetchone()

        if result is None:
            messagebox.showerror("Error", "Flight not found.")
            return

        capacity = result[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Booking b
            JOIN Flight f ON b.flight_id = f.flight_id
            WHERE f.flight_number = ?
        """, (flight_no,))

        booked = cursor.fetchone()[0]
        available = capacity - booked

        result_label.config(
            text=f"Total Seats: {capacity}\n"
                 f"Booked Seats: {booked}\n"
                 f"Available Seats: {available}"
        )

    rounded_button(
        window, "CHECK SEATS", check,
        width=190, height=43
    ).pack()


# =========================================================
# PASSENGERS ON FLIGHT
# =========================================================

def passengers_window():
    window = tk.Toplevel(root)
    window.title("Passengers on Flight")
    window.geometry("700x500")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(
        window,
        "PASSENGERS ON FLIGHT",
        "Select any flight number available in the database"
    )

    form = tk.Frame(window, bg=BG)
    form.pack()

    tk.Label(
        form, text="Flight Number:", bg=BG, fg=TEXT,
        font=("Arial", 10, "bold")
    ).grid(row=0, column=0, padx=10)

    flight_combo = ttk.Combobox(
        form, width=20, state="readonly",
        values=get_all_flight_numbers()
    )
    flight_combo.grid(row=0, column=1, padx=10)

    columns = ("Passenger ID", "Name", "Seat", "Class")
    table = ttk.Treeview(
        window, columns=columns, show="headings", height=11
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=145, anchor="center")

    table.pack(pady=20)

    def search():
        for item in table.get_children():
            table.delete(item)

        flight_no = flight_combo.get().strip().upper()

        if not flight_no:
            messagebox.showwarning(
                "Select Flight", "Please select a flight number."
            )
            return

        cursor.execute("""
            SELECT p.passenger_id, p.name,
                   b.seat_number, b.class
            FROM Passenger p
            JOIN Booking b ON p.passenger_id = b.passenger_id
            JOIN Flight f ON b.flight_id = f.flight_id
            WHERE f.flight_number = ?
            ORDER BY b.seat_number
        """, (flight_no,))

        rows = cursor.fetchall()

        for row in rows:
            table.insert("", tk.END, values=row)

        if not rows:
            messagebox.showinfo(
                "Passengers",
                "No passengers are booked on this flight."
            )

    rounded_button(
        form, "SEARCH", search,
        width=130, height=38
    ).grid(row=0, column=2, padx=10)


# =========================================================
# REVENUE WINDOW
# =========================================================

def revenue_window():
    window = tk.Toplevel(root)
    window.title("Revenue Per Flight")
    window.geometry("600x500")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(window, "TOTAL REVENUE PER FLIGHT")

    columns = ("Flight Number", "Revenue")
    table = ttk.Treeview(
        window, columns=columns, show="headings", height=13
    )

    table.heading("Flight Number", text="Flight Number")
    table.heading("Revenue", text="Revenue")
    table.column("Flight Number", width=220, anchor="center")
    table.column("Revenue", width=220, anchor="center")
    table.pack(pady=20)

    cursor.execute("""
        SELECT f.flight_number,
               COALESCE(SUM(b.fare), 0)
        FROM Flight f
        LEFT JOIN Booking b ON f.flight_id = b.flight_id
        GROUP BY f.flight_id, f.flight_number
        ORDER BY f.flight_number
    """)

    for row in cursor.fetchall():
        table.insert(
            "", tk.END,
            values=(row[0], f"₹ {row[1]:,.2f}")
        )


# =========================================================
# CONNECTING ITINERARIES
# =========================================================

def connecting_window():
    window = tk.Toplevel(root)
    window.title("Connecting Itineraries")
    window.geometry("800x450")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(window, "CONNECTING ITINERARIES")

    columns = (
        "Passenger", "Trip ID", "Itinerary", "Number of Legs"
    )

    table = ttk.Treeview(
        window, columns=columns, show="headings", height=13
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=175, anchor="center")

    table.pack(pady=20)

    cursor.execute("""
        SELECT p.name, t.trip_id, t.itinerary_name,
               COUNT(b.flight_id)
        FROM Passenger p
        JOIN Booking b ON p.passenger_id = b.passenger_id
        JOIN Trip t ON b.trip_id = t.trip_id
        GROUP BY p.passenger_id, p.name,
                 t.trip_id, t.itinerary_name
        HAVING COUNT(b.flight_id) > 1
    """)

    for row in cursor.fetchall():
        table.insert("", tk.END, values=row)


# =========================================================
# DISPLAY TABLE
# =========================================================

def display_table_window():
    window = tk.Toplevel(root)
    window.title("Database Tables")
    window.geometry("1000x550")
    window.configure(bg=BG)
    window.resizable(False, False)

    add_title(window, "DATABASE TABLES")

    table_frame = tk.Frame(window, bg=BG)
    table_frame.pack()

    tk.Label(
        table_frame, text="Select Table:",
        bg=BG, fg=TEXT, font=("Arial", 10, "bold")
    ).grid(row=0, column=0, padx=10)

    table_combo = ttk.Combobox(
        table_frame,
        values=[
            "Airport", "Passenger", "Aircraft", "Flight",
            "Trip", "Booking", "Payment"
        ],
        width=20, state="readonly"
    )
    table_combo.grid(row=0, column=1)

    output = ttk.Treeview(window)
    output.pack(
        fill="both", expand=True,
        padx=20, pady=20
    )

    def show_table():
        table_name = table_combo.get()
        if not table_name:
            return

        cursor.execute("SELECT * FROM " + table_name)
        rows = cursor.fetchall()
        column_names = [
            description[0]
            for description in cursor.description
        ]

        output.delete(*output.get_children())
        output["columns"] = column_names
        output["show"] = "headings"

        for col in column_names:
            output.heading(col, text=col)
            output.column(col, width=120)

        for row in rows:
            output.insert("", tk.END, values=row)

    rounded_button(
        table_frame, "VIEW TABLE", show_table,
        width=145, height=38
    ).grid(row=0, column=2, padx=10)


# =========================================================
# AIRPORT-STYLE MAIN SCREEN
# =========================================================

# Airport background without requiring an external image file.
# It creates a simple terminal/runway visual using Canvas.
hero = tk.Canvas(
    root, width=1000, height=210,
    bg="#b8cddd", highlightthickness=0
)
hero.pack(fill="x")

# Sky
hero.create_rectangle(0, 0, 1000, 145, fill="#b8cddd", outline="")
# Airport glass/terminal
hero.create_rectangle(0, 80, 1000, 145, fill="#6f8798", outline="")
for x in range(0, 1000, 100):
    hero.create_rectangle(
        x + 15, 92, x + 80, 137,
        fill="#dcebf4", outline=""
    )

# Runway
hero.create_rectangle(0, 145, 1000, 210, fill="#353535", outline="")
for x in range(20, 1000, 70):
    hero.create_rectangle(
        x, 174, x + 35, 181,
        fill="#ffffff", outline=""
    )

# Stylized airplane
hero.create_polygon(
    500, 32, 525, 75, 590, 85, 525, 92,
    510, 130, 490, 130, 475, 92, 410, 85,
    475, 75, fill=WHITE, outline=""
)

hero.create_text(
    500, 18,
    text="✈  FLY • BOOK • TRAVEL",
    fill=WHITE,
    font=("Arial", 16, "bold")
)

# Main content
main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True)

tk.Label(
    main_frame,
    text="AIRLINE RESERVATION SYSTEM",
    bg=BG, fg=TEXT,
    font=("Arial", 22, "bold")
).pack(pady=(12, 2))

tk.Label(
    main_frame,
    text="Flight Booking and Reservation Management",
    bg=BG, fg="#5b6573",
    font=("Arial", 10)
).pack(pady=(0, 12))

button_frame = tk.Frame(main_frame, bg=BG)
button_frame.pack()

button_style = dict(width=210, height=43)

rounded_button(
    button_frame, "SEARCH FLIGHTS",
    search_flights_window, **button_style
).grid(row=0, column=0, padx=12, pady=7)

rounded_button(
    button_frame, "BOOK FLIGHT",
    add_booking_window, **button_style
).grid(row=0, column=1, padx=12, pady=7)

rounded_button(
    button_frame, "AVAILABLE SEATS",
    available_seats_window, **button_style
).grid(row=1, column=0, padx=12, pady=7)

rounded_button(
    button_frame, "PASSENGERS ON FLIGHT",
    passengers_window, **button_style
).grid(row=1, column=1, padx=12, pady=7)

rounded_button(
    button_frame, "REVENUE PER FLIGHT",
    revenue_window, **button_style
).grid(row=2, column=0, padx=12, pady=7)

rounded_button(
    button_frame, "CONNECTING ITINERARIES",
    connecting_window, **button_style
).grid(row=2, column=1, padx=12, pady=7)

rounded_button(
    button_frame, "VIEW DATABASE TABLES",
    display_table_window, **button_style
).grid(row=3, column=0, padx=12, pady=7)

rounded_button(
    button_frame, "EXIT",
    root.destroy, **button_style
).grid(row=3, column=1, padx=12, pady=7)


# =========================================================
# START PROGRAM
# =========================================================

create_tables()
insert_sample_data()

root.mainloop()
conn.close()
