#!/bin/sh
# 重新生成练习包里的两张截图。需要 Google Chrome。
set -e
cd "$(dirname "$0")"
OUT=../../AI视频教程/资料
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$OUT/后台截图" "$OUT/审核样例"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1280,900 --screenshot="$OUT/后台截图/赛博朋克重庆-作品数据.png" "file://$PWD/后台截图-作品数据.html"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1280,720 --screenshot="$OUT/审核样例/限流通知截图.png" "file://$PWD/限流通知.html"
