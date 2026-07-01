from cmu_graphics import *
import random
from PIL import Image

# the values of each card based on the mode of the game
def getCardValue(card,mode):
    # the game contain two modes
    # Sun (in Arabic) the first mode
    # hukum (in Arabic) the second mode
    if mode == 'sun':
        cardValues = {'J': 2, 'Q': 3, 'K': 4, 'A': 11, '10': 10, '9': 0, '8': 0, '7': 0}
    elif mode == 'hukum':
        cardValues = {'J': 20, '9': 14, '10': 10, 'Q': 3, 'K': 4, 'A': 11, '8': 0, '7': 0}
    return cardValues.get(card['rank'],0)

# we need to implment a system to make the game working and know who is the winner
def proccesToEndOfTrick(app):
    # we need to make sure that the 4 cards were played
    if len(app.playedCards) != 4:
        # do nothing if the trick is not complete (the round)
        return
    
    # we select the defualt values for the game constants
    leadSuit = app.leadSuit
    trumpSuit = app.trumpSuit   
    mode = app.mode
    
    # find the winning card of the trick
    winningCard = app.playedCards[0]
    
    # since we alreayd have the first card, we need to check for the other cards
    for i in range(1,4):
        winningCard = compareCards(winningCard, app.playedCards[i], leadSuit, trumpSuit, mode)
    
    winningPlayer = winningCard['player']
    
    # then we need to save the round (trikc ) info
    app.tricks.append({'winner': winningPlayer,'cards':app.playedCards.copy()})
    
    # Reset played cards for the next trick
    app.playedCards.clear()
    app.cardsPlayedThisRound = 0
    app.leadSuit = None
    
    # winning player starts next trick
    app.currentPlayer = winningPlayer

    # If 8 tricks have been played → end of round
    if len(app.tricks) == 8:
        # Calculate scores and round winner
        result = calculateTeamScores(app.tricks, mode, winningPlayer, app.buyerPlayer)
        
        # Store scores and winner
        app.roundScore = {0: result[0], 1: result[1]}
        app.roundWinner = result['winner']
        
        # Add to total team scores
        app.score[0] += result[0]
        app.score[1] += result[1]
        
        # For testing purposes - print scores
        print(f"Team 1 Score: {app.score[0]}")
        print(f"Team 2 Score: {app.score[1]}")
        print(f"Round Winner: {app.roundWinner}")
        print(f"Game End Test: Team 1 >= {app.winningScore}: {app.score[0] >= app.winningScore}")
        print(f"Game End Test: Team 2 >= {app.winningScore}: {app.score[1] >= app.winningScore}")
        
        # Mark round as complete
        app.roundComplete = True
        
        # Make sure cards are not visible during round end
        app.viewingCards = False
        winningScore = app.winningScore
        
        # Check if game is over (points meet threshold for winning)
        if app.score[0] >= winningScore and app.score[1] >= winningScore:
            # Both teams reached threshold, higher score wins
            if app.score[0] > app.score[1]:
                app.winner = "1"
                print("Game Over: Team 1 wins with higher score!")
            else:
                app.winner = "2"
                print("Game Over: Team 2 wins with higher score!")
        elif app.score[0] >= winningScore:
            app.winner = "1"
            print("Game Over: Team 1 wins!")
        elif app.score[1] >= winningScore:
            app.winner = "2"
            print("Game Over: Team 2 wins!")
        else:
            app.winner = None

        # Reset tricks for new round
        app.tricks.clear()
        
        # Clear all card objects
        app.cardObjs.clear()
        
        # Clear any remaining played cards
        app.playedCards.clear()
        
        # Reset cards played counter
        app.cardsPlayedThisRound = 0
        
        # Reset lead suit
        app.leadSuit = None
        
        # Reset trump suit
        app.trumpSuit = None
        
        # Reset game mode for next round
        app.mode = None

#this function will be used in redrawall
def drawModeSelectionButtons(app):
    buttonWidth = 80
    buttonHeight = 30
    buttonSpacing = 20
    startX = app.width / 2 - buttonWidth - buttonSpacing
    buttonY = app.height / 2 + 100

    drawRect(startX, buttonY, buttonWidth, buttonHeight, fill='lightgray', border='black')
    drawLabel('No Buy', startX + buttonWidth / 2, buttonY + buttonHeight / 2)

    drawRect(startX + buttonWidth + buttonSpacing, buttonY, buttonWidth, buttonHeight, fill='gold', border='black')
    drawLabel('Sun', startX + buttonWidth + buttonSpacing + buttonWidth / 2, buttonY + buttonHeight / 2)

    drawRect(startX + 2 * (buttonWidth + buttonSpacing), buttonY, buttonWidth, buttonHeight, fill='orange', border='black')
    drawLabel('Hukum', startX + 2 * (buttonWidth + buttonSpacing) + buttonWidth / 2, buttonY + buttonHeight / 2)

# setup the initial deal of cards for the game
def setupInitialDeal(app):
    # Create a new shuffled deck
    gameDeck = createDeck(app)
    random.shuffle(gameDeck)
    # Create empty hands for 4 players
    app.hands = []
    for i in range(4):
        app.hands.append([])
    # Reset visual card object list
    app.cardObjs = []
    # Reset trump and lead suits making it to none because a selction will be made
    app.trumpSuit = None
    app.leadSuit = None
    # Reset game mode (sun or hukum) same goes here
    app.mode = None
    # Draw one card to be shown in the center, so it can start the game by offering multipul buttons to determinate the game mode
    app.middleCard = gameDeck.pop()
    # Store the rest of the deck to use later
    app.remainingDeck = gameDeck
    # Star from player 0
    app.currentPlayer = 0
    # Start buying from player 0
    app.offerIndex = 0
    # Players can't see cards yet
    app.viewingCards = False
    # No cards played in this round yet
    app.cardsPlayedThisRound = 0
    # Empty trick list to track tricks this round
    app.tricks = []
    # Deal 5 cards to each player to start the game
    for playerIndex in range(4):
        for i in range(5):
            currentCard = gameDeck.pop()
            app.hands[playerIndex].append(currentCard)

