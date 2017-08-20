"""
Converter contrib is managing migrating from another controller.
"""
from pyplanet.contrib.converter.xaseco2 import Xaseco2Converter
from pyplanet.contrib.converter.uaseco import UasecoConverter


def get_converter(source_type: str, **options):
	if source_type == 'xaseco2':
		return Xaseco2Converter(**options)
	elif source_type == 'uaseco':
		return UasecoConverter(**options)
