from db import *
from math import ceil
from random import choice
import functions

bjplayers = {}
cards = ('A', 'K', 'Q', 'J', 10, 9, 8, 7, 6, 5, 4, 3, 2)

class blackjack():
    def __init__(self, author, bet=0):
        self.id = author.id
        self.name = str(author.name)
        self.mention = author.mention
        self.player = author
        self.bet = int(bet)
        self.hand = []
        self.sum = 0
        self.dealer_hand = []
        self.dealer_sum = 0
        self.status = 'playing'
        updatemoney(self.id, (self.bet * -1))
        [self.getcard() for i in range(2)]
        [self.dealer_getcard() for i in range(2)]
        self.epicwin()

    def what_is_value_of_card(self, card):
        if card in ('A', 'Q', 'K', 'J'):
            if card == 'A':
                if (self.sum + 11) > 21:
                    return 1
                else:
                    return 11
            else:
                return 10
        else:
            return card

    def checkMySum(self):
        self.sum = 0
        for i in self.hand:
            if i == 'A':
                pass
            elif i in ('Q', 'K', 'J'):
                self.sum += 10
            else:
                self.sum += i
        for i in self.hand:
            if i == 'A':
                if self.sum + 11 > 21:
                    self.sum += 1
                else:
                    self.sum += 11

    def checkDealerSum(self):
        self.dealer_sum = 0
        for i in self.dealer_hand:
            if i == 'A':
                pass
            elif i in ('Q', 'K', 'J'):
                self.dealer_sum += 10
            else:
                self.dealer_sum += i
        for i in self.dealer_hand:
            if i == 'A':
                if self.dealer_sum + 11 > 21:
                    self.dealer_sum += 1
                else:
                    self.dealer_sum += 11

    # getting cards
    def getcard(self):
        card = choice(cards)
        self.hand.append(card)
        self.checkMySum()

    def dealer_getcard(self):
        card = choice(cards)
        self.dealer_hand.append(card)
        functions.log(f'Blackjack {self.player} Dealer {card}', type='debug') # ---
        self.checkDealerSum()

    # main return
    def maininfo(self):
        self.whowin()
        if self.status == 'tie':
            updatemoney(self.id, self.bet)
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum}.```\
{self.mention}, Это ничья!'
        elif self.status == 'win':
            updatemoney(self.id, int(self.bet * 2))
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum}.```\
{self.mention} выиграл {self.bet} nedocoins!'
        elif self.status == 'lose':
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum},```\
{self.mention}, Ты проиграл!`'
        elif self.status == 'epic-win':
            updatemoney(self.id, ceil(self.bet * 2.5))
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}, \n\
Карты диллера: [{str(self.dealer_hand)}]`, сумма {self.dealer_sum}.```\
{self.mention} выиграл {ceil(self.bet*1.5)} nedocoins!'
        else:
            return f'```{self.name}, Твои карты: {self.hand}, сумма: {self.sum}\n\
Карты диллера: [{str(self.dealer_hand[0])}, ?], сумма: {self.what_is_value_of_card(self.dealer_hand[0])},```\
{self.mention}, Взять ещё карту или достаточно?'

    # win types
    def whowin(self):
        if self.status == 'playing':
            if self.dealer_sum > 21:
                self.status = 'win'
            elif self.sum > 21:
                self.status = 'lose'
            elif len(self.hand) >= 5:
                self.status = 'win'
            elif len(self.dealer_hand) >= 5:
                self.status = 'lose'

    def epicwin(self):
        if self.sum == self.dealer_sum == 21:
            self.status = 'tie'
        elif self.sum == 21:
            self.status = 'epic-win'

    # to-do defs
    def hit(self):
        self.getcard()

    def stay(self):
        self.whowin()
        if self.status != 'playing':
            return
        elif self.sum == self.dealer_sum > 17:
            self.status = 'tie'
        elif self.sum < self.dealer_sum:
            self.status = 'lose'
        else:
            self.dealer_getcard()
            self.stay()
