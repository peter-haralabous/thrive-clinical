import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from sandwich.core.service.chat_service.chat import ChatContext
from sandwich.core.service.chat_service.chat import UserMessageEvent
from sandwich.core.service.chat_service.chat import receive_chat_event
from sandwich.core.service.chat_service.sse import send_user_message
from sandwich.core.util.http import AuthenticatedHttpRequest
from sandwich.patients.forms.chat import ChatForm


@login_required
@require_POST
def chat(request: AuthenticatedHttpRequest) -> HttpResponse:
    form = ChatForm(request.POST, user=request.user)
    if form.is_valid():
        patient = form.cleaned_data["patient"]
        event = UserMessageEvent(context=ChatContext(patient_id=str(patient.id)), content=form.cleaned_data["message"])

        # Update chat history to include the user's message
        send_user_message(event)

        # TODO: move this into an async job
        receive_chat_event(event)

        return HttpResponse()
    logging.error("Invalid chat form: %s", form.errors)

    context = {"chat_form": form}
    return render(request, "patient/chatty/partials/chat_form.html", context)
