from django.contrib import admin

# Register your models here.
#from django.contrib import admin
from .models import Feedback,TokenSection, TokenBooking, ChatMessage, Feedback, UnansweredQuestion

# Saare models ko register kar do taaki Admin mein dikhne lagein
admin.site.register(TokenSection)
admin.site.register(TokenBooking)
admin.site.register(ChatMessage)
admin.site.register(Feedback)
admin.site.register(UnansweredQuestion)

admin.site.register(Feedback)