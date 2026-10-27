#!/usr/bin/env bash
# MDZ-19-DA 唯讀盤點與免 Root 備份（在電腦端執行，透過網路 ADB）。
#
# 本腳本只做「讀取」：不安裝、不停用、不刪除、不改任何設定。
# 用法：
#   ./mdz19da_inventory.sh <主機IP[:5555]> [輸出資料夾]
# 環境變數：
#   PULL_APK=0        不拉取 /system 下的 APK 與 framework（預設 1 = 拉取）
#
# 前置：主機「設定 → 關於 → 連按產品型號」開啟開發者模式並開啟 ADB 偵錯，
# 首次連線時在電視上按「允許」。
set -u

TARGET="${1:?用法: $0 <主機IP[:5555]> [輸出資料夾]}"
case "$TARGET" in *:*) ;; *) TARGET="$TARGET:5555" ;; esac
OUT="${2:-mdz19da_dump_$(date +%Y%m%d_%H%M%S)}"
PULL_APK="${PULL_APK:-1}"

command -v adb >/dev/null || { echo "找不到 adb，請先安裝 Android platform-tools" >&2; exit 1; }

adb connect "$TARGET" >/dev/null
if ! adb -s "$TARGET" get-state >/dev/null 2>&1; then
  echo "無法連線 $TARGET（請確認已在電視上允許 ADB 偵錯）" >&2
  exit 1
fi

mkdir -p "$OUT"/{props,pkgs,audio,net,sys,svc,apk}
sh_out() { # sh_out <輸出檔> <裝置端指令...>
  local f="$1"; shift
  # Android 6 的 adb shell 不支援 shell v2，輸出帶 CRLF，需去掉 \r
  adb -s "$TARGET" shell "$@" </dev/null 2>&1 | tr -d '\r' >"$OUT/$f"
}

echo "[1/7] 系統屬性與身分"
sh_out props/getprop.txt getprop
sh_out props/build.prop cat /system/build.prop
sh_out props/default.prop cat /default.prop
sh_out sys/proc_version.txt cat /proc/version
sh_out sys/cpuinfo.txt cat /proc/cpuinfo
sh_out sys/cmdline.txt cat /proc/cmdline

echo "[2/7] 分割區與掛載（救磚時要對照的資料）"
sh_out sys/partitions.txt cat /proc/partitions
sh_out sys/dev_block.txt ls -l /dev/block
sh_out sys/by_name.txt 'ls -l /dev/block/platform/*/by-name /dev/block/by-name 2>&1'
sh_out sys/mounts.txt cat /proc/mounts
sh_out sys/df.txt df

echo "[3/7] 套件清單"
sh_out pkgs/all.txt pm list packages -f -i
sh_out pkgs/system.txt pm list packages -f -s
sh_out pkgs/third_party.txt pm list packages -f -3
sh_out pkgs/disabled.txt pm list packages -d
sh_out pkgs/features.txt pm list features
sh_out pkgs/libraries.txt pm list libraries
sh_out pkgs/preferred_activities.txt dumpsys package preferred

# 投屏、音訊、HDMI、環繞相關的套件逐一 dumpsys
KEYWORDS='airkan|airplay|airtunes|raop|milink|miplay|smartshare|upnp|dlna|wfd|mirror|cast|hpplay|lebo|audio|sound|dolby|dts|subwoofer|surround|soundbar|speaker|karaoke|hdmi|cec|tvplayer|tvservice|mitv\.service|droidlogic|amlogic|tvhome|tvpush|upgrade'
sed -n 's/^package:.*\.apk=\([^ ]*\).*$/\1/p' "$OUT/pkgs/all.txt" \
  | grep -Ei "$KEYWORDS" | sort -u >"$OUT/pkgs/keyword_packages.txt"
while read -r pkg; do
  [ -n "$pkg" ] && sh_out "pkgs/dumpsys_${pkg}.txt" dumpsys package "$pkg"
done <"$OUT/pkgs/keyword_packages.txt"

