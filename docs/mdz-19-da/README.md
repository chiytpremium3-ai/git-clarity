# 小米家庭影院 MDZ-19-DA：Android TV 改裝可行性評估

> 目標機型：中國版小米家庭影院 **MDZ-19-DA**（使用者回報：device `missionimpossible`、platform `613`、Amlogic T966、Android 6.0.1）
> 研究日期：2026-10-26
> 最高原則：**優先保住原廠 AirPlay 與環繞音效（低音炮＋兩顆無線後環繞）**

本文的判讀標記：

| 標記 | 意義 |
|---|---|
| ✅ 已證實 | 有原始來源直接寫明（來源編號見文末 §12） |
| 🟡 合理推測 | 有同平台／同系統的間接證據，但沒有 MDZ-19-DA 本機的證據 |
| ❓ 尚未確認 | 找不到公開資料，要用本機盤點才能確認 |

> ⚠️ 本文**不會**把 MDZ-19-AA（小米盒子 3S）、MDZ-18-DA（小米電視主機）或小米電視的成功案例當成 MDZ-19-DA 的成功案例。這些案例只用來說明「為什麼它們可以、MDZ-19-DA 為什麼不行或還不能」。

---

## 0. 一頁結論

➤ **完整刷成 Android TV：目前不可行，也不建議嘗試。**
　➤ ❓ 在 ZNDS、4PDA（搜尋摘要）、GitHub、Mobile01、恩山、數碼之家都**找不到任何 MDZ-19-DA 刷 Android TV、TWRP 或 Root 的成功案例**。4PDA 上 MDZ-19-DA 的使用者被回覆「19 型沒有英文韌體，公開韌體幾乎找不到」[S7]。
　➤ ✅ MDZ-19-AA 之所以能刷 Android TV，是因為它可以借用同硬體 Mi Box 3 的國際版韌體[S23][S30]。MDZ-19-DA 用的是電視級 SoC T966，**找不到任何 T966 機種的 Android TV 官方韌體可以借用**。
　➤ 🟡 無線後環繞（插在主機 USB 的 5G 發射器[S5]）、Soundbar 功放與調音、AirPlay（米聯）都在小米原廠 system 層，換 ROM 幾乎一定會失去。

➤ **建議路線：混合式（保留原廠底層）。**
　➤ 不動 system、不 Root、不換 recovery，只透過 ADB 安裝 Android TV 風格桌面與 App。
　➤ AirPlay、Dolby/DTS、HDMI、低音炮、後環繞都還是原廠程式在跑，風險最低。
　➤ Root 或 TWRP 備份目前**沒有** MDZ-19-DA 專用映像，列為「有條件才做」的選項。

➤ **HDMI 可能是零風險的 Android TV 捷徑（詳見 §1.1）。**
　➤ ✅ 主機有 3 個 HDMI 2.0a，其中 1 個是 ARC；另有 S/PDIF 輸入（AV 埠）與輸出[S31]。
　➤ ✅ 評測說這台主機的介面「與小米分體電視的主機基本一致」[S31]；同系列的米 3 電視主機把 **HDMI IN 1 定義為 ARC**[S32]。
　➤ 🟡 如果另外兩個 HDMI 是輸入，就能把 Google TV／Android TV 裝置接進家庭影院，聲音直接走原廠 Dolby／DTS 與環繞，系統完全不用改。
　➤ ❓ 哪個埠是輸出、哪些是輸入、HDMI 輸入的音訊會不會送到後環繞，要看你的背板標示並實測。

➤ **CleanYourTV：主線版無法裝在 Android 6；社群的 Android 6 分支可以試，但只有一台小米電視測過。**
　➤ ✅ 主線 launcher 的 `minSdk 26`（Android 8.0）[S13][S14]。
　➤ ✅ 分支 `my-tv-signal-android6` 用 `-PlauncherMinSdk=23` 編譯，只在 MiTV4-ANSM0 測過[S17]。
　➤ ✅ 小米 Android 6 會在 framework 的 `MitvPhoneWindowManager` 攔截 HOME 鍵並交給 PatchWall[S18]。所以按 HOME 可能還是回到原廠桌面。

➤ **原廠韌體：本次無法從可驗證的來源取得。**（細節見 §6）
　➤ 已改為提供分析腳本：先從你自己的機器免 Root 拉出全部系統 APK 與 framework，再離線分析。

---

## 1. 型號身分確認：先把三台「長得像」的機器分開

| 項目 | **MDZ-19-DA 小米家庭影院** | MDZ-18-DA 小米電視主機 | MDZ-19-AA 小米盒子 3S |
|---|---|---|---|
| 產品定位 | Soundbar＋低音炮＋2 顆無線後環繞＋無線收發器 ✅[S1][S4] | 上一代 Soundbar（電視主機）✅[S1][S8] | 電視盒 ✅[S1] |
| SoC | Amlogic **T966**，4 核 A53 1.8GHz ✅[S2] | MStar 6A928（4PDA 規格欄）✅[S7] | Amlogic S905X ✅[S29] |
| 記憶體／儲存 | 2GB／8GB ✅[S2] | — | 2GB／8GB |
| 能接無線後環繞 | ✅ 可以 | ✅ **不行**（官方 FAQ 寫明）[S4] | 不適用 |
| 有無國際版雙胞胎 | ❓ 找不到 | ❓ | ✅ Mi Box 3（MDZ-16-AB）[S30] |
| Android TV 成功案例 | ❓ **無** | ❓ 無（只有 Root＋GApps 的說法）[S7] | ✅ 有[S23][S30] |

其他已證實的 MDZ-19-DA 規格：