# deal the remaining cards to players after the initial deal
def dealRemainingCards(app):
    # Each player should end up with 8 cards total
    for playerIndex in range(4):
        if playerIndex == app.buyerPlayer:
            # Buyer already has 6 cards (5 initial + 1 middle card)
            cardsToDeal = 2 
        else:
            # Others have 5 cards
            cardsToDeal = 3  
        for i in range(cardsToDeal):
            # Make sure we don't run out of cards
            if len(app.remainingDeck) > 0:
                currentCard = app.remainingDeck.pop()
                app.hands[playerIndex].append(currentCard)
            else:
                print("Warning: Ran out of cards in the deck!")

    # Verify each player has 8 cards (debugging)
    for playerIndex in range(len(app.hands)):
        playerHand = app.hands[playerIndex]
        if len(playerHand) != 8:
            print(f"Warning: Player {playerIndex+1} has {len(playerHand)} cards instead of 8")

# Comparison system implementation 
# returns the winning card
def compareCards(card1, card2, leadSuit, trumpSuit, mode):
    # if the card1 is a trump suit and card2 is not then card1 wins
    if card1['suit'] == trumpSuit and card2['suit'] != trumpSuit:
        return card1
    # same logic but reversed
    if card2['suit'] == trumpSuit and card1['suit'] != trumpSuit:
        return card2
    # card1 followed the lead suit and card2 didn't so card1 wins
    if card1['suit'] == leadSuit and card2['suit'] != leadSuit:
        return card1
    # some logic but reversed
    if card2['suit'] == leadSuit and card1['suit'] != leadSuit:
        return card2
    value1 = getCardValue(card1, mode)
    value2 = getCardValue(card2, mode)
    if value1 >= value2:
        return card1
    else:
        return card2

# returns the socre of team1 and team 2
def calculateTeamScores(tricks, mode, lastTrickWinner, buyerPlayer):
    # initialize total abnat for each team
    teamScores = {0:0, 1:0}
    # we go through all the cards played in this trick
    for currentTrick in tricks:
        # loop thorugh each card played in this trick (Hukum)
        for currentCard in currentTrick['cards']:
            # we need to know which team the player belongs to
            # So if the player in position 0 or 2 which they are oppisite each other
            if currentCard['player'] in [0,2]:
                currentTeam = 0
            # if not then he should be in position 1 or 3 so team 1
            else:
                currentTeam = 1
            # add the card value to the team's score
            teamScores[currentTeam] += getCardValue(currentCard, mode)
    
    # Determine buyer team (0 or 1)
    buyerTeam = 0 if buyerPlayer in [0, 2] else 1
    otherTeam = 1 if buyerTeam == 0 else 0
    
    # we convert the abnat (which the scores) to actual game points based on mode
    if mode == 'sun':
        # Calculate initial scores (sun mode: double and divide by 10)
        team0Score = rounded((teamScores[0] * 2) / 10)
        team1Score = rounded((teamScores[1] * 2) / 10)
        
        # Make total 26
        total = team0Score + team1Score
        if total != 26:
            if team0Score >= team1Score:
                team0Score = 26 - team1Score
            else:
                team1Score = 26 - team0Score
        
        # Check if buyer lost (has fewer points)
        if (buyerTeam == 0 and team0Score < team1Score) or (buyerTeam == 1 and team1Score < team0Score):
            # Buyer team gets 0, other team gets all points
            if buyerTeam == 0:
                team0Score = 0
                team1Score = 26
                roundWinner = "Team 2"
            else:
                team0Score = 26
                team1Score = 0
                roundWinner = "Team 1"
        else:
            # Normal scoring
            roundWinner = "Team 1" if team0Score > team1Score else "Team 2"
        
    elif mode == "hukum":
        # Calculate initial scores (hukum mode: divide by 10)
        team0Score = rounded(teamScores[0] / 10)
        team1Score = rounded(teamScores[1] / 10)
        
        # Make total 16
        total = team0Score + team1Score
        if total != 16:
            if team0Score >= team1Score:
                team0Score = 16 - team1Score
            else:
                team1Score = 16 - team0Score
        
        # Check if buyer lost (has fewer points)
        if (buyerTeam == 0 and team0Score < team1Score) or (buyerTeam == 1 and team1Score < team0Score):
            # Buyer team gets 0, other team gets all points
            if buyerTeam == 0:
                team0Score = 0
                team1Score = 16
                roundWinner = "Team 2"
            else:
                team0Score = 16
                team1Score = 0
                roundWinner = "Team 1"
        else:
            # Normal scoring
            roundWinner = "Team 1" if team0Score > team1Score else "Team 2"
    
    # Return scores and winner info
    return {0: team0Score, 1: team1Score, 'winner': roundWinner}

def constants(app):
    app.RANKS = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    app.SUITS = ['♠', '♥', '♦', '♣']
    app.CARD_WIDTH = app.width / 12
    app.CARD_HEIGHT = app.height / 8
    
    # Increased button width
    app.buttonWidth = 120
    
    # Increased button height
    app.buttonHeight = 40
    
    # Positioned lower on screen
    app.buttonY = app.height / 2 + 100
    
    # Centered horizontally
    app.startX = app.width / 2 - app.buttonWidth / 2
    
    # Define color scheme using standard CMU Graphics colors
    app.COLORS = {
        # Dark green background
        'background': 'darkGreen',
        
        # Slightly lighter green for gradient
        'background2': 'green',
        
        # Button color
        'button': 'lightGreen',
        
        # Gold accent color
        'gold': 'gold',
        
        # White text
        'white': 'white',
    }

