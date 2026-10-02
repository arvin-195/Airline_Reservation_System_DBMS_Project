import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

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


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="✈ AIRLINE RESERVATION SYSTEM",
    font=("Arial", 24, "bold")
)

title.pack(pady=20)


subtitle = tk.Label(
    root,
    text="Flight Booking and Reservation Management",
    font=("Arial", 12)
)

subtitle.pack()


# =========================================================
# MAIN FRAME
# =========================================================

main_frame = tk.Frame(root)
main_frame.pack(pady=30)


# =========================================================
# SEARCH FLIGHTS
# =========================================================

def search_flights_window():

    window = tk.Toplevel(root)
    window.title("Search Flights")
    window.geometry("750x500")

    tk.Label(
        window,
        text="SEARCH FLIGHTS",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    form = tk.Frame(window)
    form.pack(pady=10)

    tk.Label(form, text="Source Airport:").grid(
        row=0, column=0, padx=10, pady=10
    )

    source = ttk.Combobox(form, width=20)
    source.grid(row=0, column=1)

    tk.Label(form, text="Destination Airport:").grid(
        row=1, column=0, padx=10, pady=10
    )

    destination = ttk.Combobox(form, width=20)
    destination.grid(row=1, column=1)

    cursor.execute("SELECT airport_code FROM Airport")
    airport_codes = [row[0] for row in cursor.fetchall()]

    source["values"] = airport_codes
    destination["values"] = airport_codes

    columns = (
        "Flight",
        "Source",
        "Destination",
        "Departure",
        "Arrival"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings",
        height=10
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=130)

    table.pack(pady=20)

    def search():

        for item in table.get_children():
            table.delete(item)

        cursor.execute("""
            SELECT
                f.flight_number,
                f.source_airport_code,
                f.destination_airport_code,
                f.departure_time,
                f.arrival_time
            FROM Flight f
            WHERE f.source_airport_code = ?
            AND f.destination_airport_code = ?
        """, (source.get(), destination.get()))

        rows = cursor.fetchall()

        for row in rows:
            table.insert("", tk.END, values=row)

        if not rows:
            messagebox.showinfo(
                "Search Result",
                "No flights found."
            )

    tk.Button(
        form,
        text="Search",
        width=15,
        command=search
    ).grid(row=2, column=0, columnspan=2, pady=10)


# =========================================================
# AVAILABLE SEATS
# =========================================================

def available_seats_window():

    window = tk.Toplevel(root)
    window.title("Available Seats")
    window.geometry("500x350")

    tk.Label(
        window,
        text="CHECK AVAILABLE SEATS",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(
        window,
        text="Flight Number:"
    ).pack()

    flight_entry = tk.Entry(window, width=25)
    flight_entry.pack(pady=10)

    result_label = tk.Label(
        window,
        text="",
        font=("Arial", 12)
    )

    result_label.pack(pady=20)

    def check():

        cursor.execute("""
            SELECT
                a.total_seating_capacity
            FROM Flight f
            JOIN Aircraft a
                ON f.aircraft_id = a.aircraft_id
            WHERE f.flight_number = ?
        """, (flight_entry.get().upper(),))

        result = cursor.fetchone()

        if result is None:
            messagebox.showerror(
                "Error",
                "Flight not found."
            )
            return

        capacity = result[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Booking b
            JOIN Flight f
                ON b.flight_id = f.flight_id
            WHERE f.flight_number = ?
        """, (flight_entry.get().upper(),))

        booked = cursor.fetchone()[0]

        available = capacity - booked

        result_label.config(
            text=f"Total Seats: {capacity}\n"
                 f"Booked Seats: {booked}\n"
                 f"Available Seats: {available}"
        )

    tk.Button(
        window,
        text="Check Seats",
        width=18,
        command=check
    ).pack()


# =========================================================
# PASSENGERS ON FLIGHT
# =========================================================

def passengers_window():

    window = tk.Toplevel(root)
    window.title("Passengers on Flight")
    window.geometry("650x450")

    tk.Label(
        window,
        text="PASSENGERS ON FLIGHT",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    form = tk.Frame(window)
    form.pack()

    tk.Label(
        form,
        text="Flight Number:"
    ).grid(row=0, column=0, padx=10)

    flight_entry = tk.Entry(form)
    flight_entry.grid(row=0, column=1, padx=10)

    columns = (
        "Passenger ID",
        "Name",
        "Seat",
        "Class"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=130)

    table.pack(pady=20)

    def search():

        for item in table.get_children():
            table.delete(item)

        cursor.execute("""
            SELECT
                p.passenger_id,
                p.name,
                b.seat_number,
                b.class
            FROM Passenger p
            JOIN Booking b
                ON p.passenger_id = b.passenger_id
            JOIN Flight f
                ON b.flight_id = f.flight_id
            WHERE f.flight_number = ?
        """, (flight_entry.get().upper(),))

        rows = cursor.fetchall()

        for row in rows:
            table.insert("", tk.END, values=row)

    tk.Button(
        form,
        text="Search",
        command=search
    ).grid(row=0, column=2, padx=10)


# =========================================================
# REVENUE WINDOW
# =========================================================

def revenue_window():

    window = tk.Toplevel(root)
    window.title("Revenue Per Flight")
    window.geometry("600x500")

    tk.Label(
        window,
        text="TOTAL REVENUE PER FLIGHT",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    columns = (
        "Flight Number",
        "Revenue"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    table.heading("Flight Number", text="Flight Number")
    table.heading("Revenue", text="Revenue")

    table.column("Flight Number", width=200)
    table.column("Revenue", width=200)

    table.pack(pady=20)

    cursor.execute("""
        SELECT
            f.flight_number,
            COALESCE(SUM(b.fare), 0)
        FROM Flight f
        LEFT JOIN Booking b
            ON f.flight_id = b.flight_id
        GROUP BY f.flight_id, f.flight_number
        ORDER BY f.flight_number
    """)

    rows = cursor.fetchall()

    for row in rows:
        table.insert(
            "",
            tk.END,
            values=(row[0], f"₹ {row[1]:,.2f}")
        )


# =========================================================
# CONNECTING ITINERARIES
# =========================================================

def connecting_window():

    window = tk.Toplevel(root)
    window.title("Connecting Itineraries")
    window.geometry("800x450")

    tk.Label(
        window,
        text="CONNECTING ITINERARIES",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    columns = (
        "Passenger",
        "Trip ID",
        "Itinerary",
        "Number of Legs"
    )

    table = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=170)

    table.pack(pady=20)

    cursor.execute("""
        SELECT
            p.name,
            t.trip_id,
            t.itinerary_name,
            COUNT(b.flight_id)
        FROM Passenger p
        JOIN Booking b
            ON p.passenger_id = b.passenger_id
        JOIN Trip t
            ON b.trip_id = t.trip_id
        GROUP BY
            p.passenger_id,
            p.name,
            t.trip_id,
            t.itinerary_name
        HAVING COUNT(b.flight_id) > 1
    """)

    rows = cursor.fetchall()

    for row in rows:
        table.insert("", tk.END, values=row)


# =========================================================
# DISPLAY TABLE
# =========================================================

def display_table_window():

    window = tk.Toplevel(root)
    window.title("Database Tables")
    window.geometry("1000x550")

    tk.Label(
        window,
        text="DATABASE TABLES",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    table_frame = tk.Frame(window)
    table_frame.pack()

    tk.Label(
        table_frame,
        text="Select Table:"
    ).grid(row=0, column=0, padx=10)

    table_combo = ttk.Combobox(
        table_frame,
        values=[
            "Airport",
            "Passenger",
            "Aircraft",
            "Flight",
            "Trip",
            "Booking",
            "Payment"
        ],
        width=20
    )

    table_combo.grid(row=0, column=1)

    output = ttk.Treeview(window)

    output.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    def show_table():

        table_name = table_combo.get()

        if not table_name:
            return

        cursor.execute(
            "SELECT * FROM " + table_name
        )

        rows = cursor.fetchall()
        column_names = [
            description[0]
            for description in cursor.description
        ]

        output.delete(
            *output.get_children()
        )

        output["columns"] = column_names
        output["show"] = "headings"

        for col in column_names:
            output.heading(col, text=col)
            output.column(col, width=120)

        for row in rows:
            output.insert(
                "",
                tk.END,
                values=row
            )

    tk.Button(
        table_frame,
        text="View Table",
        command=show_table
    ).grid(row=0, column=2, padx=10)


# =========================================================
# ADD BOOKING
# =========================================================

def add_booking_window():

    window = tk.Toplevel(root)
    window.title("Add New Booking")
    window.geometry("500x600")

    tk.Label(
        window,
        text="NEW BOOKING",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    form = tk.Frame(window)
    form.pack()

    # Passenger ID
    tk.Label(
        form,
        text="Passenger ID:"
    ).grid(row=0, column=0, sticky="w", pady=8)

    passenger_entry = tk.Entry(form)
    passenger_entry.grid(row=0, column=1)

    # Flight ID
    tk.Label(
        form,
        text="Flight ID:"
    ).grid(row=1, column=0, sticky="w", pady=8)

    flight_entry = tk.Entry(form)
    flight_entry.grid(row=1, column=1)

    # Trip ID
    tk.Label(
        form,
        text="Trip ID:"
    ).grid(row=2, column=0, sticky="w", pady=8)

    trip_entry = tk.Entry(form)
    trip_entry.grid(row=2, column=1)

    # Seat
    tk.Label(
        form,
        text="Seat Number:"
    ).grid(row=3, column=0, sticky="w", pady=8)

    seat_entry = tk.Entry(form)
    seat_entry.grid(row=3, column=1)

    # Class
    tk.Label(
        form,
        text="Class:"
    ).grid(row=4, column=0, sticky="w", pady=8)

    class_combo = ttk.Combobox(
        form,
        values=["Economy", "Business"],
        state="readonly"
    )

    class_combo.grid(row=4, column=1)
    class_combo.set("Economy")

    # Fare
    tk.Label(
        form,
        text="Fare:"
    ).grid(row=5, column=0, sticky="w", pady=8)

    fare_entry = tk.Entry(form)
    fare_entry.grid(row=5, column=1)

    result = tk.Label(
        window,
        text="",
        font=("Arial", 11)
    )

    result.pack(pady=15)

    def save_booking():

        try:

            passenger_id = int(
                passenger_entry.get()
            )

            flight_id = int(
                flight_entry.get()
            )

            trip_text = trip_entry.get()

            trip_id = (
                None
                if trip_text == ""
                else int(trip_text)
            )

            seat = seat_entry.get()
            seat_class = class_combo.get()

            fare = float(
                fare_entry.get()
            )

            # Check passenger
            cursor.execute(
                "SELECT * FROM Passenger WHERE passenger_id = ?",
                (passenger_id,)
            )

            if cursor.fetchone() is None:
                messagebox.showerror(
                    "Error",
                    "Passenger ID not found."
                )
                return

            # Check flight
            cursor.execute(
                "SELECT * FROM Flight WHERE flight_id = ?",
                (flight_id,)
            )

            if cursor.fetchone() is None:
                messagebox.showerror(
                    "Error",
                    "Flight ID not found."
                )
                return

            # Generate booking ID
            cursor.execute("""
                SELECT COALESCE(
                    MAX(booking_id), 0
                ) + 1
                FROM Booking
            """)

            booking_id = cursor.fetchone()[0]

            booking_reference = (
                "BK" +
                str(booking_id).zfill(3)
            )

            booking_date = datetime.now().strftime(
                "%Y-%m-%d"
            )

            cursor.execute("""
                INSERT INTO Booking
                (
                    booking_id,
                    booking_reference,
                    passenger_id,
                    flight_id,
                    trip_id,
                    seat_number,
                    class,
                    booking_date,
                    fare
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                booking_reference,
                passenger_id,
                flight_id,
                trip_id,
                seat,
                seat_class,
                booking_date,
                fare
            ))

            conn.commit()

            result.config(
                text=f"Booking Successful!\n"
                     f"Booking Reference: {booking_reference}"
            )

            messagebox.showinfo(
                "Success",
                f"Booking created successfully!\n\n"
                f"Booking Reference: {booking_reference}"
            )

        except sqlite3.IntegrityError as e:

            messagebox.showerror(
                "Booking Failed",
                str(e)
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Input",
                "Please enter valid values."
            )

    tk.Button(
        window,
        text="Confirm Booking",
        width=20,
        command=save_booking
    ).pack(pady=10)


# =========================================================
# MAIN BUTTONS
# =========================================================

button_frame = tk.Frame(main_frame)
button_frame.pack()


button_style = {
    "width": 22,
    "height": 2,
    "font": ("Arial", 11)
}


tk.Button(
    button_frame,
    text="Search Flights",
    command=search_flights_window,
    **button_style
).grid(row=0, column=0, padx=15, pady=10)


tk.Button(
    button_frame,
    text="Book Flight",
    command=add_booking_window,
    **button_style
).grid(row=0, column=1, padx=15, pady=10)


tk.Button(
    button_frame,
    text="Available Seats",
    command=available_seats_window,
    **button_style
).grid(row=1, column=0, padx=15, pady=10)


tk.Button(
    button_frame,
    text="Passengers on Flight",
    command=passengers_window,
    **button_style
).grid(row=1, column=1, padx=15, pady=10)


tk.Button(
    button_frame,
    text="Revenue per Flight",
    command=revenue_window,
    **button_style
).grid(row=2, column=0, padx=15, pady=10)


tk.Button(
    button_frame,
    text="Connecting Itineraries",
    command=connecting_window,
    **button_style
).grid(row=2, column=1, padx=15, pady=10)


tk.Button(
    button_frame,
    text="View Database Tables",
    command=display_table_window,
    **button_style
).grid(row=3, column=0, padx=15, pady=10)


tk.Button(
    button_frame,
    text="Exit",
    command=root.destroy,
    **button_style
).grid(row=3, column=1, padx=15, pady=10)


# =========================================================
# START PROGRAM
# =========================================================

create_tables()
insert_sample_data()

root.mainloop()

conn.close()