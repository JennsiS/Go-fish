def show_hand(hand):
    cont = 0
    x = ""
    for i in hand:
        if (i[-1] == "C"):
            palo = "\u2663"
            
        elif (i[-1] == "S"):
            palo = "\u2660"

        elif (i[-1] == "H"):
            palo = "\u2665"

        elif (i[-1] == "D"):
            palo = "\u2666"

        x = x + "|"+(i[:-1]) + palo + "|"
        cont += 1

    print("- "*((2*cont)+2))
    print(x)
    print("- "*((2*cont)+2))