# this function create a new deck of cards
def createDeck(app):
    gameDeck = []
    for currentSuit in app.SUITS:
        for currentRank in app.RANKS:
            currentCard = {'rank': currentRank, 'suit': currentSuit}
            gameDeck.append(currentCard)
    return gameDeck

# deal cards to players from the deck
def dealCards(deck):
    random.shuffle(deck)
    playerHands = []
    for i in range(4):
        currentHand = []
        for j in range(8):
            cardIndex = i * 8 + j
            currentCard = deck[cardIndex]
            currentHand.append(currentCard)
        playerHands.append(currentHand)
    return playerHands

# calculate the position of a card on the screen
def cardPosition(playerIndex, cardIndex, app, cardsInHand):
    # Set spacing to exactly the card width/height to have no gaps between cards
    
    # No spacing between cards horizontally
    spacingX = app.CARD_WIDTH
    
    # No spacing between cards vertically
    spacingY = app.CARD_HEIGHT
    
    # Calculate the total width all cards will take
    totalCardsWidth = cardsInHand * app.CARD_WIDTH
    totalCardsHeight = cardsInHand * app.CARD_HEIGHT
    
    # Calculate margins to center the cards on screen
    marginX = (app.width - totalCardsWidth) / 2
    marginY = (app.height - totalCardsHeight) / 2
    
    # Ensure margins don't go below a minimum value
    minMarginX = 30
    minMarginY = 20
    marginX = max(marginX, minMarginX)
    marginY = max(marginY, minMarginY)
    
    # Calculate positions using the card dimensions
    xAxis = marginX + cardIndex * spacingX
    yAxis = marginY + cardIndex * spacingY

    if playerIndex == 0:
        posX = xAxis
        posY = app.height - app.CARD_HEIGHT
    elif playerIndex == 1:
        posX = 30
        posY = yAxis
    elif playerIndex == 2:
        posX = xAxis
        posY = 30
    elif playerIndex == 3:
        posX = app.width - app.CARD_WIDTH - 30
        posY = yAxis
    return posX, posY

# draw a single card on the screen
def drawCard(app, card, x, y, width, height, showFace):
    if showFace:
        drawRect(x, y, width, height, fill='white', border='black')
        
        # Set color based on suit - red for hearts and diamonds, black for spades and clubs
        textColor = 'red' if card['suit'] in ['♥', '♦'] else 'black'
        drawLabel(card['rank'], x + width / 2, y + 20, size=18, bold=True, fill=textColor)
        drawLabel(card['suit'], x + width / 2, y + 40, size=24, fill=textColor)
    else:
        # Draw the card back image instead of a gray rectangle
        drawImage(app.cardBackImage, x, y, width=width, height=height)

# draw a button on the screen
def drawButton(x, y, width, height, label, fillColor='lightgray'):
    drawRect(x, y, width, height, fill=fillColor, border='black')
    drawLabel(label, x + width / 2, y + height / 2, size=12)

# draw the scoreboard on the screen
def drawScoreboard(app):
    # Draw the main scoreboard box
    boxWidth = 400
    boxHeight = 300
    boxX = app.width/2 - boxWidth/2
    boxY = app.height/2 - boxHeight/2
    drawRect(boxX, boxY, boxWidth, boxHeight, fill='lightBlue', opacity=0.8, border='black')
    
    # Draw the title
    drawLabel('Scoreboard', app.width/2, boxY + 30, size=24, bold=True)
    
    # Only show close button if not at end of round (when shown via scoreboard button)
    if not app.roundComplete and app.showScoreboard:
        closeButtonWidth = 80
        closeButtonHeight = 30
        closeButtonX = boxX + boxWidth - closeButtonWidth - 10
        closeButtonY = boxY + 10
        drawRect(closeButtonX, closeButtonY, closeButtonWidth, closeButtonHeight, 
                fill='lightGray', border='black')
        drawLabel('Close', closeButtonX + closeButtonWidth/2, closeButtonY + closeButtonHeight/2, size=12)
    
    # Draw the mode if it exists
    if app.mode:
        modeText = "Sun" if app.mode == "sun" else "Hukum"
        drawLabel(f"Game Mode: {modeText}", app.width/2, boxY + 60, size=18)
    
    # Draw win score threshold
    drawLabel(f"Win Score: {app.winningScore}", app.width/2, boxY + 85, size=14)
    
    # Draw team boxes
    teamBoxWidth = 150
    teamBoxHeight = 100
    teamBoxY = boxY + 120
    
    # Team 1 box
    team1BoxX = app.width/2 - teamBoxWidth - 20
    drawRect(team1BoxX, teamBoxY, teamBoxWidth, teamBoxHeight, fill='white', border='black')
    drawLabel('Team 1', team1BoxX + teamBoxWidth/2, teamBoxY + 20, size=16, bold=True)
    drawLabel(f'Score: {app.score[0]}', team1BoxX + teamBoxWidth/2, teamBoxY + 50, size=16)
    drawLabel(f'Round: {app.roundScore[0]}', team1BoxX + teamBoxWidth/2, teamBoxY + 80, size=16)
    
    # Team 2 box
    team2BoxX = app.width/2 + 20
    drawRect(team2BoxX, teamBoxY, teamBoxWidth, teamBoxHeight, fill='white', border='black')
    drawLabel('Team 2', team2BoxX + teamBoxWidth/2, teamBoxY + 20, size=16, bold=True)
    drawLabel(f'Score: {app.score[1]}', team2BoxX + teamBoxWidth/2, teamBoxY + 50, size=16)
    drawLabel(f'Round: {app.roundScore[1]}', team2BoxX + teamBoxWidth/2, teamBoxY + 80, size=16)
    
    # Show round winner if available
    if app.roundWinner and app.roundComplete:
        drawLabel(f"Round Winner: {app.roundWinner}!", app.width/2, teamBoxY + teamBoxHeight + 20, 
                 size=18, bold=True, fill='darkBlue')
    
    # If there's a winner, show the winner message and Return to Menu button
    if app.winner:
        # Draw winner message
        drawLabel(f"Mabroook! Team {app.winner}!", app.width/2, boxY + boxHeight - 90, 
                 size=24, bold=True, fill='darkBlue')
        
        # Draw Return to Menu button
        menuButtonWidth = 120
        menuButtonHeight = 40
        menuButtonX = app.width/2 - menuButtonWidth/2
        menuButtonY = boxY + boxHeight - 50
        drawRect(menuButtonX, menuButtonY, menuButtonWidth, menuButtonHeight, 
                fill='green', border='black')
        drawLabel('Return to Menu', menuButtonX + menuButtonWidth/2, 
                 menuButtonY + menuButtonHeight/2, size=16, bold=True)
    else:
        # Only draw Next Round button if round is complete and showing end-of-round scoreboard
        if app.roundComplete:
            nextRoundButtonWidth = 200
            nextRoundButtonHeight = 50
            nextRoundButtonX = app.width/2 - nextRoundButtonWidth/2
            nextRoundButtonY = boxY + boxHeight - 70
            drawRect(nextRoundButtonX, nextRoundButtonY, nextRoundButtonWidth, nextRoundButtonHeight, 
                    fill='lightgreen', border='black')
            drawLabel('Next Round', nextRoundButtonX + nextRoundButtonWidth/2, 
                    nextRoundButtonY + nextRoundButtonHeight/2, size=16, bold=True)

