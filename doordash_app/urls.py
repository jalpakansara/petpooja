from django.urls import path
from .views import login_page,forgot_password,signup,verify_otp_page,otp_send,home_page,report_page,funnel_page,SignupView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView, HomeAPIView,RestaurantDetailAPIView,ExportRestaurantDataAPIView, FilteredRestaurantAPIView, VerifyPhoneView

urlpatterns = [
    path('', login_page, name='login-page'),
    path('forgot-password', forgot_password, name='forgot-password-page'),
    path('signup', signup, name='signup-page'),
    path('verify/otp', verify_otp_page, name='verify-otp'),
    path('home/', home_page, name='home-page'),
    path('reports/', report_page, name='report-page'),
    path('funnel/', funnel_page, name='funnel-page'),

    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/otp_send/', otp_send, name='send-otp'),
    path('api/verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('api/home/', HomeAPIView.as_view(), name='home'),
    path('api/restaurant/show_info/<str:restaurant_id>/', RestaurantDetailAPIView.as_view(), name='restaurant-details'),
    path('api/export/restaurant/', ExportRestaurantDataAPIView.as_view(), name='export-restaurant-data'),
    path('api/restaurants/filter/', FilteredRestaurantAPIView.as_view(), name='restaurant-filter'),
]
