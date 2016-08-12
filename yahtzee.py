import random
import pickle
import os
import time
from colorama import *
init(autoreset=True)

class bcolors:
    HEADER = Fore.MAGENTA
    OKBLUE = Fore.BLUE
    OKGREEN = Fore.GREEN
    WARNING = Fore.BLACK
    FAIL = Fore.RED
    ENDC = Fore.RESET

playerScore = 0
users_moves = {}
bonus_given = False
yahtzee_won = False

def roll():
    global current_dice
    current_dice = rolldie(5)
    replacing = []
    replacing_indexes = []
    rolls = 0
    print(bcolors.OKGREEN + "Your first roll is:", current_dice, "\n")
    result = input(bcolors.HEADER + "Keep these dice? (y/n) " + bcolors.ENDC)
    result = (result.lower()).strip()
    while result not in ("y", "n"):
        result = input(bcolors.FAIL + "\nTry again. " + bcolors.ENDC)
        result = (result.lower().strip())
    if result == "n":
        while rolls != 2:
            if rolls != 0:
                print(bcolors.OKGREEN + "Current dice:", current_dice, "\n")
                result = input(bcolors.HEADER + "Keep these dice (y/n) (default: n)? " + bcolors.ENDC)
                result = (result.lower()).strip()
                if result == "y":
                    break;
            indexes = input(bcolors.HEADER + "Type the ordinal numbers (first would be 1, second would be 2, etc)\nof dice to replace. (no spaces) " + bcolors.ENDC)
            try:
                replaced_dice = list(indexes)
                for index in replaced_dice:
                    skip = False
                    #subtracting 1 to convert ordinal numbers to indexes in an array
                    array_index = int(index) - 1
                    if array_index < 0:
                        raise IndexError("Not an ordinal number!")
                    #Error checking to make sure replaced dice are only replaced once
                    while array_index in replacing_indexes:
                        print(bcolors.FAIL + "Error, already replacing " + str(current_dice[array_index]) + ".\n")
                        skip = True
                        break
                    if skip:
                        continue
                    replacing.append(current_dice[array_index])
                    replacing_indexes.append(array_index)
            except IndexError:
                print(bcolors.FAIL + "\nThere are only 5 dice!\n" + bcolors.ENDC)
                replacing = []
                replacing_indexes = []
                continue
            except:
                 print(bcolors.FAIL + "\nTry again.\n" + bcolors.ENDC)
                 replacing = []
                 replacing_indexes = []
                 continue
            if len(replacing) == 0:
                print(bcolors.OKGREEN + "Keeping all dice..." + bcolors.ENDC)
                break;
            print(bcolors.OKBLUE + "Replacing", replacing, "" + bcolors.ENDC)
            keeping = []
            for index in (set([0,1,2,3,4]) - set(replacing_indexes)):
                keeping.append(current_dice[index])
            new_dice = rolldie(len(replacing))
            for new_die in new_dice:
                keeping.append(new_die)
            current_dice = keeping
            replacing = []
            replacing_indexes = []
            rolls += 1
    print(bcolors.OKGREEN + "\nNew roll is: %s\n" %(current_dice) + bcolors.ENDC)

def rolldie(numToRoll):
    diechoices = ['1', '2', '3', '4', '5', '6']
    result = []
    for x in range(numToRoll):
        result.append(int(random.choice(diechoices)))
    return result

def countDice(number):
    counter = 0
    for n in current_dice:
        if n == number:
            counter = counter + 1
    score = counter * number
    return score

def choosePoints():
    key = allOptions[0]
    value = allOptions[1]
    bestOption = max(value)
    counter = 1;
    for index in range(0, len(key)):
        if value[index] == bestOption:
            print('\033[1m' + str(counter) + ":\t", end='\033[0m')
            print('\033[1m' + str(key[index]) + ":\t" + str(value[index]) + " points" + '\033[0m')
        else:
            print(str(counter) + ":\t", end="")
            print(str(key[index]) + ":\t" + str(value[index]) + " points.")
        counter += 1
    global playerScore
    global allKeysTaken
    option = input(bcolors.HEADER + "\nSelect an option by entering its sequential number.\n" + bcolors.ENDC)
    while True:
        try:
            option = key[int(option) - 1]
            option = (option.strip()).lower()
            for index in range(0, len(key)):
                keycopy = (key[index].strip(" ")).lower()
                if keycopy == option:
                    playerScore = playerScore + int(value[index])
                    users_moves[key[index]] = int(value[index])
                    return
        except:
            option = input(bcolors.FAIL + "Try again.\n" + bcolors.ENDC)

