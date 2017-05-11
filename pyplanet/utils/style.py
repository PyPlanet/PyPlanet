import re
import struct

import binascii

STRIP_ALL = dict(letters='wnoitsgz<>', part=r'\$[lh]\[.+\]|\$[lh]|\$[0-9a-f]{3}')
"""
Strip all custom maniaplanet styles + formatting.
"""

STRIP_COLORS = dict(letters='g', part=r'\$[0-9a-f]{3}')
"""
Strip colors from your input (including $g, color reset).
"""

STRIP_SIZES = dict(letters='wnoiz')
"""
Strip all size and adjustments styles ($w $n $o $i $z).
"""

STRIP_SHADOWS = dict(letters='s')
"""
Strip shadow style ($s).
"""

STRIP_CAPITALS = dict(letters='t')
"""
Strip capital style ($t).
"""

STRIP_LINKS = dict(part=r'\$[lh]\[.+\]|\$[lh]')
"""
Strip links ($h and $l).
"""


def style_strip(text, *strip_methods, strip_styling_blocks=True, keep_reset=False, keep_color_reset=False):
	"""
	Strip styles from the Maniaplanet universe.

	Examples:
	
	.. code-block:: python

		print("--- Strip: colours ---")
		print(style_strip("$i$fffMax$06fSmurf$f00.$fffes$$l$09f.$fffm$08f$a5x$n$w$o", STRIP_COLORS))
		print(style_strip("$l[some link]$i$FFFMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx$l", STRIP_COLORS))
		print(style_strip("$l[some link]$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx", STRIP_COLORS))
		print("--- Strip: links ---")
		print(style_strip("$l$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x$l", STRIP_LINKS))
		print(style_strip("$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x", STRIP_LINKS))
		print(style_strip("$l[some link]$i$fffMax$06fSmurf$f00.$fffes$$l$09f.$fffm$08fx$l", STRIP_LINKS))
		print(style_strip("$l[some link]$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx", STRIP_LINKS))
		print("--- Strip: sizes ---")
		print(style_strip("$i$n$fffMax$06fSmurf$f00.$w$o$fffe$$nsl$09f.$w$fffm$08f$a5$ox", STRIP_SIZES))
		print("--- Strip: everything ---")
		print(style_strip("$h$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x$h", STRIP_ALL))
		print(style_strip("$l[some link]$i$fffMax$06fSmur$$f$f00.$fffesl$09f.$fffm$08fx$l"))
		print(style_strip("$l[some link]$i$fffMax$06fSmu$nrf$f00.$fffesl$09f.$fffm$08fx"))
		# Other stuff.:
		print(style_strip("$l[some link]$i$fffMax$06fSmu$nrf$f00.$fffesl$09f.$fffm$08fx", STRIP_CAPITALS, STRIP_SHADOWS))

	.

	:param text: The input string text.
	:param strip_methods: Methods for stripping, use one of the STRIP_* constants or leave undefined to strip everything.
	:param strip_styling_blocks: Strip all styling blocks ($> and $<)
	:param keep_reset: Keep full resets ($z).
	:param keep_color_reset: Keep color resets ($g).
	:type text: str
	:type strip_styling_blocks: bool
	:type keep_reset: bool
	:type keep_color_reset: bool
	:return: Stripped style string.
	:rtype: str
	"""
	if not strip_methods:
		strip_methods = [STRIP_ALL]
	regex = None
	letters = ''
	parts = []
	for payload in strip_methods:
		if isinstance(payload, str):
			regex = payload
			break
		elif isinstance(payload, dict):
			if 'letters' in payload:
				letters += payload['letters']
			if 'part' in payload:
				parts.append(payload['part'])

	if keep_reset:
		letters = letters.replace('z', '')
	if keep_color_reset:
		letters = letters.replace('g', '')
	if strip_styling_blocks:
		letters += '<>'

	if not regex:
		regex = r'(\$[{letters}]{parts})+'.format(
			letters=letters,
			parts='|{}'.format('|'.join(parts)) if len(parts) > 0 else ''
		)

	# Strip and return.
	return re.sub(regex, '', text, flags=re.IGNORECASE)


def percentage_color(percentage):  # pragma: no cover
	red = (255 * percentage) / 100
	green = (255 * (100 - percentage)) / 100
	return int(abs(255-red)), int(abs(255-green)), 0


def rgb_to_hex(rgb):  # pragma: no cover
	return '%02x%02x%02x' % rgb
