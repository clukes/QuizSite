from django.shortcuts import render

# Create your views here.
from quiz.models import TextResponse, Question, Round

def index(request):
    """View function for home page of site."""


    context = {
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic
from django.views.generic.edit import FormMixin

class RoundListView(generic.ListView):
    model = Round

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from quiz.forms import TextReponseForm

class RoundDetailView(generic.DetailView, FormMixin):
    model = Round
    form_class = TextReponseForm

    def post(self, request, *args, **kwargs):
        text_response_form = self.get_form()
        if text_response_form.is_valid():
            text_response = TextResponse()
            text_response.response = text_response_form.cleaned_data['response']
            text_response.save()

            return HttpResponseRedirect(request.path_info)
        else:
            return self.form_invalid(text_response_form)

    def get_context_data(self, **kwargs):
        context = super(RoundDetailView, self).get_context_data()
        context['text_response_form'] = self.get_form()
        return context
