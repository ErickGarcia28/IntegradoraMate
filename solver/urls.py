from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pdf/', views.export_pdf, name='export_pdf'),
]
