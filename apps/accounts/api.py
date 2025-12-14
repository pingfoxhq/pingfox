from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the authenticated user's information.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CookieLoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        response = Response({"detail": "Login successful"})

        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=False,     # True in prod
            samesite="Lax",
            path="/",
        )
        response.set_cookie(
            "refresh",
            refresh,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )

        return response
    
class CookieRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh")
        if not refresh:
            return Response({"detail": "No refresh token"}, status=401)

        serializer = self.get_serializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)

        access = serializer.validated_data["access"]

        response = Response({"detail": "Token refreshed"})
        response.set_cookie(
            "access",
            access,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # blacklist refresh token if present
        refresh = request.COOKIES.get("refresh")
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Logged out"})
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
