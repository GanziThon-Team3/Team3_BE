# API 명세서 (Frontend용)
---
## 📖 목차
1. [기본 정보](#📌-기본-정보)
2. [AI 건강정보](#😈​-​AI-건강정보)
3. [통계 결과창](#🤡-통계-결과창)

---
## 📌 기본 정보
- **Base URL:** `kikoky.shop`
- **Content-Type:** `application/json`
- **인증:** 없음 (로그인 없이 사용 가능)

---

## 😈​​ AI 건강정보

- **URL:** `/ai_info/`
- **Method:** `POST`
- **설명** 
`disease`: 질병 코드(대문자, 숫자만 허용)
`drug_name`: 약품 이름

- **Request Body:**
```
{
  "disease”:”세파피린정”,    "drug_name": "세파피린정"
}
```

- **Response:**
```
{
  ”disease_info”:”STR”,
”drug_info”:”STR”,
”health_tip”:”STR”
}
```
**Status Codes**

- `201 Created` 성공

- `400 Bad Request` 필수값 누락

- `500 Internal Server Error` 서버 오류

## 🤡​​​ 통계 결과창

- **URL:** `/compare/`
- **Method:** `POST`
- **요청 설명** 
`dept`: 진료 과목  
`age_group`: 연령대(미성년자/성인/고령자)  
`disease`: 질병 코드(대문자, 숫자만 허용)  
`user_fee`: 사용자 부담금, 정수형  
`is_saturday`: 토요일/공휴일 여부(false/true)  
`is_night`: 야간 여부(false/ture)  


`drug_items`: 약품 객체 리스트  
`drug_name`: 약품 이름  
`user_once_dose`: 투약량, 실수형  
`user_daily_times`: 횟수, 실수형  
`user_days`: 일수, 실수형  

- **Request Body:**
```
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
    …
    }
    …
    ]
}
```

- **Response:**
```
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
    …
    }
    …
    ]
}
}
```
- **응답 설명** 
`comparision_results`: 비교 결과 객체  


`treatment_fee`: 진료비 비교 객체  
`sample_count`: 비교 표본 수(정수형)  
`avg_fee`: 평균 진료비(실수형)  
`user_fee`: 사용자 지불 비용(정수형)  
`difference_percent`: 평균 보다 얼마나 더 지불했는지(퍼센트, 실수형)  
*9999.0일 경우 평균이 0이고, 사용자 지불이 있는 경우  
`level_text`: 라벨링에 사용  


`treatment_days`: 처방일수 비교 객체  
`sample_count`: 비교 표본 수(정수형)  
`avg_days`: 평균 처방 일수(실수형)  
`user_days`: 사용자 입력 처방 일수(정수형)  
`difference_percent`: 평균 보다 얼마나 더 처방 받았는지(퍼센트, 실수형)  
`level_text`: 라벨링에 사용  


`drug_items_comparison`: 약품별 비교 객체 리스트  
`drug_name`: 약품 이름  
`sample_count`: 비교 표본 수(정수형)  
`avg_total_dose`: 평균 총 투약량(실수형)  
`user_total_dose`: 사용자 입력 총 투약량(실수형)  
`difference_percent`: 평균 보다 얼마나 더 처방 받았는지(퍼센트, 실수형)  
`level_text`: 라벨링에 사용

**Status Codes**

- `201 Created` 성공

- `400 Bad Request` 필수값 누락

- `500 Internal Server Error` 서버 오류
