# 2026-10-16 雲端接續交接

## 目前狀態

本 repo 是 codex-xk-logistic。已完成 GitHub 兩個指定來源與本機 truck／logistic 專案靜態盤點，並將統整文件放在 docs。尚未建立 frontend、backend、資料庫、OpenAPI 正式契約或部署服務。使用者要求先確認規格再實作，這個限制持續有效。

重要補充：本機找到的 React 前端包含進出口、貨櫃、獨立搬運任務、CRM 與 PORT 型別；資料複雜度超過原先「一單一車」建議。欄位及差異已保存在 02、04 文件，雲端不必先取得本機檔案即可討論，但若要重用舊介面或逐行分析仍需另取得相應原始碼。本次沒有上傳舊前端、商業模板、資料庫或任何環境設定。

## 雲端開始方式

1. 將工作環境指向 `https://github.com/xk2022/codex-xk-logistic` 的 main，先拉取最新文件。
2. 依 docs/README.md 閱讀規格，從 06 決策清單收斂 D01～D10。
3. 有使用者新回覆就更新確認紀錄；其餘維持草案，不自動套用建議。
4. 規格核准後才建立正式資料模型與 OpenAPI，再切前後端工作。

若雲端需要重新查原始碼，固定來源：

```sh
git clone https://github.com/xk2022/xk-truck-platform.git /tmp/xk-truck-reference
git -C /tmp/xk-truck-reference checkout 9a967bfc1b56fdccac6376fd08b7a6083582c876
git clone https://github.com/xk2022/codex-xk-rotaract.git /tmp/xk-rotaract-reference
git -C /tmp/xk-rotaract-reference checkout a4504de8add16941dae43fee2a2edc5ed260bafc
```

上述僅為來源查閱命令；網路與私有 repo 權限依雲端設定，不將存取憑證寫進 repo。不可假定目前 main 仍與分析版本相同。

## 明日可直接貼上的提示

> 請先閱讀這個 repo 的 docs/README.md、07-cloud-handoff.md 及其餘規格文件。這是物流平台的規格確認階段，尚未授權開始實作。請沿用既有分析，優先與我確認 06 文件 D01～D10，尤其一單多櫃／多段任務、進出口欄位、撤改派與資源釋放。以本機前端摘要補齊業務，以 xk-truck-platform 固定版本為領域參考，以 codex-xk-rotaract 固定版本為前後端分離方式參考。確認後先更新規格與決策紀錄，再依我授權進入實作。不要把 Mock、註解 API 或文件規劃當成已完成能力。

## 尚需補充的業務例子

請各給一筆典型進口、出口、國內運輸案例：幾個櫃、幾段路線、是否換車／換司機／拉板、何時可安排下一單、誰確認完工。這些例子比單看舊欄位更能決定正確的資料模型。

## 驗證限制

本次未執行舊系統／測試／資料庫，因此沒有「可直接上線」結論。選取來源的指紋只供追溯，不是完整原始碼備份。L7 的 213 檔相同比對只涵蓋 Java／Markdown／XML；詳見來源盤點。