➤ ✅ 2016-12-12 首賣，售價人民幣 1999 元[S5][S26]。
➤ ✅ 系統是 PatchWall，內建小米電視的影視內容[S4][S5]。
➤ ✅ 支援 Dolby Audio 與 DTS-HD「雙解碼」[S2][S4][S5]。
➤ ✅ 雙頻 Wi-Fi（802.11ac）與藍牙 4.1[S2]。
➤ ✅ 無線收發器插在主機背面的 USB 2.0 埠；後環繞走 5G 無線，有自動跳頻；低音炮用線材連接[S5]。
➤ ✅ 兩顆後環繞之間用 6 公尺線材互連，只需要一條電源線[S4]。訊號異常時可按後環繞背面的重置鍵[S5]。
➤ ✅ 低音炮背面有 AUX IN[S5]。
➤ ✅ 主機背板：HDMI 2.0a ×3（含 1 個 ARC）、USB 3.0 ×1、USB 2.0 ×1、乙太網路 ×1、AV（R/L/Video，兼 S/PDIF 輸入）×1、S/PDIF 輸出 ×1、Woofer ×1、類比訊號／DTMB ×1、DC IN ×1[S31]。
➤ ✅ 手機、平板、筆電可透過藍牙或 Wi-Fi 送音訊過來[S3][S5]。

關於 `missionimpossible`／`613`：

➤ ❓ 公開網路上只有一個 SEO 韌體站出現「Xiaomi mitv3s missionimpossible」[S9]。這個站的檔案只有幾 MB、日期矛盾、沒有雜湊值，**不可信也不要下載**。
➤ 🟡 字串本身暗示這台機器的 build 是掛在 mitv3s 世代的小米電視產品線底下，跟 MDZ-19-DA 同期（2016 年底）的小米電視 3s 相符。
➤ ✅ 同為 T966 的小米機種：小米電視 4 的 65 吋版[S24]（49／55 吋是 T968）。這是唯一已知同 SoC 的小米機種，但它是電視，不是 Soundbar。

### 1.1 HDMI 1 的特殊角色

➤ ✅ hdav 評測（2017-02-14）：3 個 HDMI 2.0a「含 1 個 ARC」，介面「與小米電視的主機基本一致」，但沒有標出哪個埠是 HDMI 1／2／3，也沒寫輸入或輸出[S31]。
➤ ✅ 同系列的米 3 電視主機在 2015 年底用軟體更新把 **HDMI IN 1 指定為 ARC**，設定路徑是「設定 → 圖像與聲音 → 聲音／輸出 → HDMI(ARC)」[S32]。
➤ ✅ CleanYourTV 的小米 Android 6 文件記錄：小米系統用 `com.xiaomi.mitv.tvplayer/.ExternalSourceActivity` 切換訊號源，`input` 參數 HDMI 1＝23、HDMI 2＝24、HDMI 3＝25、AV＝2[S16]。
➤ 🟡 分體電視主機是用專用線接面板，所以 3 個 HDMI 都是輸入。家庭影院要把畫面送到一般電視，必須有一個埠改當**輸出**。你記得「HDMI 1 比較特殊」，最可能的情況是：
　➤ HDMI 1＝**輸出到電視＋ARC**（電視自己的 App 聲音可以回傳到家庭影院），或
　➤ HDMI 1＝**ARC 輸入**（沿用米 3 主機的定義），另有一個埠是輸出。
➤ ❓ 兩種情況都還沒有原始資料證實，請直接看主機背板 HDMI 旁的印字（例如 `HDMI OUT (ARC)`、`HDMI IN 1`）。

**這對改裝方案的影響**

➤ 如果有可用的 HDMI 輸入：外接 Google TV／Android TV 裝置 → 家庭影院 HDMI IN → 家庭影院 HDMI OUT → 電視。Android TV 體驗來自外接裝置，家庭影院本身的系統、AirPlay、環繞一律不動（方案 D，見 §7）。
➤ 如果 HDMI 1 是輸出＋ARC：外接裝置也可以接在**電視**上，再靠 ARC 把聲音送回家庭影院。缺點是 ARC 只能傳壓縮的 Dolby Digital／DTS 或雙聲道 PCM，而且要看電視的 ARC 實作。
➤ ❓ 外接 HDMI 輸入的聲音會不會經過原廠上混送到兩顆後環繞，必須實測（§9 Phase 0 已加入測試項目）。

---

## 2. 原廠 AirPlay 音訊與螢幕鏡像：怎麼實作的

### 2.1 已證實的部分

➤ ✅ 小米 PatchWall 系統的 AirPlay／DLNA 接收端是 **`com.duokan.airkan.tvbox`**。第三方 APK 站的名稱是「Mi-Link (Airkan/DLNA/Airplay) Services」[S10]，中文對照表寫「米联投射服务」[S11]。
➤ ✅ 小米電視與電視主機的官方規格寫「內建米聯協議，相容 AirPlay、Miracast、WiDi、DLNA」[S2-b]。**但 MDZ-19-DA 官方頁的搜尋摘要只寫藍牙／Wi-Fi 投射，沒有出現 AirPlay 字樣**[S3]。所以「MDZ-19-DA 有 AirPlay」目前是你本機的實測，而不是官方規格。
➤ ✅ 同世代小米系統上，社群文件列出的投屏相關套件：

| 套件 | 用途（來源標示） | 出現的機種 |
|---|---|---|
| `com.duokan.airkan.tvbox` | 米聯投射（AirPlay／DLNA） | 多數 PatchWall 機種[S11][S16][S19] |
| `com.xiaomi.mitv.smartshare` | 無線投屏 | 多數機種[S11][S19] |
| `com.xiaomi.wfdsinkhelperservice` | 無線直連助手（Wi-Fi Display） | [S11] |
| `com.xiaomi.upnp` | 小米即插即用服務 | [S11][S19] |
| `com.xiaomi.dlnatvservice` | DLNA | MiTV3S-48（Android 4.4）[S19] |
| `com.xiaomi.miplay`、`com.mi.miplay.mitvupnpsink` | MiPlay／UPnP sink | MiTV4-ANSM0（Android 6.0.1）[S16] |
| `mitv.service` | 小米電視系統服務（遙控、投屏都靠它） | [S11][S16] |

