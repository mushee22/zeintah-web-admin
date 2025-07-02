from django.db import models
from baseapp.models import BasemodelMixin
from backend.models import CustomUser

# Create your models here.
class Batch(models.Model):
    name = models.CharField(max_length=250,null=True,blank=True)
    code = models.CharField(unique=True,max_length=200)

    def __str__(self):
        return f"{self.name} {self.code}"

class Student(BasemodelMixin):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    group_code = models.CharField(max_length=200,null=True,blank=True)
    profile_image = models.ImageField(null=True,blank=True,upload_to='students')
    student_bio = models.TextField(null=True,blank=True)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    package = models.ForeignKey('Package', on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)

    # def __str__(self):
    #     return f"{self.user}"

class Chapter(BasemodelMixin):
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='chapters')
    description = models.TextField(null=True,blank=True)
    duration = models.IntegerField(null=True,blank=True)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.title}"

class SubChapters(BasemodelMixin):
    chapter = models.ForeignKey(Chapter,on_delete=models.CASCADE,related_name="sub_chapter")
    title = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    video = models.FileField(upload_to='subchapters/videos')
    thumbnail = models.ImageField(upload_to='chapters/subchapters')
    duration = models.IntegerField(null=True,blank=True)
    order = models.IntegerField()

class Features(BasemodelMixin):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"

class Package(BasemodelMixin):
    title = models.CharField(max_length=200)
    thumbnail =  models.ImageField(upload_to='packages')
    price = models.FloatField(default=0)
    offer = models.FloatField(default=0)
    features= models.ManyToManyField(Features,related_name="package_features")

class Purchase(BasemodelMixin):
    payment_status = [
        ("success","Success"),
        ("in_progress","In progress"),
        ("failed","Failed")
    ]
    student = models.ForeignKey(Student,on_delete=models.SET_NULL,null=True,related_name='purchased_student')
    package = models.ForeignKey(Package,on_delete=models.SET_NULL,related_name="purchased_package",null=True)
    payment_id = models.CharField(max_length=200)
    status = models.CharField(choices=payment_status)

    # def __str__(self):
    #     return f"{self.course_name.title} {self.get_status_display()}"

class SubChapterProgress(BasemodelMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_progress')
    sub_chapter = models.ForeignKey(SubChapters, on_delete=models.CASCADE, related_name='sub_chapter_progress')
    is_completed = models.BooleanField(default=False)
    watched_duration = models.IntegerField(default=0)
    last_watched_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'sub_chapter')

    # def __str__(self):
    #     return f"{self.student.user} - {self.chapter.title} - {'Completed' if self.is_completed else 'In Progress'}"

class IdeaCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='idea_categories', null=True, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Idea(BasemodelMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_ideas')
    category = models.ForeignKey(IdeaCategory, on_delete=models.CASCADE, related_name='ideas')
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbanil = models.ImageField(upload_to='ideas', null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.student.user.username}"
    
class IdeaComment(BasemodelMixin):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='idea_comments')
    comment = models.TextField()

    def __str__(self):
        return f"Comment by {self.student.user.username} on {self.idea.title}"

class IdeaLike(BasemodelMixin):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='likes')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='liked_ideas')

    class Meta:
        unique_together = ('idea', 'student')

    def __str__(self):
        return f"{self.student.user.username} liked {self.idea.title}"

