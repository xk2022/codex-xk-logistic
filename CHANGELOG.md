# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Accepted ADR-0008與機器可讀的15個單角色／operation對照；另增Proposed隔離測試啟動包DEV-P01、START-P01～P04。

- ADR-0007：使用者確認沒有必須保留的舊Truck客戶／訂單／照片，本次採M01全新啟用；未執行舊資料匯入或刪除。
- 首片權限與測試環境提案ACC-P01／P02、DEV-P01，明示Proposed及環境／驗收待辦，不變更授權政策。

- 首片訂單資料模型與 OpenAPI 3.1.0 契約 v0.1.0：建立／完整替換草稿、清單、明細、只讀受理欄位檢核，共五項操作；包含版本衝突、重送、暫存參照、統一 traceId envelope 與合成正反例。
- 契約檢查紀錄，區分文件／schema 驗證與尚未執行的 DB／HTTP／產品驗收；不代表服務已上線。

### Changed

- 使用者明確採用ACC-P01／P02，五項草稿API的管理員／調度員本公司範圍與司機整單拒絕已記錄；OpenAPI文件轉0.2.0，paths／request／response schema與sessionAuth技術不變。尚無產品實作，其他登入／環境政策未一併核准。

- 使用者於2026-11-17採用 ORD-P01～P03；D04 的草稿／受理及類型必填基準轉為已確認，其餘業務例外與維運仍待確認；D07本次後續已依ADR-0007採M01。
- 首片 API 使用 DRAFT 表達待受理草稿、PUT 表達完整替換、traceId 表達請求追查；取代舊概念稿的 NEW／PATCH／requestId。新版 API 尚未實作或部署，無既有消費端遷移；舊 Truck 不受本變更影響。
