from django.db import models
from django.contrib.auth.models import User

# Profile model to store extra info like role
class Profile(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ChatMessage model to store user questions and answers
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question[:30]}"


# Model to store unanswered questions for review
class UnansweredQuestion(models.Model):
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question




class TokenSection(models.Model):
    name = models.CharField(max_length=50)
    current_token = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class TokenBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.ForeignKey(TokenSection, on_delete=models.CASCADE)
    token_number = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.section.name} - Token {self.token_number}"
    
    
    
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # 1 to 5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"


