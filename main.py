import requests
import json
import os 
from company_list import company_list
from config import BASE_DIR, MAIN_URL, BROWSER_HEADER, AUTH_COOKIE_STRING, SEARCH_KEYWORDS
from utils import parse_cookie_header

def fetch_company_jobs(company_list_data: dict = company_list):
    """
    根據公司列表和關鍵字抓取職缺資訊。

    Args:
        company_list_data (dict): 包含公司名稱和其 ID 的字典。
                                  預設使用 company_list 模組中的資料。
    """
    job_list_path = os.path.join(BASE_DIR, "job_list.json")
    all_jobs_data: dict = {}
    cookies = parse_cookie_header(AUTH_COOKIE_STRING)

    for company_name, company_id in company_list_data.items():
        company_jobs = {"data": {"list": {"normalJobs": []}}} # 初始化公司職缺資料
        print(f"開始抓取 {company_name} 的職缺...")

        for keyword in SEARCH_KEYWORDS:
            url = MAIN_URL + f"/company/ajax/joblist/{company_id}"
            params = {
                "job": keyword,
                "page": 1,
                "pageSize": 40,
                "order": 99,
                "asc": 0,
            }
            
            # 複製 BROWSER_HEADER 以便修改 referer
            headers = BROWSER_HEADER.copy()
            headers["referer"] = MAIN_URL + f"/company/{company_id}"

            try:
                resp = requests.get(url, params=params, cookies=cookies, headers=headers)
                resp.raise_for_status() # 如果狀態碼不是 200，則拋出 HTTPError

                response_json = resp.json()
                if response_json and "data" in response_json and "list" in response_json["data"]:
                    fetched_jobs = response_json["data"]["list"].get("normalJobs", [])
                    
                    # 合併職缺，避免重複
                    for job in fetched_jobs:
                        if job not in company_jobs["data"]["list"]["normalJobs"]:
                            company_jobs["data"]["list"]["normalJobs"].append(job)
                            print(f"  - {company_name} 抓取到新職缺: {job.get('jobName', '未知職位')}")
                else:
                    print(f"  - {company_name} 關鍵字 '{keyword}' 無有效職缺資料。")

            except requests.exceptions.RequestException as e:
                print(f"  - {company_name} 關鍵字 '{keyword}' 讀取失敗: {e}")
            except json.JSONDecodeError:
                print(f"  - {company_name} 關鍵字 '{keyword}' 回應不是有效的 JSON。")
        
        all_jobs_data[company_name] = company_jobs
        print(f"{company_name} 職缺抓取完成。")

    with open(job_list_path, "w", encoding="utf-8") as f:
        json.dump(all_jobs_data, f, indent=2, ensure_ascii=False)
    print(f"所有職缺資料已儲存至 {job_list_path}")

def fetch_jd():
    cookies = parse_cookie_header(AUTH_COOKIE_STRING)
    file_dir = os.path.join(BASE_DIR, "job_list.json")
    with open(file_dir, "r", encoding="utf-8") as f:
        job_list = json.load(f)
        
    for item, value in job_list.items():
        print(f"{item}:")
        for each_company_job in value["data"]["list"]["normalJobs"]:
            encodedJobNo = each_company_job["encodedJobNo"]
            print("抓取JD   " + encodedJobNo)
            resp = requests.get(f"https://www.104.com.tw/job/ajax/content/{encodedJobNo}", cookies=cookies, headers=BROWSER_HEADER)
            # print(resp.text[:50])
            # job_list[item]["data"]["list"]["normalJobs"]
            each_company_job["JD"] = resp.json()
    
    with open(file_dir, "w", encoding="utf-8") as f:
        json.dump(job_list, f, indent=2, ensure_ascii=False)
        print(f"職缺描述已儲存至 {file_dir}")

def main():
    fetch_company_jobs()
    fetch_jd()
if __name__ == "__main__":
    main()
