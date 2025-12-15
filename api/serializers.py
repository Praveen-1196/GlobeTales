from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from .models import DiaryEntry, Comment, Like


# USER SERIALIZER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',"is_staff", "is_superuser"]


# REGISTER SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        # Auto create profile
        Profile.objects.create(user=user)

        return user


from rest_framework import serializers
from .models import DiaryEntry, Comment, Like

class DiaryEntrySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = DiaryEntry
        fields = [
            "id",
            "author",
            "title",
            "description",
            "location",
            "date",
            "photos",
            "created_at",
            "updated_at",
            "like_count",
            "comment_count",
        ]

    # AUTHOR
    def get_author(self, obj):
        if not obj.author:
            return None
        return {
            "id": obj.author.id,
            "username": obj.author.username,
            "email": obj.author.email,
        }

    # LIKE COUNT (SAFE)
    def get_like_count(self, obj):
        return Like.objects.filter(diary_entry=obj).count()

    # COMMENT COUNT (SAFE)
    def get_comment_count(self, obj):
        return Comment.objects.filter(diary_entry=obj).count()

    # PHOTO URL FIX (Cloudinary + Render + Local)
    def get_photos(self, obj):
        if not obj.photos:
            return None

        url = str(obj.photos)

        # Cloudinary already gives full URL
        if url.startswith("http"):
            return url

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(url)

        return url

        


# comment serializer

from .models import DiaryEntry, Comment 
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

# like serializer
from .models import Like

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = '__all__'

