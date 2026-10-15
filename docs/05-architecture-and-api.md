# 前後端架構與 API 草案

## 建議結構

```text
frontend/                 React + TypeScript + Vite
backend/                  Java 21 + Spring Boot
  src/main/.../upms/
  src/main/.../adm/
  src/main/.../crm/
  src/main/.../ordercore/
  src/main/.../tom/
  src/main/.../fms/
  src/main/resources/db/migration/
docs/                     規格、決策、驗收
  api/openapi.yaml        確認規格後才建立
compose.yaml              確認後建立本機服務
```

以上為目標，不代表這些程式檔已存在。後端採模組化單體，HTTP／應用用例／領域規則／資料存取分層。避免單純為 CRUD 複製大量 Port／Adapter；跨領域交易與外部儲存才明確建立介面。

## 選型候選

| 項目 | 建議 | 尚待決定 |
|---|---|---|
| 前端 | React／TypeScript／Vite／Tailwind，自有元件 | 版型與是否有可用 Metronic 授權 |
| 後端 | Java 21／Spring Boot／Spring Security | 實作時確認受支援且相容的精確版本 |
| DB | PostgreSQL 17／Flyway，對齊 G2 | 是否保留 MySQL 與舊資料遷移 |
| 資料存取 | 明確 SQL／JDBC 或 JPA 搭配投影均可 | G2 用 JDBC、G1 用 JPA；不能以換 DB 自動決定 ORM |
| 認證 | 伺服器 Session＋CSRF | 是否需要外部 App token 用例 |
| 檔案 | S3 相容儲存介面；本機可用本機 adapter | 供應商、容量、保存期限與存取政策 |
| 部署 | 前後端獨立建置，反向代理同源 /api | 雲端平台、staging／production 與網域 |

「前後端分離」為程式、契約、建置與測試分離；不要求不同網域或微服務。沿 G2 的同源代理可簡化 Cookie 與 CSRF。Session Cookie 採 Secure／HttpOnly／SameSite，寫入檢查 CSRF 與來源；登出與停權能撤銷存取。前端不在 localStorage 保存長效登入 token。這些是推薦基準，實作前仍須確認 D01。

## API 共通規範候選

- `/api/v1`，JSON；UUID 字串，列舉代碼大寫。
- 分頁 page=0 起，size 預設 20、上限 100；排序欄白名單；過濾與授權在資料庫查詢層完成。
- 列表回 data、page、size、totalElements；錯誤回 code、message、fieldErrors、requestId，確認後寫入 OpenAPI。
- 400 格式／驗證、401 未登入、403 無權限、404 不存在或範圍遮罩、409 版本／占用／狀態衝突、429 限流。
- 動作使用明確端點；不能讓前端任意 PATCH status 跳過業務規則。
- availableActions 可由後端回傳供 UI 顯示，執行時後端仍重新驗證。

## API 清單草案

| 範圍 | 端點與動作 |
|---|---|
| 認證 | GET /csrf-token；POST /sessions；DELETE /sessions/current；GET /me |
| 本人 | PATCH /me/profile；POST /me/password-changes |
| UPMS | /users、/roles、/permissions 列表／明細／管理；使用者角色與角色權限指派 |
| ADM | /dictionary-categories、分類項目、排序與 /system-parameters |
| CRM | /customers 列表／建立／明細／編輯／啟停；聯絡人依範圍確認 |
| 訂單 | GET／POST /orders；GET／PATCH /orders/{id}；POST /orders/{id}/accept、/cancel、/close；GET /orders/{id}/history |
| 貨櫃 | /orders/{id}/containers；編輯、查詢規則待 D03／D04 |
| 運輸任務 | /transport-tasks 列表／建立／明細；關聯訂單或貨櫃，待 D03 |
| 車隊 | /vehicles、/drivers 列表／建立／明細／編輯；狀態動作另定 |
| 派工 | POST /dispatches；GET /dispatches、/{id}；POST /dispatches/{id}/start、/sign、/complete、/cancel；改派待 D05 |
| 司機 | GET /me/dispatches；本人 on-duty 動作；使用派工動作並強制本人範圍 |
| 資產 | 簽收照片上傳、完成驗證及授權讀取流程，待 D06 |
| 總覽 | GET /dashboard/summary |

本表未加上的完整前綴均為 `/api/v1`。UPMS 管理的密碼重設、首次改密碼與忘記密碼需另定交付政策，不能直接回傳密碼或假裝已寄信。

## 遷移與實作注意

Flyway 建立結構及唯一約束，不依 ddl-auto=update 管理正式資料；所有秘密由環境注入，範例檔只放佔位值。照片需驗證實際格式、大小與歸屬，不能讓司機讀取他人資產。正式監控、備份與還原需在上線前驗收。

本機舊前端含商業模板目錄，本次不散布資產。新版先自行建立一致元件，若取得授權再決定是否使用模板。
