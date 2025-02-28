from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer

User = get_user_model()


class UserView(generics.ListCreateAPIView):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    pass


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Successfull user registration!",
                    "status": "success",
                    "code": status.HTTP_201_CREATED,
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
