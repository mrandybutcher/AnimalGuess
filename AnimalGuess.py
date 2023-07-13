import sys
import json
from json import JSONEncoder



class Question(object):
  def __init__(self, qText):
    self.questionText = qText

  def ask(self):
  	ans = raw_input(self.questionText + "\n")
  	self.handleAnswer(ans)

  def handleAnswer(self, answer):
  	if (answer.lower().startswith("y")):
  		self.handleYes()
  	else:
  		self.handleNo()


class AnimalGuess(Question):
  def __init__(self, aName):
    super(AnimalGuess, self).__init__("Is it " + aName + "?")
    self.animalName = aName

  def handleYes(self):
    print("\nHURRAH!!!\n")
    playAgainPrompt()

  def handleNo(self):
    global previousYesNoQuestion
    global previousYesOrNo
    global animalChecklist
    correctAnswer = raw_input("I give up! What is the correct answer?\n")
    correctAnswer = ensureArticle(correctAnswer)
    allGood = True
    if (contains(animalChecklist, correctAnswer)):
      allGood = False

    while not allGood:
      # We already know this animal!
      sure = raw_input("Oh... I already know that animal. Are your answers above definitely correct?\n")
      if (sure.lower().startswith("y")):
        print("Someone has misinformed me in the past! Please check questions.txt. I'll remember what you've told me though.")
        allGood = True
      else:
        correctAnswer = raw_input("Please tell me a new answer which works for the above questions, or say cancel\n")
        if correctAnswer.lower().startswith("cancel"):
        	print("No problem")
        	playAgainPrompt()
        	allGood = True
        	break
        correctAnswer = ensureArticle(correctAnswer)
        if (not contains(animalChecklist, correctAnswer)):
        	allGood = True

    newAnimal = AnimalGuess(correctAnswer)
    distQuestion = raw_input("Tell me a Yes/No question which would distinguish between " + self.animalName + " and " + correctAnswer + "?\n")
    distQuestion = ensureCapital(distQuestion)
    distQuestionAnswer = raw_input("What is the answer for " + correctAnswer + "?\n")
    newYesNoQuestion = YesNoQuestion(distQuestion, "", "")
    if (distQuestionAnswer.lower().startswith("y")):
      newYesNoQuestion.yesResponse = newAnimal
      newYesNoQuestion.noResponse = self
    else:
      newYesNoQuestion.yesResponse = self
      newYesNoQuestion.noResponse = newAnimal
    
    if (previousYesOrNo.lower().startswith("y")):
      previousYesNoQuestion.yesResponse = newYesNoQuestion
    else:
      previousYesNoQuestion.noResponse = newYesNoQuestion
    print("Thank you, I'll remember that for next time\n")
    playAgainPrompt()


class YesNoQuestion(Question):
  def __init__(self, qText, yResponse, nResponse):
    super(YesNoQuestion, self).__init__(qText)
    self.yesResponse = yResponse
    self.noResponse = nResponse

  def handleYes(self):
    global previousYesNoQuestion
    global previousYesOrNo
    previousYesNoQuestion = self
    previousYesOrNo = "y"
    self.yesResponse.ask()
  	
  def handleNo(self):
    global previousYesNoQuestion
    global previousYesOrNo
    previousYesNoQuestion = self
    previousYesOrNo = "n"
    self.noResponse.ask()


class QuestionEncoder(JSONEncoder):
  def default(self, o):
    return o.__dict__


def playAgainPrompt():
  saveQuestionsToFile()
  playAgain = raw_input("Do you want to play again?\n")
  if (playAgain.lower().startswith("n")):
    print("See you next time!\n")
    sys.exit()
  else:
  	runGame()

def clearScreen():
    print(chr(27)+'[2j')
    print('\033c')
    print('\x1bc')


def runGame():
  clearScreen()
  raw_input("Think of an animal. Press return when you've thought of it.\n")
  questions.ask()


def decode_question(dct):
  global animalChecklist
  if "animalName" in dct:
  	# It's an AnimalGuess
  	# Make a note in the animal list to check for duplicates
    animalChecklist.append(dct["animalName"])
    return AnimalGuess(dct["animalName"])
  elif "yesResponse" in dct:
  	# It's a YesNoQuestion
    return YesNoQuestion(dct["questionText"], dct["yesResponse"], dct["noResponse"])
  return dct

def readQuestionsFromFile():
  global questions
  with open("questions.json") as complex_data:
    data = complex_data.read()
    questions = json.loads(data, object_hook=decode_question)


def encode_question(q):
  if isinstance(q, AnimalGuess):
  	return {"animalName": q.animalName}
  elif isinstance(q, YesNoQuestion):
    return {"questionText": q.questionText, "yesResponse": q.yesResponse, "noResponse": q.noResponse}
  else:
    type_name = z.__class__.__name__
    raise TypeError("Object of type '{type_name}' is not JSON serializable!")


def saveQuestionsToFile():
  global questions
  # encode to json
  data = json.dumps(questions, default=encode_question)
  # write to file
  with open("questions.json","w") as f:
    f.write(data)

def contains(in_array, value):
  found = False
  for animal in in_array:
    if value == animal:
      found = True
  return found

def ensureArticle(animal):
  animal = animal.lower()
  if (not animal.startswith("a ")) and (not animal.startswith("an ")):
    if animal[:1] in ["a","e","i","o","u"]:
      return "an " + animal.lower()
    else:
      return "a " + animal.lower()
  return animal

def ensureCapital(question):
  if not question[:1].isupper():
    question = question[:1].upper() + question[1:]
  return question


#questions = YesNoQuestion("Does it have four legs?", AnimalGuess("a labrador"), AnimalGuess("a magpie"))
questions = None
animalChecklist = []
readQuestionsFromFile()
previousYesNoQuestion = questions
previousYesOrNo = None
runGame()