➤ ✅ CleanYourTV 的 MiTV4-ANSM0（Android 6.0.1）文件把 `mitv.service`、`com.mi.miplay.mitvupnpsink`、`com.xiaomi.miplay`、`com.duokan.airkan.tvbox` 列為「必須保留：遙控與投屏」[S16]。
➤ ✅ MiTV3S-48（Android 4.4）文件記錄使用者在 2026-10-23 回報 AirPlay 與 Android 投屏恢復正常，相關套件是 smartshare、airkan、dlnatvservice、upnp[S19]。

### 2.2 合理推測（要在本機確認）

➤ 🟡 MDZ-19-DA 的 AirPlay 推送（音訊、照片、影片）很可能由 `com.duokan.airkan.tvbox` 提供，跟同期小米電視一樣。
➤ 🟡 依賴鏈大致如下：

```
iPhone ──mDNS(_airplay._tcp/_raop._tcp)──▶ com.duokan.airkan.tvbox（米聯）
                                             │ 綁定
                                             ▼
                                        mitv.service（小米電視系統服務）
                                             │ 影片走小米播放器，音訊走 AudioTrack
                                             ▼
                        Android MediaCodec / AudioFlinger（framework）
                                             ▼
                 Amlogic audio HAL（/system/lib/hw/audio.primary.*.so）
                     │                                   │
                     ▼                                   ▼
          Soundbar 功放＋低音炮輸出               USB 5G 發射器 ──▶ 兩顆後環繞
```

➤ 🟡 Dolby／DTS 解碼與環繞上混（upmix）應該在 audio HAL 或其載入的 vendor 函式庫裡，跟 AirPlay 是否「保留」直接綁在一起：**只要 system 不換，AirPlay 的聲音就會走原廠環繞路徑。**

### 2.3 尚未確認

➤ ❓ 螢幕鏡像（mirroring）是 airkan 自己做的，還是 `smartshare` 或乐播（Lebo）方案。知乎有回答主張小米的 AirPlay 其實是乐播[S25]，但沒有證據能套到 MDZ-19-DA。
➤ ❓ 原生函式庫名稱（例如 airplay／raop／fairplay 相關 `.so`）。
➤ ❓ 後環繞發射器是被當成 USB 音效卡（ALSA）還是私有協定，由哪個服務驅動。

**確認方法**（§9 的 Phase 1 會跑）：

➤ 執行 `scripts/mdz19da_inventory.sh`。看 `net/listen_ports_uid.txt` 哪個 uid 在監聽 7000／7100／47000 等埠，再從 `pkgs/dumpsys_*.txt` 的 `userId=` 對回套件名。
➤ 在同網段的電腦執行 `avahi-browse -rt _airplay._tcp` 或 `dns-sd -B _airplay._tcp`。TXT 記錄裡的 `srcvers`、`model`、`features` 可以看出是哪一套實作。
➤ 看 `audio/usb_devices.txt` 與 `audio/asound_cards.txt`，找出發射器的 USB VID／PID，以及系統有沒有把它當成音效卡。

---

## 3. ROM、TWRP、Root、Recovery、救磚：案例盤點

| 機型 | 案例內容 | 能不能套到 MDZ-19-DA |
|---|---|---|
| **MDZ-19-DA** | ❓ **找不到任何案例**。4PDA 上有車主詢問英文化，被回覆「19 型沒有英文韌體、公開韌體很少，建議去中文論壇找」[S7]。 | — |
| MDZ-18-DA | ✅ 4PDA 有韌體 1.2.11.988；USB 升級方式是「開機時按住機身 + 與 −」；Root 的說法是 KingRoot／360 Root，加上為 MDZ-18-AA 做的 GApps 包（相容性未證實）[S7]。 | ❌ 不同 SoC（MStar）。🟡 「按住機身 +／− 進 USB 升級」的按鍵組合**可能**相同，❓ 未確認。 |
| MDZ-19-AA | ✅ 用 Mi Box 3 國際版的 `xiaomi_update`＋`update.zip`，開機按住遙控器 Home＋Menu 強刷，升 Android TV 8 再 OTA 到 9[S23]；Kodi／Lowyat 社群也有轉國際版的回報[S30]。 | ❌ 原理是「同硬體借用韌體」，MDZ-19-DA 沒有可借的 Android TV 韌體。 |
| 小米電視 4A／4S／4X（Android 6.0.1，Amlogic） | ✅ `adb reboot update` 讓 Amlogic u-boot 從 USB 載入 TWRP（不寫入 recovery），再刷 Magisk 19.1。部分機種只會回到原廠 recovery，USB 隨身碟相容性差[S20]。 | 🟡 T966 的 u-boot 很可能也支援 `reboot update`，但 **TWRP 要用該機的 kernel／dtb 編**，目前沒有 MDZ-19-DA 版本。❓ |
| 小米電視（Android 10，baymax） | ✅ 用 USB 轉 TTL 進 u-boot：先 `printenv` 備份，必要時 `avboff`，再 dd boot、用 Magisk 修補後寫回[S22]。 | 🟡 方法通用於 Amlogic 小米電視，但要拆機找 UART 焊點，❓ MDZ-19-DA 的焊點位置不明。 |
| 小米電視 4S 75 吋（MiTV-ANSM0） | ✅ Root 後可掛載 `/dev/block/backup`，裡面有 `update_xxx.zip` 與 `xiaomi_update`，就是原廠出廠韌體；可放 FAT32 隨身碟根目錄後斷電重開來還原[S21]。 | 🟡 MDZ-19-DA 可能也有 `backup` 分割區，❓ 要 Root 才能讀。 |
| Amlogic 通用 | ✅ USB Burning Tool 需要該機專用的 `aml_upgrade_package.img`[S27]。 | ❓ 沒有公開的 MDZ-19-DA 線刷包，等於**沒有最後一道救磚手段**。 |