echo "[4/7] 音訊鏈（AudioFlinger／Policy／HAL／USB 無線發射器）"
sh_out audio/audio_flinger.txt dumpsys media.audio_flinger
sh_out audio/audio_policy.txt dumpsys media.audio_policy
sh_out audio/audio_service.txt dumpsys audio
sh_out audio/hdmi_control.txt dumpsys hdmi_control
sh_out audio/tv_input.txt dumpsys tv_input
sh_out audio/asound_cards.txt cat /proc/asound/cards
sh_out audio/asound_pcm.txt cat /proc/asound/pcm
sh_out audio/dev_snd.txt ls -l /dev/snd
sh_out audio/lib_hw.txt ls -l /system/lib/hw
sh_out audio/lib_keyword.txt "ls -l /system/lib /system/vendor/lib 2>&1 | grep -Ei 'audio|dolby|dts|dcv|ms12|ddp|ac3|airplay|airtunes|raop|fairplay|mirror|cast|hpplay|tas|amp|wireless'"
sh_out audio/etc_audio_files.txt "ls -l /system/etc /system/vendor/etc 2>&1 | grep -Ei 'audio|effect|mixer|codec|dolby|dts'"
sh_out audio/audio_policy.conf cat /system/etc/audio_policy.conf
sh_out audio/audio_effects.conf cat /system/etc/audio_effects.conf
sh_out audio/usb_devices.txt 'for d in /sys/bus/usb/devices/*; do echo "== $d"; for k in idVendor idProduct manufacturer product bInterfaceClass; do [ -f "$d/$k" ] && echo "$k=$(cat "$d/$k")"; done; done'

echo "[5/7] 服務與行程"
sh_out svc/service_list.txt service list
sh_out svc/dumpsys_list.txt dumpsys -l
sh_out svc/ps.txt ps
sh_out svc/activity_services.txt dumpsys activity services
sh_out svc/init_rc_list.txt 'ls -l / /system/etc/init 2>&1'

echo "[6/7] 網路埠（AirPlay 通常監聽 7000/7100/47000 等）與設定值"
sh_out net/tcp.txt cat /proc/net/tcp
sh_out net/tcp6.txt cat /proc/net/tcp6
sh_out net/udp.txt cat /proc/net/udp
sh_out net/netstat.txt netstat -n
sh_out net/settings_system.txt settings list system
sh_out net/settings_secure.txt settings list secure
sh_out net/settings_global.txt settings list global

if [ "$PULL_APK" = "1" ]; then
  echo "[7/7] 拉取系統 APK 與 framework（免 Root 備份，供日後重裝或分析）"
  sed -n 's/^package:\(.*\.apk\)=\([^ ]*\).*$/\1 \2/p' "$OUT/pkgs/system.txt" \
  | while read -r path pkg; do
      adb -s "$TARGET" pull "$path" "$OUT/apk/${pkg}.apk" </dev/null >/dev/null 2>&1 \
        || echo "pull 失敗: $pkg ($path)" >>"$OUT/apk/_failed.txt"
    done
  adb -s "$TARGET" pull /system/framework "$OUT/framework" >/dev/null 2>&1 \
    || echo "framework 拉取失敗" >>"$OUT/apk/_failed.txt"
else
  echo "[7/7] 跳過 APK 拉取（PULL_APK=0）"
fi

# 監聽埠對應 uid（/proc/net/tcp 第 8 欄），方便找出是哪個套件在提供 AirPlay
cat "$OUT/net/tcp.txt" "$OUT/net/tcp6.txt" 2>/dev/null \
  | awk '$4=="0A" {split($2,a,":"); print a[2], $8}' \
  | while read -r hexport uid; do printf 'port=%d uid=%s\n' "0x$hexport" "$uid"; done \
  | sort -u >"$OUT/net/listen_ports_uid.txt"

cat <<EOF

完成：$OUT
下一步建議：
  1. 檢查 $OUT/pkgs/keyword_packages.txt 與 net/listen_ports_uid.txt，
     用 dumpsys_*.txt 內的 userId 對應出 AirPlay／環繞相關套件。
  2. 在同網段電腦執行（擇一）查看 AirPlay 廣播的 TXT 記錄（srcvers、model、features）：
       avahi-browse -rt _airplay._tcp ; avahi-browse -rt _raop._tcp
       dns-sd -B _airplay._tcp      （macOS）
  3. 把整個 $OUT 資料夾複製到兩個以上不同的儲存位置。
EOF
