from django.urls import path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 
from main.views import entrar, sair, inicio, indicadores, cadastros, qualificacao, historico, forbidden

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
	re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

    path('admin', admin.site.urls),    
    path('', inicio, name='inicio'),
    path('entrar', entrar, name='entrar'),
    path('sair', sair, name='sair'),
    path('indicadores', indicadores, name='indicadores'),
    path('cadastros', cadastros, name='cadastros'),
    path('reguas', qualificacao, name='reguas'),
    path('historico', historico, name='historico'),
    path('forbidden', forbidden, name='forbidden'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)