**結論**：MDZ-19-DA 目前**沒有**已證實的 Root 方法、TWRP、可借用的 Android TV ROM，也沒有公開線刷包。任何寫入式改裝都等於在沒有退路的情況下操作。

---

## 4. 功能保留評估

| 功能 | 混合式（不動 system） | 完整刷 Android TV（假設日後出現 ROM） | 依據 |
|---|---|---|---|
| AirPlay 音訊 | ✅ 保留 | ❌ 幾乎確定失去（米聯是小米簽章的系統 App，依賴 `mitv.service`） | §2 |
| AirPlay 螢幕鏡像 | ✅ 保留 | ❌ 同上；只能改裝第三方接收器（如 AirScreen），音訊不一定走原廠環繞 | 🟡 |
| Dolby／DTS 解碼 | ✅ 保留 | 🟡 高機率失去或降級（解碼器與授權在 vendor 層） | [S2][S4] |
| HDMI 輸出／CEC | ✅ 保留 | 🟡 可能可用，但解析度、HDR、CEC 行為不保證 | ❓ |
| HDMI 輸入切換、HDMI 1 ARC | ✅ 保留 | 🟡 高機率失去：訊號源切換靠小米 `tvplayer`，ARC 設定在小米設定 App | [S16][S32] |
| Soundbar 主喇叭 | ✅ 保留 | 🟡 **可能完全無聲**：功放初始化與 EQ 在原廠 kernel／dtb／audio HAL | 🟡 |
| 低音炮（有線） | ✅ 保留 | 🟡 同上，輸出路由靠原廠 mixer 設定 | [S5] |
| 兩顆無線後環繞 | ✅ 保留 | ❌ 幾乎確定失去（USB 5G 發射器需要私有驅動／服務） | [S5] |
| 遙控器 | ✅ 保留 | 🟡 MDZ-19-AA 刷國際版後有遙控器配對問題[S23] | [S23] |
| Google Play／Android TV 介面 | 🟡 只能用替代桌面＋側載 App | ✅（如果真的有 ROM） | — |

➤ 換句話說：**你最想保住的 AirPlay 與環繞，正好是完整刷機一定會犧牲的部分。**

---

## 5. CleanYourTV 在 Android 6 的相容性

### 5.1 已證實

➤ ✅ 上游 README：「The TV needs Android 8.0 (API 26) or newer」；安裝腳本會先檢查 SDK 等級[S13]。`launcher/app/build.gradle` 寫死 `minSdk 26`[S14]。
➤ ✅ 社群分支 **`qqwersde/my-tv-signal-android6`**[S17]：
　➤ 用 `./gradlew assembleRelease -PlauncherMinSdk=23` 編出 API 23 版本，並對 `java.time` 做 desugaring。
　➤ HOME intent filter 的 priority 設成 999（原廠 `com.mitv.tvhome` 是 100，開機會搶回 HOME）。
　➤ 只在 **MiTV4-ANSM0**（小米電視 4S 75 吋，`xmen`，board `gxbaby`，韌體 20.3.6.2057）測試過。
　➤ README 明講：**不要**在這類機器上跑 `tools/disable.sh`，也不要跑完整的 `tools/restore.sh`。
➤ ✅ MiTV4-ANSM0（Android 6.0.1）的實測[S15][S16]：
　➤ `pm disable-user`、`pm disable`、`pm hide` 都被拒絕（SecurityException）。
　➤ Android 6 沒有 `cmd`，所以 `cmd package set-home-activity` 不能用。
　➤ 安裝有黑名單機制（`pi_config`），`com.xiaomi.mitv.tvpush.tvpushservice` 必須保留。
　➤ 一位使用者用 `pm uninstall --user 0` 移除 `com.mitv.tvhome` 後，HOME 自動指向側載的桌面，3/3 次成功；**但維護者不背書這條路**。
➤ ✅ aerial-tv #81（同一款 MiTV4-ANSM0）[S18]：
　➤ HOME（keyCode 3）在 `MitvPhoneWindowManager` 就被直接送去 PatchWall，第三方的無障礙服務收不到。
　➤ 手寫 `preferred_home_activity` 無效；直接啟動 HOME intent 需要 `com.mitv.tvhome.permission.HOME_STATE` 簽章權限。
　➤ 可用的替代做法是每秒用 usage stats 檢查前景 App，再把桌面拉回來，但會有約 5 秒延遲。

### 5.2 套到 MDZ-19-DA 的判斷

➤ 🟡 MDZ-19-DA 與 MiTV4-ANSM0 同為小米 Android 6 PatchWall 系統，**預期會遇到同樣的限制**：無法停用套件、HOME 鍵被攔截、安裝有黑名單。
➤ ❓ 這個分支從沒在 MDZ-19-DA（platform 613）上跑過。
➤ 🟡 MDZ-19-DA 沒有電視訊號源，分支裡的「Inputs → ExternalSourceActivity」功能沒有意義。
➤ **建議做法**：
　➤ 用分支的 API 23 版本，當成「一般 App」安裝與開啟，**不要**跑任何 disable、restore、uninstall 腳本。
　➤ 第一階段**不要**移除 `com.mitv.tvhome`。按 HOME 回到 PatchWall 就接受它，用遙控器的 App 捷徑或開機自動啟動來進入新桌面。
　➤ 確認 AirPlay 與環繞都正常之後，才考慮 `pm uninstall --user 0 com.mitv.tvhome`。
　➤ Android 6 沒有 `pm install-existing`[S15]，還原要靠事先用 inventory 腳本拉好的原始 APK，以 `adb install -r` 裝回（🟡），或恢復原廠設定。
　➤ 這一步仍屬 ❓，因為 MDZ-19-DA 的 PatchWall 可能同時負責 Soundbar 的音效設定入口。

