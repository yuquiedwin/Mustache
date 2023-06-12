import requests, json,  datetime

from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings

from .my_captcha import FormWithCaptcha
from .models import *
from .utils import generate_random_password, cartData,  guestOrder, staff_required

# Create your views here.
def index(request):
    return render(request, 'index.html')

def contacto(request):
    if request.method == 'POST':
        #Obtener los datos del usuario
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        mensaje = request.POST['mensaje']

        #Enviar el correo
        subject = f'Mensaje de cliente {nombre}'
        message = f'El asunto es: {mensaje}.\n\n El correo para comunicarse es: {correo}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_RECEPTOR]
        #Envia el correo
        send_mail(subject, message, from_email, recipient_list)
        
        return redirect('contact')
    else:
        return render(request, 'contact.html',)

def iniciarSesion(request):
    if request.method == 'POST':
        # Obtener los datos del usuario
        username = request.POST['username']
        password = request.POST['password']

        # Verificar si el usuario existe y la contraseña es correcta
        user = authenticate(request, username=username, password=password)
        if user is not None:
            
            # Autenticar al usuario y redirigir a la página de inicio
            # Si el usuario es superusuario o staff 
            if user.is_staff or user.is_superuser:
                login(request, user)
                # Redirigir a la página del staff
                return redirect('index')
            else:
                login(request, user)
                return redirect('index')
        else:
            # Mostrar un mensaje de error
            messages.success(request, "El nombre de usuario o la contraseña son incorrectos.")
            return redirect('login')
    else:
        return render(request, 'login.html')


def cerrarSesion(request):
    logout(request)
    return redirect('index')

def registro(request):
    context = {"captcha": FormWithCaptcha, }
    if request.method == 'POST':
        #Obtener los datos del usuario
        correo = request.POST['correo']
        contraseña = request.POST['contraseña']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        usuario = request.POST['usuario']
        recaptcha_response = request.POST.get('g-recaptcha-response')
        
        # Verificar el reCAPTCHA
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        #Verificar si el correo y el usuario ya existe
        if User.objects.filter(email=correo).exists():
            messages.success(request, "El correo ya existe.")
            return redirect('registro')
        elif User.objects.filter(username=usuario).exists():
            messages.success(request, "El usuario ya existe.")
            return redirect('registro')
        else:
            #Crear el usuario
            user = User.objects.create_user(email=correo, password=contraseña, first_name=nombre, last_name=apellido, username=usuario)

            #Guardar el usuario
            user.save()

            customer = Customer.objects.create(user=user, email=correo, name=f"{nombre} {apellido}")
            
            # Guardar el objeto Customer
            customer.save()
            return redirect('login')
    else:
        return render(request, 'registro.html', context)

def recuperarContraseña(request):
    if request.method == 'POST':
        #Recepciona el correo electrónico del usuario
        correo = request.POST['correo']
        #Verifica que exista usuario con ese correo
        user = get_object_or_404(User, email=correo)
        #Genera nueva contraseña
        nueva_contraseña = generate_random_password()
        #Asigna y guarda la contraseña nueva
        user.set_password(nueva_contraseña)
        user.save()

        #Generando la estructura del correo
        subject = 'Nueva contraseña'
        message = f'Tu nueva contraseña es: {nueva_contraseña}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        #Envia el correo
        send_mail(subject, message, from_email, recipient_list)
        return redirect('recuperarContraseña')
    else:
        return render(request, 'recuperarContraseña.html')


@login_required(login_url='/login')
def obtenerCita(request):
    barberos = Barber.objects.all()
    context = {'barberos': barberos}
    return render(request, 'obtenerCita.html', context=context)
@csrf_exempt
@login_required(login_url='/login')
def crearCita(request):
    if request.method == 'POST':
        #Recepcionando datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('correo')
        name = nombre + ' ' + apellido
        telefono = request.POST.get('numero_telefono')
        fecha_hora = request.POST.get('fecha_hora')
        barber_id = request.POST.get('barbero_id')

        # Obtener la fecha y la hora de la cadena recibida
        fecha, hora = fecha_hora.split('T')

        # Agregando datos a variables
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        hora = datetime.strptime(hora, '%H:%M').time()

        barber = Barber.objects.get(id=barber_id)

        cita = Cita.objects.create(fecha=fecha, hora=hora, client= name, email=email ,cellphone=telefono ,barber=barber)
        cita.save()
        return redirect('index')
    else:
        return redirect('obtenerCita')
    
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products = Product.objects.all()
    context = {'products':products,  'cartItems':cartItems,}
    return render(request, 'store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order': order, 'cartItems':cartItems}
    return render(request, 'cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order': order, 'cartItems':cartItems}
    return render(request, 'checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
       orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:

        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    else:
        print('User is not logged in')

        print('COOKIES:', request.COOKIES)
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse('Payment complete', safe=False)

@staff_required
@login_required(login_url='login')
def adminVentas(request):
    user =  User.objects.get(username=request.user)
    orders = Order.objects.all()
    
    order_data = []
    for order in orders:
        items = OrderItem.objects.filter(order=order)

        if order.complete ==  True:
            estado = 'Completado'
        else:
            estado = 'Pendiente'

        if order.customer ==  None:
            customer = 'Anonimo'
        else:
            customer = order.customer
            
        order_data.append({
            'transaction_id': order.transaction_id,
            'complete': estado,
            'date_ordered': order.date_ordered,
            'customer': customer,
            'items': items
        })
    context = {
        'user': user,
        'order_data': order_data
    }
    return render(request, 'ventas.html', context=context)

@staff_required
@login_required(login_url='login')
def adminProductos(request):
    user =  User.objects.get(username=request.user)
    products = Product.objects.all()

    context = {'user':user, 'products':products}

    if request.method == 'POST':
        nombre = request.POST.get('name-product')
        precio = request.POST.get('price-product')
        es_digital = request.POST.get('is-digital')
        if es_digital == 'no':
            es_digital = False
        else:
            es_digital = True
        imagen = request.FILES.get('image-product')
        producto = Product.objects.create(name=nombre,price=precio,digital=es_digital,image=imagen)
        producto.save()

        return redirect('adminProductos',)
    else:
        return render(request, 'productos.html', context=context)

@staff_required
@login_required(login_url='login')
def adminCitas(request):
    user =  User.objects.get(username=request.user)
    citas = Cita.objects.all()
    
    context = {'user':user, 'citas':citas}
    return render(request, 'citas.html', context=context)

