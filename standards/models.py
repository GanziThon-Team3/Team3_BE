from django.db import models

# 진료내역 기준 통계
class TreatmentStandard(models.Model):
    # 기준 필드
    # db_index: 해당 필드에 데이터베이스 인덱스를 생성하도록 지시 -> 해당 필드 기준으로 하는 데이터 탐색/필터링 속도 향상
    disease = models.CharField(max_length=200, db_index=True, help_text="주상병 이름")
    dept = models.CharField(max_length=20, db_index=True, help_text="진료과목 이름")
    age_group = models.CharField(max_length=50, verbose_name='연령대')
    
    # 통계치 필드
    avg_fee = models.IntegerField(help_text="그룹별 평균 심결본인부담금")
    avg_days = models.FloatField(help_text="그룹별 평균 총 처방일수") 

    class Meta:
        verbose_name = "진료내역 기준 통계"
        # 기준 중복 저장 방지
        unique_together = ('disease', 'dept', 'age_group')

# 의약품처방 기준 통계
class DrugStandard(models.Model):
    # 기준 필드
    drug_name = models.CharField(max_length=200, db_index=True, help_text="약품 제품명")
    age_group = models.CharField(max_length=50, verbose_name='연령대')
    
    # 통계치 필드
    avg_daily_dose = models.FloatField(help_text="그룹별 평균 1일 투약량") 

    class Meta:
        verbose_name = "의약품처방 기준 통계"
        unique_together = ('drug_name', 'age_group')