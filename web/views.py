from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.db.models import Prefetch, Count
# Internal funcions imports
from web.serializers import *
from baseapp.mixins import LoginRequiredMixin
from rest_framework.pagination import PageNumberPagination


# Create your views here.

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = request.data.copy()
            data['user'] = user.id
            customer_serializer = CustomerCreateSerializer(data=data)
            if customer_serializer.is_valid():
                customer_serializer.save()
                return Response({
                    "message": "User creation completed successfully.",
                    "resp_code": 1
                })
            else:
                return Response({
                    "resp_code": 0,
                    "message": customer_serializer.errors
                })
        else:
            return Response({
                "resp_code": 0,
                "message": serializer.errors
            })
    
    
class CustomerProfileView(LoginRequiredMixin,APIView):
    def get(self,request):
        try:
            student = Student.objects.get(user=request.user)
        except:
            response = {"resp_code":0,"message":"Student not found","data":{}}
        else:
            serializer = PersonalProfileSerilizer(student)
            response = {"resp_code":1,"message":"success","data":serializer.data}
        return Response(response)
    
class StudentDetailsView(LoginRequiredMixin, APIView):
    def get(self,request, slug):
        try:
            student = Student.objects.get(id=slug)
        except:
            response = {"resp_code":0,"message":"Student not found","data":{}}
        else:
            serializer = PersonalProfileSerilizer(student)
            response = {"resp_code":1,"message":"success","data":serializer.data}
        return Response(response)    
    
    
class ProfileUpdateView(LoginRequiredMixin,APIView):
    def put(self,request):
        student = Student.objects.get(user=request.user)
        serializer = CustomerUpdateSerializer(
            instance=student, data=request.data, 
            user=request.data['user'], partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "resp_code":1,
                "message":"Profile updated successfully.",
                "data":serializer.data
            },
            status=status.HTTP_200_OK
            )

        else:
            return Response({
               "resp_code":0,
               "message":serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
            )


class UpdateUserPassword(LoginRequiredMixin, APIView):
    def put(self, request):
        serializer = CustomerPasswordUpdateSerializer(
            data=request.data, 
            context={'request': request}
        )  
        if serializer.is_valid():
            serializer.save()
            return Response({
                "resp_code":1,
                "message":"Password updated successfully.",
                "data":serializer.data
            },
            status=status.HTTP_200_OK
            )

        else:
            return Response({
               "resp_code":0,
               "message":serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
            )
       
        
class ChapterListView(LoginRequiredMixin,APIView):
    def get(self, request):
        search = request.GET.get('search')

        try:
            chapters = Chapter.objects.filter(is_active=True)
            if search:
                chapters = chapters.filter(title__icontains=search)

            serializer = ChapterSerializer(chapters, many=True,context={'request': request})
            return Response(
                {
                    "message": "success",
                    "resp_code": 1,
                    "data": serializer.data
                }
            )
        
        except Exception as e:
            return Response(
                {
                    "message": f"An error occurred: {str(e)}",
                    "resp_code": 0
                }
            )
        

class SubChapterListView(LoginRequiredMixin, APIView):
    def get(self, request, slug):
        try:
            chapter = Chapter.objects.get(id=slug,is_active=True)
        except Chapter.DoesNotExist:
            return Response({
                "message": "Chapter not found",
                "resp_code": 0
            }, status=404)

        subchapters = chapter.sub_chapter.all().order_by('order')  # Optional ordering
        serializer = SubChapterSerializer(subchapters, many=True, context={'request': request})


        return Response({
            "message": "success",
            "resp_code": 1,
            "data": {
                "chapter_title": chapter.title,
                "chapter_description": chapter.description,
                "subchapters": serializer.data
            }
        })


class SubChapterDetailView(LoginRequiredMixin, APIView):
    def get(self, request, slug):
        try:
            subchapter = SubChapters.objects.get(id=slug)
        except SubChapters.DoesNotExist:
            return Response({
                "message": "Subchapter not found",
                "resp_code": 0
            }, status=404)

        serializer = SubChapterDetailSerializer(subchapter, context={'request': request})
        return Response({
            "message": "success",
            "resp_code": 1,
            "data": serializer.data
        })
    

class UpdateSubChapterProgressView(LoginRequiredMixin, APIView):
    def post(self, request):
        sub_chapter_id = request.data.get('sub_chapter_id')
        is_completed = request.data.get('is_completed', False)
        watched_duration = request.data.get('watched_duration', 0)

        if sub_chapter_id is None:
            return Response({
                "message": "sub_chapter_id is required",
                "resp_code": 0
            }, status=400)

        try:
            student = Student.objects.get(user=request.user)
            sub_chapter = SubChapters.objects.get(id=sub_chapter_id)
        except Student.DoesNotExist:
            return Response({"message": "Student not found", "resp_code": 0}, status=404)
        except SubChapters.DoesNotExist:
            return Response({"message": "Subchapter not found", "resp_code": 0}, status=404)

        progress, created = SubChapterProgress.objects.get_or_create(
            student=student,
            sub_chapter=sub_chapter,
            defaults={
                'is_completed': is_completed,
                'watched_duration': watched_duration
            }
        )

        if created:
            return Response({
                "message": "Progress created",
                "resp_code": 1
            })

        progress.watched_duration = watched_duration
        if not progress.is_completed:
            progress.is_completed = is_completed
        progress.save()


        return Response({
            "message": "Progress updated",
            "resp_code": 1
        })
    
    
class UpdateStudentProfileImageView(LoginRequiredMixin, APIView):
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"message": "Student not found", "resp_code": 0}, status=404)

        profile_image = request.FILES.get('profile_image')
        if not profile_image:
            return Response({"message": "No image file provided", "resp_code": 0}, status=400)

        student.profile_image = profile_image
        student.save()

        return Response({
            "message": "Profile image updated successfully",
            "resp_code": 1,
            "image_url": request.build_absolute_uri(student.profile_image.url)
        }, status=200)
        