# update the card objects after dealing remaining cards
def updateCardObjects(app):
    # Clear existing objects
    app.cardObjs = []
    
    # Create new card objects for all player hands
    for player_index in range(4):
        hand = app.hands[player_index]
        for card_index in range(len(hand)):
            card = hand[card_index]
            x, y = cardPosition(player_index, card_index, app, len(hand))
            app.cardObjs.append({
                'rank': card['rank'],
                'suit': card['suit'],
                'x': x,
                'y': y,
                'player': player_index,
                'card_index': card_index})

# update the indices of cards in a player's hand after one is played
def updatePlayerCardIndices(app, playerIndex):
    currentCards = []
    for currentCard in app.cardObjs:
        if currentCard['player'] == playerIndex:
            currentCards.append(currentCard)

    for newIndex in range(len(currentCards)):
        currentCard = currentCards[newIndex]
        currentCard['card_index'] = newIndex
        posX, posY = cardPosition(playerIndex, newIndex, app, len(currentCards))
        currentCard['x'] = posX
        currentCard['y'] = posY

# update the game state on each step
def onStep(app):
    constants(app)
    
    # Update temporary message timer
    if app.messageTimer > 0:
        app.messageTimer -= 1
        if app.messageTimer <= 0:
            app.message = None
    
    # Only update card positions if there are cards to update
    if len(app.cardObjs) > 0:
        # Update card positions
        for i in range(len(app.cardObjs)):
            currentCard = app.cardObjs[i]
            currentPlayer = currentCard['player']
            cardCount = 0
            for otherCard in app.cardObjs:
                if otherCard['player'] == currentPlayer:
                    cardCount += 1
            posX, posY = cardPosition(currentPlayer, currentCard['card_index'], app, cardCount)
            currentCard['x'] = posX
            currentCard['y'] = posY

# initialize the game
def onAppStart(app):
    constants(app)
    
    # game starts with the menu screen
    app.menu = True
    
    # game hasn't started yet
    app.gameStarted = False
    
    # link to the game rules
    app.rulesUrl = "https://blog.jawaker.com/en/baloot-rules-en/"
    
    # Debug print
    print("Game initialized with menu =", app.menu)
    
    # Load and scale the logo image
    logoImage = Image.open('C:\\Users\\aaalh\\Downloads\\Baloot.png')
    targetWidth = 400
    ratio = targetWidth / logoImage.size[0]
    newHeight = int(logoImage.size[1] * ratio)
    app.logo = CMUImage(logoImage.resize((targetWidth, newHeight)))
    
    # Load the background image
    bgImage = Image.open('g2.png')
    app.backgroundImage = CMUImage(bgImage)
    
    # Load the main menu background image
    menuBgImage = Image.open('main background.png')
    app.menuBackgroundImage = CMUImage(menuBgImage)
    
    # Load the card back image
    cardBackImage = Image.open('bicyclebacks.jpg')
    app.cardBackImage = CMUImage(cardBackImage)

    # Define button dimensions and text only (not positions)
    app.startButton = {
        'width': 250,
        'height': 60,
        'text': 'Start Game'
    }
    
    app.exitButton = {
        'width': 250,
        'height': 60,
        'text': 'Exit'
    }
    
    app.rulesButton = {
        'width': 180,
        'height': 50,
        'text': 'Game Rules'
    }

    # Use setupInitialDeal to deal 5 cards + middle card
    setupInitialDeal(app)
    
    app.cardObjs = []
    app.playedCards = []
    app.cardsPlayedThisRound = 0
    app.currentPlayer = 0
    app.viewingCards = False
    app.score = {0: 0, 1: 0}
    app.tricks = []
    app.winner = None
    app.roundComplete = False
    # To store round scores
    app.roundScore = {0: 0, 1: 0}
    # To store round winner
    app.roundWinner = None
    
    # Message notification system
    app.message = None
    app.messageTimer = 0

    # Offer round index (for No Buy phase)
    app.offerIndex = 0

    # Mode starts as None so middle card + buttons will show
    app.mode = None
    app.trumpSuit = None
    app.buyerPlayer = None
    
    # Add scoreboard visibility flag
    app.showScoreboard = False
    
    # Set default winning score threshold
    app.winningScore = 10

    # Draw the initial 5 cards for each player
    for playerIndex in range(4):
        playerHand = app.hands[playerIndex]
        for cardIndex in range(len(playerHand)):
            currentCard = playerHand[cardIndex]
            posX, posY = cardPosition(playerIndex, cardIndex, app, len(playerHand))
            app.cardObjs.append({
                'rank': currentCard['rank'],
                'suit': currentCard['suit'],
                'x': posX,
                'y': posY,
                'player': playerIndex,
                'card_index': cardIndex})

