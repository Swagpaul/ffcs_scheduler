import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen('https://ffcsscheduler-production.up.railway.app/api/data')
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print(e.read().decode())
