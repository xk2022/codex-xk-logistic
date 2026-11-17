# XK Logistic 製作文件

初版文件日期：2026-10-15；狀態更新：2026-11-17（Asia/Taipei）。新版重建方向、部分產品基準及 Java／React／PostgreSQL／JPA／Flyway／Session 技術方案已確認；其餘子項、資料接續與上線決策待確認，產品尚未實作。

本次任務是統整 GitHub 與本機 truck／logistic 專案，讓 2026-10-16 的雲端工作能直接延續。上傳文件不代表同意技術選型、功能範圍或開始開發。

## 最新入口

- [已採用技術與資料接續提案](TECHNOLOGY_AND_DATA_PROPOSAL.md)：六項技術方案已採用，五份 ADR 轉為 Accepted；精確版本／整合待驗證，資料接續現況維持待確認。

- [決策與剩餘子項](06-decisions-and-acceptance.md)：已確認基準優先於舊文件的概括未決說法。
- [重建方向 ADR](adr/ADR-0001.md)、[功能差異矩陣](TRUCK_PLATFORM_TO_LOGISTICS_MATRIX.md)。
- [舊碼靜態核對與固定版本證據](SOURCE_CODE_AUDIT_20261117.md)、[45 個來源檔案清單](SOURCE_AUDIT_MANIFEST_20261117.json)。
- [第一個開發切片及前提](REBUILD_DELIVERY_SLICES.md)、[主要任務 Issue #4](https://github.com/xk2022/codex-xk-logistic/issues/4)。

## 閱讀順序

1. [雲端交接](07-cloud-handoff.md)：目前進度、限制、明日可直接使用的提示。
2. [來源盤點](01-source-inventory.md)：搜尋範圍、來源版本與可信度。
3. [差異分析](02-gap-analysis.md)：哪些可沿用、哪些只是畫面或規劃。
4. [產品規格](03-product-spec.md)：功能、角色、頁面與範圍。
5. [資料與流程](04-domain-and-workflows.md)：欄位、關聯、狀態與交易。
6. [架構與 API](05-architecture-and-api.md)：前後端分離方式與契約草案。
7. [決策與驗收](06-decisions-and-acceptance.md)：待確認清單與驗收情境。
8. [來源指紋](sources-manifest.json)：已選取來源檔案的 SHA-256，供日後辨識版本。

## 狀態定義

- **已確認**：使用者明確要求；來源為本次對話。
- **觀察**：靜態閱讀檔案可證實，未代表建置或執行成功。
- **建議**：供規格討論的設計，不是已核准需求。
- **待確認**：會影響資料模型、成本或交付範圍，需使用者決定。

已確認：參考 xk-truck-platform 的業務，依 codex-xk-rotaract 方式前後端分離；先確認規格再實作；搜尋本機相關專案；文件存於本 repo 的 docs 並推送 GitHub。

未執行：啟動舊系統、連接舊資料庫、驗證舊測試、移轉正式資料、複製商業模板與舊專案原始碼。文件只整理結構與業務，不收錄密碼、Token、連線設定或客戶實際資料。

## L1–L4 接手更新

本輪已依管理中心規則展開規格決策工作，請先閱讀 [執行與決策入口](LOGISTICS_EXECUTION.md)。四份細化提案補充既有 01–07 文件；已明確確認的範圍見決策紀錄，其餘提案維持待確認。新版程式仍排在關聯規格、來源與技術決策後。

- [L1 業務模型](L1_BUSINESS_MODEL.md)
- [L2 第一版與驗收](L2_MVP_AND_ACCEPTANCE.md)
- [L3 新舊接續與技術](L3_LEGACY_AND_TECHNOLOGY.md)
- [L4 維運與費用](L4_OPERATIONS_AND_COST.md)
