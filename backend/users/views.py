import logging

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, AvatarSerializer, ProfileSerializer, LogoutSerializer

logger = logging.getLogger(__name__)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            logger.info("Avatar updated: user_id=%s", request.user.id)
            return Response(serializer.data)

        logger.warning("Avatar update failed validation: user_id=%s", request.user.id)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AvatarDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.avatar.delete(save=True)
        logger.info("Avatar deleted: user_id=%s", user.id)

        return Response({
            "message": "Avatar deleted successfully"
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.info("User logged out: user_id=%s", request.user.id)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
