import customtkinter as ctk
from tkinter import messagebox, Toplevel
from tkcalendar import Calendar
from datetime import datetime, timedelta
import os
import csv
import hashlib
import uuid
import json

# Medical-themed color palette
MEDICAL_BLUE = "#0077b6"
MEDICAL_LIGHT_BLUE = "#90e0ef"
MEDICAL_WHITE = "#f8f9fa"
MEDICAL_GRAY = "#e9ecef"
MEDICAL_DARK_BLUE = "#023e8a"
MEDICAL_GREEN = "#2a9d8f"
MEDICAL_RED = "#e63946"

DOCTOR_CREDENTIALS = {
    "dr_smith": "password123",
    "dr_johnson": "password123",
    "dr_williams": "password123",
    "dr_brown": "password123",
    "dr_davis": "password123"
}

DOCTOR_NAMES = {
    "dr_smith": "Dr. Smith (Cardiology)",
    "dr_johnson": "Dr. Johnson (Pediatrics)",
    "dr_williams": "Dr. Williams (Neurology)",
    "dr_brown": "Dr. Brown (Orthopedics)",
    "dr_davis": "Dr. Davis (Dermatology)"
}

# ======================== DATABASE FUNCTIONS ========================
DB_FOLDER = "user_database"
APPOINTMENT_FILE = "appointments.json"
USER_APPOINTMENT_FILE = "user_appointments.json"  # New file to track user-specific appointments
os.makedirs(DB_FOLDER, exist_ok=True)


def hash_password(password):
    """Hash a password for storing."""
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def verify_password(hashed_password, user_password):
    """Verify a stored password against one provided by user"""
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def verify_doctor_login(username, password):
    """Verify doctor credentials"""
    return username in DOCTOR_CREDENTIALS and DOCTOR_CREDENTIALS[username] == password

def save_user_data(username, email, phone, password):
    """Save user data to a CSV file (one file per user)"""
    filename = os.path.join(DB_FOLDER, f"{username}.csv")
    hashed_pw = hash_password(password)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["username", "email", "phone", "password"])
        writer.writerow([username, email, phone, hashed_pw])


def check_user_exists(username):
    """Check if user exists in database"""
    filename = os.path.join(DB_FOLDER, f"{username}.csv")
    return os.path.exists(filename)


def verify_login(username, password):
    """Verify user credentials"""
    filename = os.path.join(DB_FOLDER, f"{username}.csv")
    if not os.path.exists(filename):
        return False

    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if verify_password(row['password'], password):
                return True
    return False


def load_appointments():
    """Load appointments from JSON file"""
    if not os.path.exists(APPOINTMENT_FILE):
        # Initialize with sample doctors and availability
        return {
            "Dr. Smith (Cardiology)": {},
            "Dr. Johnson (Pediatrics)": {},
            "Dr. Williams (Neurology)": {},
            "Dr. Brown (Orthopedics)": {},
            "Dr. Davis (Dermatology)": {}
        }

    with open(APPOINTMENT_FILE, 'r') as file:
        try:
            data = json.load(file)
            # Ensure all default doctors are present
            default_doctors = ["Dr. Smith (Cardiology)", "Dr. Johnson (Pediatrics)",
                               "Dr. Williams (Neurology)", "Dr. Brown (Orthopedics)",
                               "Dr. Davis (Dermatology)"]
            for doctor in default_doctors:
                if doctor not in data:
                    data[doctor] = {}
            return data
        except json.JSONDecodeError:
            return {
                "Dr. Smith (Cardiology)": {},
                "Dr. Johnson (Pediatrics)": {},
                "Dr. Williams (Neurology)": {},
                "Dr. Brown (Orthopedics)": {},
                "Dr. Davis (Dermatology)": {}
            }


def save_appointments(appointments):
    """Save appointments to JSON file"""
    with open(APPOINTMENT_FILE, 'w') as file:
        json.dump(appointments, file)


def load_user_appointments(username):
    """Load user-specific appointments"""
    if not os.path.exists(USER_APPOINTMENT_FILE):
        return []

    with open(USER_APPOINTMENT_FILE, 'r') as file:
        try:
            data = json.load(file)
            return data.get(username, [])
        except json.JSONDecodeError:
            return []


def save_user_appointments(username, appointments):
    """Save user-specific appointments"""
    all_data = {}
    if os.path.exists(USER_APPOINTMENT_FILE):
        with open(USER_APPOINTMENT_FILE, 'r') as file:
            try:
                all_data = json.load(file)
            except json.JSONDecodeError:
                all_data = {}

    all_data[username] = appointments

    with open(USER_APPOINTMENT_FILE, 'w') as file:
        json.dump(all_data, file)


