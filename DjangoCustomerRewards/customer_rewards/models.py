from django.db import models

class CustomerReward(models.Model):
    customer_id = models.UUIDField()
    rewards_points = models.IntegerField()
