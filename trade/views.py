from django.shortcuts import render
import jwt
import random
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.http import HttpResponse
from .models import *
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from .models import stocks
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING
from drf_yasg import openapi

SECRET_KEY = 'u^3JJZ#Lc9AV4C*46q9st$7kr$pz!kW1' 
User = get_user_model()

# Sign up view
@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication,])
@permission_classes([AllowAny,])
@swagger_auto_schema(
    operation_description='SIGNUP',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Email address',
                format=openapi.FORMAT_EMAIL
            ),
            'fullname': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Full name',
                max_length=100
            ),
            'lastname': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Last name',
                max_length=100
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Password',
                format=openapi.FORMAT_PASSWORD
            ),
            'confirm_password': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Confirm password',
                format=openapi.FORMAT_PASSWORD
            ),
            
        },
        required=['email', 'fullname','password','confirm_password'],
    ),
    responses={
        200: 'OK',
        400: 'Bad Request',
    },
    operation_id='my_api_operation',
)
def signup(request):
    email = request.POST.get('email')
    fullname = request.POST.get('fullname')
    lastname = request.POST.get('lastname')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if (not email) or (not fullname) or (not lastname) or (not password) or (not confirm_password):
        return Response({'error': 'All fields are required'})

    if password != confirm_password:
        return Response({'error': 'Passwords do not match'})

    try:
        # Check if user already exists
        user = User.objects.get(email = email)
        return Response({'error': 'User already exists'})
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(email=email, fullname=fullname, lastname=lastname, password=password)
        return Response({'success': 'User created successfully',
                         'refresh': str(RefreshToken.for_user(user)),
                         'access_token' : str(RefreshToken.for_user(user).access_token)
                         })

# Login view
@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication,])
@permission_classes([AllowAny,])
@swagger_auto_schema(
    operation_description='LOGIN',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Email address',
                format=openapi.FORMAT_EMAIL
            ),
            'otp': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='OTP',
                maxLength=6
            ),
            
        },
        required=['email', 'otp'],
    ),
    responses={
        200: 'OK',
        400: 'Bad Request',
    },
    operation_id='my_api_operation',
)
def login(request):
    email = request.POST.get('email')
    otp = request.POST.get('otp')

    if not email or not otp:
        return Response({'error': 'Email and OTP are required'})

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'})

    # Check if OTP is valid
    user = User.objects.get(email=email)
    user_otp = user_otps.objects.filter(user = user).latest('id')
    if otp != str(user_otp.otp) :
        return Response({'error': 'Invalid OTP'})

    return Response({'success': 'Login successfull',
                    'refresh': str(RefreshToken.for_user(user)),
                    'access_token' : str(RefreshToken.for_user(user).access_token)
                    })

# Send OTP view
@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication,])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.POST.get('email')
    if not email:
        return Response({'error': 'Email is required'})

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'})

    # Generate random 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # Store OTP in session
    user = User.objects.get(email = email)
    user_otps.objects.create(user=user,otp = otp)

    # Send OTP to user's email
    html_content = f"<strong>Your Login OTP is : {otp}</strong>"
    email = EmailMessage("my subject", html_content, "tellabiyyamabhilash123@gmail.com", [email])
    email.content_subtype = "html"
    res = email.send()

    return Response({'success': 'OTP sent'})


class StockList(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = stocks.objects.all()
    serializer_class = StockSerializer

class BuyApi(APIView):
    authentication_classes = [JWTAuthentication,]
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_description='Description of your API view',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='User ID',
                    format=openapi.FORMAT_INT32
                ),
                'stock': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Stock ID',
                    format=openapi.FORMAT_INT32
                ),
                'id_mis': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='ID MIS',
                    default=False
                ),
                'on_nrml': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='ON NRML',
                    default=False
                ),
                'qty': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Quantity',
                    format=openapi.FORMAT_INT32,
                    default=0
                ),
                'lots': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Lots',
                    format=openapi.FORMAT_DECIMAL,
                    default=0,
                    maximum=999999999999.99
                ),
                'market': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Market',
                    default=True
                ),
                'limit': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Limit',
                    default=False
                ),
                'price': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Price',
                    format=openapi.FORMAT_DECIMAL,
                    default=0,
                    maximum=99999999999999.99
                ),
            },
            required=['user', 'stock'],
        ),
        responses={
            200: 'OK',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            500: 'Internal Server Error',
        },
        operation_id='my_api_operation',
    )

    def post(self,request):
        serializer = BuySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        stock = serializer.validated_data['stock']
        market = serializer.validated_data['market']
        limit = serializer.validated_data['limit']
        id_mis = serializer.validated_data['id_mis']
        on_nrml = serializer.validated_data['on_nrml']
        qty = serializer.validated_data['qty']
        lot = qty/50
        record  = Buy.objects.create(user=user,stock=stock,market=market,limit=limit,id_mis=id_mis,on_nrml=on_nrml,lots=lot)
        return Response({
            'status' : "bought",
        })

class SellApi(APIView):
    authentication_classes = [JWTAuthentication,]
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_description='Description of your API view',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='User ID',
                    format=openapi.FORMAT_INT32
                ),
                'stock': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Stock ID',
                    format=openapi.FORMAT_INT32
                ),
                'id_mis': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='ID MIS',
                    default=False
                ),
                'on_nrml': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='ON NRML',
                    default=False
                ),
                'qty': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Quantity',
                    format=openapi.FORMAT_INT32,
                    default=0
                ),
                'lots': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Lots',
                    format=openapi.FORMAT_DECIMAL,
                    default=0,
                    maximum=999999999999.99
                ),
                'market': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Market',
                    default=True
                ),
                'limit': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Limit',
                    default=False
                ),
                'price': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Price',
                    format=openapi.FORMAT_DECIMAL,
                    default=0,
                    maximum=99999999999999.99
                ),
            },
            required=['user', 'stock'],
        ),
        responses={
            200: 'OK',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            500: 'Internal Server Error',
        },
        operation_id='my_api_operation',
    )
    def post(self,request):
        serializer = SellSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        stock = serializer.validated_data['stock']
        market = serializer.validated_data['market']
        limit = serializer.validated_data['limit']
        id_mis = serializer.validated_data['id_mis']
        on_nrml = serializer.validated_data['on_nrml']
        qty = serializer.validated_data['qty']
        lot = qty/50
        record  = Buy.objects.create(user=user,stock=stock,market=market,limit=limit,id_mis=id_mis,on_nrml=on_nrml,lots=lot)
        return Response({
            'status' : "sold",
        })