from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Third Eye"
admin.site.site_title = "Third Eye Admin"
admin.site.index_title = "Welcome to Third Eye Control Room"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",include('myapp.urls')),
    path("analyze",include('analyze.urls')),
    path("photos",include('photos.urls')),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


