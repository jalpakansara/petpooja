from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class SignupSerializer(serializers.ModelSerializer):
    company_url = serializers.URLField(
        required=False,
        allow_blank=True,
        error_messages={
            "invalid": "Please enter a valid company website URL (e.g., https://www.example.com)"
        }
    )

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'is_phone_verified': {'read_only': True},
        }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid email or password")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set longer expiration if "remember me" is checked
        if data.get("remember_me"):
            refresh.set_exp(lifetime=timedelta(days=30))  # Extend refresh token to 30 days

        return {
            "email": user.email,
            "access_token": access_token,
            "refresh_token": str(refresh),
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        # Generate token and UID
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Create password reset link
        reset_url = f"http://localhost:8000/reset-password/{uid}/{token}/"

        try:
            # Send email
            # print(settings.EMAIL_HOST_USER)
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [value],
                fail_silently=False,
            )
        except Exception as e:
            raise serializers.ValidationError(f"Failed to send email: {e}")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        """Validate the token and user ID before setting a new password."""
        uid = data.get("uid")
        token = data.get("token")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = CustomUser.objects.get(pk=uid_decoded)
        except (ObjectDoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError({"error": "Invalid user ID"})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"error": "Invalid or expired token"})

        data["user"] = user
        return data

    def save(self):
        """Save the new password for the user."""
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()

class HomeSerializer(serializers.Serializer):
    url = serializers.CharField()
    restaurant_id = serializers.IntegerField()
    restaurant_name = serializers.CharField()
    restaurant_name_lower = serializers.CharField()
    breadcrumb = serializers.CharField()
    street_address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    phone = serializers.IntegerField()
    star_rating = serializers.FloatField()
    reviews_count = serializers.IntegerField()
    price_range = serializers.CharField()
    cuisine1 = serializers.CharField()
    opening_hours = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    display_address = serializers.CharField()
    category = serializers.CharField()
    # item_name = serializers.CharField()
    item_name_lower = serializers.CharField()
    item_description = serializers.CharField()
    item_image = serializers.CharField()
    item_price = serializers.CharField()
    num_items = serializers.IntegerField()

class RestaurantDetailSerializer(serializers.Serializer):
    url = serializers.CharField()
    restaurant_id = serializers.IntegerField()
    restaurant_name = serializers.CharField()
    restaurant_name_lower = serializers.CharField()
    breadcrumb = serializers.CharField()
    street_address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    phone = serializers.IntegerField()
    star_rating = serializers.FloatField()
    reviews_count = serializers.IntegerField()
    price_range = serializers.CharField()
    cuisine1 = serializers.CharField()
    opening_hours = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    display_address = serializers.CharField()
    category = serializers.CharField()
    item_name = serializers.CharField()
    item_name_lower = serializers.CharField()
    item_description = serializers.CharField()
    item_image = serializers.CharField()
    item_price = serializers.CharField()
    # num_items = serializers.IntegerField()