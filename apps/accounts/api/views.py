from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.api.serializers import (
    LoginSerializer,
    RegisterSerializer,
    TOTPConfirmSerializer,
    UserSerializer,
)
from apps.accounts.services.auth_service import AuthService
from apps.core.models.audit import AuditLog


class AuthThrottle(AnonRateThrottle):
    scope = "auth"


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    throttle_classes = [AuthThrottle]


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AuthService()
        user, tokens, error = service.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            totp_code=serializer.validated_data.get("totp_code"),
        )
        if error == "2FA required":
            return Response({"requires_2fa": True}, status=status.HTTP_200_OK)
        if error:
            return Response({"detail": error}, status=status.HTTP_401_UNAUTHORIZED)
        service.log_audit(user, AuditLog.Action.LOGIN, request)
        return Response({"user": UserSerializer(user).data, "tokens": tokens})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class TOTPSetupView(APIView):
    def post(self, request):
        data = AuthService().setup_totp(request.user)
        return Response(data)


class TOTPConfirmView(APIView):
    def post(self, request):
        serializer = TOTPConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ok = AuthService().confirm_totp(request.user, serializer.validated_data["code"])
        if ok:
            return Response({"status": "2fa_enabled"})
        return Response({"detail": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)


class GDPRDeleteRequestView(APIView):
    """RGPD — request account data deletion."""

    def post(self, request):
        from django.utils import timezone

        request.user.data_deletion_requested_at = timezone.now()
        request.user.save(update_fields=["data_deletion_requested_at"])
        return Response({"status": "deletion_scheduled"})


class RefreshTokenView(TokenRefreshView):
    pass
