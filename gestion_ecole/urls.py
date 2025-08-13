from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('auth_app.urls')),
    path('school/', include('school.urls')),
    path('academics/', include('academics.urls')),
     path('teachers/', include('teachers.urls')),
    path('admin/', admin.site.urls),
    path('finance/', include('finance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)