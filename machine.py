# coding: utf-8
__author__ = 'Miso&Roboo'


from polyglot.text import Text
from collections import defaultdict
import pandas as pd
import logging
import numpy


class Stack():

    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def stack_items(self):
        return [x for x in self.items]


class Preprocessing():

    def __init__(self):
        self.numbers = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        self.neterminaly = None
        self.terminaly = None
        self.excel = 'tabulka2.xlsx'
        self.input_file = 'inputX.txt'

        self.table = defaultdict(list)

        self.logger = logging.getLogger(__name__)
        self.hdlr = logging.FileHandler('logging.log', mode='w')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.INFO)

        self.logger.info("Starting up the Analyzer:")

    def inputParse(self):
        try:
            file = open(self.input_file, "r")
        except Exception:
            self.logger.error('[ERROR] !!! Problem with loading table rules... ' + str(Exception))
        plain = file.read()
        priradenie = ''
        new_slova = []
        slova = Text(plain.lower()).words

        if str(slova[0]) != 'begin':
            option = raw_input('Chcete pokracovat? Program neobsahuje BEGIN...')
            if str(option) == 'y' or str(option) == 'Y':
                new_slova.append('')
                new_slova[0] = 'begin'

        for slovo in slova:
            if slovo not in self.terminaly:
                if len(slovo) == 1 and not slovo.isdigit() and not slovo.isalpha():
                    priradenie += slovo
                    if priradenie == 2 * slovo:
                        option = raw_input('Chcete pokracovat? Program detegoval zlu syntax.')
                        if str(option) == 'y' or str(option) == 'Y':
                            priradenie = slovo
                        else:
                            continue
                    if priradenie == ':=':
                        new_slova.append(priradenie)
                        priradenie = ''
                else:
                    for x in list(slovo):
                        new_slova.append(x)
            else:
                new_slova.append(slovo)

        if str(slova[len(slova) - 2]) != 'end':
                option = raw_input('Chcete pokracovat? Program neobsahuje END...')
                if str(option) == 'y' or str(option) == 'Y':
                    new_slova[len(new_slova) - 1] = 'end'
                    new_slova.append('$')
        print new_slova
        return new_slova

    # nacitanie pravidiel z excel tabulky
    def tableRules(self):

        table = pd.read_excel(self.excel)
        data = pd.DataFrame(table)
        data = data.fillna(0)

        columns = list(data.columns.values)   # terminaly
        self.terminaly = columns
        rows = list(data.index)  # neterminaly + terminaly
        indexes = zip(*numpy.where(data != 0))
        for index in indexes:
            self.table[(rows[index[0]], columns[index[1]])] = data.get_value(rows[index[0]], columns[index[1]]), rows[index[0]]

    def analyze(self, words):

        # '/' = epsilon..vyberame zo stacku
        # digit = 0-9   map(chr, range(48, 58))
        # digit2 = 1-9  map(chr, range(49, 58))
        # letter = a-z ...map(chr, range(97, 123))

        # ################### GRAMATIKA #################################
        pravidla = defaultdict(set)
        pravidla[(1, 'PROGRAM')] = 'begin', 'STATEMENT_LIST', 'end'
        pravidla[(2, 'STATEMENT_LIST')] = 'STATEMENT', 'D'
        pravidla[(3, 'D')] = 'STATEMENT_LIST'
        pravidla[(4, 'D')] = '/'
        pravidla[(5, 'STATEMENT')] = 'IDENT', ':=', 'EXPRESSION', ';'
        pravidla[(6, 'STATEMENT')] = 'read', '(', 'ID_LIST', ')', ';'
        pravidla[(7, 'STATEMENT')] = 'write', '(', 'EXPR_LIST', ')', ';'
        pravidla[(8, 'STATEMENT')] = 'if', 'BEXPR', 'then', 'STATEMENT', 'E'
        pravidla[(9, 'E')] = 'else', 'STATEMENT', ';'
        pravidla[(10, 'E')] = ';'
        pravidla[(11, 'ID_LIST')] = 'IDENT', 'F'
        pravidla[(12, 'F')] = ',', 'ID_LIST'
        pravidla[(13, 'F')] = '/'
        pravidla[(14, 'EXPR_LIST')] = 'EXPRESSION', 'G'
        pravidla[(15, 'G')] = ',', 'EXPR_LIST'
        pravidla[(16, 'G')] = '/'
        pravidla[(17, 'EXPRESSION')] = 'FACTOR', 'C'
        pravidla[(18, 'C')] = 'OP', 'FACTOR', 'C'
        pravidla[(19, 'C')] = '/'
        pravidla[(20, 'FACTOR')] = '(', 'EXPRESSION', ')'
        pravidla[(21, 'FACTOR')] = 'IDENT'
        pravidla[(22, 'FACTOR')] = 'NUMBER'
        pravidla[(23, 'OP')] = '+'
        pravidla[(24, 'OP')] = '-'
        pravidla[(25, 'BEXPR')] = 'BTERM', 'B'
        pravidla[(26, 'B')] = 'or', 'BTERM', 'B'
        pravidla[(27, 'B')] = '/'
        pravidla[(28, 'BTERM')] = 'BFACTOR', 'A'
        pravidla[(29, 'A')] = 'and', 'BFACTOR', 'A'
        pravidla[(30, 'A')] = '/'
        pravidla[(31, 'BFACTOR')] = 'not', 'BFACTOR'
        pravidla[(32, 'BFACTOR')] = '(', 'BEXPR', ')'
        pravidla[(33, 'BFACTOR')] = 'true'
        pravidla[(34, 'BFACTOR')] = 'false'
        pravidla[(35, 'IDENT')] = 'letter', 'H'   # LETTER povodne
        pravidla[(36, 'H')] = 'IDENT'
        pravidla[(37, 'H')] = 'X'
        pravidla[(38, 'X')] = 'DIGIT09', 'X'
        pravidla[(39, 'X')] = '/'
        pravidla[(40, 'NUMBER')] = '+', 'DIGIT19', 'Z'
        pravidla[(41, 'NUMBER')] = '-', 'DIGIT19', 'Z'
        pravidla[(42, 'NUMBER')] = 'DIGIT19', 'Z'
        pravidla[(43, 'Z')] = 'DIGIT09', 'Z'
        pravidla[(44, 'Z')] = '/'
        pravidla[(45, 'DIGIT09')] = 'digit'
        pravidla[(46, 'DIGIT19')] = 'digit2'

        ######################################################

        stack = Stack()
        stack.push('#')
        stack.push('end')
        stack.push('STATEMENT_LIST')
        stack.push('begin')

        for word in words:
            self.logger.info('Aktualne nacitane slovo: ' + word)

            while word != stack.peek():
                self.logger.info("-------------------------------")
                self.logger.info("Aktualny obsah zasobnika " + str(stack.stack_items()))

                if stack.peek() == '#' and word == '$':
                    self.logger.info("/////***** Vstupna veta bola uspesne parsovana analyzerom! KONIEC PROGRAMU. *****")
                    print "KONIEC PROGRAMU !!!"
                    return 0
                else:
                    self.logger.info("*****Slovo na vrchu zasobnika sa nezhoduje s prichadzajucim slovom!*****")
                    if word.isalpha() and len(word) == 1:
                        print word
                        try:
                            slova = pravidla[self.table[(stack.peek(), 'letter')]]
                        except TypeError:
                            self.logger.error("-----ZLY VSTUP !!! OPAKUJEM ZLY VSTUP !!!------Koniec programu.")
                            return 1

                        if stack.peek() == 'IDENT':
                            for s in slova:
                                print s
                                if s == 'letter':
                                    print s
                                    word = s
                                else:
                                    pass

                        # slova = ''.join([w for w in slova if all(len(x) == 1 and x.isalpha() for x in slova)])
                        stack.pop()
                        if all(len(x) == 1 and x != '/' for x in slova):
                            slova = ''.join([w for w in slova])
                            self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slova))
                            stack.push(slova)
                        else:
                            slova = list(reversed(slova))
                            for slovo in slova:
                                if slovo != '/':
                                    self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slovo))
                                    stack.push(slovo)
                    elif word.isdigit() and len(word) == 1:
                        print word
                        try:
                            slova = pravidla[self.table[(stack.peek(), int(word))]]
                        except TypeError:
                            self.logger.error("-----ZLY VSTUP !!! OPAKUJEM ZLY VSTUP !!!------Koniec programu.")
                            return 1

                        stack.pop()
                        if (int(word) in self.numbers)\
                           and (slova == 'digit' or slova == 'digit2'):
                            slova = word
                            self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slova))
                            stack.push(slova)
                        elif all(len(x) == 1 and x != '/' for x in slova):
                            slova = ''.join([w for w in slova])
                            self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slova))
                            stack.push(slova)
                        else:
                            slova = list(reversed(slova))
                            for slovo in slova:
                                if slovo != '/':
                                    self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slovo))
                                    stack.push(slovo)
                    else:
                        try:
                            slova = pravidla[self.table[(stack.peek(), str(word))]]
                        except TypeError:
                            self.logger.error("-----ZLY VSTUP !!! OPAKUJEM ZLY VSTUP !!!------Koniec programu.")
                            return 1

                        stack.pop()
                        if all(len(x) == 1 and x != '/' for x in slova):
                            slova = ''.join([w for w in slova])
                            self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slova))
                            stack.push(slova)
                        else:
                            slova = list(reversed(slova))
                            print slova
                            for slovo in slova:
                                if slovo != '/':
                                    self.logger.info("Vkladam na vrch zasobnika nasledovne: " + str(slovo))
                                    stack.push(slovo)
                        self.logger.info("Vrchol zasobnika: " + str(stack.peek()))
            self.logger.info('*****ZHODA*****')
            self.logger.info(".....Obsah zasobnika PRED vybratim: " + str(stack.stack_items()))
            stack.pop()
            self.logger.info(".....DLZKA zasobnika PO vybrati: " + str(stack.size()))
            self.logger.info(".....Vrchol zasobnika PO vybrati: " + stack.peek())
            self.logger.info(".....Obsah zasobnika PO vybrati: " + str(stack.stack_items()))
        # if stack.peek() == '#' and word == '$':
        #     return 0
        # else:
        return 1


def main():
    if __name__ == '__main__':
        process = Preprocessing()
        process.tableRules()
        words = process.inputParse()
        final = process.analyze(words)
        if final == 0:
            print 'Vstupne slovo bolo uspesne parsovane!'
        else:
            print 'Vstupne slovo sa neda parsovat vytvorenym analyzatorom.'


main()
