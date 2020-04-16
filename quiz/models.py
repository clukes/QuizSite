from django.db import models

#NOTE: add users and assign responses

# Create your models here.
class TextResponse(models.Model):
    """Model representing a book genre."""
    response = models.CharField(max_length=300, help_text='Enter your answer:')
    question = models.ForeignKey('question', on_delete=models.CASCADE, null=False)

    def __str__(self):
        """String for representing the Model object."""
        return self.response

class Question(models.Model):
    """Model representing a Question."""
    number = models.IntegerField(unique=True, editable=True)
    question = models.CharField(max_length=300)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file
    round = models.ForeignKey('Round', on_delete=models.SET_NULL, null=True)
    answer = models.CharField(max_length=300)

    def __str__(self):
        """String for representing the Model object."""
        return self.question

    def get_absolute_url(self):
        """Returns the url to access the page for this round."""
        return reverse('question-detail', args=[str(self.round.id), str(self.id)])


from django.urls import reverse # Used to generate URLs by reversing the URL patterns

class Round(models.Model):
    """Model representing a round"""
    title = models.CharField(max_length=200)

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access the page for this round."""
        return reverse('round-detail', args=[str(self.id)])

    def get_first_question(self):
        return self.question_set.all().order_by('number').first()

class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    game = models.ForeignKey('Game', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        """String for representing the Model object."""
        return self.username

class Game(models.Model):
    """Model representing a game"""
    leader = models.ForeignKey('User', related_name='game_leader', on_delete=models.CASCADE, null=False)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        """String for representing the Model object."""
        return self.id
