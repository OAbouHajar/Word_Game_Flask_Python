from flask import Flask, render_template, request, session
from collections import Counter
import random
import time
from flask import g
import csv
import pickle
from operator import itemgetter

app = Flask(__name__)  # "dunder name".
app.secret_key = "any random string"


def start_the_Time():
    startTime = time.time()
    return startTime


def open_File_As_List():
    with open("words.txt") as re:
        fileData = re.readlines()
    file_List_No_N = [line.rstrip("\n") for line in fileData]
    file_List_No_S = [line.replace("'s", "") for line in file_List_No_N]
    return file_List_No_S


def pick_Random_Word():
    randomWord = ""
    # chose only the words with lenght of 7
    while len(randomWord) != 7:
        randomWord = random.choice(open_File_As_List())
    # create a dictionary
    dicRandWork = Counter(randomWord.lower())
    random_Word_lower = randomWord.lower()
    return random_Word_lower


def check_The_Answer_lenght(theAnswer):
    the_Answer_length = len(theAnswer.split())
    return the_Answer_length


def check_dupes_words(theAnswer):
    listAnser = theAnswer.split()
    dupes_words = [x for n, x in enumerate(listAnser) if x in listAnser[:n]]
    return dupes_words


def check_word_in_dic(theAnswer):
    inDic = True
    words = ""
    for word in theAnswer.split():
        if (word in open_File_As_List()) and (len(word) >= 3):
            pass
        else:
            inDic = False
            words += " " + word

    session["words"] = words
    return inDic


def check_No_Extra_Letters(theAnswer):
    dicyes = True
    extraLetters = ""
    listAnswer = theAnswer.split()
    dicRandWork = Counter(session["RanWord"])
    for n in range(check_The_Answer_lenght(theAnswer)):
        dicAnswer = Counter(listAnswer[n])
        for k, v in dicAnswer.items():
            if dicAnswer[k] > dicRandWork[k]:
                dicyes = False
                extraLetters += (
                    ">>>>' " + str(k) + " ' in Word ' " + str(listAnswer[n]) + " ' \n"
                )
    session["extraLetters"] = extraLetters
    return dicyes


def check_If_Same_Source_Word(theAnswer):
    sameSourceWord = True
    for same in theAnswer.split():
        if same == session["RanWord"]:
            sameSourceWord = False
    return sameSourceWord


@app.route("/")
@app.route("/start")
def start_page():
    return render_template("start.html", the_title="Welcome to the Game")


@app.route("/displayform")
def display_form():
    session["Stime"] = start_the_Time()
    session["RanWord"] = pick_Random_Word()
    return render_template(
        "form.html",
        the_title="Enter you answer please! :",
        wordGuess=session["RanWord"],
    )


@app.route("/processform", methods=["POST"])
def process_form():
    Mistake = ""
    theanswer = request.form["theanswer"]
    answer = theanswer.lower()
    checkDupes = True
    checkDic = True
    sameRandomWord = True
    checkExtra = True
    Mistake = "your Answer Is " + str(check_The_Answer_lenght(answer)) + " words\n"
    if len(check_dupes_words(answer)) > 0:
        Mistake += "you Dublicate Words are : " + str(sorted(check_dupes_words(answer)))
        checkDupes = False
    if (check_word_in_dic(answer)) == False:
        Mistake += "the Words :: '" + session["words"] + "' are not in Dictionary \n"
        checkDic = False
    if (check_No_Extra_Letters(answer)) == False:
        Mistake += "your word has extra letters ::  " + session["extraLetters"] + "\n"
        checkExtra = False
    if check_If_Same_Source_Word(answer) == False:
        Mistake += "you Have Entered the same Source Word\n"
        sameRandomWord = False
    if (
        check_The_Answer_lenght(answer) == 7
        and checkDic == True
        and checkExtra == True
        and sameRandomWord == True
        and check_The_Answer_lenght(answer) == 7
    ):
        page = "thanks.html"
        answerOK = "Your Answer was right"
    else:
        page = "thanksFail.html"
        answerOK = "Your Answer was NOT right"

    ETime = time.time()
    TotalTime = int(ETime - session["Stime"])
    session["Ttime"] = TotalTime
    return render_template(
        page,
        finalAnswer=answerOK,
        time=TotalTime,
        the_title="Thanks for your data!",
        Mistake=Mistake,
    )


@app.route("/enterResults", methods=["POST"])
def Enter_Results():
    name = request.form["thewinner"]
    time = session["Ttime"]
    dataDic = {"name": name, "score": time}
    pickle.dump(dataDic, open("winnerData.dat", "ab"))
    data = []
    with open("winnerData.dat", "rb") as fr:
        try:
            while True:
                data.append(pickle.load(fr))
        except EOFError:
            pass
    newlist = sorted(data, key=itemgetter("score"))
    newTenList = newlist[:10]
    topTenOutPut = ""
    for i in range(10):
        topTenOutPut += (
            "Number :"
            + str(i + 1)
            + " >> \t "
            + str(newTenList[i]["name"] + " ," + str(newTenList[i]["score"]))
            + " Seconds ..\n"
        )
    pos = [i for i, _ in enumerate(newlist) if _["name"] == name][0]
    pos += 1
    return render_template(
        "results.html",
        the_title="Your Postion on the table!",
        results=topTenOutPut,
        POS=str(pos),
    )


app.run(debug=True)
