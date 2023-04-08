import argparse
import os.path

from playwright.sync_api import sync_playwright

from RCHelper import RunCloudHelper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-le", "--login-email", type=str, nargs='?', help="Login Email")
    parser.add_argument("-lp", "--login-passwd", type=str, nargs='?', help="Login Password")

    parser.add_argument("-c", "--credential-file", type=str, nargs='?',
                        help="Text file containing \\n separated login email and passwd")

    parser.add_argument("-s", "--server-ip", type=str, help="Server IP Address")
    parser.add_argument("-d", "--domain", type=str, help="Website Domain")

    parser.add_argument("-t", "--title", nargs='?', type=str, help="Website Title")
    parser.add_argument("-u", "--user", nargs='?', type=str, help="Admin Username")
    parser.add_argument("-p", "--password", nargs='?', type=str, help="Admin Password")
    parser.add_argument("-e", "--email", nargs='?', type=str, help="Admin Email")
    args = parser.parse_args()

    if args.login_email and args.login_passwd:
        login_email, login_passwd = args.login_email, args.login_passwd
    elif args.credential_file:
        file = args.credential_file
        if os.path.exists(file):
            with open(file, 'r') as fin:
                login_email, login_passwd = fin.readlines()[:2]
        else:
            print("Credential File Doesn't Exist")
    else:
        print("You have to enter username and passwd or path to the credential file")

    with sync_playwright() as p:
        # Create browser
        browser_ = p.chromium.launch(headless=True)
        helper = RunCloudHelper(browser_, login_email, login_passwd, state_file_path="./data/state.json")
        server_id = helper.get_server_by_ip(args.server_ip)
        data = helper.create_webapp(server_id=server_id, domain=args.domain, title=args.title, username=args.user,
                                    password=args.password, email=args.email)
        helper.export_results(data, "./data/sites.csv")
        print(data)
