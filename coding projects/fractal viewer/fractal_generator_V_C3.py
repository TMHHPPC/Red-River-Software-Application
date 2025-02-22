#Import necessary libraries
import sys
from PIL import Image, ImageTk
from math import log, floor, sin, pi, e, ceil
from tkinter import Canvas, Tk, END, Entry, Button
import tkinter as tk
from ast import literal_eval
from numbers import Number

#imports the cython part of the code
from cy_fractal_static import colour_scheme, iterate


# control variables:
zoom = 1  # controls how deep the zoom into the set is, 1 is normal size,
# 1000000000000000 zoom is around the area where floating point errors occur
maximum_generation = 1000  # controls the maximum iteration count
real_coordinate = -0.6  # the real (x-axis) coordinate of the current centre of screen
imaginary_coordinate = 0.0  # the imaginary (y-axis) coordinate of the current centre of screen
quality = 1  # the resolution of the image, lower is better
colour_sensitivity = log(pi,e)  # controls how sensitive the colour scheme is
# good settings for this are log(6,10), log(10, 4) and log(pi, e)
maximum_period = 100  # controls the maximum period the periodicity checker can check for,
#currently unused as I haven't implemented the periodicity checker in cython yet



#scaling setup
def scale(input):
    #scales coordinates based on the current scale factor
    global scale_factor
    scaled_output = input*scale_factor
    return scaled_output

def inverse_scale(input):
    #inversely scales coordinates based on the current scale factor
    global scale_factor
    scaled_output = input/scale_factor
    return scaled_output

#window setup
window = Tk()
screen_width = window.winfo_screenwidth()  # width of the screen
screen_height = window.winfo_screenheight()  # height of the screen
#determining which scale factor to use
if (screen_height/960) < (screen_width/1440):
    scale_factor = (screen_height/960)
else:
    scale_factor = (screen_width/1440)

window_width = scale(1200)
window_height = scale(800)
# positioning the window in the middle of the screen
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2) - (screen_height / 20)
canvas = Canvas(window,width=screen_width, height=screen_height, bg="#000000", highlightthickness=0)
canvas.pack()
window.title("Fractal Generator")
window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))
window.configure(bg="#000000")

# GUI setup
#setting up the object lists
shape_list = []
text_list = []
widget_list = []
#setting up the "null" image so the generating and resizing functions doesn't crash when there's no image present
#null image causes some undesirable visual effects while on screen, so I banish it to the shadow realm (far offscreen)
img = Image.new('RGB', (1, 1))
fractal_image = canvas.create_image((window_width+scale(100000)), (window_height+scale(100000)), image=ImageTk.PhotoImage(img))
img_scaled_list = 0
image_list = [[fractal_image, img, scale(100000), scale(100000)]]

x_offset = 0
y_offset = 0

