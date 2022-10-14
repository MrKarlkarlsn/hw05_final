from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.internal_server_error'
handler403 = 'core.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls,),
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('about/', include('about.urls'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
