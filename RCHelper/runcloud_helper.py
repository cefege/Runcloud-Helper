import os.path
import shutil
import uuid
from csv import writer

from playwright.sync_api import Page


class RunCloudHelper:
    def __init__(self, browser, login_email, login_password, state_file_path):
        self.__create_dirs(state_file_path)
        self.login_email = login_email
        self.login_password = login_password
        self.browser = browser
        self.page: Page = None
        self.__login(state_file_path)
        # Accept any popup messages
        self.page.on("dialog", lambda dialog: dialog.accept())

    def __login(self, state_file_path, n_login_trials=3):
        def load_state():
            """
            Function to load state (cookies) if exists, otherwise, raise a flag to save it after log in.
            :return: tuple(browser context, flag indicate whether the state is loaded or not'
            """
            if os.path.exists(state_file_path):
                context_ = self.browser.new_context(storage_state=state_file_path)
                return context_, True
            else:
                context_ = self.browser.new_context()
                return context_, False

        context, context_loaded = load_state()
        self.page = context.new_page()
        n_trials = 0
        while n_trials < n_login_trials:
            try:
                self.page.goto("https://manage.runcloud.io/auth/login")
                break
            except Exception as e:
                print(f"This error occurred {str(e)}, trial number {n_trials}")
                n_trials += 1

        # Login if there's no previous state (occurs first time you log-in)
        if not context_loaded:
            # Fill username and password
            self.page.fill("[name='email']", self.login_email)
            self.page.fill("[name='password']", self.login_password)
            self.page.locator("#rememberMe").check()
            # press submit button
            self.page.click('[class="btn btn-primary btn-block btn-lg"]')
        else:
            print("[Log In] Cookies Loaded!")
        # wait for page loading
        self.page.wait_for_load_state("networkidle")
        # Check if logged successfully
        if self.page.locator("text=Sign Out").count():
            if not context_loaded:
                context.storage_state(path=state_file_path)
                print("[Log In] Cookies Saved!")
            print(f"[Log In] Logged In")
        else:
            if context_loaded:
                os.remove(state_file_path)
                print("Cookies are expired")
                self.__login("")
            else:
                print("Please Enter a Valid Username/Password")
                exit()

    def get_server_by_ip(self, server_ip):
        # List table rows
        table_rows = self.page.locator('[class="table table-hover"]').locator("tr")
        if table_rows.count():
            for row_idx in range(table_rows.count()):
                # List table columns
                cols = table_rows.nth(row_idx).locator("td")
                if cols.count():
                    # Extract IP Address
                    detected_ip = cols.nth(1).inner_text().split("\n")[0]
                    # if detected IP matches with the input IP
                    if detected_ip == server_ip:
                        server_id_ = cols.locator('a[href*="/servers/"]').get_attribute("href").split("/")[-2]
                        return server_id_
            else:
                print("Server Not Found.")
        return 0

    def create_webapp(self, server_id, domain, title, username="admin", password="",
                      email="mateiasmihaiandrei@gmail.com"):
        strip_domain = domain.split(".")[0]
        site_title = title if title else strip_domain
        password = password if password else str(uuid.uuid4()).replace("-", "")[:10]
        self.page.goto(f"https://manage.runcloud.io/servers/{server_id}/webapplications/create")
        self.page.wait_for_load_state("networkidle")
        self.page.fill("[name='name']", strip_domain)
        self.page.fill("[name='domainName']", domain)
        www_checkbox = self.page.locator("#www")
        if www_checkbox.count():
            www_checkbox.check()
        self.page.fill("[name='siteTitle']", site_title)
        self.page.fill("[name='adminUsername']", username)
        self.page.fill("[name='password']", password)
        self.page.fill("[name='adminEmail']", email)
        self.page.locator('[class="btn btn-primary flex-shrink-0"]').click()
        self.page.wait_for_timeout(2000)
        result = self.page.locator('[class="help-block"]')
        if result.count():
            for i in range(result.count()):
                print(result.nth(i).inner_text())
            return {}

        self.page.reload()
        if "webapplications/create" in self.page.url:
            print("Error Occurred Please Revise The Information")
            return {}
        else:
            self.page.wait_for_url("**dashboard**")
            return {"Website Name": strip_domain, "Domain Name": domain, "Site Title": site_title,
                    "Admin Username": username, "Admin Password": password, "Admin Email": email}

    def export_results(self, data, csv_path="./data/site.csv"):
        if not data:
            return False
        self.__create_dirs(csv_path)
        file_exist = os.path.exists(csv_path)
        with open(csv_path, 'a+') as csv_object:
            # Pass the CSV  file object to the writer() function
            writer_object = writer(csv_object)
            # Result - a writer object
            # Write file headers if it's newly created
            if not file_exist:
                writer_object.writerow(['Domain Name', 'Admin Username', 'Admin Password'])
            # Pass the data in the list as an argument into the writerow() function
            writer_object.writerow([data['Domain Name'], data['Admin Username'], data['Admin Password']])
            # Close the file object
            csv_object.close()
        return True
    @staticmethod
    def __create_dirs(path):
        base_dir = os.path.dirname(path)
        if base_dir and not os.path.exists(base_dir):
            os.makedirs(base_dir)
