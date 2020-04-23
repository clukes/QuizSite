from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.
from quiz.models import GenericQuestion, TextQuestion, TextResponse, Round, Game, User, UserScore
from quiz.forms import TextReponseForm, UsernameForm, JoinRoomForm
from django.contrib import messages
from django.db import IntegrityError

def index(request):
    """View function for home page of site."""
    if request.method == 'POST':
        if 'set-name' in request.POST:
            username_form = UsernameForm(request.POST)
            if username_form.is_valid():
                try:
                    name = username_form.cleaned_data['username']
                    user = User()
                    user.username = name
                    user.save()
                    request.session['userID'] = user.id
                    request.session['username'] = user.username
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
                        userScore, created = UserScore.objects.get_or_create(user=user, game=game)
                        request.session['currentGameCode'] = game.id
                    else:
                        messages.add_message(request, messages.ERROR, "The game has ended.")
                except User.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "User not in database.")
                    request.session['userID'] = None
                    request.session['username'] = None
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
                request.session['username'] = None
            request.session['currentGameCode'] = None
            return HttpResponseRedirect(reverse('index'))

    else:
        username_form = UsernameForm()
        join_room_form = JoinRoomForm()

    context = {
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
                request.session['username'] = None
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
                request.session['username'] = None
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

class GenericQuestionDetailView(generic.DetailView):
    model = GenericQuestion
    template_name = 'leader/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GenericQuestionDetailView, self).get_context_data()
        try:
            gameID = self.request.session.get('currentGameCode')
            game = Game.objects.get(id=gameID)
            users = game.user_set.all()
            question = self.get_object()
            answers = {}
            for user in users:
                response = user.get_response(question)
                print(response)
                answers[user.username] = response
            context['answers'] = answers
        except Game.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, "No game running.")
        return context


from django.shortcuts import render

def leader_room(request, room_code):
    return render(request, 'leader/room.html', {
        'room_code': room_code
    })

def player_game(request):
    answer = ''
    try:
        userID = request.session.get('userID')
        user = User.objects.get(id=userID)
        gameID = request.session.get('currentGameCode')
        game = Game.objects.get(id=gameID)
        if(not game.active):
            messages.add_message(request, messages.ERROR, "Game has ended.")
            request.session['currentGameCode'] = None
            return HttpResponseRedirect(reverse('index'))
        if(game.currentQuestion):
            answer = game.currentQuestion.get_detail().get_user_response(user, game)
    except Game.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Game doesn't exist.")
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        text_response_form = TextReponseForm(request.POST)
        if text_response_form.is_valid():
            questionID = request.POST.get('question_id')
            question = GenericQuestion.objects.get(id=questionID)
            text_response, created = TextResponse.objects.get_or_create(question=question.get_detail(), user=user, game=game)
            text_response.response = text_response_form.cleaned_data['response']
            text_response.save()

            return HttpResponseRedirect(request.path_info)
        else:
            return self.form_invalid(text_response_form)

        return HttpResponseRedirect(reverse('player-room'))

    else:
        text_response_form = TextReponseForm()

    context = {
        'form': text_response_form,
        'answer': answer
    }
    return render(request, 'game.html', context=context);
