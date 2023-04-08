# Runcloud Helper

## Installation
### Using pip
```angular2html
pip install git+https://github.com/cefege/Runcloud-Helper.git
```
or clone the repository
```angular2html
git clone https://github.com/cefege/Runcloud-Helper.git
```
## Usage
- Import `playwright` and `RCHelper` 
```
from playwright.sync_api import sync_playwright
from RCHelper import RunCloudHelper
```
- Get Server ID by IP
```
server_id = helper.get_server_by_ip({IP-Address})
```

- Create New WebApp
```angular2html
data = helper.create_webapp(server_id, domain, title, username, password, email)
```
Alternatively,
```angular2html
python main.py --login-email="" --login-passwd="" --server-ip="" --domain="" --title="" --user="" --email=""
```
or
```angular2html
python main.py --credential-file="Path to a newline separated email and password" --server-ip="" --domain="" --title="" --user="" --email=""
```
