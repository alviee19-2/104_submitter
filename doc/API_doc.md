# 104 API Documentation
---
Base URL: 
https://www.104.com.tw

## Endpoints

### 1. 公司相關 API
#### 1.1 公司職缺列表 GET /company/ajax/joblist/{companyId}
**Query Parameters**
- `job`: 關鍵字 (例: `實習`)
- `page`: 頁數
- `pageSize`: 每頁筆數
- `order`: 排序方式
- `asc`: 升/降冪 (0 = 降冪, 1 = 升冪)

### 2. 投遞相關 API
#### 2.1 投遞工作 GET job/ajax/apply/{jobId}
**Query Parameters**
- `custNo`: 公司id
### 2.1 刪除投遞 DELETE job/ajax/apply/{jobId}
**無parameters**
