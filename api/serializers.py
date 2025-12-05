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

    # Return username + id
    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "username": obj.author.username,
        }

    def get_like_count(self, obj):
        return Like.objects.filter(diary_entry=obj).count()

    def get_comment_count(self, obj):
        return Comment.objects.filter(diary_entry=obj).count()

        


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

