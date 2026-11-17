# 首片契約檢查紀錄

日期：2026-11-17（Asia/Taipei）；[Issue #4](https://github.com/xk2022/codex-xk-logistic/issues/4)。來源基準：Logistics main afc032b49ce8ea579abdcd1d04dd3c37833f6d08（PR #8）。本輪交付是採用紀錄、資料模型與文件契約，沒有產品程式或已部署服務。

## 重現方式

使用既有 Python 3、PyYAML 6.0.3、jsonschema 4.26.0；未安裝新套件，未新增產品相依或變更產品建置。準備官方 [OAI schema.yaml 固定版本](https://github.com/OAI/OpenAPI-Specification/blob/3.1.1/schemas/v3.1/schema.yaml)（blob bd1925ca9c12a700b2b5fb646624c26ec5bde355），保存為本機檔案後於repo根目錄執行：

```bash
python docs/api/VALIDATE_CONTRACT.py --oas-schema /path/to/openapi-3.1-schema.yaml
```

schema的 `$id` 為 `https://spec.openapis.org/oas/3.1/schema/2022-10-07`。它驗證OpenAPI文件結構，官方說明不涵蓋components schema驗證；因此另用JSON Schema Draft2020-12檢查31份components與合成資料。此處不是宣稱執行完整第三方OpenAPI validator，也不是產品Contract Test。

預裝jsonschema沒有可選date-time驗證套件；檢查程式明確補上本契約含offset／有效日曆的檢查，未讓未知format靜默通過。日期時間profile接受RFC3339含offset且秒數00～59、小數秒最多6位、offset小時00～23／分鐘00～59，不接受閏秒字面；OpenAPI亦寫入此界線。

## 檢查範圍

| 檢查 | 結果／限制 |
|---|---|
| OpenAPI 3.1文件結構、內部$ref解析、31份schema合法性 | 由上述指令執行；$ref不依賴遠端解析。 |
| 3個path／5項操作的operationId、Session、POST／PUT的CSRF與重送header | 靜態一致性；沒有實際驗證Session／CSRF攔截。 |
| 16組schema正例、25組schema反例 | 預期接受／拒絕；含最小草稿、三類多段請求與完整回應、清單、欄位完整性、版本錯誤、偽造欄位、日期時區、數值、不可免除旗標。 |
| 11組輸入圖案例 | 靜態檢查3組合法圖、8組重複ref／序號、失聯、自指、有環或逆向時間；沒有執行Service或DB守衛。 |
| 完整讀回示例的ref／UUID／同單／前置映射 | 只核對合成檔案內一致性，非HTTP讀回證據。 |
| 40筆欄位／CSV、Markdown連結與圍欄 | 分列accepted_scope／pending_scope，不將後續必填時點一併核准。 |
| 8項服務情境 | 全部not_run：停用客戶、交易回滾、舊版本、重播次序、key競爭、授權、無派工副作用與客戶快照。 |

檢查指令輸出提供實際計數；結果只支持文件形狀、示例與參照一致性。實際業務完整性運算、客戶可引用性、並發鎖／版本、冪等副作用、DB約束、查詢分頁與授權仍需產品實作後驗證。不能把25組反例或8項未跑情境宣稱為已通過產品測試。

## 獨立審查與遠端證據

依repo規則另由唯讀驗收Agent檢查採用界線、跨文件一致性、資料／API映射、重送順序及未決政策；主AI整合必要修正後再次檢查。審查曾發現offset分鐘未限59及小數秒超過PostgreSQL微秒精度，已限縮schema／checker、補6個反例及1個微秒正例，並澄清新寫入／成功重播流程。主AI另驗證regex尾端換行漏洞，補ref／十進位字串的排除字元約束與2個反例。實際複查結果、Commit／PR、合併後main／tree及GitHub檢查狀態由 [Issue #4](https://github.com/xk2022/codex-xk-logistic/issues/4) 記錄，以免本文件自引用尚未產生的SHA。

本輪未執行Maven／前端build、DB／Migration、真實HTTP、登入／授權／CSRF／並發、手機、照片、搬遷、部署或還原。沒有設定自動監看或行事曆；原G1～G5開工與上線門檻保留。
