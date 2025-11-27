import httpx

URL = "https://nookentoktobaev.atlassian.net/wiki/rest/api/content/164060/child/attachment"
FILE = "docs/20251127_052429_new_feature_business_requirements_document.docx"
AUTH = ("nookentoktobaev@gmail.com", "ATATT3xFfGF02z4CTIL0ebYXiEKnAKADAxtnsTnXPnksOMXofQSLQwpbSerPgCFdiVFgVvpEMLQv8YArrqFFq1YM5jYwkFrEFJKDoHmz3OpD2qJZlWJ5AfLWt9ap5adaKDv4bIo9Y4cxlLThQGE3hTh1VqKH8FHx65ph8thKDjvngVoCFNLXWAk")

with open(FILE, "rb") as f:
    files = {
        "file": (FILE, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }

    headers = {"X-Atlassian-Token": "no-check"}  # MUST HAVE

    r = httpx.post(URL, auth=AUTH, files=files, headers=headers)

print(r.status_code, r.text)
