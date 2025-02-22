#the following code is one of my parts of a project I am currently working on with a friend
#the aim of the project is to develop an online chat client, through which we can send and receive messages



from tkinter import *
from time import *
from math import floor


username = "User"
background_colour = "#000000"
foreground_colour = "#000000"
border_colour = "#FFFFFF"
text_colour = "#FFFFFF"
username_colour = "#0066AA"

#framerate and scroll speed
scroll_speed = 500
framerate = 500



#window setup -T
window_width = 800
window_height = 800
window = Tk()
screen_width = window.winfo_screenwidth()  # width of the screen
screen_height = window.winfo_screenheight() # height of the screen
# positioning the window in the middle of the screen
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2) - (screen_height / 20)
canvas = Canvas(window, width=window_width, height=window_height, bg=background_colour)
canvas.pack()
window.title("Chat thingy")
window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))
window.lift()

#setting up the text field -T
text = StringVar()
text_field_border = Frame(window, highlightbackground=border_colour,
                                    highlightthickness=2, bd=0, background=border_colour)
text_field = Text(text_field_border, width=60, height=2, font=('calibre', 13, 'normal'), fg=text_colour,
                  bg=foreground_colour, borderwidth=0, insertbackground=text_colour)
text_field.pack()
text_field_border.place_configure(anchor='center')
text_field_border.place(x=310, y=750)

#setting up the start button -T
start_button_border = Frame(window, highlightbackground=border_colour,
                                    highlightthickness=2, bd=0)
start_button = Button(start_button_border, text='Send',command=lambda: send(),width=15, height=1, fg="#FFFFFF",
                              font=('Bold', 15, 'normal'), bg="#000000", relief="flat")
start_button.pack()
start_button_border.place(x=670, y=750, anchor="center")

message_matrix = [["Thomas", "(test data)", "The quick brown fox jumped over the lazy dog"]]
message_object_list = [[0, 0, 0]]

scroll_offset= 0
maximum_scroll_offset = 0

def load():
    global message_matrix, message_object_list, scroll_offset, maximum_scroll_offset
    #deleting all the previous message objects every time this is called-T
    for i in message_object_list:
        canvas.delete(i)
    message_object_list = []
    message_count = len(message_matrix)
    offset = 0
    for i in range(message_count):
        #splitting the matrix data into its 3 components-T
        message_data = message_matrix[message_count-i-1]
        message_author = str(message_data[0])
        message_date = str(message_data[1])
        message_contents = str(message_data[2])

        #calculating the height of the messages
        #and the offsets of the start and end of the messages -T
        message_start_pos = 700 - offset + scroll_offset
        if message_start_pos < 0:
            break
        message_height = (message_contents.count("\n")+1)*19
        offset += message_height
        message_end_pos = 700-offset + scroll_offset


        #only render the text if it can be seen on screen, to increase speed -T
        if (0 < message_end_pos < 700) or (700 > message_start_pos > 0) or (message_end_pos < 350 < message_start_pos):
            #placing the message contents on screen-T
            message_contents_text = canvas.create_text(40,message_end_pos, text=message_contents, font=('calibre', 13, 'normal'), fill=text_colour, anchor="nw")
            message_object_list.append(message_contents_text)

        message_start_pos = message_end_pos
        offset += 20
        y_position = 700 - offset + scroll_offset
        message_end_pos = y_position

        #only render the text if it can be seen on screen, to increase speed -T
        if (20 <= message_end_pos <= 720) or (720 >= message_start_pos >= -20) or (message_end_pos <= 350 <= message_start_pos):
            #placing the message author on screen-T
            message_author_text = canvas.create_text(40, y_position, text=message_author,
                                                       font=('calibre', 13, 'normal'), fill=username_colour, anchor="nw")
            message_object_list.append(message_author_text)
            #calculating the X position of the timestamp-T
            date_x_pos = 35+(11*len(message_author))
            #placing the timestamp on screen-T
            message_date_text = canvas.create_text(date_x_pos, y_position, text=message_date,
                                                       font=('calibre', 13, 'normal'), fill=text_colour, anchor="nw")
            message_object_list.append(message_date_text)

        offset += 20

    maximum_scroll_offset = offset - 700
    if maximum_scroll_offset < 0:
        maximum_scroll_offset = 0
    window.update()

def format(string):
    # we now need to format the message, a basic, naive way to do this would be to delete all
    # user generated linebreaks (\n) and put our own linebreaks with no regard to anything but
    # the basic index position of the linebreaks. However, I wanted to make it so that it
    # respects user generated linebreaks and is able to change the position the linebreaks are in
    # so that it doesn't do weird things like put a linebreak in the middle of a word -T
    formatted_string = ""
    # formatting the message contents
    # message might have some user-inserted line breaks so we first split the message by them -T
    string_contents_list = string.split('\n')
    # we then search through each section of the message, if a section is wider than 70 characters,
    # we insert line breaks so it doesn't go offscreen -T
    for i in string_contents_list:
        # setting up the indexes
        new_index = -1
        index = 0
        # adding the new linebreaks
        while index <= len(i) - 1:
            # finding the next default index position -T
            index = new_index + 70
            new_index = index
            # just to make sure the index doesn't exceed the length of the string -T
            if index >= len(i) - 1:
                break
            # inserting the line breaks
            # we start by checking the default index position for the linebreak
            # if the linebreak occurs on a space by default, nothing changes-T
            if i[index] == " ":
                i = i[:index] + "\n" + i[(index + 1):]
            # if the linebreak doesn't occur on a space by default,
            # the code searches for the nearest space to the left of the default position-T
            elif i[index] != " ":
                new_index = index
                while i[new_index] != " ":
                    new_index -= 1
                    # if there is no space close to the default position,
                    # the code gives up and inserts the linebreak in the default position-T
                    if new_index <= (index - 70):
                        break
                if new_index <= (index - 70):
                    i = i[:index] + "\n" + i[index:]
                    new_index = index
                # if a space near the default position has been found,
                # the code inserts the linebreak there instead-T
                else:
                    i = i[:new_index] + "\n" + i[(new_index + 1):]

        # rebuilding the now formatted message-T
        if formatted_string == "":
            formatted_string = i
        else:
            formatted_string = formatted_string + "\n" + i

    # deleting any extra linebreaks at the end
    # there shouldn't be any, but better safe than sorry -T
    while formatted_string[-1:] == "\n":
        formatted_string = formatted_string[:-1]
    # updating offset based on the height of the message-T
    return formatted_string

