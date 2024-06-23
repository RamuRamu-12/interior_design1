from django.urls import path
from .views import *

urlpatterns = [
    path("", testing, name="testing"),
    path(r'login', loginpage, name='login'),
    path(r'register', register, name='register'),
    path("upload", upload_data, name="upload_data"),
    path("getResult", genAIPrompt, name="GenAIPrompt"),
    path("getImage", genAIPrompt2, name="GenAIPrompt2"),
    path("getAnalytics", genAIPrompt3, name="GenAIPrompt3"),
    path("generateCombinedImage",generateCombinedImage,name="generate_combined_image"),
]



