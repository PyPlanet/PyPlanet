import datetime

from peewee import Model as PeeweeModel
from peewee import DateTimeField
from peewee_async import Manager

from .database import Proxy


class ObjectManager(Manager):
	database = Proxy


class Model(PeeweeModel):
	objects = ObjectManager()

	@classmethod
	async def get(cls, *args, **kwargs):
		return await cls.objects.get(cls, *args, **kwargs)

	@classmethod
	async def select(cls, query):
		return await cls.objects.get(query)

	@classmethod
	async def get_or_create(cls, *args, **kwargs):
		return await cls.objects.get_or_create(cls, *args, **kwargs)

	@classmethod
	async def create(cls, **insert):
		inst = cls(**insert)
		await inst.save(force_insert=True)
		inst._prepare_instance()
		return inst

	@classmethod
	async def _insert(cls, **insert):
		return await cls.objects.create(cls, **insert)

	async def _update(self, **update):
		return await self.objects.update(self, only=update)

	async def save(self, force_insert=False, only=None):
		field_dict = dict(self._data)
		if self._meta.primary_key is not False:
			pk_field = self._meta.primary_key
			pk_value = self._get_pk_value()
		else:
			pk_field = pk_value = None
		if only:
			field_dict = self._prune_fields(field_dict, only)
		elif self._meta.only_save_dirty and not force_insert:
			field_dict = self._prune_fields(
				field_dict,
				self.dirty_fields)
			if not field_dict:
				self._dirty.clear()
				return False

		self._populate_unsaved_relations(field_dict)
		if pk_value is not None and not force_insert:
			if self._meta.composite_key:
				for pk_part_name in pk_field.field_names:
					field_dict.pop(pk_part_name, None)
			else:
				field_dict.pop(pk_field.name, None)
			return await self._update(__data=True, **field_dict)
		elif pk_field is None:
			await self._insert(**field_dict)
			rows = 1
		else:
			pk_from_cursor = await self._insert(**field_dict)
			if pk_from_cursor is not None:
				pk_value = pk_from_cursor
			self._set_pk_value(pk_value)
			rows = 1
		self._dirty.clear()
		return rows

	async def destroy(self, recursive=False, delete_nullable=False):
		return await self.objects.delete(self, recursive, delete_nullable)

	class Meta:
		database = Proxy


class TimedModel(Model):
	created_at = DateTimeField(default=datetime.datetime.now)
	updated_at = DateTimeField()

	async def save(self, *args, **kwargs):
		self.updated_at = datetime.datetime.now()
		return await super().save(*args, **kwargs)
