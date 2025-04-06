from re import IGNORECASE, compile

from httpx import Client, RequestError

from app.core.settings import settings


def fetch_description(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com",
    }

    try:
        with Client(headers=headers, proxy=settings.PROXY, verify=False, follow_redirects=True) as client:
            response = client.get(url)

        if response.is_success:
            meta_description_pattern = compile(
                r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
                IGNORECASE,
            )

            if match := meta_description_pattern.search(response.text):
                return match.group(1)
            return "No description tag found."
        return f"Failed to fetch the page, status code: {response.status_code}"

    except RequestError as e:
        return f"Error fetching the page: {e}"
