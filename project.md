# Project dev
--- 
## 已完成
1. 根據company list hard coded的資料抓取職缺
2. 自動submit履歷的機器
3. 兩個API documentation
## 待完成(需要觀察新的API)
1. 自動抓取已投遞的工作 (使用者自行處理 API 探索)

## 待完成 - 程式碼優化
1. 優化關鍵字(keyword)搜尋 company list 的職缺
2. 提升程式碼可用性與可讀性
    1. 變數名稱難以理解 -> 重新命名變數，使其更具描述性
    2. 函數拆分，使功能更專一
    3. 增加註釋與文件字串 (docstrings)
3. 提升鬆散耦合 (Loose Coupling) 與配置管理
    1. 集中管理配置 (例如：`BASE_URL`, `browser_header`, `cookie`)
    2. 模組間的依賴注入 (Dependency Injection)
    3. 考慮類別封裝 (Class Encapsulation)

## 待完成 - 程式完整性提升 (未來規劃)
1. 錯誤處理和日誌記錄 (Error Handling and Logging)
2. 排程功能 (Scheduling)，讓程式自動定期執行
3. 資料庫或持久化儲存 (Database or Persistent Storage)，追蹤已投遞職位，避免重複投遞
4. 使用者介面 (User Interface)，方便配置與監控
5. 更智慧的投遞策略 (Smarter Application Strategy)，自動篩選匹配職位
6. 通知機制 (Notification Mechanism)，即時回報程式運行狀態
7. 使用telegram 自動掃一次 (先不用完成)
