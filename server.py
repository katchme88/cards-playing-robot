import socketio
import time
import re
import names

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
    if (len(playerSequence) == 4):
        updateNextAvatar(playerPerspective.indexOf(playerSequence[0]))
        indicateTrumpCaller(playerPerspective.indexOf(playerSequence[0]))

@socket.on('card thrown') 
def on_card_thrown (data):
    turn = data['turn']

@socket.on('hands picked') 
def on_hands_picked (data):
    winner = playerSequence.index(data['username'])+1
    msg = ''
    if (playerNumber == winner or playerNumber == winner+2 or playerNumber == winner-2):
        msg = 'Your team picked '+data['handsPicked']+' hands'
    else:

        msg = 'Your opponents picked '+data['handsPicked']+' hands'

@socket.on("request trump")
def on_request_trump(data):
    trumpAsked = True

@socket.on("reveal trump")
def on_reveal_trump(data):
    global trumpCard
    global trumpRevealed
    trumpCard = data['trumpCard']
    print(trumpCard)
    trumpRevealed = True

@socket.on('user joined') 
def on_user_joined (data):
    playerSequence = data['playerSequence']

@socket.on('deal') 
def on_deal(data):
    global cardsInHand 
    cardsInHand = cardsInHand + data['hand']
    cardsInHand.sort()
    print(cardsInHand)

@socket.on('your turn') 
def on_your_turn (data):
    global myTurn
    global turn
    global cardsInHand
    myTurn = True
    currentRoundSuit = data['currentRoundSuit']
    time.sleep(1)
    throwCard(currentRoundSuit, cardsInHand)
    turn+=1
    print(cardsInHand)

@socket.on('choose trump')
def on_choose_trump (data):
    pass

@socket.on('choose bet') 
def on_choose_bet (data):
    highestBet = data['highestBet']
    socket.emit('bet', {'bet': 'pass', 'username': username})

def throwCard(suite, cardsInHand):
    global trumpRevealed
    global trumpCard
    global playerNumber
    r = re.compile(f"{suite}.*")
    cardsOfSuit = list(filter(r.match, cardsInHand)) # Read Note
    if (trumpRevealed and len(cardsOfSuit) ==  0):
        print('trump revealed throwing any card')
        card = cardsInHand.pop()
    elif (not trumpRevealed and len(cardsOfSuit) ==  0):
        print ('requesting trump')
        socket.emit('request trump')
        time.sleep(2)
        suite = re.split('\d+', trumpCard)[0]
        print(suite)
        r = re.compile(f"{suite}.*")
        cardsOfSuit = list(filter(r.match, cardsInHand))
        if (len(cardsOfSuit) > 0):
            card = cardsOfSuit.pop()
        else:
            card = cardsInHand.pop()
    else:
        card = cardsOfSuit.pop()
        cardsInHand.remove(card)

    socket.emit('card thrown', card)

def drawCardsInHand (data, cardsInHand):
    print(data)
    cardsInHand = cardsInHand + data['hand']
    updateSuitsInHand(cardsInHand.sort())
