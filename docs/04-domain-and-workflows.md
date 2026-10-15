# 資料模型與流程草案

## 領域邊界與關聯

- UPMS：帳號、角色、權限與關聯。
- ADM：字典分類、項目、參數。
- CRM：客戶及聯絡人。
- OrderCore：訂單身份、編號與高階生命週期。
- TOM：運輸訂單、貨櫃／貨物項目與運輸任務（後兩者範圍待確認）。
- FMS：司機、車輛、派工與資源占用。
- Assets／Audit：簽收資產與操作歷程。

OrderCore 與 TomOrder 共用 orderUuid。若採多段模式，TransportTask 表達「搬什麼、從哪到哪」，Dispatch 表達「誰、用什麼資源、何時執行」，避免 TOM 任務與 FMS 派工各自變成兩個互相矛盾的執行狀態來源。

候選基數：Customer 1:N Order；Order 1:N ContainerItem；Order 1:N TransportTask；Task N:1 ContainerItem（可空）；Task 1:N DispatchHistory，最多一個有效 Dispatch。獨立空車／板車任務可不關聯訂單，由 D03 決定。此模型並未建立資料表。

## 基礎欄位

| 資料 | 必要或建議欄位 |
|---|---|
| 客戶 | UUID、名稱、公司代碼、統編、狀態、電話、Email、地址；多聯絡人是否納第一版待定 |
| 訂單 | UUID、orderNo、IMPORT／EXPORT／LOCAL、customerUuid、客戶名稱快照、提貨／送貨地址、預定時間、客戶參考號、remark |
| 車輛 | UUID、唯一車牌、車型、品牌型號、capacityTon、狀態 |
| 司機 | UUID、關聯 accountId、姓名、電話、駕照類型、在職狀態、onDuty |
| 運輸任務 | UUID、taskNo、標的類型、標的識別、起終點、預定開始時間、orderId／containerItemId（可空）、remark |
| 派工 | UUID、taskId（或簡化版 orderId）、driverId、vehicleId、選配 trailerId、狀態、指派／出發／簽收／完成時間 |
| 簽收 | 所屬派工、資產 ID、上傳者、時間、備註；檔案規格及保存期限待定 |
| 歷程 | UUID、對象與 ID、動作、前後狀態、操作者、時間、原因、requestId |

共用：createdAt／updatedAt、建立與異動者、version。新 ID 採 UUID 字串；單號與 UUID 分開，單號唯一並由後端產生。金額／重量用 decimal，明確單位，不能用字串或浮點數混算。電話唯一與共用公司電話的例外待確認。

## 本機獨有進出口欄位摘要

下列為 L8 型別的候選需求摘要，並非核准必填欄位，不是舊碼 API 契約。

| 類別 | 候選欄位 |
|---|---|
| 船務共用 | 船公司 shippingCompany、船名航次 vesselVoyage、船期 shipDate、裝貨港 pol、卸貨港 pod、ETD／ETA |
| 貨櫃／貨物 | containerNo（舊名另有 containerNumber）、containerType、件數 packageQty、毛重 grossWeight、體積 cbm |
| 進口 | 換單地點 deliveryOrderLocation、提單 blNo、進口報單 importDeclNo、海關放行時間 customsReleaseTime、倉庫 warehouse、到貨通知 arrivalNotice |
| 進口作業 | 貨櫃場 containerYard、最後提櫃日 lastPickupDate、送貨地點／日期／時間、還櫃場 returnYard、還櫃日期／時間 |
| 出口 | 通關日 clearanceDate、提櫃碼 pickupCode、提櫃場 pickupYard、交櫃場 deliveryYard、裝貨地 loadingLocation、裝貨日期／時間 |
| 櫃型 | L8 候選：20GP、40GP、40HQ、45HQ、40RH、OTHER |
| 任務標的 | CONTAINER、TRAILER、EMPTY_MOVE、VEHICLE、OTHER |

一張訂單內是否可有不同櫃型、船期、作業地址與多個交付點，會決定欄位放在訂單、櫃項還是任務；需 D03／D04 後才定稿。櫃號能在不同航次重複出現，不宜直接設整個歷史資料庫永久唯一。可先以訂單內櫃項唯一為候選，必要時支援未知櫃號稍後補登。

## 狀態與規則

| 層級 | 建議代碼 | 說明 |
|---|---|---|
| OrderCore | OPEN／CANCELLED／CLOSED | 取消與結案為終態 |
| TOM 安排 | NEW → ACCEPTED → ASSIGNED | 只代表安排，不代表已出發或交貨 |
| FMS 執行 | ASSIGNED → IN_PROGRESS → SIGNED → COMPLETED | CREATED 是否保留待確認；直接派工可從 ASSIGNED 起始 |
| 車輛 | AVAILABLE／IN_USE／MAINTENANCE／RETIRED | 統一原文件 BUSY／IN_USE 落差 |
| 司機 | ACTIVE／SUSPENDED／INACTIVE，加 onDuty | 上線不等於未被占用 |

建議：建立訂單同交易建立 Core 與 TOM；受理須 OPEN＋NEW；派工須 OPEN＋ACCEPTED（多任務模式另算整體安排狀態）；車可用、司機 ACTIVE＋onDuty 且無有效占用。出發只允許 ASSIGNED，簽收只允許 IN_PROGRESS，後台完成只允許 SIGNED。若簽收照片列必填，未有通過驗證的資產不可簽收。

取消：原 TOM 規則禁止 ASSIGNED 後取消，FMS 卻直接允許 cancel，存在衝突。新版尚未核定例外。候選是出發前可撤派／改派，需原因；出發後不直接取消，走異常處理。取消訂單與取消單一派工不同，不得相互隱含。

多任務結案：建議所有必要任務 COMPLETED、無未處理異常，才可 CLOSED。單一派工完成不能直接關閉仍有其他任務的訂單。撤派後 TOM 回 ACCEPTED 或維持最後安排狀態需 D05 決定，必須留史。

## 交易與並發

- 派工交易需共同保護訂單／任務、資源、有效指派與歷程；單靠前端篩選不足。
- 同一車輛／司機的有效占用採資料庫唯一約束搭配鎖定或等效機制，固定鎖定順序。
- 編輯採 version，衝突回 409；不得覆寫他人最新修改。
- 建立、派工、簽收與完工等重送敏感操作定義 Idempotency-Key；相同 key 不重做副作用，不同內容回 409。
- 完成後釋放資源的時間（簽收或後台完成）屬 D09，避免等待後台確認期間錯誤阻擋下一單。
- 儲存時間用可表示 UTC 的型別，API ISO 8601 含時區；日期型欄位不可當 UTC 午夜任意轉換。
