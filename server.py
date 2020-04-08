import socketio
import time
import re
import names
import random

socket = socketio.Client()

choosingTrump = False
trumpCard = ""
currentRoundSuit = ''
trumpAsked = False
trumpRevealed = False
username=names.get_first_name('female')
connected = False
typing = False
myTurn = False
cardsInHand = []
suitsInHand = []
playerNumber = 0
playerSequence=[]
playerPerspective = []
turn = 0
youRequestedTrump = False

socket.connect('http://localhost:3000')
socket.emit('add user', username)

@socket.on('login')
def on_login (data):
    connected = True
    print('logged in')
    playerNumber = data['playerNumber']
    playerSequence = data['playerSequence']
    print (playerNumber)

@socket.on('card thrown') 
def on_card_thrown (data):
    turn = data['turn']

# @socket.on('hands picked') 
# def on_hands_picked (data):
#     winner = playerSequence.index(data['username'])+1
#     msg = ''
#     if (playerNumber == winner or playerNumber == winner+2 or playerNumber == winner-2):
#         msg = 'Your team picked '+data['handsPicked']+' hands'
#     else:
#         msg = 'Your opponents picked '+data['handsPicked']+' hands'

@socket.on("request trump")
def on_request_trump(data):
    trumpAsked = True
    global cardsInHand
    socket.emit('reveal trump')
    cardsInHand.append(trumpCard)

@socket.on("reveal trump")
def on_reveal_trump(data):
    global trumpCard
    global trumpRevealed
    trumpCard = data['trumpCard']
    trumpRevealed = True

@socket.on('user joined') 
def on_user_joined (data):
    playerSequence = data['playerSequence']

@socket.on('deal') 
def on_deal(data):
    global cardsInHand 
    cardsInHand = cardsInHand + data['hand']
    cardsInHand.sort()
    # print(cardsInHand)

@socket.on('your turn') 
def on_your_turn (data):
    global myTurn
    global turn
    global cardsInHand
    myTurn = True
    currentRoundSuit = data['currentRoundSuit']
    time.sleep(3)
    throwCard(currentRoundSuit, cardsInHand)
    turn+=1
    myTurn = False

@socket.on('choose trump')
def on_choose_trump (data):
    global cardsInHand
    global trumpCard
    trumpCard = cardsInHand.pop()
    print(cardsInHand)
    print(trumpCard)
    socket.emit('trump card', trumpCard)
    

@socket.on('choose bet') 
def on_choose_bet (data):
    highestBet = data['highestBet']
    socket.emit('bet', {'bet': 'pass', 'username': username})

@ socket.on('redeal')
def on_redeal(data):
    global choosingTrump
    global trumpCard
    global currentRoundSuit
    global trumpAsked
    global trumpRevealed
    global myTurn
    global suitsInHand
    global cardsInHand
    global turn
    global youRequestedTrump
    global playerSequence
    global playerNumber

    choosingTrump = False
    trumpCard = ""
    currentRoundSuit = ""
    trumpAsked = False
    trumpRevealed = False
    myTurn = False
    suitsInHand = []
    cardsInHand = []
    turn = 0
    youRequestedTrump = False
    playerSequence = data['playerSequence']
    playerNumber = data['playerNumber']
 

def throwCard(suite, cardsInHand):
    global trumpRevealed
    global trumpCard
    global playerNumber
    global myTurn

    r = re.compile(f"{suite}.*")
    cardsOfSuit = list(filter(r.match, cardsInHand)) # Read Note
    print(trumpRevealed)
    if (myTurn):
        if (trumpRevealed and len(cardsOfSuit) ==  0):
            card = cardsInHand.pop(int(random.random()*len(cardsInHand)))
        elif (not trumpRevealed and len(cardsOfSuit) ==  0 and (playerNumber == 2 or playerNumber == 4)):
            socket.emit('request trump')
            time.sleep(3)
            suite = re.split('\d+', trumpCard)[0]
            r = re.compile(f"{suite}.*")
            cardsOfSuit = list(filter(r.match, cardsInHand))
            if (len(cardsOfSuit) > 0):
                card = cardsOfSuit.pop(int(random.random()*len(cardsOfSuit)))
                cardsInHand.remove(card)
            else:
                card = cardsInHand.pop(int(random.random()*len(cardsInHand)))
        else:
            card = cardsInHand.pop(int(random.random()*len(cardsInHand)))

        socket.emit('card thrown', card)
