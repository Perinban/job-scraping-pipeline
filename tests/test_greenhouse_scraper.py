import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "greenhouse-scraper.py"
spec = importlib.util.spec_from_file_location("greenhouse_scraper", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class GreenhouseTests(unittest.TestCase):
    def test_normalize_job_uses_talentbliss_schema_only(self):
        board = {"board_token": "acme", "company_name": "Acme"}
        job = {
            "id": 123,
            "title": "Software Engineering Intern",
            "location": {"name": "Berlin"},
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/123",
            "updated_at": "2026-07-28T00:00:00Z",
            "language": "en",
            "content": "<p>Build useful software.</p>",
            "departments": [{"name": "Engineering"}],
            "offices": [{"name": "Berlin"}],
        }
        result = module.normalize_job(board, job)
        self.assertEqual(
            set(result),
            {
                "Company_Name",
                "Company_Logo_Url",
                "Job_URL",
                "Job_Title",
                "Job_Location",
                "Job_Status",
                "Job_Domain",
                "Job_Salary",
                "Job_Details",
                "Last_Updated",
                "reject_reason",
            },
        )
        self.assertEqual(result["Job_Title"], "Software Engineering Intern")
        self.assertEqual(result["Job_Domain"], "Engineering")

    def test_regular_jobs_are_included(self):
        board = {"board_token": "acme", "company_name": "Acme"}
        job = {
            "id": 456,
            "title": "Senior Finance Manager",
            "location": {"name": "Munich"},
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/456",
            "content": "<p>Lead the finance organization.</p>",
        }
        result = module.normalize_job(board, job)
        self.assertEqual(result["Job_URL"], job["absolute_url"])
        self.assertEqual(result["Job_Title"], "Senior Finance Manager")


if __name__ == "__main__":
    unittest.main()
