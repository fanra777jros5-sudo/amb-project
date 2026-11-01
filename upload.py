import requests
import base64
import os
import sys
from pathlib import Path
from datetime import datetime

# ==========================================
# AMB PROJECT — GITHUB UPLOADER
# ==========================================

USERNAME = "YOUR_GITHUB_USERNAME"
REPOSITORY = "amb-project"
BRANCH = "main"

FILE_PATH = Path("index.html")

TOKEN = os.getenv("GITHUB_TOKEN")

API_URL = (
    f"https://api.github.com/repos/"
    f"{USERNAME}/{REPOSITORY}/contents/{FILE_PATH.name}"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


def check_configuration():
    if not TOKEN:
        print("[ERROR] GitHub token not found!")
        print("Set GITHUB_TOKEN environment variable.")
        sys.exit(1)

    if USERNAME == "YOUR_GITHUB_USERNAME":
        print("[ERROR] Enter your GitHub username.")
        sys.exit(1)

    if not FILE_PATH.exists():
        print("[ERROR] index.html not found!")
        sys.exit(1)


def get_file_sha():
    response = requests.get(
        API_URL,
        headers=HEADERS,
        params={"ref": BRANCH},
        timeout=20
    )

    if response.status_code == 200:
        return response.json()["sha"]

    if response.status_code == 404:
        return None

    raise Exception(
        f"GitHub API error: {response.status_code}\n"
        f"{response.text}"
    )


def upload_website():
    print("\n================================")
    print("       AMB PROJECT UPLOADER")
    print("================================\n")

    check_configuration()

    print("[1/3] Reading website...")

    content = FILE_PATH.read_bytes()

    encoded_content = base64.b64encode(
        content
    ).decode("utf-8")

    print("[2/3] Checking GitHub repository...")

    sha = get_file_sha()

    payload = {
        "message": (
            "AMB website update — "
            + datetime.now().strftime("%Y-%m-%d %H:%M")
        ),
        "content": encoded_content,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha
        print("Existing website found. Updating...")
    else:
        print("Creating new website...")

    print("[3/3] Uploading website...")

    response = requests.put(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if response.status_code in (200, 201):
        print("\n[SUCCESS] AMB website uploaded!")

        print(
            f"\nWebsite repository:\n"
            f"https://github.com/{USERNAME}/{REPOSITORY}"
        )

        print(
            f"\nGitHub Pages address:\n"
            f"https://{USERNAME}.github.io/{REPOSITORY}/"
        )

    else:
        print("\n[ERROR] Upload failed!")
        print(response.status_code)
        print(response.text)


if __name__ == "__main__":
    try:
        upload_website()

    except requests.RequestException as error:
        print(f"\n[NETWORK ERROR] {error}")

    except Exception as error:
        print(f"\n[ERROR] {error}")