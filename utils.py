'''
Universidad del Valle de Guatemala
Redes - CC3067
Proyecto 2

Integrantes:
- Luis Quezada 18028
- Jennifer Sandoval 18962
- Esteban del Valle 18221
'''
# Function that allows cards to be displayed graphically
def showCards(listOfCards):
    cont = 0
    x = ""
    for i in listOfCards:
        if (i[-1] == "C"):
            suit = "\u2663"
            
        elif (i[-1] == "S"):
            suit = "\u2660"

        elif (i[-1] == "H"):
            suit = "\u2665"

        elif (i[-1] == "D"):
            suit = "\u2666"

        x = x + "|"+(i[:-1]) + suit + "|"
        cont += 1

    print("- "*((2*cont)+1))
    print(x)
    print("- "*((2*cont)+1))
    
#Function that allows verifying that an entered value is a whole number
def isNumber(text):
    isNum=False
    while isNum==False:
        value=input(text)
        isNum=value.isnumeric()
        if (isNum==False):
            print ('<!> You must enter an int number ')
        else:
            value=int(value)
    return value


