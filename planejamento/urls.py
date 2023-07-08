from django.urls import path
from . import views

urlpatterns = [
    path('definir_planejamento/', views.definir_planejamento, name="definir_planejamento"),
    path('apdate_valor_categoria/<int:id>',views.apdate_valor_categoria, name="apdate_valor_categoria"),
    path('ver_planejamento/', views.ver_planejamento, name="ver_planejamento"),
]