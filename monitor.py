import requests
import os
from datetime import datetime, timedelta

GOODS_CODE = "26005599"
PERF_URL   = f"https://tickets.interpark.com/goods/{GOODS_CODE}"
BASE_URL   = "https://api-ticketfront.interpark.com"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]

PLAY_DATES = ["20260607"]

HEADERS = {
    "sec-ch-ua-platform": '"macOS"',
    "referer":            "https://tickets.interpark.com/",
    "user-agent":         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "accept":             "application/json, text/plain, */*",
    "sec-ch-ua":          '"HeadlessChrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "accept-language":    "ko-KR",
    "sec-ch-ua-mobile":   "?0",
}

def check_remain(play_date):
    ts  = int(datetime.now().timestamp() * 1000)
    url = f"{BASE_URL}/v1/goods/{GOODS_CODE}/playSeq/PlayDate/{play_date}/ALL"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        return data.get("data", {}).get("remainSeat", [])
    except Exception as e:
        print(f"[{play_date}] 조회 오류: {e}")
        return None

def send_telegram(message):
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message},
            timeout=10,
        )
        if resp.status_code == 200:
            print("✅ 텔레그램 알림 전송 완료!")
        else:
            print(f"⚠️  텔레그램 오류: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] 인터파크 취소표 모니터 시작 (공연: {GOODS_CODE})")

    available_list = []

    for date in PLAY_DATES:
        remain = check_remain(date)
        yyyy, mm, dd = date[:4], date[4:6], date[6:]
        label = f"{yyyy}년 {mm}월 {dd}일"

        if remain is None:
            print(f"  [{label}] ❌ 조회 실패")
            continue

        print(f"  [{label}] 잔여석: {remain}")

        if len(remain) > 0:
            seats_text = "\n".join([
                f"  ✅ {r.get('playSeqName', '회차')} - 잔여 {r.get('remainCnt', '?')}석"
                for r in remain
            ])
            available_list.append(f"📅 {label}\n{seats_text}")

    if available_list:
        msg  = "🚨 인터파크 취소표 발생!\n\n"
        msg += "\n\n".join(available_list)
        msg += f"\n\n🔗 {PERF_URL}"
        print("\n" + msg)
        send_telegram(msg)
    else:
        print("\n모든 날짜 매진 상태입니다.")

if __name__ == "__main__":
    main()
