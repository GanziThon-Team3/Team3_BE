from django.urls import path
from .views import ComparisonView, AiInfoView, DiseaseSearchView

urlpatterns = [
    # as_view() 클래스 기반 뷰를 함수 기반 뷰처럼 사용하게 해줌
    path('compare/', ComparisonView.as_view(), name='compare'), 
    path('ai_info/', AiInfoView.as_view()),
    path('search/diseases/', DiseaseSearchView.as_view(), name='disease-search'),
]