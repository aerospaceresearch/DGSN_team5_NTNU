morseAlphabet ={
        "A" : ".-",
        "B" : "-...",
        "C" : "-.-.",
        "D" : "-..",
        "E" : ".",
        "F" : "..-.",
        "G" : "--.",
        "H" : "....",
        "I" : "..",
        "J" : ".---",
        "K" : "-.-",
        "L" : ".-..",
        "M" : "--",
        "N" : "-.",
        "O" : "---",
        "P" : ".--.",
        "Q" : "--.-",
        "R" : ".-.",
        "S" : "...",
        "T" : "-",
        "U" : "..-",
        "V" : "...-",
        "W" : ".--",
        "X" : "-..-",
        "Y" : "-.--",
        "Z" : "--..",
        " " : " ",
	"1" : ".----",
	"2" : "..---",
	"3" : "...--",
	"4" : "....-",
	"5" : ".....",
	"6" : "-....",
	"7" : "--...",
	"8" : "---..",
	"9" : "----.",
	"0" : "-----",
	"" : ""
        }

invMorseAlphabet = {v: k for k, v in morseAlphabet.items()}

def morseToLatin(morseletter):
	#global invMorseAlphabet
	return invMorseAlphabet[morseletter]

def translateMorseString(string):
	letter = ""
	returnstr = ""
	for i in range(0, len(string)):
		if(string[i]!= " "):
			letter += string[i]
		else:
			returnstr += morseToLatin(letter)
			letter =""
	return returnstr



