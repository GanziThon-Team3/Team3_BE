import pandas as pd
from django.core.management.base import BaseCommand
from standards.models import TreatmentStandard, DrugStandard
from django.db import transaction

class Command(BaseCommand): 
    # 커맨드 실행 시 호출되는 메인 함수
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Starting Data Load ---")) # 터미널에 로딩 시작 알림 출력

        BASE_DIR = 'data/' # 데이터 파일 디렉토리
        TREATMENT_FILE = BASE_DIR + 'treat_stats_2023.csv' # 진료내역 파일 경로
        DRUG_FILE = BASE_DIR + 'drug_stats.csv' # 의약품처방 파일 경로

        self._load_treatment_data(TREATMENT_FILE) # 진료내역 데이터 로드 함수 호출
        self._load_drug_data(DRUG_FILE) # 의약품처방 데이터 로드 함수 호출
        
        self.stdout.write(self.style.NOTICE("--- Data Load Complete ---")) # 로딩 완료 알림 출력

    # 진료내역 데이터 로드 함수
    def _load_treatment_data(self, file_path): 
        self.stdout.write(self.style.NOTICE(f"Loading Treatment data from {file_path}...")) # 현재 로드 중인 파일 알림
        
        DEPT_CODE_MAPPING = {
            0: "일반의",
            1: "내과",
            2: "신경과",
            3: "정신과",
            4: "외과",
            5: "정형외과",
        }
        
        df = pd.read_csv(file_path) # 판다스를 사용해 csv 파일 읽기(DataFrame 생성)

        # 컬럼명 매핑 (csv 컬럼명 -> 모델 필드명)
        df = df.rename(columns={ 
            'main_diag': 'disease',
            'disease_name': 'disease_name',
            'dept': 'dept_code', # 변환 전 코드
            'age_group': 'age_group',
            'mean_copay': 'avg_fee',
            'mean_days': 'avg_days',
            'sample_count': 'sample_count',
        })

        df['dept'] = df['dept_code'].map(DEPT_CODE_MAPPING) # 진료 과목 코드 매핑
        df = df.dropna(subset=['disease', 'dept', 'age_group']) # 해당 속성이 없는 행 제거
        
        records_to_create = [] # DB에 적재할 객체 리스트 초기화
        for _, row in df.iterrows(): # 데이터프레임의 각 행을 순회하며 데이터 처리
            records_to_create.append( # TreatmentStandard 모델 객체 생성 후 리스트에 추가
                TreatmentStandard(
                    age_group=row['age_group'], 
                    dept=row['dept'], 
                    disease=row['disease'], 
                    disease_name=row['disease_name'],
                    avg_fee=float(row['avg_fee']), 
                    avg_days=float(row['avg_days']), # FloatField에 맞게 형변환
                    sample_count=int(row['sample_count'])
                )
            )

        with transaction.atomic(): # 트랜잭션을 사용하여 DB 작업의 원자성 보장
            TreatmentStandard.objects.all().delete() # 기존 DB 데이터 전체 삭제 (데이터 갱신 시)
            # bulk_create로 DB에 대량 삽입(1000개씩)
            TreatmentStandard.objects.bulk_create(records_to_create, batch_size=1000)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(records_to_create)} Treatment records.")) # 성공적으로 로드된 레코드 수 출력

    # 의약품처방 데이터 로드 함수
    def _load_drug_data(self, file_path): 
        self.stdout.write(self.style.NOTICE(f"Loading Drug data from {file_path}..."))
        
        df = pd.read_csv(file_path)

        df = df.rename(columns={ 
            'short_name': 'drug_name',
            'age_group': 'age_group',
            'mean_total_dose': 'avg_total_dose',
            'sample_count': 'sample_count',
        })

        df = df.dropna(subset=['drug_name', 'age_group'])

        records_to_create = []
        for _, row in df.iterrows(): 
            # 제품명에서 _(언더바)와 괄호 이전의 핵심 텍스트만 추출
            tmp = row['drug_name'].split('_')[0]
            cleaned_drug_name = tmp.split('(')[0].strip()
            
            records_to_create.append( 
                DrugStandard(
                    age_group=row['age_group'], 
                    drug_name=cleaned_drug_name, 
                    avg_total_dose=float(row['avg_total_dose']), 
                    sample_count=int(row['sample_count']),
                )
            )

        with transaction.atomic():
            DrugStandard.objects.all().delete()
            DrugStandard.objects.bulk_create(records_to_create, batch_size=1000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(records_to_create)} Drug records."))