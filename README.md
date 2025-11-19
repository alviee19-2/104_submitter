## 104 submitter 履歷投遞機器
*一個自動抓取公司職缺、自動投遞公司職缺的程式*


### 架構圖：
<img src="https://github.com/alviee19-2/104_submitter/blob/main/image%20src/104%20submitter.png" width="600">

## 使用流程
### 抓取流程
1. 將authentication貼進**config.py**，coverletter也要貼進去。  
    a. 推薦把你想要把職缺名稱也寫上去 ```SEARCH_KEYWORDS = ["實習", "intern", "在學"]```
3. 接下來會從你想要抓取的公司貼上去**companyList.json**。範例："國泰金控_國泰金融控股股份有限公司": "wjct48g" (key不重要，可以亂打。)
4. **main.py**會把**companyList.json**裡面的公司，對上**SEARCH_KEYWORDS**去抓取。
5. **main.py**會output到**jobList.json**
### 投遞流程
1. **submitter.py**會讀取**jobList.json**所有職缺，開始投遞
2. 結束會會輸出**error.json**、**report.json**。讓你知道那些履歷沒有投遞成功，那些成功。


---  

[架構介紹]  
**config.py**  
**main.py**  
**submitter.py**  

**companyList.json**  
**jobList.json**  
**error.json**  
**report.json**

