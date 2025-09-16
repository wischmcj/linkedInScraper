import os 
# Pipeline Global Settings
SEARCH_LIMIT = 100

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

API_BASE_URL = "https://www.linkedin.com/voyager/api"
REQUEST_HEADERS = {
    "user-agent": " ".join(
        [
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/133.0.0.0 Mobile Safari/537.36",
        ]
    ),
    'accept-language': 'en-US,en;q=0.9',
    "x-li-lang": "en_US",
    "x-restli-protocol-version": "2.0.0",
    # "accept": "application/vnd.linkedin.normalized+json+2.1"
}
#Auth\
AUTH_BASE_URL = "https://www.linkedin.com"
AUTH_REQUEST_HEADERS = {
    "X-Li-User-Agent": "LIAuthLibrary:3.2.4 \
                        com.linkedin.LinkedIn:8.8.1 \
                        iPhone:8.3",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
    "X-User-Language": "en",
    "X-User-Locale": "en_US",
    "Accept-Language": "en-us",
}

BATCH_SIZE = 25

client_defaults = {
    'base_url': API_BASE_URL,
}
resource_defaults = {
    'write_disposition': 'merge',
}

standalones = {
    ''
}