def redrawAll(app):
    # first check if we're showing the menu or the game
    if app.menu:
        # draw the main menu if we're in menu mode
        drawMenu(app)
    else:

        # Draw background image first
        drawImage(app.backgroundImage, 0, 0, width=app.width , height=app.height )
        
        # Game status & scores
        drawLabel(f"Baloot - Player {app.currentPlayer + 1}'s Turn", app.width / 2, 10, size=16, bold=True)
        
        # Draw Scoreboard button in top left corner
        scoreboardButtonWidth = 120
        scoreboardButtonHeight = 30
        scoreboardButtonX = 10
        scoreboardButtonY = 10
        drawButton(scoreboardButtonX, scoreboardButtonY, scoreboardButtonWidth, scoreboardButtonHeight, 'Scoreboard', 'lightGreen')
        
        # Draw Exit to Menu button in top right corner
        exitMenuButtonWidth = 120
        exitMenuButtonHeight = 30
        exitMenuButtonX = app.width - exitMenuButtonWidth - 10
        exitMenuButtonY = 10
        drawButton(exitMenuButtonX, exitMenuButtonY, exitMenuButtonWidth, exitMenuButtonHeight, 'Exit to Menu', 'lightGreen')
        
        # Draw Toggle Win Score button in bottom right corner
        toggleScoreButtonWidth = 180
        toggleScoreButtonHeight = 30
        toggleScoreButtonX = app.width - toggleScoreButtonWidth - 10
        toggleScoreButtonY = app.height - toggleScoreButtonHeight - 10
        buttonText = f"Win Score: {app.winningScore}"
        drawButton(toggleScoreButtonX, toggleScoreButtonY, toggleScoreButtonWidth, toggleScoreButtonHeight, buttonText, 'pink')
        
        # Show scoreboard when button is clicked
        if app.showScoreboard:
            drawScoreboard(app)
            return
            
        # Show scoreboard only at the end of the round
        if app.roundComplete:
            drawScoreboard(app)
            return

        # If round is complete, show round score and next round button
        elif app.roundComplete:
            roundBoxWidth = 300
            roundBoxHeight = 180
            roundBoxX = app.width/2 - roundBoxWidth/2
            roundBoxY = app.height/2 - 100
            drawRect(roundBoxX, roundBoxY, roundBoxWidth, roundBoxHeight, fill='lightBlue', opacity=0.8)
            drawLabel("Round Complete!", app.width/2, app.height/2 - 70, size=20, bold=True)
            
            # Show the mode
            modeText = "Sun" if app.mode == "sun" else "Hukum"
            drawLabel(f"Game Mode: {modeText}", app.width/2, app.height/2 - 40, size=16)
            
            # Show round points
            drawLabel(f"Team 1 got {app.roundScore[0]} points this round", 
                     app.width/2, app.height/2 - 10, size=16)
            drawLabel(f"Team 2 got {app.roundScore[1]} points this round", 
                     app.width/2, app.height/2 + 20, size=16)
            
            # Show the round winner
            drawLabel(f"Round Winner: {app.roundWinner}!", 
                     app.width/2, app.height/2 + 50, size=18, bold=True, fill='darkBlue')
            
            # Next Round button
            nextRoundButtonWidth = 150
            nextRoundButtonHeight = 40
            nextRoundButtonX = app.width/2 - nextRoundButtonWidth/2
            nextRoundButtonY = app.height/2 + 90
            drawButton(nextRoundButtonX, nextRoundButtonY, nextRoundButtonWidth, nextRoundButtonHeight, 'Next Round', fillColor='yellow')
            return
        
        # Display temporary notification messages
        elif app.message and app.messageTimer > 0:
            messageBoxWidth = 400
            messageBoxHeight = 60
            messageBoxX = app.width/2 - messageBoxWidth/2
            messageBoxY = app.height/2 - 30
            drawRect(messageBoxX, messageBoxY, messageBoxWidth, messageBoxHeight, fill='lightYellow', opacity=0.8, border='black')
            drawLabel(app.message, app.width/2, app.height/1.5, size=16, bold=True, fill= 'white')

        # Only draw cards if there are cards to draw
        if len(app.cardObjs) > 0:
            # Draw cards in each player's hand
            for currentCard in app.cardObjs:
                cardX = currentCard['x']
                cardY = currentCard['y']
                # Show cards if in buying phase and viewing cards is true, or if in game phase
                showCard = ((app.mode is None and app.viewingCards and currentCard['player'] == app.offerIndex) or
                           (app.mode is not None and app.viewingCards and currentCard['player'] == app.currentPlayer))
                drawCard(app, currentCard, cardX, cardY, app.CARD_WIDTH, app.CARD_HEIGHT, showCard)

            # Draw played cards in the center
            centerX = app.width / 2 - app.CARD_WIDTH / 2
            centerY = app.height / 2 - 100
            for cardIndex in range(len(app.playedCards)):
                currentCard = app.playedCards[cardIndex]
                cardX = centerX + (cardIndex - 1.5) * (app.CARD_WIDTH + 10)
                cardY = centerY
                drawCard(app, currentCard, cardX, cardY, app.CARD_WIDTH, app.CARD_HEIGHT, showFace=True)
            
            # Show trump suit indicator if in Hukum mode
            if app.mode == 'hukum' and app.trumpSuit:
                labelY = app.height - app.CARD_HEIGHT - 25
                labelX = app.width / 2
                
                # Draw "Hukum: " in default color
                drawLabel("Hukum: ", labelX - 20, labelY, size=16, bold=True, align="right")
                
                # Draw the suit symbol in the appropriate color
                if app.trumpSuit in ['♥', '♦']:
                    suitColor = 'red'
                else:
                    suitColor = 'black'
                
                # Draw the suit symbol with color
                drawLabel(app.trumpSuit, labelX + 20, labelY, size=16, bold=True, fill=suitColor)

        # Game buttons (Start) - Only shown when game has started (mode is selected)
        if app.mode is not None and not app.roundComplete:
            drawButton(app.startX, app.buttonY, app.buttonWidth, app.buttonHeight, 'Start', 'lightblue')
            
            # If game mode is set, show whose turn it is
            if not app.viewingCards:
                drawLabel(f"Player {app.currentPlayer + 1}, click 'Start' to see your cards", 
                         app.width / 2, app.height / 1.4, size=16, bold=True, fill = 'white')

        # Show offer phase UI (middle card + buttons) 
        # Only during buying phase
        if app.mode is None:
            midX = app.width / 2 - app.CARD_WIDTH / 2
            midY = app.height / 2 - app.CARD_HEIGHT / 2
            drawCard(app, app.middleCard, midX, midY, app.CARD_WIDTH, app.CARD_HEIGHT, showFace=True)

            drawLabel(f"Player {app.offerIndex + 1} is deciding to buy...", 
                      app.width / 2, midY + app.CARD_HEIGHT + 30, size=14, bold=True, fill = 'white')

            # Button row layout
            buyButtonWidth = 100
            buyButtonHeight = 30
            buttonSpacing = 30
            startX = app.width / 2 - (1.5 * buyButtonWidth + buttonSpacing)
            buttonY = midY + app.CARD_HEIGHT + 60

            # View Cards button
            viewCardsButtonX = app.width / 2 - buyButtonWidth / 2
            viewCardsButtonY = midY - buyButtonHeight - 20
            drawButton(viewCardsButtonX, viewCardsButtonY, buyButtonWidth, buyButtonHeight, 'View Cards', 'lightblue')

            # Buying options buttons
            drawButton(startX, buttonY, buyButtonWidth, buyButtonHeight, 'No Buy', 'lightgray')
            drawButton(startX + buyButtonWidth + buttonSpacing, buttonY, buyButtonWidth, buyButtonHeight, 'Sun', 'gold')
            drawButton(startX + 2 * (buyButtonWidth + buttonSpacing), buttonY, buyButtonWidth, buyButtonHeight, 'Hukum', 'orange')

            # Show helpful instruction
            drawLabel(f"Player {app.offerIndex + 1}, select an option", 
                     app.width / 2, buttonY + buyButtonHeight + 30, size=14, bold=True, fill = 'white')



