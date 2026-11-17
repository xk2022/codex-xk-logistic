# 首片隔離測試啟動包 v0.1

日期：2026-11-17（Asia/Taipei）。[Issue #4](https://github.com/xk2022/codex-xk-logistic/issues/4)。狀態：Proposed；本頁START-P01～P04及DEV-P01均尚未採用或執行。ACC-P01／P02的採用另見[ADR-0008](adr/ADR-0008.md)，不能據此推定本包已核准。

本包要形成一個可驗收的首片：隔離環境建立空DB與測試帳號，登入後依已採用角色完成訂單草稿建立／修改／重讀。P01～P03、M01與角色範圍已有決策；本頁補環境與登入配套，讓下一次實作有明確輸入。正式部署／主機／照片與完整MVP交付仍另按既有切片辦理。

## DEV-P01：GitHub Actions隔離測試（待確認）

建議使用本repo的標準GitHub-hosted Ubuntu 24.04 runner、Java 21及PostgreSQL 17 service container；每次job從新庫開始，以合成資料驗證Flyway、真正DB交易與HTTP。服務只存在該job，不連使用者NAS／正式DB或匯入舊資料。來源與版本於實作時固定；不是沿用範例的postgres不鎖版標籤。

已唯讀查核：2026-11-17本repo visibility=public。GitHub官方說明公開repo的標準hosted runner運算免費；這不表示Actions設定、artifact／cache額度或未來私有庫計費已查證。本包不使用larger／self-hosted runner、cache或artifact上傳，不建立付費資源。若repo改私有、服務被停用或條件不符，先回報環境阻礙，不能改用需付費平台。

擬定workflow為pull_request與手動觸發、contents:read、Ubuntu標準runner、第三方Actions固定完整commit、每job最長30分鐘、無正式Secrets、無部署步驟。fork PR不使用pull_request_target或受信任Secrets；只執行隔離合成測試。DB使用僅該次job有效的測試憑證；測試報告在job log提供摘要，不輸出密碼、Session、CSRF、reset token或完整認證payload。

目前只有環境方案；沒有建立或啟動workflow／service container，也沒有驗證Actions可執行。Maven Wrapper與前端lockfile待實作時依官方來源建立，不能把本回合主機PATH沒有mvn／docker當成使用者設備缺少工具。

## START-P01：首次管理員及測試帳號（待確認）

首次管理員由具主機操作權的真人執行離線初始化命令，僅在帳號表全空時允許；同交易／鎖保護，兩個初始化最多一個成功。有任一帳號即拒絕，不提供公開bootstrap HTTP入口。帳號名稱由操作者輸入，密碼以隱藏輸入取得，不放command arguments、Git、環境範例或log；本輪未建立帳號。

隔離自動測試可由test-only fixture建立ADMIN／DISPATCHER／DRIVER各一帳號與合成客戶。fixture只能在指定的隔離測試DB／profile執行，不能因一般環境變數誤設就在正常啟動建立登入後門；生產build不提供測試seed入口。測試用隨機憑證只在process內使用，不回寫成固定正式密碼。

## START-P02：帳號復原（待確認）

首片先採人工受控復原：既有管理員，或管理員全數失去登入能力時具主機操作權且經責任人核實的真人，以離線命令指定帳號並隱藏輸入臨時密碼。命令記錄操作者識別、原因與目標；不保存／列印明文密碼，交付方式由真人處理，AI不發信或訊息。未知操作者／原因不執行，不能用匿名網頁重設。

復原交易增加帳號認證版本、撤銷既有Session，設mustChangePassword；臨時密碼最長15分鐘有效，首次登入僅可變更本人密碼、讀取必要本人狀態／CSRF或登出，不能操作訂單。改密成功即作廢臨時密碼並要求重新登入；逾期只能重新受控復原。正常改密也撤銷其他Session。人工復原權限／稽核流程在正式上線前仍需真人主責，不由AI擔任。

## START-P03：Session與角色生效（待確認）

單一帳號在首片先只啟用一個業務角色；同一真人若兼任角色，先使用各自具名帳號，不自動合併ADMIN與DRIVER權限。未來多角色切換另定，首片遇到多個業務角色的帳號不擅自做union或deny-overrides，拒絕登入並回報設定需處理。

Session閒置30分鐘或登入起8小時到期；不提供remember-me。每帳號最多3個並存Session，超過時撤銷最舊Session。登入成功換Session ID，登入／登出後更新CSRF；登出、停用、角色異動、復原及改密使後續請求不能沿用舊認證版本。已進行中的寫入交易須在提交前核對帳號／角色版本，與停用操作協調鎖順序。

同源HTTPS的Session Cookie使用Secure、HttpOnly、SameSite=Lax及Path=/，前端不讀Session Cookie；CSRF由獨立取得流程提供，寫入必驗。隔離HTTP整合測試可用test-only非Secure Cookie以驗伺服器，不能據此宣稱HTTPS／瀏覽器Secure Cookie已驗收；有UI端到端驗收時須另提供同源測試TLS。啟動時若非隔離test卻未符合HTTPS／Cookie必要設定則拒絕服務，不靜默降級。

## START-P04：密碼規則與儲存（待確認）

建議一般及臨時密碼為15～128個Unicode code point，允許空格／Unicode，使用NFC一致化後計數與雜湊，不自動trim或截斷，不強制大小寫符號組合或定期更換。初始化、改密與復原均檢查不可用常見／已知外洩密碼清單；清單來源／授權／固定版本在實作時查證，未查證前不能宣稱此項通過。臨時密碼仍須符合長度規則。

建議使用Spring Security內建PBKDF2-HMAC-SHA-256、600,000 iterations、每筆隨機16-byte salt與256-bit輸出，保存可辨識參數版本的格式；禁止plaintext／noop或無salt快速SHA。選PBKDF2是為使用既有Java／Spring能力，不新增密碼演算法套件；沒有聲稱符合任何認證。實作前用測試硬體核對效能與encoder參數／Unicode一致性，不能為讓CI變快而降正式設定。

登入對同帳號15分鐘內最多10次失敗，達限暫停登入15分鐘；不存在帳號採相同外部錯誤及有界限流處理，不能暴露帳號是否存在。時間與計數以伺服器處理，成功／復原如何重設計數需留稽核；初版單instance，不引入Redis。多instance限流與防濫用是正式部署前需另驗的配置，不能把單機測試當成分散式保證。

## 擬定實作清單與驗收

本包採用後，首片工作限制為已採用的建單／角色範圍與上述配套，先完成可從空環境重現的登入／草稿保存／查詢。依[既有G1～G5](LOGISTICS_EXECUTION.md)核對與本片相關的輸入，未確認的派工、照片、計費與正式部署政策繼續留在對應切片，不能用本包核准推定它們已通過。

依賴沿已採用Java21／Boot4.1.x、Security、JPA、PostgreSQL17與Flyway；前端React／TypeScript／Vite。實作時列出BOM／精確lockfile與測試相依清單，使用官方兼容組合；本頁不允許任意加入其他框架、付費SDK或跨repo共用服務，也沒有解析／安裝新產品相依。

| 交付 | 必要驗收（全部未執行） |
|---|---|
| 環境／初始化 | 空庫Flyway可重建；重跑無重複seed；並發bootstrap只有一次成功；非測試DB拒絕test fixture |
| 登入與復原 | 無預設帳密、密碼規則／雜湊、登入限流、到期／換密／復原／CSRF／Session撤銷與多角色拒絕均可重現 |
| 授權 | 五operation×三單角色的15個契約對照以真實HTTP執行；司機整單拒絕、範圍外404，計數與重播不越權 |
| 訂單 | 既有FS-T01～T08、ORD-A01～A16中首片相關項，以PostgreSQL與真實HTTP驗版本、重送、回滾與關聯 |
| 介面 | 最小草稿及三類合成案例可重新開啟，未登入／API失敗不顯示假成功；只讀完整性不受理或占用人車 |
| 交付證據 | 記錄commit、相依版本、CI實際狀態、指令與失敗原因；產品驗收未跑即標not_run，不用52個靜態案例代替 |

正式NAS／主機／網域、照片供應商、資料保存、真人維運責任與上線日期仍待確認；本包不是正式部署授權。若相關開工輸入未齊，回報具體阻礙，不擅自降低既有門檻。

## 官方依據與提案性質

本包的30分鐘／8小時／3Session／10次與15分鐘等是供使用者核定的產品方案，不是官方強制值。參考來源：[GitHub PostgreSQL service](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)、[GitHub runner與費用](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)、[Spring Session](https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html)、[Spring PasswordEncoder](https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html)、[NIST密碼](https://pages.nist.gov/800-63-4/sp800-63b.html)、[OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)。查閱日2026-11-17；本輪只完成可審閱方案。
