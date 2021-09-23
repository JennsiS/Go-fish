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
def showCards(cards):
    cont = 0
    x = ""
    for i in cards:
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
    
# Function that allows verifying that an entered value is a whole number
def isNumber(text):
    isNum = False
    while isNum == False:
        value = input(text)
        isNum = value.isnumeric()
        if (isNum == False):
            print ('<!> You must enter an int number ')
        else:
            value = int(value)
    return value


# Function that shows the ocean graphically
# if pos is none all cards are upside down
# if pos is a position in the ocean it will reveal that card
# Otherwise error message is shwon
def showOcean(ocean,pos):
    x = ""
    y = ""
    cont = 0
    if(pos == None):
        for i in range (1, len(ocean)+1):
            x = x+" - -"
            y = y +"|"+ str(i) +"| "
            cont +=1

            if (cont == 6):
                print(x)
                print(y)
                cont = 0
                x = ""
                y = ""
        print(x)
        print(y)
        return True
            
    elif(0 < pos <= len(ocean)):
        for i in range (1, len(ocean)+1):
            if(i == pos):
                palo = ""
                if (ocean[i-1][-1] == "C"):
                    palo = "\u2663"
            
                elif (ocean[i-1][-1] == "S"):
                    palo = "\u2660"

                elif (ocean[i-1][-1] == "H"):
                    palo = "\u2665"

                elif (ocean[i-1][-1] == "D"):
                    palo = "\u2666"
                card = ocean[i-1][:-1]+palo
                x = x+" - -"
                y = y +"|"+ card +"| "
                cont +=1

            else:
                x = x+" - -"
                y = y +"|"+ str(i) +"| "
                cont +=1

            if (cont == 6):
                print(x)
                print(y)
                cont = 0
                x = ""
                y = ""
        print(x)
        print(y)
        return True

    else:
        return False

