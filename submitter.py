import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests

from config import (
    BASE_DIR,
    MAIN_URL,
    BROWSER_HEADER,
    AUTH_COOKIE_STRING,
    SUBMIT_API_URL,
    DEFAULT_APPLY_MESSAGE,
    DEFAULT_CUST_NO,
    QUANT_INTERN,
    FINANCE_INTERN,
    ACCOUNTING_INTERN,
    TRADE_INTERN,
    PM_INTERN,
)
from utils import parse_cookie_header


@dataclass
class JobApplication:
    """```description
    Lightweight container for submission details resolved from the job list.
    ```"""
    company_name: str
    job_name: str
    job_code: str
    cust_no: str
    message_key: str
    message: str

    def to_report_entry(self) -> Dict[str, str]:
        """```description
        Convert the application into a serialisable dict for reporting output.
        ```"""
        return {
            "companyName": self.company_name,
            "jobName": self.job_name,
            "jobCode": self.job_code,
            "custNo": self.cust_no,
            "messageKey": self.message_key,
            "message": self.message,
        }


MATCHED_TEMPLATES = [
    ("QUANT_INTERN", QUANT_INTERN, ("quant", "量化", "數據", "模型", "data science", "algo", "derivative")),
    ("FINANCE_INTERN", FINANCE_INTERN, ("finance", "金融", "財務", "investment", "投資", "banking", "wealth")),
    ("ACCOUNTING_INTERN", ACCOUNTING_INTERN, ("account", "會計", "查帳", "auditing", "稅", "報表")),
    ("TRADE_INTERN", TRADE_INTERN, ("trade", "國貿", "貿易", "supply chain", "進出口", "export", "import")),
    ("PM_INTERN", PM_INTERN, ("pm", "產品經理", "product manager", "產品管理", "專案管理", "project manager")),
]