def send():
    global text_field, message_matrix
    #fetches the message from the message field
    message = text_field.get(1.0, END)
    text_field.delete(1.0, END)
    message = message.replace("\n", "")
    #checks to make sure you're just not sending an empty message -T
    if message != "":
        #checks to ensure there are no breaks at the end of the line -T
        while message[-1:] == "\n":
            message = message[:-1]

        #creating the timestamp
        timestamp = "(" + strftime("%d %b %Y, %H:%M:%S GMT", gmtime()) + ")"

        #put the code for server communication somewhere here -T

        #appends the new message to the matrix -T
        message = format(message)
        message_matrix.append([username, timestamp, message])
        #if the message count is over 500, delete the oldest message in the list
        if len(message_matrix) > 500:
            del message_matrix[0]
        load()

def receive():
    #put the code for server communication here, the communication
    #should be in a format that gives the username, timestamp and actual message content

    #appends the new message to the matrix -T
    timestamp = ""
    message = ""
    message = format(message)
    message_matrix.append([username, timestamp, message])
    #if the message count is over 500, delete the oldest message in the list
    if len(message_matrix) > 500:
        del message_matrix[0]
    load()

shift_down = False
def on_shift_press(event=None):
    global shift_down
    shift_down = True

def on_shift_release(event=None):
    global shift_down
    shift_down = False

def on_enter(event=None):
    global shift_down
    #if shift isn't held down, the message is sent -T
    if shift_down == False:
        send()
        #stops the default function of the enter key (creating a new line)
        #from activating -T
        return 'break'


#once again the basic and naive way to do this would be to use a normal while loop to move it,
#However this produces inconsistent speeds as the time it takes for one cycle of the loop to
#complete will change drastically, as such I implemented a framerate system to keep the speed
#consistent. is this probably way too overcomplicated and unnecessary? yes, but it's cool -T
down_key_held_down = False
up_key_held_down = False

def on_down_key_down(event=None):
    global down_key_held_down, scroll_offset, maximum_scroll_offset, framerate, scroll_speed
    #this stops windows auto-keys from activating the loop multiple times, which would lead
    #to a stack overflow
    if down_key_held_down == False:
        #calculate how long an ideal frame will last
        target_time = 1 / framerate
        #use that to calculate a rough estimate for the time the first frame will take to complete
        frame_time = target_time
        down_key_held_down = True
        while down_key_held_down == True:
            #start timing the frame
            frame_start = time()
            if scroll_offset >= 0:
                #use the estimated frame time to calculate the distance to move
                frame_movement = -1*(scroll_speed*frame_time)
                scroll_offset += frame_movement
                load()
            window.update()
            frame_end = time()
            #if the calculations finish before the frame should, this just eats up time
            #until it's time for the next frame
            while frame_end - frame_start < target_time:
                frame_end = time()
            #use the time this frame took to complete as an estimate for how long the next
            #frame will take to complete
            frame_time = frame_end-frame_start

def on_down_key_up(event=None):
    global  down_key_held_down
    down_key_held_down = False


def on_up_key_down(event=None):
    global up_key_held_down, scroll_offset, maximum_scroll_offset, framerate, scroll_speed
    # this stops windows auto-keys from activating the loop multiple times, which would lead
    # to a stack overflow
    if up_key_held_down == False:
        target_time = 1 / framerate
        # use that to calculate a rough estimate for the time the first frame will take to complete
        frame_time = target_time
        up_key_held_down = True
        while up_key_held_down == True:
            #start timing the frame
            frame_start = time()
            if scroll_offset < maximum_scroll_offset:
                #use the estimated frame time to calculate the distance to move
                frame_movement = (scroll_speed * frame_time)
                scroll_offset += frame_movement
                load()
            window.update()
            frame_end = time()
            #if the calculations finish before the frame should, this just eats up time
            #until it's time for the next frame
            while frame_end - frame_start < target_time:
                frame_end = time()
            #use the time this frame took to complete as an estimate for how long the next
            #frame will take to complete
            frame_time = frame_end - frame_start

def on_up_key_up(event=None):
    global  up_key_held_down
    up_key_held_down = False


#binding all the key commands to their respective keys
text_field.bind("<Shift_L>", on_shift_press)
text_field.bind("<Shift-KeyRelease>", on_shift_release)
text_field.bind('<Return>', on_enter)
window.bind('<Up>', on_up_key_down)
window.bind('<KeyRelease-Up>', on_up_key_up)
window.bind('<Down>', on_down_key_down)
window.bind('<KeyRelease-Down>', on_down_key_up)

#loading test data
for i in message_matrix:
    i[2] = format(i[2])

load()
window.mainloop()