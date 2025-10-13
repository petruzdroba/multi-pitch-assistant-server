from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token

            return Response(
                {"access": str(new_access)},
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED
            )
