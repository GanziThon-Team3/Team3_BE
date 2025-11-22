# 📚 API 명세서

---

## 📖 목차

1. 기본 정보
2. 질병 검색
3. 통계 결과
4. AI 건강정보
5. 추가 질의 응답

---

## 1. 기본 정보

- **Base URL:** `kikoky.shop`
- **Content-Type:** `application/json`
- **인증:** 없음 (로그인 없이 사용 가능)

---

## 2. 질병 검색

- **URL:** `/search/diseases/?query=[사용자 입력 문자열]`
- **Method:** `GET`

### 📌 요청 설명

사용자가 질병 입력창에 입력한 문자열을 `query` 파라미터로 전달합니다.

**예시 요청**

```
GET /search/diseases/?query=비염

```

### 📌 Response 예시

```json
[
  {
    "code": "J00",
    "name": "감염성 비염"
  },
  {
    "code": "J300",
    "name": "혈관운동성 비염"
  }
]

```

### 📌 응답 설명

- 응답은 리스트 형태
    - `code`: 질병 코드
    - `name`: 질병 이름
- 다음 경우 빈 리스트 반환 (`[]`)
    - query 없음
    - 한 글자 입력
    - 검색 결과 없음

### 📌 Status Codes

- `200 OK`
- `400 Bad Request`
- `500 Internal Server Error`

---

## 3. 통계 결과

### ✔ 3-1. 결과 보기

- **URL:** `/compare/`
- **Method:** `POST`

### 📌 요청 설명

사용자의 진료비·처방일수·투약량을 통계 기준과 비교합니다.

### 공통 필드

| 필드 | 설명 |
| --- | --- |
| dept | 진료 과목 |
| age_group | 연령대(미성년자/성인/고령자) |
| disease | 질병 코드 |
| user_fee | 사용자 부담금 |
| is_saturday | 토요일/공휴일 여부 |
| is_night | 야간 여부 |

### drug_items 리스트

| 필드 | 설명 |
| --- | --- |
| drug_name | 약품 이름 |
| user_once_dose | 1회 투약량 |
| user_daily_times | 일일 투약 횟수 |
| user_days | 처방 일수 |

### 📌 Request Body 예시

```json
{
  "dept": "내과",
  "age_group": "성인",
  "disease": "A062",
  "user_fee": 15000,
  "is_saturday": false,
  "is_night": false,
  "drug_items": [
    {
      "drug_name": "세파피린정",
      "user_once_dose": 3.0,
      "user_daily_times": 3.0,
      "user_days": 3
    },
    {
      "drug_name": "세토펜현탁액",
      "user_once_dose": 2.5,
      "user_daily_times": 3.0,
      "user_days": 3
    }
  ]
}

```

### 📌 Response 예시

```json
{
  "comparison_results": {
    "treatment_fee": {
      "sample_count": 16,
      "avg_fee": 22629,
      "user_fee": 15000,
      "difference_percent": -33.71,
      "level_text": "낮음"
    },
    "treatment_days": {
      "sample_count": 16,
      "avg_days": 3.9,
      "user_days": 5,
      "difference_percent": 29.03,
      "level_text": "높음"
    },
    "drug_items_comparison": [
      {
        "drug_name": "세파피린정",
        "sample_count": 3357,
        "avg_total_dose": 12.75,
        "user_total_dose": 27.0,
        "difference_percent": 111.72,
        "level_text": "높음"
      },
      {
        "drug_name": "세토펜현탁액",
        "sample_count": 1240,
        "avg_total_dose": 10.0,
        "user_total_dose": 22.5,
        "difference_percent": 125.0,
        "level_text": "높음"
      }
    ]
  }
}

```

### 📌 Status Codes

- `200 OK`
- `400 Bad Request`
- `500 Internal Server Error`

---

## 4. AI 건강정보

- **URL:** `/ai_info/`
- **Method:** `POST`

### 📌 설명

입력된 **질병 코드 + 약품명**을 기반으로
Langgraph에 연결된 node 순서대로
PubMed, Scholar, Cochrane, ClinicalTrials에서 에서 질병정보를, 
FAD open database에서 약정보를 가져와
LLM으로 최종 요약 제공한다.

- 질병 설명 (`disease_info`) : 질병의 개요, 주요 증상을 1~2문장 이내로 요약 제공
- 약품 설명 (`drug_info`) : 약의 성분, 용도, 주의사항을1~2문장 이내로 요약 제공
- 건강 관리 팁 (`health_tip`) : 질병에 대한 생활습관(식단/운동/수면 등), 간단한 치료/관리 내용을 4~6문장 정도로 요약 제공을 AI가 생성합니다.
    

### 📌 Request Body 예시

```json
{
  "disease": "A062",
  "drug_name": "세토펜현탁액"
}

```

### 📌 Response 예시

```json
{
  "disease_info": "아메바성 비이질성 결장염은 ...",
  "drug_info": "세토펜현탁액은 ...",
  "health_tip": "1. 감염 예방을 위해 손 씻기..."
}

```

### 📌 Status Codes

- `200 OK`
- `400 Bad Request`
- `500 Internal Server Error`

---

## 5. 추가 질의 응답

> /ai_info/ 결과를 기반으로 사용자가 “추가 질문”을 입력하면,
> 
> 
> 그 질문에 대한 AI 답변을 반환하는 API입니다.
> 
- **URL:** `/ai_answer/`
- **Method:** `POST`
- **Content-Type:** `application/json`

### 📌 요청 설명

- `question` 한 가지만 전송하면 됨.
- 백엔드는 직전 질병/약품 정보를 자동으로 활용해 답변 생성.

### 📌 Request Body 예시

```json
{
  "question": "타이레놀 주의사항에 대해 더 자세히 알려줘"
}

```

### 📌 Response 예시

```json
{
  "result": "타이레놀(아세트아미노펜) 주의사항:\n- 간 손상 위험이 있어 하루 최대 4,000mg 이하 복용...\n- 음주 후 복용 시 간독성 증가...\n..."
}

```

### 📌 응답 설명

- `result`: 사용자의 질문에 AI가 생성한 텍스트 전체

### 📌 Status Codes

- `200 OK`
- `400 Bad Request`
- `500 Internal Server Error`