---

## 6. 原廠韌體：取得狀況與分析方式

### 6.1 本次嘗試結果（全部失敗或不可信）

| 來源 | 結果 |
|---|---|
| 小米官網 `mi.com/misurround`、`/specs` | Akamai 403，只能看搜尋摘要 |
| Wayback Machine | 本環境的出口政策封鎖 `web.archive.org`（API 顯示 2018-05-16 有存檔） |
| 4PDA | 反機器人驗證頁，只能看搜尋摘要 |
| Mobile01 | Akamai 403，只能看搜尋摘要 |
| 恩山「小米電視系統升級官方固件合集」 | 型號表有列 MDZ-19-DA，但下載要登入，檔案在迅雷／夸克網盤[S8] |
| 數碼之家 | 網站 WAF 攔截 |
| gofirmware 等 SEO 站 | **不可信**：檔案只有數 MB、日期矛盾、沒有雜湊值[S9] |

➤ 結論：**沒有取得可驗證的 MDZ-19-DA 原廠韌體**，所以這一版沒有實際解包結果。我不會把來路不明的網盤檔案當成原廠韌體分析。

### 6.2 最可靠的韌體來源：你手上的機器

➤ **免 Root**：`scripts/mdz19da_inventory.sh` 會用 `adb pull` 拉出 `/system` 下所有 APK 與整個 `/system/framework`。Android 6 的 shell 通常讀得到這些檔案。
➤ **有 Root 之後**：dd 每個分割區，特別是 `backup`（🟡 可能就是原廠出廠韌體[S21]）。
➤ **網盤合集**：如果真的要用，至少要比對 `build.prop` 的 `ro.build.fingerprint` 與本機完全一致，並用 `apksigner verify --print-certs` 比對系統 APK 的簽章與本機拉出來的一致。

### 6.3 分析什麼、怎麼分析

```bash
# 輸入可以是 OTA zip、system.img、boot.img，或 inventory 的輸出資料夾
docs/mdz-19-da/scripts/fw_analyze.sh mdz19da_dump_20261026_xxxx  fw_work
```

腳本會產生 `fw_work/report.txt`，涵蓋：

➤ `build.prop` 的身分欄位（device、fingerprint、platform 等）。
➤ 每個 APK 的套件名稱、版本與元件樹（service、receiver、intent action、權限），不需要 Android SDK。
➤ 關鍵字命中：airplay／raop／fairplay／airkan／milink／miplay／mirror／hpplay／lebo／dolby／dts／ms12／ddp／subwoofer／surround／soundbar／hdmi／cec 等。
➤ `framework` 內的小米客製類別（例如 `MitvPhoneWindowManager`），用來判斷 HOME 攔截與音訊路由。
➤ audio HAL 與 `audio_policy.conf`、`audio_effects.conf`、`mixer_paths*.xml`、`media_codecs*.xml`。
➤ `init*.rc` 中的原生服務（環繞發射器、音效服務通常是原生 daemon）。

---

## 7. 改裝方案比較

| 方案 | 內容 | 可行性 | AirPlay／環繞 | 磚機風險 | 建議 |
|---|---|---|---|---|---|
| **A. 完整刷 Android TV** | 整機換 ATV ROM | ❌ 沒有 ROM、沒有 TWRP、沒有線刷包 | ❌ 失去 | 極高，且無救磚手段 | **不要做** |
| **B. 混合式（免 Root）** | 原廠系統不動；ADB 側載 Android 6 版桌面與 App | ✅ 技術上可行（同系統有成功例） | ✅ 保留 | 低（只裝 App，可解除安裝） | **首選** |
| C. 混合式＋Root | 用 USB 開機的 TWRP 做全分割區備份，Magisk systemless | ❓ 目前沒有 MDZ-19-DA 版 TWRP；UART 焊點未知 | ✅ 理論上保留 | 中至高 | 只有出現專用 TWRP 或能接 UART 時才考慮 |
| D. 外接 Google TV 裝置 | Google TV 裝置接到家庭影院的 HDMI 輸入（或接電視再走 ARC）；家庭影院系統完全不動 | 🟡 取決於 HDMI 埠角色（§1.1） | ✅ 完全不動 | 零 | **若 HDMI 輸入可用，與 B 並列首選** |

方案 D 補充：

➤ ✅ 主機有 3 個 HDMI（含 ARC）與 S/PDIF 輸入[S31]，外接裝置的聲音有機會直接進家庭影院解碼。
➤ 🟡 最理想的接法是「外接裝置 → 家庭影院 HDMI IN → 家庭影院 HDMI OUT → 電視」；次佳是「外接裝置 → 電視 → ARC 回傳」。
➤ ✅ 其他音訊進入方式：AV 埠的 S/PDIF 輸入[S31]、低音炮的 AUX IN（類比立體聲，沒有環繞）[S5]、手機／電腦以 AirPlay 或藍牙推送[S3]。
➤ ❓ 外接音源有沒有後環繞，要實測。

---

## 8. 風險清單

