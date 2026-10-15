# 來源盤點與證據

## 搜尋方式與限制

2026-10-15 搜尋本機使用者家目錄中名稱包含 truck 或 logistic 的目錄（不分大小寫），另檢查命中專案的父層。第一輪針對 projects、Documents、Desktop、Downloads 與常見開發目錄；第二輪家目錄搜尋深度最多八層，略過隱藏目錄、Library、node_modules、target、dist、build、Pods 與虛擬機。這是可讀開發目錄的搜尋結果，並非整台電腦每個磁碟與壓縮檔的完整鑑識。

以下本機位置以 `~/` 縮寫記錄供追溯；雲端不能直接存取，必要結論與候選欄位已整理到其他文件。

## GitHub 基準

| ID | 專案與固定版本 | 用途 |
|---|---|---|
| G1 | [xk-truck-platform](https://github.com/xk2022/xk-truck-platform/tree/9a967bfc1b56fdccac6376fd08b7a6083582c876) | 物流領域與既有 API 程式 |
| G2 | [codex-xk-rotaract](https://github.com/xk2022/codex-xk-rotaract/tree/a4504de8add16941dae43fee2a2edc5ed260bafc) | 前後端分離、API 契約、遷移與驗收方式 |

兩個基準以唯讀分析目的 clone 至暫存目錄。G2 含有未完成模組，不以文件規劃當作完整後端。

## 本機來源

| ID | 本機位置 | 觀察 | 採用方式 |
|---|---|---|---|
| L1 | `~/Git/base` 中的 `src/main/java/com/xk/truck`、`templates/truck`、`static/static_truck` | 舊 MVC 系統；truck Java 區有 38 個檔案；客戶、車輛、權限與任務入口 | 追溯用語與客戶來源，不沿用舊 UI 技術 |
| L2 | `~/Git/xk/xkTruck` | pom 指向 Java 8；有 Thymeleaf、JPA／MyBatis、UPMS controllers 與模板 | 權限管理操作參考，非新版物流核心 |
| L3 | `~/Git/xk/truck` | src 主要是 BaseApplication、TestController 與設定檔 | 啟動骨架，不當成功能來源 |
| L4 | `~/XKsystem25/xk-logistics-platform` | Java 21、Spring Boot 3.5.0 設定；src 中僅見兩個 Java 檔 | 架構試作，不當成完整物流平台 |
| L5 | `~/XKsystem25/xk-system/xk-truck` | 觀察到 pom，未找到 Java 程式；父層另有 xk-base、common 等模組 | 模組命名參考 |
| L6 | `~/XKsystem25/xk-truck-platform`（含內層 xk-truck） | 搜尋未找到可分析的一般程式檔 | 空／未完整目錄，不能推論已有實作 |
| L7 | `~/XKsystem25/xk-logistics/xk-truck-platform` | 後端與規格副本 | 與 G1 交叉比對 |
| L8 | `~/XKsystem25/xk-logistics/xkbase-app/frontend` | React 18、TS、Vite、Bootstrap、Metronic 目錄；TOM／FMS／CRM／PORT 等頁面與型別 | 最重要的本機補充來源，摘要保存至本文件集 |
| L9 | `~/XKsystem25/xk-logistics` 的專案建議報告、登入與權限分析 | 既有評估與整合建議 | 作為待驗證背景，不照抄完成率與工時 |
| T | `~/projects/codex-demo/codex-xk-logistic` | 本次目標 repo；文件製作前無提交與程式 | 新版交付位置 |

上述 L1～L7 的指定專案根目錄未辨識為 Git 工作樹，無可靠本機 commit ID，故以選取檔案的內容指紋留存。不能據目錄名稱建立 GitHub 來源連結。

## 重複來源比對

L7 與 G1 對照 `.java`、`.md`、`.xml`，排除 .git／IDE／target／node_modules：213 個本機檔案內容相同，0 個差異，0 個本機獨有。此結果是由本機向 G1 單向比對，不涵蓋 yml、SQL、圖片與建置產物，也不代表兩目錄每個檔案都相同。

## 關鍵證據入口

- G1：`README.md`、`業務邏輯定義文件.md`。
- G1：`xk-truck/src/main/java/com/xk/truck/tom/controller/api/TomOrderController.java`；多個 GET／派單入口被註解。
- G1：`.../tom/domain/model/TomOrder.java`、`TomOrderType.java`、`TomOrderStatus.java`。
- G1：`.../fms/domain/service/DispatchService.java`、`.../fms/domain/model/DispatchStatus.java`。
- G2：`docs/architecture.md`、`backend/README.md`、`frontend/package.json`、`compose.yaml`。
- L1：`src/main/java/com/xk/truck/information/model/po/T_Customer.java` 與 `modules/model/po/T_Task.java`。
- L8：`src/app/pages/tom/order/Model.tsx`、`Query.tsx`；`tom/container/Model.tsx`；`tom/tasks/Model.tsx`；`crm/Model.tsx`；`port/Model.ts`。

本次只做靜態分析；未執行來源專案，不將舊報告中的完成率、測試數與估時當成本次驗證結果。
