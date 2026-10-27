#!/usr/bin/env bash
# MDZ-19-DA 韌體離線分析：找出 APK、Framework、音訊服務與 AirPlay 相關元件。
#
# 用法：
#   ./fw_analyze.sh <輸入> [工作資料夾]
# <輸入> 可以是：
#   ➤ OTA／卡刷 zip（block-based：system.new.dat + system.transfer.list；或 file-based：內含 system/）
#   ➤ system.img（raw ext4 或 Android sparse）
#   ➤ boot.img / recovery.img（只解 ramdisk 與 init*.rc）
#   ➤ 已解開的 system 資料夾，或 mdz19da_inventory.sh 拉下來的輸出資料夾
#
# 只讀取輸入、不修改輸入。解出來的檔案視為不可信資料，全部放在工作資料夾。
# 需要：bash、python3、unzip、strings；選用：debugfs（e2fsprogs）、simg2img、brotli。
set -u

IN="${1:?用法: $0 <zip|img|資料夾> [工作資料夾]}"
WORK="${2:-fw_work_$(date +%Y%m%d_%H%M%S)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="python3 -I"
KW='airplay|airtunes|raop|fairplay|airkan|milink|miplay|mirror|smartshare|hpplay|lebo|dlna|upnp|wfd|miracast|dolby|dts|ms12|dcv|ddp|eac3|ac3|truehd|subwoofer|surround|soundbar|speaker|wireless|dongle|hdmi|\bcec\b|\barc\b|spdif|tas57|amplifier|droidlogic'

[ -e "$IN" ] || { echo "找不到輸入：$IN" >&2; exit 1; }
mkdir -p "$WORK"
WORK="$(cd "$WORK" && pwd)"
REPORT="$WORK/report.txt"
: >"$REPORT"
log() { printf '%s\n' "$*" | tee -a "$REPORT"; }
section() { log ""; log "==================== $* ===================="; }
have() { command -v "$1" >/dev/null 2>&1; }

ROOT=""      # 解開後的 system 根目錄
RAMDISKS=()  # 解開後的 ramdisk 目錄

magic_hex() { od -An -tx1 -N "$2" -j "${3:-0}" "$1" | tr -d ' \n'; }

extract_bootimg() { # extract_bootimg <img> <name>
  local out="$WORK/$2"
  $PY "$SCRIPT_DIR/bootimg_ramdisk.py" "$1" "$out" | tee -a "$REPORT"
  [ -d "$out/ramdisk" ] && RAMDISKS+=("$out/ramdisk")
}

extract_ext4() { # extract_ext4 <system.img>
  local img="$1"
  if [ "$(magic_hex "$img" 4)" = "3aff26ed" ]; then
    have simg2img || { log "sparse image 需要 simg2img（android-sdk-libsparse-utils）"; return 1; }
    simg2img "$img" "$WORK/system.raw.img" && img="$WORK/system.raw.img"
  fi
  if [ "$(magic_hex "$img" 2 1080)" != "53ef" ]; then
    log "不是 ext4 映像（可能是 Amlogic aml_upgrade_package.img，需先用 aml 解包工具拆開）"
    return 1
  fi
  have debugfs || { log "需要 debugfs（e2fsprogs）來免掛載解開 ext4"; return 1; }
  mkdir -p "$WORK/system_root"
  debugfs -R "rdump / $WORK/system_root" "$img" >/dev/null 2>&1
  ROOT="$WORK/system_root"
}

section "輸入：$IN"
if [ -d "$IN" ]; then
  if [ -f "$IN/build.prop" ]; then ROOT="$(cd "$IN" && pwd)"
  elif [ -f "$IN/system/build.prop" ]; then ROOT="$(cd "$IN/system" && pwd)"
  elif [ -d "$IN/apk" ] && [ -d "$IN/props" ]; then ROOT="$(cd "$IN" && pwd)"; log "偵測為 mdz19da_inventory.sh 的輸出資料夾"
  else log "資料夾內找不到 build.prop"; exit 1; fi
