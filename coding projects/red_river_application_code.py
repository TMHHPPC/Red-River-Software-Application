DATA = ("100 200 300\n400 250\n100\n600 700 900\n300")

def get_highest_order(data):
    highest_total = 0
    #spliting the string along the linebreaks, turning each order into its own string in a list
    data = data.split("\n")
    #for each order
    for i in data:
        #get each individual value by splitting each order along the spaces
        values = i.split(" ")
        #add all the costs together to get the total value for that order
        total = 0
        for value in values:
            total += int(value)
        #check if the total value for that order is the highest so far
        #if so, set it to the highest value order so far
        if total > highest_total:
            highest_total = total

    return highest_total



print(get_highest_order(DATA))