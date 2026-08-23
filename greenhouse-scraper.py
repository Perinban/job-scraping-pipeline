from __future__ import annotations

import html
import json
import logging
import os
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)
API_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
def plain_text(value: str | None) -> str:
    soup = BeautifulSoup(html.unescape(value or ""), "html.parser")
    return "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())


def normalize_job(board: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    description = plain_text(job.get("content"))
    departments = [item.get("name") for item in job.get("departments", []) if item.get("name")]
    title = str(job.get("title") or "").strip()
    return {
        "Company_Name": board["company_name"],
        "Company_Logo_Url": board.get("logo_url"),
        "Job_URL": job.get("absolute_url"),
        "Job_Title": title,
        "Job_Location": (job.get("location") or {}).get("name"),
        "Job_Status": None,
        "Job_Domain": ", ".join(departments) or None,
        "Job_Salary": None,
        "Job_Details": [{"header": "Description", "content": description}],
        "Last_Updated": job.get("updated_at"),
        "reject_reason": None,
    }


def fetch_board(session: requests.Session, board: dict[str, Any], timeout: int = 30) -> list[dict[str, Any]]:
    response = session.get(API_TEMPLATE.format(token=board["board_token"]), params={"content": "true"}, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return [normalize_job(board, job) for job in payload.get("jobs", [])]


def load_boards(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    boards = []
    for item in data:
        token = str(item.get("board_token") or "").strip().lower()
        company = str(item.get("company_name") or "").strip()
        if token and company and token not in seen:
            seen.add(token)
            boards.append({**item, "board_token": token, "company_name": company})
    return boards


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
    boards = load_boards(Path(os.getenv("GREENHOUSE_BOARDS_FILE", "greenhouse_boards.json")))
    output = Path(os.getenv("GREENHOUSE_OUTPUT_FILE", "greenhouse_job_summary.json"))
    jobs: list[dict[str, Any]] = []
    failures = 0
    with requests.Session() as session:
        session.headers.update({"User-Agent": "TalentBlissGreenhouse/1.0"})
        for board in boards:
            try:
                board_jobs = fetch_board(session, board)
                jobs.extend(board_jobs)
                LOGGER.info("%s: %d jobs", board["board_token"], len(board_jobs))
            except (requests.RequestException, ValueError) as error:
                failures += 1
                LOGGER.warning("%s failed: %s", board["board_token"], error)
    deduped = {job["Job_URL"]: job for job in jobs if job.get("Job_URL")}
    records = sorted(deduped.values(), key=lambda item: (item["Company_Name"].lower(), item["Job_Title"].lower(), item["Job_URL"]))
    output.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    LOGGER.info("Saved %d Greenhouse jobs from %d boards (%d failures)", len(records), len(boards), failures)
    if boards and failures == len(boards):
        raise RuntimeError("All Greenhouse boards failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