elif [ "$(magic_hex "$IN" 4)" = "504b0304" ]; then
  mkdir -p "$WORK/zip"
  unzip -o -q "$IN" -d "$WORK/zip"
  log "zip 內容（前 200 項）："; unzip -l "$IN" | head -200 | tee -a "$REPORT" >/dev/null
  Z="$WORK/zip"
  for f in "$Z/META-INF/com/google/android/updater-script" "$Z/META-INF/com/android/metadata"; do
    [ -f "$f" ] && { log "--- $(basename "$f") ---"; head -80 "$f" | tee -a "$REPORT" >/dev/null; }
  done
  if [ -f "$Z/system.new.dat.br" ] && [ ! -f "$Z/system.new.dat" ]; then
    have brotli && brotli -d -o "$Z/system.new.dat" "$Z/system.new.dat.br" || log "需要 brotli 解壓 system.new.dat.br"
  fi
  if [ -f "$Z/system.new.dat" ] && [ -f "$Z/system.transfer.list" ]; then
    $PY "$SCRIPT_DIR/sdat2img.py" "$Z/system.transfer.list" "$Z/system.new.dat" "$WORK/system.img" | tee -a "$REPORT"
    extract_ext4 "$WORK/system.img"
  elif [ -f "$Z/system.img" ]; then extract_ext4 "$Z/system.img"
  elif [ -f "$Z/system/build.prop" ]; then ROOT="$Z/system"
  fi
  for b in boot recovery; do [ -f "$Z/$b.img" ] && extract_bootimg "$Z/$b.img" "$b"; done
elif [ "$(magic_hex "$IN" 8)" = "414e44524f494421" ] || grep -qa 'ANDROID!' <(head -c 4096 "$IN"); then
  extract_bootimg "$IN" "$(basename "$IN" .img)"
else
  extract_ext4 "$IN"
fi

