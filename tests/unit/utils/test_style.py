from pyplanet.utils import style


def test_style_stripping():
	# Colors
	raw = '$i$fffMax$06fSmurf$f00.$fffes$$l$09f.$fffm$08f$a5x$n$w$o'
	expect = '$iMaxSmurf.es$$l.m$a5x$n$w$o'
	assert style.style_strip(raw, style.STRIP_COLORS) == expect

	raw = '$l[some link]$i$FFFMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx$l'
	expect = '$l[some link]$iMaxSmurf.esl.mx$l'
	assert style.style_strip(raw, style.STRIP_COLORS) == expect

	raw = '$l[some link]$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx'
	expect = '$l[some link]$iMaxSmurf.esl.mx'
	assert style.style_strip(raw, style.STRIP_COLORS) == expect


	# Links
	raw = '$l$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x$l'
	expect = '$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x'
	assert style.style_strip(raw, style.STRIP_LINKS) == expect

	raw = '$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x'
	expect = '$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x'
	assert style.style_strip(raw, style.STRIP_LINKS) == expect

	raw = '$l[some link]$i$fffMax$06fSmurf$f00.$fffes$$l$09f.$fffm$08fx$l'
	expect = '$i$fffMax$06fSmurf$f00.$fffes$$09f.$fffm$08fx'
	assert style.style_strip(raw, style.STRIP_LINKS) == expect

	raw = '$l[some link]$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx'
	expect = '$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08fx'
	assert style.style_strip(raw, style.STRIP_LINKS) == expect


	# Sizes
	raw = '$i$n$fffMax$06fSmurf$f00.$w$o$fffe$$nsl$09f.$w$fffm$08f$a5$ox'
	expect = '$fffMax$06fSmurf$f00.$fffe$sl$09f.$fffm$08f$a5x'
	assert style.style_strip(raw, style.STRIP_SIZES) == expect


	# All
	raw = '$h$i$fffMax$06fSmurf$f00.$fffesl$09f.$fffm$08f$a5x$h'
	expect = 'MaxSmurf.esl.m$a5x'
	assert style.style_strip(raw) == expect

	raw = '$l[some link]$i$fffMax$06fSmur$$f$f00.$fffesl$09f.$fffm$08fx$l'
	expect = 'MaxSmur$$f.esl.mx'
	assert style.style_strip(raw) == expect

	raw = '$l[some link]$i$fffMax$06fSmu$nrf$f00.$fffesl$09f.$fffm$08fx'
	expect = 'MaxSmurf.esl.mx'
	assert style.style_strip(raw) == expect


	# Combination & Misc
	raw = '$f80$i$oToffe$g$z$06fSmurf $z$sHello'
	expect = 'Toffe$zSmurf $zHello'
	assert style.style_strip(raw, keep_reset=True) == expect

	raw = '$f80$i$oToffe$g$z$06fSmurf $z$sHello'
	expect = 'ToffeSmurf $sHello'
	assert style.style_strip(raw, style.STRIP_SIZES, style.STRIP_COLORS) == expect