def drawMenu(app):
    # Draw the main menu background image instead of solid color
    drawImage(app.menuBackgroundImage, 0, 0, width=app.width, height=app.height)
    
    # Draw the logo
    drawImage(app.logo, app.width/2, app.height/4, align='center')
    
    # Calculate button positions based on current window dimensions
    startButtonX = app.width/2 - app.startButton['width']/2
    startButtonY = app.height/2 + 30
    
    exitButtonX = app.width/2 - app.exitButton['width']/2
    exitButtonY = app.height/2 + 120
    
    rulesButtonX = app.width - app.rulesButton['width'] - 30
    rulesButtonY = app.height - 80
    
    # Draw the start button
    drawRect(startButtonX, startButtonY, 
            app.startButton['width'], app.startButton['height'],
            fill='lightGreen', border='gold')
    drawLabel(app.startButton['text'], 
             startButtonX + app.startButton['width']/2,
             startButtonY + app.startButton['height']/2, 
             size=20, bold=True, fill='black')
    
    # Draw the exit button
    drawRect(exitButtonX, exitButtonY, 
            app.exitButton['width'], app.exitButton['height'],
            fill='lightGreen', border='gold')
    drawLabel(app.exitButton['text'], 
             exitButtonX + app.exitButton['width']/2,
             exitButtonY + app.exitButton['height']/2, 
             size=20, bold=True, fill='black')
    
    # Draw the rules button
    drawRect(rulesButtonX, rulesButtonY, 
            app.rulesButton['width'], app.rulesButton['height'],
            fill='lightGreen', border='gold')
    drawLabel(app.rulesButton['text'], 
             rulesButtonX + app.rulesButton['width']/2,
             rulesButtonY + app.rulesButton['height']/2, 
             size=20, bold=True, fill='black')
    
    # Draw the rules URL
    drawLine(rulesButtonX, rulesButtonY + app.rulesButton['height'] + 15, 
            rulesButtonX + app.rulesButton['width'], 
            rulesButtonY + app.rulesButton['height'] + 15, 
            fill='gold', lineWidth=1)
    
    drawLabel(f"Rules: {app.rulesUrl}", 
             rulesButtonX + app.rulesButton['width']/2, 
             rulesButtonY + app.rulesButton['height'] + 35, 
             size=12, fill='gold')

