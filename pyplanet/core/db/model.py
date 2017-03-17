import datetime

from peewee import Model as PeeweeModel
from peewee import DateTimeField

from .database import Proxy


class Model(PeeweeModel):
	class Meta:
		database = Proxy


class TimedModel(Model):
	created_at = DateTimeField(default=datetime.datetime.now)
	updated_at = DateTimeField()

	def save(self, *args, **kwargs):
		self.updated_at = datetime.datetime.now()
		return super().save(*args, **kwargs)

	def update(self, *args, **kwargs):
		self.updated_at = datetime.datetime.now()
		return super().update(*args, **kwargs)
