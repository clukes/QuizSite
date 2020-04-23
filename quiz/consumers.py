# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from quiz.models import GenericQuestion, User, Game, TextResponse, QUESTION_TYPES
from django.template import defaultfilters

class GameConsumer(WebsocketConsumer):
    def get_question(self, data):
        try:
            userID = data['userID']
            user = User.objects.get(id=userID)
            game = user.game
            if(game is None):
                content = {
                    'command': 'question',
                    'question': {}
                }
            else:
                question = user.game.currentQuestion
                content = {
                    'command': 'question',
                    'question': self.question_to_json(question),
                    'marking': game.marking
                }
        except User.DoesNotExist:
            content = {
                'command': 'question',
                'question': {}
            }
        self.send_message(content)


    def change_question(self, data):
        try:
            questionID = data['questionID']
            gameID = data['gameID']
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            game.currentRound = question.round
            game.currentQuestion = question
            game.marking = False
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
        self.send_message_to_group(content)

    def mark_question(self, data):
        try:
            questionID = data['questionID']
            gameID = data['gameID']
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            game.currentRound = question.round
            game.currentQuestion = question
            game.marking = True
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
                'points': response.points,
            }
            print(content)
            self.send_message(content)
            # self.show_answer(data)
        except TextResponse.DoesNotExist:
            pass

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
        points = defaultfilters.floatformat(response.points)
        html = (f"<span id=\"{username}\">"
                f"<strong>{username}</strong> - {answer}"
                f"({marking}, {points} points)"
                f"<br></span>")
        return html

    commands = {
            'get_question': get_question,
            'change_question': change_question,
            'set_text_answer': set_text_answer,
            'mark_question': mark_question,
            'show_answer': show_answer,
            'mark_answer': mark_answer
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

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)

        self.commands[data['command']](self, data)

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

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
