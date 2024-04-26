from django.http import HttpRequest
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import User
from .serializers import UserSerializer
from member_manager_app.models import *
from shift_manager_app.models import *
from shift_manager_app.serializers import MemberSerializer
from member_manager_app.serializers import RoleSerializer,OrganizationSerializer
from django.contrib.auth import authenticate,login,logout
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .permissions import IsRoleAdmin

class MemberListCreateView(APIView):
    # authentication_classes = [SessionAuthentication, TokenAuthentication]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [IsAuthenticated(), IsRoleAdmin()]
    #     return [IsAuthenticated()]

    def get(self, request, format=None):
        user = request.user
        organ_id = get_object_or_404(Member, user=user.id)
        queryset = Member.objects.filter(organization_id=organ_id.organization)
        serializer = MemberSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = request.data
        if not data.get('first_name'):
            return Response('First name required')
        if not data.get('last_name'):
            return Response('last name required')
        if not data.get('username'):
            return Response('username required')
        if not data.get('email'):
            return Response('email')
        organization_name = data.get('organization')
        role_name = data.get('role')

        if not organization_name or not role_name:
            return Response({'message': 'Organization name and Role name are required'}, status=status.HTTP_400_BAD_REQUEST)

        organization, created = Organization.objects.get_or_create(name=organization_name)
        role, created = Role.objects.get_or_create(name=role_name)

        user = User.objects.create(
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=make_password(data.get('password'))
        )

        member = Member.objects.create(user=user, organization=organization, role=role)
        user_serializer = UserSerializer(user)
        member_serializer = MemberSerializer(member)
        role_serializer = RoleSerializer(role)
        return Response({
            "message":"Member created ",
            "user": user_serializer.data,
            "member": member_serializer.data,
            "role": role_serializer.data
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            user = request.user
            try:
                member = Member.objects.get(user = user)
                member = MemberSerializer(member)
            except Member.DoesNotExist:
                return Response("Member not found")
            return Response({'message': 'Authentication successful',"data":member.data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        request.session.flush()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class user_details(APIView):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                members = Member.objects.get(user = request.user)
            except Member.DoesNotExist:
                return Response ("Member not found")
            serializer = MemberSerializer(members)
            return Response({"data ":serializer.data})
        return Response({"data":"please login"})



class MemberRetrieveUpdateDestroyView(APIView):
  

    authentication_classes = [SessionAuthentication]
   

    def get(self, request, format=None, uuid=None) -> Response:
        member_uuid = uuid
        print(f'mem uuid = {member_uuid}')
        user = request.user
        member = Member.objects.get(user = user)
        print(member.organization)
        member = get_object_or_404(Member, organization=member.organization,uuid =member_uuid )
        serializer = MemberSerializer(member)
        user_serializer = UserSerializer(member.user)
        role_serializer = RoleSerializer(member.role)
        
        data = {
            'member': serializer.data,
            'user': user_serializer.data,
            'role': role_serializer.data,
        }
        return Response(data)

    def put(self, request, format=None, uuid=None) -> Response:
     
        member_uuid = uuid
        print(f'mem uuid = {member_uuid}')
        user = request.user
        member = Member.objects.get(uuid = member_uuid)
        print(member.organization)
        try:
            user_data = User.objects.get(uuid = member.user.uuid)
            print(f'user_data == {user_data}')
            user_data.first_name = request.data["first_name"]
            user_data.last_name = request.data["first_name"]
            user_data.save()

        except User.DoesNotExist:
            return Response("User not found")
        member = get_object_or_404(Member, organization=member.organization,uuid =member_uuid )
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"member updated","data":serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None, uuid=None) -> Response:
      
        member_uuid = uuid
        print(f'mem uuid = {member_uuid}')
        user = request.user
        member = Member.objects.get(uuid = member_uuid)
        member.delete()
        return Response({"message":"member deleted"},status=status.HTTP_204_NO_CONTENT)