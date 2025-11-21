import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from standards.models import DiseaseMapping 

class Command(BaseCommand): 
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(f"--- Starting Disease Mapping Load ---"))
        BASE_DIR = 'data/' # 데이터 파일 디렉토리
        file_path = BASE_DIR + 'treat_stats_2023.csv' # 진료내역 파일 재사용

        df = pd.read_csv(file_path)

        df = df.rename(columns={
            'main_diag': 'disease_code',
            'disease_name': 'disease_name',
        })
        
        df = df.dropna(subset=['disease_code', 'disease_name'])
        
        # disease_code 중복 행 제거(첫번째 행만 사용)
        df.drop_duplicates(subset=['disease_code'], keep='first', inplace=True)

        records_to_create = []
        for _, row in df.iterrows():
            records_to_create.append(
                DiseaseMapping(
                    disease_code=row['disease_code'],
                    disease_name=row['disease_name'],
                )
            )

        with transaction.atomic():
            DiseaseMapping.objects.all().delete()
            DiseaseMapping.objects.bulk_create(records_to_create, batch_size=1000)
            
        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(records_to_create)} unique disease mappings."))