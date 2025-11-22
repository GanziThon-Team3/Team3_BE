# API 명세서
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


&nbsp;&nbsp;`disease`: 질병 코드(대문자, 숫자만 허용)


&nbsp;&nbsp;`drug_name`: 약품 이름


<br>

- **Request Body :**
```
{
  "disease”:”AO62”,    "drug_name": "세파피린정"
}
```
<br>

- **Response :**
```
{
  ”disease_info”:”STR”,
”drug_info”:”STR”,
”health_tip”:”STR”
}
```
<br>

**Status Codes**

- `201 Created` 성공

- `400 Bad Request` 필수값 누락

- `500 Internal Server Error` 서버 오류

---
## 🤡​​​ 통계 결과창

<br>

**1. 질병 검색**
- **URL:** `/search/diseases/?query=[사용자 입력 문자열]`
- **Method:** `GET`
- **요청 설명:** 사용자가 질병 입력창에 입력한 문자열을 ‘query’라는 이름의 쿼리 파라미터로 보냄 


<br>

- **Response :**
```
[
    {
    “code”: “J00”,
    “name": "감염성 비염”
    },
    {
    "code": "J300",
    "name": "혈관운동성 비염"
    },
    …
]
```
<br>

- **응답 설명** 

&nbsp;&nbsp;- 리스트(쿼리셋)로 응답  
&nbsp;&nbsp;`code`: 질병 코드(백엔드에 넘겨줘야 할 것)  
&nbsp;&nbsp;`name`: 질병 이름(사용자가 질병 코드를 선택할 수 있도록 보여주는 것)  

&nbsp;&nbsp;- 쿼리 파라미터가 없거나, 한글자거나, 검색 결과가 없는 경우
&nbsp;&nbsp;→ [ ](빈 쿼리셋) 반환

<br>

**Status Codes**

- `201 Created` 성공

- `400 Bad Request` 필수값 누락

- `500 Internal Server Error` 서버 오류


<br><br>

**2. 결과 보기**
- **URL:** `/compare/`
- **Method:** `POST`
- **요청 설명** 


&nbsp;&nbsp;`dept`: 진료 과목  


&nbsp;&nbsp;`age_group`: 연령대(미성년자/성인/고령자)  


&nbsp;&nbsp;`disease`: 질병 코드(대문자, 숫자만 허용)  


&nbsp;&nbsp;`user_fee`: 사용자 부담금, 정수형  


&nbsp;&nbsp;`is_saturday`: 토요일/공휴일 여부(false/true)  


&nbsp;&nbsp;`is_night`: 야간 여부(false/ture)  


&nbsp;&nbsp;· · ·

&nbsp;&nbsp;`drug_items`: 약품 객체 리스트  


&nbsp;&nbsp;`drug_name`: 약품 이름  


&nbsp;&nbsp;`user_once_dose`: 투약량, 실수형  


&nbsp;&nbsp;`user_daily_times`: 횟수, 실수형  


&nbsp;&nbsp;`user_days`: 일수, 실수형  

<br>

- **Request Body :**
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
<br>

- **Response :**
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
<br>

- **응답 설명** 


&nbsp;&nbsp;`comparision_results`: 비교 결과 객체  


&nbsp;&nbsp;· · ·

&nbsp;&nbsp;`treatment_fee`: 진료비 비교 객체  


&nbsp;&nbsp;`sample_count`: 비교 표본 수(정수형)  


&nbsp;&nbsp;`avg_fee`: 평균 진료비(실수형)  


&nbsp;&nbsp;`user_fee`: 사용자 지불 비용(정수형)  


&nbsp;&nbsp;`difference_percent`: 평균 보다 얼마나 더 지불했는지(퍼센트, 실수형)  
&nbsp;&nbsp;*9999.0일 경우 평균이 0이고, 사용자 지불이 있는 경우  


&nbsp;&nbsp;`level_text`: 라벨링에 사용  

&nbsp;&nbsp;· · ·


&nbsp;&nbsp;`treatment_days`: 처방일수 비교 객체  


&nbsp;&nbsp;`sample_count`: 비교 표본 수(정수형)  


&nbsp;&nbsp;`avg_days`: 평균 처방 일수(실수형)  


&nbsp;&nbsp;`user_days`: 사용자 입력 처방 일수(정수형)  


&nbsp;&nbsp;`difference_percent`: 평균 보다 얼마나 더 처방 받았는지(퍼센트, 실수형)  


&nbsp;&nbsp;`level_text`: 라벨링에 사용  


&nbsp;&nbsp;· · ·

&nbsp;&nbsp;`drug_items_comparison`: 약품별 비교 객체 리스트  


&nbsp;&nbsp;`drug_name`: 약품 이름  


&nbsp;&nbsp;`sample_count`: 비교 표본 수(정수형)  


&nbsp;&nbsp;`avg_total_dose`: 평균 총 투약량(실수형)  


&nbsp;&nbsp;`user_total_dose`: 사용자 입력 총 투약량(실수형)  


&nbsp;&nbsp;`difference_percent`: 평균 보다 얼마나 더 처방 받았는지(퍼센트, 실수형)  


&nbsp;&nbsp;`level_text`: 라벨링에 사용


<br>

**Status Codes**

- `201 Created` 성공

- `400 Bad Request` 필수값 누락

- `500 Internal Server Error` 서버 오류
