from django.contrib import admin
from django.urls import path, re_path
from app.views import home_view, ocr_view_birth, sign_up, ocr_view_alevel, ocr_view_olevel, cert_choice, application_status, ocr_view_olevel_zim, review_view, AdminLoginView 


urlpatterns = [
    path('', home_view, name = 'home_view'),
    path('home/', home_view, name = 'home_view'),
    path('sign_up', sign_up, name = 'sign_up'),
    path('birth_cert/', ocr_view_birth, name = 'ocr_view'),
    path('cert_choice/', cert_choice, name = 'cert_choice'),
    path('olevel_cam/', ocr_view_olevel, name = 'ocr_view'),
    path('alevel_cam/', ocr_view_alevel, name = 'ocr_view2'),
    path('olevel_zim/', ocr_view_olevel_zim, name = 'ocr_view'),
    path('alevel_zim/', ocr_view_olevel, name = 'ocr_view'),
    re_path('track_app/', application_status, name = 'track_view'),
    path('review/', review_view, name = 'review'),
    path('adlogin/', AdminLoginView.as_view(), name='admin_login'),

]
    



  

