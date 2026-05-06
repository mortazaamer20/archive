
from django.contrib import admin
from api import urls as api_urls
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
]