| # | 風險 | 機率 | 影響 | 緩解 |
|---|---|---|---|---|
| R1 | 寫入 boot／recovery／system 後無法開機，且沒有線刷包 | 高（若做 A／C） | 永久磚機 | 不做 A；C 只在有專用 TWRP 且已完整 dd 備份後才做 |
| R2 | 換 ROM 後主喇叭、低音炮或後環繞無聲 | 高（若做 A） | 核心功能喪失 | 不做 A |
| R3 | 移除或停用米聯相關套件，AirPlay 消失 | 中 | AirPlay 喪失 | 清單中的投屏、`mitv.service` 一律不動 |
| R4 | 移除 `com.mitv.tvhome` 後黑畫面、失去 Soundbar 設定入口 | 中 | 需恢復原廠設定 | 第一階段不移除；先拉好原始 APK |
| R5 | 小米 OTA 更新後側載桌面被封鎖、ADB 被關、HOME 白名單收緊 | 中 | 改裝失效 | 改裝前記錄版本；側載 App 都保留 APK |
| R6 | 安裝黑名單（`pi_config`）擋掉部分 App | 中 | 部分 App 裝不上 | 保留 `tvpushservice`；改用其他 App |
| R7 | 恢復原廠設定後後環繞要重新配對、或配對不穩 | 低至中 | 暫時沒有環繞 | 後環繞背面重置鍵；發射器插回原 USB 埠 |
| R8 | 下載到假韌體或植入惡意程式的網盤 ROM | 中 | 資安、磚機 | 只用本機拉出的檔案；比對 fingerprint 與簽章 |
| R9 | 拆機接 UART 損壞主機板、失去保固 | 中 | 硬體損壞 | 非必要不拆；機器早已過保也要評估 |
| R10 | ADB 一直開著被區網其他裝置連入 | 低 | 資安 | 改裝完關閉 ADB 偵錯 |

---

## 9. 建議改裝路線（每一步都有「停止條件」）

**Phase 0：記錄現況（10 分鐘）**

➤ 拍下「設定 → 關於」的所有頁面（型號、系統版本、MAC）。
➤ 實測並記錄：iPhone AirPlay 音樂、AirPlay 螢幕鏡像、含 Dolby／DTS 音軌的影片、低音炮、兩顆後環繞。這份紀錄就是之後每一步的驗收標準。
➤ 拍下主機背板 HDMI 埠旁的印字，記錄目前哪一條線接哪個埠。
➤ HDMI 測試：
　➤ 把任何 HDMI 裝置（電腦、遊戲機、盒子）接到另外兩個 HDMI 埠，用訊號源選單切換，看畫面與聲音是否正常。
　➤ 播放含 Dolby／DTS 5.1 音軌的內容，確認兩顆後環繞有沒有聲音。
　➤ 在「設定 → 聲音／輸出」找有沒有 HDMI(ARC) 選項，並測試電視的聲音能不能回傳。
➤ 在完成 Phase 1 備份之前，**不要**做系統更新，也不要恢復原廠設定。

**Phase 1：免 Root 盤點與備份（必做）**

```bash
# 主機：設定 → 關於 → 連按「產品型號」開開發者模式 → 開 ADB 偵錯
./docs/mdz-19-da/scripts/mdz19da_inventory.sh 192.168.1.50
./docs/mdz-19-da/scripts/fw_analyze.sh mdz19da_dump_<時間>  fw_work
```

➤ 停止條件：拉不出系統 APK 或 framework → 不要進 Phase 2，先回報輸出。

**Phase 2：混合式 Android TV 化（免 Root）**

➤ 用 `adb install` 安裝 Android 6 版桌面（例如 CleanYourTV 的 API 23 分支）與需要的 App。
➤ **不要**執行任何 `pm disable`、`pm hide`、`pm uninstall`。
➤ 每裝一個 App 就重跑一次 Phase 0 的五項測試。
➤ 停止條件：任何一項 AirPlay 或環繞測試失敗 → `adb uninstall` 最後裝的 App，再測一次。

**Phase 3（選做）：減少 PatchWall 的存在感**

➤ 只有在 Phase 2 穩定使用一週後才考慮。
➤ 先試 `appops set <套件> POST_NOTIFICATION deny` 這類可逆、不刪套件的做法[S16]。
➤ `pm uninstall --user 0 com.mitv.tvhome` 屬 ❓ 高風險，必須先確認 Soundbar 音效設定不在 PatchWall 裡。

**Phase 4（不建議）：Root、TWRP、換 ROM**

➤ 前提：出現 MDZ-19-DA 專用、可 USB 開機（不寫入）的 TWRP，**或**能接 UART 並備份 u-boot 環境變數與分割表。
➤ 第一件事是 §10 的 Level 1 全分割區備份，備份完成前不寫入任何東西。
➤ 完整換 ROM（方案 A）目前沒有可用的 ROM，不列入路線。

---

## 10. 必要備份與復原方案

### 10.1 備份

**Level 0：免 Root（現在就能做）**

➤ `mdz19da_inventory.sh` 的整個輸出資料夾：`getprop`、`build.prop`、套件清單、各套件 `dumpsys`、音訊鏈 `dumpsys`、USB 裝置、監聽埠、`settings list`、全部系統 APK、`/system/framework`。
➤ 同一份資料存兩個以上不同位置（例如電腦＋雲端）。
➤ Phase 0 的照片與功能測試紀錄。

**Level 1：有 Root 或 USB 開機 TWRP 之後**

➤ 先存 `cat /proc/partitions`、`ls -l /dev/block`（腳本已收集）。
➤ 每個分割區都 dd 出來並計算 SHA-256（`userdata`、`cache` 可略過）：

```bash
# 在 TWRP 或 su 環境；<名稱> 以 /dev/block 下實際看到的為準
dd if=/dev/block/<名稱> of=/storage/<USB>/<名稱>.img
sha256sum /storage/<USB>/*.img > /storage/<USB>/SHA256SUMS
```

