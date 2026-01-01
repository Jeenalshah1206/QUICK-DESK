from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('news/', views.news, name='news'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('token/', views.token, name='token'),
    path('feedback/', views.feedback_view, name='feedback'),
   
    path('register/', views.register, name='register'),
    path('contact/', views.contact, name='contact'),
    path('token_booking/<int:section_id>/', views.token_booking, name='token_booking'),
    path('gemini-chat/', views.gemini_chat_view, name='gemini_chat'),


]