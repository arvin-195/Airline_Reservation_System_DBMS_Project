
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date

DB = "airline_app.db"

# ============================================================
# AIRLINE RESERVATION / FLIGHT BOOKING DESKTOP APP
# Python + Tkinter + SQLite
#
# Features:
# - Search one-way flights
# - Economy / Business class
# - Live fare calculation
# - Direct flight selection -> booking screen
# - Passenger registration
# - Automatic Flight ID / Trip ID / Passenger ID / Fare
# - Seat map and seat availability
# - Payment simulation
# - Booking confirmation / PNR
# - My Bookings / cancellation
# ============================================================

class RoundedButton(tk.Frame):
    def __init__(self, parent, text, command, width=16,
                 bg="#111827", hover="#263244", fg="white"):
        super().__init__(parent, bg=parent.cget("bg") if "bg" in parent.keys() else "#eef3f8")
        self.command = command
        self.normal = bg
        self.hover = hover
        self.fg = fg
        self.w = max(85, width * 9 + 34)
        self.h = 42

        self.canvas = tk.Canvas(
            self, width=self.w, height=self.h,
            bg=self["bg"], highlightthickness=0
        )
        self.canvas.pack()

        self._draw(self.normal, text)
        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Enter>", lambda e: self._draw(self.hover, text))
        self.canvas.bind("<Leave>", lambda e: self._draw(self.normal, text))
        self.canvas.bind("<ButtonPress-1>",
                         lambda e: self._draw("#0b1320", text))
        self.canvas.bind("<ButtonRelease-1>",
                         lambda e: self._draw(self.hover, text))

    def _rounded_rect(self, x1, y1, x2, y2, r, fill):
        self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r,
                               start=90, extent=90, fill=fill, outline=fill)
        self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r,
                               start=0, extent=90, fill=fill, outline=fill)
        self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2,
                               start=180, extent=90, fill=fill, outline=fill)
        self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2,
                               start=270, extent=90, fill=fill, outline=fill)
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2,
                                     fill=fill, outline=fill)
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r,
                                     fill=fill, outline=fill)

    def _draw(self, color, text):
        self.canvas.delete("all")
        self._rounded_rect(1, 1, self.w-1, self.h-1, 12, color)
        self.canvas.create_text(
            self.w/2, self.h/2, text=text,
            fill=self.fg, font=("Segoe UI", 10, "bold")
        )

    def _click(self, event):
        self.command()


class AirlineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkyConnect - Airline Reservation System")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 680)
        self.root.configure(bg="#eef3f8")
        self.root.option_add("*Font", ("Segoe UI", 10))

        self.conn = sqlite3.connect(DB)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

        self.selected_flight = None
        self.selected_class = "Economy"
        self.selected_seat = None
        self.current_booking = None

        self.setup_database()
        self.seed_data()
        self.setup_style()
        self.show_home()

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------
    def setup_database(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS airports(
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS aircraft(
            aircraft_id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            capacity INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS flights(
            flight_id INTEGER PRIMARY KEY,
            flight_no TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            depart TEXT NOT NULL,
            arrive TEXT NOT NULL,
            aircraft_id INTEGER NOT NULL,
            economy_fare REAL NOT NULL,
            business_fare REAL NOT NULL,
            FOREIGN KEY(source) REFERENCES airports(code),
            FOREIGN KEY(destination) REFERENCES airports(code),
            FOREIGN KEY(aircraft_id) REFERENCES aircraft(aircraft_id)
        );

        CREATE TABLE IF NOT EXISTS passengers(
            passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT,
            passport TEXT UNIQUE,
            phone TEXT NOT NULL,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS trips(
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_code TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS bookings(
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr TEXT UNIQUE NOT NULL,
            trip_id INTEGER NOT NULL,
            passenger_id INTEGER NOT NULL,
            flight_id INTEGER NOT NULL,
            seat TEXT NOT NULL,
            travel_class TEXT NOT NULL,
            fare REAL NOT NULL,
            booking_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Confirmed',
            UNIQUE(flight_id, seat),
            FOREIGN KEY(trip_id) REFERENCES trips(trip_id),
            FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
            FOREIGN KEY(flight_id) REFERENCES flights(flight_id)
        );

        CREATE TABLE IF NOT EXISTS payments(
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT NOT NULL,
            status TEXT NOT NULL,
            paid_at TEXT NOT NULL,
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
        """)
        self.conn.commit()

    def seed_data(self):
        if self.conn.execute("SELECT COUNT(*) FROM airports").fetchone()[0] == 0:
            airports = [
                ("IXE", "Mangalore International Airport", "Mangalore", "India"),
                ("BLR", "Kempegowda International Airport", "Bengaluru", "India"),
                ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India"),
                ("DEL", "Indira Gandhi International Airport", "Delhi", "India"),
                ("MAA", "Chennai International Airport", "Chennai", "India"),
                ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "India"),
                ("GOI", "Manohar International Airport", "Goa", "India"),
                ("COK", "Cochin International Airport", "Kochi", "India"),
            ]
            self.conn.executemany(
                "INSERT INTO airports VALUES(?,?,?,?)", airports
            )

        if self.conn.execute("SELECT COUNT(*) FROM aircraft").fetchone()[0] == 0:
            aircraft = [
                (1, "Airbus A320", 180),
                (2, "Boeing 737-800", 189),
                (3, "Airbus A321", 220),
                (4, "Boeing 787 Dreamliner", 240),
            ]
            self.conn.executemany(
                "INSERT INTO aircraft VALUES(?,?,?)", aircraft
            )

        if self.conn.execute("SELECT COUNT(*) FROM flights").fetchone()[0] == 0:
            flights = [
                (1, "SC101", "IXE", "BLR", "06:30", "07:45", 1, 3499, 8499),
                (2, "SC102", "BLR", "DEL", "09:30", "12:15", 2, 5999, 12999),
                (3, "SC103", "IXE", "BOM", "08:15", "09:45", 1, 4299, 9999),
                (4, "SC104", "BOM", "DEL", "11:00", "13:10", 3, 5299, 11999),
                (5, "SC105", "IXE", "MAA", "10:00", "11:30", 2, 3999, 8999),
                (6, "SC106", "MAA", "DEL", "14:00", "17:00", 3, 5799, 12499),
                (7, "SC107", "BLR", "HYD", "07:00", "08:15", 1, 2999, 7499),
                (8, "SC108", "HYD", "BOM", "10:30", "12:00", 2, 3799, 8499),
                (9, "SC109", "BOM", "BLR", "16:00", "17:40", 4, 4599, 10499),
                (10, "SC110", "DEL", "BLR", "18:30", "21:10", 3, 6199, 13999),
                (11, "SC111", "GOI", "BLR", "09:00", "10:05", 1, 2799, 6999),
                (12, "SC112", "COK", "IXE", "13:30", "14:30", 1, 2499, 6499),
            ]
            self.conn.executemany("""
                INSERT INTO flights
                VALUES(?,?,?,?,?,?,?,?,?)
            """, flights)

        self.conn.commit()

    # --------------------------------------------------------
    # UI STYLE
    # --------------------------------------------------------
    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview",
                        rowheight=34,
                        font=("Segoe UI", 10),
                        background="white",
                        fieldbackground="white")
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"))

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def button(self, parent, text, command, width=16):
        # Custom rounded professional button.
        return RoundedButton(parent, text, command, width)

    def header(self, title, subtitle=""):
        bar = tk.Frame(self.root, bg="#071a2d", height=76)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        brand = tk.Frame(bar, bg="#071a2d")
        brand.pack(side="left", padx=28)

        tk.Label(
            brand, text="✈",
            bg="#071a2d", fg="#38bdf8",
            font=("Segoe UI Symbol", 25, "bold")
        ).pack(side="left", padx=(0, 8))

        tk.Label(
            brand, text="SKYCONNECT",
            bg="#071a2d", fg="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left")

        tk.Label(
            bar, text=title,
            bg="#071a2d", fg="#cbd5e1",
            font=("Segoe UI", 11)
        ).pack(side="right", padx=(15, 30))

        if title != "Search Flights":
            RoundedButton(
                bar, "HOME", self.show_home, 9,
                bg="#0f2b45", hover="#16405f"
            ).pack(side="right", padx=5)

        if title not in ("My Bookings", "Search Flights"):
            RoundedButton(
                bar, "MY BOOKINGS", self.show_bookings, 13,
                bg="#0f2b45", hover="#16405f"
            ).pack(side="right", padx=5)

        if subtitle:
            tk.Label(
                self.root, text=subtitle,
                bg="#eef3f8", fg="#64748b",
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=38, pady=(14, 2))

    def airport_name(self, code):
        row = self.conn.execute(
            "SELECT city FROM airports WHERE code=?", (code,)
        ).fetchone()
        return row["city"] if row else code

    # --------------------------------------------------------
    # HOME / SEARCH
    # --------------------------------------------------------
    def show_home(self):
        self.clear()
        self.header("Search Flights", "Book domestic flights quickly and securely.")

        # Airport-style hero background made with Canvas.
        canvas = tk.Canvas(self.root, height=225, bg="#0b2138", highlightthickness=0)
        canvas.pack(fill="x")
        canvas.create_rectangle(0, 0, 1200, 225, fill="#0b2138", outline="")
        canvas.create_rectangle(0, 165, 1200, 225, fill="#0d2a45", outline="")
        canvas.create_oval(850, -70, 1110, 190, fill="#17486a", outline="")
        canvas.create_oval(980, 35, 1260, 315, fill="#123a58", outline="")
        canvas.create_text(
            55, 70, anchor="w",
            text="Where will you fly today?",
            fill="white", font=("Segoe UI", 28, "bold")
        )
        canvas.create_text(
            55, 112, anchor="w",
            text="Search • Select • Book • Fly",
            fill="#c9e6ff", font=("Segoe UI", 14)
        )
        canvas.create_text(
            1030, 120, text="✈", fill="white",
            font=("Segoe UI", 58)
        )

        search = tk.Frame(self.root, bg="white", bd=0, highlightthickness=1,
                          highlightbackground="#d4dce5")
        search.place(relx=0.5, y=260, anchor="n", relwidth=0.90, height=220)

        # Search variables
        codes = [r["code"] for r in self.conn.execute(
            "SELECT code FROM airports ORDER BY city"
        ).fetchall()]

        self.from_var = tk.StringVar(value="IXE")
        self.to_var = tk.StringVar(value="BLR")
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.class_var = tk.StringVar(value="Economy")

        self.field(search, "FROM", self.from_var, codes, 25, 32)
        self.field(search, "TO", self.to_var, codes, 245, 32)

        tk.Label(search, text="DEPARTURE DATE", bg="white",
                 fg="#5b6675", font=("Segoe UI", 9, "bold")).place(x=465, y=30)
        tk.Entry(search, textvariable=self.date_var, font=("Segoe UI", 12),
                 relief="solid", bd=1).place(x=465, y=55, width=190, height=38)

        tk.Label(search, text="CLASS", bg="white",
                 fg="#5b6675", font=("Segoe UI", 9, "bold")).place(x=690, y=30)
        ttk.Combobox(search, textvariable=self.class_var,
                     values=["Economy", "Business"],
                     state="readonly", font=("Segoe UI", 11)).place(
                         x=690, y=55, width=180, height=38)

        self.button(search, "SEARCH FLIGHTS", self.search_flights, 17).place(
            x=895, y=53
        )

        trust = tk.Frame(self.root, bg="#eef3f8")
        trust.pack(pady=(142, 8))
        for txt in ("✓ Secure booking", "✓ Instant confirmation", "✓ Easy cancellation"):
            tk.Label(trust, text=txt, bg="#eef3f8", fg="#475569",
                     font=("Segoe UI", 9, "bold")).pack(side="left", padx=22)

        self.button(self.root, "MY BOOKINGS", self.show_bookings, 16).pack(
            pady=(5, 10)
        )

        tk.Label(
            self.root,
            text="Demo booking system • No real payment is processed",
            bg="#eef3f8", fg="#718096",
            font=("Segoe UI", 9)
        ).pack()

    def field(self, parent, label, variable, values, x, y):
        tk.Label(parent, text=label, bg="white", fg="#5b6675",
                 font=("Segoe UI", 9, "bold")).place(x=x, y=y)
        cb = ttk.Combobox(parent, textvariable=variable,
                          values=values, state="readonly",
                          font=("Segoe UI", 11))
        cb.place(x=x, y=y+25, width=180, height=38)

    def search_flights(self):
        source = self.from_var.get()
        destination = self.to_var.get()
        travel_date = self.date_var.get()

        if source == destination:
            messagebox.showerror("Invalid route",
                                 "Source and destination must be different.")
            return

        try:
            datetime.strptime(travel_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Enter the date in YYYY-MM-DD format."
            )
            return

        rows = self.conn.execute("""
            SELECT f.*, a1.city AS source_city, a2.city AS destination_city,
                   ac.model, ac.capacity
            FROM flights f
            JOIN airports a1 ON f.source=a1.code
            JOIN airports a2 ON f.destination=a2.code
            JOIN aircraft ac ON f.aircraft_id=ac.aircraft_id
            WHERE f.source=? AND f.destination=?
            ORDER BY f.depart
        """, (source, destination)).fetchall()

        # If there is no direct flight, offer connecting routes.
        if not rows:
            self.search_connecting(source, destination, travel_date)
        else:
            self.show_results(rows, source, destination, travel_date)

    def search_connecting(self, source, destination, travel_date):
        rows = self.conn.execute("""
            SELECT
                f1.flight_id AS f1id, f1.flight_no AS f1no,
                f1.depart AS f1depart, f1.arrive AS f1arrive,
                f1.economy_fare AS f1eco, f1.business_fare AS f1biz,
                f1.destination AS middle,
                f2.flight_id AS f2id, f2.flight_no AS f2no,
                f2.depart AS f2depart, f2.arrive AS f2arrive,
                f2.economy_fare AS f2eco, f2.business_fare AS f2biz
            FROM flights f1
            JOIN flights f2
              ON f1.destination=f2.source
            WHERE f1.source=? AND f2.destination=?
              AND f1.destination<>?
            ORDER BY f1.depart
        """, (source, destination, destination)).fetchall()

        self.clear()
        self.header("Connecting Flights",
                     f"{self.airport_name(source)} → {self.airport_name(destination)}")

        body = tk.Frame(self.root, bg="#eef3f8")
        body.pack(fill="both", expand=True, padx=35, pady=20)

        if not rows:
            tk.Label(body, text="No flights found.",
                     bg="#eef3f8", fg="#334155",
                     font=("Segoe UI", 18, "bold")).pack(pady=80)
            self.button(body, "NEW SEARCH", self.show_home).pack()
            return

        tk.Label(body, text="Connecting itineraries",
                 bg="#eef3f8", font=("Segoe UI", 18, "bold")).pack(anchor="w")

        for r in rows:
            card = tk.Frame(body, bg="white", bd=1, relief="solid")
            card.pack(fill="x", pady=8)

            fare = (r["f1eco"] + r["f2eco"])
            text = (
                f'{r["f1no"]}  {r["f1depart"]} → {r["f1arrive"]}   '
                f'•   {r["f2no"]}  {r["f2depart"]} → {r["f2arrive"]}\n'
                f'1 stop at {self.airport_name(r["middle"])}     '
                f'From ₹{fare:,.0f}'
            )
            tk.Label(card, text=text, bg="white", justify="left",
                     font=("Segoe UI", 11)).pack(side="left", padx=20, pady=16)

            self.button(
                card, "SELECT",
                lambda x=r: self.select_connecting(x),
                12
            ).pack(side="right", padx=20)

        self.button(self.root, "BACK", self.show_home).pack(pady=15)

    def select_connecting(self, row):
        # The first leg is selected for the demo booking flow.
        # The second leg is stored as the connecting flight.
        first = self.conn.execute("""
            SELECT f.*, a1.city AS source_city, a2.city AS destination_city,
                   ac.model, ac.capacity
            FROM flights f
            JOIN airports a1 ON f.source=a1.code
            JOIN airports a2 ON f.destination=a2.code
            JOIN aircraft ac ON f.aircraft_id=ac.aircraft_id
            WHERE f.flight_id=?
        """, (row["f1id"],)).fetchone()

        self.selected_flight = dict(first)
        self.selected_flight["connecting_flight_id"] = row["f2id"]
        self.selected_flight["connecting_flight_no"] = row["f2no"]
        self.show_booking()

    def show_results(self, rows, source, destination, travel_date):
        self.clear()
        self.header(
            "Available Flights",
            f"{self.airport_name(source)} ({source}) → "
            f"{self.airport_name(destination)} ({destination}) • {travel_date}"
        )

        outer = tk.Frame(self.root, bg="#eef3f8")
        outer.pack(fill="both", expand=True, padx=35, pady=20)

        for r in rows:
            self.flight_card(outer, r)

        self.button(self.root, "BACK TO SEARCH", self.show_home).pack(pady=15)

    def flight_card(self, parent, r):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", pady=7)

        left = tk.Frame(card, bg="white")
        left.pack(side="left", fill="x", expand=True, padx=20, pady=15)

        tk.Label(left, text=r["flight_no"], bg="white",
                 font=("Segoe UI", 14, "bold"), fg="#0f2942").pack(anchor="w")

        tk.Label(left,
                 text=f'{r["source_city"]} ({r["source"]})   '
                      f'{r["depart"]}   →   {r["arrive"]}   '
                      f'{r["destination_city"]} ({r["destination"]})',
                 bg="white", fg="#334155",
                 font=("Segoe UI", 11)).pack(anchor="w", pady=5)

        tk.Label(left, text=f'{r["model"]} •  {r["capacity"]} seats',
                 bg="white", fg="#718096",
                 font=("Segoe UI", 9)).pack(anchor="w")

        right = tk.Frame(card, bg="white")
        right.pack(side="right", padx=20, pady=15)

        tk.Label(right, text=f'Economy  ₹{r["economy_fare"]:,.0f}',
                 bg="white", fg="#374151",
                 font=("Segoe UI", 10, "bold")).pack(anchor="e")

        tk.Label(right, text=f'Business  ₹{r["business_fare"]:,.0f}',
                 bg="white", fg="#374151",
                 font=("Segoe UI", 10)).pack(anchor="e", pady=(3, 8))

        self.button(
            right, "SELECT FLIGHT",
            lambda x=dict(r): self.select_flight(x),
            15
        ).pack()

    def select_flight(self, flight):
        self.selected_flight = flight
        self.show_booking()

    # --------------------------------------------------------
    # BOOKING
    # --------------------------------------------------------
    def show_booking(self):
        self.clear()
        f = self.selected_flight

        self.header("Passenger & Seat Details",
                     f'{f["flight_no"]} • {f["source_city"]} → {f["destination_city"]}')

        main = tk.Frame(self.root, bg="#eef3f8")
        main.pack(fill="both", expand=True, padx=35, pady=15)

        left = tk.Frame(main, bg="white", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(main, bg="white", bd=1, relief="solid")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Passenger section
        tk.Label(left, text="Passenger Information",
                 bg="white", fg="#0f2942",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25, pady=(22, 15))

        self.name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.passport_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()

        self.entry_field(left, "Full Name *", self.name_var)
        self.entry_field(left, "Date of Birth (YYYY-MM-DD)", self.dob_var)
        self.entry_field(left, "Passport Number", self.passport_var)
        self.entry_field(left, "Mobile Number *", self.phone_var)
        self.entry_field(left, "Email", self.email_var)

        # Class
        tk.Label(left, text="Travel Class",
                 bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=25, pady=(5, 4))

        self.class_booking = tk.StringVar(value=self.selected_class)
        class_box = ttk.Combobox(
            left, textvariable=self.class_booking,
            values=["Economy", "Business"],
            state="readonly", font=("Segoe UI", 11)
        )
        class_box.pack(fill="x", padx=25, ipady=6)
        class_box.bind("<<ComboboxSelected>>", self.refresh_booking_summary)

        # Summary
        self.summary = tk.Label(
            left, text="", bg="white", justify="left",
            fg="#334155", font=("Segoe UI", 10)
        )
        self.summary.pack(anchor="w", padx=25, pady=18)

        # Right side seat map
        tk.Label(right, text="Choose Your Seat",
                 bg="white", fg="#0f2942",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25, pady=(22, 5))

        tk.Label(right, text="Green = Available   Red = Occupied   Blue = Selected",
                 bg="white", fg="#64748b",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=25, pady=(0, 12))

        seat_frame = tk.Frame(right, bg="white")
        seat_frame.pack(fill="both", expand=True, padx=20)

        self.seat_buttons = {}
        self.build_seat_map(seat_frame)

        bottom = tk.Frame(self.root, bg="#eef3f8")
        bottom.pack(fill="x", padx=35, pady=10)

        self.button(bottom, "BACK", self.show_home, 10).pack(side="left")
        self.button(bottom, "CONTINUE TO PAYMENT",
                    self.validate_and_payment, 22).pack(side="right")

        self.refresh_booking_summary()

    def entry_field(self, parent, label, variable):
        tk.Label(parent, text=label, bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=25, pady=(5, 3))
        tk.Entry(parent, textvariable=variable,
                 font=("Segoe UI", 11), relief="solid", bd=1).pack(
                     fill="x", padx=25, ipady=6, pady=(0, 5)
                 )

    def occupied_seats(self, flight_id):
        rows = self.conn.execute("""
            SELECT seat FROM bookings
            WHERE flight_id=? AND status='Confirmed'
        """, (flight_id,)).fetchall()
        return {r["seat"] for r in rows}

    def build_seat_map(self, parent):
        occupied = self.occupied_seats(self.selected_flight["flight_id"])
        capacity = self.selected_flight["capacity"]

        # Display up to the aircraft capacity. For very large aircraft,
        # the map remains scrollable.
        canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient="vertical",
                                command=canvas.yview)
        inner = tk.Frame(canvas, bg="white")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        columns = ["A", "B", "C", "D", "E", "F"]
        rows_needed = (capacity + 5) // 6

        for row in range(1, rows_needed + 1):
            for col, letter in enumerate(columns):
                number = (row - 1) * 6 + col + 1
                if number > capacity:
                    break

                seat = f"{number}{letter}"
                occupied_flag = seat in occupied

                btn = tk.Button(
                    inner, text=seat,
                    width=5, height=1,
                    relief="flat",
                    font=("Segoe UI", 8, "bold"),
                    cursor="hand2" if not occupied_flag else "arrow",
                    bg="#e8f5e9" if not occupied_flag else "#ef4444",
                    fg="#166534" if not occupied_flag else "white",
                    state="normal" if not occupied_flag else "disabled"
                )

                if not occupied_flag:
                    btn.configure(command=lambda s=seat: self.select_seat(s))

                btn.grid(row=row, column=col, padx=3, pady=3)
                self.seat_buttons[seat] = btn

    def select_seat(self, seat):
        for s, btn in self.seat_buttons.items():
            if btn["state"] != "disabled":
                btn.configure(bg="#e8f5e9", fg="#166534")

        self.selected_seat = seat
        self.seat_buttons[seat].configure(bg="#2563eb", fg="white")
        self.refresh_booking_summary()

    def refresh_booking_summary(self, event=None):
        if not hasattr(self, "summary"):
            return

        cls = self.class_booking.get()
        fare = (
            self.selected_flight["business_fare"]
            if cls == "Business"
            else self.selected_flight["economy_fare"]
        )
        self.selected_class = cls

        text = (
            f'Flight ID: {self.selected_flight["flight_id"]}\n'
            f'Flight: {self.selected_flight["flight_no"]}\n'
            f'Route: {self.selected_flight["source"]} → '
            f'{self.selected_flight["destination"]}\n'
            f'Class: {cls}\n'
            f'Seat: {self.selected_seat or "Not selected"}\n'
            f'Fare: ₹{fare:,.2f}'
        )

        if self.selected_flight.get("connecting_flight_no"):
            text += (
                f'\nConnecting flight: '
                f'{self.selected_flight["connecting_flight_no"]}'
            )

        self.summary.configure(text=text)

    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------
    def validate_and_payment(self):
        if not self.name_var.get().strip():
            messagebox.showerror("Missing information",
                                 "Enter the passenger name.")
            return

        if not self.phone_var.get().strip():
            messagebox.showerror("Missing information",
                                 "Enter the mobile number.")
            return

        if not self.selected_seat:
            messagebox.showerror("Seat required",
                                 "Please select an available seat.")
            return

        if self.passport_var.get().strip():
            existing = self.conn.execute(
                "SELECT passenger_id FROM passengers WHERE passport=?",
                (self.passport_var.get().strip(),)
            ).fetchone()
            if existing:
                # Existing passenger is allowed only if the entered details
                # are being reused; use that passenger ID.
                self.passenger_id = existing["passenger_id"]
            else:
                self.passenger_id = None
        else:
            self.passenger_id = None

        self.show_payment()

    def show_payment(self):
        self.clear()
        self.header("Secure Payment", "Demo payment screen — no real money is charged.")

        f = self.selected_flight
        cls = self.class_booking.get()
        fare = f["business_fare"] if cls == "Business" else f["economy_fare"]

        box = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        box.pack(fill="both", expand=True, padx=180, pady=35)

        tk.Label(box, text="Payment Summary",
                 bg="white", fg="#0f2942",
                 font=("Segoe UI", 20, "bold")).pack(pady=(25, 15))

        details = (
            f'Flight ID: {f["flight_id"]}\n'
            f'Flight: {f["flight_no"]}\n'
            f'Route: {f["source"]} → {f["destination"]}\n'
            f'Passenger: {self.name_var.get()}\n'
            f'Seat: {self.selected_seat}\n'
            f'Class: {cls}\n\n'
            f'TOTAL: ₹{fare:,.2f}'
        )

        tk.Label(box, text=details, bg="white",
                 fg="#334155", justify="left",
                 font=("Segoe UI", 12)).pack(pady=10)

        tk.Label(box, text="Payment Method",
                 bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(pady=(20, 5))

        self.payment_method = tk.StringVar(value="UPI")
        ttk.Combobox(
            box, textvariable=self.payment_method,
            values=["UPI", "Credit Card", "Debit Card", "Net Banking"],
            state="readonly", font=("Segoe UI", 11)
        ).pack(ipady=5, padx=100, fill="x")

        # Demo card/UPI field
        self.payment_ref = tk.StringVar()
        tk.Label(box, text="Payment ID / UPI / Card Reference",
                 bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(pady=(15, 5))
        tk.Entry(box, textvariable=self.payment_ref,
                 font=("Segoe UI", 11), relief="solid", bd=1).pack(
                     ipady=6, padx=100, fill="x"
                 )

        bottom = tk.Frame(box, bg="white")
        bottom.pack(pady=30)

        self.button(bottom, "BACK", self.show_booking, 12).pack(
            side="left", padx=8
        )
        self.button(bottom, "PAY & CONFIRM BOOKING",
                    lambda: self.complete_booking(fare), 24).pack(
                        side="left", padx=8
                    )

    def complete_booking(self, fare):
        if not self.payment_ref.get().strip():
            messagebox.showerror("Payment details",
                                 "Enter a demo payment reference.")
            return

        # Passenger: reuse by passport when available; otherwise create.
        passenger_id = getattr(self, "passenger_id", None)

        if passenger_id is None:
            passport = self.passport_var.get().strip() or None
            try:
                cur = self.conn.execute("""
                    INSERT INTO passengers
                    (name,dob,passport,phone,email)
                    VALUES(?,?,?,?,?)
                """, (
                    self.name_var.get().strip(),
                    self.dob_var.get().strip(),
                    passport,
                    self.phone_var.get().strip(),
                    self.email_var.get().strip()
                ))
                passenger_id = cur.lastrowid
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Passenger error",
                    "That passport number is already registered."
                )
                return

        # Create trip automatically.
        trip_code = "TR" + datetime.now().strftime("%y%m%d%H%M%S%f")[-10:]
        cur = self.conn.execute("""
            INSERT INTO trips(trip_code,created_at)
            VALUES(?,?)
        """, (trip_code, datetime.now().isoformat(timespec="seconds")))
        trip_id = cur.lastrowid

        pnr = "SC" + datetime.now().strftime("%H%M%S%f")[-8:]

        try:
            cur = self.conn.execute("""
                INSERT INTO bookings
                (pnr,trip_id,passenger_id,flight_id,seat,
                 travel_class,fare,booking_date,status)
                VALUES(?,?,?,?,?,?,?,?,?)
            """, (
                pnr, trip_id, passenger_id,
                self.selected_flight["flight_id"],
                self.selected_seat,
                self.class_booking.get(),
                fare,
                date.today().isoformat(),
                "Confirmed"
            ))

            booking_id = cur.lastrowid

            self.conn.execute("""
                INSERT INTO payments
                (booking_id,amount,method,status,paid_at)
                VALUES(?,?,?,?,?)
            """, (
                booking_id, fare,
                self.payment_method.get(),
                "Paid",
                datetime.now().isoformat(timespec="seconds")
            ))

            self.conn.commit()

            self.current_booking = {
                "booking_id": booking_id,
                "pnr": pnr,
                "trip_id": trip_id,
                "passenger_id": passenger_id,
                "flight_id": self.selected_flight["flight_id"],
                "fare": fare,
                "seat": self.selected_seat
            }

            self.show_confirmation()

        except sqlite3.IntegrityError:
            self.conn.rollback()
            messagebox.showerror(
                "Seat unavailable",
                "That seat was just booked. Please choose another seat."
            )
            self.show_booking()

    # --------------------------------------------------------
    # CONFIRMATION
    # --------------------------------------------------------
    def show_confirmation(self):
        self.clear()
        self.header("Booking Confirmed", "Your demo reservation has been created.")

        box = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        box.pack(fill="both", expand=True, padx=220, pady=45)

        tk.Label(box, text="✓",
                 bg="white", fg="#16a34a",
                 font=("Segoe UI", 55, "bold")).pack(pady=(20, 0))

        tk.Label(box, text="Booking Confirmed!",
                 bg="white", fg="#0f2942",
                 font=("Segoe UI", 24, "bold")).pack()

        b = self.current_booking

        details = (
            f'PNR: {b["pnr"]}\n'
            f'Passenger ID: {b["passenger_id"]}\n'
            f'Trip ID: {b["trip_id"]}\n'
            f'Flight ID: {b["flight_id"]}\n'
            f'Seat: {b["seat"]}\n'
            f'Class: {self.class_booking.get()}\n'
            f'Fare: ₹{b["fare"]:,.2f}\n'
            f'Status: CONFIRMED'
        )

        tk.Label(box, text=details,
                 bg="white", fg="#334155",
                 justify="left", font=("Segoe UI", 12)).pack(pady=20)

        buttons = tk.Frame(box, bg="white")
        buttons.pack(pady=15)

        self.button(buttons, "NEW SEARCH", self.show_home, 14).pack(
            side="left", padx=8
        )
        self.button(buttons, "MY BOOKINGS", self.show_bookings, 14).pack(
            side="left", padx=8
        )

    # --------------------------------------------------------
    # MY BOOKINGS
    # --------------------------------------------------------
    def show_bookings(self):
        self.clear()
        self.header("My Bookings", "View and cancel reservations stored in this application.")

        frame = tk.Frame(self.root, bg="#eef3f8")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        columns = ("PNR", "Passenger", "Flight", "Route",
                   "Seat", "Class", "Fare", "Status")

        tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=125, anchor="center")

        tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(frame, orient="vertical",
                               command=tree.yview)
        scroll.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scroll.set)

        rows = self.conn.execute("""
            SELECT b.*, p.name AS passenger,
                   f.flight_no,
                   f.source || ' → ' || f.destination AS route
            FROM bookings b
            JOIN passengers p ON b.passenger_id=p.passenger_id
            JOIN flights f ON b.flight_id=f.flight_id
            ORDER BY b.booking_id DESC
        """).fetchall()

        for r in rows:
            tree.insert("", "end", iid=str(r["booking_id"]),
                        values=(
                            r["pnr"], r["passenger"],
                            r["flight_no"], r["route"],
                            r["seat"], r["travel_class"],
                            f'₹{r["fare"]:,.0f}', r["status"]
                        ))

        controls = tk.Frame(self.root, bg="#eef3f8")
        controls.pack(pady=10)

        self.button(
            controls, "CANCEL SELECTED",
            lambda: self.cancel_booking(tree),
            18
        ).pack(side="left", padx=8)

        self.button(
            controls, "BACK TO HOME",
            self.show_home, 15
        ).pack(side="left", padx=8)

    def cancel_booking(self, tree):
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select booking",
                "Select a booking first."
            )
            return

        booking_id = int(selected[0])

        if not messagebox.askyesno(
            "Cancel booking",
            "Are you sure you want to cancel this booking?"
        ):
            return

        self.conn.execute("""
            UPDATE bookings
            SET status='Cancelled'
            WHERE booking_id=?
        """, (booking_id,))

        self.conn.execute("""
            UPDATE payments
            SET status='Refund Pending'
            WHERE booking_id=?
        """, (booking_id,))

        self.conn.commit()

        messagebox.showinfo(
            "Cancelled",
            "Booking cancelled successfully."
        )

        self.show_bookings()

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------
    def close(self):
        self.conn.close()
        self.root.destroy()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AirlineApp(root)
    root.mainloop()
