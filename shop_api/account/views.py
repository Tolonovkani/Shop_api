from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from . import serializers
from config.tasks import send_confirmation_email_task

User = get_user_model()


class UserViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(['POST'], detail=False)
    def register(self, request, *args,  **kwargs):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email_task.delay(user.email, user.activate_code)
            except Exception as e:
                print(e, '!!!!!!!!!!!!')
                return Response({'msg': 'Registered, but troubles with email!',
                                 'data': serializer.data}, status=201)
        return Response({'msg': 'Registered and sent mail!', 'data': serializer.data},
                        status=201)

    @action(['GET'], detail=False, url_path='activate/(?P<uuid>[0-9A-Fa-f-]+)')
    def activate(self, request, uuid):
        try:
            user = User.objects.get(activate_code=uuid)
        except User.DoesNotExist:
            return Response({'msg': 'Invalid link or link expired!'}, status=400)

        user.is_active = True
        user.activate_code = ''
        user.save()
        return Response({'msg': 'Successfully activated!'}, status=200)
