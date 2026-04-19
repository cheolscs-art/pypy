import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# =========================
# 1. 종목 리스트
# =========================
def get_krx_list():
    try:
        df = fdr.StockListing('KRX')
        df = df[['Code', 'Name']]
        print(f"✅ 종목 수: {len(df)}")
        return df
    except Exception as e:
        print("❌ 종목 리스트 로드 실패:", e)
        return pd.DataFrame(columns=['Code', 'Name'])


# =========================
# 2. 가격 데이터
# =========================
def get_price(code):
    end = datetime.today()
    start = end - timedelta(days=90)

    try:
        df = fdr.DataReader(code, start, end)

        if df is None or df.empty:
            return pd.DataFrame()

        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required):
            return pd.DataFrame()

        return df[required].copy()

    except:
        return pd.DataFrame()


# =========================
# 3. 기술지표
# =========================
def add_indicators(df):
    df = df.copy()

    # 이동평균
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()

    # 거래량 평균
    df['Vol_MA20'] = df['Volume'].rolling(20).mean()

    # 변동성
    df['Volatility'] = df['Close'].pct_change().rolling(10).std()

    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    loss = loss.replace(0, np.nan)

    rs = gain / loss
    df['RSI'] = (100 - (100 / (1 + rs))).fillna(50)

    return df.ffill().fillna(0)


# =========================
# 4. 급등 탐지 로직
# =========================
def detect_surge(df):
    if len(df) < 30:
        return 0

    latest = df.iloc[-1]

    score = 0

    # 1️⃣ 거래량 폭발
    if latest['Volume'] > latest['Vol_MA20'] * 3:
        score += 30

    # 2️⃣ 단기 상승률
    ret = (latest['Close'] / df['Close'].iloc[-5] - 1) * 100
    if ret > 5:
        score += 25
    elif ret < -3:
        score -= 10

    # 3️⃣ 변동성 증가
    if latest['Volatility'] > 0.03:
        score += 15

    # 4️⃣ 고점 돌파
    if latest['Close'] > df['High'].rolling(20).max().iloc[-2]:
        score += 30

    # 5️⃣ 이동평균 정배열
    if latest['MA5'] > latest['MA20']:
        score += 10

    # 6️⃣ RSI 필터
    if latest['RSI'] < 30:
        score += 10
    elif latest['RSI'] > 75:
        score -= 5

    return int(score)


# =========================
# 5. AI 점수 (간단 버전)
# =========================
def ai_score(df):
    try:
        momentum = df['Close'].pct_change().rolling(5).mean().iloc[-1]
        accel = df['Close'].pct_change().diff().iloc[-1]

        score = (momentum * 1000) + (accel * 500)

        return int(score)
    except:
        return 0


# =========================
# 6. 시장 스캔
# =========================
def scan_market(limit=200):
    stocks = get_krx_list()

    results = []

    print("\n🚀 시장 스캔 시작...\n")

    # 속도 개선: 일부만 먼저 스캔 (원하면 전체로 변경 가능)
    stocks = stocks.head(limit)

    for i, row in stocks.iterrows():
        code = row['Code']
        name = row['Name']

        df = get_price(code)

        if df.empty:
            continue

        df = add_indicators(df)

        rule_score = detect_surge(df)
        ai_s = ai_score(df)

        total_score = rule_score + ai_s

        if total_score >= 60:
            results.append({
                "name": name,
                "code": code,
                "score": total_score,
                "price": int(df['Close'].iloc[-1])
            })

            print(f"🔥 {name} ({code}) → {total_score}")

    results = sorted(results, key=lambda x: x['score'], reverse=True)

    return results


# =========================
# 7. 결과 출력 (TOP 3만 출력하도록 수정)
# =========================
def print_top(results, top_n=3):
    print("\n📊 가장 유력한 급등 후보 TOP 3\n")

    if not results:
        print("❌ 조건을 만족하는 종목이 없습니다.")
        return

    for r in results[:top_n]:
        print(f"{r['name']} ({r['code']}) | 점수: {r['score']} | 현재가: {r['price']:,}원")


# =========================
# 실행
# =========================
if __name__ == "__main__":
    results = scan_market(limit=150)  # 속도 조절

    print_top(results)  # TOP 3만 출력