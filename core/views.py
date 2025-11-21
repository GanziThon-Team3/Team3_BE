from rest_framework.views import APIView 
from rest_framework.response import Response
from standards.models import TreatmentStandard, DrugStandard, DiseaseMapping
from .serializers import ComparisonInputSerializer, DiseaseSearchSerializer
from .ai_graph import graph
from rest_framework import status
from .ai_tool_call import ai_answer
from rest_framework import generics
from rest_framework.exceptions import ValidationError

# 팀 상의 후 비율과 텍스트 수정 예정
def _get_comparison_level(diff_percent):
    if diff_percent > 10.0: # +10% 초과
        return "높음"
    elif diff_percent < -10.0: # -10% 미만
        return "낮음"
    else: # 그 외(±10% 이내)
        return "평균"    
    return "판별불가"

# 'compare/' 엔드포인트의 POST 요청 처리 클래스
class ComparisonView(APIView):
    # POST 요청시 실행되는 메인 함수
    def post(self, request):
        serializer = ComparisonInputSerializer(data=request.data)
        # Serializer의 유효성 검사 -> 실패 시 에러 메시지를 400 코드로 반환
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # 파이썬 딕셔너리로 타입 변환 및 정제까지 완료된 데이터
        validated_data = serializer.validated_data
        
        # 핵심 비교 로직을 수행하는 내부 함수 호출
        # 사용자 입력 데이터는 DB 저장 없이 이 함수 내에서만 사용됨
        comparison_results = self._perform_comparison(validated_data) 
        
        # 건강 정보 추천 로직 추가

        return Response({
            "comparison_results": comparison_results, 
            # 여기에 건강 정보 추천 결과값 추가
        }, status=200)

    # 실제 비교 로직 함수
    def _perform_comparison(self, data):
        results = {} # 최종 결과 딕셔너리
        
        max_user_days = 0
        for item in data.get('drug_items', []):
            # 약품 항목에서 처방일수 추출
            current_days = float(item['user_days'])
            if current_days > max_user_days:
                max_user_days = current_days

        age_group = data['age_group']
        disease = data['disease']
        dept = data['dept']
        user_fee = data['user_fee']
        user_days = max_user_days
        is_saturday = data['is_saturday']
        is_night = data['is_night']
        # drug_items는 선택적 필드 -> 없으면 빈 리스트 반환
        drug_items = data.get('drug_items', [])

        # ----- 진료내역 DB 비교 로직
        try: # 주상병, 진료과목, 연령대를 기준으로 TreatmentStandard DB 조회 -> 실패 시 예외처리로
            treatment_standard = TreatmentStandard.objects.get(
                disease=disease, 
                dept=dept, 
                age_group=age_group
            )
            avg_fee = treatment_standard.avg_fee
            avg_days = treatment_standard.avg_days
            sample_count = treatment_standard.sample_count

            # 비용 비교
            # 토요일/야간 -> user_fee를 1.3으로 나눠 일반 비용으로 변환
            user_fee = user_fee / 1.3 if (is_saturday or is_night) else user_fee    
            # (사용자 입력 비용 - 평균비용) / 평균비용 * 100 -> 0 나누기 방지 필요
            if avg_fee > 0:
                fee_diff_percent = ((user_fee - avg_fee) / avg_fee) * 100
            elif user_fee > 0:
                fee_diff_percent = 9999.0 # 평균은 0인데 사용자가 비용을 지불한 경우 -> 압도적으로 높음
            else:
                fee_diff_percent = 0 # 평균도 0이고 사용자도 0인 경우 -> 차이 없음
            results['treatment_fee'] = {
                'sample_count': sample_count,
                'avg_fee': round(avg_fee), # DB 평균 비용(반올림)
                'user_fee': user_fee, # 사용자 입력 비용
                'difference_percent': round(fee_diff_percent, 2), 
                'level_text': _get_comparison_level(fee_diff_percent), 
            }

            # 처방일수 비교
            # (사용자 입력 일수 - 평균일수) / 평균일수 * 100
            if avg_days > 0:
                days_diff_percent = ((user_days - avg_days) / avg_days) * 100
            elif user_days > 0:
                days_diff_percent = 9999.0
            else:
                days_diff_percent = 0
            results['treatment_days'] = {
                'sample_count': sample_count,
                'avg_days': round(avg_days, 1), # DB 평균 일수
                'user_days': user_days, # 사용자 입력 일수
                'difference_percent': round(days_diff_percent, 2),
                'level_text': _get_comparison_level(days_diff_percent), 
            }  
        except TreatmentStandard.DoesNotExist: 
            results['treatment_error'] = {"message": "해당 조건의 진료내역 기준 데이터가 DB에 없습니다."}
            
        # ----- 의약품 DB 비교 로직
        drug_comparison_results = [] # 약품별 비교 결과 전체 리스트

        for item in drug_items:
            drug_name = item['drug_name']
            user_once_dose = item['user_once_dose']
            user_daily_times = item['user_daily_times']
            user_days = item['user_days']

            tmp = drug_name.split('_')[0]
            cleaned_drug_name = tmp.split('(')[0].strip()
            
            comparison_item = {'drug_name': drug_name} # 개별 약품 결과 딕셔너리, 사용자 입력 약품명 추가

            try: # 정제된 약품명, 연령대를 기준으로 DrugStandard DB 조회 -> 실패 시 예외처리로
                drug_standard = DrugStandard.objects.get(
                    drug_name=cleaned_drug_name, 
                    age_group=age_group
                )
                avg_total_dose = drug_standard.avg_total_dose
                sample_count = drug_standard.sample_count
                # 1회 투약량*1일 투약 횟수로 1일 투약량 계산
                user_total_dose = user_once_dose * user_daily_times * user_days

                # (사용자량 - 평균량) / 평균량 * 100
                if avg_total_dose > 0:
                    dose_diff_percent = ((user_total_dose - avg_total_dose) / avg_total_dose) * 100
                elif user_total_dose > 0:
                    dose_diff_percent = 9999.0
                else:
                    dose_diff_percent = 0

                comparison_item.update({
                    'sample_count': sample_count,
                    'avg_total_dose': round(avg_total_dose, 2),
                    'user_total_dose': user_total_dose,
                    'difference_percent': round(dose_diff_percent, 2),
                    'level_text': _get_comparison_level(dose_diff_percent),
                })
            except DrugStandard.DoesNotExist: 
                 comparison_item['drug_error'] = f"약품 '{drug_name}' 기준 데이터가 없습니다."
            
            drug_comparison_results.append(comparison_item) # 개별 약품 결과를 전체 리스트에 추가
    
        results['drug_items_comparison'] = drug_comparison_results

        return results # 모든 비교가 완료된 최종 results 반환

