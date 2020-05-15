from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.template import defaultfilters
from django.core import serializers
from django.utils import timezone

QUESTION_TYPES = (
    ('t', 'Text'),
    ('i', 'Image'),
    ('v', 'Video'),
    ('a', 'Audio')
)

RESPONSE_TYPES = (
    ('t', 'Text'),
)

class GenericQuestion(models.Model):
    """Model representing a Question."""
    number = models.IntegerField()
    round = models.ForeignKey('Round', on_delete=models.SET_NULL, null=True)
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=500)
    media_url = models.URLField(max_length=1000, null=True, blank=True)

    type = models.CharField(
        max_length=1,
        choices=QUESTION_TYPES,
        default='t',
    )
    multiple_choice = models.BooleanField(default=False)

    object_id = models.IntegerField(null=True, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    detail = GenericForeignKey(
        'content_type',
        'object_id',
    )

    class Meta:
        unique_together = (('number', 'round'), ('content_type', 'object_id'))

        ordering = ['round', 'number']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.round}: {self.question}'

    def get_absolute_url(self):
        """Returns the url to access the page for this round."""
        return reverse('question-detail', args=[str(self.round.quiz.id), str(self.round.id), str(self.id)])

    def get_detail(self):
        """Returns the detail object."""
        return self.detail

    def get_user_response(self, user, game):
        response, created = self.genericresponse_set.get_or_create(user=user, game=game)
        return response

    def get_all_users_responses(self, users, game):
        return self.genericresponse_set.filter(user__in=users, game=game).all().order_by('user')

    def get_all_responses(self, game):
        return self.genericresponse_set.filter(game=game).all().order_by('user')

class QuestionDetail(models.Model):
    class Meta:
        abstract = True

    generic_question_relation = GenericRelation('GenericQuestion')

    def __str__(self):
        """String for representing the Model object."""
        return self.generic_question.question

    @property
    def generic_question(self):
        # Return the object in exists
        # else None
        return self.generic_question_relation.first()

class TextQuestion(QuestionDetail):
    pass

class MultipleChoiceQuestion(QuestionDetail):
    pass

class MultipleChoiceOption(models.Model):
    question = models.ForeignKey('MultipleChoiceQuestion', related_name='options', on_delete=models.CASCADE, null=False)
    option = models.CharField(max_length=300)

    def __str__(self):
        """String for representing the Model object."""
        return self.option

class GenericResponse(models.Model):
    """Model representing a generic response."""
    question = models.ForeignKey('GenericQuestion', on_delete=models.CASCADE, null=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)

    MARKING_CHOICES = [
        ('c', 'Correct'),
        ('i', 'Incorrect'),
        ('p', 'Partial'),
    ]

    marking = models.CharField(
        max_length=1,
        choices=MARKING_CHOICES,
        default='i',
    )
    points = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    type = models.CharField(
        max_length=1,
        choices=RESPONSE_TYPES,
        default='t',
    )

    object_id = models.IntegerField(null=True, blank=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        null=True, blank=True
    )
    response_detail = GenericForeignKey(
        'content_type',
        'object_id',
    )

    class Meta:
        unique_together = (('question', 'user', 'game'), ('content_type', 'object_id'))

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.question}: {self.user} - {self.response_detail}'

    def add_response(self, response):
        print("ADD")
        self.content_type = ContentType.objects.get_for_model(response)
        self.object_id = response.pk
        self.save()
        return self.response_detail

    def get_response(self):
        if self.response_detail:
            return self.response_detail.response
        return None

    def get_points(self):
        return defaultfilters.floatformat(self.points, "-2")

    def save(self, *args, **kwargs):
        # recalculate user score when points is changed
        try:
            this = GenericResponse.objects.get(id=self.id)
            if this.points != self.points:
                userscore, created = UserScore.objects.get_or_create(user=self.user,game=self.game)
                userscore.score -= Decimal(this.points)
                userscore.score += Decimal(self.points)
                userscore.save()
        except GenericResponse.DoesNotExist:
            pass
        super(GenericResponse, self).save(*args, **kwargs)

class TextResponse(models.Model):
    """Model representing a text question response."""
    response = models.CharField(max_length=500, default="", help_text='Enter your answer:')

    def __str__(self):
        return self.response

from django.urls import reverse # Used to generate URLs by reversing the URL patterns

class Round(models.Model):
    """Model representing a round"""
    quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True)
    number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    background_image_url = models.URLField(max_length=300, null=True, blank=True)

    class Meta:
        ordering = ['quiz__number', 'number']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.quiz}: {self.title}'

    def get_absolute_url(self):
        """Returns the url to access the page for this round."""
        return reverse('round-detail', args=[str(self.quiz.id), str(self.id)])

    def get_first_question(self):
        return self.genericquestion_set.all().order_by('number').first()

class Quiz(models.Model):
    """Model representing a quiz"""
    number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access the page for this round."""
        return reverse('quiz-detail', args=[str(self.id)])

class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    game = models.ForeignKey('Game', on_delete=models.SET_NULL, null=True)
    connected = models.BooleanField(default=False)

    class Meta:
        ordering = ['username']

    def __str__(self):
        """String for representing the Model object."""
        return self.username

    def get_response(self, question):
        return question.get_user_response(self, self.game)

    def get_responses(self, game):
        return question.get_user_responses(self, self.game)

    def connect(self):
        self.connected = True
        self.save()

    def disconnect(self):
        self.connected = False
        self.save()

    def natural_key(self):
        return (self.id, self.username)

class UserScore(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)
    score = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user}: {self.score}'

class Game(models.Model):
    """Model representing a game"""
    leader = models.ForeignKey('User', related_name='game_leader', on_delete=models.CASCADE, null=False)
    active = models.BooleanField(default=False)
    currentQuiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, blank=True, null=True)
    currentRound = models.ForeignKey('Round', on_delete=models.SET_NULL, blank=True, null=True)
    currentQuestion = models.ForeignKey('GenericQuestion', on_delete=models.SET_NULL, blank=True, null=True)
    timerEnd = models.DateTimeField(blank=True, null=True)

    CURRENT_SCREEN_CHOICES = [
        ('gs', 'Game Start'),
        ('qs', 'Quiz Start'),
        ('qe', 'Quiz End'),
        ('rs', 'Round Start'),
        ('rt', 'Round Transition'),
        ('re', 'Round End'),
        ('qa', 'Question Answering'),
        ('qm', 'Question Marking'),
    ]
    currentScreen = models.CharField(
        max_length=2,
        choices=CURRENT_SCREEN_CHOICES,
        default='gs',
        null=False,
        blank=False
    )

    def __str__(self):
        """String for representing the Model object."""
        return str(self.id)

    def get_connected_players_list(self):
        return self.user_set.filter(connected=True).values_list('username', flat=True).order_by('username')

    def get_scores(self):
        return UserScore.objects.filter(game=self).order_by('-score')

    def get_time_remaining(self):
        """Time left on timer in milliseconds."""
        if self.timerEnd:
            return (self.timerEnd - timezone.now()).total_seconds() * 1000
        return false