# ======================== DASHBOARD CLASS ========================
class Dashboard:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.appointments = load_appointments()
        self.user_appointments = load_user_appointments(username)
        self.setup_ui()

    def setup_ui(self):
        self.master.geometry("1200x800")
        self.master.title(f"HopeSaver Dashboard - {self.username}")
        self.master.resizable(False, False)

        # Main container
        self.main_container = ctk.CTkFrame(self.master, fg_color=MEDICAL_WHITE)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, fg_color=MEDICAL_BLUE, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo placeholder
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            width=200,
            height=100,
            fg_color=MEDICAL_WHITE,
            corner_radius=10
        )
        logo_frame.pack(pady=(20, 30), padx=20)

        ctk.CTkLabel(
            logo_frame,
            text="HopeSaver",
            font=("Arial", 20, "bold"),
            text_color=MEDICAL_BLUE
        ).pack(expand=True)

        # Sidebar header
        sidebar_header = ctk.CTkLabel(
            self.sidebar,
            text=f"Welcome,\n{self.username}",
            font=("Arial", 16, "bold"),
            text_color=MEDICAL_WHITE
        )
        sidebar_header.pack(pady=(0, 30), padx=10)

        # Sidebar buttons
        buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📅 Make Appointment", self.show_appointment_form),
            ("🩺 My Appointments", self.show_appointments)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=("Arial", 14),
                fg_color="transparent",
                hover_color=MEDICAL_LIGHT_BLUE,
                text_color=MEDICAL_WHITE,
                anchor="w",
                command=command,
                height=45,
                border_spacing=15,
                corner_radius=8
            )
            btn.pack(fill="x", padx=15, pady=5)

        # Spacer to push logout button to bottom
        ctk.CTkFrame(self.sidebar, height=0, fg_color="transparent").pack(expand=True)

        # Logout button
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            font=("Arial", 14),
            fg_color=MEDICAL_RED,
            hover_color="#c1121f",
            text_color=MEDICAL_WHITE,
            height=45,
            corner_radius=8,
            command=self.logout
        )
        logout_btn.pack(side="bottom", pady=(0, 30), padx=15, fill="x")

        # Main content area
        self.content_area = ctk.CTkFrame(self.main_container, fg_color=MEDICAL_GRAY)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Show default view
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()

        # Main container with padding
        main_container = ctk.CTkFrame(self.content_area, fg_color=MEDICAL_GRAY)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color=MEDICAL_GRAY)
        scroll_frame.pack(fill="both", expand=True)

        # Header Section
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Welcome back, {self.username}",
            font=("Arial", 28, "bold"),
            text_color=MEDICAL_BLUE
        )
        welcome_label.pack(side="left")

        date_label = ctk.CTkLabel(
            header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("Arial", 16),
            text_color=MEDICAL_DARK_BLUE
        )
        date_label.pack(side="right")

        # Stats Cards Section
        stats_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))

        # Calculate stats
        now = datetime.now()
        upcoming_count = len([a for a in self.user_appointments
                              if datetime.strptime(a['date'], "%m/%d/%Y") >= now])
        past_count = len([a for a in self.user_appointments
                          if datetime.strptime(a['date'], "%m/%d/%Y") < now])
        cancelled_count = len([a for a in self.user_appointments if a.get('status') == 'Cancelled'])
        doctors_count = len({a['doctor'] for a in self.user_appointments})

        stats = [
            ("🩺 Upcoming", upcoming_count, MEDICAL_GREEN),
            ("📅 Past", past_count, MEDICAL_BLUE),
            ("❌ Cancelled", cancelled_count, MEDICAL_RED),
            ("👨‍⚕️ Doctors", doctors_count, MEDICAL_DARK_BLUE)
        ]

        for stat_name, stat_value, color in stats:
            card = ctk.CTkFrame(
                stats_frame,
                fg_color=MEDICAL_WHITE,
                border_width=1,
                border_color="#dee2e6",
                corner_radius=10
            )
            card.pack(side="left", padx=10, fill="both", expand=True)

            # Card content
            ctk.CTkLabel(
                card,
                text=stat_name,
                font=("Arial", 14),
                text_color="#6c757d"
            ).pack(pady=(15, 5), padx=15, anchor="w")

            ctk.CTkLabel(
                card,
                text=str(stat_value),
                font=("Arial", 28, "bold"),
                text_color=color
            ).pack(pady=(0, 15), padx=15, anchor="w")

        # Upcoming Appointments Section
        upcoming_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=MEDICAL_WHITE,
            border_width=1,
            border_color="#dee2e6",
            corner_radius=10
        )
        upcoming_frame.pack(fill="x", pady=(0, 30))

        # Section header
        section_header = ctk.CTkFrame(upcoming_frame, fg_color=MEDICAL_DARK_BLUE, height=50, corner_radius=10)
        section_header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            section_header,
            text="Your Upcoming Appointments",
            font=("Arial", 18, "bold"),
            text_color=MEDICAL_WHITE
        ).pack(side="left", padx=15)

        # Get upcoming appointments (next 30 days)
        upcoming_appointments = [
                                    a for a in self.user_appointments
                                    if datetime.strptime(a['date'], "%m/%d/%Y") >= now and
                                       (datetime.strptime(a['date'], "%m/%d/%Y") - now).days <= 30 and
                                       a.get('status') != 'Cancelled'
                                ][:3]  # Show only the next 3 appointments

        if not upcoming_appointments:
            ctk.CTkLabel(
                upcoming_frame,
                text="No upcoming appointments in the next 30 days",
                font=("Arial", 14),
                text_color="#6c757d"
            ).pack(pady=30)
        else:
            for appt in upcoming_appointments:
                appt_card = ctk.CTkFrame(
                    upcoming_frame,
                    fg_color=MEDICAL_LIGHT_BLUE,
                    corner_radius=8
                )
                appt_card.pack(fill="x", padx=10, pady=5)

                # Appointment info
                info_frame = ctk.CTkFrame(appt_card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

                # Doctor and date
                ctk.CTkLabel(
                    info_frame,
                    text=f"👨‍⚕️ {appt['doctor']}",
                    font=("Arial", 16, "bold"),
                    text_color=MEDICAL_DARK_BLUE,
                    anchor="w"
                ).pack(fill="x")

                ctk.CTkLabel(
                    info_frame,
                    text=f"📅 {appt['date']} at ⏰ {appt['time']}",
                    font=("Arial", 14),
                    text_color=MEDICAL_DARK_BLUE,
                    anchor="w"
                ).pack(fill="x", pady=(5, 0))

                # Status
                status_frame = ctk.CTkFrame(appt_card, fg_color="transparent")
                status_frame.pack(side="right", padx=10, pady=10)

                status_label = ctk.CTkLabel(
                    status_frame,
                    text=f"Status: {appt.get('status', 'Confirmed')}",
                    font=("Arial", 14),
                    text_color=MEDICAL_DARK_BLUE
                )
                status_label.pack(side="left", padx=(0, 10))

                # Add cancel button for upcoming appointments
                if appt.get('status') == 'Confirmed':
                    cancel_btn = ctk.CTkButton(
                        status_frame,
                        text="Cancel",
                        width=100,
                        fg_color=MEDICAL_RED,
                        hover_color="#c1121f",
                        font=("Arial", 12),
                        command=lambda a=appt: self.cancel_appointment_from_dashboard(a)
                    )
                    cancel_btn.pack(side="right")

        # Recent Activity Section
        activity_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=MEDICAL_WHITE,
            border_width=1,
            border_color="#dee2e6",
            corner_radius=10
        )
        activity_frame.pack(fill="x")

        # Section header
        section_header = ctk.CTkFrame(activity_frame, fg_color=MEDICAL_BLUE, height=50, corner_radius=10)
        section_header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            section_header,
            text="Recent Activity",
            font=("Arial", 18, "bold"),
            text_color=MEDICAL_WHITE
        ).pack(side="left", padx=15)

        # Generate recent activity
        recent_activity = []
        for appt in sorted(
                self.user_appointments,
                key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y"),
                reverse=True
        )[:5]:  # Show only the 5 most recent
            if datetime.strptime(appt['date'], "%m/%d/%Y") < now:
                status = "Completed"
                icon = "✅"
                color = MEDICAL_GREEN
            elif appt.get('status') == 'Cancelled':
                status = "Cancelled"
                icon = "❌"
                color = MEDICAL_RED
            else:
                status = "Upcoming"
                icon = "⏳"
                color = MEDICAL_BLUE

            recent_activity.append((
                f"{icon} {status} visit with {appt['doctor']}",
                f"on {appt['date']} at {appt['time']}",
                color
            ))

        if not recent_activity:
            ctk.CTkLabel(
                activity_frame,
                text="No recent activity",
                font=("Arial", 14),
                text_color="#6c757d"
            ).pack(pady=30)
        else:
            for activity, date, color in recent_activity:
                activity_item = ctk.CTkFrame(activity_frame, fg_color="transparent")
                activity_item.pack(fill="x", padx=15, pady=10)

                # Activity icon and text
                ctk.CTkLabel(
                    activity_item,
                    text=activity,
                    font=("Arial", 14),
                    text_color=color,
                    anchor="w"
                ).pack(side="left", fill="x", expand=True)

                # Date
                ctk.CTkLabel(
                    activity_item,
                    text=date,
                    font=("Arial", 12),
                    text_color="#6c757d",
                    anchor="e"
                ).pack(side="right")

                # Separator
                if activity != recent_activity[-1][0]:
                    ctk.CTkFrame(
                        activity_item,
                        height=1,
                        fg_color="#dee2e6"
                    ).pack(fill="x", pady=5)

    def cancel_appointment_from_dashboard(self, appointment):
        """Cancel an appointment from the dashboard view"""
        if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this appointment?"):
            # Update the appointment status
            for appt in self.user_appointments:
                if (appt['doctor'] == appointment['doctor'] and
                        appt['date'] == appointment['date'] and
                        appt['time'] == appointment['time']):
                    appt['status'] = 'Cancelled'
                    break

            # Save the updated user appointments
            save_user_appointments(self.username, self.user_appointments)

            # Update the main appointments data
            doctor = appointment['doctor']
            date = appointment['date']
            time = appointment['time']

            if doctor in self.appointments and date in self.appointments[doctor]:
                if time in self.appointments[doctor][date]:
                    self.appointments[doctor][date].remove(time)
                    save_appointments(self.appointments)

            # Refresh the dashboard
            self.show_dashboard()
            messagebox.showinfo("Success", "Appointment cancelled successfully")

    def show_appointment_form(self):
        self.clear_content()

        title = ctk.CTkLabel(
            self.content_area,
            text="Schedule Appointment",
            font=("Arial", 24, "bold"),
            text_color=MEDICAL_BLUE
        )
        title.pack(pady=30)

        form_frame = ctk.CTkFrame(self.content_area, fg_color=MEDICAL_WHITE, corner_radius=10)
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # All possible time slots (9AM to 5PM)
        self.all_time_slots = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
                               "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"]

        self.selected_date = None
        self.selected_time = None

        # Form fields with medical theme (removed Date of Birth)
        fields = [
            ("Patient's Name", "Enter full name"),
            ("Contact Number", "Enter phone number"),
            ("Insurance Provider", "Enter insurance information"),
            ("Doctor", "Select doctor"),
            ("Date", "Select date"),
            ("Time", "Select time"),
            ("Reason for Visit", "Describe your symptoms")
        ]

        self.form_entries = {}

        for i, (field_name, placeholder) in enumerate(fields):
            frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            frame.pack(pady=10, padx=20, fill="x")

            ctk.CTkLabel(
                frame,
                text=field_name + ":",
                font=("Arial", 14),
                anchor="w",
                text_color=MEDICAL_BLUE
            ).pack(side="left", padx=5)

            if field_name == "Doctor":
                self.doctor_var = ctk.StringVar()
                doctors = list(self.appointments.keys())
                entry = ctk.CTkComboBox(
                    frame,
                    variable=self.doctor_var,
                    values=doctors,
                    width=300,
                    dropdown_fg_color=MEDICAL_WHITE,
                    button_color=MEDICAL_BLUE,
                    command=self.update_calendar_availability
                )
                self.doctor_var.set(doctors[0] if doctors else "")
                self.form_entries[field_name] = entry
            elif field_name == "Date":
                # Create a frame for calendar
                self.calendar_frame = ctk.CTkFrame(frame, fg_color="transparent")
                self.calendar_frame.pack(side="right", expand=True, fill="x")

                # Create a button to open calendar
                self.calendar_btn = ctk.CTkButton(
                    self.calendar_frame,
                    text="Select Date",
                    width=300,
                    fg_color=MEDICAL_DARK_BLUE,
                    hover_color=MEDICAL_BLUE,
                    command=self.open_calendar
                )
                self.calendar_btn.pack()

                # Label to show selected date
                self.date_label = ctk.CTkLabel(
                    self.calendar_frame,
                    text="No date selected",
                    font=("Arial", 12),
                    text_color=MEDICAL_DARK_BLUE
                )
                self.date_label.pack(pady=5)

            elif field_name == "Time":
                # Create a frame for time slots
                self.time_slots_frame = ctk.CTkFrame(frame, fg_color="transparent")
                self.time_slots_frame.pack(side="right", expand=True, fill="x")

                # Label for time slots
                ctk.CTkLabel(
                    self.time_slots_frame,
                    text="Available Time Slots:",
                    font=("Arial", 12),
                    anchor="w",
                    text_color=MEDICAL_BLUE
                ).pack(anchor="w")

                # Frame for time slot buttons
                self.time_buttons_frame = ctk.CTkFrame(self.time_slots_frame, fg_color="transparent")
                self.time_buttons_frame.pack(fill="x", pady=5)

                # Initially disabled until date is selected
                self.update_time_slots()

            elif field_name == "Reason for Visit":
                entry = ctk.CTkTextbox(frame, height=100, fg_color=MEDICAL_WHITE, border_color=MEDICAL_BLUE)
                self.form_entries[field_name] = entry
            else:
                entry = ctk.CTkEntry(
                    frame,
                    placeholder_text=placeholder,
                    width=300,
                    fg_color=MEDICAL_WHITE,
                    border_color=MEDICAL_BLUE
                )
                self.form_entries[field_name] = entry

            if field_name not in ["Date", "Time"]:
                entry.pack(side="right", expand=True, fill="x")

        # Initialize calendar availability
        self.update_calendar_availability()

        # Submit button with medical theme
        submit_btn = ctk.CTkButton(
            form_frame,
            text="Schedule Appointment",
            fg_color=MEDICAL_GREEN,
            hover_color=MEDICAL_BLUE,
            font=("Arial", 14, "bold"),
            command=self.submit_appointment
        )
        submit_btn.pack(pady=20)

    def open_calendar(self):
        """Open calendar popup to select date"""
        top = Toplevel()
        top.title("Select Appointment Date")
        top.geometry("300x300")
        top.resizable(False, False)
        top.configure(bg=MEDICAL_WHITE)

        # Create calendar widget with medical theme
        cal = Calendar(
            top,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            date_pattern="mm/dd/yyyy",
            mindate=datetime.now(),
            maxdate=datetime.now() + timedelta(days=60),  # Show 2 months ahead
            background=MEDICAL_BLUE,
            foreground="white",
            bordercolor=MEDICAL_BLUE,
            headersbackground=MEDICAL_BLUE,
            normalbackground=MEDICAL_WHITE,
            weekendbackground=MEDICAL_WHITE,
            selectbackground=MEDICAL_LIGHT_BLUE
        )
        cal.pack(pady=10, padx=10, fill="both", expand=True)

        # Select button
        select_btn = ctk.CTkButton(
            top,
            text="Select Date",
            fg_color=MEDICAL_GREEN,
            hover_color=MEDICAL_BLUE,
            command=lambda: self.on_date_selected(cal.get_date(), top)
        )
        select_btn.pack(pady=5)

    def on_date_selected(self, date_str, top):
        """Handle date selection from calendar"""
        self.selected_date = date_str
        self.date_label.configure(text=date_str)
        self.update_time_slots()
        top.destroy()

    def update_calendar_availability(self, event=None):
        """Update calendar based on selected doctor"""
        self.selected_date = None
        self.selected_time = None
        self.date_label.configure(text="No date selected")
        self.update_time_slots()

    def update_time_slots(self):
        """Update available time slots based on selected doctor and date"""
        # Clear existing time buttons
        for widget in self.time_buttons_frame.winfo_children():
            widget.destroy()

        doctor = self.doctor_var.get()
        date = self.selected_date

        if not doctor or not date:
            # No doctor or date selected
            ctk.CTkLabel(
                self.time_buttons_frame,
                text="Please select a doctor and date first",
                text_color=MEDICAL_BLUE
            ).pack()
            return

        # Get booked times for this doctor/date
        booked_times = self.appointments.get(doctor, {}).get(date, [])

        # Create time slot buttons
        for time_slot in self.all_time_slots:
            if time_slot in booked_times:
                # Time slot is booked - show as unavailable
                btn = ctk.CTkButton(
                    self.time_buttons_frame,
                    text=time_slot,
                    fg_color=MEDICAL_RED,  # Red
                    hover_color="#c1121f",
                    state="disabled",
                    width=100,
                    text_color=MEDICAL_WHITE
                )
            else:
                # Time slot is available
                btn = ctk.CTkButton(
                    self.time_buttons_frame,
                    text=time_slot,
                    fg_color=MEDICAL_GREEN if self.selected_time == time_slot else MEDICAL_BLUE,
                    hover_color=MEDICAL_LIGHT_BLUE,
                    text_color=MEDICAL_WHITE,
                    command=lambda ts=time_slot: self.select_time_slot(ts),
                    width=100
                )
            btn.pack(side="left", padx=5, pady=5)

    def select_time_slot(self, time_slot):
        """Handle time slot selection"""
        self.selected_time = time_slot
        self.update_time_slots()  # Refresh to highlight selected time

    def submit_appointment(self):
        """Handle appointment submission"""
        # Get all form data
        patient_name = self.form_entries["Patient's Name"].get()
        contact = self.form_entries["Contact Number"].get()
        insurance = self.form_entries["Insurance Provider"].get()
        doctor = self.doctor_var.get()
        date = self.selected_date
        time = self.selected_time
        reason = self.form_entries["Reason for Visit"].get("1.0", "end-1c")

        # Validate inputs (removed dob from validation)
        if not all([patient_name, contact, doctor, date, time, reason]):
            messagebox.showerror("Error", "Please fill in all required fields!")
            return

        # Update appointments data
        if doctor not in self.appointments:
            self.appointments[doctor] = {}
        if date not in self.appointments[doctor]:
            self.appointments[doctor][date] = []

        # Add the new appointment
        self.appointments[doctor][date].append(time)
        save_appointments(self.appointments)

        # Add to user's appointments (removed dob from appointment data)
        new_appointment = {
            'patient_name': patient_name,
            'contact': contact,
            'insurance': insurance,
            'doctor': doctor,
            'date': date,
            'time': time,
            'reason': reason,
            'status': 'Confirmed',
            'created_at': datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        }
        self.user_appointments.append(new_appointment)
        save_user_appointments(self.username, self.user_appointments)

        # Show confirmation (removed dob from confirmation message)
        confirmation = (
            f"Appointment Booked Successfully!\n\n"
            f"Patient: {patient_name}\n"
            f"Contact: {contact}\n"
            f"Insurance: {insurance}\n"
            f"Doctor: {doctor}\n"
            f"Date: {date}\n"
            f"Time: {time}\n"
            f"Reason: {reason}"
        )

        messagebox.showinfo("Appointment Confirmation", confirmation)

        # Clear the form
        for field in self.form_entries.values():
            if isinstance(field, ctk.CTkTextbox):
                field.delete("1.0", "end")
            else:
                field.delete(0, "end")
        self.selected_date = None
        self.selected_time = None
        self.date_label.configure(text="No date selected")
        self.update_time_slots()

        # Return to dashboard
        self.show_dashboard()

    def show_appointments(self):
        self.clear_content()

        title = ctk.CTkLabel(
            self.content_area,
            text="My Appointments",
            font=("Arial", 24, "bold"),
            text_color=MEDICAL_BLUE
        )
        title.pack(pady=20)

        # Search frame
        search_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        search_frame.pack(fill="x", padx=50, pady=(0, 20))

        # Doctor dropdown
        doctors = list({a['doctor'] for a in self.user_appointments}) if self.user_appointments else ["No appointments yet"]
        self.selected_doctor = ctk.StringVar(value=doctors[0] if doctors else "")

        ctk.CTkLabel(
            search_frame,
            text="Filter by Doctor:",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(side="left", padx=(0, 10))

        doctor_dropdown = ctk.CTkComboBox(
            search_frame,
            variable=self.selected_doctor,
            values=doctors,
            width=200,
            dropdown_fg_color=MEDICAL_WHITE,
            button_color=MEDICAL_BLUE,
            command=self.filter_appointments
        )
        doctor_dropdown.pack(side="left", padx=(0, 20))

        # Status filter
        statuses = ["All", "Upcoming", "Completed", "Cancelled"]
        self.selected_status = ctk.StringVar(value="All")

        ctk.CTkLabel(
            search_frame,
            text="Filter by Status:",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(side="left", padx=(0, 10))

        status_dropdown = ctk.CTkComboBox(
            search_frame,
            variable=self.selected_status,
            values=statuses,
            width=150,
            dropdown_fg_color=MEDICAL_WHITE,
            button_color=MEDICAL_BLUE,
            command=self.filter_appointments
        )
        status_dropdown.pack(side="left", padx=(0, 20))

        # Date filter frame
        date_filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        date_filter_frame.pack(side="left", padx=(20, 0))

        ctk.CTkLabel(
            date_filter_frame,
            text="Filter by Date:",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(side="left")

        # Calendar button
        self.calendar_btn = ctk.CTkButton(
            date_filter_frame,
            text="Select Date",
            width=120,
            fg_color=MEDICAL_DARK_BLUE,
            hover_color=MEDICAL_BLUE,
            command=self.open_appointments_calendar
        )
        self.calendar_btn.pack(side="left", padx=(10, 0))

        # Selected date label
        self.selected_filter_date = None
        self.date_filter_label = ctk.CTkLabel(
            date_filter_frame,
            text="All dates",
            font=("Arial", 12),
            text_color=MEDICAL_DARK_BLUE
        )
        self.date_filter_label.pack(side="left", padx=(10, 0))

        # Clear date filter button
        clear_date_btn = ctk.CTkButton(
            date_filter_frame,
            text="Clear",
            width=80,
            fg_color=MEDICAL_RED,
            hover_color="#c1121f",
            command=self.clear_date_filter
        )
        clear_date_btn.pack(side="left", padx=(10, 0))

        # Results frame
        self.results_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, padx=50, pady=10)

        # Display initial appointments
        self.filter_appointments()

    def open_appointments_calendar(self):
        """Open calendar popup to filter appointments by date"""
        top = Toplevel()
        top.title("Select Date to Filter Appointments")
        top.geometry("300x300")
        top.resizable(False, False)
        top.configure(bg=MEDICAL_WHITE)

        # Create calendar widget with medical theme
        cal = Calendar(
            top,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            date_pattern="mm/dd/yyyy",
            background=MEDICAL_BLUE,
            foreground="white",
            bordercolor=MEDICAL_BLUE,
            headersbackground=MEDICAL_BLUE,
            normalbackground=MEDICAL_WHITE,
            weekendbackground=MEDICAL_WHITE,
            selectbackground=MEDICAL_LIGHT_BLUE
        )
        cal.pack(pady=10, padx=10, fill="both", expand=True)

        # Select button
        select_btn = ctk.CTkButton(
            top,
            text="Select Date",
            fg_color=MEDICAL_GREEN,
            hover_color=MEDICAL_BLUE,
            command=lambda: self.on_filter_date_selected(cal.get_date(), top)
        )
        select_btn.pack(pady=5)

    def on_filter_date_selected(self, date_str, top):
        """Handle date selection for filtering appointments"""
        self.selected_filter_date = date_str
        self.date_filter_label.configure(text=date_str)
        self.filter_appointments()
        top.destroy()

    def clear_date_filter(self):
        """Clear the date filter"""
        self.selected_filter_date = None
        self.date_filter_label.configure(text="All dates")
        self.filter_appointments()

    def filter_appointments(self, event=None):
        """Filter appointments based on selected criteria"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Get search criteria
        doctor_filter = self.selected_doctor.get()
        status_filter = self.selected_status.get()
        date_filter = self.selected_filter_date
        now = datetime.now()

        # Filter appointments
        filtered_appointments = []
        for appt in self.user_appointments:
            # Check doctor filter
            if doctor_filter != "All" and appt['doctor'] != doctor_filter:
                continue

            # Check date filter
            if date_filter and appt['date'] != date_filter:
                continue

            # Check status filter
            appt_date = datetime.strptime(appt['date'], "%m/%d/%Y")
            if status_filter == "Upcoming" and (appt_date < now or appt.get('status') in ['Cancelled', 'Completed']):
                continue
            elif status_filter == "Completed" and (appt_date >= now or appt.get('status') != 'Completed'):
                continue
            elif status_filter == "Cancelled" and appt.get('status') != 'Cancelled':
                continue

            filtered_appointments.append(appt)

        # Sort by date (newest first)
        filtered_appointments.sort(
            key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y"),
            reverse=True
        )

        if not filtered_appointments:
            ctk.CTkLabel(
                self.results_frame,
                text="No appointments found for the selected criteria",
                font=("Arial", 14),
                text_color=MEDICAL_BLUE
            ).pack(pady=50)
            return

        # Display appointments
        for appt in filtered_appointments:
            # Determine status
            appt_date = datetime.strptime(appt['date'], "%m/%d/%Y")
            if appt.get('status') == 'Cancelled':
                status = "Cancelled"
                status_color = MEDICAL_RED
                status_icon = "❌"
            elif appt.get('status') == 'Completed' or appt_date < now:
                status = "Completed"
                status_color = MEDICAL_GREEN
                status_icon = "✅"
            else:
                status = "Upcoming"
                status_color = MEDICAL_BLUE
                status_icon = "⏳"

            app_frame = ctk.CTkFrame(
                self.results_frame,
                fg_color=MEDICAL_WHITE,
                border_width=1,
                border_color=MEDICAL_BLUE,
                corner_radius=10
            )
            app_frame.pack(fill="x", pady=5)

            # Appointment info
            info_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=(10, 0))

            ctk.CTkLabel(
                info_frame,
                text=f"{status_icon} {appt['doctor']}",
                font=("Arial", 16, "bold"),
                anchor="w",
                text_color=status_color
            ).pack(side="left")

            ctk.CTkLabel(
                info_frame,
                text=f"📅 {appt['date']} at ⏰ {appt['time']}",
                font=("Arial", 14),
                anchor="w",
                text_color=status_color
            ).pack(side="left", padx=20)

            # Details frame
            details_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=10, pady=(0, 10))

            ctk.CTkLabel(
                details_frame,
                text=f"Patient: {appt.get('patient_name', 'N/A')} | Contact: {appt.get('contact', 'N/A')}",
                font=("Arial", 12),
                text_color="#495057"
            ).pack(anchor="w")

            ctk.CTkLabel(
                details_frame,
                text=f"Insurance: {appt.get('insurance', 'N/A')}",
                font=("Arial", 12),
                text_color="#495057"
            ).pack(anchor="w")

            ctk.CTkLabel(
                details_frame,
                text=f"Reason: {appt.get('reason', 'N/A')}",
                font=("Arial", 12),
                text_color="#495057"
            ).pack(anchor="w")

            # Action buttons
            action_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            action_frame.pack(fill="x", padx=10, pady=(0, 10))

            if status == "Upcoming":
                # Show both Cancel and Complete buttons for upcoming appointments
                cancel_btn = ctk.CTkButton(
                    action_frame,
                    text="Cancel Appointment",
                    width=150,
                    fg_color=MEDICAL_RED,
                    hover_color="#c1121f",
                    font=("Arial", 12),
                    command=lambda a=appt: self.cancel_appointment(a)
                )
                cancel_btn.pack(side="right", padx=5)

                complete_btn = ctk.CTkButton(
                    action_frame,
                    text="Complete Visit",
                    width=150,
                    fg_color=MEDICAL_GREEN,
                    hover_color=MEDICAL_BLUE,
                    font=("Arial", 12),
                    command=lambda a=appt: self.complete_appointment(a)
                )
                complete_btn.pack(side="right", padx=5)
            elif status == "Completed":
                # No action buttons for completed appointments
                pass
            elif status == "Cancelled":
                # No action buttons for cancelled appointments
                pass

            # View Details button (always shown)
            details_btn = ctk.CTkButton(
                action_frame,
                text="View Details",
                width=150,
                fg_color=MEDICAL_BLUE,
                hover_color=MEDICAL_LIGHT_BLUE,
                font=("Arial", 12),
                command=lambda a=appt: self.view_appointment_details(a)
            )
            details_btn.pack(side="right", padx=5)

    def complete_appointment(self, appointment):
        """Mark an appointment as completed"""
        if messagebox.askyesno("Confirm Completion", "Are you sure you want to mark this visit as completed?"):
            # Update the appointment status in user appointments
            for appt in self.user_appointments:
                if (appt['doctor'] == appointment['doctor'] and
                        appt['date'] == appointment['date'] and
                        appt['time'] == appointment['time']):
                    appt['status'] = 'Completed'
                    break

            # Save the updated user appointments
            save_user_appointments(self.username, self.user_appointments)

            # Refresh the appointments view
            self.filter_appointments()
            messagebox.showinfo("Success", "Visit marked as completed successfully")

    def cancel_appointment(self, appointment):
        """Cancel an existing appointment"""
        if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this appointment?"):
            # Update the appointment status
            for appt in self.user_appointments:
                if (appt['doctor'] == appointment['doctor'] and
                        appt['date'] == appointment['date'] and
                        appt['time'] == appointment['time']):
                    appt['status'] = 'Cancelled'
                    break

            # Save the updated user appointments
            save_user_appointments(self.username, self.user_appointments)

            # Update the main appointments data
            doctor = appointment['doctor']
            date = appointment['date']
            time = appointment['time']

            if doctor in self.appointments and date in self.appointments[doctor]:
                if time in self.appointments[doctor][date]:
                    self.appointments[doctor][date].remove(time)
                    save_appointments(self.appointments)

            # Refresh the appointments view
            self.filter_appointments()
            messagebox.showinfo("Success", "Appointment cancelled successfully")

    def view_appointment_details(self, appointment):
        """Show detailed view of an appointment"""
        top = Toplevel()
        top.title("Appointment Details")
        top.geometry("600x500")
        top.resizable(False, False)
        top.configure(bg=MEDICAL_WHITE)

        # Main frame
        main_frame = ctk.CTkFrame(top, fg_color=MEDICAL_WHITE)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(
            main_frame,
            text="Appointment Details",
            font=("Arial", 20, "bold"),
            text_color=MEDICAL_BLUE
        ).pack(pady=10)

        # Details frame
        details_frame = ctk.CTkFrame(main_frame, fg_color=MEDICAL_WHITE)
        details_frame.pack(fill="x", padx=20, pady=10)

        # Appointment status
        appt_date = datetime.strptime(appointment['date'], "%m/%d/%Y")
        now = datetime.now()
        if appt_date < now:
            status = "Completed"
        elif appointment.get('status') == 'Cancelled':
            status = "Cancelled"
        else:
            status = "Upcoming"

        status_color = MEDICAL_GREEN if status == "Completed" else MEDICAL_RED if status == "Cancelled" else MEDICAL_BLUE

        ctk.CTkLabel(
            details_frame,
            text=f"Status: {status}",
            font=("Arial", 16, "bold"),
            text_color=status_color
        ).pack(anchor="w", pady=5)

        # Doctor info
        ctk.CTkLabel(
            details_frame,
            text=f"👨‍⚕️ Doctor: {appointment['doctor']}",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(anchor="w", pady=5)

        # Date and time
        ctk.CTkLabel(
            details_frame,
            text=f"📅 Date: {appointment['date']} at ⏰ {appointment['time']}",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(anchor="w", pady=5)

        # Patient info
        ctk.CTkLabel(
            details_frame,
            text="Patient Information:",
            font=("Arial", 14, "bold"),
            text_color=MEDICAL_BLUE
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            details_frame,
            text=f"Name: {appointment.get('patient_name', 'N/A')}",
            font=("Arial", 12),
            text_color="#495057"
        ).pack(anchor="w")

        ctk.CTkLabel(
            details_frame,
            text=f"Contact: {appointment.get('contact', 'N/A')}",
            font=("Arial", 12),
            text_color="#495057"
        ).pack(anchor="w")

        ctk.CTkLabel(
            details_frame,
            text=f"Insurance: {appointment.get('insurance', 'N/A')}",
            font=("Arial", 12),
            text_color="#495057"
        ).pack(anchor="w")

        # Reason for visit
        ctk.CTkLabel(
            details_frame,
            text="Reason for Visit:",
            font=("Arial", 14, "bold"),
            text_color=MEDICAL_BLUE
        ).pack(anchor="w", pady=(10, 5))

        reason_text = ctk.CTkTextbox(
            details_frame,
            height=100,
            fg_color=MEDICAL_WHITE,
            border_color=MEDICAL_BLUE,
            font=("Arial", 12),
            wrap="word"
        )
        reason_text.pack(fill="x", padx=5, pady=5)
        reason_text.insert("1.0", appointment.get('reason', 'N/A'))
        reason_text.configure(state="disabled")

        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            width=150,
            fg_color=MEDICAL_BLUE,
            hover_color=MEDICAL_LIGHT_BLUE,
            font=("Arial", 14),
            command=top.destroy
        )
        close_btn.pack(pady=20)

    def logout(self):
        self.master.destroy()
        auth_app = AuthApp()
        auth_app.run()


class DoctorDashboard:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        self.doctor_name = DOCTOR_NAMES[username]
        self.appointments = load_appointments()
        self.setup_ui()

    def setup_ui(self):
        self.master.geometry("1200x800")
        self.master.title(f"HopeSaver Doctor Portal - {self.doctor_name}")
        self.master.resizable(False, False)

        # Main container
        self.main_container = ctk.CTkFrame(self.master, fg_color=MEDICAL_WHITE)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, fg_color=MEDICAL_BLUE, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo placeholder
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            width=200,
            height=100,
            fg_color=MEDICAL_WHITE,
            corner_radius=10
        )
        logo_frame.pack(pady=(20, 30), padx=20)

        ctk.CTkLabel(
            logo_frame,
            text="HopeSaver",
            font=("Arial", 20, "bold"),
            text_color=MEDICAL_BLUE
        ).pack(expand=True)

        # Sidebar header
        sidebar_header = ctk.CTkLabel(
            self.sidebar,
            text=f"Welcome,\n{self.doctor_name}",
            font=("Arial", 16, "bold"),
            text_color=MEDICAL_WHITE
        )
        sidebar_header.pack(pady=(0, 30), padx=10)

        # Sidebar buttons
        buttons = [
            ("📅 Today's Schedule", self.show_today_schedule),
            ("🩺 All Appointments", self.show_all_appointments)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=("Arial", 14),
                fg_color="transparent",
                hover_color=MEDICAL_LIGHT_BLUE,
                text_color=MEDICAL_WHITE,
                anchor="w",
                command=command,
                height=45,
                border_spacing=15,
                corner_radius=8
            )
            btn.pack(fill="x", padx=15, pady=5)

        # Spacer to push logout button to bottom
        ctk.CTkFrame(self.sidebar, height=0, fg_color="transparent").pack(expand=True)

        # Logout button
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            font=("Arial", 14),
            fg_color=MEDICAL_RED,
            hover_color="#c1121f",
            text_color=MEDICAL_WHITE,
            height=45,
            corner_radius=8,
            command=self.logout
        )
        logout_btn.pack(side="bottom", pady=(0, 30), padx=15, fill="x")

        # Main content area
        self.content_area = ctk.CTkFrame(self.main_container, fg_color=MEDICAL_GRAY)
        self.content_area.pack(side="right", fill="both", expand=True)

        # Show default view
        self.show_today_schedule()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_today_schedule(self):
        self.clear_content()

        # Main container with padding
        main_container = ctk.CTkFrame(self.content_area, fg_color=MEDICAL_GRAY)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color=MEDICAL_GRAY)
        scroll_frame.pack(fill="both", expand=True)

        # Header Section
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Today's Schedule - {datetime.now().strftime('%A, %B %d, %Y')}",
            font=("Arial", 28, "bold"),
            text_color=MEDICAL_BLUE
        )
        welcome_label.pack(side="left")

        # Get today's date in the same format as stored
        today_str = datetime.now().strftime("%m/%d/%Y")

        # Get today's appointments for this doctor
        today_appointments = []
        if self.doctor_name in self.appointments and today_str in self.appointments[self.doctor_name]:
            booked_times = self.appointments[self.doctor_name][today_str]

            # Load all user appointments to get details
            if os.path.exists(USER_APPOINTMENT_FILE):
                with open(USER_APPOINTMENT_FILE, 'r') as file:
                    try:
                        all_user_appointments = json.load(file)
                    except json.JSONDecodeError:
                        all_user_appointments = {}

            # Find appointments matching today's date and time slots
            for username, appointments in all_user_appointments.items():
                for appt in appointments:
                    if (appt['doctor'] == self.doctor_name and
                            appt['date'] == today_str and
                            appt['time'] in booked_times and
                            appt.get('status', 'Confirmed') != 'Cancelled'):
                        today_appointments.append(appt)

            # Sort by time
            today_appointments.sort(key=lambda x: datetime.strptime(x['time'], "%I:%M %p"))

        # Today's Appointments Section
        appointments_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=MEDICAL_WHITE,
            border_width=1,
            border_color="#dee2e6",
            corner_radius=10
        )
        appointments_frame.pack(fill="x", pady=(0, 30))

        # Section header
        section_header = ctk.CTkFrame(appointments_frame, fg_color=MEDICAL_DARK_BLUE, height=50, corner_radius=10)
        section_header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            section_header,
            text=f"Your Appointments for Today ({len(today_appointments)})",
            font=("Arial", 18, "bold"),
            text_color=MEDICAL_WHITE
        ).pack(side="left", padx=15)

        if not today_appointments:
            ctk.CTkLabel(
                appointments_frame,
                text="No appointments scheduled for today",
                font=("Arial", 14),
                text_color="#6c757d"
            ).pack(pady=30)
        else:
            for appt in today_appointments:
                appt_card = ctk.CTkFrame(
                    appointments_frame,
                    fg_color=MEDICAL_LIGHT_BLUE,
                    corner_radius=8
                )
                appt_card.pack(fill="x", padx=10, pady=5)

                # Appointment info
                info_frame = ctk.CTkFrame(appt_card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

                # Time and patient
                ctk.CTkLabel(
                    info_frame,
                    text=f"⏰ {appt['time']} - 👤 {appt['patient_name']}",
                    font=("Arial", 16, "bold"),
                    text_color=MEDICAL_DARK_BLUE,
                    anchor="w"
                ).pack(fill="x")

                # Contact and insurance
                ctk.CTkLabel(
                    info_frame,
                    text=f"📞 {appt['contact']} | 🏥 {appt['insurance']}",
                    font=("Arial", 14),
                    text_color=MEDICAL_DARK_BLUE,
                    anchor="w"
                ).pack(fill="x", pady=(5, 0))

                # Reason
                ctk.CTkLabel(
                    info_frame,
                    text=f"Reason: {appt['reason']}",
                    font=("Arial", 14),
                    text_color=MEDICAL_DARK_BLUE,
                    anchor="w"
                ).pack(fill="x", pady=(5, 0))

                # Status and actions
                status_frame = ctk.CTkFrame(appt_card, fg_color="transparent")
                status_frame.pack(side="right", padx=10, pady=10)

                status_label = ctk.CTkLabel(
                    status_frame,
                    text=f"Status: {appt.get('status', 'Confirmed')}",
                    font=("Arial", 14),
                    text_color=MEDICAL_DARK_BLUE
                )
                status_label.pack(side="left", padx=(0, 10))

                # Complete button
                if appt.get('status') == 'Confirmed':
                    complete_btn = ctk.CTkButton(
                        status_frame,
                        text="Complete",
                        width=100,
                        fg_color=MEDICAL_GREEN,
                        hover_color=MEDICAL_BLUE,
                        font=("Arial", 12),
                        command=lambda a=appt: self.complete_appointment(a)
                    )
                    complete_btn.pack(side="right")

    def show_all_appointments(self):
        self.clear_content()

        title = ctk.CTkLabel(
            self.content_area,
            text="All Appointments",
            font=("Arial", 24, "bold"),
            text_color=MEDICAL_BLUE
        )
        title.pack(pady=20)

        # Search frame
        search_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        search_frame.pack(fill="x", padx=50, pady=(0, 20))

        # Date filter frame
        date_filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        date_filter_frame.pack(side="left", padx=(20, 0))

        ctk.CTkLabel(
            date_filter_frame,
            text="Filter by Date:",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(side="left")

        # Calendar button
        self.calendar_btn = ctk.CTkButton(
            date_filter_frame,
            text="Select Date",
            width=120,
            fg_color=MEDICAL_DARK_BLUE,
            hover_color=MEDICAL_BLUE,
            command=self.open_appointments_calendar
        )
        self.calendar_btn.pack(side="left", padx=(10, 0))

        # Selected date label
        self.selected_filter_date = None
        self.date_filter_label = ctk.CTkLabel(
            date_filter_frame,
            text="All dates",
            font=("Arial", 12),
            text_color=MEDICAL_DARK_BLUE
        )
        self.date_filter_label.pack(side="left", padx=(10, 0))

        # Clear date filter button
        clear_date_btn = ctk.CTkButton(
            date_filter_frame,
            text="Clear",
            width=80,
            fg_color=MEDICAL_RED,
            hover_color="#c1121f",
            command=self.clear_date_filter
        )
        clear_date_btn.pack(side="left", padx=(10, 0))

        # Status filter
        statuses = ["All", "Confirmed", "Completed", "Cancelled"]
        self.selected_status = ctk.StringVar(value="All")

        ctk.CTkLabel(
            search_frame,
            text="Filter by Status:",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        ).pack(side="left", padx=(0, 10))

        status_dropdown = ctk.CTkComboBox(
            search_frame,
            variable=self.selected_status,
            values=statuses,
            width=150,
            dropdown_fg_color=MEDICAL_WHITE,
            button_color=MEDICAL_BLUE,
            command=self.filter_appointments
        )
        status_dropdown.pack(side="left", padx=(0, 20))

        # Results frame
        self.results_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, padx=50, pady=10)

        # Display initial appointments
        self.filter_appointments()

    def open_appointments_calendar(self):
        """Open calendar popup to filter appointments by date"""
        top = Toplevel()
        top.title("Select Date to Filter Appointments")
        top.geometry("300x300")
        top.resizable(False, False)
        top.configure(bg=MEDICAL_WHITE)

        # Create calendar widget with medical theme
        cal = Calendar(
            top,
            selectmode="day",
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            date_pattern="mm/dd/yyyy",  # Fixed: Changed from "mm/dd/%Y" to "mm/dd/yyyy"
            background=MEDICAL_BLUE,
            foreground="white",
            bordercolor=MEDICAL_BLUE,
            headersbackground=MEDICAL_BLUE,
            normalbackground=MEDICAL_WHITE,
            weekendbackground=MEDICAL_WHITE,
            selectbackground=MEDICAL_LIGHT_BLUE
        )
        cal.pack(pady=10, padx=10, fill="both", expand=True)

        # Select button
        select_btn = ctk.CTkButton(
            top,
            text="Select Date",
            fg_color=MEDICAL_GREEN,
            hover_color=MEDICAL_BLUE,
            command=lambda: self.on_filter_date_selected(cal.get_date(), top)
        )
        select_btn.pack(pady=5)

    def on_filter_date_selected(self, date_str, top):
        """Handle date selection for filtering appointments"""
        self.selected_filter_date = date_str
        self.date_filter_label.configure(text=date_str)
        self.filter_appointments()
        top.destroy()

    def clear_date_filter(self):
        """Clear the date filter"""
        self.selected_filter_date = None
        self.date_filter_label.configure(text="All dates")
        self.filter_appointments()

    def filter_appointments(self, event=None):
        """Filter appointments based on selected criteria"""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Get search criteria
        status_filter = self.selected_status.get()
        date_filter = self.selected_filter_date
        now = datetime.now()

        # Load all user appointments to find this doctor's appointments
        all_user_appointments = {}
        if os.path.exists(USER_APPOINTMENT_FILE):
            with open(USER_APPOINTMENT_FILE, 'r') as file:
                try:
                    all_user_appointments = json.load(file)
                except json.JSONDecodeError:
                    all_user_appointments = {}

        # Collect all appointments for this doctor
        doctor_appointments = []
        for username, appointments in all_user_appointments.items():
            for appt in appointments:
                if appt['doctor'] == self.doctor_name:
                    doctor_appointments.append(appt)

        # Filter appointments
        filtered_appointments = []
        for appt in doctor_appointments:
            # Check date filter
            if date_filter and appt['date'] != date_filter:
                continue

            # Check status filter
            current_status = appt.get('status', 'Confirmed')
            if status_filter == "Confirmed" and current_status != 'Confirmed':
                continue
            elif status_filter == "Completed" and current_status != 'Completed':
                continue
            elif status_filter == "Cancelled" and current_status != 'Cancelled':
                continue

            filtered_appointments.append(appt)

        # Sort by date (newest first)
        filtered_appointments.sort(
            key=lambda x: datetime.strptime(x['date'], "%m/%d/%Y"),
            reverse=True
        )

        if not filtered_appointments:
            ctk.CTkLabel(
                self.results_frame,
                text="No appointments found for the selected criteria",
                font=("Arial", 14),
                text_color=MEDICAL_BLUE
            ).pack(pady=50)
            return

        # Display appointments
        for appt in filtered_appointments:
            # Determine status
            if appt.get('status') == 'Cancelled':
                status = "Cancelled"
                status_color = MEDICAL_RED
                status_icon = "❌"
            elif appt.get('status') == 'Completed':
                status = "Completed"
                status_color = MEDICAL_GREEN
                status_icon = "✅"
            else:
                status = "Confirmed"
                status_color = MEDICAL_BLUE
                status_icon = "⏳"

            app_frame = ctk.CTkFrame(
                self.results_frame,
                fg_color=MEDICAL_WHITE,
                border_width=1,
                border_color=MEDICAL_BLUE,
                corner_radius=10
            )
            app_frame.pack(fill="x", pady=5)

            # Appointment info
            info_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=(10, 0))

            ctk.CTkLabel(
                info_frame,
                text=f"{status_icon} {appt['date']} at {appt['time']}",
                font=("Arial", 16, "bold"),
                anchor="w",
                text_color=status_color
            ).pack(side="left")

            ctk.CTkLabel(
                info_frame,
                text=f"👤 {appt['patient_name']}",
                font=("Arial", 14),
                anchor="w",
                text_color=status_color
            ).pack(side="left", padx=20)

            # Details frame
            details_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=10, pady=(0, 10))

            ctk.CTkLabel(
                details_frame,
                text=f"Contact: {appt.get('contact', 'N/A')} | Insurance: {appt.get('insurance', 'N/A')}",
                font=("Arial", 12),
                text_color="#495057"
            ).pack(anchor="w")

            ctk.CTkLabel(
                details_frame,
                text=f"Reason: {appt.get('reason', 'N/A')}",
                font=("Arial", 12),
                text_color="#495057"
            ).pack(anchor="w")

            # Action buttons
            action_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            action_frame.pack(fill="x", padx=10, pady=(0, 10))

            if status == "Confirmed":
                # Show Complete button for confirmed appointments
                complete_btn = ctk.CTkButton(
                    action_frame,
                    text="Complete Visit",
                    width=150,
                    fg_color=MEDICAL_GREEN,
                    hover_color=MEDICAL_BLUE,
                    font=("Arial", 12),
                    command=lambda a=appt: self.complete_appointment(a)
                )
                complete_btn.pack(side="right", padx=5)

    def complete_appointment(self, appointment):
        """Mark an appointment as completed"""
        if messagebox.askyesno("Confirm Completion", "Are you sure you want to mark this visit as completed?"):
            # Load all user appointments
            all_data = {}
            if os.path.exists(USER_APPOINTMENT_FILE):
                with open(USER_APPOINTMENT_FILE, 'r') as file:
                    try:
                        all_data = json.load(file)
                    except json.JSONDecodeError:
                        all_data = {}

            # Find and update the appointment
            for username, appointments in all_data.items():
                for appt in appointments:
                    if (appt['doctor'] == appointment['doctor'] and
                            appt['date'] == appointment['date'] and
                            appt['time'] == appointment['time']):
                        appt['status'] = 'Completed'
                        break

            # Save the updated data
            with open(USER_APPOINTMENT_FILE, 'w') as file:
                json.dump(all_data, file)

            # Refresh the view
            if hasattr(self, 'selected_filter_date') and self.selected_filter_date:
                self.filter_appointments()
            else:
                self.show_today_schedule()

            messagebox.showinfo("Success", "Visit marked as completed successfully")

    def logout(self):
        self.master.destroy()
        auth_app = AuthApp()
        auth_app.run()


# ======================== AUTHENTICATION APP ========================
class AuthApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.geometry("1200x800")
        self.app.title("HopeSaver Patient Portal")
        self.app.resizable(False, False)

        self.show_login_form()

    def clear_frame(self):
        for widget in self.app.winfo_children():
            widget.destroy()

    def show_login_form(self):
        self.clear_frame()

        # Background frame with medical theme
        bg_frame = ctk.CTkFrame(self.app, width=1200, height=800, fg_color=MEDICAL_WHITE)
        bg_frame.pack_propagate(False)
        bg_frame.pack()

        # Left decorative panel with medical theme
        left_panel = ctk.CTkFrame(bg_frame, width=400, height=760, fg_color=MEDICAL_BLUE, corner_radius=20)
        left_panel.pack_propagate(False)
        left_panel.pack(side="left", padx=20, pady=20)

        # Medical logo and welcome message
        logo_label = ctk.CTkLabel(
            left_panel,
            text="🏥 HopeSaver",
            font=("Arial", 32, "bold"),
            text_color=MEDICAL_WHITE
        )
        logo_label.pack(pady=(100, 10))

        welcome_label = ctk.CTkLabel(
            left_panel,
            text="Portal Login",
            font=("Arial", 24),
            text_color=MEDICAL_WHITE
        )
        welcome_label.pack(pady=(0, 50))

        # Medical icon
        icon_label = ctk.CTkLabel(
            left_panel,
            text="🩺",
            font=("Arial", 80),
            text_color=MEDICAL_WHITE
        )
        icon_label.pack(pady=50)

        # Right form panel
        right_panel = ctk.CTkFrame(bg_frame, width=700, height=760, fg_color=MEDICAL_WHITE, corner_radius=20)
        right_panel.pack_propagate(False)
        right_panel.pack(side="right", padx=20, pady=20)

        # Form title with medical theme
        form_title = ctk.CTkLabel(
            right_panel,
            text="Login to Portal",
            font=("Arial", 28, "bold"),
            text_color=MEDICAL_BLUE
        )
        form_title.pack(pady=(60, 40))

        # Login type selection
        self.login_type = ctk.StringVar(value="patient")

        patient_radio = ctk.CTkRadioButton(
            right_panel,
            text="Patient Login",
            variable=self.login_type,
            value="patient",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        )
        patient_radio.pack(pady=(0, 10))

        doctor_radio = ctk.CTkRadioButton(
            right_panel,
            text="Doctor Login",
            variable=self.login_type,
            value="doctor",
            font=("Arial", 14),
            text_color=MEDICAL_BLUE
        )
        doctor_radio.pack(pady=(0, 20))

        # Form fields with medical styling
        entry_width = 500
        entry_height = 50
        font_size = 16
        entry_font = ("Arial", font_size)

        # Username field
        self.login_username_entry = ctk.CTkEntry(
            right_panel,
            width=entry_width,
            height=entry_height,
            placeholder_text="Enter your username",
            font=entry_font,
            corner_radius=10,
            border_color=MEDICAL_BLUE,
            fg_color=MEDICAL_WHITE
        )
        self.login_username_entry.pack(pady=(0, 20))

        # Password field
        self.login_password_entry = ctk.CTkEntry(
            right_panel,
            width=entry_width,
            height=entry_height,
            placeholder_text="Enter your password",
            font=entry_font,
            corner_radius=10,
            border_color=MEDICAL_BLUE,
            fg_color=MEDICAL_WHITE,
            show="•"
        )
        self.login_password_entry.pack(pady=(0, 20))

        # Login button with medical theme
        login_button = ctk.CTkButton(
            right_panel,
            text="Login",
            width=entry_width,
            height=entry_height,
            font=("Arial", font_size, "bold"),
            corner_radius=10,
            fg_color=MEDICAL_BLUE,
            hover_color=MEDICAL_LIGHT_BLUE,
            command=self.perform_login
        )
        login_button.pack(pady=(0, 10))

        # Register link (only for patients)
        register_link = ctk.CTkLabel(
            right_panel,
            text="Don't have an account? Register here",
            font=("Arial", 12),
            text_color=MEDICAL_BLUE,
            cursor="hand2"
        )
        register_link.pack(pady=(20, 0))
        register_link.bind("<Button-1>", lambda e: self.show_register_form())

    def perform_login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        if not all([username, password]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        if self.login_type.get() == "patient":
            if not check_user_exists(username):
                messagebox.showerror("Error", "Username not found!")
                return

            if verify_login(username, password):
                self.app.destroy()  # Close the login window
                dashboard_root = ctk.CTk()
                Dashboard(dashboard_root, username)
                dashboard_root.mainloop()
            else:
                messagebox.showerror("Error", "Incorrect password!")
        else:  # Doctor login
            if verify_doctor_login(username, password):
                self.app.destroy()  # Close the login window
                dashboard_root = ctk.CTk()
                DoctorDashboard(dashboard_root, username)
                dashboard_root.mainloop()
            else:
                messagebox.showerror("Error", "Invalid doctor credentials!")


    def show_register_form(self):
        self.clear_frame()

        # Background frame
        bg_frame = ctk.CTkFrame(self.app, width=1200, height=800, fg_color=MEDICAL_WHITE)
        bg_frame.pack_propagate(False)
        bg_frame.pack()

        # Left decorative panel with medical theme
        left_panel = ctk.CTkFrame(bg_frame, width=400, height=760, fg_color=MEDICAL_DARK_BLUE, corner_radius=20)
        left_panel.pack_propagate(False)
        left_panel.pack(side="left", padx=20, pady=20)

        # Medical logo and welcome message
        logo_label = ctk.CTkLabel(
            left_panel,
            text="🏥 HopeSaver",
            font=("Arial", 32, "bold"),
            text_color=MEDICAL_WHITE
        )
        logo_label.pack(pady=(100, 10))

        welcome_label = ctk.CTkLabel(
            left_panel,
            text="Patient Registration",
            font=("Arial", 24),
            text_color=MEDICAL_WHITE
        )
        welcome_label.pack(pady=(0, 50))

        # Medical icon
        icon_label = ctk.CTkLabel(
            left_panel,
            text="🩺",
            font=("Arial", 80),
            text_color=MEDICAL_WHITE
        )
        icon_label.pack(pady=50)

        # Right form panel
        right_panel = ctk.CTkFrame(bg_frame, width=700, height=760, fg_color=MEDICAL_WHITE, corner_radius=20)
        right_panel.pack_propagate(False)
        right_panel.pack(side="right", padx=20, pady=20)

        # Form title with medical theme
        form_title = ctk.CTkLabel(
            right_panel,
            text="New Patient Registration",
            font=("Arial", 28, "bold"),
            text_color=MEDICAL_BLUE
        )
        form_title.pack(pady=(60, 40))

        # Form fields with medical styling
        entry_width = 500
        entry_height = 50
        font_size = 16
        entry_font = ("Arial", font_size)

        # Username field
        self.reg_username_entry = ctk.CTkEntry(
            right_panel,
            width=entry_width,
            height=entry_height,
            placeholder_text="Enter your username",
            font=entry_font,
            corner_radius=10,
            border_color=MEDICAL_BLUE,
            fg_color=MEDICAL_WHITE
        )
        self.reg_username_entry.pack(pady=(0, 20))

        # Email field
        self.reg_email_entry = ctk.CTkEntry(
            right_panel,
            width=entry_width,
            height=entry_height,
            placeholder_text="Enter your email",
            font=entry_font,
            corner_radius=10,
            border_color=MEDICAL_BLUE,
            fg_color=MEDICAL_WHITE
        )
        self.reg_email_entry.pack(pady=(0, 20))

        # Phone number field
        self.reg_phone_entry = ctk.CTkEntry(
            right_panel,
            width=entry_width,
            height=entry_height,
            placeholder_text="Enter your phone number",
            font=entry_font,
            corner_radius=10,
            border_color=MEDICAL_BLUE,
            fg_color=MEDICAL_WHITE
        )
        self.reg_phone_entry.pack(pady=(0, 20))

        # Password field
        self.reg_password_entry = ctk.CTkEntry(
            right_panel,
            width=entry_width,
            height=entry_height,
            placeholder_text="Enter your password",
            font=entry_font,
            corner_radius=10,
            border_color=MEDICAL_BLUE,
            fg_color=MEDICAL_WHITE,
            show="•"
        )
        self.reg_password_entry.pack(pady=(0, 40))

        # Register button with medical theme
        register_button = ctk.CTkButton(
            right_panel,
            text="Register",
            width=entry_width,
            height=entry_height,
            font=("Arial", font_size, "bold"),
            corner_radius=10,
            fg_color=MEDICAL_GREEN,
            hover_color=MEDICAL_BLUE,
            command=self.perform_register
        )
        register_button.pack(pady=(0, 20))

        # Login link
        login_link = ctk.CTkLabel(
            right_panel, text="Already have an account? Login here", font=("Arial", 12), text_color=MEDICAL_BLUE,cursor="hand2")
        login_link.pack(pady=(20, 0))
        login_link.bind("<Button-1>", lambda e: self.show_login_form())

    def perform_register(self):
        username = self.reg_username_entry.get()
        email = self.reg_email_entry.get()
        phone = self.reg_phone_entry.get()
        password = self.reg_password_entry.get()

        if not all([username, email, phone, password]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        if check_user_exists(username):
            messagebox.showerror("Error", "Username already exists!")
            return

        save_user_data(username, email, phone, password)
        messagebox.showinfo("Success", f"Account created for {username}!")
        self.show_login_form()

    def run(self):
        self.app.mainloop()


# ======================== RUN APPLICATION ========================
if __name__ == "__main__":
    auth_app = AuthApp()
    auth_app.run()