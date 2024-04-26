"""
URL configuration for at_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from authenticator_app.views import *
from shift_manager_app.views import *
from attendance_manager_app.views import *
from csv_generator_app.views import *
# from flower import views as flower_views
from django.views.generic import RedirectView
from django.conf.urls.static import static
urlpatterns = [

    path('admin/', admin.site.urls),
    #Authentication
    path('api/login/',UserLoginView.as_view()),
    path('api/logout/',UserLogoutView.as_view()),
    #Member
    path('api/user-details/', user_details.as_view()),
    path('api/member/',MemberListCreateView.as_view()),
    path('api/member/<uuid:uuid>/', MemberRetrieveUpdateDestroyView.as_view(), name='member-retrieve-update-destroy'),
    #System Location
    path('api/system-location/',SystemLocationCreateView.as_view()),
    path('api/system-location/<uuid:uuid>/', SystemLocationRetrieveUpdateDestroyView.as_view()),
    #Shift
    path('api/shift/',ShiftGetCreateView.as_view()),
    path('api/shift/<uuid:uuid>/', ShiftRetrieveUpdateDestroyView.as_view()),
    #ShiftScheduleLog
    path('api/shift-schedule-log/',ShiftScheduleLogGetCreateView.as_view()),
    path('api/shift-schedule-log/<uuid:uuid>/', ShiftScheduleLogRetrieveUpdateDestroyView.as_view()),
    #LocationSettings
    path('api/location-settings/shift-schedule-log/<uuid:uuid>/',LocationSettingsGetCreateView.as_view()),
    path('api/location-settings/<uuid:uuid>/', LocationSettingsUpdateDeleteView.as_view()),
    #FRImage
    path('api/fri-images/',FRImageView.as_view()),
    path('api/fri-images/<uuid:uuid>/', FRImageDetailView .as_view()),
    #Check in and check out
    path('api/scan/',ScanAPIView.as_view()),
    #Attendance 
    path('api/compute/',ComputeAttendanceApi.as_view()),
    path('api/attendance/',GetAttendanceAPIView.as_view()),
    #CSV
    path('export-request/', export_request, name='export_request'),
    path('export-request/<uuid:export_request_id>/',export_request_status, name='export_request_status'),
    # path('download-csv/<uuid:export_request_id>/', download_csv, name='download_csv'),
     path('flower/', RedirectView.as_view(url=settings.FLOWER_URL), name='flower'),
    # path('admin/flower/', flower_views.FlowerAdminSite.urls),

    path('api/roles/',roles_view),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

