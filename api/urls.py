from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_risk, name='predict_risk'),
    path('api/predict/batch/', views.batch_predict, name='batch_predict'),
    path('api/dashboard/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('api/shipments/', views.get_shipments, name='get_shipments'),
    path('api/shipments/<int:shipment_id>/feedback/', views.update_shipment_status, name='update_shipment_status'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/reports/', views.submit_delay_report, name='submit_delay_report'),
    
    path('api/auth/status/', views.auth_status, name='auth_status'),
    path('api/auth/login/', views.auth_login, name='auth_login'),
    path('api/auth/logout/', views.auth_logout, name='auth_logout'),
    path('api/auth/register/', views.auth_register, name='auth_register'),
    path('login/', views.login_page, name='login_page'),
    path('', views.dashboard, name='dashboard'),
]
