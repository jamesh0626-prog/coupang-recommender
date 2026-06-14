"""
쿠팡 AI 전자기기 추천 & 리뷰 분석 웹앱
AI Engine: Google Gemini 3.5 Flash
"""

import streamlit as st
import json
import re
import urllib.parse

try:
    import google.generativeai as genai
except ImportError:
    st.error("google-generativeai 패키지가 필요합니다: pip install -U google-generativeai")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="쿠팡 AI 전자기기 추천",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 가상 상품 데이터 (Mock Data)
# ─────────────────────────────────────────────────────────────────────────────
MOCK_PRODUCTS = [
    {
        "id": "P001",
        "name": "UGREEN Nexode 100W GaN 4포트 멀티충전기",
        "price": 49900,
        "category": "충전기",
        "rating": 4.6,
        "review_count": 1823,
        "weight": "135g",
        "icon": "🔌",
        "spec": {
            "최대출력": "100W",
            "포트구성": "C×3 + A×1",
            "GaN": "5세대",
            "무게": "135g",
            "크기": "65×65×32mm",
        },
        "detail_text": """
UGREEN Nexode 100W 충전기는 GaN(질화갈륨) 5세대 칩을 탑재한 초소형 고출력 충전기입니다.

[Dynamic Power Allocation 시스템]
포트별 지능형 전력 분배 기술 탑재. 연결된 기기 수와 종류에 따라 실시간으로 전력을 재분배합니다.
C포트1만 연결 시 100W 풀출력, C포트1+2 동시 연결 시 자동으로 65W/35W로 분배됩니다.
UGREEN 독자 특허 알고리즘으로 단순 전력 공유가 아닌 기기별 수요를 실시간 계산합니다.

[PPS 고속충전 지원]
삼성 갤럭시 Super Fast Charging 2.0을 위한 PPS(Programmable Power Supply) 지원.
갤럭시 S24 Ultra를 0→50% 기준 18분 충전 가능 (공식 측정값).

[Active Cooling Algorithm]
내장 온도 센서가 0.1초 간격으로 온도 모니터링. 이상 감지 시 출력을 단계적으로 낮춤.
완전 차단 전 3단계 경고 출력 저하를 거쳐 기기를 보호하는 독자 열 관리 시스템.

[접이식 플러그]
180도 완전 접이식 플러그 설계. 여행 시 파우치 안감 손상 방지.
""",
        "reviews_positive": [
            "노트북, 아이패드, 폰 세 개 동시 충전해도 속도가 거의 안 느려짐. 진짜임",
            "여행 다닐 때 멀티탭 필요 없어짐. 충전기 하나로 다 해결",
            "갤럭시 S24 충전이 기존 45W 정품 어댑터보다 오히려 빠른 것 같음",
            "발열이 거의 없음. 밤새 충전해도 따뜻한 정도",
            "플러그 접히는 게 소소하지만 진짜 편함. 가방에 찔리는 게 없음",
            "2년 써도 출력 저하 없음. 내구성 좋음",
        ],
        "reviews_negative": [
            "맥북프로 16인치 100W 연결하면 다른 포트들이 진짜 느려짐. 노트북 우선순위가 절대적",
            "두 포트 이상 쓰면 충전기 자체가 꽤 뜨거워짐 (화상 수준은 아니지만 신경 쓰임)",
            "USB-A 포트는 최대 18W라 구형 기기나 보조배터리 충전 느림",
            "5만원 가격이 부담. 기능은 인정하지만 일반 멀티탭 살 돈",
            "포트 전력 분배 설명이 박스에 너무 불친절하게 적혀있음",
            "초기 불량 케이스 몇 개 봄. 개봉하자마자 테스트 필수",
        ],
    },
    {
        "id": "P002",
        "name": "샤오미 33W GaN 초소형 2포트 충전기",
        "price": 17900,
        "category": "충전기",
        "rating": 4.3,
        "review_count": 4521,
        "weight": "62g",
        "icon": "🔌",
        "spec": {
            "최대출력": "33W",
            "포트구성": "C×1 + A×1",
            "GaN": "3세대",
            "무게": "62g",
            "크기": "42×42×28mm",
        },
        "detail_text": """
샤오미 33W GaN 충전기. 62g 초경량으로 손가락 세 개 크기의 미니 폼팩터.

[AutoSense 프로토콜 자동 선택]
연결된 기기를 자동 인식하여 QC3.0 / PD3.0 / AFC / FCP / Apple Fast Charge 중
최적 프로토콜을 자동 선택합니다. 사용자가 기기 종류를 몰라도 항상 최속 충전.

[스마트 완충 감지 & 트리클 충전]
기기가 완충되면 자동으로 '트리클 모드'로 전환. 과충전 방지 및 대기전력 0.1W 미만으로 최소화.
배터리 수명 보호에 최적화된 알고리즘 탑재.

[1.5m 낙하 테스트 통과]
PC+ABS 혼합 합성수지 케이스. 62g의 가벼운 무게에도 불구하고 내구성 강화 소재 적용.
""",
        "reviews_positive": [
            "이 크기에 33W라니 믿기지 않음. 폰 충전은 완벽",
            "출장용으로 최고. 가방 무게 차이 없는 수준",
            "아이폰 충전 속도가 기존 정품 충전기보다 빠르다고 느낌",
            "2만원 이하에 이 성능이면 가성비 최고",
            "심플한 디자인이 고급스러워 보임",
        ],
        "reviews_negative": [
            "맥북은 33W 한계로 충전이 거의 안 됨. 노트북 충전용으로 사면 안 됨",
            "두 포트 동시 사용하면 한 포트가 5W로 뚝 떨어짐. 동시 사용 사실상 불가",
            "발열이 예상보다 있음. 특히 여름철 더운 환경에서 신경 쓰임",
            "케이블 미포함. C-to-C 케이블 별도 구매 필수",
            "PD 지원이지만 맥북 연결하면 저전력 경고 뜸",
        ],
    },
    {
        "id": "P003",
        "name": "다이슨 쿨 퓨처 AM07 무날개 무선 선풍기",
        "price": 289000,
        "category": "선풍기",
        "rating": 4.8,
        "review_count": 892,
        "weight": "980g",
        "icon": "🌀",
        "spec": {
            "방식": "무날개 Air Multiplier",
            "소음": "최저 39dB",
            "풍량단계": "10단계",
            "배터리": "3000mAh",
            "사용시간": "최대 6시간",
            "무게": "980g",
        },
        "detail_text": """
다이슨 쿨 퓨처 AM07. Air Multiplier 기술로 날개 없이 안전하고 균일한 바람 생성.

[디지털 풍량 표시 LED 링]
기기 하단 베이스부에 원형 LED 링 탑재. 현재 풍량 단계를 색상과 밝기로 실시간 표시.
1-3단: 파란색, 4-7단: 초록색, 8-10단: 붉은 주황색으로 구분.
어두운 침실에서도 현재 설정을 즉시 파악 가능한 타사 미적용 독자 기능.

[점진적 풍량 감소 수면 알고리즘]
수면 모드 설정 시 단순 꺼짐 타이머가 아닌 '점진적 감소' 방식.
10단→7단→4단→2단→꺼짐 순서로 자동으로 풍량을 낮춰 수면 중 과냉각 방지.

[자이로스코프 자동 균형 보정]
내장 자이로스코프 센서가 바닥 기울기 0~5도 범위 내에서 모터 출력 자동 보정.
기울어진 바닥에서도 진동이나 소음 없이 동작.

[HEPA 필터 장착 슬롯 내장]
하단 흡기구에 별도 판매 HEPA 13등급 필터 삽입 슬롯 내장.
필터 장착 시 미세먼지 0.3μm 이상 99.97% 제거. 선풍기+공기청정기 겸용 가능.
""",
        "reviews_positive": [
            "날개 없어서 청소가 너무 편합니다. 먼지 낄 데가 없음",
            "1-3단 소음이 정말 없어요. 수면 중 틀어놔도 전혀 안 들림",
            "LED 풍량 표시가 침실에서 매우 실용적. 불 안 켜고 설정 확인 가능",
            "수면 모드 점진 감소 기능 덕에 새벽에 이불 걷어차는 일이 없어짐",
            "어린 자녀 있는 집에서 안전사고 걱정 없는 게 제일 큰 장점",
            "인테리어 소품 같은 디자인. 거실에 놓으면 방문객들이 선풍기인 줄 모름",
        ],
        "reviews_negative": [
            "29만원은 너무 비쌈. 기능 차이를 돈으로 합리화하기 어려운 가격",
            "최대 풍량이 일반 날개 선풍기보다 약함. 찜통더위엔 부족할 수 있음",
            "배터리 완충에 4시간. 유선 모드 없어서 긴 사용 시 계속 충전 필요",
            "HEPA 필터 별도 구매 가격이 3.5만원. 유지비 부담",
            "리모컨 분실 시 단품 구매가 매우 어려움",
            "공식 AS 센터 수가 적어 고장 시 택배 수리만 가능한 지역 많음",
        ],
    },
    {
        "id": "P004",
        "name": "보이어 16단계 DC인버터 초저소음 선풍기 BF-1290",
        "price": 67000,
        "category": "선풍기",
        "rating": 4.5,
        "review_count": 3241,
        "weight": "3.8kg",
        "icon": "🌀",
        "spec": {
            "방식": "날개형 (12인치 7날)",
            "소음": "최저 22dB",
            "풍량단계": "16단계",
            "소비전력": "2W~38W",
            "높이조절": "90~130cm 무단",
            "무게": "3.8kg",
        },
        "detail_text": """
보이어 BF-1290 DC 인버터 스탠드형 선풍기. 에너지 절약과 초저소음을 동시 달성.

[22dB 브러쉬리스 DC 인버터 모터]
일반 AC 모터 대비 소음 70% 저감 달성. 1단 22dB는 무반향 스튜디오 수준.
도서관 환경음(30dB)보다 조용한 수치. 수면 민감자, 신생아 가정, 재택근무자에 최적.

[풍량 메모리 & 설정 복귀 기능]
전원 차단 후 재가동 시 이전 설정(풍량 단계 + 동작 모드)이 자동 복원됩니다.
정전 후 복귀 시에도 동일하게 적용. 매번 재설정 불필요.

[3패턴 랜덤 자연풍 알고리즘]
'자연풍 모드'에서 강풍/약풍/정지의 3가지 패턴을 랜덤 조합하여 실제 자연 바람의 불규칙성 재현.
단순 ON/OFF 자연풍과 달리 인체 냉각 효율 향상.

[16단계 미세 풍량 조절]
일반 선풍기의 3단계 대비 16단계 초세밀 조절. 1단계씩 조절하며 최적 바람세기 탐색 가능.

[월 600원 전기요금]
1단 소비전력 2W. 하루 10시간 × 30일 사용 기준 전기요금 약 600원.
""",
        "reviews_positive": [
            "22dB이 진짜임. 수면 중에 틀고 자는데 바람 소리 외엔 아무것도 안 들림",
            "16단계 풍량이 과장인 줄 알았는데 진짜 미세하게 조절 가능. 내 최적 단계 찾음",
            "전기요금 걱정 없이 밤새 틀어놓을 수 있는 게 제일 큰 장점",
            "풍량 메모리 기능 때문에 매번 설정 안 해도 됨. 켜기만 하면 알아서 됨",
            "자연풍 모드가 타사 제품이랑 달리 진짜 자연스럽게 변화함",
            "5년 전 10만원 선풍기 버리고 이걸로 바꿨는데 훨씬 조용하고 시원함",
        ],
        "reviews_negative": [
            "리모컨 수신 거리가 짧아서 방 구석에서는 잘 안 됨. 5m 이상 거리에서 반응 불안정",
            "날개형이라 2주에 한 번 정도 청소 필요. 먼지 끼면 소음 증가함",
            "무단 높이조절 고정 나사가 처음엔 매우 뻑뻑함. 길들기까지 시간 걸림",
            "받침대 조립 설명서가 너무 불친절. 유튜브 검색 필요했음",
            "AS 기간 1년으로 짧다는 불만 많음. 2년 이상 쓰다 고장 나면 부품 구하기 어려움",
            "색상이 흰색 단일. 인테리어 다크톤 가정에서는 안 어울림",
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Gemini API 설정
# ─────────────────────────────────────────────────────────────────────────────
def get_api_key() -> str | None:
    if st.session_state.get("GOOGLE_API_KEY"):
        return st.session_state.GOOGLE_API_KEY
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return None


@st.cache_resource
def get_gemini_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-3.5-flash")


# ─────────────────────────────────────────────────────────────────────────────
# AI 핵심 함수
# ─────────────────────────────────────────────────────────────────────────────
def extract_search_intent(history: list, user_msg: str, model) -> dict:
    """대화 맥락에서 검색 의도 및 파라미터 JSON 추출"""
    history_str = "\n".join(
        f"{'사용자' if m['role'] == 'user' else 'AI'}: {m.get('content', '[상품 추천 결과]')}"
        for m in history[-6:]
    )

    prompt = f"""당신은 쿠팡 전자기기 검색 의도 분석 AI입니다.
아래 대화 맥락과 현재 메시지를 분석하여 검색 파라미터를 JSON으로 추출하세요.

[대화 맥락]
{history_str or "(첫 메시지)"}

[현재 사용자 메시지]
{user_msg}

JSON 형식으로만 응답 (마크다운 코드블록 없이):
{{
    "is_product_request": true 또는 false,
    "category": "아래 목록 중 정확히 하나만 선택",
    "search_keywords": ["키워드1", "키워드2"],
    "max_price": 숫자 또는 null,
    "min_price": 숫자 또는 null,
    "required_features": ["GaN", "무선", "저소음" 등],
    "user_intent_summary": "사용자 의도 한 줄 요약"
}}

[category 선택 규칙 - 반드시 준수]
- "충전기": 벽 콘센트에 꽂는 전원 어댑터/충전 어댑터 (GaN 충전기, 멀티포트 충전기 등)
- "선풍기": 바람을 내는 선풍기, 서큘레이터
- "보조배터리": 휴대용 외장 배터리, 파워뱅크 (충전기와 완전히 다른 제품)
- "충전케이블": USB 케이블, C타입 케이블, 라이트닝 케이블 등 선(wire) 형태의 케이블
- "이어폰": 이어폰, 헤드폰, 이어버드
- "노트북": 노트북, 랩톱
- "기타": 위 어디에도 해당하지 않는 전자기기

is_product_request는 상품 검색/추천/재검색/조건 변경을 원할 때만 true."""

    try:
        resp = model.generate_content(prompt)
        text = re.sub(r"```json\n?|\n?```", "", resp.text).strip()
        return json.loads(text)
    except Exception:
        return {"is_product_request": False, "user_intent_summary": user_msg}


# 현재 Mock DB에 실제로 존재하는 카테고리
_DB_CATEGORIES = {"충전기", "선풍기"}


def search_products(context: dict) -> tuple[list, bool]:
    """저장된 검색 컨텍스트 기반 상품 필터링.
    반환값: (상품 리스트, DB에 해당 카테고리가 있는지 여부)
    """
    cat = context.get("category", "기타").lower()

    # DB에 없는 카테고리는 즉시 없음 처리
    if cat not in ("충전기", "선풍기", "기타", ""):
        return [], False

    results = MOCK_PRODUCTS.copy()

    if cat == "충전기":
        results = [p for p in results if p["category"] == "충전기"]
    elif cat == "선풍기":
        results = [p for p in results if p["category"] == "선풍기"]
    # "기타" / ""는 전체 DB에서 키워드로만 탐색

    if max_p := context.get("max_price"):
        results = [p for p in results if p["price"] <= max_p]
    if min_p := context.get("min_price"):
        results = [p for p in results if p["price"] >= min_p]

    keywords = context.get("search_keywords", [])
    if keywords:
        kw_hit = []
        for p in results:
            for kw in keywords:
                if kw.lower() in p["name"].lower() or kw.lower() in p["detail_text"].lower():
                    if p not in kw_hit:
                        kw_hit.append(p)
        if kw_hit:
            results = kw_hit

    features = context.get("required_features", [])
    if features:
        feat_hit = [
            p for p in results
            if any(
                f.lower() in p["detail_text"].lower() or f.lower() in p["name"].lower()
                for f in features
            )
        ]
        if feat_hit:
            results = feat_hit

    return results[:3], True


def analyze_unique_features(product: dict, model) -> str:
    """AI로 상품의 독특하고 차별화된 기능 분석"""
    prompt = f"""전자기기 전문 분석가로서, 아래 상품 상세 텍스트에서
이 제품만의 독특하고 차별화된 기능을 2~3가지 찾아내세요.
일반 스펙(무게, 크기) 제외, 진짜 독특한 기술/설계만 선택하세요.

[상품명] {product['name']}
[상세 텍스트]
{product['detail_text']}

형식 (이 형식 그대로만 응답):
• [기능명]: 한 줄 설명
• [기능명]: 한 줄 설명
• [기능명]: 한 줄 설명"""

    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return "• 분석 오류: AI 분석 중 오류가 발생했습니다."


def analyze_reviews(product: dict, model) -> dict:
    """AI로 리뷰에서 광고성 제거 후 진짜 장단점 추출"""
    pos = "\n".join(f"- {r}" for r in product["reviews_positive"])
    neg = "\n".join(f"- {r}" for r in product["reviews_negative"])

    prompt = f"""소비자 리뷰 전문 분석가로서, 아래 실제 구매 리뷰를 분석해주세요.
광고성 내용을 걸러내고 반드시 알아야 할 진짜 장단점을 추출하세요.

[상품명] {product['name']}
[긍정 리뷰]
{pos}
[부정 리뷰]
{neg}

JSON 형식으로만 응답 (마크다운 없이):
{{
    "real_pros": ["장점1 (구체적으로)", "장점2", "장점3"],
    "real_cons": ["치명적 단점1 (구체적으로)", "단점2", "단점3"],
    "recommendation": "이런 분께 추천 / 이런 분은 비추천 (한 줄)"
}}"""

    try:
        text = re.sub(r"```json\n?|\n?```", "", model.generate_content(prompt).text).strip()
        return json.loads(text)
    except Exception:
        return {
            "real_pros": ["리뷰 분석 오류"],
            "real_cons": ["리뷰 분석 오류"],
            "recommendation": "분석 오류",
        }


def generate_not_found_response(intent: dict, model) -> str:
    """DB에 없는 카테고리 요청 시 없다고 안내하고 유사 상품 제안"""
    prompt = f"""쿠팡 AI 쇼핑 어시스턴트입니다.
사용자가 '{intent.get('category', '해당 상품')}'을(를) 찾고 있지만,
현재 DB에는 '충전기(GaN 멀티충전기 2종)'와 '선풍기(DC인버터 선풍기 2종)'만 있습니다.

사용자 요청: {intent.get('user_intent_summary', '')}

다음 내용을 포함해 친절하고 자연스럽게 한국어로 3~4문장 응답하세요:
1. 요청하신 '{intent.get('category', '상품')}'은 현재 준비된 상품이 없다는 점을 솔직하게 안내
2. 현재 DB에서 가장 관련이 있을 수 있는 상품 카테고리(충전기 또는 선풍기)를 자연스럽게 언급
3. 원하신다면 해당 카테고리를 안내해 드릴 수 있다고 제안"""

    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        cat = intent.get("category", "해당 상품")
        return (
            f"죄송합니다, '{cat}'은(는) 현재 준비된 상품이 없어요 😅\n\n"
            "현재 DB에는 **GaN 충전기**와 **DC인버터 선풍기** 2종씩 있습니다. "
            "혹시 이 중에서 찾아드릴까요?"
        )


def generate_intro(intent: dict, products: list, model) -> str:
    """자연스러운 추천 인트로 메시지 생성"""
    names = ", ".join(f"{p['name']}(₩{p['price']:,})" for p in products)
    prompt = f"""친근한 쿠팡 AI 어시스턴트로서, 사용자 요청에 맞는 상품을 찾았음을
자연스럽게 2~3문장으로 소개하세요. 이모지 적절히 사용.

사용자 요청: {intent.get('user_intent_summary', '')}
찾은 상품: {names}

아래에 상세 카드가 표시되므로 간단한 소개 멘트만 작성."""

    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return f"요청하신 조건에 맞는 상품 {len(products)}개를 찾았어요! 아래에서 확인해보세요 🛒"


def generate_chat_response(history: list, user_msg: str, model) -> str:
    """일반 대화 응답 생성"""
    history_str = "\n".join(
        f"{'사용자' if m['role'] == 'user' else 'AI'}: {m.get('content', '[상품 추천]')}"
        for m in history[-6:]
    )
    prompt = f"""쿠팡 AI 쇼핑 어시스턴트로서 친절하게 응답하세요.
전자기기 추천과 쇼핑 관련 질문을 도와드립니다.

[대화 기록]
{history_str}

[사용자]
{user_msg}

한국어로 자연스럽고 도움이 되는 응답을."""

    try:
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        return f"죄송합니다, 오류가 발생했습니다: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# UI 컴포넌트
# ─────────────────────────────────────────────────────────────────────────────
def render_product_card(data: dict):
    """상품 카드 렌더링 (expander 형태의 특이 기능 + 리뷰 분석 포함)"""
    p = data["product"]
    unique_features: str = data.get("unique_features", "")
    review: dict = data.get("review_analysis", {})

    with st.container(border=True):
        col_name, col_price = st.columns([3, 1])
        with col_name:
            st.markdown(f"### {p['icon']} {p['name']}")
        with col_price:
            st.markdown(
                f"<h3 style='color:#e44d26; text-align:right;'>₩{p['price']:,}</h3>",
                unsafe_allow_html=True,
            )

        stars = "⭐" * int(p["rating"])
        st.caption(f"{stars} **{p['rating']}** · 리뷰 {p['review_count']:,}개 · {p['weight']}")

        # 쿠팡 검색 링크 (상품명으로 검색 결과 페이지 이동)
        coupang_url = (
            "https://www.coupang.com/np/search?q="
            + urllib.parse.quote(p["name"])
        )
        st.link_button("🛒 쿠팡에서 확인하기", coupang_url, use_container_width=True)

        # 스펙 표
        spec_items = list(p["spec"].items())
        cols = st.columns(len(spec_items))
        for col, (k, v) in zip(cols, spec_items):
            col.metric(k, v)

        st.divider()

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            with st.expander("✨ AI 발굴 특이 기능"):
                st.markdown(unique_features or "분석 데이터 없음")

        with col_exp2:
            with st.expander("📊 리뷰 기반 진짜 장단점"):
                pros = review.get("real_pros", [])
                cons = review.get("real_cons", [])
                rec = review.get("recommendation", "")

                st.markdown("**👍 진짜 장점**")
                for item in pros:
                    if item:
                        st.markdown(f"✅ {item}")

                st.markdown("**👎 주의할 단점**")
                for item in cons:
                    if item:
                        st.markdown(f"❌ {item}")

                if rec:
                    st.info(f"💡 {rec}")


# ─────────────────────────────────────────────────────────────────────────────
# 메인 앱
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] { text-align: center; }
        div[data-testid="stMetric"] label { font-size: 0.75rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 🛒 쿠팡 AI 전자기기 추천")
    st.caption("자연어로 원하는 전자기기를 말씀해주세요. AI가 특이 기능과 리뷰까지 분석합니다.")

    # ── 사이드바 ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        api_input = st.text_input(
            "Google API 키",
            type="password",
            value=st.session_state.get("GOOGLE_API_KEY", ""),
            help="Google AI Studio (aistudio.google.com) 에서 무료 발급",
        )
        if api_input:
            st.session_state.GOOGLE_API_KEY = api_input

        st.markdown("---")
        st.markdown("### 💡 예시 질문 (클릭)")
        examples = [
            "5만원 이하 GaN 충전기 추천해줘",
            "수면할 때 쓸 조용한 선풍기",
            "노트북이랑 폰 동시 충전 가능한 거",
            "방금 추천 중에 더 가벼운 거 없어?",
            "2만원 이하로 낮춰서 다시 보여줘",
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                st.session_state["_quick_input"] = ex
                st.rerun()

        st.markdown("---")
        st.markdown("### 📦 모의 상품 DB")
        st.markdown("- 충전기: UGREEN 100W, 샤오미 33W\n- 선풍기: 다이슨 AM07, 보이어 BF-1290")

        if st.button("🗑️ 대화 초기화", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.session_state.search_context = {}
            st.rerun()

        st.caption("⚡ Powered by Gemini 3.5 Flash")

    # ── Session State 초기화 ──────────────────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "search_context" not in st.session_state:
        st.session_state.search_context = {}

    # ── API 키 확인 ────────────────────────────────────────────────────────────
    api_key = get_api_key()
    if not api_key:
        st.warning("⚠️ 왼쪽 사이드바에서 Google API 키를 입력해주세요.")
        st.info("🔑 Google AI Studio (aistudio.google.com) 에서 무료로 발급 가능합니다.")
        return

    model = get_gemini_model(api_key)

    # ── 웰컴 메시지 (첫 방문 시) ──────────────────────────────────────────────
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                """안녕하세요! 저는 **쿠팡 AI 쇼핑 어시스턴트**입니다 🛒

원하시는 전자기기를 편하게 말씀해주세요.
추천 이후에도 *"더 저렴한 걸로"*, *"더 가벼운 거"*, *"2만원 이하로 다시"* 처럼
대화를 이어가며 조건을 좁혀나갈 수 있어요! ✨

> **현재 DB:** GaN 멀티충전기 2종 / DC인버터 선풍기 2종"""
            )

    # ── 채팅 기록 렌더링 ──────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "products":
                st.markdown(msg["intro"])
                for pd in msg["products"]:
                    render_product_card(pd)
            else:
                st.markdown(msg["content"])

    # ── 예시 버튼 입력 처리 ───────────────────────────────────────────────────
    quick = st.session_state.pop("_quick_input", None)

    # ── 채팅 입력 ─────────────────────────────────────────────────────────────
    user_input = st.chat_input("원하는 전자기기를 자유롭게 말씀해주세요...") or quick

    if not user_input:
        return

    # 사용자 메시지 표시 & 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 처리
    with st.chat_message("assistant"):
        with st.spinner("의도 분석 중..."):
            intent = extract_search_intent(
                st.session_state.messages[:-1], user_input, model
            )

        if intent.get("is_product_request"):
            # 이전 컨텍스트와 병합 (대화 연속성 유지)
            for k, v in intent.items():
                if v and k not in ("is_product_request", "user_intent_summary"):
                    st.session_state.search_context[k] = v

            products, category_in_db = search_products(st.session_state.search_context)

            if not category_in_db:
                # DB에 아예 없는 카테고리 요청
                reply = generate_not_found_response(intent, model)
                # 컨텍스트 오염 방지: 없는 카테고리는 저장하지 않음
                st.session_state.search_context.pop("category", None)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            elif not products:
                reply = "😅 조건에 맞는 상품을 찾지 못했어요. 가격 조건을 올리거나 필터를 줄여보시겠어요?"
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                with st.spinner(f"🤖 {len(products)}개 상품 AI 분석 중 (특이 기능 + 리뷰)..."):
                    analyses = []
                    for p in products:
                        analyses.append(
                            {
                                "unique_features": analyze_unique_features(p, model),
                                "review_analysis": analyze_reviews(p, model),
                            }
                        )

                intro = generate_intro(intent, products, model)
                st.markdown(intro)

                saved_products = []
                for p, a in zip(products, analyses):
                    pd = {"product": p, **a}
                    render_product_card(pd)
                    saved_products.append(pd)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "type": "products",
                        "intro": intro,
                        "products": saved_products,
                    }
                )
        else:
            reply = generate_chat_response(
                st.session_state.messages[:-1], user_input, model
            )
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
