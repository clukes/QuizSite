# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from quiz.models import GenericQuestion, User, Game, GenericResponse, TextResponse, UserScore, UserProgressiveStage, Quiz, Round, FinalResults
from quiz.forms import MultipleChoiceForm
from django.template import defaultfilters
from django.db import close_old_connections
from urllib.parse import parse_qs
from channels.auth import login, logout, get_user
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.core import serializers
from django.utils import timezone
from django.db.models import F
import ast
from decimal import Decimal
import math

MAP_MAX_DISTANCES = {
    'world_mill': 200,
    'uk_regions_mill': 10,
}

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
        game = data['game']
        quiz = game.currentQuiz
        scores = game.get_scores()
        message = {
            'command': 'quizEnd',
            'quizTitle': quiz.title,
            'quizNumber': quiz.number,
            'scoresDict': self.scores_to_dict(scores)
        }
        self.send_message(message)

    def get_round_start(self, data):
        game = data['game']
        round = game.currentRound

        message = {
            'command': 'roundStart',
            'roundTitle': round.title,
            'roundNumber': round.number,
            'roundDesc': round.description,
            'roundImg': round.background_image_url
        }
        self.send_message(message)

    def get_round_transition(self, data):
        message = {
            'command': 'roundTransition'
        }
        self.send_message(message)

    def get_round_end(self, data):
        game = data['game']
        round = game.currentRound
        scores = game.get_scores()
        print(scores)
        scoresDict = {key:UserScore.objects.filter(game=game,score__gt=key.score).count()+1 for rank, key in enumerate(scores)}
        message = {
            'command': 'roundEnd',
            'roundTitle': round.title,
            'roundNumber': round.number,
            'scoresHTML': self.scores_to_html(scoresDict)
        }
        self.send_message(message)

    def get_question_answering(self, data):
        self.get_question(data, False)

    def get_question_marking(self, data):
        self.get_question(data, True)

    def get_final_results(self, data):
        message = {
            'command': 'finalResults',
            'draw': FinalResults.objects.first().draw
        }
        self.send_message(message)

    screen_commands = {
        'gs': get_game_start,
        'qs': get_quiz_start,
        'qe': get_quiz_end,
        'rs': get_round_start,
        'rt': get_round_transition,
        're': get_round_end,
        'qa': get_question_answering,
        'qm': get_question_marking,
        'fr': get_final_results
    }

    def get_question(self, data, marking):
        user = data['user']
        game = data['game']
        question = game.currentQuestion
        answer = question.get_user_response(user, game).get_response()
        timerEnd = None
        if not marking:
            if game.timerEnd:
                timerEnd = str(game.timerEnd.isoformat())
        currentStage = 0
        if question.question_type == 'p':
            userStage, created = UserProgressiveStage.objects.get_or_create(user=user, game=game, question=question.detail)
            currentStage = userStage.current_stage
        content = {
            'command': 'question',
            'question': self.question_to_json(question),
            'marking': marking,
            'answer': answer,
            'currentStage': currentStage,
            'timerEnd': timerEnd,
            'timeRemaining': game.get_time_remaining()
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
            game.timerEnd = None
            game.save()
            content = {
                'command': 'question',
                'question': self.question_to_json(question),
                'marking': False,
                'timerEnd': None
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
            game.timerEnd = None
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
            response = GenericResponse.objects.get(id=responseID)
            content = {
                'command': 'showAnswer',
                'questionID': response.question.id,
                'username': response.user.username,
                'answerHTML': self.answer_to_html(response),
                'answer': response.get_response()
            }
        except GenericResponse.DoesNotExist:
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
            response = GenericResponse.objects.get(id=responseID)
            response.marking = marking
            response.points = points
            response.save()
            content = {
                'command': 'markedAnswer',
                'responseID': responseID,
                'marking': response.get_marking_display(),
                'points': response.get_points(),
            }
            self.send_message(content)
            self.show_answer(data)
        except GenericResponse.DoesNotExist:
            pass

    def mark_map_answer(self, data):
        # Calculate points for answer. Then reshow answer to users.
        try:
            responseID = data['responseID']
            response = GenericResponse.objects.get(id=responseID)
            coords = ast.literal_eval(response.get_response())
            correctCoords = {'lat': response.question.detail.lat, 'lng': response.question.detail.lng}
            latDist = abs(correctCoords['lat'] - Decimal(coords['lat']))
            lngDist = abs(correctCoords['lng'] - Decimal(coords['lng']))
            map = response.question.detail.map
            if(map == "world_mill"):
                latDist = min(latDist, 180-latDist)
                lngDist = min(lngDist, 360-lngDist)
            dist = math.sqrt((latDist**2) + (lngDist**2))
            print(dist)
            max_dist = MAP_MAX_DISTANCES[map]
            points = 100/(1+((dist/(max_dist/10))**((-0.00789*max_dist)+3.07894)))
            print(points)
            if(points < 10):
                points = 0
            else:
                points = round(points/100, 1)
            # points = 100*math.exp((-dist)/(max_dist/8))
            # print(points)
            # if(points > 75):
            #     points = math.ceil(points/10)/10
            # else:
            #     points = round(points/100, 1)
            # print(points)
            if(points == 1):
                marking = 'c'
            elif(points == 0):
                marking = 'i'
            else:
                marking = 'p'
            response.marking = marking
            response.points = points
            response.save()
            content = {
                'command': 'markedAnswer',
                'responseID': responseID,
                'marking': response.get_marking_display(),
                'points': response.get_points(),
            }
            self.send_message(content)
            self.show_answer(data)
        except GenericResponse.DoesNotExist:
            pass

    def show_all_answers(self, data):
        questionID = data['questionID']
        gameID = data['gameID']
        try:
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            users = game.user_set.all()
            answers = question.get_all_users_responses(users, game)
            content = {
                'command': 'showAllAnswers',
                'questionID': questionID,
                'answersHTML': self.answers_to_html(answers)
            }
            self.send_message_to_group(content)
        except GenericQuestion.DoesNotExist:
            print("Question does not exist")
        except Game.DoesNotExist:
            print("Game does not exist")

    def show_correct_answer(self, data):
        questionID = data['questionID']
        gameID = data['gameID']
        answer = data['answer']
        comparisonItems = None
        questionType = 't'
        coords = None
        try:
            question = GenericQuestion.objects.get(id=questionID)
            questionType = question.question_type
            if questionType == 'g':
                question = GenericQuestion.objects.get(id=questionID)
                game = Game.objects.get(id=gameID)
                users = game.user_set.all()
                answers = question.get_all_users_responses(users, game)
                comparisonItems = self.answers_to_comparisonItems(answers)
            elif questionType == 'w':
                coords = {"lat": str(question.detail.lat), "lng": str(question.detail.lng)}
        except (GenericQuestion.DoesNotExist, Game.DoesNotExist, TextResponse.DoesNotExist) as e:
            pass
        content = {
            'command': 'correctAnswer',
            'questionID': questionID,
            'questionType': questionType,
            'comparisonItems': comparisonItems,
            'answer': answer,
            'coords': coords
        }
        self.send_message_to_group(content)

    def set_timer(self, data):
        try:
            questionID = data['questionID']
            gameID = data['gameID']
            timerLength = int(data['timerLength'])
            question = GenericQuestion.objects.get(id=questionID)
            game = Game.objects.get(id=gameID)
            if(game.currentQuestion == question):
                game.timerEnd = timezone.now() + timezone.timedelta(seconds=timerLength)
                game.save()
                content = {
                    'command': 'timer',
                    'questionID': questionID,
                    'timerEnd': str(game.timerEnd.isoformat()),
                    'timeRemaining': game.get_time_remaining()
                }
                self.send_message_to_group(content)
        except Game.DoesNotExist:
            print("Game does not exist")
        except GenericQuestion.DoesNotExist:
            print("Question does not exist")

    def set_text_answer(self, data):
        try:
            userID = data['userID']
            questionID = data['questionID']
            answer = data['answer']
            gameID = data['gameID']
            maxPoints = data['maxPoints']
            game = Game.objects.get(id=gameID)
            user = User.objects.get(id=userID)
            question = GenericQuestion.objects.get(id=questionID)
            if(question.question_type in ['t', 'm', 'p', 'g', 'w']):
                type = 't'
                if(question.question_type == 'w'):
                    type = 'w'
                response, created = GenericResponse.objects.get_or_create(user=user, question=question, game=game, type=type)
                if response.response_detail is None:
                    text_response = TextResponse(response=answer)
                    text_response.save()
                    response.add_response(text_response)
                else:
                    response_detail = response.response_detail
                    response_detail.response = answer
                    response_detail.save()

                response.type = type
                if(maxPoints):
                    response.max_points = maxPoints
                response.save()
                content = {
                    'username': user.username,
                    'answer': answer,
                    'questionID': question.id,
                    'maxPoints': defaultfilters.floatformat(maxPoints, "-2")
                }
                message = {
                    'command': 'answer',
                    'answer': content
                }
                self.send_message_to_group(message)
        except (User.DoesNotExist, GenericQuestion.DoesNotExist, TextResponse.DoesNotExist, Game.DoesNotExist) as e:
            pass

    def set_ordering_answer(self, data):
        try:
            userID = data['userID']
            questionID = data['questionID']
            answer = data['answer']
            gameID = data['gameID']
            maxPoints = data['maxPoints']
            game = Game.objects.get(id=gameID)
            user = User.objects.get(id=userID)
            question = GenericQuestion.objects.get(id=questionID)

            if(question.question_type in ['o']):
                maxPoints = question.detail.max_points
                i = 0
                correct = 0
                points = 0

                for element in answer:
                    ordering_element = question.detail.elements.get(pk=answer[i])
                    if(question.detail.elements.get(pk=answer[i]).correct_ordering == i+1):
                        correct += 1
                    i += 1

                if(i > 0):
                    points = (correct * float(maxPoints)) / i

                marking='p'
                if(points == maxPoints):
                    marking='c'
                elif(points == 0):
                    marking='i'

                textAnswer = ', '.join([str(question.detail.elements.get(pk=i)) for i in answer])
                response, created = GenericResponse.objects.get_or_create(user=user, question=question, game=game, type='t')
                if response.response_detail is None:
                    text_response = TextResponse(response=textAnswer)
                    text_response.save()
                    response.add_response(text_response)
                else:
                    response_detail = response.response_detail
                    response_detail.response = textAnswer
                    response_detail.save()

                response.max_points = maxPoints
                response.marking=marking
                response.points=points
                response.save()

                content = {
                    'username': user.username,
                    'answer': textAnswer,
                    'questionID': question.id,
                    'maxPoints': defaultfilters.floatformat(maxPoints, "-2"),
                    'points': points,
                    'marking': response.get_marking_display()
                }
                message = {
                    'command': 'answer',
                    'answer': content
                }
                self.send_message_to_group(message)
        except (User.DoesNotExist, GenericQuestion.DoesNotExist, TextResponse.DoesNotExist, Game.DoesNotExist) as e:
            pass

    def increment_user_progressive_stage(self, data):
        try:
            questionID = data['questionID']
            question = GenericQuestion.objects.get(id=questionID)
            if(question.question_type == 'p'):
                gameID = data['gameID']
                userID = data['userID']
                currentStage = data['currentStage']
                maxPoints = data['maxPoints']

                game = Game.objects.get(id=gameID)
                user = User.objects.get(id=userID)

                UserProgressiveStage.objects.filter(game=game, user=user, question=question.detail).update(current_stage = F("current_stage") + 1)

                response = GenericResponse.objects.get(game=game, user=user, question=question)
                response.max_points = maxPoints
                response.save()

                message = {
                    'command': 'updateMaxPoints',
                    'responseID': response.id,
                    'maxPoints': defaultfilters.floatformat(maxPoints, "-2")
                }
                self.send_message_to_group(message)
        except (User.DoesNotExist, GenericQuestion.DoesNotExist, UserProgressiveStage.DoesNotExist, Game.DoesNotExist, GenericResponse.DoesNotExist) as e:
            pass

    def get_player_list(self, data):
        try:
            gameID = data['gameID']
            game = Game.objects.get(id=gameID)
            playerList = list(game.get_connected_players_list())
            formattedPlayerList = ''.join(map("<p id='plist-{0}'>{0}</p>".format, playerList))
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
                'scoresDict': self.scores_to_dict(scores)
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
                'command': 'roundStart',
                'roundTitle': round.title,
                'roundNumber': round.number,
                'roundDesc': round.description,
                'roundImg': round.background_image_url
            }
        except (Round.DoesNotExist, Game.DoesNotExist) as e:
            message = {}
        self.send_message_to_group(message)


    def show_round_transition(self, data):
        try:
            gameID = data['gameID']
            game = Game.objects.get(id=gameID)
            game.currentScreen = 'rt'
            game.save()

            message = {
                'command': 'roundTransition',
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
            scoresDict = {key:UserScore.objects.filter(game=game,score__gt=key.score).count()+1 for rank, key in enumerate(scores)}
            message = {
                'command': 'roundEnd',
                'roundTitle': round.title,
                'roundNumber': round.number,
                'scoresHTML': self.scores_to_html(scoresDict)
            }
        except (Round.DoesNotExist, Game.DoesNotExist) as e:
            message = {}
        self.send_message_to_group(message)

    def calculate_final_results(self, data):
        try:
            gameID = data['gameID']
            game = Game.objects.get(id=gameID)
            scores = UserScore.objects.filter(game=game).order_by('-score')
            print(scores)
            for userscore in scores:
                rank = UserScore.objects.filter(game=game,score__gt=userscore.score).count() + 1
                print(rank)
                try:
                    resultsObj = FinalResults.objects.get(user=userscore.user)
                    resultsObj.total_score += userscore.score
                    resultsObj.weighted_score += Decimal((2 - ((rank-1)*0.25)))
                    places = ['first', 'second', 'third', 'fourth']
                    setattr(resultsObj, places[rank-1], F(places[rank-1]) + 1)
                    resultsObj.save()
                except FinalResults.DoesNotExist:
                    pass
            draw = False
            results = FinalResults.objects.order_by('-weighted_score')
            if(results[0].weighted_score == results[1].weighted_score):
                draw = True
            FinalResults.objects.all().update(video_loaded=False, draw=draw)
            self.send_message({'command': 'calculatedFinalResults', 'draw': FinalResults.objects.first().draw})
        except Game.DoesNotExist:
            pass

    def show_final_results(self, data):
        try:
            gameID = data['gameID']
            game = Game.objects.get(id=gameID)
            game.currentQuiz = None
            game.currentRound = None
            game.currentScreen = 'fr'
            game.save()
            FinalResults.objects.all().update(video_loaded=False)
            message = {
                'command': 'finalResults',
                'draw': FinalResults.objects.first().draw
            }
        except Game.DoesNotExist:
            message = {}
        self.send_message_to_group(message)

    def set_video_load(self, data):
        try:
            userID = data['userID']
            loaded = data['loaded']
            user = User.objects.get(id=userID)
            resultObj = FinalResults.objects.get(user=user)
            resultObj.video_loaded = loaded
            resultObj.save()
            if(not FinalResults.objects.filter(video_loaded=False).exists()):
                message = {
                    'command': 'allLoaded',
                }
                self.send_message_to_group(message)
        except (FinalResults.DoesNotExist, User.DoesNotExist) as e:
            pass

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def question_to_json(self, question):
        if(question is None):
            return None
        image = None
        multiple_choice_form = None
        progressive_info = None
        ordering_elements = None
        map = None
        if question.question_type == 'm':
            multiple_choice_form = MultipleChoiceForm(instance = question.detail).as_p()
        elif question.question_type == 'p':
            progressive_stages = serializers.serialize("json", question.detail.stages.all())
            progressive_info = {'max_points': defaultfilters.floatformat(question.detail.max_points, "-2"),
                                'min_points': defaultfilters.floatformat(question.detail.min_points, "-2"),
                                'step': defaultfilters.floatformat(question.detail.step, "-2"),
                                'stages': progressive_stages}
        elif question.question_type == 'o':
            ordering_elements = serializers.serialize("json", question.detail.elements.all().order_by('display_ordering'), fields=["text", "display_ordering"])
        elif question.question_type == 'w':
            map = question.detail.map
        return {
            'id': question.id,
            'number': question.number,
            'question': question.question,
            'question_type': question.question_type,
            'media_type': question.media_type,
            'media_url': question.media_url,
            'multiple_choice_form': multiple_choice_form,
            'progressive_info': progressive_info,
            'ordering_elements': ordering_elements,
            'map': map
        }

    def construct_correct_icon(self, points):
        return '<i class="fas fa-check-circle"></i>'

    def construct_incorrect_icon(self, points):
        return '<i class="fas fa-times-circle"></i>'

    def construct_partial_icon(self, points):
        numerator, denominator = points.as_integer_ratio()
        if points == 1:
            return self.construct_correct_icon(points)
        elif points > 1:
            if(denominator == 1):
                return f"""<span class="fa-layers fa-fw">
                <i class="fas fa-circle" style="color:limegreen"></i>
                 <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-5 up-0.25" style="font-weight:800;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;
                ">+{numerator}</span>
                 </span>"""
            else:
                return f"""<span class="fa-layers fa-fw">
                <i class="fas fa-circle" style="color:limegreen"></i>
                <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-8 left-5" style="font-weight:700;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;
                ">+</span>
                 <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-9 left-0.5 up-2.75" style="font-weight:700;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;
                ">{numerator}</span>
                <i class="fa-layers fa-fw fas fa-slash" data-fa-transform="shrink-10 rotate-80 up-0.5 right-1.75" style="font-weight:700;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;"></i>
                <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-9 right-4 down-1.75" style="font-weight:700;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;
                ">{denominator}</span>
                 </span>"""
        else:
            return f"""<span class="fa-layers fa-fw">
            <i class="fas fa-circle" style="color:darkorange"></i>
             <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-7 left-3.25 up-1.5" style="font-weight:800;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;
            ">{numerator}</span>
            <i class="fa-layers fa-fw fas fa-slash" data-fa-transform="shrink-9 rotate-80" style="font-weight:800;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;"></i>
            <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-7.75 right-3 down-1.75" style="font-weight:800;color:#2B3E50;font-family:Arial Rounded MT Bold, Arial;  font-weight: bold;
            ">{denominator}</span>
             </span>"""


    MARKING_ICONS = {
        'c': construct_correct_icon,
        'i': construct_incorrect_icon,
        'p': construct_partial_icon
    }

    def answer_to_html(self, response):
        username = response.user.username
        answer = response.get_response()
        marking = self.MARKING_ICONS[response.marking](self, response.points)
        points = defaultfilters.floatformat(response.points, "-2")
        bonus=""
        if(response.type == "w"):
            answer = ""
        if(response.points > response.max_points):
            bonus="<span style='color:lawngreen'> Bonus!</span>"
        html = (f"<span id='answers-{username}'>"
                f"<strong>{username}</strong> - {answer} "
                f"{marking} ({points} points){bonus} <br></span>")
        return html

    def answers_to_html(self, answers):
        html = ''.join(map(self.answer_to_html, answers))
        return html

    def answers_to_comparisonItems(self, answers):
        comparisonItems = [{"keyword": response.get_response(),"geo":"GB","time":"today 12-m"} for response in answers if response.get_response() is not None]
        return comparisonItems

    def score_to_html(self, userScore, ranking):
        username = userScore.user.username
        points = defaultfilters.floatformat(userScore.score, "-2")
        html = (f"<span class='score' id='scores-{username}'>"
                f"<strong>{ranking}. {username}</strong> - {points} points"
                f"<br></span>")
        return html

    def scores_to_html(self, scoresDict):
        print(scoresDict)
        html = ''.join(self.score_to_html(k, v) for k, v in scoresDict.items())
        return html

    def scores_to_dict(self, scores):
        scoresDict = [{'username':userScore.user.username,
                        'score': defaultfilters.floatformat(userScore.score, "-2"),
                        } for userScore in scores]
        return scoresDict


    commands = {
            'get_current_screen': get_current_screen,
            'change_question': change_question,
            'set_text_answer': set_text_answer,
            'set_ordering_answer': set_ordering_answer,
            'increment_user_progressive_stage': increment_user_progressive_stage,
            'mark_question': mark_question,
            'show_answer': show_answer,
            'mark_answer': mark_answer,
            'mark_map_answer': mark_map_answer,
            'show_all_answers': show_all_answers,
            'show_correct_answer': show_correct_answer,
            'set_timer': set_timer,
            'get_player_list': get_player_list,
            'show_quiz_start': show_quiz_start,
            'show_quiz_end': show_quiz_end,
            'show_round_start': show_round_start,
            'show_round_transition': show_round_transition,
            'show_round_end': show_round_end,
            'calculate_final_results': calculate_final_results,
            'show_final_results': show_final_results,
            'set_video_load': set_video_load
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
        currentStage = 0
        if user.id is not None:
            questionID = message['question']['id']
            game = user.game
            try:
                question = GenericQuestion.objects.get(id=questionID)
                answer = question.get_user_response(user, user.game).get_response()
                if question.question_type == 'p':
                    userStage, created = UserProgressiveStage.objects.get_or_create(user=user, game=game, question=question.detail)
                    currentStage = userStage.current_stage
            except GenericQuestion.DoesNotExist:
                pass
        message['answer'] = answer
        message['currentStage'] = currentStage

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

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
