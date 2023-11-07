from managebac import ManageBac
from os import system, environ
import time
import datetime

USEENVVARIABLES = False  # Recommended — avoids hardcoding credentials in source
EMAIL = ""               # Ignored if USEENVVARIABLES is True
PASSWORD = ""            # Ignored if USEENVVARIABLES is True

INTERVAL = 5 * 60        # Seconds between attendance polling cycles
DOMAINPREFIX = "demo"    # Your institution's ManageBac subdomain
classes = [10277775]     # List of class IDs to monitor

if USEENVVARIABLES:
    EMAIL = environ.get("EMAIL")
    PASSWORD = environ.get("PASSWORD")

ManagebacSession = ManageBac(Email=EMAIL, Password=PASSWORD, domainprefix=DOMAINPREFIX, role="teacher")

def print_log(message):
    now = datetime.datetime.now()
    timenow = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"\033[1;34;40m[{timenow}]\033[0m {message}")

while True:
    for class_ in classes:
        print_log(f"Fetching attendance for class: {class_}")
        attendance_list = ManagebacSession.fetch_attendance(class_)
        lenstudents = len(attendance_list)
        print_log(f"Fetched {lenstudents} students for class: {class_}")
        csrf = ManagebacSession.fetch_attendance_csrf(class_)
        for attendance in attendance_list:
            if attendance["status"] == None:
                print_log(f"Marked student present for {class_}")
                ManagebacSession.set_attendance(csrf, attendance["user_id"], attendance["period"], class_, 1, attendance["attr_id"], date="2023-11-07")
            else:
                print_log(f"Skipping student since already marked...")
    time.sleep(INTERVAL)