if [ -z "$ROOT" ] && [ ${#RAMDISKS[@]} -eq 0 ]; then
  log "無法取得可分析的檔案系統，結束。"; exit 1
fi

if [ -n "$ROOT" ]; then
  BP="$ROOT/build.prop"; [ -f "$BP" ] || BP="$ROOT/props/build.prop"
  section "身分（build.prop）"
  [ -f "$BP" ] && grep -Ei '^ro\.(product\.|build\.(fingerprint|version\.(release|sdk|incremental)|display\.id|date=|type|tags)|board|hardware|mitv|mi\.|boot)|platform|soundbar|subwoofer|surround|dolby|dts' "$BP" | tee -a "$REPORT" >/dev/null

  section "APK 清單（路徑 | 大小 | 套件 | 版本）"
  APKS="$WORK/apk_list.txt"; : >"$APKS"
  mkdir -p "$WORK/manifests"
  find "$ROOT" -type f -name '*.apk' 2>/dev/null | sort | while read -r apk; do
    m="$WORK/manifests/$(echo "${apk#"$ROOT"/}" | tr '/' '_').txt"
    $PY "$SCRIPT_DIR/axml_dump.py" "$apk" >"$m" 2>&1
    head1="$(head -1 "$m")"
    pkg="$(sed -n 's/.*package=\([^ >]*\).*/\1/p' <<<"$head1")"
    ver="$(sed -n 's/.*versionName=\([^ >]*\).*/\1/p' <<<"$head1")"
    printf '%s | %s | %s | %s\n' "${apk#"$ROOT"/}" "$(stat -c %s "$apk")" "${pkg:-?}" "${ver:-?}" >>"$APKS"
  done
  tee -a "$REPORT" <"$APKS" >/dev/null
  log "（每個 APK 的元件樹在 $WORK/manifests/）"

  section "關鍵字命中：APK 套件／元件（投屏、AirPlay、音訊、HDMI、環繞）"
  grep -Eil "$KW" "$WORK"/manifests/*.txt 2>/dev/null | while read -r m; do
    log "--- $(basename "$m" .txt)"
    grep -Ei "$KW|<manifest|<service|<receiver" "$m" | head -40 | tee -a "$REPORT" >/dev/null
  done

  section "關鍵字命中：APK 內的原生函式庫與資源"
  find "$ROOT" -type f -name '*.apk' 2>/dev/null | sort | while read -r apk; do
    hits="$(unzip -Z1 "$apk" 2>/dev/null | grep -Ei "$KW|\.so$" | grep -Ei "$KW|lib/")"
    [ -n "$hits" ] && { log "--- ${apk#"$ROOT"/}"; head -30 <<<"$hits" | tee -a "$REPORT" >/dev/null; }
  done

  section "系統原生函式庫（/lib、/lib/hw、/vendor/lib）中的關鍵字"
  find "$ROOT" -type f -name '*.so' 2>/dev/null | grep -Ei "$KW|/hw/|audio" | sed "s#^$ROOT/##" | sort | tee -a "$REPORT" >/dev/null
  log "--- .so 內部字串命中次數（前 40 名）"
  find "$ROOT" -type f -name '*.so' 2>/dev/null | while read -r so; do
    n="$(strings -n 5 "$so" 2>/dev/null | grep -Eic 'airplay|airtunes|raop|fairplay|mirror|dolby|dts|ddp|eac3|subwoofer|surround|soundbar|wireless')"
    [ "$n" -gt 0 ] && echo "$n ${so#"$ROOT"/}"
  done | sort -rn | head -40 | tee -a "$REPORT" >/dev/null

  section "Framework（找小米客製的 PhoneWindowManager、HOME 攔截、音訊路由）"
  for fw in "$ROOT"/framework/*.jar "$ROOT"/framework/*.apk "$ROOT"/framework/*/*.odex "$ROOT"/framework/*/*.oat; do
    [ -f "$fw" ] || continue
    if unzip -Z1 "$fw" 2>/dev/null | grep -q '^classes.*\.dex$'; then
      src="$(unzip -p "$fw" 'classes*.dex' 2>/dev/null | strings -n 6)"
    else
      src="$(strings -n 6 "$fw")"
    fi
    hits="$(grep -Eo 'L?(com|android|mitv|miui)/[A-Za-z0-9_/$]*([Mm]itv|[Mm]iui|[Xx]iaomi|[Ss]oundbar|[Ss]ubwoofer|[Ss]urround|[Aa]irplay|[Hh]dmi|[Dd]olby|[Dd]ts)[A-Za-z0-9_/$]*' <<<"$src" | sort -u | head -25)"
    [ -n "$hits" ] && { log "--- ${fw#"$ROOT"/}"; tee -a "$REPORT" <<<"$hits" >/dev/null; }
  done

  section "音訊與媒體設定檔（已複製到 $WORK/audio_cfg）"
  mkdir -p "$WORK/audio_cfg"
  find "$ROOT" -type f \( -name 'audio_policy*' -o -name 'audio_effects*' -o -name 'mixer_paths*' -o -name 'media_codecs*' -o -name 'media_profiles*' -o -iname '*dolby*' -o -iname '*dts*' \) 2>/dev/null \
    | while read -r f; do cp -p "$f" "$WORK/audio_cfg/$(echo "${f#"$ROOT"/}" | tr '/' '_')"; log "${f#"$ROOT"/}"; done
fi

section "init 服務（system/etc/init 與 ramdisk 的 *.rc）"
for d in "${ROOT:-/nonexistent}" "${RAMDISKS[@]}"; do
  [ -d "$d" ] || continue
  find "$d" -maxdepth 3 -type f -name '*.rc' 2>/dev/null | while read -r rc; do
    svc="$(grep -E '^service ' "$rc")"
    [ -n "$svc" ] && { log "--- $rc"; tee -a "$REPORT" <<<"$svc" >/dev/null; }
  done
done

log ""
log "完成。完整報告：$REPORT"
