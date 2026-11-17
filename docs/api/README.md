# 首片訂單 API 契約 v0.1

日期：2026-11-17（Asia/Taipei）。[Issue #4](https://github.com/xk2022/codex-xk-logistic/issues/4)。

[openapi.yaml](openapi.yaml) 是 OpenAPI 3.1.0 工程契約，依已採用的 [ORD-P01～P03](../FIRST_SLICE_ORDER_SPEC.md) 與 [資料模型](../FIRST_SLICE_DATA_MODEL.md) 建立。尚無 API 程式、可連線服務、DB 或執行驗收；文件版本 0.1.0 不是產品發版。詳細授權等未決政策不因 schema 存在變成已核准。

## 操作範圍

前綴 `/api/v1`；JSON；同源 Session。下表 3 個 path、5 個 operation。

| 方法／路徑 | 正常回應 | 用途 |
|---|---|---|
| POST /orders | 201，OrderEnvelope、Location、Idempotency-Replayed | type＋有效 customerId 即可建 OPEN＋DRAFT、version=0；可含多項目／多任務。 |
| GET /orders | 200，OrderPageEnvelope | 依授權範圍查清單；page=0、size=20／最大100，排序白名單，最後以 id 固定順序。type／customerId 可選。 |
| GET /orders/{orderId} | 200，OrderEnvelope | 重讀訂單及全部所屬項目／任務／前置關係；空值明確 null、集合是陣列。 |
| PUT /orders/{orderId} | 200，OrderEnvelope、Idempotency-Replayed | expectedVersion＋完整 draft；只編輯未執行的 OPEN＋DRAFT，替換規則見下節。 |
| GET /orders/{orderId}/acceptance-check | 200，AcceptanceCheckEnvelope | 只檢查已採用的建單／受理欄位完整性；不改狀態，不授予受理或派工。 |

列表／明細保留 OPEN／CANCELLED／CLOSED 及 DRAFT／ACCEPTED 的讀值供未來銜接；本片只建立 OPEN＋DRAFT。舊概念稿的 NEW 對應本契約 DRAFT（尚無已部署舊版新 API 相容承諾）；不寫任意 status，也不提供受理、取消、派工或結案操作。

## 請求、參照與完整替換

CreateDraftRequest 只必填 type 與 customerId。提供 items 時每筆必有 clientRef，提供 tasks 時每筆必有 clientRef／itemRef；predecessorRefs 使用同單 task.clientRef。引用須在這次完整 draft 內存在，不能自我依賴、有環或跨單；陣列順序不代表執行依賴。

clientRef 是同單穩定的草稿參照，1～64 字元，首字英數，其餘英數／`_`／`-`，項目與任務各自唯一。伺服器為新 ref 產生 UUID，既有 ref 保持 UUID；回應同時帶 id、itemId、predecessorTaskIds 與 ref。所有輸入物件拒絕未知欄位；不能送 id／orderId／單號／狀態／客戶名稱快照／操作者來覆寫系統欄位。

PUT 不做 PATCH：draft 的省略可選純量變 null，省略集合變空；shipping／siteContact 若給空物件，讀回為各欄 null 的物件，與整組 null 有別。省略的舊草稿子項移除並保留不可變版本快照；若已有執行／派工／受保護關聯則整次 409。修改 clientRef 相當於移除舊子項並建立新子項，前端應沿用讀回 ref。成功新 PUT 版本加一，重播不加。

同 customerId 編輯保持歷史 customerName；草稿明確換成另一個有效客戶時，伺服器取得新名稱快照。CRM 名稱需符合本版 200 字傳輸範圍；本次不匯入舊資料；新版輸入仍不可無聲截斷，未來另有匯入需求時重新核對範圍與格式。精確字典尚未核定，taskKind／containerType 為非空文字，不能把示意名稱當成已核准 enum。

日期時間用RFC3339含offset、秒數00～59、小數秒最多6位（對齊timestamptz(6)）；offset小時00～23／分鐘00～59，不接受閏秒字面，超精度拒絕而非無聲捨入；date 不轉 UTC 午夜。重量／體積是非負十進位字串，最多32字元；null 未知、"0" 已知零，不用假值補齊；讀回可正規化尾零。數量／序號為正整數，上限2147483647；version 上限9007199254740991。名稱200字、地址1000字、備註4000字、電話50字是工程傳輸界線，實際業務例外仍待確認。

## 受理欄位檢核

檢核對讀取到的同一版聚合執行並回傳 version。checkedRules 固定三個 ORD-P ID；confirmedRulesOutcome 只代表這三項已確認規則是否齊全。

| 規則 | 本版完整性檢查 |
|---|---|
| P01 | type 合法、customerId 仍存在且可新增引用；已停用客戶仍可讀歷史，但檢核列出缺口，不視為可受理。 |
| P02 | 至少一項目；各項目 sequence／itemKind 齊全且序號不重複；CONTAINER 有 containerType；LOCAL＋CARGO 有 packageQty；每項目至少一段 requiredTask=true 的任務；每段 taskKind 與起終點名稱／地址齊全，關聯存在且無環。 |
| P03 | IMPORT／EXPORT 有 shippingCompany／vesselVoyage／pol／pod；IMPORT 有 eta／blNo，且 CONTAINER 項有 lastPickupDate；EXPORT 有 etd，且 CONTAINER 項有 deliveryCutoffAt。LOCAL 不要求船務；CARGO 不要求櫃號／櫃型。 |

每一缺口回 path、fieldId（對應40筆欄位；集合缺口可用 ORD-P02）、ruleId、message；path 使用 `/items/0/containerType` 這類 JSON Pointer。COMPLETE 時 missingFields 必空，INCOMPLETE 時至少一筆缺口。

pendingPolicyIds 保留相關未決政策，例如 D04_CONTACT、D04_CONTAINER_FORMAT、D04_WEIGHT、D04_DICTIONARY、D04_DEADLINE_EXCEPTION、D05_REQUIRED_TASK_WAIVER；不把未知當已通過。requiredTask 可 true／null，不開放 false 免除；具體義務判斷未決時保留 pending。operationalAcceptance 永遠 NOT_GRANTED；即使 confirmedRulesOutcome=COMPLETE，也沒有受理或占用人車的副作用。

## 認證與重送

沿已採用 Session＋CSRF，cookie 以 JSESSIONID 表示；POST／PUT 必有 X-CSRF-TOKEN 及 Idempotency-Key。這是契約表示，不是已設定 Cookie／登入／復原政策。登入與更新 token 端點不在本片；D02 逐動作與資料範圍核定前不得以「已登入」取代授權後暴露這些操作。列表、明細、計數與重播結果均要查同一授權範圍。

寫入處理次序：

1. 驗證目前 Session／帳號、CSRF、操作及資料權限；解析 JSON，重複 property key／未知欄位／格式非法回400。
2. 用伺服器公司範圍＋actorId＋HTTP method＋canonical path＋key 取得重送紀錄。canonical path 是無 query 的實際 API 路徑（UUID 正規化）；key 區分大小寫。body 以解析後 JSON 的 property依Unicode code point遞迴排序、UTF-8緊湊JSON及SHA-256計算hash（整數以無前置零的十進位輸出），保留陣列順序、字串、null與欄位省略差異；expectedVersion 也在 hash 內。
3. 相同 key／相同 body 已成功：在確認目前仍有權存取該訂單後，重播原 status／業務 data／Location，Idempotency-Replayed=true，本次產生新的 traceId；不先拿原 expectedVersion 與現版比對，不增加版本／歷程。重播可能是舊版快照，需要最新資料另 GET。
4. 相同 key 不同 body 回409 IDEMPOTENCY_KEY_REUSED；尚在處理回409 IDEMPOTENCY_IN_PROGRESS，不回假成功。首送通過後才檢查客戶、前態、expectedVersion 與完整輸入圖；交易完成才與業務資料一起保存成功重送紀錄。
5. 新成功回 Idempotency-Replayed=false。交易失敗不留成功紀錄，可同 key 重試；業務拒絕／400等不快取為成功。key 保存與清理期限待 D10，未核定前不自動過期或復用；不代表已核准永久保存。

若同 key 以不同 CSRF／不同 Session 重試，只要仍為同一授權 actor 且目前檢查通過才可重播。停權、登出、失去權限後不能因舊 key 取得資料；原結果不等於永久存取權。

## 回應與錯誤

成功使用 `{code:"OK",message,data,traceId}`。錯誤使用相同四欄加 fieldErrors；data 通常 null，版本衝突可含 actualVersion。traceId 是本次請求追查值，不採舊草案 requestId；實作不得傳回 Entity、內部堆疊或認證敏感欄位。

| HTTP | 本片 code／情境 |
|---|---|
| 400 | VALIDATION_ERROR：缺 type/customerId、未知／伺服器欄位、格式、重複 ref、序號、失聯／自指／有環參照或逆向時間；INVALID_CUSTOMER：不存在／停用而新增引用，均可帶欄位定位。 |
| 401 | UNAUTHENTICATED：未登入／Session失效。 |
| 403 | FORBIDDEN／CSRF_INVALID：操作無權限或已登入的寫入 CSRF 缺失／錯誤。 |
| 404 | ORDER_NOT_FOUND：授權範圍查無訂單，不能洩漏範圍外訂單是否存在。 |
| 409 | VERSION_CONFLICT／ORDER_NOT_EDITABLE／PROTECTED_RELATION／IDEMPOTENCY_KEY_REUSED／IDEMPOTENCY_IN_PROGRESS。 |
| 500 | INTERNAL_ERROR：未預期失敗，交易回滾；不顯示內部細節。 |

## 驗證與下一步

[契約合成資料](ORDER_DRAFT_CONTRACT_EXAMPLES.json) 明確區分 schema 正反例、圖結構正反例與未執行服務情境；不是 DB seed 或實際 HTTP 結果。[檢查紀錄](CONTRACT_CHECKS.md) 記範圍及限制。舊 [概念案例](../FIRST_SLICE_ORDER_EXAMPLES.json) 保留作欄位追溯，不當成本契約的請求／完整回應。

D07本次已採[M01全新啟用](../adr/ADR-0007.md)。後續需完成D02／D04字典與例外、D10開發與測試環境／保存政策及既有開工門檻，才進行程式、Migration、DB／HTTP／交易與授權驗收；手機／照片／部署仍按各自切片。未建立日曆事件或指定上線日。

技術依據：[OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0)、[Cookie Authentication](https://swagger.io/docs/specification/v3_0/authentication/cookie-authentication/)、[Spring Security CSRF](https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html)。
