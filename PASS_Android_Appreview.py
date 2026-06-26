# ==========================================
# PASS Android Review Report
# ==========================================
import os

from google_play_scraper import reviews
import pandas as pd
from datetime import datetime, timedelta
import requests

# ==========================================
# Telegram 설정
# ==========================================

BOT_TOKEN = os.getenv("REVIEW_BOT_TOKEN")
CHAT_ID = os.getenv("REVIEW_CHAT_ID")

# ==========================================
# 리뷰 수집
# ==========================================

result, _ = reviews(
    'com.sktelecom.tauth',
    lang='ko',
    country='kr',
    count=500
)

review_list = []

for r in result:
    review_list.append({
        "작성일": pd.to_datetime(r["at"]),
        "작성자": r["userName"],
        "평점": int(r["score"]),
        "리뷰내용": str(r["content"])
    })

df = pd.DataFrame(review_list)

# ==========================================
# 분석기간
# 현재일 -8일 ~ 현재일 -1일
# ==========================================

today = datetime.now()

start_date = today - timedelta(days=8)
end_date = today - timedelta(days=1)

recent_df = df[
    (df["작성일"] >= start_date) &
    (df["작성일"] <= end_date)
].copy()

# ==========================================
# 리뷰 통계
# ==========================================

review_count = len(recent_df)

avg_score = (
    round(recent_df["평점"].mean(), 2)
    if review_count > 0
    else 0
)

# ==========================================
# 긍정 리뷰 TOP3
# ==========================================

positive_reviews = recent_df[
    recent_df["평점"] >= 4
].sort_values(
    by=["평점", "작성일"],
    ascending=[False, False]
).head(3)

# ==========================================
# 부정 리뷰 TOP5
# ==========================================

negative_reviews = recent_df[
    recent_df["평점"] <= 2
].sort_values(
    by=["평점", "작성일"],
    ascending=[True, False]
).head(5)

# ==========================================
# 메시지 생성
# ==========================================

nums = ["①", "②", "③", "④", "⑤"]

message = ""

message += "📱 PASS Android Review Report\n"

message += "━━━━━━━━━━━━━━━\n\n"

message += "📅 분석 기간\n"
message += (
    f"{start_date.strftime('%Y.%m.%d')} ~ "
    f"{end_date.strftime('%Y.%m.%d')}\n\n"
)

message += "⭐ 리뷰 현황\n"
message += f"• 평균 별점 : {avg_score}점 / 5점\n"
message += f"• 리뷰 수 : 총 {review_count}건\n\n"

# ==========================================
# 긍정 리뷰 TOP3
# ==========================================

message += "───────────────\n\n"

message += "👍 긍정 리뷰 (별점 4개 이상)\n\n"

if len(positive_reviews) == 0:

    message += "• 해당 기간 리뷰 없음\n\n"

else:

    for idx, row in enumerate(
        positive_reviews.itertuples()
    ):

        review = (
            row.리뷰내용[:120]
            .replace("\n", " ")
            .strip()
        )

        message += f"{nums[idx]} {review}\n"

# ==========================================
# 부정 리뷰 TOP5
# ==========================================

message += "\n\n👎 부정 리뷰 (별점 2개 이하)\n\n"

if len(negative_reviews) == 0:

    message += "• 해당 기간 리뷰 없음\n\n"

else:

    for idx, row in enumerate(
        negative_reviews.itertuples()
    ):

        review = (
            row.리뷰내용[:150]
            .replace("\n", " ")
            .strip()
        )

        message += f"{nums[idx]} {review}\n"

# ==========================================
# Store 링크
# ==========================================

message += "\n───────────────\n\n"

message += "아래 링크로 🔍 Store Review 보러가기\n\n"

message += (
    "Android\n"
    "https://play.google.com/store/apps/details"
    "?id=com.sktelecom.tauth&showAllReviews=true"
)

# 텔레그램 제한 대응
message = message[:3900]

# ==========================================
# 콘솔 확인
# ==========================================

print(message)

# ==========================================
# Telegram 발송
# ==========================================


url = (
    f"https://api.telegram.org/bot"
    f"{BOT_TOKEN}/sendMessage"
)

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("\n전송결과 :", response.status_code)
print(response.text)
