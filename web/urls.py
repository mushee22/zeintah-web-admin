from django.urls import path
from web.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



urlpatterns = [
    # login
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # student
    path('registration/', CustomerRegistrationView.as_view(), name='student-registration'),
    path('student-profile/', CustomerProfileView.as_view(), name='student-profile'),
    path('student-profile/update/', ProfileUpdateView.as_view(), name='student-profile-update'),
    path('student/update-profile-image/', UpdateStudentProfileImageView.as_view(), name='update-student-image'),
    path('student/update-password/', UpdateUserPassword.as_view(), name="update-student-password"),
    path('student-details/<int:slug>/', StudentDetailsView.as_view(), name="student-details"),
    # Chapters 
    path('chapters/', ChapterListView.as_view(), name='chapter-list'),
    path('chapters/<int:slug>/subchapters/', SubChapterListView.as_view(), name='subchapter-list'),
    path('subchapters/<int:slug>/', SubChapterDetailView.as_view(), name='subchapter-detail'),
    path('subchapter/progress/update/', UpdateSubChapterProgressView.as_view(), name='update-chapter-progress'),
    path('total/progress/', TotalProgressView.as_view(), name='total-progress'),
    # Packages
    path('packages/', PackageListView.as_view(), name='package-list'),
    #Categories
    path('categories/', CategoryListView.as_view(), name="category-list"),
    #Ideas
    path('ideas/', IdeaListView.as_view(), name="ideas-list"), 
    path('ideas/create/', IdeaCreateView.as_view(), name="idea-create"),
    path('ideas/<int:slug>/', IdeaUpdateDeleteView.as_view(), name="idea-update"),
    path('ideas/<int:slug>/like-toggle/', IdeaLikeView.as_view(), name="idea-like"),
    path('ideas/<int:slug>/comments/', IdeaCommentListView.as_view(), name="idea-comments"),
    # Media upload
    path('media/upload/', MediaUploadView.as_view(), name="media-upload"),
    path('media/<int:pk>/', MediaDetailView.as_view(), name="media-detail"),
]
