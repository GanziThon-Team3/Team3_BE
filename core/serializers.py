from rest_framework import serializers

# 약품 하나의 구조와 타입 정의
class DrugItemSerializer(serializers.Serializer):
    drug_name = serializers.CharField(max_length=200, help_text="처방 약품 제품명") 
    user_daily_dose = serializers.FloatField(min_value=0.0, help_text="처방 받은 1일 투약량")

# 사용자 입력 데이터 구조와 타입 정의
class ComparisonInputSerializer(serializers.Serializer):
    
    # DB 조회 key로 사용됨 ->TreatmentStandard 모델과 일치해야 함
    dept = serializers.CharField(max_length=20, help_text="진료과목 이름") 
    age_group = serializers.CharField(max_length=50, help_text="연령대")
    disease = serializers.CharField(max_length=200, help_text="주상병") 
    
    # 평균값 DB와 비교할 사용자 입력값
    user_fee = serializers.IntegerField(min_value=0, help_text="사용자 지불 본인부담금")
    user_days = serializers.IntegerField(min_value=0, help_text="사용자 처방 일수") 
    
    # 비용 비교 시 사용
    is_saturday = serializers.BooleanField(default=False, help_text="토요일 진료 여부") 
    is_night = serializers.BooleanField(default=False, help_text="야간 진료 여부")
    
    # 약품 정보 리스트, DrugItemSerializer를 자식으로 가지는 리스트 필드
    drug_items = serializers.ListField(
        child=DrugItemSerializer(), 
        required=False, # 처방 약품이 없을 경우 대비
        allow_empty=True, # 빈 리스트도 허용
        help_text="처방 약품 목록"
    )