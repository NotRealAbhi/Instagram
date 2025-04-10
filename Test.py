import requests
from Config import SESSION_ID
# Replace this with your actual session ID

# URL for your Instagram profile
username = 'soniya_rajput_9911'  # Replace with the username you're testing
url = f'https://www.instagram.com/{username}/'

# Set the headers with the session ID
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

cookies = {
    'sessionid': SESSION_ID
}

# Send the GET request with the session ID
response = requests.get(url, headers=headers, cookies=cookies)

# Check the response
if response.status_code == 200:
    print("Session ID is valid!")
    print("Response Content:")
    print(response.text[:500])  # Print the first 500 characters of the response for inspection
else:
    print(f"Failed to fetch data. Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")  # Print the first 500 characters of the error response
