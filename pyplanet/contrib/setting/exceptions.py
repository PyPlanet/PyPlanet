"""
Exceptions for Setting Manager.
"""


class SettingException(Exception):
	"""Abstract setting exception."""


class SerializationException(SettingException):
	"""Setting value (un)serialization problems"""


class TypeUnknownException(SettingException):
	"""The type is unknown."""
