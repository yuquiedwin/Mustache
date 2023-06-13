from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contacto/', views.contacto, name='contact'),
    path('login/', views.iniciarSesion, name='login'),
    path('logout/', views.cerrarSesion, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('recuperar-contraseña/', views.recuperarContraseña, name='recuperarContraseña'),
    path('agendar-cita/', views.obtenerCita, name="obtenerCita" ),
    path('crear-cita/', views.crearCita, name="crearCita" ),
    path('staff/administrar-citas', views.adminCitas, name='adminCitas'),
    path('staff/administrar-ventas', views.adminVentas, name='adminVentas'),
    path('staff/administrar-productos', views.adminProductos, name='adminProductos'),
    path('store/', views.store, name='store'),
    path('store/checkout/', views.checkout, name='checkout'),
    path('store/checkout/process_order/', views.processOrder, name="process_order"),
    path('store/cart/', views.cart, name='cart'),
    path('store/cart/update_item/', views.updateItem, name='update_item'),
    path('store/update_item/', views.updateItem, name="update_item"),
]