➤ 🟡 Amlogic 小米機種通常會有 `bootloader`、`env`、`logo`、`recovery`、`misc`、`boot`、`system`、`backup` 等分割區；**以本機實際列出的為準**。
➤ 如果有 UART：在 u-boot 下 `printenv` 與 `mmc part`，存成文字檔[S21][S22]。

### 10.2 復原（由輕到重）

| 層級 | 情境 | 做法 | 狀態 |
|---|---|---|---|
| 1 | 側載 App 造成問題 | `adb uninstall <套件>` | ✅ 一般 Android 行為 |
| 2 | 桌面或 HOME 異常 | 用 Level 0 拉出的原始 APK `adb install -r` 裝回 | ✅ |
| 3 | 系統設定錯亂 | 設定 → 恢復出廠設定；之後按後環繞背面重置鍵重新配對 | ✅[S5] |
| 4 | 開不了機但進得了 recovery | 小米 recovery 的清除資料或還原選項 | 🟡 進入方式 ❓ |
| 5 | 需要重灌原廠系統 | FAT32 隨身碟根目錄放 `xiaomi_update`＋`update.zip`（取自本機 `backup` 分割區），斷電重開或按鍵強刷 | 🟡 MiTV 與 MDZ-19-AA 有此格式[S21][S23]；MDZ-19-DA 按鍵組合 ❓（MDZ-18-DA 是機身 +／−[S7]） |
| 6 | 寫壞了分割區 | 用 TWRP 或 su 把 Level 1 的 dd 映像寫回 | 🟡 前提是做過 Level 1 |
| 7 | 完全沒有反應 | Amlogic USB Burning Tool＋該機專用線刷包 | ❓ **沒有公開線刷包** → 只能送小米售後 |

> 因為第 7 層目前不存在，第 1～3 層以外的任何操作，都要先把 Level 1 備份做完。

---

## 11. 尚待你本機確認的項目

Phase 1 跑完後，下面這些就能從 ❓ 變成 ✅：

1. `ro.product.device`、`ro.build.fingerprint`，以及 platform 613 存在哪個 property。
2. AirPlay 監聽埠對應的套件，以及 mDNS 的 `srcvers`、`features`。
3. 是否有 `com.hpplay.*`（乐播）或其他鏡像套件。
4. 後環繞 USB 發射器的 VID／PID，以及有沒有出現在 `/proc/asound/cards`。
5. `/dev/block` 下是否有 `backup` 分割區。
6. `framework` 內是否有 `MitvPhoneWindowManager`（決定 HOME 鍵是否會被攔截）。
7. audio HAL 的檔名，以及 Dolby／DTS 相關函式庫的位置。
8. 三個 HDMI 埠各自的角色（背板印字＋`audio/hdmi_control.txt`、`audio/tv_input.txt`），以及外接 HDMI 音源是否送到後環繞。

---

## 12. 來源

> 標「摘要」者：該站阻擋自動化存取，本研究只看到搜尋引擎摘要，未讀到原文。

