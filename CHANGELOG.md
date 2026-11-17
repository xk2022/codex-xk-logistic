# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- 首片訂單資料模型與 OpenAPI 3.1.0 契約 v0.1.0：建立／完整替換草稿、清單、明細、只讀受理欄位檢核，共五項操作；包含版本衝突、重送、暫存參照、統一 traceId envelope 與合成正反例。
- 契約檢查紀錄，區分文件／schema 驗證與尚未執行的 DB／HTTP／產品驗收；不代表服務已上線。

### Changed

- 使用者於2026-11-17採用 ORD-P01～P03；D04 的草稿／受理及類型必填基準轉為已確認，其餘業務例外、資料接續與維運仍待確認。
- 首片 API 使用 DRAFT 表達待受理草稿、PUT 表達完整替換、traceId 表達請求追查；取代舊概念稿的 NEW／PATCH／requestId。新版 API 尚未實作或部署，無既有消費端遷移；舊 Truck 不受本變更影響。