#function for dynamically resizing the canvas
def canvas_resize(event):
    global canvas, scale_factor, screen_height, screen_width, image_list, shape_list, text_list, shape_list, old_image,\
        new_image, img_scaled_list, x_offset, y_offset
    window_new_height = event.height
    window_new_width = event.width
    if (window_new_height / 800) < (window_new_width / 1200):
        scale_factor = (window_new_height / 800)
    else:
        scale_factor = (window_new_width / 1200)
    x_offset = (window_new_width - scale(1200))/2
    y_offset = (window_new_height - scale(800))/2
    #resizes all the canvas shapes
    for i in shape_list:
        shape = i[0]
        shape_x1 = floor(scale(i[1])+x_offset)
        shape_y1 = floor(scale(i[2])+y_offset)
        shape_x2 = floor(scale(i[3])+x_offset)
        shape_y2 = floor(scale(i[4])+y_offset)
        canvas.coords(shape, shape_x1, shape_y1, shape_x2, shape_y2)
    #resizes all the canvas text
    for i in text_list:
        text  = i[0]
        text_font_size = i[1]
        text_x = i[2]
        text_y = i[3]
        text_x = floor(scale(text_x)+x_offset)
        text_y = floor(scale(text_y)+y_offset)
        text_font = canvas.itemcget(text, "font").split(" ")
        text_font[1] = floor(scale(text_font_size))
        if text_font[1] == 0:
            text_font[1] = 1
        text_font = tuple(text_font)
        canvas.itemconfigure(text, font=text_font)
        canvas.coords(text, text_x, text_y)
    #resizes all the widgets (buttons, fields ect)
    for i in widget_list:
        widget = i[0]
        widget_font_size = i[1]
        widget_x = i[2]
        widget_y = i[3]
        widget_font = widget["font"].split(" ")
        widget_font[1] = floor(scale(widget_font_size))
        if widget_font[1] == 0:
            widget_font[1] = 1
        widget_font = tuple(widget_font)
        widget_x = floor(scale(widget_x)+x_offset)
        widget_y = floor(scale(widget_y)+y_offset)
        widget.place_configure(x=widget_x, y=widget_y, anchor="nw")
        widget["font"] = widget_font
    #resizes all the images, currently this only works with one image due to img_scaled_list and old_image not being a list
    #it was painful enough getting one image to be dynamically resizable, I don't want to try expanding it for now
    for i in image_list:
            object = i[0]
            #have to keep a constant reference to the original image otherwise python's garbage collection deletes
            #its reference from RAM, causing all the images based on that image to stop working
            old_image = i[1]
            new_image = old_image.resize((floor(scale(1000)), floor(scale(800))), Image.Resampling.LANCZOS)
            new_object_image = ImageTk.PhotoImage(new_image)
            image_x = i[2]
            image_y= i[3]
            image_x = floor(scale(image_x)+x_offset)
            image_y = floor(scale(image_y)+y_offset)
            canvas.itemconfigure(object, image=new_object_image)
            canvas.coords(object, image_x, image_y)
            img_scaled = new_object_image

    window.update()


images=[]
def create_rectangle(x,y,a,b,**options):
    # adds transparency as an option since tkinter doesn't have it for some reason
   global outline, outline_fill
   if 'alpha' in options:
      # Calculate the alpha transparency for every color(RGB)
      alpha = int(options.pop('alpha') * 255)
      # Use the fill variable to fill the shape with transparent color
      fill = options.pop('fill')
      fill = window.winfo_rgb(fill) + (alpha,)
      transimage = Image.new('RGBA', (int(a-x), int(b-y)), fill)
      images.append(ImageTk.PhotoImage(transimage))
      outline_fill = canvas.create_image(x, y, image=images[-1], anchor='nw')
      outline = canvas.create_rectangle(x, y,a,b, **options)



#Building GUI
area = canvas.create_rectangle(0, 0, scale(1000), scale(800), fill="#888888")
shape_list.append([area, 0, 0, 1000, 800])

# writing onscreen variables + adding fields
def write_to_screen(x, y, text, font):
    #function that writes the text to screen and saves its values for the text list
    #the weird x and y value additions are because I originally used a different screen drawer (turtle), which uses a
    #different coordinate system and im too lazy to update them all individually
    global text_list
    font = tuple((font[0], floor(scale(font[1])), font[2]))
    text = canvas.create_text(scale(x+685), scale(-y+390), text=text, font=font, fill="#FFFFFF")
    text_list.append([text, font[1], (x+685), (-y+390)])

#writing info text to screen
write_to_screen(410, 370, "Fractal Generator", ("calibre", 15, "normal"))
write_to_screen(410, 350, "By Thomas H", ("calibre", 12, "normal"))
write_to_screen(410, 300, "Real Coordinate: ", ("calibre", 10, "normal"))
write_to_screen(410, 240, "Imaginary Coordinate: ", ("calibre", 10, "normal"))
write_to_screen(410, 180, "Zoom: ", ("calibre", 10, "normal"))
write_to_screen(410, 120, "Maximum Generation: ", ("calibre", 10, "normal"))
write_to_screen(410, 60, "Quality: ", ("calibre", 10, "normal"))
write_to_screen(410, 40, str(quality), ("calibre", 10, "normal"))
write_to_screen(410, -370, "Version: ", ("calibre", 10, "normal"))
write_to_screen(410, -390, "Cython Rendering 3 (5/1/25)", ("calibre", 10, "normal"))