| 編號 | 來源 | 用途 |
|---|---|---|
| S1 | [KHwang9883/MobileModels：mitv_cn.md](https://github.com/KHwang9883/MobileModels/blob/master/brands/mitv_cn.md) | MDZ-19-DA＝小米家庭影院；MDZ-19-AA＝小米盒子 3s |
| S2 | [小米商城：小米家庭影院 參數](https://www.mi.com/misurround/specs)（摘要） | T966、2GB／8GB、Dolby／DTS、5G 無線後環繞、Wi-Fi／藍牙 |
| S2-b | [小米商城：小米電視主機 參數](https://www.mi.com/tvzj/specs)（摘要） | 「米聯協議，相容 AirPlay、Miracast、WiDi、DLNA」 |
| S3 | [小米商城：小米家庭影院](https://www.mi.com/misurround)（摘要） | 藍牙／Wi-Fi 音訊投射；Dolby Audio＋DTS-HD |
| S4 | [ZNDS：小米家庭影院常見問題解答（2016-12-14）](https://www.znds.com/tv-602153-1-1.html) | 組成、上一代主機不支援後環繞、6 m 互連線、PatchWall |
| S5 | [ZNDS：1999 元小米家庭影院深度評測（2017-03-15）](https://www.znds.com/tv-700888-1-1.html) | USB 2.0 發射器、5G 自動跳頻、低音炮有線與 AUX IN、重置鍵 |
| S6 | [京東：MDZ-19-DA 商品頁](https://item.jd.com/4175268.html)（摘要） | 型號與商品對應 |
| S7 | [4PDA：Xiaomi Mi TV Bar (MDZ-18-DA) + Subwoofer 討論串](https://4pda.to/forum/index.php?showtopic=749224)、[第 620 頁起](https://4pda.to/forum/index.php?showtopic=749224&st=620)（摘要） | MDZ-19-DA 車主討論、無英文韌體；MDZ-18-DA 的 MStar、1.2.11.988、+／− 升級 |
| S8 | [恩山：小米電視系統升級官方固件合集](https://www.right.com.cn/forum/thread-8429455-1-1.html) | 型號表列出 MDZ-19-DA、MDZ-18-DA；檔案需登入、走網盤 |
| S9 | [gofirmware：Xiaomi mitv3s missionimpossible](http://gofirmware.com/download/xiaomi-mitv3s-missionimpossible) | 唯一出現 missionimpossible 的頁面；判定不可信 |
| S10 | [ApkCombo：Mi-Link (Airkan/DLNA/Airplay) Services](https://apkcombo.com/mi-link-airkan-dlna-airplay-services/com.duokan.airkan.tvbox/)（摘要） | `com.duokan.airkan.tvbox` 的正式名稱 |
| S11 | [小米電視系統應用對照表（appmiu，2023-02-08）](https://www.appmiu.com/16104.html) | 米聯投射、無線投屏、WFD、UPnP、droidlogic 音效套件 |
| S12 | [ychisbest/mitv-thirdparty-launcher](https://github.com/ychisbest/mitv-thirdparty-launcher) | 投屏套件勿凍結（Android 10 機種，僅作對照） |
| S13 | [Gathin23/cleanyourtv README](https://github.com/Gathin23/cleanyourtv) | 需要 Android 8.0（API 26） |
| S14 | [cleanyourtv：launcher/app/build.gradle](https://github.com/Gathin23/cleanyourtv/blob/main/launcher/app/build.gradle) | `minSdk 26` |
| S15 | [cleanyourtv Issue #1185：MiTV4-ANSM0 (Android 6.0.1)](https://github.com/Gathin23/cleanyourtv/issues/1185) | Android 6 的 pm 限制、HOME 行為、維護者立場 |
| S16 | [cleanyourtv：docs/devices/xiaomi-mitv4-ansm0.md](https://github.com/Gathin23/cleanyourtv/blob/main/docs/devices/xiaomi-mitv4-ansm0.md) | 必留套件（含投屏）、`pi_config`、appops 靜音 |
| S17 | [qqwersde/my-tv-signal-android6](https://github.com/qqwersde/my-tv-signal-android6) | CleanYourTV 的 API 23 分支 |
| S18 | [pengchujin/aerial-tv Issue #81](https://github.com/pengchujin/aerial-tv/issues/81) | `MitvPhoneWindowManager` 攔截 HOME |
| S19 | [cleanyourtv：xiaomi-mitv3s-48-hancock-follow-up.md](https://github.com/Gathin23/cleanyourtv/blob/main/docs/devices/xiaomi-mitv3s-48-hancock-follow-up.md) | MiTV3S-48 的投屏套件與 AirPlay 恢復紀錄 |
| S20 | [ZNDS：小米電視系列 ROOT 教程（Android 6.0.1，2020-06-07）](https://www.znds.com/tv-1175499-1-1.html) | `adb reboot update`＋USB TWRP＋Magisk |
| S21 | [ZNDS：備份／提取小米電視刷機包教程（2023-01-01）](https://www.znds.com/tv-1228243-1-1.html) | `backup` 分割區、dd 備份、隨身碟還原 |
| S22 | [ZNDS：2022 新款小米電視硬核 Root（USB 轉 TTL）](https://www.znds.com/tv-1228229-1-1.html) | u-boot `printenv`、`avboff`、dd boot |
| S23 | [ZNDS：小米盒子 3S（MDZ-19-AA）刷 Android TV 6 → 9（2022-01-04）](https://www.znds.com/tv-1208855-1-1.html) | 借用 Mi Box 3 韌體、Home＋Menu 強刷、遙控器問題 |
| S24 | [HiFiVision：Mi TV series in India](https://www.hifivision.com/threads/mi-tv-series-in-india.69342/)（摘要） | 小米電視 4 的 65 吋版為 T966 |
| S25 | [知乎：小米盒子是否原生支援 AirPlay](https://www.zhihu.com/question/20597548/answer/1129063613)（摘要） | 主張小米 AirPlay 為乐播方案（有爭議） |
| S26 | [PjTime：小米家庭影院 12 月 12 日首賣](http://www.pjtime.com/2016/12/182714691226.shtml)（摘要） | 首賣日期 |
| S27 | [CoreELEC Wiki：Amlogic USB Burning Tool](https://wiki.coreelec.org/coreelec:aml_usb_tool)（摘要） | 線刷需要專用映像 |
| S28 | [Mobile01：開箱 小米家庭影視劇院 無線環繞版](https://www.mobile01.com/topicdetail.php?f=347&t=5022408)（摘要） | 台灣使用者開箱，未涉及 AirPlay 或刷機 |
| S29 | [4PDA：Xiaomi Mi Box 3S](https://4pda.to/forum/index.php?showtopic=785507)（摘要）、[CNX Software](https://www.cnx-software.com/?p=39631)（摘要） | MDZ-19-AA 為 S905X |
| S30 | [Kodi Forum：MDZ-19-AA can flash to Global](https://forum.kodi.tv/showthread.php?tid=316627)、[Lowyat 論壇](https://forum.lowyat.net/topic/3561305/+1380)（摘要） | MDZ-19-AA 轉國際版的社群回報 |
| S31 | [家庭影院網：小米家庭影院體驗評測（2017-02-14）](https://www.hdav.com.cn/cp/cpyx/3883.html) | 主機背板介面：HDMI 2.0a ×3（含 1 個 ARC）、S/PDIF 輸入與輸出；介面與分體電視主機基本一致 |
| S32 | [ZNDS：小米 3 電視連接次世代功放（ARC）教程（2016-03-02）](https://www.znds.com/tv-376894-1-1.html) | 米 3 電視主機把 HDMI IN 1 定義為 ARC，以及設定路徑 |

---

## 附錄：腳本

| 檔案 | 用途 | 會不會寫入裝置 |
|---|---|---|
| `scripts/mdz19da_inventory.sh` | 透過 ADB 唯讀盤點並拉出系統 APK／framework | 不會 |
| `scripts/fw_analyze.sh` | 離線分析 OTA zip、system.img、boot.img 或盤點資料夾 | 不碰裝置 |
| `scripts/sdat2img.py` | block-based OTA（`system.new.dat`）還原成 ext4 | — |
| `scripts/bootimg_ramdisk.py` | 解 boot／recovery 的 ramdisk（會擋掉 `..` 路徑） | — |
| `scripts/axml_dump.py` | 免 SDK 解析 APK 的二進位 AndroidManifest | — |

所有 Python 腳本都建議用 `python3 -I` 執行，因為它們讀的是不可信的韌體內容。
