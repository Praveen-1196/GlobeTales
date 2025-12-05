from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth.models import User

from django.db.models import Q, Count

# REGISTER API
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# LOGIN API
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        })




# CRUD

from .models import DiaryEntry,Comment
from .serializers import DiaryEntrySerializer,CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

# CREATE DIARY ENTRY
class CreateDiaryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = DiaryEntrySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# GET ALL ENTRIES
class ListDiariesView(APIView):
    def get(self, request):
        entries = DiaryEntry.objects.all().order_by('-created_at')
        serializer = DiaryEntrySerializer(entries, many=True)
        return Response(serializer.data)

class MyDiariesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        diaries = DiaryEntry.objects.filter(author=request.user).order_by('-created_at')
        serializer = DiaryEntrySerializer(diaries, many=True)
        return Response(serializer.data, status=200)


# GET SINGLE ENTRY
class DiaryDetailView(APIView):
    def get(self, request, pk):
        try:
            entry = DiaryEntry.objects.get(id=pk)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=404)

        serializer = DiaryEntrySerializer(entry)
        return Response(serializer.data)


# UPDATE OWN ENTRY
class UpdateDiaryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        try:
            entry = DiaryEntry.objects.get(id=pk)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=404)

        # Only author can update
        if entry.author != request.user:
            return Response({"error": "Not allowed"}, status=403)

        serializer = DiaryEntrySerializer(entry, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# DELETE OWN ENTRY
class DeleteDiaryView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            entry = DiaryEntry.objects.get(id=pk)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=404)

        # Only author can delete
        if entry.author != request.user:
            return Response({"error": "Not allowed"}, status=403)

        entry.delete()
        return Response({"message": "Diary deleted"}, status=200)

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView

# CREATE COMMENT FOR A DIARY ENTRY
class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]   # 🔥 force login

    def post(self, request, diary_id):
        # 1) Check user is authenticated (extra safety)
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # 2) Check diary exists
        try:
            diary = DiaryEntry.objects.get(pk=diary_id)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=status.HTTP_404_NOT_FOUND)

        # 3) Validate content
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 4) Create comment with the logged-in user
        comment = Comment.objects.create(
            diary_entry=diary,
            user=request.user,   # ✅ now guaranteed to be a real user
            content=content
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# LIST COMMENTS FOR A DIARY ENTRY
class ListCommentsView(APIView):
    def get(self, request, diary_id):
        comments = Comment.objects.filter(diary_entry_id=diary_id).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


# UPDATE OWN COMMENT
class UpdateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=404)

        # only owner can edit
        if comment.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# DELETE COMMENT (owner or admin)
class DeleteCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=404)

        # allow delete if owner or staff/admin
        if comment.user != request.user and not request.user.is_staff:
            return Response({"error": "Not allowed"}, status=403)

        comment.delete()
        return Response({"message": "Comment deleted"}, status=200)


# LIKE / UNLIKE FUNCTIONALITY

from .models import Like
from .serializers import LikeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
# TOGGLE LIKE / UNLIKE
class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diary_id):
        # Check diary exists
        try:
            diary = DiaryEntry.objects.get(pk=diary_id)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if like already exists
        existing_like = Like.objects.filter(diary_entry=diary, user=request.user).first()

        if existing_like:
            # Unlike
            existing_like.delete()
            return Response({"message": "Unliked"}, status=status.HTTP_200_OK)
        else:
            # Like
            like = Like.objects.create(diary_entry=diary, user=request.user)
            serializer = LikeSerializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# GET LIKE COUNT FOR A DIARY
class LikeCountView(APIView):
    def get(self, request, diary_id):
        count = Like.objects.filter(diary_entry_id=diary_id).count()
        return Response({"likes": count}, status=status.HTTP_200_OK)

class LikeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, diary_id):
        liked = Like.objects.filter(diary_entry_id=diary_id, user=request.user).exists()
        return Response({"liked": liked}, status=200)