#setting up the variables for the fields
real_coordinate_field_variable = tk.StringVar()
imaginary_coordinate_field_variable = tk.StringVar()
zoom_field_variable = tk.StringVar()
maximum_generation_field_variable = tk.StringVar()
quality_field_variable = tk.StringVar()

#setting up real coordinate field
real_coordinate_field = Entry(canvas, textvariable=real_coordinate_field_variable, width=25,
                              font=('calibre', 10, 'normal'), bg="#888888", )
real_coordinate_field.insert(0, str(real_coordinate))
real_coordinate_field.place(x=scale(1007), y=scale(100))
widget_list.append([real_coordinate_field, 10,1007, 100])

#setting up imaginary coordinate field
imaginary_coordinate_field = Entry(canvas, textvariable=imaginary_coordinate_field_variable, width=25,
                                   font=('calibre', 10, 'normal'), bg="#888888")
imaginary_coordinate_field.insert(0, str(imaginary_coordinate))
imaginary_coordinate_field.place(x=scale(1007), y=scale(160))
widget_list.append([imaginary_coordinate_field, 10,1007, 160])

#setting up zoom field
zoom_field = Entry(canvas, textvariable=zoom_field_variable, width=25, font=('calibre', 10, 'normal'), bg="#888888")
zoom_field.insert(0, str(zoom))
zoom_field.place(x=scale(1007), y=scale(220))
widget_list.append([zoom_field, 10, 1007, 220])

#setting up maximum generation field
maximum_generation_field = Entry(canvas, textvariable=maximum_generation_field_variable, width=25,
                                 font=('calibre', 10, 'normal'), bg="#888888")
maximum_generation_field.insert(0, str(maximum_generation))
maximum_generation_field.place(x=scale(1007), y=scale(280))
widget_list.append([maximum_generation_field, 10, 1007, 280])

#setting up quality field
quality_field = Entry(canvas, textvariable=quality_field_variable, width=25, font=('calibre', 10, 'normal'),
                      bg="#888888")
quality_field.insert(0, str(quality))
quality_field.place(x=scale(1007), y=scale(340))
widget_list.append([quality_field, 10, 1007, 340])

#setting up percent text
percent_text= canvas.create_text(scale(400), scale(400), text="", font=("calibre", 30))
text_list.append([percent_text, 30, 500, 370])

#setting up generate button
generation_button = Button(canvas, text='Generate', command=lambda: generate(), width=13, height=1, bg="#888888",
                           font=("calibre", 10, "normal"))
generation_button.place(x=1007, y=400)
widget_list.append([generation_button, 10, 1007, 400])

#setting up reset button
resetting_button = Button(canvas, text='Reset', command=lambda: reset(), width=13, height=1, bg="#888888",
                          font=("calibre", 10, "normal"))
resetting_button.place(x=1007, y=440)
widget_list.append([resetting_button, 10, 1007, 440])

#setting up stop button
stop_button = Button(canvas, text='Stop', command=lambda: stop(), width=13, height=1, bg="#888888",
                     font=("calibre", 10, "normal"))
stop_button.place(x=1007, y=480)
widget_list.append([stop_button, 10, 1007, 480])

#setting up exit button
exit_button = Button(canvas, text='Exit', command=lambda: exit(), width=13, height=1, bg="#888888",
                     font=("calibre", 10, "normal"))
exit_button.place(x=1007, y=640)
widget_list.append([exit_button, 10, 1007, 640])


#other variables
interrupt = False #determines if an interrupt has been called
generating = True #determines if generating is currently in progress
first_time = True #determines if this is the first time the program has run




