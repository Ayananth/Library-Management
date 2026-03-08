from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, AvatarSerializer



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
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AvatarDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):

        user = request.user
        user.avatar.delete(save=True)

        return Response({
            "message": "Avatar deleted successfully"
        })