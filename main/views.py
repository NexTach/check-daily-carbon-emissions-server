from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import UserProfile, DailyRecord, Reward
from .serializers import UserProfileSerializer, DailyRecordSerializer, RewardSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import Http404
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .services import create_or_update_daily_record, get_existing_record


class DailyRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DailyRecordSerializer

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        total_emission = (
            data.get('water_consumed', 0) * 0.000298 +
            data.get('car_usage_distance', 0) * 0.15 +
            data.get('electricity_usage', 0) * 0.443 +
            data.get('video_watching_time', 0) * 0.01 +
            data.get('internet_usage', 0) * 0.011
        )

        carbon_saved = (
            data.get('walking_steps', 0) * 0.0001 +
            data.get('public_transport_time', 0) * 0.005
        )

        serializer.save(
            user=self.request.user,
            total_carbon_emission=total_emission,
            carbon_saved=carbon_saved
        )

    def create(self, request, *args, **kwargs):
        try:
            existing_record = DailyRecord.objects.filter(
                user=request.user,
                date=timezone.now().date()
            ).first()
            
            if existing_record:
                serializer = self.get_serializer(existing_record, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_update(self, serializer):
        self.perform_create(serializer)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    profile = UserProfile.objects.get(user=request.user)
    return Response({
        'points': profile.points,
        'total_carbon_saved': profile.total_carbon_saved
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if 'username' not in request.data or 'password' not in request.data:
        return Response(
            {"error": "Both username and password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if User.objects.filter(username=request.data['username']).exists():
        return Response(
            {"error": "Username already exists"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    user = User.objects.create_user(
        username=request.data['username'],
        password=request.data['password']
    )
    
    token = Token.objects.create(user=user)
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(
        username=request.data.get('username'),
        password=request.data.get('password')
    )
    
    if not user:
        return Response(
            {"error": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    })
    
class DailyRecordView(generics.ListCreateAPIView):
    serializer_class = DailyRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user).order_by('-date')

    def create(self, request, *args, **kwargs):
        try:
            existing_record = get_existing_record(request.user)
            
            if existing_record:
                serializer = self.get_serializer(existing_record, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        create_or_update_daily_record(
            user=self.request.user,
            data=serializer.validated_data,
            serializer=serializer
        )

    def perform_update(self, serializer):
        self.perform_create(serializer)

class DailyRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DailyRecordSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'date'

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        date = self.kwargs[self.lookup_field]
        try:
            return queryset.get(date=date)
        except DailyRecord.DoesNotExist:
            raise Http404("그 날짜에 기록이 없어.")

class ProfileImageUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def put(self, request, *args, **kwargs):
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
            if 'profileImage' not in request.FILES:
                return Response({'error': '이미지 파일이 없다니까'}, status=400)
                
            image_file = request.FILES['profileImage']
            
            if profile.profileImage:
                profile.profileImage.delete(save=False)
                
            profile.profileImage = image_file
            profile.save()
            
            return Response({
                'message': 'ㅇㅋ',
                'profileImage': request.build_absolute_uri(settings.MEDIA_URL + profile.profileImage.name)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)
