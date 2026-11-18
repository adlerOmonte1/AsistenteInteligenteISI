from django.urls import path

from .views import ChatView, FeedbackView, ProbadorView

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/<int:consulta_id>/feedback/", FeedbackView.as_view(), name="chat-feedback"),
    path("probador/", ProbadorView.as_view(), name="probador"),
]
