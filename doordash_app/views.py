# Create your views here.
from .models import CustomUser, Doordash
from .serializers import SignupSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, HomeSerializer, RestaurantDetailSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import csv
from django.http import HttpResponse
import random
from rest_framework import generics, status
from twilio.rest import Client
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Avg, F, FloatField, Value
from django.db.models.functions import Cast, Replace
import openpyxl

# Temporary in-memory storage for OTPs
otp_storage = {}

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def login_page(request):
    return render(request, 'login.html')

def forgot_password(request):
    return render(request, 'forgot_password.html')

def signup(request):
    return render(request, 'signup.html')

def verify_otp_page(request):
    return render(request, 'verify_otp.html')

# @login_required(login_url=settings.LOGIN_URL) 
def home_page(request):
    # Fetch all businesses from DB
    # business_list = Doordash.objects.all().order_by('restaurant_name')

    # business_list = Doordash.objects.values(
    #     'restaurant_name','star_rating', 'category'
    # ).annotate(num_items=Count('item_name')).order_by('restaurant_name')

    # Convert item_price to numeric by removing '$' and casting to float
    business_list = (
       Doordash.objects
        .annotate(
            price_numeric=Cast(
                Replace(F('item_price'), Value('$'), Value('')),  # remove $ sign
                FloatField()
            )
        )
        .values(
            'restaurant_name','star_rating', 'category', 'reviews_count'
        )
        .annotate(
            num_items=Count('item_name'),
            avg_price=Avg('price_numeric')
        )
        .order_by('restaurant_name')
    )

    # print("business_list :: ",business_list)

    # Pagination: 5 items per page
    paginator = Paginator(business_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {'page_obj': page_obj})

def otp_send(phone):
    otp = random.randint(1000, 9999)
    # print("phone ::",phone, type(phone))
    otp_storage[phone] = str(otp)
    # print("otp_storage::",otp_storage)
    # print(f"OTP for {phone}: {otp}")  # Replace with SMS sending logic
            
    # Send OTP via Twilio SMS
    try:
        message = client.messages.create(
            body=f"Your OTP is: {otp}",
            from_= settings.TWILIO_PHONE_NUMBER,
            to="+91"+phone
        )
        return Response({'message': message, 'phone_number': phone}, status=status.HTTP_200_OK)
            #     print(f"Sent OTP to {phone}: {otp}")
    except Exception as e:
            #     print("Twilio Error:", e)
        return Response({'error': 'Failed to send OTP. '+str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def report_page(request):
    return render(request, 'reports.html')

def funnel_page(request):
    # Fetch unique values from the table
    star_ratings = Doordash.objects.values_list('star_rating', flat=True).distinct()
    cuisines = Doordash.objects.values_list('cuisine1', flat=True).distinct()
    restaurant_types = Doordash.objects.values_list('category', flat=True).distinct()

    context = {
        'star_ratings': star_ratings,
        'cuisines': cuisines,
        'restaurant_types': restaurant_types,
    }

    return render(request, 'funnel.html', context)

class SignupView(generics.CreateAPIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            # Generate and "send" OTP
            result = otp_send(phone)
            print("otp result :: ",result)
            serializer.save()
            # return Response({'message': 'Signup successful.'}, status=status.HTTP_201_CREATED)
            return Response({'message': 'Signup successful. Verify your phone.', 'phone_number': phone,'success':True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyPhoneView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone or not otp:
            return Response({'error': 'Phone number and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        if phone in otp_storage and otp_storage[phone] == otp:
            try:
                user = CustomUser.objects.get(phone_number=phone)
                user.is_phone_verified = True
                user.save()
                del otp_storage[phone]
                return Response({'message': 'Phone number verified successfully','success':True})
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print("valid login data")
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        else:
            print("invalid serializer")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # This will now work after enabling blacklisting

            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Password reset link sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HomeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        queryset = (
            Doordash.objects
            .values('url','restaurant_id','restaurant_name', 'restaurant_name_lower','breadcrumb','star_rating', 'cuisine1','street_address','city','state','country','phone','reviews_count','price_range','opening_hours','latitude','longitude','display_address','category','item_name_lower','item_description','item_image','item_price')
            .annotate(num_items=Count('item_name', distinct=True))
            .filter(num_items__gt=1)
        )

        # Add pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Optional: override default here
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = HomeSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class RestaurantDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, restaurant_id):
        data = Doordash.objects.filter(restaurant_id=restaurant_id)
        if not data.exists():
            return Response({"detail": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        # Add pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Optional: override default here
        paginated_queryset = paginator.paginate_queryset(data, request)

        serializer = RestaurantDetailSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class ExportRestaurantDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Create the HTTP response with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="restaurant_data.csv"'

        writer = csv.writer(response)

        # Write the CSV header
        writer.writerow([
            'restaurant_name', 'star_rating', 'cuisine1'
        ])

        # Fetch and write data
        queryset = (
            Doordash.objects
            .values('restaurant_name', 'star_rating', 'cuisine1')
            .annotate(num_items=Count('item_name', distinct=True))
            .filter(num_items__gt=1)
        )
        for obj in queryset:
            writer.writerow([
                obj['restaurant_name'],
                obj['star_rating'],
                obj['cuisine1'],
                obj['num_items']
            ])

        return response

class FilteredRestaurantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        star_rating = request.query_params.get('star_rating')
        cuisine1 = request.query_params.get('cuisine1')
        item_quantity = request.query_params.get('item_quantity', 1)

        queryset = (
            Doordash.objects
            .values('restaurant_id', 'restaurant_name', 'star_rating', 'cuisine1')
            .annotate(num_items=Count('item_name', distinct=True))
            .filter(num_items__gte=item_quantity)
        )

        if star_rating:
            try:
                rating = float(star_rating)
                print("rating : ",rating)
                # lower = max(0, rating - 0.5)
                upper = min(5, rating + 0.4)  # So 4.5 gives range 4.0 to 4.9
                # print("lower : ",lower)
                print("upper : ",upper)
                queryset = queryset.filter(star_rating__gte=4.0, star_rating__lte=4.9)
            except ValueError:
                pass  # ignore invalid input
            # queryset = queryset.filter(star_rating=star_rating)

        if cuisine1:
            queryset = queryset.filter(cuisine1__iexact=cuisine1)

        return Response(queryset)
    
# def export_all_businesses(request):
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.title = "Businesses"

#     # Header row
#     ws.append([
#         "Name of business", "Rating", "Restaurant Type", 
#         "No. of items", "Avg. price (1 person)", 
#         "Avg Online Orders (Monthly)", "Service Type"
#     ])

#     # All rows
#     for b in Doordash.objects.all():
#         ws.append([
#             b.restaurant_name,
#             b.star_rating,
#             b.category,
#             b.num_items,
#             float(b.avg_price),
#             b.reviews_count,
#             b.service_type
#         ])

#     # Create HTTP response
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename=all_businesses.xlsx'
#     wb.save(response)
#     return response