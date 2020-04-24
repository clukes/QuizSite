# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from quiz.models import GenericQuestion, User, Game, TextResponse, User, Quiz, Round
from django.template import defaultfilters
from django.db import close_old_connections
from urllib.parse import parse_qs
from channels.auth import login, logout, get_user
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser

class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).

        query_string = parse_qs(scope['query_string'])
        if b'userID' in query_string:
            try:
                user = User.objects.get(id=int(query_string[b'userID'][0]))
            except User.DoesNotExist:
                user = AnonymousUser()
            close_old_connections()
        else:
            user = AnonymousUser()
        scope['user'] = user
        # Return the inner application directly and let it run everything else
        return self.inner(scope)

QueryAuthMiddlewareStack = lambda inner: QueryAuthMiddleware(AuthMiddlewareStack(inner))

class GameConsumer(WebsocketConsumer):
    def get_current_screen(self, data):
        try:
            userID = data['userID']
            user = User.objects.get(id=userID)
            game = user.game
            if(game is None):
                return
            else:
                data['user'] = user
                data['game'] = game
                self.screen_commands[game.currentScreen](self, data)
        except User.DoesNotExist:
            return

    def get_game_start(self, data):
        message = {
            'command': 'gameStart',
        }
        self.send_message_to_group(message)

    def get_quiz_start(self, data):
        user = data['user']
        game = data['game']
        quiz = game.currentQuiz

        message = {
            'command': 'quizStart',
            'quizTitle': quiz.title,
            'quizNumber': quiz.number,
            'quizDesc': quiz.description
        }
        self.send_message(message)

    def get_quiz_end(self, data):
        user = data['user']
        game = data['game']
        quiz = game.currentQuiz
        scores = game.get_scores()
        message = {
            'command': 'quizEnd',
            'quizTitle': quiz.title,
            'quizNumber': quiz.number,
            'scoresHTML': self.scores_to_html(scores)
        }
        self.send_message(message)

    def get_round_start(self, data):
        user = data['user']
        game = data['game']
        round = game.currentRound

        message = {
            'command': 'roundStart',
            'roundTitle': round.title,
            'roundNumber': round.number,
            'roundDesc': round.description
        }
        self.send_message(message)

    def get_round_end(self, data):
        user = data['user']
        game = data['game']
        round = game.currentRound
        scores = game.get_scores()
        message = {
            'command': 'roundEnd',
            'roundTitle': round.title,
            'roundNumber': round.number,
            'scoresHTML': self.scores_to_html(scores)
        }
        self.send_message(message)

    def get_question_answering(self, data):
        self.get_question(data, False)

    def get_question_marking(self, data):
        self.get_question(data, True)

    screen_commands = {
        'gs': get_game_start,
        'qs': get_quiz_start,
        'qe': get_quiz_end,
        'rs': get_round_start,
        're': get_round_end,
        'qa': get_question_answering,
        'qm': get_question_marking,
    }

    def get_question(self, data, marking):
        user = data['user']
        game = data['game']
        question = game.currentQuestion
        answer = question.get_detail().get_user_response(user, game).response
        content = {
            'command': 'question',
            'question': self.question_to_json(question),
            'marking': marking,
            'answer': answer
        }
        self.send_message(content)


    def change_question(self, data):
        try:
            questionID = data['questionID']
            gameID = data['gameID']
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            game.currentQuiz = question.round.quiz
            game.currentRound = question.round
            game.currentQuestion = question
            game.currentScreen = 'qa'
            game.save()
            content = {
                'command': 'question',
                'question': self.question_to_json(question),
                'marking': False
            }
        except Game.DoesNotExist:
            print("Game does not exist")
            content = {
                'command': 'question',
                'question': {}
            }
        except GenericQuestion.DoesNotExist:
            print("Question does not exist")
            content = {
                'command': 'question',
                'question': {}
            }
        self.send_question_to_group(content)

    def mark_question(self, data):
        try:
            questionID = data['questionID']
            gameID = data['gameID']
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            game.currentQuiz = question.round.quiz
            game.currentRound = question.round
            game.currentQuestion = question
            game.currentScreen = 'qm'
            game.save()
            content = {
                'command': 'question',
                'question': self.question_to_json(question),
                'marking': True
            }
        except Game.DoesNotExist:
            print("Game does not exist")
            content = {
                'command': 'question',
                'question': {}
            }
        except GenericQuestion.DoesNotExist:
            print("Question does not exist")
            content = {
                'command': 'question',
                'question': {}
            }
        self.send_message_to_group(content)

    def show_answer(self, data):
        responseID = data['responseID']
        try:
            response = TextResponse.objects.get(id=responseID)
            content = {
                'command': 'showAnswer',
                'questionID': response.question.generic_question.id,
                'username': response.user.username,
                'answerHTML': self.answer_to_html(response)
            }
        except TextResponse.DoesNotExist:
            print("Game does not exist")
            content = {
                'command': 'showAnswer',
                'question': {}
            }

        self.send_message_to_group(content)

    def mark_answer(self, data):
        # Update points for answer. Then reshow answer to users.
        try:
            responseID = data['responseID']
            marking = data['marking']
            points = data['points']
            response = TextResponse.objects.get(id=responseID)
            response.marking = marking
            response.points = points
            response.save()
            content = {
                'command': 'markedAnswer',
                'responseID': responseID,
                'marking': response.get_marking_display(),
                'points': response.get_points(),
            }
            print(content)
            self.send_message(content)
            self.show_answer(data)
        except TextResponse.DoesNotExist:
            pass

    def show_all_answers(self, data):
        questionID = data['questionID']
        gameID = data['gameID']
        try:
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            answers = question.detail.get_all_responses(game)
            content = {
                'command': 'showAllAnswers',
                'questionID': questionID,
                'answersHTML': self.answers_to_html(answers)
            }
        except GenericQuestion.DoesNotExist:
            print("Question does not exist")
            content = {
                'command': 'showAllAnswers',
                'question': {}
            }
        except Game.DoesNotExist:
            print("Game does not exist")
            content = {
                'command': 'showAllAnswers',
                'question': {}
            }


        self.send_message_to_group(content)

    def set_text_answer(self, data):
        try:
            userID = data['userID']
            questionID = data['questionID']
            answer = data['answer']
            gameID = data['gameID']
            game = Game.objects.get(id=gameID)
            user = User.objects.get(id=userID)
            question = GenericQuestion.objects.get(id=questionID)
            if(question.type == 't'):
                response, created = TextResponse.objects.get_or_create(user=user, question=question.detail, game=game)
                response.response = answer
                response.save()
                content = {
                    'username': user.username,
                    'answer': answer,
                    'questionID': question.id
                }
            else:
                content = {}
        except (User.DoesNotExist, GenericQuestion.DoesNotExist, Game.DoesNotExist) as e:
            content = {}

        message = {
            'command': 'answer',
            'answer': content
        }
        self.send_message_to_group(message)

    def get_player_list(self, data):
        try:
            gameID = data['gameID']
            game = Game.objects.get(id=gameID)
            playerList = list(game.get_connected_players_list())
            formattedPlayerList = ''.join(map("<li id='plist-{0}'>{0}</li>".format, playerList))
            content = {
                'command': 'playerList',
                'playerList': formattedPlayerList
            }
        except (User.DoesNotExist, Game.DoesNotExist) as e:
            content = {}
        self.send_message(content)

    def show_quiz_start(self, data):
        try:
            gameID = data['gameID']
            quizID = data['quizID']
            quiz = Quiz.objects.get(id=quizID)
            game = Game.objects.get(id=gameID)
            game.currentQuiz = quiz
            game.currentScreen = 'qs'
            game.save()

            message = {
                'command': 'quizStart',
                'quizTitle': quiz.title,
                'quizNumber': quiz.number,
                'quizDesc': quiz.description
            }
        except (Quiz.DoesNotExist, Game.DoesNotExist) as e:
            message = {}
        self.send_message_to_group(message)

    def show_quiz_end(self, data):
        try:
            gameID = data['gameID']
            quizID = data['quizID']
            quiz = Quiz.objects.get(id=quizID)
            game = Game.objects.get(id=gameID)
            game.currentQuiz = quiz
            game.currentScreen = 'qe'
            game.save()
            scores = game.get_scores()
            message = {
                'command': 'quizEnd',
                'quizTitle': quiz.title,
                'quizNumber': quiz.number,
                'scoresHTML': self.scores_to_html(scores)
            }
        except (Quiz.DoesNotExist, Game.DoesNotExist) as e:
            message = {}
        self.send_message_to_group(message)

    def show_round_start(self, data):
        try:
            gameID = data['gameID']
            roundID = data['roundID']
            round = Round.objects.get(id=roundID)
            game = Game.objects.get(id=gameID)
            game.currentQuiz = round.quiz
            game.currentRound = round
            game.currentScreen = 'rs'
            game.save()

            message = {
                'command': 'quizStart',
                'roundTitle': round.title,
                'roundNumber': round.number,
                'roundDesc': round.description
            }
        except (Round.DoesNotExist, Game.DoesNotExist) as e:
            message = {}
        self.send_message_to_group(message)

    def show_round_end(self, data):
        try:
            gameID = data['gameID']
            roundID = data['roundID']
            round = Round.objects.get(id=roundID)
            game = Game.objects.get(id=gameID)
            game.currentQuiz = round.quiz
            game.currentRound = round
            game.currentScreen = 're'
            game.save()
            scores = game.get_scores()
            message = {
                'command': 'roundEnd',
                'roundTitle': round.title,
                'roundNumber': round.number,
                'scoresHTML': self.scores_to_html(scores)
            }
        except (Round.DoesNotExist, Game.DoesNotExist) as e:
            message = {}
        self.send_message_to_group(message)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def question_to_json(self, question):
        if(question is None):
            return None

        return {
            'id': question.id,
            'number': question.number,
            'question': question.question
        }

    def answer_to_html(self, response):
        username = response.user.username
        answer = response.response
        marking = response.get_marking_display()
        points = defaultfilters.floatformat(response.points, "-2")
        html = (f"<span id=\"{username}\">"
                f"<strong>{username}</strong> - {answer} "
                f"({marking}, {points} points)"
                f"<br></span>")
        return html

    def answers_to_html(self, answers):
        html = ''.join(map(self.answer_to_html, answers))
        return html

    def score_to_html(self, ranking, userScore):
        username = userScore.user.username
        points = defaultfilters.floatformat(userScore.score, "-2")
        html = (f"<span id=\"{username}\">"
                f"<strong>{ranking}. {username}</strong> - {points} points"
                f"<br></span>")
        return html

    def scores_to_html(self, scores):
        scoresDict = {rank+1: key for rank, key in enumerate(scores)}
        html = ''.join(self.score_to_html(k, v) for k, v in scoresDict.items())
        return html


    commands = {
            'get_current_screen': get_current_screen,
            'change_question': change_question,
            'set_text_answer': set_text_answer,
            'mark_question': mark_question,
            'show_answer': show_answer,
            'mark_answer': mark_answer,
            'show_all_answers': show_all_answers,
            'get_player_list': get_player_list,
            'show_quiz_start': show_quiz_start,
            'show_quiz_end': show_quiz_end,
            'show_round_start': show_round_start,
            'show_round_end': show_round_end
        }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'game_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        user = self.scope["user"]
        if user.id is not None:
            user.connect()
            self.send_player_connect_or_disconnect("playerConnect", user)

    def disconnect(self, close_code):
        # Leave room group
        user = self.scope["user"]
        if user.id is not None:
            user.disconnect()
            self.send_player_connect_or_disconnect("playerDisconnect", user)
        self.scope["user"] = AnonymousUser()
        self.scope["session"].save()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        print("recieve" + str(self.scope["user"]))

        self.commands[data['command']](self, data)

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def send_question_to_group(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'question_to_group',
                'message': message
            }
        )

    # Receive message from room group
    def question_to_group(self, event):
        message = event['message']
        user = self.scope['user']
        answer = ""
        if user.id is not None:
            questionID = message['question']['id']
            try:
                question = GenericQuestion.objects.get(id=questionID)
                answer = question.get_detail().get_user_response(user, user.game).response
            except GenericQuestion.DoesNotExist:
                pass
        message['answer'] = answer
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

    def send_player_connect_or_disconnect(self, type, user):
        message = {
            'command': type,
            'username': user.username
        }
        self.send_message_to_group(message)

    def send_message_to_group(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'message_to_group',
                'message': message
            }
        )

    # Receive message from room group
    def message_to_group(self, event):
        message = event['message']

        print(message)
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