# Handle mouse clicks for cards and buttons
def onMousePress(app, mouseX, mouseY):
    # Debug print
    print(f"Mouse click at: ({mouseX}, {mouseY}), Menu mode: {app.menu}")
    
    # Check if we're in the menu
    if app.menu:
        # Calculate current button positions (same as in drawMenu)
        startButtonX = app.width/2 - app.startButton['width']/2
        startButtonY = app.height/2 + 30
        
        exitButtonX = app.width/2 - app.exitButton['width']/2
        exitButtonY = app.height/2 + 120
        
        rulesButtonX = app.width - app.rulesButton['width'] - 30
        rulesButtonY = app.height - 80
        
        # Check if start button was clicked
        if (mouseX >= startButtonX and mouseX <= startButtonX + app.startButton['width'] and
            mouseY >= startButtonY and mouseY <= startButtonY + app.startButton['height']):
            print("Start button clicked!")
            app.menu = False
            app.gameStarted = True
            return
        
        # Check if exit button was clicked
        if (mouseX >= exitButtonX and mouseX <= exitButtonX + app.exitButton['width'] and
            mouseY >= exitButtonY and mouseY <= exitButtonY + app.exitButton['height']):
            print("Exit button clicked!")
            app.quit()
            return
        
        # Check if rules button was clicked
        if (mouseX >= rulesButtonX and mouseX <= rulesButtonX + app.rulesButton['width'] and
            mouseY >= rulesButtonY and mouseY <= rulesButtonY + app.rulesButton['height']):
            print("Rules button clicked!")
            import webbrowser
            webbrowser.open(app.rulesUrl)
            return
    else:
        # Check if Toggle Win Score button was clicked
        toggleScoreButtonWidth = 180
        toggleScoreButtonHeight = 30
        toggleScoreButtonX = app.width - toggleScoreButtonWidth - 10
        toggleScoreButtonY = app.height - toggleScoreButtonHeight - 10
        
        if (mouseX >= toggleScoreButtonX and mouseX <= toggleScoreButtonX + toggleScoreButtonWidth and
            mouseY >= toggleScoreButtonY and mouseY <= toggleScoreButtonY + toggleScoreButtonHeight):
            # Toggle between 10 and 152
            app.winningScore = 152 if app.winningScore == 10 else 10
            app.message = f"Winning score threshold set to {app.winningScore}"
            app.messageTimer = 60
            return
        
        # Check if Scoreboard is visible and close button was clicked
        if app.showScoreboard and not app.roundComplete:
            boxWidth = 400
            boxHeight = 300
            boxX = app.width/2 - boxWidth/2
            boxY = app.height/2 - boxHeight/2
            
            closeButtonWidth = 80
            closeButtonHeight = 30
            closeButtonX = boxX + boxWidth - closeButtonWidth - 10
            closeButtonY = boxY + 10
            
            if (mouseX >= closeButtonX and mouseX <= closeButtonX + closeButtonWidth and
                mouseY >= closeButtonY and mouseY <= closeButtonY + closeButtonHeight):
                app.showScoreboard = False
                return
        
        # Check if Scoreboard button was clicked (in top left corner)
        scoreboardButtonWidth = 120
        scoreboardButtonHeight = 30
        scoreboardButtonX = 10
        scoreboardButtonY = 10
        
        if (mouseX >= scoreboardButtonX and mouseX <= scoreboardButtonX + scoreboardButtonWidth and
            mouseY >= scoreboardButtonY and mouseY <= scoreboardButtonY + scoreboardButtonHeight):
            print("Scoreboard button clicked!")
            # Toggle scoreboard visibility
            app.showScoreboard = not app.showScoreboard
            return
            
        # Check if Exit to Menu button was clicked (only available during gameplay)
        exitMenuButtonWidth = 120
        exitMenuButtonHeight = 30
        exitMenuButtonX = app.width - exitMenuButtonWidth - 10
        exitMenuButtonY = 10
        
        if (mouseX >= exitMenuButtonX and mouseX <= exitMenuButtonX + exitMenuButtonWidth and
            mouseY >= exitMenuButtonY and mouseY <= exitMenuButtonY + exitMenuButtonHeight):
            print("Exit to Menu button clicked!")
            # Return to menu
            app.menu = True
            # Reset all game variables
            onAppStart(app)
            return
            
        # If round is complete, check for Next Round button
        if app.roundComplete:
            boxWidth = 400
            boxHeight = 300
            boxX = app.width/2 - boxWidth/2
            boxY = app.height/2 - boxHeight/2
            
            if app.winner:
                # Check for Return to Menu button
                menuButtonWidth = 120
                menuButtonHeight = 40
                menuButtonX = app.width/2 - menuButtonWidth/2
                menuButtonY = boxY + boxHeight - 50
                
                if (mouseX >= menuButtonX and mouseX <= menuButtonX + menuButtonWidth and
                    mouseY >= menuButtonY and mouseY <= menuButtonY + menuButtonHeight):
                    # Reset scores
                    app.score = {0: 0, 1: 0}
                    app.winner = None
                    # Return to menu
                    app.menu = True
                    onAppStart(app)
                    return
            else:
                # Check for Next Round button
                nextRoundButtonWidth = 200
                nextRoundButtonHeight = 50
                nextRoundButtonX = app.width/2 - nextRoundButtonWidth/2
                nextRoundButtonY = boxY + boxHeight - 70
                
                if (mouseX >= nextRoundButtonX and mouseX <= nextRoundButtonX + nextRoundButtonWidth and
                    mouseY >= nextRoundButtonY and mouseY <= nextRoundButtonY + nextRoundButtonHeight):
                    savedScore = app.score.copy()
                    onAppStart(app)
                    app.score = savedScore
                    # Keep the game going without showing menu
                    app.menu = False
                    app.gameStarted = True
                    return

        # Start button - only active if game has started (mode is set) and round not complete
        if app.mode is not None and not app.roundComplete:
            if mouseX >= app.startX and mouseX <= app.startX + app.buttonWidth:
                if mouseY >= app.buttonY and mouseY <= app.buttonY + app.buttonHeight:
                    app.viewingCards = True
                    return
            
        # View Cards button during buying phase
        if app.mode is None:
            midX = app.width / 2 - app.CARD_WIDTH / 2
            midY = app.height / 2 - app.CARD_HEIGHT / 2
            buyButtonWidth = 100
            buyButtonHeight = 30
            viewCardsButtonX = app.width / 2 - buyButtonWidth / 2
            viewCardsButtonY = midY - buyButtonHeight - 20
            
            if (mouseX >= viewCardsButtonX and mouseX <= viewCardsButtonX + buyButtonWidth and
                mouseY >= viewCardsButtonY and mouseY <= viewCardsButtonY + buyButtonHeight):
                app.viewingCards = True
                return

            # Buying options buttons
            buttonSpacing = 30
            startX = app.width / 2 - (1.5 * buyButtonWidth + buttonSpacing)
            buttonY = midY + app.CARD_HEIGHT + 60

            # No Buy button
            if (mouseX >= startX and mouseX <= startX + buyButtonWidth and
                mouseY >= buttonY and mouseY <= buttonY + buyButtonHeight):
                app.offerIndex = (app.offerIndex - 1) % 4
                if app.offerIndex == 0:
                    app.message = "Everyone passed - Starting new deal"
                    app.messageTimer = 60
                    savedScore = app.score.copy()
                    onAppStart(app)
                    app.score = savedScore
                    # Keep the game going without showing menu
                    app.menu = False
                    app.gameStarted = True
                else:
                    app.currentPlayer = app.offerIndex
                app.viewingCards = False
                return

            # Sun button
            if (mouseX >= startX + buyButtonWidth + buttonSpacing and 
                mouseX <= startX + 2*buyButtonWidth + buttonSpacing and
                mouseY >= buttonY and mouseY <= buttonY + buyButtonHeight):
                app.mode = 'sun'
                app.buyerPlayer = app.offerIndex
                app.hands[app.offerIndex].append(app.middleCard)
                dealRemainingCards(app)
                updateCardObjects(app)
                app.currentPlayer = app.offerIndex
                app.viewingCards = False
                return

            # Hukum button
            if (mouseX >= startX + 2*(buyButtonWidth + buttonSpacing) and 
                mouseX <= startX + 3*buyButtonWidth + buttonSpacing and
                mouseY >= buttonY and mouseY <= buttonY + buyButtonHeight):
                app.mode = 'hukum'
                app.trumpSuit = app.middleCard['suit']
                app.buyerPlayer = app.offerIndex
                app.hands[app.offerIndex].append(app.middleCard)
                dealRemainingCards(app)
                updateCardObjects(app)
                app.currentPlayer = app.offerIndex
                app.viewingCards = False
                return
                
        # Card playing logic - when game has started and cards are visible
        if app.mode is not None and app.viewingCards:
            # Check if the click is on a card in the current player's hand
            for cardObj in app.cardObjs:
                if cardObj['player'] == app.currentPlayer:
                    cardX = cardObj['x']
                    cardY = cardObj['y']
                    
                    # Check if click is within card boundaries
                    if (mouseX >= cardX and mouseX <= cardX + app.CARD_WIDTH and
                        mouseY >= cardY and mouseY <= cardY + app.CARD_HEIGHT):
                        
                        # Get the card from hand
                        cardIndex = cardObj['card_index']
                        selectedCard = app.hands[app.currentPlayer][cardIndex]
                        
                        # Validate play based on lead suit
                        validPlay = True
                        
                        # First card of the trick can be any card
                        if app.leadSuit is None:
                            app.leadSuit = selectedCard['suit']
                        # Otherwise must follow suit if possible
                        else:
                            # Check if player has any cards of the lead suit
                            hasLeadSuit = any(card['suit'] == app.leadSuit for card in app.hands[app.currentPlayer])
                            
                            # Must follow suit if you have it
                            if hasLeadSuit and selectedCard['suit'] != app.leadSuit:
                                validPlay = False
                                app.message = "You must follow the lead suit!"
                                app.messageTimer = 60
                        
                        if validPlay:
                            print(f"Playing card: {selectedCard['rank']} of {selectedCard['suit']}")
                            
                            # Remove card from player's hand
                            playedCard = app.hands[app.currentPlayer].pop(cardIndex)
                            
                            # Add player info to the card
                            playedCard['player'] = app.currentPlayer
                            
                            # Add to played cards
                            app.playedCards.append(playedCard)
                            app.cardsPlayedThisRound += 1
                            
                            # Remove card object
                            for i, obj in enumerate(app.cardObjs):
                                if (obj['player'] == app.currentPlayer and 
                                    obj['card_index'] == cardIndex):
                                    app.cardObjs.pop(i)
                                    break
                            
                            # Update indices for remaining cards
                            updatePlayerCardIndices(app, app.currentPlayer)
                            
                            # Move to next player
                            app.currentPlayer = (app.currentPlayer - 1) % 4
                            app.viewingCards = False
                            
                            # If all 4 players have played, process the end of trick
                            if app.cardsPlayedThisRound == 4:
                                proccesToEndOfTrick(app)
                            
                            return

runApp(800,500)