class PackageListView(APIView):
    def get(self, request):
        packages = Package.objects.all()
        serializer = PackageSerializer(packages, many=True, context={'request': request})
        return Response({
            "message": "success",
            "resp_code": 1,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class CategoryListView(APIView):
    def get(self, request):
        categories  = IdeaCategory.objects.all()
        
        serializer =  CategorySerializer(categories, many=True, context={'request': request})
        return Response({
            "message": "success",
            "resp_code": 1,
            "data": serializer.data
        }, status=status.HTTP_200_OK) 

class IdeaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IdeaListView(LoginRequiredMixin,APIView):
    def get(self, request):

       ideas = Idea.objects.all().order_by('-created_date')

       if request.GET.get('category_id'):
            category_id = request.GET.get('category_id')
            ideas = ideas.filter(category__id = category_id )
       if request.GET.get('user_id'):
            user_id = request.GET.get('user_id')
            ideas = ideas.filter(student__id = user_id)

       ideas = ideas.annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', distinct=True)
       )     
                         
       paginator = IdeaPagination()
       
       pagination_ideas = paginator.paginate_queryset(ideas, request) 
       
       serializer = IdeaSerializer(pagination_ideas, many=True, context={'request': request}) 

       pagination_data = {
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'current_page': paginator.page.number,
            'total_pages': paginator.page.paginator.num_pages,
            'page_size': paginator.get_page_size(request),
            'has_next': paginator.page.has_next(),
            'has_previous': paginator.page.has_previous()
        }
       pagination_serilizer = PaginationSerializer(pagination_data)
       return Response({
            "message": "success",
            "resp_code": 1,
            "data": serializer.data,
            "meta": pagination_serilizer.data,
        }, status=status.HTTP_200_OK)   
      

class IdeaCreateView(LoginRequiredMixin, APIView):
    def post(self, request):
        try:
            data = request.data.copy()
            category_id = request.data.get('category_id')
            if category_id:
                if not category_id:
                    return Response({
                        "message": "category_id is required",
                        "resp_code": 0
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    category = IdeaCategory.objects.get(id=category_id)
                    data['category'] = category.id
                except IdeaCategory.DoesNotExist:
                    return Response({
                        "message": "Category not found",
                        "resp_code": 0
                    }, status=status.HTTP_404_NOT_FOUND)

            user = request.user
            try:
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                return Response({
                    "message": "Student not found",
                    "resp_code": 0
                }, status=status.HTTP_404_NOT_FOUND)

            data['student'] = student.id
            

            serializer = IdeaSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Idea created successfully",
                    "resp_code": 1,
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": serializer.errors,
                    "resp_code": 0
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "Something went wrong",
                "resp_code": 0,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IdeaUpdateDeleteView(LoginRequiredMixin, APIView):
    def get_object(self, slug, user):
        try:
            student = Student.objects.get(user=user)
            return Idea.objects.get(id=slug, student=student)
        except (Idea.DoesNotExist, Student.DoesNotExist):
            return None
        
    def get(self, request, slug):
        idea = self.get_object(slug, request.user)
        if not idea:
            return Response({
                "message": "Idea not found or permission denied",
                "resp_code": 0
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IdeaSerializer(idea, many=False, context={'request': request})

        return Response({
            "message": "success",
            "resp_code": 1,
            "data": serializer.data,
        }, status=status.HTTP_200_OK) 

        


    def put(self, request, slug):
        idea = self.get_object(slug, request.user)
        if not idea:
            return Response({
                "message": "Idea not found or permission denied",
                "resp_code": 0
            }, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        category_id = data.get('category_id')
        if category_id:
            try:
                category = IdeaCategory.objects.get(id = category_id)
            except IdeaCategory.DoesNotExist:
                return Response({
                    "message": "Category not found",
                    "resp_code": 0
                }, status=status.HTTP_404_NOT_FOUND)

        is_uploaded_image_removed = data.get('is_uploaded_image_removed')
        if is_uploaded_image_removed in ['true', 'True', True, '1']:
           if idea.thumbnail and idea.thumbnail.name:
              idea.thumbnail.delete(save=False)
              idea.thumbnail = None     
            
        serializer = IdeaSerializer(idea, data=data, context={'request': request}, partial=True)    

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Idea updated successfully",
                "resp_code": 1,
                "data": serializer.data
            })
        return Response({
            "message": serializer.errors,
            "resp_code": 0
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, slug):  
        idea = self.get_object(slug, request.user)
        if not idea:
            return Response({
                "message": "Idea not found or permission denied",
                "resp_code": 0
            })
        idea.delete()
        return Response({
            "message": "Idea deleted successfully",
            "resp_code": 1
        }, status=status.HTTP_200_OK)   

class IdeaCommentPagenation(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IdeaCommentListView(LoginRequiredMixin, APIView):
    def get(self, request, slug):
        try:
            idea = Idea.objects.get(id=slug)
        except Idea.DoesNotExist:
            return Response({
                "message": "Idea not found",
                "resp_code": 0
            }, status=status.HTTP_404_NOT_FOUND)

        comments = idea.comments.all().order_by('-created_date')
        paginator = IdeaCommentPagenation()
        pagination_comments = paginator.paginate_queryset(comments, request)
        serializer = IdeaCommentSerializer(pagination_comments, many=True, context={'request': request})

        pagination_meta = {
            "count": paginator.page.paginator.count,
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "has_next": paginator.page.has_next(),
        }

        return Response({
            "message": "success",
            "resp_code": 1,
            "data": serializer.data,
            "meta": pagination_meta
        }, status=status.HTTP_200_OK)
    
    def post(self, request, slug):
        try:
            idea = Idea.objects.get(id=slug)
        except Idea.DoesNotExist:
            return Response({"message": "Idea not found", "resp_code": 0}, status=404)

        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"message": "Student not found", "resp_code": 0}, status=404)

        comment_text = request.data.get('comment')
        if not comment_text:
            return Response({"message": "Comment text is required", "resp_code": 0}, status=400)

        comment = IdeaComment.objects.create(
            idea=idea,
            student=student,
            comment=comment_text
        )

        serializer = IdeaCommentSerializer(comment, context={'request': request})

        return Response({
            "message": "Comment added",
            "resp_code": 1,
            "data": serializer.data
        }, status=201)
    
    def delete(self, request, slug):
        user = request.user
        student = Student.objects.filter(user=user).first()
        if not student:
            return Response({"message": "Student not found", "resp_code": 0}, status=404)

        try:
            comment = IdeaComment.objects.get(id=slug, student=student)
        except IdeaComment.DoesNotExist:
            return Response({"message": "Comment not found", "resp_code": 0}, status=404)

        comment.delete()
        return Response({"message": "Comment deleted successfully", "resp_code": 1}, status=200)

class IdeaLikeView(LoginRequiredMixin, APIView):
    def post(self, request, slug):
        try:
            idea = Idea.objects.get(id=slug)
        except Idea.DoesNotExist:
            return Response({"message": "Idea not found", "resp_code": 0}, status=404)

        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"message": "Student not found", "resp_code": 0}, status=404)

        like, created = IdeaLike.objects.get_or_create(idea=idea, student=student)

        if created:
            return Response({"message": "Idea liked successfully", "resp_code": 1}, status=201)
        else:
            like.delete()
            return Response({"message": "Idea unliked successfully", "resp_code": 1}, status=200)

class TotalProgressView(LoginRequiredMixin, APIView):
    def get(self, request):
        try:
            user = request.user
            student = Student.objects.get(user=user)

            total_subchapters = SubChapters.objects.count()
            completed_subchapters = SubChapterProgress.objects.filter(
                student=student, is_completed=True
            ).count()

            last_watched_sub_chapter = SubChapterProgress.objects.filter(
                student=student
            ).order_by('-last_watched_at').first()

            if last_watched_sub_chapter:
                sub_chapter = SubChapters.objects.get(id=last_watched_sub_chapter.sub_chapter.id)
                serializer = SubChapterDetailSerializer(sub_chapter, context={'request': request})


            return Response({
                "message": "success",
                "resp_code": 1,
                "data": {
                    "total_subchapters": total_subchapters,
                    "completed_subchapters": completed_subchapters,
                    "last_watched_sub_chapter": serializer.data if last_watched_sub_chapter else None
                }
            }, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({
                "message": "Student profile not found",
                "resp_code": 0
            }, status=status.HTTP_404_NOT_FOUND)


