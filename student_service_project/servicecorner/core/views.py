from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatMessage  # make sure this model exists

from django.shortcuts import render, get_object_or_404


from .models import TokenSection, TokenBooking
from django.utils import timezone
from datetime import timedelta
from .models import Feedback
from django.contrib import messages


import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse
from django.http import StreamingHttpResponse

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# Home Page
def home(request):
    return render(request, 'home.html')

# About Page
def about(request):
    return render(request, 'about.html')

# Register Page (FIXED BACKEND ERROR)
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if not name or not email or not password:
            return render(request, 'register.html', {'error': 'All fields are required.'})

        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(username=email).exists():
            return render(request, 'register.html', {'error': 'User with this email already exists.'})

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        # Auto login - FIXED by adding explicit backend
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')

    return render(request, 'register.html')


# Login Page (FIXED BACKEND ERROR)
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            # FIXED by adding explicit backend
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password.'})

    return render(request, 'login.html')


# Dashboard Page
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')


# News Page
@login_required(login_url='login')
def news(request):
    return render(request, 'news.html')


# Chatbot Page
@login_required(login_url='login')
def chatbot(request):
    response = ""
    predefined_answers = {
        "how to book a token": "Go to the Digital Token section and book your token online.",
        "how to give feedback": "Go to the Feedback page and fill the feedback form.",
        "contact support": "You can contact support from the Contact page.",
        "what is quick desk": "Quick Desk is your digital student service portal."
    }

    if request.method == "POST":
        question = request.POST.get("question", "").lower()
        answer = predefined_answers.get(question)

        # If the bot doesn't know the answer, save it in UnansweredQuestion
        if not answer:
            answer = "Sorry, I don't know the answer. Our team will get back to you."
            from .models import UnansweredQuestion
            UnansweredQuestion.objects.create(question=question)

        # Save every chat in ChatMessage
        ChatMessage.objects.create(user=request.user, question=question, answer=answer)

        response = answer

    messages_list = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:10]

    context = {
        'messages': messages_list,
        'response': response
    }
    return render(request, 'chatbot.html', context)


# Feedback View
@login_required(login_url='login')
def feedback_view(request):
    quotes = [
        "Feedback is the breakfast of champions.",
        "Your opinion matters — help us improve!",
        "Constructive feedback makes services better.",
    ]

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        rating = int(request.POST.get("rating", 5))
        if feedback_text.strip():
            Feedback.objects.create(
                user=request.user,
                feedback_text=feedback_text,
                rating=rating
            )
            messages.success(request, "Thank you for your feedback! 🌟")
            return redirect('feedback')

    return render(request, 'feedback.html', {"quotes": quotes})


# Contact Page
#@login_required(login_url='login')
def contact(request):
    return render(request, 'contact.html')


# Token Booking Logic
@login_required(login_url='login')
def token_booking(request, section_id):
    section = get_object_or_404(TokenSection, id=section_id)
    message = ""
    user_booking = None
    today = timezone.now().date()

    # Check if user already booked today
    existing_booking = TokenBooking.objects.filter(
        user=request.user, section=section, booked_at__date=today
    ).first()

    if existing_booking:
        message = f"You already have token {existing_booking.token_number} for {section.name} today."
        user_booking = existing_booking
    else:
        # Increment current token in section
        section.current_token += 1
        section.save()

        # Create booking
        booking = TokenBooking.objects.create(
            user=request.user,
            section=section,
            token_number=section.current_token
        )
        user_booking = booking
        message = f"Your token {booking.token_number} for {section.name} is confirmed. Token valid only for today."

    # Calculate expected time (5 min per token)
    expected_time = max(0, (user_booking.token_number - section.current_token) * 5)

    context = {
        "section": section,
        "user_booking": user_booking,
        "expected_time": expected_time,
        "message": message
    }
    return render(request, "token_booking.html", context)

@login_required(login_url='login')
def token(request):
    return render(request, 'token.html')


# Configure the SDK
genai.configure(api_key=settings.GEMINI_API_KEY)

def ask_gemini(request):
    prompt = request.GET.get('q', 'Hello!')
    
    # Keeping your model choice as 2.5
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    response = model.generate_content(prompt)
    
    return JsonResponse({'response': response.text})

def gemini_chat_view(request):
    user_query = request.GET.get('q', '')
    model = genai.GenerativeModel('gemini-2.5-flash')

    def stream_generator():
        # Using stream=True for the word-by-word effect
        response = model.generate_content(user_query, stream=True)
        for chunk in response:
            yield chunk.text

    return StreamingHttpResponse(stream_generator(), content_type='text/plain')