def draw(quality, zoom, real_coordinate, imaginary_coordinate, maximum_generation):
    global interrupt, percent_text, colour_sensitivity
    #setting up the matrix for the image data
    img_data = [[0 for j in range(800)] for i in range(1000)]
    #calculating the quality offset needed to find the midpoint of every section
    midpoint_offset = (quality)/2
    if quality == 1:
        midpoint_offset = 0
    for x in range(ceil(len(img_data)/quality)):
        x_pos = (int(x)*quality)
        x = img_data[x]
        percent = str("%.2f %%" % (x_pos / (window_width - 200) * 100.0))
        canvas.itemconfigure(percent_text, text=percent)
        window.update()

        if interrupt == True:
            break

        for y in range(ceil(len(x)/quality)):
            y_pos=(int(y)*quality)
            y = x[y]
            #converting the x and y coordinates into complex values for the set
            x_value = ((x_pos+midpoint_offset-500)/(zoom * 300)) + real_coordinate
            y_value = ((y_pos+midpoint_offset-400)/(zoom * 300))+ imaginary_coordinate
            if y_value == 0:  # converting i=0 to a small non-zero value to remove the black line that shows up at i=0
                # as it is meant to be infinitely small
                y_value = 0.1 / (zoom * 300)
            #passes the x and y values to the iterate function to return the colour at that point
            colour = iterate(x_value,y_value, maximum_generation, colour_sensitivity)
            x_iteration = 0
            while x_iteration < quality:
                if x_pos + x_iteration >= 1000:
                    break
                y_iteration = 0
                while y_iteration < quality:
                    if y_pos + y_iteration >= 800:
                        break
                    if interrupt == True:
                        #if an interrupt is called, exit
                        break
                    img_data[(x_pos+x_iteration)][(y_pos+y_iteration)] = colour
                    y_iteration +=1
                x_iteration += 1
            if interrupt == True:
                break
    return img_data

def check_if_integer(value):
    # function for checking the input is an integer
    if value == "":
        return False
    else:
        try:
            return isinstance(literal_eval(value), Number)
        except ValueError:
            return False


