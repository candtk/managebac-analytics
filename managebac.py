import requests
from bs4 import BeautifulSoup
from datetime import datetime


class ManageBac:
    def __init__(self, Email=None, Password=None, domainprefix="demo", role="student"):
        self.domainprefix = domainprefix
        self.role = role
        self.ReqSession = requests.Session()
        if Email is not None and Password is not None:
            self.Email = Email
            self.Password = Password
            self.logintoaccount()
            self.gather_user_info()
        else:
            raise Exception("No Username or password was provided")

    @property
    def _base_url(self):
        return f"https://{self.domainprefix}.managebac.com"

    def _headers(self, referer_path="login"):
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Origin": self._base_url,
            "Referer": f"{self._base_url}/{referer_path}"
        }

    def logintoaccount(self):
        # ManageBac login requires a CSRF token — fetch the login page first to extract it
        csrfreq = self.ReqSession.get(f"{self._base_url}/sessions").text

        # Parse and extract the hidden CSRF token from the login form
        parser = BeautifulSoup(csrfreq, features="html.parser")
        csrf = parser.find("input", type="hidden").get('value')
        data = {
            "authenticity_token": csrf,
            "login": self.Email,
            "password": self.Password,
            "remember_me": "1",
            "commit": "Sign-in"
        }
        response = self.ReqSession.post(f"{self._base_url}/sessions", data=data, headers=self._headers("login"))

        if "Login</title>" in response.text:
            raise Exception("Invalid Email and password")

    def gather_user_info(self):
        user = self.ReqSession.get(f"{self._base_url}/{self.role}/profile", headers=self._headers("login"))
        finalcheck = BeautifulSoup(user.text, features="html.parser")
        print(f"Succesfully logged into {finalcheck.title}")

    def gather_notification_auth(self):
        # Extract the bearer token embedded in the dashboard page's data-token attribute
        response = self.ReqSession.get(f"{self._base_url}/{self.role}", headers=self._headers(self.role))
        result = response.text.split('data-token="')[1]
        result = result.split('"')[0]
        return result

    def gather_notifications(self):
        auth = self.gather_notification_auth()
        headers = self._headers(self.role)
        headers["Accept"] = "application/json"
        headers["Authorization"] = auth
        print("Fetching notifications...")
        response = self.ReqSession.get("https://mnn-hub-ca.prod.faria.co/api/frontend/notifications?page=1&q=", headers=headers)
        return response.json()

    def get_class_messages(self, discussionid):
        discussion = self.ReqSession.get(
            f"{self._base_url}/{self.role}/classes/{discussionid}/discussions",
            headers=self._headers("login")
        )
        soup = BeautifulSoup(discussion.text, features="html.parser")

        # Extract the body text of each discussion post
        posts = soup.find_all('div', {'class': "fix-body-margins redactor-styles fr-view fr-element"})
        return [post.text for post in posts]

    def fetch_attendance(self, classid):
        attendance = self.ReqSession.get(
            f"{self._base_url}/{self.role}/classes/{classid}/attendance/marks",
            headers=self._headers("login")
        )
        soup = BeautifulSoup(attendance.text, features="html.parser")

        # Extract the period label from the attendance page header
        period_elem = soup.find('div', {'class': 'period'})
        period = period_elem.text.split(": ")[1]

        # Each attendance-bar div holds one student's attendance record
        return [
            {"user_id": ai['user_id'], "status": ai.get("status"), "period": period, "attr_id": ai.get("att_id")}
            for ai in soup.select('div[class^="attendance-bar"]')
        ]

    def fetch_attendance_csrf(self, classid):
        response = self.ReqSession.get(
            f"{self._base_url}/{self.role}/classes/{classid}/attendance/marks",
            headers=self._headers("login")
        )
        soup = BeautifulSoup(response.text, features="html.parser")
        return soup.find('meta', {'name': 'csrf-token'})["content"]

    def set_attendance(self, csrf, user_id, period, classid, status, attr_id, date=None):
        headers = self._headers("login")
        headers.update({
            "X-CSRF-Token": csrf,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        })

        if date is None:
            date = datetime.today().strftime('%Y-%m-%d')

        # Build the attendance payload — attr_id is only included when updating an existing record
        data = {
            "attendances[0][user_id]": user_id,
            "attendances[0][period]": f"{period}",
            "attendances[0][ib_class_id]": f"{classid}",
            "attendances[0][date]": date,
            "attendances[0][status]": f"{status}"
        }

        if attr_id is not None:
            data["attendances[0][id]"] = attr_id

        self.ReqSession.put(
            f"{self._base_url}/{self.role}/classes/{classid}/attendance/marks/update_marks",
            data=data,
            headers=headers
        )
