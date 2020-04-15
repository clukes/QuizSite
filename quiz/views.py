from django.shortcuts import render

# Create your views here.
from quiz.models import TextResponse, Question, Round
from quiz.forms import TextReponseForm, UsernameForm

def index(request):
    """View function for home page of site."""

    name = request.session.get('name')
    if request.method == 'POST':
        username_form = UsernameForm(request.POST)
        if username_form.is_valid():
            request.session['name'] = username_form.cleaned_data['username']
            return HttpResponseRedirect(reverse('index'))

    else:
        username_form = UsernameForm()

    context = {
        'name': name,
        'form': username_form,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def leaderHome(request):
    """View function for the leader landing screen"""
    return render(request, 'leader/index.html')




from django.views import generic
from django.views.generic.edit import FormMixin

class RoundListView(generic.ListView):
    model = Round
    template_name = 'leader/round_list.html'

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse


class RoundDetailView(generic.DetailView):
    model = Round
    template_name = 'leader/round_detail.html'

class QuestionDetailView(generic.DetailView, FormMixin):
    model = Question
    form_class = TextReponseForm
    template_name = 'leader/question_detail.html'

    def post(self, request, *args, **kwargs):
        text_response_form = self.get_form()
        if text_response_form.is_valid():
            text_response = TextResponse()
            text_response.response = text_response_form.cleaned_data['response']
            question_id = request.POST.get('question_id')
            text_response.question = Question.objects.get(id=question_id)

            text_response.save()

            return HttpResponseRedirect(request.path_info)
        else:
            return self.form_invalid(text_response_form)

    def get_context_data(self, **kwargs):
        context = super(QuestionDetailView, self).get_context_data()
        context['text_response_form'] = self.get_form()
        return context


from django.shortcuts import render

def room(request, room_name):
    return render(request, 'leader/room.html', {
        'room_name': room_name
    })
