from django.urls import path
from .views import MyDiariesView, RegisterView, LoginView,LikeStatusView,ProfileView,ChangePasswordView,PublicProfileView
from .views import ToggleBookmarkView, IsBookmarkedView, ListBookmarksView


from .views import (
    CreateDiaryView,
    ListDiariesView,
    DiaryDetailView,
    UpdateDiaryView,
    DeleteDiaryView
)
from .views import (
    CreateCommentView,
    ListCommentsView,
    UpdateCommentView,
    DeleteCommentView,
)
from .views import (
    ToggleLikeView,
    LikeCountView,
    LikeListView,
)
from .views import (
    AdminUserListView,
    AdminDeleteUserView,
    AdminDeleteDiaryView,
    AdminDeleteCommentView,
    AdminStatsView,
)

from .views import SearchFilterDiaryView


urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name="login"),
    path('diary/create/', CreateDiaryView.as_view()),
    path('diary/', ListDiariesView.as_view()),
    # path('diary/my/', MyDiariesView.as_view()),
    path("my-diaries/", MyDiariesView.as_view()),


    path('diary/<int:pk>/', DiaryDetailView.as_view()),
    path('diary/<int:pk>/update/', UpdateDiaryView.as_view()),
    path('diary/<int:pk>/delete/', DeleteDiaryView.as_view()),
    # comments
    path('diary/<int:diary_id>/comments/create/', CreateCommentView.as_view()),
    path('diary/<int:diary_id>/comments/', ListCommentsView.as_view()),
    path('comments/<int:pk>/update/', UpdateCommentView.as_view()),
    path('comments/<int:pk>/delete/', DeleteCommentView.as_view()),
    # likes
    path('diary/<int:diary_id>/like-toggle/', ToggleLikeView.as_view()),
    path('diary/<int:diary_id>/likes/count/', LikeCountView.as_view()),
    path('diary/<int:diary_id>/likes/', LikeListView.as_view()),
    path("diary/<int:diary_id>/like-status/", LikeStatusView.as_view()),

    # search and filter
     path('diary/search/', SearchFilterDiaryView.as_view()),
    #   ADMIN ROUTES
    path('admin/users/', AdminUserListView.as_view()),
    path('admin/users/<int:user_id>/delete/', AdminDeleteUserView.as_view()),
    path('admin/diary/<int:diary_id>/delete/', AdminDeleteDiaryView.as_view()),
    path('admin/comments/<int:comment_id>/delete/', AdminDeleteCommentView.as_view()),
    path('admin/stats/', AdminStatsView.as_view()),
    # profile
    path("profile/", ProfileView.as_view()),
    path("change-password/",ChangePasswordView.as_view()),
    path("users/<str:username>/", PublicProfileView.as_view()),
path("diary/<int:diary_id>/bookmark-toggle/", ToggleBookmarkView.as_view()),
path("diary/<int:diary_id>/bookmarked/", IsBookmarkedView.as_view()),
path("bookmarks/", ListBookmarksView.as_view()),

]