class AiInfoView(APIView):
    def post(self, request, *args, **kwargs):
        body = request.data

        disease_code = body.get("disease")
        drug_name = body.get("drug_name")

        try:
            disease_obj = TreatmentStandard.objects.get(disease=disease_code)
            disease_name = disease_obj.disease_name
        except TreatmentStandard.MultipleObjectsReturned:
            disease_obj = (
                TreatmentStandard.objects
                .filter(disease=disease_code)
                .order_by("id")
                .first()
            )
            disease_name = disease_obj.disease_name
        except TreatmentStandard.DoesNotExist:
            return Response(
                {"error": f"해당 질병 코드({disease_code})에 해당하는 정보가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        initial_state = {
            "disease_name": disease_name,
            "drug_name": drug_name,
            "disease_name_eng": None,
            "drug_name_eng": None,
            "disease_raw": None,
            "drug_raw": None,
            "result":None
        }

        final_state = graph.invoke(initial_state)
        return Response(final_state["result"], status=status.HTTP_200_OK)

        # # 디버깅용
        return Response(final_state, status=status.HTTP_200_OK)

class AiAnswerView(APIView):
    def post(self, request, *args, **kwargs):
        question = request.data.get("question")

        if not question:
            return Response(
                {"error": "question 필드를 body에 포함해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = ai_answer(question).get("result")

            return Response({"result": result}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
# 질병 코드 매핑
class DiseaseSearchView(generics.ListAPIView):
    serializer_class = DiseaseSearchSerializer
    
    # GET 요청시 실행, 쿼리셋 반환
    def get_queryset(self):
        # 쿼리 파라미터값 가져옴(없으면 빈 문자열('') 반환)
        query = self.request.query_params.get('query', '')
        
        if not query or len(query) < 2: # 쿼리 파라미터가 없거나 너무 짧으면 빈 쿼리셋 반환
            return DiseaseMapping.objects.none()

        # query를 포함하는 모든 DiseaseMapping 객체 필터링
        return DiseaseMapping.objects.filter(
            disease_name__icontains=query
        )
