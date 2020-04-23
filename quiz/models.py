from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

QUESTION_TYPES = (
    ('t', 'Text'),
    ('m', 'Multiple Choice'),
)

class TextResponse(models.Model):
    """Model representing a text question response."""
    response = models.CharField(max_length=300, help_text='Enter your answer:')
    question = models.ForeignKey('TextQuestion', on_delete=models.CASCADE, null=False)
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
    points = models.DecimalField(max_digits=10, decimal_places=5, default=0)

    class Meta:
        unique_together = ('question', 'user', 'game')

    def __str__(self):
        """String for representing the Model object."""
        return self.response

    def save(self, *args, **kwargs):
        # recalculate user score when points is changed
        try:
            this = TextResponse.objects.get(id=self.id)
            if this.points != self.points:
                userscore, created = UserScore.objects.get_or_create(user=self.user,game=self.game)
                userscore.score -= Decimal(this.points)
                userscore.score += Decimal(self.points)
                userscore.save()
        except TextResponse.DoesNotExist:
            pass
        super(TextResponse, self).save(*args, **kwargs)

class TextQuestion(models.Model):
    generic_question = models.OneToOneField('GenericQuestion', related_name='detail', on_delete=models.CASCADE, primary_key=True)
    answer = models.CharField(max_length=300)

    def __str__(self):
        """String for representing the Model object."""
        return self.generic_question.question

    def get_user_response(self, user, game):
        response, created = self.textresponse_set.get_or_create(user=user, game=game)
        return response

    def get_all_responses(self, game):
        return self.textresponse_set.filter(game=game).all()

class GenericQuestion(models.Model):
    """Model representing a Question."""
    number = models.IntegerField()
    round = models.ForeignKey('Round', on_delete=models.SET_NULL, null=True)
    question = models.CharField(max_length=300)

    type = models.CharField(
        max_length=1,
        choices=QUESTION_TYPES,
        default='t',
    )

    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # detail = GenericForeignKey('content_type', 'object_id')
    class Meta:
        unique_together = ('number', 'round')
        ordering = ['number']

    def __str__(self):
        """String for representing the Model object."""
        return self.question

    def get_absolute_url(self):
        """Returns the url to access the page for this round."""
        return reverse('question-detail', args=[str(self.round.id), str(self.id)])

    def get_detail(self):
        """Returns the detail object."""
        return self.detail

from django.urls import reverse # Used to generate URLs by reversing the URL patterns

class Round(models.Model):
    """Model representing a round"""
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
        return reverse('round-detail', args=[str(self.id)])

    def get_first_question(self):
        return self.genericquestion_set.all().order_by('number').first()

class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    game = models.ForeignKey('Game', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.username

    def get_response(self, question):
        return question.detail.get_user_response(self, self.game)

    def get_responses(self, game):
        return question.detail.get_user_responses(self, self.game)

class UserScore(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)
    score = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user}: {self.score}'

class Game(models.Model):
    """Model representing a game"""
    leader = models.ForeignKey('User', related_name='game_leader', on_delete=models.CASCADE, null=False)
    active = models.BooleanField(default=False)
    currentRound = models.ForeignKey('Round', on_delete=models.SET_NULL, blank=True, null=True)
    currentQuestion = models.ForeignKey('GenericQuestion', on_delete=models.SET_NULL, blank=True, null=True)
    marking = models.BooleanField(default=False)

    def __str__(self):
        """String for representing the Model object."""
        return str(self.id)