# (Optional) LIST USERS WHO LIKED A DIARY
class LikeListView(APIView):
    def get(self, request, diary_id):
        likes = Like.objects.filter(diary_entry_id=diary_id)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# search diaries by title or description
class SearchFilterDiaryView(APIView):
    """
    Search and filter diaries using:
    - ?q=keyword
    - ?location=Goa
    - ?sort=likes | newest | oldest
    - ?start_date=YYYY-MM-DD
    - ?end_date=YYYY-MM-DD
    """
    def get(self, request):
        diaries = DiaryEntry.objects.all()

        # SEARCH
        q = request.GET.get("q")
        if q:
            diaries = diaries.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(location__icontains=q)
            )

        # FILTER BY LOCATION
        location = request.GET.get("location")
        if location:
            diaries = diaries.filter(location__icontains=location)

        # FILTER BY DATE RANGE
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            diaries = diaries.filter(date__range=[start_date, end_date])

        # SORTING
        sort = request.GET.get("sort")
        if sort == "newest":
            diaries = diaries.order_by("-created_at")
        elif sort == "oldest":
            diaries = diaries.order_by("created_at")
        elif sort == "likes":
            diaries = diaries.annotate(like_count=Count("likes")).order_by("-like_count")

        serializer = DiaryEntrySerializer(diaries, many=True)
        return Response(serializer.data, status=200)

from django.contrib.auth.models import User
from .permissions import IsAdmin

class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class AdminDeleteUserView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.delete()
        return Response({"message": "User deleted"}, status=200)

class AdminDeleteDiaryView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, diary_id):
        try:
            diary = DiaryEntry.objects.get(pk=diary_id)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=404)

        diary.delete()
        return Response({"message": "Diary deleted by admin"}, status=200)

class AdminDeleteCommentView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=404)

        comment.delete()
        return Response({"message": "Comment deleted by admin"}, status=200)

class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        total_users = User.objects.count()
        total_diaries = DiaryEntry.objects.count()
        total_comments = Comment.objects.count()

        return Response({
            "total_users": total_users,
            "total_diaries": total_diaries,
            "total_comments": total_comments
        })


from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        username = request.data.get("username")
        email = request.data.get("email")

        if username:
            user.username = username
        if email:
            user.email = email

        user.save()
        return Response({"message": "Profile updated successfully"})


from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not old_password or not new_password or not confirm_password:
            return Response({"error": "All fields are required"}, status=400)

        # Check old password matches
        if not check_password(old_password, user.password):
            return Response({"error": "Old password is incorrect"}, status=400)

        # Check new passwords match
        if new_password != confirm_password:
            return Response({"error": "New passwords do not match"}, status=400)

        # Optional security check
        if len(new_password) < 6:
            return Response({"error": "Password must be at least 6 characters long"}, status=400)

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"}, status=200)

class PublicProfileView(APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Get all diaries of this author
        diaries = DiaryEntry.objects.filter(author=user).order_by("-created_at")

        diary_data = DiaryEntrySerializer(diaries, many=True).data

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined,
            "diary_count": diaries.count(),
            "diaries": diary_data,
        })
    
from .models import Bookmark

# bookmark
class ToggleBookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diary_id):
        try:
            diary = DiaryEntry.objects.get(id=diary_id)
        except DiaryEntry.DoesNotExist:
            return Response({"error": "Diary not found"}, status=404)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            diary_entry=diary
        )

        if not created:
            bookmark.delete()
            return Response({"message": "Removed from bookmarks"})

        return Response({"message": "Added to bookmarks"})


class IsBookmarkedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, diary_id):
        is_saved = Bookmark.objects.filter(
            diary_entry_id=diary_id,
            user=request.user
        ).exists()
        return Response({"bookmarked": is_saved})


class ListBookmarksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookmarks = Bookmark.objects.filter(user=request.user)
        diaries = [b.diary_entry for b in bookmarks]
        serializer = DiaryEntrySerializer(diaries, many=True)
        return Response(serializer.data)
