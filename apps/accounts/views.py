from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserSerializer,
)
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "access_token": str(
                    refresh.access_token
                ),
                "refresh_token": str(
                    refresh
                ),
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        user.last_login_at = (
            timezone.now()
        )

        user.save(
            update_fields=[
                "last_login_at"
            ]
        )

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "access_token": str(
                    refresh.access_token
                ),
                "refresh_token": str(
                    refresh
                ),
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
            }
        )
    

class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "message": "Logout successful."
            },
            status=status.HTTP_200_OK
        )



class ProfileView(APIView):
    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):
        return Response(
            UserSerializer(
                request.user
            ).data
        )