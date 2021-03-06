#
# Copyright (C) 2012-2013 kimmybot
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import bisect
import re
import textwrap


class Expando(object): pass

def intlog2(n):
    if n >= 2:
        return len(bin(n)) - 3
    else:
        return 0

def ceildiv(a, b):
    return (a+b-1) // b

def roll(rng, a, b):
    # Roll aDb, returns an integer
    return sum(rng.get(1, b) for hippopotamus in range(0, a))

def shuffle(rng, a, b):
    # Roll aSb, returns a list of integers
    results = []
    results_sorted = []
    for i in range(0, a):
        x = rng.get(1, b-i)
        for j in results_sorted:
            if x >= j:
                x += 1
        results.append(x)
        bisect.insort(results_sorted, x)
    return results

def prefix_lines(text, prefix, margin):
    # Resolve and dedent hanging indent
    text_split = text.strip().split('\n', 1)
    text_dedented = (text_split[0] + '\n' +
            '\n'.join(textwrap.dedent(x) for x in text_split[1:])).strip()
    if margin:
        text_dedented = '\n' + text_dedented + '\n'
    # Prefix each line
    s = prefix + ('\n' + prefix).join(text_dedented.split('\n'))
    # Remove trailing whitespaces
    s = re.sub(r'\s+$', '', s, flags=re.MULTILINE)
    return s + '\n'



# units supported in kimmytory expressions
units = {'': 1, 'k': 1000, 'm': 1000000, 'b': 1000000000}

def isunit(s):
    return s.lower() in units

def getunit(c):
    return units[c.lower()]

def format_with_unit(n):
    if n == 0:
        return '0'
    best_unit = ''
    best_multiplier = 1
    for unit, multiplier in units.iteritems():
        if n % multiplier == 0 and multiplier > best_multiplier:
            best_unit = unit
            best_multiplier = multiplier
    return str(n / best_multiplier) + best_unit



# uneffectable effects
# key must always be the effect number
# first list entry of each value must always be the 'canonical' effect name
uneffectables = {
        59: ['Wanged'],
        697: ['Bruised Jaw', 'Jawbruised'],
        718: ['B-b-brr!', 'Snowballed'],
}

class Uneffectable(object):
    def __init__(self, inputname):
        self._inputname = inputname
        if inputname == '':
            self._matches = ()
            return

        matches = []
        front_matches = []
        exact_matches = []

        for effect_id, effect_names in uneffectables.iteritems():
            if str(effect_id) == inputname:
                exact_matches.append(effect_id)
            else:
                for effect_name in effect_names:
                    if effect_name.lower().startswith(inputname.lower()):
                        front_matches.append(effect_id)
                        break
                    if inputname.lower() in effect_name.lower():
                        matches.append(effect_id)
                        break
                    abbrev = re.sub(r'([A-Za-z])[A-Za-z]*[ !-]*', '\\1', effect_name)
                    if inputname.lower() == abbrev.lower():
                        matches.append(effect_id)
                        break

        if exact_matches:
            self._matches = tuple(exact_matches)
        elif front_matches:
            self._matches = tuple(front_matches)
        else:
            self._matches = tuple(matches)

    def inputname(self):
        return self._inputname

    def count(self):
        return len(self._matches)

    def effect_ids(self):
        return self._matches

    def effect_names(self):
        return tuple(uneffectables[effect_id][0] for effect_id in self._matches)

