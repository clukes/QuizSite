from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.
from quiz.models import TextResponse, Question, Round, Game, User
from quiz.forms import TextReponseForm, UsernameForm, JoinRoomForm
from django.contrib import messages
from django.db import IntegrityError

def index(request):
    """View function for home page of site."""

    name = request.session.get('name')
    if request.method == 'POST':
        if 'set-name' in request.POST:
            username_form = UsernameForm(request.POST)
            if username_form.is_valid():
                try:
                    name = username_form.cleaned_data['username']
                    user = User()
                    user.username = name
                    user.save()
                    request.session['name'] = name
                    request.session['userID'] = user.id
                except IntegrityError as e:
                    messages.add_message(request, messages.ERROR, "Username not unique.")
                return HttpResponseRedirect(reverse('index'))
        elif 'join-room' in request.POST:
            join_room_form = JoinRoomForm(request.POST)
            if join_room_form.is_valid():
                try:
                    userID = request.session.get('userID')
                    user = User.objects.get(id=userID)
                    gameID = join_room_form.cleaned_data['roomCode']
                    game = Game.objects.get(id=gameID)
                    if(game.active):
                        user.game = game
                        user.save()
                        request.session['currentGameCode'] = game.id
                    else:
                        messages.add_message(request, messages.ERROR, "The game has ended.")
                except User.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "User not in database.")
                    request.session['userID'] = None
                    request.session['currentGameCode'] = None
                except Game.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "No game with that code.")
                    request.session['currentGameCode'] = None
                return HttpResponseRedirect(reverse('index'))
        elif 'enter-game' in request.POST:
            return HttpResponseRedirect(reverse('player-room'))
        elif 'leave-game' in request.POST:
            try:
                userID = request.session.get('userID')
                user = User.objects.get(id=userID)
                user.game = None
                user.save()
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, "User not in database.")
                request.session['userID'] = None
            request.session['currentGameCode'] = None
            return HttpResponseRedirect(reverse('index'))

    else:
        username_form = UsernameForm()
        join_room_form = JoinRoomForm()

    context = {
        'name': name,
        'username_form': username_form,
        'join_room_form': join_room_form,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def leaderHome(request):
    """View function for the leader landing screen"""
    if request.method == 'POST':
        if 'create-game' in request.POST:
            try:
                userID = request.session.get('userID')
                user = User.objects.get(id=userID)
                game = Game()
                game.leader = user
                game.active = True
                game.save()
                request.session['currentGameCode'] = game.id
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, "User not in database.")
                request.session['userID'] = None
                request.session['currentGameCode'] = None

            return HttpResponseRedirect(reverse('leader-home'))

        elif 'end-game' in request.POST:
            try:
                gameID = request.session.get('currentGameCode')
                game = Game.objects.get(id=gameID)
                game.active = False
                game.save()
                userID = request.session.get('userID')
                user = User.objects.get(id=userID)
                user.game = None
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, "User not in database.")
                request.session['userID'] = None
            except Game.DoesNotExist:
                messages.add_message(request, messages.ERROR, "No game running.")

            request.session['currentGameCode'] = None
            return HttpResponseRedirect(reverse('leader-home'))

    context = {
    }

    return render(request, 'leader/index.html', context)


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

def leader_room(request, room_code):
    return render(request, 'leader/room.html', {
        'room_code': room_code
    })

def player_game(request):
    try:
        gameID = request.session.get('currentGameCode')
        game = Game.objects.get(id=gameID)
        if(not game.active):
            messages.add_message(request, messages.ERROR, "Game has ended.")
            request.session['currentGameCode'] = None
            return HttpResponseRedirect(reverse('index'))
    except Game.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Game doesn't exist.")
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        text_response_form = TextReponseForm(request.POST)
        if text_response_form.is_valid():
            return HttpResponseRedirect(reverse('player-room'))

    else:
        text_response_form = TextReponseForm()

    context = {
        'form': text_response_form,
    }
    return render(request, 'game.html', context=context);
