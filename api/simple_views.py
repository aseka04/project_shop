from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_root(request):
    return Response({
        'message': 'Welcome to E-Commerce API',
        'endpoints': {
            'products': '/api/products/',
            'categories': '/api/categories/',
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
        }
    })


@api_view(['GET'])
def products_list(request):
    from apps.shop.models import Product
    products = Product.objects.all()[:10]
    data = [
        {
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'stock': p.stock
        }
        for p in products
    ]
    return Response(data)


@api_view(['POST'])
def register(request):
    from apps.accounts.models import User
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    return Response({
        'message': 'User created successfully',
        'user_id': user.id,
        'username': user.username
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        return Response({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)