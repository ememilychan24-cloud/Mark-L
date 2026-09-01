#!/usr/bin/env bash
# 多租戶隔離測試。跑法：cd web && ./test.sh
#
# 呢度測嘅唔係功能，係**一個客戶睇唔睇到第二個客戶嘅嘢**。
# 呢條規矩錯咗唔會有錯誤訊息，只會有一日有人喺自己個工作台見到人哋嘅同意書。
set -u
PORT=${PORT:-8899}
H='Content-Type: application/json'
B=http://127.0.0.1:$PORT
FAIL=0

ok(){ if [ "$2" = "$3" ]; then echo "  ✓ $1"; else echo "  ✗ $1（得到 $2，應該 $3）"; FAIL=$((FAIL+1)); fi; }
code(){ curl -s -o /dev/null -w '%{http_code}' "$@"; }

rm -rf .wrangler/state 2>/dev/null
npx --yes wrangler@4 d1 execute workbench --file=./schema.sql --local >/dev/null 2>&1
npx --yes wrangler@4 dev --local --port "$PORT" --ip 127.0.0.1 >/tmp/wb-test.log 2>&1 &
DEV_PID=$!
# 用 PID 收工，唔用 pkill —— pkill -f 個 pattern 會連跑緊呢個腳本嘅 shell 都殺埋
cleanup(){ kill $DEV_PID 2>/dev/null; }
trap cleanup EXIT

for _ in $(seq 1 60); do curl -sf -o /dev/null $B/login.html 2>/dev/null && break; sleep 1; done

O=$(mktemp); A=$(mktemp)
curl -s -c "$O" -X POST -H "$H" -d '{"code":"test-owner-key"}' $B/api/login >/dev/null
curl -s -b "$O" -X POST -H "$H" \
  -d '{"draft":{"archetype":"service-booking","platforms":["ig"],"handles":["client-a"]}}' \
  $B/api/clients >/dev/null
curl -s -b "$O" -X POST -H "$H" \
  -d '{"draft":{"archetype":"local-storefront","platforms":["fb"],"handles":["client-b"]}}' \
  $B/api/clients >/dev/null
CODE=$(curl -s -b "$O" -X POST -H "$H" -d '{"slug":"client-a"}' $B/api/invites \
  | python3 -c 'import json,sys;print(json.load(sys.stdin)["code"])')
curl -s -c "$A" -X POST -H "$H" -d "{\"code\":\"$CODE\"}" $B/api/login >/dev/null

echo "隔離"
ok "未登入睇唔到嘢"           "$(code $B/api/clients)" 401
ok "錯碼入唔到"               "$(code -X POST -H "$H" -d '{"code":"nope"}' $B/api/login)" 401
ok "客戶睇到自己"             "$(code -b "$A" $B/api/clients/client-a/files)" 200
ok "客戶偷唔到第二個客"       "$(code -b "$A" $B/api/clients/client-b/files)" 404
ok "客戶偷唔到人哋嘅檔案"     "$(code -b "$A" "$B/api/clients/client-b/file?path=brand/BIBLE.md")" 404
ok "客戶開唔到新客"           "$(code -b "$A" -X POST -H "$H" -d '{"draft":{"archetype":"education","platforms":["fb"]}}' $B/api/clients)" 404
ok "客戶發唔到邀請碼"         "$(code -b "$A" -X POST -H "$H" -d '{"slug":"client-b"}' $B/api/invites)" 404
ok "路徑穿越無效"             "$(code -b "$A" "$B/api/clients/client-a/file?path=../client-b/brand/BIBLE.md")" 404
ok "偽造 cookie 無效"         "$(code -H 'Cookie: wb=owner%7C%7C99999999999%7Cfake' $B/api/clients)" 401
ok "撞名唔會靜靜雞合併"       "$(code -b "$O" -X POST -H "$H" -d '{"draft":{"archetype":"education","platforms":["fb"],"handles":["client-a"]}}' $B/api/clients)" 409

N=$(curl -s -b "$A" $B/api/clients | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["clients"]))')
ok "客戶名單只有自己一個"     "$N" 1
M=$(curl -s -b "$O" $B/api/clients | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["clients"]))')
ok "owner 見到兩個"           "$M" 2

echo
if [ $FAIL -eq 0 ]; then echo "✓ 全部通過"; else echo "✗ $FAIL 項failed"; fi
exit $FAIL
