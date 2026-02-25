import requests
import time
import logging
import os
from dotenv import load_dotenv

# Try to import streamlit for secrets handling, fallback for local scripts
try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubClient:
    """
    A resilient GitHub API client with rate limit handling and exponential backoff.
    """
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token=None):
        self.session = requests.Session()
        
        # 1. Try passed token
        # 2. Try Streamlit Secrets (for live hosting)
        # 3. Try Environment Variables (for local dev)
        self.token = token
        if not self.token and st and "GITHUB_TOKEN" in st.secrets:
            self.token = st.secrets["GITHUB_TOKEN"]
        if not self.token:
            self.token = os.getenv("GITHUB_TOKEN")
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            })
        else:
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json"
            })
            logger.warning("No GitHub Token provided. Rate limits will be strictly enforced (60 req/hr).")

    def _request(self, method, endpoint, params=None, retries=3, backoff_factor=2):
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(retries):
            try:
                response = self.session.request(method, url, params=params)
                
                # Check for rate limit hit
                if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
                    if response.headers.get("X-RateLimit-Remaining") == "0":
                        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                        sleep_duration = max(reset_time - time.time(), 0) + 1
                        logger.warning(f"Rate limit exceeded. Sleeping for {sleep_duration:.2f} seconds.")
                        time.sleep(sleep_duration)
                        continue # Retry after sleep
                
                # Handle other 4xx/5xx errors
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if attempt == retries - 1:
                    logger.error(f"HTTP Error after {retries} retries: {e}")
                    raise
                
                sleep_time = backoff_factor ** attempt
                logger.warning(f"Request failed ({e}). Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

    def get_user_info(self, username):
        return self._request("GET", f"/users/{username}")

    def get_user_repos(self, username):
        # Using pagination to get up to 100 repos
        params = {"per_page": 100, "sort": "updated"}
        return self._request("GET", f"/users/{username}/repos", params=params)

    def get_repo_languages(self, owner, repo):
        return self._request("GET", f"/repos/{owner}/{repo}/languages")

    def get_repo_commits(self, owner, repo):
        # Get last 30 commits
        params = {"per_page": 30}
        return self._request("GET", f"/repos/{owner}/{repo}/commits", params=params)
