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
    question = models.CharField(max_length=300)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file
    round = models.ForeignKey('Round', on_delete=models.SET_NULL, null=True)
    answer = models.CharField(max_length=300)

    def __str__(self):
        """String for representing the Model object."""
        return self.question

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
