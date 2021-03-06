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


import kimmy.util

class RollLimitError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PrivatePerPlayerRollLimitError(RollLimitError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PublicPerPlayerRollLimitError(RollLimitError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PublicPerChannelRollLimitError(RollLimitError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RollLimiter(object):
    def __init__(self):
        self._public_perchannel = {}
        self._public_perplayer = {}
        self._private_perplayer = {}
        self._private_perplayer_burst = {}
        self._clockskew = False
    def check(self, channel, userId, clanId, currentTime, kimmybot_config):
        # clanId must be 0 if channel is not a clan channel
        t = currentTime
        if channel == '':
            # Private roll
            private_perplayer_limit = kimmybot_config.get('private_perplayer_limit')
            if not self._check(self._private_perplayer, userId, private_perplayer_limit, t):
                burst = self._private_perplayer_burst.get(userId, 0)
                if burst >= kimmybot_config.get('private_perplayer_burst') - 1:
                    raise PrivatePerPlayerRollLimitError('Private per-player roll limit')
        else:
            # Public roll
            public_perplayer_limit = kimmybot_config.get('public_perplayer_limit')
            if not self._check(self._public_perplayer, userId, public_perplayer_limit, t):
                raise PublicPerPlayerRollLimitError('Public per-player roll limit')
            public_perchannel_limit = kimmybot_config.get('public_perchannel_limit')
            if clanId not in self._public_perchannel:
                self._public_perchannel[clanId] = {}
            if not self._check(self._public_perchannel[clanId], channel, public_perchannel_limit, t):
                raise PublicPerChannelRollLimitError('Public global roll limit')
    def _check(self, container, index, limit, t):
        if index not in container:
            return True
        if container[index] > t:
            self._clockskew = True
            container[index] = t
        return container[index] + limit <= t
    def clock_skew_check(self):
        result = self._clockskew
        self._clockskew = False
        return result
    def update(self, channel, userId, clanId, currentTime, kimmybot_config):
        # clanId must be 0 if channel is not a clan channel
        t = currentTime
        if channel == '':
            # Private roll
            oldt = self._private_perplayer.get(userId, None)
            self._private_perplayer[userId] = t
            # (Handle bursts)
            private_perplayer_limit = kimmybot_config.get('private_perplayer_limit')
            if oldt is None or oldt + private_perplayer_limit <= t:
                self._private_perplayer_burst[userId] = 0
            else:
                oldburst = self._private_perplayer_burst.get(userId, 0)
                self._private_perplayer_burst[userId] = oldburst + 1
        else:
            # Public roll
            if clanId not in self._public_perchannel:
                self._public_perchannel[clanId] = {}
            self._public_perchannel[clanId][channel] = t
            self._public_perplayer[userId] = t


if __name__ == '__main__':
    import readline
    import time
    import kimmy.config
    import kimmy.rng
    config = kimmy.config.kimmybotConfig(kimmy.rng.RNG())
    config.load_defaults()
    config.set('private_perplayer_limit', 10)
    config.set('private_perplayer_burst', 5)
    config.set('public_perplayer_limit', 600)
    config.set('public_perchannel_limit', 60)
    limiter = RollLimiter()
    while True:
        s = raw_input('--> ')
        fields = s.split()
        currentTime = time.time()
        try:
            if len(fields) == 0:
                pass
            elif len(fields) == 1:
                userId = int(fields[0])
                print 'Private roll for player ' + str(userId)
                limiter.check('', userId, 0, currentTime, config)
                limiter.update('', userId, 0, currentTime, config)
            elif len(fields) == 2:
                channel = fields[0]
                userId = int(fields[1])
                print 'Public roll in channel ' + channel + ' for player ' + str(userId)
                limiter.check(channel, userId, 0, currentTime, config)
                limiter.update(channel, userId, 0, currentTime, config)
            else:
                channel = fields[0]
                userId = int(fields[1])
                clanId = int(fields[2])
                print 'Clan roll in channel ' + channel + ' for player ' + str(userId) + ' in clan ' + str(clanId)
                limiter.check(channel, userId, clanId, currentTime, config)
                limiter.update(channel, userId, clanId, currentTime, config)
        except ValueError as err:
            print('Unable to parse request, make sure to only use player/clan IDs instead of names')
        except RollLimitError as err:
            print('Roll failed: ' + str(err))
