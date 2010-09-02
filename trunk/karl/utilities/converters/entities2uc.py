# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

entitydefs = {
    'AElig':    u'\u00c6',         # latin capital letter AE = latin capital ligature AE, U+00C6 ISOlat1
    'Aacute':   u'\u00c1',         # latin capital letter A with acute, U+00C1 ISOlat1
    'Acirc':    u'\u00c2',         # latin capital letter A with circumflex, U+00C2 ISOlat1
    'Agrave':   u'\u00c0',         # latin capital letter A with grave = latin capital letter A grave, U+00C0 ISOlat1
    'Alpha':    u'\u0391',         # greek capital letter alpha, U+0391
    'Aring':    u'\u00c5',         # latin capital letter A with ring above = latin capital letter A ring, U+00C5 ISOlat1
    'Atilde':   u'\u00c3',         # latin capital letter A with tilde, U+00C3 ISOlat1
    'Auml':     u'\u00c4',         # latin capital letter A with diaeresis, U+00C4 ISOlat1
    'Beta':     u'\u0392',         # greek capital letter beta, U+0392
    'Ccedil':   u'\u00c7',         # latin capital letter C with cedilla, U+00C7 ISOlat1
    'Chi':      u'\u03a7',         # greek capital letter chi, U+03A7
    'Dagger':   u'\u2021',         # double dagger, U+2021 ISOpub
    'Delta':    u'\u0394',         # greek capital letter delta, U+0394 ISOgrk3
    'ETH':      u'\u00d0',         # latin capital letter ETH, U+00D0 ISOlat1
    'Eacute':   u'\u00c9',         # latin capital letter E with acute, U+00C9 ISOlat1
    'Ecirc':    u'\u00ca',         # latin capital letter E with circumflex, U+00CA ISOlat1
    'Egrave':   u'\u00c8',         # latin capital letter E with grave, U+00C8 ISOlat1
    'Epsilon':  u'\u0395',         # greek capital letter epsilon, U+0395
    'Eta':      u'\u0397',         # greek capital letter eta, U+0397
    'Euml':     u'\u00cb',         # latin capital letter E with diaeresis, U+00CB ISOlat1
    'Gamma':    u'\u0393',         # greek capital letter gamma, U+0393 ISOgrk3
    'Gcirc':    u'\u011C',         # G with circumlex, U+011C
    'Iacute':   u'\u00cd',         # latin capital letter I with acute, U+00CD ISOlat1
    'Icirc':    u'\u00ce',         # latin capital letter I with circumflex, U+00CE ISOlat1
    'Igrave':   u'\u00cc',         # latin capital letter I with grave, U+00CC ISOlat1
    'Iota':     u'\u0399',         # greek capital letter iota, U+0399
    'Iuml':     u'\u00cf',         # latin capital letter I with diaeresis, U+00CF ISOlat1
    'Kappa':    u'\u039a',         # greek capital letter kappa, U+039A
    'Lambda':   u'\u039b',         # greek capital letter lambda, U+039B ISOgrk3
    'Mu':       u'\u039c',         # greek capital letter mu, U+039C
    'Ntilde':   u'\u00d1',         # latin capital letter N with tilde, U+00D1 ISOlat1
    'Nu':       u'\u039d',         # greek capital letter nu, U+039D
    'OElig':    u'\u0152',         # latin capital ligature OE, U+0152 ISOlat2
    'Oacute':   u'\u00d3',         # latin capital letter O with acute, U+00D3 ISOlat1
    'Ocirc':    u'\u00d4',         # latin capital letter O with circumflex, U+00D4 ISOlat1
    'Ograve':   u'\u00d2',         # latin capital letter O with grave, U+00D2 ISOlat1
    'Omega':    u'\u03a9',         # greek capital letter omega, U+03A9 ISOgrk3
    'Omicron':  u'\u039f',         # greek capital letter omicron, U+039F
    'Oslash':   u'\u00d8',         # latin capital letter O with stroke = latin capital letter O slash, U+00D8 ISOlat1
    'Otilde':   u'\u00d5',         # latin capital letter O with tilde, U+00D5 ISOlat1
    'Ouml':     u'\u00d6',         # latin capital letter O with diaeresis, U+00D6 ISOlat1
    'Phi':      u'\u03a6',         # greek capital letter phi, U+03A6 ISOgrk3
    'Pi':       u'\u03a0',         # greek capital letter pi, U+03A0 ISOgrk3
    'Prime':    u'\u2033',         # double prime = seconds = inches, U+2033 ISOtech
    'Psi':      u'\u03a8',         # greek capital letter psi, U+03A8 ISOgrk3
    'Rho':      u'\u03a1',         # greek capital letter rho, U+03A1
    'Scaron':   u'\u0160',         # latin capital letter S with caron, U+0160 ISOlat2
    'Sigma':    u'\u03a3',         # greek capital letter sigma, U+03A3 ISOgrk3
    'THORN':    u'\u00de',         # latin capital letter THORN, U+00DE ISOlat1
    'Tau':      u'\u03a4',         # greek capital letter tau, U+03A4
    'Theta':    u'\u0398',         # greek capital letter theta, U+0398 ISOgrk3
    'Uacute':   u'\u00da',         # latin capital letter U with acute, U+00DA ISOlat1
    'Ucirc':    u'\u00db',         # latin capital letter U with circumflex, U+00DB ISOlat1
    'Ugrave':   u'\u00d9',         # latin capital letter U with grave, U+00D9 ISOlat1
    'Upsilon':  u'\u03a5',         # greek capital letter upsilon, U+03A5 ISOgrk3
    'Uuml':     u'\u00dc',         # latin capital letter U with diaeresis, U+00DC ISOlat1
    'Vdot':     u'\u1E7E',         # latin capital letter V with dot below, U+1E7E
    'Xi':       u'\u039e',         # greek capital letter xi, U+039E ISOgrk3
    'Yacute':   u'\u00dd',         # latin capital letter Y with acute, U+00DD ISOlat1
    'Yuml':     u'\u0178',         # latin capital letter Y with diaeresis, U+0178 ISOlat2
    'Zeta':     u'\u0396',         # greek capital letter zeta, U+0396
    'aacute':   u'\u00e1',         # latin small letter a with acute, U+00E1 ISOlat1
    'acirc':    u'\u00e2',         # latin small letter a with circumflex, U+00E2 ISOlat1
    'acute':    u'\u00b4',         # acute accent = spacing acute, U+00B4 ISOdia
    'aelig':    u'\u00e6',         # latin small letter ae = latin small ligature ae, U+00E6 ISOlat1
    'agrave':   u'\u00e0',         # latin small letter a with grave = latin small letter a grave, U+00E0 ISOlat1
    'alefsym':  u'\u2135',         # alef symbol = first transfinite cardinal, U+2135 NEW
    'alpha':    u'\u03b1',         # greek small letter alpha, U+03B1 ISOgrk3
    #'amp':      u'\u0026',        # ampersand, U+0026 ISOnum
    'and':      u'\u2227',         # logical and = wedge, U+2227 ISOtech
    'ang':      u'\u2220',         # angle, U+2220 ISOamso
    'ap':      u'\u2245',          # approximate,
    'apos':      u'\u0027',        # apostrophe
    'ast':       '\00D7',          #star
    'aring':    u'\u00e5',         # latin small letter a with ring above = latin small letter a ring, U+00E5 ISOlat1
    'asymp':    u'\u2248',         # almost equal to = asymptotic to, U+2248 ISOamsr
    'atilde':   u'\u00e3',         # latin small letter a with tilde, U+00E3 ISOlat1
    'auml':     u'\u00e4',         # latin small letter a with diaeresis, U+00E4 ISOlat1
    'bdquo':    u'\u201e',         # double low-9 quotation mark, U+201E NEW
    'beta':     u'\u03b2',         # greek small letter beta, U+03B2 ISOgrk3
    'brvbar':   u'\u00a6',         # broken bar = broken vertical bar, U+00A6 ISOnum
    'bull':     u'\u2022',         # bullet = black small circle, U+2022 ISOpub
    'cap':      u'\u2229',         # intersection = cap, U+2229 ISOtech
    'ccedil':   u'\u00e7',         # latin small letter c with cedilla, U+00E7 ISOlat1
    'cedil':    u'\u00b8',         # cedilla = spacing cedilla, U+00B8 ISOdia
    'cent':     u'\u00a2',         # cent sign, U+00A2 ISOnum
    'chi':      u'\u03c7',         # greek small letter chi, U+03C7 ISOgrk3
    'circ':     u'\u02c6',         # modifier letter circumflex accent, U+02C6 ISOpub
    'clubs':    u'\u2663',         # black club suit = shamrock, U+2663 ISOpub
    'cong':     u'\u2245',         # approximately equal to, U+2245 ISOtech
    'copy':     u'\u00a9',         # copyright sign, U+00A9 ISOnum
    'crarr':    u'\u21b5',         # downwards arrow with corner leftwards = carriage return, U+21B5 NEW
    'cup':      u'\u222a',         # union = cup, U+222A ISOtech
    'curren':   u'\u00a4',         # currency sign, U+00A4 ISOnum
    'dArr':     u'\u21d3',         # downwards double arrow, U+21D3 ISOamsa
    'dagger':   u'\u2020',         # dagger, U+2020 ISOpub
    'darr':     u'\u2193',         # downwards arrow, U+2193 ISOnum
    'deg':      u'\u00b0',         # degree sign, U+00B0 ISOnum
    'delta':    u'\u03b4',         # greek small letter delta, U+03B4 ISOgrk3
    'diams':    u'\u2666',         # black diamond suit, U+2666 ISOpub
    'divide':   u'\u00f7',         # division sign, U+00F7 ISOnum
    'eacute':   u'\u00e9',         # latin small letter e with acute, U+00E9 ISOlat1
    'ecirc':    u'\u00ea',         # latin small letter e with circumflex, U+00EA ISOlat1
    'egrave':   u'\u00e8',         # latin small letter e with grave, U+00E8 ISOlat1
    'empty':    u'\u2205',         # empty set = null set = diameter, U+2205 ISOamso
    'emsp':     u'\u2003',         # em space, U+2003 ISOpub
    'ensp':     u'\u2002',         # en space, U+2002 ISOpub
    'epsilon':  u'\u03b5',         # greek small letter epsilon, U+03B5 ISOgrk3
    'equiv':    u'\u2261',         # identical to, U+2261 ISOtech
    'eta':      u'\u03b7',         # greek small letter eta, U+03B7 ISOgrk3
    'eth':      u'\u00f0',         # latin small letter eth, U+00F0 ISOlat1
    'euml':     u'\u00eb',         # latin small letter e with diaeresis, U+00EB ISOlat1
    'euro':     u'\u20ac',         # euro sign, U+20AC NEW
    'exist':    u'\u2203',         # there exists, U+2203 ISOtech
    'fnof':     u'\u0192',         # latin small f with hook = function = florin, U+0192 ISOtech
    'forall':   u'\u2200',         # for all, U+2200 ISOtech
    'frac12':   u'\u00bd',         # vulgar fraction one half = fraction one half, U+00BD ISOnum
    'frac14':   u'\u00bc',         # vulgar fraction one quarter = fraction one quarter, U+00BC ISOnum
    'frac34':   u'\u00be',         # vulgar fraction three quarters = fraction three quarters, U+00BE ISOnum
    'frasl':    u'\u2044',         # fraction slash, U+2044 NEW
    'gamma':    u'\u03b3',         # greek small letter gamma, U+03B3 ISOgrk3
    'ge':       u'\u2265',         # greater-than or equal to, U+2265 ISOtech
    #'gt':       u'\u003e',        # greater-than sign, U+003E ISOnum
    'hArr':     u'\u21d4',         # left right double arrow, U+21D4 ISOamsa
    'harr':     u'\u2194',         # left right arrow, U+2194 ISOamsa
    'hearts':   u'\u2665',         # black heart suit = valentine, U+2665 ISOpub
    'hellip':   u'\u2026',         # horizontal ellipsis = three dot leader, U+2026 ISOpub
    'iacute':   u'\u00ed',         # latin small letter i with acute, U+00ED ISOlat1
    'icirc':    u'\u00ee',         # latin small letter i with circumflex, U+00EE ISOlat1
    'iexcl':    u'\u00a1',         # inverted exclamation mark, U+00A1 ISOnum
    'igrave':   u'\u00ec',         # latin small letter i with grave, U+00EC ISOlat1
    'image':    u'\u2111',         # blackletter capital I = imaginary part, U+2111 ISOamso
    'infin':    u'\u221e',         # infinity, U+221E ISOtech
    'int':      u'\u222b',         # integral, U+222B ISOtech
    'iota':     u'\u03b9',         # greek small letter iota, U+03B9 ISOgrk3
    'iquest':   u'\u00bf',         # inverted question mark = turned question mark, U+00BF ISOnum
    'isin':     u'\u2208',         # element of, U+2208 ISOtech
    'iuml':     u'\u00ef',         # latin small letter i with diaeresis, U+00EF ISOlat1
    'kappa':    u'\u03ba',         # greek small letter kappa, U+03BA ISOgrk3
    'lArr':     u'\u21d0',         # leftwards double arrow, U+21D0 ISOtech
    'lambda':   u'\u03bb',         # greek small letter lambda, U+03BB ISOgrk3
    'lang':     u'\u2329',         # left-pointing angle bracket = bra, U+2329 ISOtech
    'laquo':    u'\u00ab',         # left-pointing double angle quotation mark = left pointing guillemet, U+00AB ISOnum
    'larr':     u'\u2190',         # leftwards arrow, U+2190 ISOnum
    'lceil':    u'\u2308',         # left ceiling = apl upstile, U+2308 ISOamsc
    'ldquo':    u'\u201c',         # left double quotation mark, U+201C ISOnum
    'le':       u'\u2264',         # less-than or equal to, U+2264 ISOtech
    'lfloor':   u'\u230a',         # left floor = apl downstile, U+230A ISOamsc
    'lowast':   u'\u2217',         # asterisk operator, U+2217 ISOtech
    'loz':      u'\u25ca',         # lozenge, U+25CA ISOpub
    'lrm':      u'\u200e',         # left-to-right mark, U+200E NEW RFC 2070
    'lsaquo':   u'\u2039',         # single left-pointing angle quotation mark, U+2039 ISO proposed
    'lsquo':    u'\u2018',         # left single quotation mark, U+2018 ISOnum
    #'lt':       u'\u003c',        # less-than sign, U+003C ISOnum
    'macr':     u'\u00af',         # macron = spacing macron = overline = APL overbar, U+00AF ISOdia
    'mdash':    u'\u2014',         # em dash, U+2014 ISOpub
    'micro':    u'\u00b5',         # micro sign, U+00B5 ISOnum
    'middot':   u'\u00b7',         # middle dot = Georgian comma = Greek middle dot, U+00B7 ISOnum
    'minus':    u'\u2212',         # minus sign, U+2212 ISOtech
    'mu':       u'\u03bc',         # greek small letter mu, U+03BC ISOgrk3
    'nabla':    u'\u2207',         # nabla = backward difference, U+2207 ISOtech
    'nbsp':     u'\u00a0',         # no-break space = non-breaking space, U+00A0 ISOnum
    'ndash':    u'\u2013',         # en dash, U+2013 ISOpub
    'ne':       u'\u2260',         # not equal to, U+2260 ISOtech
    'ni':       u'\u220b',         # contains as member, U+220B ISOtech
    'not':      u'\u00ac',         # not sign, U+00AC ISOnum
    'notin':    u'\u2209',         # not an element of, U+2209 ISOtech
    'nsub':     u'\u2284',         # not a subset of, U+2284 ISOamsn
    'ntilde':   u'\u00f1',         # latin small letter n with tilde, U+00F1 ISOlat1
    'nu':       u'\u03bd',         # greek small letter nu, U+03BD ISOgrk3
    'oacute':   u'\u00f3',         # latin small letter o with acute, U+00F3 ISOlat1
    'ocirc':    u'\u00f4',         # latin small letter o with circumflex, U+00F4 ISOlat1
    'oelig':    u'\u0153',         # latin small ligature oe, U+0153 ISOlat2
    'ograve':   u'\u00f2',         # latin small letter o with grave, U+00F2 ISOlat1
    'oline':    u'\u203e',         # overline = spacing overscore, U+203E NEW
    'omega':    u'\u03c9',         # greek small letter omega, U+03C9 ISOgrk3
    'omicron':  u'\u03bf',         # greek small letter omicron, U+03BF NEW
    'oplus':    u'\u2295',         # circled plus = direct sum, U+2295 ISOamsb
    'or':       u'\u2228',         # logical or = vee, U+2228 ISOtech
    'ordf':     u'\u00aa',         # feminine ordinal indicator, U+00AA ISOnum
    'ordm':     u'\u00ba',         # masculine ordinal indicator, U+00BA ISOnum
    'oslash':   u'\u00f8',         # latin small letter o with stroke, = latin small letter o slash, U+00F8 ISOlat1
    'otilde':   u'\u00f5',         # latin small letter o with tilde, U+00F5 ISOlat1
    'otimes':   u'\u2297',         # circled times = vector product, U+2297 ISOamsb
    'ouml':     u'\u00f6',         # latin small letter o with diaeresis, U+00F6 ISOlat1
    'para':     u'\u00b6',         # pilcrow sign = paragraph sign, U+00B6 ISOnum
    'part':     u'\u2202',         # partial differential, U+2202 ISOtech
    'percnt':   u'\u0025',         # percent sign, U+0025
    'permil':   u'\u2030',         # per mille sign, U+2030 ISOtech
    'perp':     u'\u22a5',         # up tack = orthogonal to = perpendicular, U+22A5 ISOtech
    'phi':      u'\u03c6',         # greek small letter phi, U+03C6 ISOgrk3
    'pi':       u'\u03c0',         # greek small letter pi, U+03C0 ISOgrk3
    'piv':      u'\u03d6',         # greek pi symbol, U+03D6 ISOgrk3
    'plusmn':   u'\u00b1',         # plus-minus sign = plus-or-minus sign, U+00B1 ISOnum
    'pound':    u'\u00a3',         # pound sign, U+00A3 ISOnum
    'prime':    u'\u2032',         # prime = minutes = feet, U+2032 ISOtech
    'prod':     u'\u220f',         # n-ary product = product sign, U+220F ISOamsb
    'prop':     u'\u221d',         # proportional to, U+221D ISOtech
    'psi':      u'\u03c8',         # greek small letter psi, U+03C8 ISOgrk3
    #'quot':     u'\u0022,         # quotation mark = APL quote, U+0022 ISOnum
    'rArr':     u'\u21d2',         # rightwards double arrow, U+21D2 ISOtech
    'radic':    u'\u221a',         # square root = radical sign, U+221A ISOtech
    'rang':     u'\u232a',         # right-pointing angle bracket = ket, U+232A ISOtech
    'raquo':    u'\u00bb',         # right-pointing double angle quotation mark = right pointing guillemet, U+00BB ISOnum
    'rarr':     u'\u2192',         # rightwards arrow, U+2192 ISOnum
    'rceil':    u'\u2309',         # right ceiling, U+2309 ISOamsc
    'rdquo':    u'\u201d',         # right double quotation mark, U+201D ISOnum
    'real':     u'\u211c',         # blackletter capital R = real part symbol, U+211C ISOamso
    'reg':      u'\u00ae',         # registered sign = registered trade mark sign, U+00AE ISOnum
    'rfloor':   u'\u230b',         # right floor, U+230B ISOamsc
    'rho':      u'\u03c1',         # greek small letter rho, U+03C1 ISOgrk3
    'rlm':      u'\u200f',         # right-to-left mark, U+200F NEW RFC 2070
    'rsaquo':   u'\u203a',         # single right-pointing angle quotation mark, U+203A ISO proposed
    'rsquo':    u'\u2019',         # right single quotation mark, U+2019 ISOnum
    'sbquo':    u'\u201a',         # single low-9 quotation mark, U+201A NEW
    'scaron':   u'\u0161',         # latin small letter s with caron, U+0161 ISOlat2
    'sdot':     u'\u22c5',         # dot operator, U+22C5 ISOamsb
    'sect':     u'\u00a7',         # section sign, U+00A7 ISOnum
    'shy':      u'\u00ad',         # soft hyphen = discretionary hyphen, U+00AD ISOnum
    'sigma':    u'\u03c3',         # greek small letter sigma, U+03C3 ISOgrk3
    'sigmaf':   u'\u03c2',         # greek small letter final sigma, U+03C2 ISOgrk3
    'sim':      u'\u223c',         # tilde operator = varies with = similar to, U+223C ISOtech
    'spades':   u'\u2660',         # black spade suit, U+2660 ISOpub
    'sub':      u'\u2282',         # subset of, U+2282 ISOtech
    'sube':     u'\u2286',         # subset of or equal to, U+2286 ISOtech
    'sum':      u'\u2211',         # n-ary sumation, U+2211 ISOamsb
    'sup':      u'\u2283',         # superset of, U+2283 ISOtech
    'sup1':     u'\u00b9',         # superscript one = superscript digit one, U+00B9 ISOnum
    'sup2':     u'\u00b2',         # superscript two = superscript digit two = squared, U+00B2 ISOnum
    'sup3':     u'\u00b3',         # superscript three = superscript digit three = cubed, U+00B3 ISOnum
    'supe':     u'\u2287',         # superset of or equal to, U+2287 ISOtech
    'szlig':    u'\u00df',         # latin small letter sharp s = ess-zed, U+00DF ISOlat1
    'tau':      u'\u03c4',         # greek small letter tau, U+03C4 ISOgrk3
    'there4':   u'\u2234',         # therefore, U+2234 ISOtech
    'theta':    u'\u03b8',         # greek small letter theta, U+03B8 ISOgrk3
    'thetasym': u'\u03d1',         # greek small letter theta symbol, U+03D1 NEW
    'thinsp':   u'\u2009',         # thin space, U+2009 ISOpub
    'thorn':    u'\u00fe',         # latin small letter thorn with, U+00FE ISOlat1
    'tilde':    u'\u02dc',         # small tilde, U+02DC ISOdia
    'times':    u'\u00d7',         # multiplication sign, U+00D7 ISOnum
    'trade':    u'\u2122',         # trade mark sign, U+2122 ISOnum
    'uArr':     u'\u21d1',         # upwards double arrow, U+21D1 ISOamsa
    'uacute':   u'\u00fa',         # latin small letter u with acute, U+00FA ISOlat1
    'uarr':     u'\u2191',         # upwards arrow, U+2191 ISOnum
    'ucirc':    u'\u00fb',         # latin small letter u with circumflex, U+00FB ISOlat1
    'ugrave':   u'\u00f9',         # latin small letter u with grave, U+00F9 ISOlat1
    'uml':      u'\u00a8',         # diaeresis = spacing diaeresis, U+00A8 ISOdia
    'upsih':    u'\u03d2',         # greek upsilon with hook symbol, U+03D2 NEW
    'upsilon':  u'\u03c5',         # greek small letter upsilon, U+03C5 ISOgrk3
    'uuml':     u'\u00fc',         # latin small letter u with diaeresis, U+00FC ISOlat1
    'weierp':   u'\u2118',         # script capital P = power set = Weierstrass p, U+2118 ISOamso
    'xi':       u'\u03be',         # greek small letter xi, U+03BE ISOgrk3
    'yacute':   u'\u00fd',         # latin small letter y with acute, U+00FD ISOlat1
    'yen':      u'\u00a5',         # yen sign = yuan sign, U+00A5 ISOnum
    'yuml':     u'\u00ff',         # latin small letter y with diaeresis, U+00FF ISOlat1
    'zeta':     u'\u03b6',         # greek small letter zeta, U+03B6 ISOgrk3
    'zwj':      u'\u200d',         # zero width joiner, U+200D NEW RFC 2070
    'zwnj':     u'\u200c',         # zero width non-joiner, U+200C NEW RFC 2070

}