def checkFullHouse():
    for num in current_dice:
        if current_dice.count(num) == 3:
            for second_num in current_dice:
                if current_dice.count(second_num) == 2:
                    return 25
    return 0

def ofAKind(numOfKind):
    global yahtzee_won
    for number in current_dice:
        if current_dice.count(number) == numOfKind:
            if numOfKind == 5:
                if yahtzee_won:
                    return 100;
                else:
                    yahtzee_won = True
                    return 50
            else:
                return numOfKind * number
    return 0

def checkStraight(smallOrLarge):
    sortedArray = list(set(current_dice))
    if smallOrLarge == 1:
        if [1,2,3,4,5] == sortedArray or [2,3,4,5,6] == sortedArray:
            return 40
    else:
        if all(x in sortedArray for x in [1,2,3,4]) or all(x in sortedArray for x in [2,3,4,5]) or all(x in sortedArray for x in [3,4,5,6]):
            return 30
    return 0

def removeTakenOptions():
    key = allOptions[0]
    value = allOptions[1]
    index = len(key) - 1
    while index >= 0:
        if "Pass          " not in key[index]:
            if value[index] == 0:
                del key[index]
                del value[index]
        index -= 1
    global users_moves
    for takenKey in users_moves.keys():
        index = len(key) - 1
        while index >= 0:
            if "Pass          " not in takenKey:
                if takenKey is key[index]:
                    del key[index]
                    del value[index]
            index -= 1

def over63():
    global bonus_given
    if bonus_given:
        return False;
    global users_moves
    sumOfFirstSix = 0
    arrayToCheck = ['Ones          ', 'Twos          ', 'Threes        ',
                     'Fours         ', 'Fives         ', 'Sixes         ']
    if all(x in list(users_moves.keys()) for x in arrayToCheck):
        for index in arrayToCheck:
            sumOfFirstSix += int(users_moves[index])
    if sumOfFirstSix >= 63:
        bonus_given = True
        return True
    else:
        return False

def printScoreCard(allOptions):
    global playerScore
    printedBonus = True
    print(bcolors.HEADER + "Yahtzee Score Card" + bcolors.ENDC)
    for key in allOptions:
        if key == "Over 63 = +35 ":
            print(bcolors.OKBLUE + key + "|\t" + bcolors.ENDC, end = "")
        elif key != "Pass          ":
            print(bcolors.OKBLUE + key + "|\t" + bcolors.ENDC, end="")
        for k, v in users_moves.items():
            if k == key and k != "Pass          ": #already taken
                print(bcolors.OKGREEN + str(v), end = "")
            if key == "Over 63 = +35 ":
                if over63():
                    playerScore += 35
                if bonus_given and printedBonus:
                    print(bcolors.OKGREEN + "35" + bcolors.ENDC, end = "")
                    printedBonus = False
        print()
    print("Current Score: " + str(playerScore))

try:
    inFile = open("highscores.dat", "rb")
    highScore = pickle.load(inFile)
    print(bcolors.HEADER + "The high score is: " + str(highScore) + ". Try to beat it!")
except EOFError:
    pass
for turnNumber in range(13):
    print(bcolors.HEADER+ "Turn %s started.\n" %(turnNumber + 1) + bcolors.ENDC)
    roll()

    allOptions = [   ["Ones          ", "Twos          ", "Threes        ",
                     "Fours         ", "Fives         ", "Sixes         ",
                     "Over 63 = +35 ",
                     "3 of a kind   ", "4 of a kind   ", "Full House    ",
                     "Small Straight", "Large Straight", "Yahtzee       ",
                     "Chance        ", "Pass          "],
                    [countDice(1), countDice(2), countDice(3),
                     countDice(4), countDice(5), countDice(6), 0,
                     ofAKind(3), ofAKind(4), checkFullHouse(),
                     checkStraight(0), checkStraight(1), ofAKind(5),
                     sum(current_dice), 0]]
    allKeys = allOptions[0].copy()
    removeTakenOptions()
    choosePoints()
    time.sleep(0.5)
    os.system('cls' if os.name=='nt' else 'clear')
    print(bcolors.HEADER + "\nTurn", turnNumber + 1, "completed." + bcolors.ENDC)
    print(bcolors.OKGREEN + "Current Score Card:\n\n" + bcolors.ENDC)
    printScoreCard(allKeys)

print(bcolors.HEADER + "Game Over! Your score was: " + str(playerScore) + bcolors.ENDC)
outFile = open("highscores.dat", "wb")
try:
    if playerScore > highScore:
        highScore = playerScore
    pickles.dump(highScore, outFile)
except NameError:
    pickle.dump(playerScore, outFile)
outFile.close()
