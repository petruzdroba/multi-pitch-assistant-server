from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..serializers.auth_serializers import SignupSerializer, LoginSerializer, MeSerializer


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class MeView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        auth = JWTAuthentication()
        user_auth_tuple = auth.authenticate(request)
        if user_auth_tuple is None:
            return Response({"user": None}, status=status.HTTP_200_OK)

        user, token = user_auth_tuple

        refresh = RefreshToken.for_user(user)
        new_access_token = str(refresh.access_token)

        serializer = MeSerializer(user)
        return Response({
            "user": serializer.data,
            "access": new_access_token
        }, status=status.HTTP_200_OK)

