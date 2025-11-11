from django.http import HttpResponse, JsonResponse

def home(request):
    return HttpResponse("Backend OK: Team3_BE is running.")

def health_check(request):
    return JsonResponse({"status": "ok"})