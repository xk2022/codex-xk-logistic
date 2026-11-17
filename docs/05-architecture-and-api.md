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

## 最新技術提案

2026-11-17 使用者回覆「是！採用」，已確認 [Java 21／Boot 4.1.x、React／TypeScript／Vite、PostgreSQL 17、JPA、Session／CSRF 與 Flyway](TECHNOLOGY_AND_DATA_PROPOSAL.md)，ADR-0002～0006 為 Accepted。以下保留已採用基準與剩餘細節，精確版本、詳細授權／復原及環境待定；本輪未建立程式或正式 OpenAPI。

## 已採用技術與剩餘選項

| 項目 | 已採用／候選 | 仍待完成 |
|---|---|---|
| 前端 | 已採用 React／TypeScript／Vite | 精確版本、UI 元件／樣式及資產授權待定；Tailwind 仍為候選 |
| 後端 | 已採用 Java 21／Spring Boot 4.1.x；Spring Security 實作 Session／CSRF | 核對並鎖定修補版及相容 BOM／工具 |
| DB | 已採用 PostgreSQL 17 | 修補版與相依待驗證；舊 MySQL 資料是否／如何接續仍待 D07 |
| 資料存取 | 已採用 Spring Data JPA；查詢視需要用投影／明確查詢 | Entity／交易／鎖與效能依核定業務規格設計、驗收 |
| 認證 | 已採用同源瀏覽器 Session＋CSRF | 詳細逾時、復原、各動作資料授權待 D02／D10；外部 App 是後續候選 |
| 結構版本 | 已採用 Flyway，JPA 驗證映射 | PostgreSQL module／版本與空庫／升級驗收待完成 |
| 檔案 | 候選：S3 相容儲存介面；開發本機 adapter | 供應商、容量、保存期限與存取政策 |
| 部署 | 前後端獨立建置，反向代理同源 /api | 雲端平台、staging／production 與網域 |

「前後端分離」為程式、契約、建置與測試分離；不要求不同網域或微服務。沿 G2 的同源代理可簡化 Cookie 與 CSRF。Session Cookie 採 Secure／HttpOnly／SameSite，寫入檢查 CSRF 與來源；登出與停權能撤銷存取。前端不在 localStorage 保存長效登入 token。Session＋CSRF 技術選擇已確認；具體 Cookie／逾時、停權及授權細節依 D02／D10 定稿並驗收。

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
