from django.db import models

# Create your models here.
class Watched(models.Model):
	movie_id = models.IntegerField()
	WORSE = 1
	BAD = 2
	AVERAGE = 3
	GOOD = 4
	EXCELLENT = 5
	RATING_CHOICES = (
		(WORSE, 'WORSE'),
		(BAD, "BAD"),
		(AVERAGE, "AVERAGE"),
		(GOOD, "GOOD"),
		(EXCELLENT, "EXCELLENT"),
		)
	movie_rating = models.IntegerField(
        choices=RATING_CHOICES,
        blank = True,
        null = True
    )

class Not_Watched(models.Model):
	movie_id = models.IntegerField()