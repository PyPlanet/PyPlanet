"""
Converter contrib is managing migrating from another controller.
"""
from pyplanet.contrib.converter.xaseco2 import Xaseco2Converter


def get_converter(source_type: str, **options):
	if source_type == 'xaseco2':
		return Xaseco2Converter(**options)

