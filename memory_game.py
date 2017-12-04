import logging

from random import randint
import random
import string

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session


app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch

def new_game():

    welcome_msg = render_template('welcome')

    return question(welcome_msg)

@ask.intent('AMAZON.HelpIntent')
def helpme():
    return instructions_intent()


@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.CancelIntent')
def cancelme():
    return statement('')

@ask.intent("YesIntent")

def next_round():

    numbers = [randint(0, 9) for _ in range(3)]

    round_msg = render_template('round', numbers=numbers)

    session.attributes['numbers'] = numbers[::-1]  # reverse

    return question(round_msg)

@ask.intent("InstructionsIntent")
def instructions_intent():
    instructions_msg = render_template('instructions')
    return question(instructions_msg)

@ask.intent("StartRoundIntent")
def start_round():
    session.attributes['word_fragment'] = random.choice(string.ascii_letters).lower()
    print "the starting word_fragment is", session.attributes['word_fragment']
    return play_round_begin()

@ask.intent("RepeatIntent")
def repeatme():
    return play_round()

def play_round_begin():
    round_msg = render_template('get_next_letter_begin',word_fragment = session.attributes['word_fragment'].strip())
    return question(round_msg)

def play_round():
    round_msg = render_template('get_next_letter',word_fragment = session.attributes['word_fragment'].strip())
    return question(round_msg)

def play_round_misheard():
    round_msg = render_template('get_next_letter_misheard',word_fragment = session.attributes['word_fragment'].strip())
    return question(round_msg)

@ask.intent("GiveLetterIntent", convert={'letter': str})
def answer_intent(letter):
    letter = letter.lower()
    letter = letter.replace(".","")
    print letter
    if len(letter) != 1:
        return play_round_misheard()
    if not letter.isalpha():
        return play_round_misheard()
    word_fragment = session.attributes['word_fragment']
    word_fragment += letter
    my_dict = render_template('dictionary')
    #print "hello"
    #print "my_dict:", my_dict
    print "word fragment:", word_fragment
    #print my_dict
    if word_fragment.replace(" ","") in my_dict.split(","):
        return question(render_template('indict',word_fragment=word_fragment))
    they_won = False
    possible_words = []
    could_say = -1
    for word in my_dict.split(","):
        if (word.startswith(word_fragment.replace(" ","")) and len(word)%2 == 0):
            possible_words.append(word)
            print "word:",word
        if (word.startswith(word_fragment.replace(" ",""))): #theres a word in the dictionary that starts with the word fragment
            print word
            they_won = True
        if (word.startswith(word_fragment[:-1].replace(" ",""))): #theres a word in the dictionary that starts with the word fragment
            print word
            could_say = word
    if len(possible_words) > 0:
        w = random.choice(possible_words)
        word_fragment += w[len(word_fragment.replace(" ",""))] 
        session.attributes['word_fragment'] = word_fragment
        return play_round()
    if they_won:
        return question(render_template('winner',word_fragment=word_fragment))
    else:
        if could_say != -1:
            return question(render_template('madeupcould',word_fragment=[word_fragment,could_say]))
        else:
            return question(render_template('madeup',word_fragment=word_fragment))

@ask.intent('AMAZON.CancelIntent')
@ask.intent('AMAZON.StopIntent')
def exit_skill():
    return statement('')


if __name__ == '__main__':

    app.run(debug=True)