def generate(event=None):
    #sets up the program to generate the image and then displays the generated image once it's finished
    global image, canvas, real_coordinate_field_variable, imaginary_coordinate_field_variable, zoom_field_variable, \
        quality_field_variable, maximum_generation_field_variable, real_coordinate, imaginary_coordinate, zoom, \
        quality, maximum_generation, interrupt, generating, first_time, img, img_scaled_list, fractal_image
    #the sheer number of global variables here probably constitutes some kind of war crime but i'm too lazy to
    #reformat all of this code in object-oriented

    generating = True
    stop_button.config(bg="#888888", fg="#000000", relief="raised")
    stop_button["state"] = "normal"
    generation_button["state"] = "disabled"
    generation_button.config(bg="#444444", fg="#000000", relief="sunken")
    resetting_button["state"] = "disabled"
    resetting_button.config(bg="#444444", fg="#000000", relief="sunken")
    interrupt = False
    if first_time == False:
        image.__del__()
        canvas.delete(fractal_image)
    #checking field content to make sure the content is a number + loading fields into variables
    if check_if_integer(real_coordinate_field_variable.get()) == False:
        real_coordinate = real_coordinate
        real_coordinate_field.delete(0, END)
        real_coordinate_field.insert(0, str(real_coordinate))
    else:
        real_coordinate = float(real_coordinate_field_variable.get())

    if check_if_integer(imaginary_coordinate_field_variable.get()) == False:
        imaginary_coordinate = imaginary_coordinate
        imaginary_coordinate_field.delete(0, END)
        imaginary_coordinate_field.insert(0, str(imaginary_coordinate))
    else:
        imaginary_coordinate = float(imaginary_coordinate_field_variable.get())

    if check_if_integer(zoom_field_variable.get()) == False:
        zoom = zoom
        zoom_field.delete(0, END)
        zoom_field.insert(0, str(zoom))
    else:
        zoom = float(zoom_field_variable.get())
    if check_if_integer(maximum_generation_field_variable.get()) == False:
        maximum_generation = maximum_generation
        maximum_generation_field.delete(0, END)
        maximum_generation_field.insert(0, str(maximum_generation))
    else:
        maximum_generation = int(maximum_generation_field_variable.get())

    if check_if_integer(quality_field_variable.get()) == False:
        quality = quality
        quality_field.delete(0, END)
        quality_field.insert(0, str(quality))
    else:
        if floor(float(quality_field_variable.get())) < 1:
            quality = quality
            quality_field.delete(0, END)
            quality_field.insert(0, str(quality))
        else:
            quality = floor(float(quality_field_variable.get()))
            quality_field.delete(0, END)
            quality_field.insert(0, str(quality))



    img_data = draw(quality, zoom, real_coordinate, imaginary_coordinate, maximum_generation)
    # putting PIL image on tkinter screen
    img = Image.new('RGB', (1000, 800))
    pixels = img.load()
    x_pos = 0
    y_pos = 0
    for x in img_data:
        for y in x:
            pixels[x_pos, y_pos] = img_data[x_pos][y_pos]
            y_pos += 1
        y_pos = 0
        x_pos += 1
    img_scaled = img.resize((floor(1000*scale_factor), floor(800*scale_factor)), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(img_scaled)
    if interrupt == True:
        image.__del__()
        return
    fractal_image = canvas.create_image(floor(scale(500)+x_offset), floor(scale(400)+y_offset), image=image)
    image_list[0] = ([fractal_image, img, 500, 400])
    generating = False
    generation_button.config(bg="#888888", relief="raised")
    generation_button["state"] = "normal"
    resetting_button.config(bg="#888888", relief="raised")
    resetting_button["state"] = "normal"
    stop_button.config(bg="#444444", fg="#000000", relief="sunken")
    stop_button["state"] = "disabled"
    window.update()
    if first_time == True:
        first_time = False

def stop():
    #calls an interrupt and resets button states
    global interrupt, generating
    interrupt = True
    generating = False
    generation_button.config(bg="#888888")
    generation_button["state"] = "normal"
    resetting_button.config(bg="#888888")
    resetting_button["state"] = "normal"

def reset():
    #resets all field values and regenerates the image
    global real_coordinate, imaginary_coordinate, zoom, quality, maximum_generation
    #resetting all variables back to their original states
    real_coordinate_field.delete(0, END)
    real_coordinate_field.insert(0, str(-0.6))
    imaginary_coordinate_field.delete(0, END)
    imaginary_coordinate_field.insert(0, str(0.0))
    zoom_field.delete(0, END)
    zoom_field.insert(0, str(1))
    maximum_generation_field.delete(0, END)
    maximum_generation_field.insert(0, str(1000))
    quality_field.delete(0, END)
    quality_field.insert(0, str(1))
    generate()

#creating variables for the mouse area selector
# x and y values for when the mouse is clicked
x_mouse_down_value = 0
y_mouse_down_value = 0
# x and y values for when the mouse is released
x_mouse_up_value = 0
y_mouse_up_value = 0
#current mouse position
mouse_x_position = 0
mouse_y_position = 0
mouse_is_down = False
create_rectangle(1, 1,1,1, fill= "#000000", alpha=0.1)

#checking if the mouse has been clicked
def mouse_down(event):
    global x_mouse_down_value, y_mouse_down_value, mouse_is_down, generating, interrupt
    if event.x > scale(1000):
        return
    x_mouse_down_value = event.x
    y_mouse_down_value = event.y
    if generating == True:
        mouse_is_down = False
    if generating == False and interrupt == False:
        mouse_is_down = True


# updates the outline box while the mouse is held down
def draw_outline_box(event):
    global x_mouse_down_value, y_mouse_down_value, mouse_is_down, outline, generating, outline_fill
    mouse_x_position, mouse_y_position = canvas.canvasx(event.x), canvas.canvasy(event.y)
    if generating == True:
        mouse_is_down = False
    if interrupt == True:
        mouse_is_down = False
    if mouse_x_position >= scale(1000) or mouse_x_position <= scale(0) or mouse_y_position >= scale(800) or mouse_y_position <= scale(0):
        mouse_is_down = False
        canvas.delete(outline)  # deleting old outline box
        canvas.delete(outline_fill)
        return
    if mouse_is_down == True:
        canvas.delete(outline)
        canvas.delete(outline_fill)
        x_coordinate = x_mouse_down_value
        y_coordinate = y_mouse_down_value
        if mouse_x_position < x_coordinate:  # switching around the x and y values if needed cause otherwise it doesnt work
            temp_x_position = x_coordinate
            x_coordinate = mouse_x_position
            mouse_x_position = temp_x_position
        if mouse_y_position < y_coordinate:
            temp_y_position = y_coordinate
            y_coordinate = mouse_y_position
            mouse_y_position = temp_y_position
        create_rectangle(x_coordinate, y_coordinate, mouse_x_position, mouse_y_position, width=scale(2), outline="#888888",
                         fill="#888888", alpha=0.4)



def mouse_up(event):
    # deletes outline box, changes real_coordinate, imaginary_coordinate and zoom based on values determined by the box
    # and reloads the set
    global x_mouse_up_value, y_mouse_up_value, x_mouse_down_value, y_mouse_down_value, zoom, real_coordinate, \
        imaginary_coordinate, mouse_is_down, outline, outline_fill
    if mouse_is_down == False:
        return
    mouse_is_down = False

    if event.x > scale(1000):
        return

    canvas.delete(outline)
    canvas.delete(outline_fill)
    x_mouse_up_value = event.x
    y_mouse_up_value = event.y
    if x_mouse_down_value == x_mouse_up_value and y_mouse_down_value == y_mouse_up_value:
        mouse_is_down = False
        return
    if x_mouse_down_value == x_mouse_up_value:
        x_mouse_up_value += 1
    if y_mouse_down_value == y_mouse_up_value:
        y_mouse_up_value += 1
    # calculating real and imaginary coordinates
    y_mouse_down_value = inverse_scale(y_mouse_down_value)
    x_mouse_down_value = inverse_scale(x_mouse_down_value)
    y_mouse_up_value = inverse_scale(y_mouse_up_value)
    x_mouse_up_value = inverse_scale(x_mouse_up_value)
    x_outline_midpoint = ((x_mouse_down_value + x_mouse_up_value) / 2)
    y_outline_midpoint = ((y_mouse_down_value + y_mouse_up_value) / 2)
    real_coordinate = ((x_outline_midpoint - 500) / (zoom * 300)) + real_coordinate
    imaginary_coordinate = ((y_outline_midpoint - 400) / (zoom * 300)) + imaginary_coordinate
    # calculating zoom
    x_zoom_multiple = abs(1000 / (x_mouse_down_value - x_mouse_up_value))
    y_zoom_multiple = abs(800 / (y_mouse_down_value - y_mouse_up_value))
    # maintaining aspect ratio of the image
    if x_zoom_multiple < y_zoom_multiple:
        zoom = (y_zoom_multiple * zoom)

    if x_zoom_multiple > y_zoom_multiple:
        zoom = (x_zoom_multiple * zoom)
    zoom = round(zoom, 3-int(log(zoom, 10))) #keeps the numbers simpler by rounding it to 4 significant figures
    real_coordinate_field.delete(0, END)
    real_coordinate_field.insert(0, str(real_coordinate))
    imaginary_coordinate_field.delete(0, END)
    imaginary_coordinate_field.insert(0, str(imaginary_coordinate))
    zoom_field.delete(0, END)
    zoom_field.insert(0, str(zoom))
    generate()

def cancel(event=None):
    #cancels the box being drawn by the mouse
    global mouse_is_down
    mouse_is_down = False
    canvas.delete(outline)
    canvas.delete(outline_fill)


def exit():
    #shuts down the program
    stop()
    window.quit()
    sys.exit()


#binding the box commands to the mouse
canvas.bind("<Configure>", canvas_resize)
window.bind("<Motion>", draw_outline_box)
window.bind("<Button-1>", mouse_down)
window.bind("<ButtonRelease>", mouse_up)
window.bind('<Escape>', cancel)







window.update()
generate()
window.mainloop()

