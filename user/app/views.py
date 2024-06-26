from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer, ProfileSerializer, UserSerializer
from django.contrib.auth import authenticate,logout
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from .models import Profile

# class Login(APIView):
#     def post(self, request):
#         data = request.data
#         serializer = LoginSerializer(data=data)
#         if serializer.is_valid():
#             username = serializer.validated_data.get('username')
#             password = serializer.validated_data.get('password')
#             user_obj = User.objects.get(username=username)
            
#             if user_obj:
#                 user = authenticate(username=username, password=password)
#                 print(user)
#                 if user is not None:
#                     refresh = RefreshToken.for_user(user)
#                     print(refresh.access_token)
#                     return Response({
#                         'status': status.HTTP_200_OK,
#                         'refresh': str(refresh.token),
#                         'access': str(refresh.access_token),
#                         'message': "Login successful"
#                     })
#             return Response({
#                 "status": 400,
#                 "message": "something went wrong",
#                 "data": serializer.errors
#             })
#         return Response({  
#             "status": 500,
#             "message": "Internal Server Error",
#             "data": None
#             })


class RegisterAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            print(data)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                phone_no = request.data.get("phone_no")
                image_file = request.FILES.get("profile_img")
                profile, created = Profile.objects.get_or_create(user=user)

                if phone_no is not None:
                    profile.phone_No = phone_no
                if image_file is not None:
                    profile.profile_pic = image_file

                profile.full_clean() 
                profile.save()

                print(phone_no)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            print(e)
            return Response({  # Make sure to return a Response object in case of exceptions
                "status": 500,
                "message": "Internal Server Error",
                "data": None
            })

class profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            user = User.objects.get(username=user.username)
            profile, created = Profile.objects.get_or_create(user=user) 
            print(profile)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        user_info = {
            "username": user.username,
            "email": user.email,
        }

        if profile.profile_pic:
            user_info["profile_pic"] = profile.profile_pic.url
        print(profile.profile_pic)
        
        if profile.phone_No:
            user_info["phone_no"] = profile.phone_No

        print(user_info)
        serializer = ProfileSerializer(profile)
        serialized_profile = serializer.data
        user_info.update(serialized_profile)

        return Response({"user": user_info})
       


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request) 
        return Response({"message": "Logout successful"}, status=200)
    

class EditProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        user_info = {
            "username": user.username,
            "email": user.email,
            "phone_no": profile.phone_No,
            "profile_img": profile.profile_pic.url if profile.profile_pic else None 
        }

        return Response(user_info, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        phone_no = request.data.get("phone_no")
        image_file = request.FILES.get("image") 

        try:
            profile, created = Profile.objects.get_or_create(user=user)

            if phone_no is not None:
                profile.phone_No = phone_no
            if image_file is not None:
                profile.profile_pic = image_file

            profile.full_clean() 
            profile.save()

            user_info = {
                "username": user.username,
                "email": user.email,
                "phone_no": profile.phone_No,
                "profile_img": profile.profile_pic.url if profile.profile_pic else None
            }

            response_data = {
                "message": "Profile updated successfully",
                "user": user_info
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except Profile.DoesNotExist:
            return Response({"error": "Profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
class adminlogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_staff:
            if user is not None:
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'status': status.HTTP_200_OK,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': "Login successful"
                    })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class Dashboard(APIView):
    def get(self,request):
        users=User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"users":serializer.data})
    
class deleteuser(APIView):
     def post(self, request,id):
        try:
            user = User.objects.get(id=id)
            print(user)
            user.delete()
            return Response({"Success": "User Deleted"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

