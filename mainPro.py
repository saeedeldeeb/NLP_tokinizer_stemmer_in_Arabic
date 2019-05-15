#!/usr/bin/env python
import nltk
import re
from PyQt5.QtWidgets import *
import sys
import mysql.connector


# prefixAR = ب / ك / س / و / ال / ا / ل / ف
# suffixAR = ان / ون / ين / ات / وا / تم / هما / هم / كم / ى / ه / ت / ك / ا / ن / و
class Window(QWidget):
    stable_nouns = ['كرة', 'محمد', 'احمد', 'صلاح', 'ماجد', 'سعيد']
    prefixAR = ['است', 'مست', 'تست', 'ن', 'يست', 'سا', 'س', 'ال', 'ت', 'ي', 'ا', 'م', 'الا']
    suffixAR = ['ون', 'ة', 'ت', 'وا', 'ا', 'ين', 'ان', 'ن', 'ات']
    PRON_AR = ['هي', 'نحن', 'هو', 'هن', 'هما', 'هم']
    VB_AR = ['ي', 'ا', 'ن', 'سا', 'س', 'ت', 'است']
    PROP_AR = ['عن', 'علي', 'من', 'الي', 'كي', 'منذ', 'في']



    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        self.lineedit = QLineEdit()
        self.lineedit.returnPressed.connect(self.return_pressed)
        layout.addWidget(self.lineedit)
        self.label = QLabel("Stem")
        layout.addWidget(self.label)
        self.label2 = QLabel("tag")
        layout.addWidget(self.label2)
        button = QPushButton("Get ST")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)

    def on_button_clicked(self):
        print("The button was pressed!")
        print(self.lineedit.text())
        self.tokenizeFile(self.lineedit.text())
        print(self.StemmerAR(self.lineedit.text()))
        print(self.POS_Tagger_AR(self.lineedit.text()))
        self.label.setText(str(self.StemmerAR(self.lineedit.text())))
        self.label2.setText(str(self.POS_Tagger_AR(self.lineedit.text())))
        self.databasecon()


    def return_pressed(self):
        print(self.lineedit.text())


#--------DataBase Area-------------
    def databasecon(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="pythondatabase"
        )

        print(mydb)
        mycursor = mydb.cursor()

        sql = "INSERT INTO nlp_table (userWord, wordStem , POS) VALUES (%s, %s ,%s)"
        val = (self.lineedit.text(), self.StemmerAR(self.lineedit.text()), str(self.POS_Tagger_AR(self.lineedit.text())))
        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")
        # ----------- Tokenization Area -----------------

   # sentence = ""

    def tokenizeFile(self,sentence):
        print(nltk.regexp_tokenize(sentence, "[\u0600-\u06FF]+"))  # 0750–077F arabic letters


    # ------------ Stemming Area -------------------

    def StemmerAR(self,word):
        if word in self.PRON_AR:
            return word
        if word in self.PROP_AR:
            return word
        if word in self.stable_nouns:
            return word
        for pre in self.prefixAR:
            if word.startswith(pre):
                word = word[len(pre):]
                print(pre)
        for suf in self.suffixAR:
            if word.endswith(suf):
                word = word[:len(word) - len(suf)]
                print(suf)
            # compare String with pattern then substitute
            if re.match('[ن|م|أ|ا|ت|ي]ن[أ-ي]', word):
                word = re.sub('[ن|م|أ|ا|ي|ت]ن', "", word)
            elif re.match('م[أ-ي]ا[أ-ي]{2}', word):
                word = re.sub('م', "", word)
                word = re.sub('ا', "", word)
            elif re.match('م[أ-ي]ا[أ-ي]ي[أ-ي]', word):
                word = re.sub('م', "", word)
                word = re.sub('ا', "", word)
                word = re.sub('ي', "", word)
            elif re.match('[أ-ي]{2}ا[أ-ي]', word):
                word = re.sub('ا', "", word)
            elif re.match('ا[أ-ي]ت[أ-ي]ا[أ-ي]', word):
                # word = re.sub('م', "", word)
                word = re.sub('ا', "", word)
                word = re.sub('ت', "", word)
            elif re.match('[أ-ي]{2}و[أ-ي]', word):
                word = re.sub('و', "", word)
            elif re.match('[أ-ي]{1}ا[أ-ي]', word):
                word = re.sub('ا', "", word)
            elif re.match('م[أ-ي]{2}و[أ-ي]', word):
                word = re.sub('م', "", word)
                word = re.sub('و', "", word)
            elif re.match('م[أ-ي]{2}ا[أ-ي]', word):
                word = re.sub('م', "", word)
                word = re.sub('ا', "", word)
            elif re.match('[أ-ي]{2}ي[أ-ي]', word):
                word = re.sub('ي', "", word)
            elif re.match('م[أ-ي]{3}', word):
                word = re.sub('م', "", word)
        return word


#-----------POS Area-----------------
    def POS_Tagger_AR(self,word):
        dictionary = {}
        for verb in self.VB_AR:
            if word.startswith(verb):
                dictionary[word] = 'VB-AR'
                break
            else:
                dictionary[word] = 'NOUN'
        for pron in self.PRON_AR:
            if word == pron:
                dictionary[word] = 'PRON'
        for prop in self.PROP_AR:
            if word == prop:
                dictionary[word] = 'PROP'
        if word.startswith('ال'):
            dictionary[word] = 'NOUN'
        return dictionary


app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec_())

