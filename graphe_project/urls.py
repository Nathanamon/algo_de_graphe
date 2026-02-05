from django.contrib import admin
from django.urls import path
from core import views  # On importe nos vues

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),               # Page d'accueil
    path('api/calculer/', views.calculer, name='calculer'), # Notre lien "caché" pour les calculs
]