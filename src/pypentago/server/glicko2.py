#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyPentago - a board game
# Copyright (C) 2008 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import sqrt, pi
from db import player, player_manager, gamehistory, game_history_manager, session_manager

class RatingCalculator(object):

    def __init__(self):
        pass

    def update_ratings(self, p1, p2):
        """update both players ratings, p1 was the winner"""
        #1 get both players player database objects using the playermanager
        p_manager = player_manager
        self.player1 = p_manager.get_player_by_id(p1.database_id)
        self.player2 = p_manager.get_player_by_id(p2.database_id)

        self.p1games = game_history_manager.getGameHistoryById(p1.database_id)

        self.p2games = game_history_manager.getGameHistoryById(p1.database_id)

    def calculate_new_rating(self, last_games_list, current_sigma, current_phi):
        """Calculate the new rating using the list of previous games, current_sigma, 
        and current_phi.
        
        Return a list of [NewRating , NewRD, NewVolatility]  which is equivalent 
        to [NewGlickoRating, NewGlickoRD, NewVolatility]  which is also
        [NewRating, New Phi, and New Sigma] in terms of the variables below.
        Ratings stored in the database are actually Glicko ratings. 
        Glicko-2 affects only the process of calculating the new ratings"""
        #TODO: optimize the calling of the functions so that calculations are only done once, increasing efficiency.
        #Here things are calculated multiple times, but computers are fast nowadays, maybe it will be fine.
        #e.g.   __g(phi)**2 is called many times.  So is __E(a,b,c)
        return [__r_prime(last_games_list, current_sigma, current_phi),     #the new rating
                __rd_prime(last_games_list, current_sigma, current_phi),    #the new RD
                __sigma_prime(last_games_list, current_sigma, current_phi)] #the new volatility

    #********************************************************************************
    #Private methods below are for rating calculation
    #********************************************************************************

    def __E(self, mu, mu_j, phi_j):
        #test string:  __E([ [0, -0.5756, 0.1727], [0, 0.2878, 0.5756], [0, 1.1513, 1.7269] ])
        return round(1 / (1 + exp(-1 * __g(phi_j) * (mu - mu_j))), 3)

    def __g(self, phi):
        #test string:  __g(1.1513)
        return round(1 / sqrt(1 + 3* phi**2 / (pi**2)), 4)

    def __v(self, L):
        #test string:  __v([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ])
        # ((0.9955**2) * (0.639) * (1 - 0.639) + (0.9531**2) * (0.432) * (1 - 0.432) + (0.7242**2) * (0.303) * (1 - 0.303)) **(-1)
        v = 0
        for m in L:
            mu, mu_j, phi_j, s_j = m
            #watch rounding...
            v += (__g(phi_j)**2) * __E(mu, mu_j, phi_j) * (1 - __E(mu, mu_j, phi_j))
        v = v**(-1)
        return v

    def __delta(self, L):
        #test string:  __delta([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ])
        d = 0
        for m in L:
            mu, mu_j, phi_j, s_j = m
            d += __g(phi_j) * (s_j - __E(mu, mu_j, phi_j))
        d = d * __v(L)
        return d

    def __sigma_prime(self, L, sigma, phi):
        #test string:  __sigma_prime([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ], 0.06, 1.1513)
        a = round(log(sigma**2), 6)
        _d = __delta(L)
        _v = __v(L)
        tau = 0.5
        x = a
        last_x = a
        for i in range(20):
            d = (phi**2) + _v + exp(x)
            h1 = (x - a)/(tau**2) - 0.5 * exp(x) / d + 0.5 * exp(x) * (_d / d)**2
            h2 = -1/(tau**2) - 0.5 * exp(x) * ((phi**2) + _v)/(d**2) + 0.5 * (_d**2) * exp(x) * ((phi**2) + _v - exp(x))/(d**3)
            x2 = x - h1/h2
            print "[x] %(x)f [d] %(d)f" % {"x": x, "d": d}

            if (fabs(x2 - x) < 0.001):
                break
            x = x2
        return exp(x/2)

    def __phi_star(self, L, sigma, phi):
        #test string:  __phi_star([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ], 0.06, 1.1513)
        return sqrt((phi**2) + (__sigma_prime(L, sigma, phi)**2))

    def __phi_prime(self, L, sigma, phi):
        #test string:  __phi_prime ([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ], 0.06, 1.1513)
        return (1 / sqrt((1/(__phi_star(L, sigma, phi)**2)) + (1/__v(L))))

    def __mu_prime(self, L, sigma, phi):
        #test string:  __mu_prime([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ], 0.06, 1.1513)
        mp=0
        for m in L:
            mu, mu_j, phi_j, s_j = m
            mp += __g(phi_j) * (s_j - __E(mu, mu_j, phi_j))
        mp = mp * (__phi_prime(L, sigma, phi)**2)
        mp += mu
        return mp

    def __r_prime(self, L, sigma, phi):
        #test string:  __r_prime([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ], 0.06, 1.1513)
        return 173.7178 * __mu_prime(L, sigma, phi) + 1500

    def __rd_prime(self, L, sigma, phi):
        #test string:  __rd_prime([ [0, -0.5756, 0.1727, 1], [0, 0.2878, 0.5756, 0], [0, 1.1513, 1.7269, 0] ], 0.06, 1.1513)
        return 173.7178 * __phi_prime(L, sigma, phi)

    #not used but possibly save some typing if we decide to make a Rating object
    #class Rating(object):
    #    def __init__(self, player, rating=1500, RD=350, volatility=0.06):
    #        self.player = player
    #        self.rating = rating
    #        self.RD = RD
    #        self.volatility = volatility
