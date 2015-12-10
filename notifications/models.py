from django.db import models

# Create your models here.
from django.db.models import ForeignKey, DateTimeField, CharField, BooleanField

from ingredients.models import Ingredient


class Notification(models.Model):
    user = ForeignKey('user.UserProfile', related_name='user_notifications')
    timestamp = DateTimeField(auto_now_add=True, db_index=True)
    notification = CharField(max_length=50)
    ingredient = ForeignKey(Ingredient, related_name='low_ingredient_notification')
    is_read = BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'ingredient'),)
        ordering = ['-timestamp']

    def __str__(self):
        return 'Profile: {user}-->Ingredient: {ing}-->Notification: {notify}'.format(user=self.user,
                                                                                     ing=self.ingredient,
                                                                                     notify=self.notification[:14])

    @classmethod
    def get_notification(cls, user):
        return cls.objects.filter(user=user)

    @classmethod
    def _get_low_notification_message(cls, ingredient_id):
        ing_name = Ingredient.objects.filter(pk=ingredient_id).only('name')[0].name
        return 'Low Ingredient: {}'.format(ing_name)

    @classmethod
    def create_low_ingredient_notifications(cls, user, ingredient_ids):
        notifications = [
            cls(
                user=user,
                ingredient_id=ingredient_id,
                notification=cls._get_low_notification_message(ingredient_id)
            )
            for ingredient_id in ingredient_ids
        ]

        cls.objects.bulk_create(notifications)

    @classmethod
    def remove_low_ingredient_notifications(cls, user, ingredient_ids):
        Notification.objects.filter(user=user, ingredient_id__in=ingredient_ids).delete()

    def mark_read(self):
        self.is_read = True
        self.save()