def load_job_list(path: str) -> dict:
    """```description
    Load the saved job list JSON from disk so callers can inspect each JD entry.
    ```"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"job list not found at {path}")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_job_text(job: dict) -> str:
    """```description
    Collect every textual snippet from a job payload to feed keyword matching.
    ```"""
    texts: List[str] = []

    def append_text(value: Any) -> None:
        """```description
        Recursively extract string values from nested job fields.
        ```"""
        if isinstance(value, str):
            value = value.strip()
            if value:
                texts.append(value)
        elif isinstance(value, list):
            for item in value:
                append_text(item)
        elif isinstance(value, dict):
            for item in value.values():
                append_text(item)

    append_text(job.get("jobDescription"))

    jd = job.get("JD")
    if isinstance(jd, dict):
        jd_data = jd.get("data")
        if isinstance(jd_data, dict):
            append_text(jd_data.get("jobDetail"))
            append_text(jd_data.get("condition"))
            append_text(jd_data.get("welfare"))
    return "\n".join(texts)


def determine_apply_message(job: dict) -> Tuple[Optional[str], Optional[str]]:
    """```description
    Select the appropriate apply message template based on keywords found in the JD.
    ```"""
    job_name = job.get("jobName", "")
    combined_text = "\n".join(filter(None, [job_name, extract_job_text(job)]))
    lowered_text = combined_text.lower()

    for key, template, keywords in MATCHED_TEMPLATES:
        for keyword in keywords:
            if keyword.lower() in lowered_text:
                selected_message = template or DEFAULT_APPLY_MESSAGE
                return key, selected_message

    return None, None


def prepare_job_data(job_list_path: str) -> Tuple[List[JobApplication], List[Dict[str, str]]]:
    """```description
    Flatten the job list JSON into unique applications and collect unmatched jobs.
    ```"""
    job_list = load_job_list(job_list_path)
    applications: List[JobApplication] = []
    unmatched: List[Dict[str, str]] = []
    seen_codes = set()

    for company_name, company_payload in job_list.items():
        company_data = company_payload if isinstance(company_payload, dict) else {}
        normal_jobs = (
            company_data.get("data", {})
            .get("list", {})
            .get("normalJobs", [])
        )

        for job in normal_jobs:
            if not isinstance(job, dict):
                continue

            job_code = job.get("encodedJobNo") or job.get("jobNo")
            job_name = job.get("jobName", "未命名職缺")

            if not job_code:
                unmatched.append(
                    {
                        "companyName": company_name,
                        "jobName": job_name,
                        "jobCode": "",
                        "reason": "missing_job_code",
                    }
                )
                continue

            if job_code in seen_codes:
                continue
            seen_codes.add(job_code)

            message_key, message = determine_apply_message(job)

            cust_no = DEFAULT_CUST_NO
            jd = job.get("JD")
            if isinstance(jd, dict):
                jd_data = jd.get("data")
                if isinstance(jd_data, dict):
                    jd_cust_no = jd_data.get("custNo")
                    if jd_cust_no:
                        cust_no = jd_cust_no
            job_level_cust_no = job.get("custNo")
            if job_level_cust_no:
                cust_no = job_level_cust_no

            if message_key is None or message is None:
                unmatched.append(
                    {
                        "companyName": company_name,
                        "jobName": job_name,
                        "jobCode": job_code,
                        "custNo": cust_no,
                        "reason": "template_not_found",
                    }
                )
                continue

            applications.append(
                JobApplication(
                    company_name=company_name,
                    job_name=job_name,
                    job_code=job_code,
                    cust_no=cust_no,
                    message_key=message_key,
                    message=message,
                )
            )

    return applications, unmatched


def preview_applications(applications: List[JobApplication], unmatched: List[Dict[str, str]]) -> None:
    """```description
    Print a human-readable preview of matched and unmatched jobs before submission.
    ```"""
    print("\n=== Applications Preview ===")
    if not applications:
        print("No applications ready for submission.")
    else:
        for index, app in enumerate(applications, start=1):
            print(f"[{index}] {app.company_name} - {app.job_name}")
            print(f"     job_code: {app.job_code} | custNo: {app.cust_no}")
            print(f"     message ({app.message_key}): {app.message}")

    if unmatched:
        print("\n--- Unmatched Jobs (see error.json) ---")
        for item in unmatched:
            print(
                f"* {item['companyName']} - {item['jobName']} "
                f"(code: {item.get('jobCode', '') or 'N/A'} | reason: {item['reason']})"
            )
    print("============================\n")


def submit_applications(applications: List[JobApplication]) -> None:
    """```description
    Send application payloads to the submit API using the resolved templates.
    ```"""
    if not applications:
        print("No applications to submit.")
        return

    cookies = parse_cookie_header(AUTH_COOKIE_STRING)

    for app in applications:
        post_url = f"{SUBMIT_API_URL}/{app.job_code}"
        headers = BROWSER_HEADER.copy()
        headers["referer"] = f"{MAIN_URL}/job/{app.job_code}?apply=form"

        payload = {
            "custNo": app.cust_no,
            "jobSource": "m104",
            "versionNo": "76635rid1",
            "applyMsg": {
                "id": "0",
                "msg": app.message,
                "operation": 2,
            },
            "questions": [],
        }

        print(f"Submitting {app.company_name} - {app.job_name} ({app.job_code}) with {app.message_key}")
        response = None
        try:
            response = requests.post(
                post_url,
                data=json.dumps(payload, ensure_ascii=False),
                cookies=cookies,
                headers=headers,
            )
            response.raise_for_status()
            if response.status_code == 204:
                print("  -> Submit succeeded (204).")
            else:
                print(f"  -> Submit completed with status {response.status_code}.")
        except requests.exceptions.RequestException as exc:
            print(f"  -> Submit failed: {exc}")
            if response is not None and response.text:
                print(f"     Response body: {response.text}")


def delete_job_applications(applications: List[JobApplication]) -> None:
    """```description
    Issue delete requests for previously submitted applications when requested.
    ```"""
    if not applications:
        print("No applications to delete.")
        return

    cookies = parse_cookie_header(AUTH_COOKIE_STRING)

    for app in applications:
        delete_url = f"{SUBMIT_API_URL}/{app.job_code}"
        headers = BROWSER_HEADER.copy()
        headers["referer"] = f"{MAIN_URL}/job/{app.job_code}?apply=form"

        print(f"Deleting application for {app.company_name} - {app.job_name} ({app.job_code})")
        response = None
        try:
            response = requests.delete(
                delete_url,
                params={"custNo": app.cust_no},
                cookies=cookies,
                headers=headers,
            )
            response.raise_for_status()
            if response.status_code == 204:
                print("  -> Delete succeeded (204).")
            else:
                print(f"  -> Delete completed with status {response.status_code}.")
        except requests.exceptions.RequestException as exc:
            print(f"  -> Delete failed: {exc}")
            if response is not None and response.text:
                print(f"     Response body: {response.text}")


def write_reports(applications: List[JobApplication], unmatched: List[Dict[str, str]]) -> None:
    """```description
    Persist submission-ready jobs and unmatched entries to report.json and error.json.
    ```"""
    error_path = os.path.join(BASE_DIR, "error.json")
    report_path = os.path.join(BASE_DIR, "report.json")

    with open(error_path, "w", encoding="utf-8") as error_file:
        json.dump(unmatched, error_file, indent=2, ensure_ascii=False)

    report_payload = {
        "submit": [app.to_report_entry() for app in applications],
        "error": unmatched,
    }
    with open(report_path, "w", encoding="utf-8") as report_file:
        json.dump(report_payload, report_file, indent=2, ensure_ascii=False)

    print(f"Saved error details to {error_path}")
    print(f"Saved submission report to {report_path}")


def main() -> None:
    """```description
    Drive the CLI workflow: load jobs, preview them, and optionally submit or delete.
    ```"""
    job_list_path = os.path.join(BASE_DIR, "job_list.json")
    try:
        applications, unmatched = prepare_job_data(job_list_path)
    except FileNotFoundError as error:
        print(error)
        return

    preview_applications(applications, unmatched)
    write_reports(applications, unmatched)

    if not applications:
        return

    should_submit = input("Submit the above applications? (Y/N): ").strip().lower()
    if should_submit == "y":
        submit_applications(applications)
    else:
        print("Submission skipped.")

    should_delete = input("Delete the submitted applications? (Y/N): ").strip().lower()
    if should_delete == "y":
        delete_job_applications(applications)
    else:
        print("Deletion skipped.")


if __name__ == "__main__":
    main()
