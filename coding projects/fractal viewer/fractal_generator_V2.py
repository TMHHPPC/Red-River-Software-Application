#Import necessary libraries
import sys
from PIL import Image, ImageTk
from math import log, floor, sin, pi, e, ceil
from tkinter import Canvas, Tk, Text, END, Entry, Button
import tkinter as tk
from ast import literal_eval
from numbers import Number

# control variables:
zoom = 1  # controls how deep the zoom into the set is, 1 is normal size,
# 1000000000000000 zoom is around the area where floating point errors occur
maximum_generation = 1000  # controls the maximum iteration count
real_coordinate = -0.6  # the real (x-axis) coordinate of the current centre of screen
imaginary_coordinate = 0.0  # the imaginary (y-axis) coordinate of the current centre of screen
quality = 1  # the resolution of the image, lower is better
colour_sensitivity = log(6, 10)  # controls how sensitive the colour scheme is
# good settings for this are log(3,10) and log(10, 4)
maximum_period = 100  # controls the maximum period the period checker can check for

#other variables
interrupt = False
generating = True
first_time = True
# window setup
window_width = 1200
window_height = 800
window = Tk()
screen_width = window.winfo_screenwidth()  # width of the screen
screen_height = window.winfo_screenheight()  # height of the screen
# positioning the window in the middle of the screen
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2) - (screen_height / 20)
canvas = Canvas(window, width=window_width, height=window_height, bg="#888888")
canvas.pack()
window.title("Fractal Generator")
window.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

real_coordinate_field_variable = tk.StringVar()
imaginary_coordinate_field_variable = tk.StringVar()
zoom_field_variable = tk.StringVar()
maximum_generation_field_variable = tk.StringVar()
quality_field_variable = tk.StringVar()
# GUI setup
#adding transparency as an option since tkinter doesn't have it for some dumb reason
images=[]
def create_rectangle(x,y,a,b,**options):
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
# turtle setup



# building GUI + writing onscreen variables
textlist = []
def write_to_screen(x, y, text, font):
    text = canvas.create_text(x+685, -y+390, text=text, font=font, fill="#FFFFFF")
    textlist.append(text)




canvas.create_rectangle(1000, 0, 1200, 800, fill="#000000")
# writing onscreen variables + adding fields
write_to_screen(410, 370, "Fractal Generator", ("Verdana", 15, "normal"))
write_to_screen(410, 350, "By Thomas H", ("Verdana", 12, "normal"))
write_to_screen(410, 300, "Real Coordinate: ", ("Verdana", 10, "normal"))
real_coordinate_field = Entry(window, textvariable=real_coordinate_field_variable, width=25,
                              font=('calibre', 10, 'normal'), bg="#888888", )
real_coordinate_field.insert(0, str(real_coordinate))
real_coordinate_field.place(x=1007, y=100)
write_to_screen(410, 240, "Imaginary Coordinate: ", ("Verdana", 10, "normal"))
imaginary_coordinate_field = Entry(window, textvariable=imaginary_coordinate_field_variable, width=25,
                                   font=('calibre', 10, 'normal'), bg="#888888")
imaginary_coordinate_field.insert(0, str(imaginary_coordinate))
imaginary_coordinate_field.place(x=1007, y=160)
write_to_screen(410, 180, "Zoom: ", ("Verdana", 10, "normal"))
zoom_field = Entry(window, textvariable=zoom_field_variable, width=25, font=('calibre', 10, 'normal'), bg="#888888")
zoom_field.insert(0, str(zoom))
zoom_field.place(x=1007, y=220)
write_to_screen(410, 120, "Maximum Generation: ", ("Verdana", 10, "normal"))
maximum_generation_field = Entry(window, textvariable=maximum_generation_field_variable, width=25,
                                 font=('calibre', 10, 'normal'), bg="#888888")
maximum_generation_field.insert(0, str(maximum_generation))
maximum_generation_field.place(x=1007, y=280)
write_to_screen(410, 60, "Quality: ", ("Verdana", 10, "normal"))
write_to_screen(410, 40, str(quality), ("Verdana", 10, "normal"))
quality_field = Entry(window, textvariable=quality_field_variable, width=25, font=('calibre', 10, 'normal'),
                      bg="#888888")
quality_field.insert(0, str(quality))
quality_field.place(x=1007, y=340)
write_to_screen(410, -370, "Version: ", ("Verdana", 10, "normal"))
write_to_screen(410, -390, "V2 (26/09/24)", ("Verdana", 10, "normal"))


# colour scheme code
def colour_scheme(generation_number, z):
    # smooth colouring code
    smooth_colouring_value = log((log(((z.real ** 2) + (z.imag ** 2)), e) / 2) / log(2, e), e) / log(2, e)
    colour_value = (generation_number + 1 - smooth_colouring_value)
    if colour_value < 2:
        colour_value = 2
    # formulae for the colour scheme
    colour_value = log(colour_value, e) / colour_sensitivity  # logarithmic colouring + applying the colour sensitivity
    # calculations for rgb values
    r = int(170 * abs(sin(colour_value - (pi / 3))))
    g = int(170 * abs(sin(colour_value - (pi / 6))))
    b = int(170 * abs(sin(colour_value)))
    return r, g, b


# escape loop code
def iterate(x, y, maximum_generation):
    if y == 0:  # converting i=0 to a small non-zero value to remove the black line that shows up at i=0
        # as it is meant to be infinitely small
        y = 0.1 / (zoom * 300)
    c = complex(x, y)
    z = c
    global maximum_period
    for i in range(0, maximum_generation):
        if abs(z) > 256:
            return colour_scheme(i, z)  # sends any escaping value to the colour scheme
        z = (z*z)+c # actual formula for the set
    return 0, 0, 0  # returns black if value didn't escape


def draw(quality, zoom, real_coordinate, imaginary_coordinate, maximum_generation):
    # creating the new image in RGB mode
    global interrupt
    img = Image.new('RGB', (1000, 800))
    pixels = img.load()
    percent_text = Text(window, height=1, width=7, font=("Verdana", 30), bg="#888888", bd=0)
    percent_text.pack()
    percent_text.place(x=400, y=370)
    #calculating the quality offset needed to find the midpoint of every section
    midpoint_offset = (quality)/2
    if quality == 1:
        midpoint_offset = 0

    for x in range(ceil(img.size[0]/quality)):
        x = (int(x)*quality)
        percent = str("%.2f %%" % (x / (window_width - 200) * 100.0))
        percent_text.delete(1.0, END)
        percent_text.insert(tk.END, percent)
        window.update()

        if interrupt == True:
            break

        for y in range(ceil(img.size[1]/quality)):
            y=(int(y)*quality)
            #converting the x and y coordinates into complex values for the set
            x_value = ((x+midpoint_offset-500)/(zoom * 300)) + real_coordinate
            y_value = ((y+midpoint_offset-400)/(zoom * 300))+ imaginary_coordinate
            colour = iterate(x_value,y_value, maximum_generation)
            x_iteration = 0
            while x_iteration < quality:
                if x + x_iteration >= 1000:
                    break
                y_iteration = 0
                while y_iteration < quality:
                    if y + y_iteration >= 800:
                        break
                    if interrupt == True:
                        break
                    pixels[(x+x_iteration), (y+y_iteration)] = colour
                    y_iteration +=1
                x_iteration += 1
            if interrupt == True:
                break
    percent_text.destroy()
    #putting PIL image on tkinter screen
    image = ImageTk.PhotoImage(img)
    return image


def check(value):
    if value == "":
        return False
    else:
        try:
            return isinstance(literal_eval(value), Number)
        except ValueError:
            return False


def generate(event=None):
    global image, canvas, real_coordinate_field_variable, imaginary_coordinate_field_variable, zoom_field_variable, \
        quality_field_variable, maximum_generation_field_variable, real_coordinate, imaginary_coordinate, zoom, \
        quality, maximum_generation, interrupt, generating, first_time

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
    #checking field content to make sure the content is a number + loading fields into variables
    if check(real_coordinate_field_variable.get()) == False:
        real_coordinate = real_coordinate
        real_coordinate_field.delete(0, END)
        real_coordinate_field.insert(0, str(real_coordinate))
    else:
        real_coordinate = float(real_coordinate_field_variable.get())

    if check(imaginary_coordinate_field_variable.get()) == False:
        imaginary_coordinate = imaginary_coordinate
        imaginary_coordinate_field.delete(0, END)
        imaginary_coordinate_field.insert(0, str(imaginary_coordinate))
    else:
        imaginary_coordinate = float(imaginary_coordinate_field_variable.get())

    if check(zoom_field_variable.get()) == False:
        zoom = zoom
        zoom_field.delete(0, END)
        zoom_field.insert(0, str(zoom))
    else:
        zoom = float(zoom_field_variable.get())
    if check(maximum_generation_field_variable.get()) == False:
        maximum_generation = maximum_generation
        maximum_generation_field.delete(0, END)
        maximum_generation_field.insert(0, str(maximum_generation))
    else:
        maximum_generation = int(maximum_generation_field_variable.get())

    if check(quality_field_variable.get()) == False:
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



    image = draw(quality, zoom, real_coordinate, imaginary_coordinate, maximum_generation)
    if interrupt == True:
        image.__del__()
        return
    canvas.create_image((floor(500), floor(400)), image=image)
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
    global interrupt, generating
    interrupt = True
    generating = False
    generation_button.config(bg="#888888")
    generation_button["state"] = "normal"
    resetting_button.config(bg="#888888")
    resetting_button["state"] = "normal"

def reset():
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
    quality_field.insert(0, str(4))
    generate()

#creating variables for the mouse area selector
x_mouse_down_value = 0
y_mouse_down_value = 0
x_mouse_up_value = 0
y_mouse_up_value = 0
mouse_x_position = 0
mouse_y_position = 0
mouse_is_down = False
create_rectangle(1, 1,1,1, fill= "#000000", alpha=0.1)
#checking if the mouse has been clicked
def mouse_down(event):
    global x_mouse_down_value, y_mouse_down_value, mouse_is_down, generating, interrupt
    if event.x > 1000:
        return
    x_mouse_down_value = event.x
    y_mouse_down_value = event.y
    if generating == True:
        mouse_is_down = False
    if generating == False and interrupt == False:
        mouse_is_down = True

#updates the outline box while the mouse is held down
def draw_outline_box(event):
    global x_mouse_down_value, y_mouse_down_value, mouse_is_down, outline, generating, outline_fill
    mouse_x_position, mouse_y_position = canvas.canvasx(event.x), canvas.canvasy(event.y)
    if generating == True:
        mouse_is_down = False
    if interrupt == True:
        mouse_is_down = False
    if mouse_x_position >= 1000 or mouse_x_position <= 0 or mouse_y_position >= 800 or mouse_y_position <= 0:
        mouse_is_down = False
        canvas.delete(outline) #deleting old outline box
        canvas.delete(outline_fill)
        return
    if mouse_is_down == True:
        canvas.delete(outline)
        canvas.delete(outline_fill)
        x_coordinate = x_mouse_down_value
        y_coordinate = y_mouse_down_value
        if mouse_x_position < x_coordinate: #switching around the x and y values if needed cause otherwise it doesnt work
            temp_x_position = x_coordinate
            x_coordinate = mouse_x_position
            mouse_x_position = temp_x_position
        if mouse_y_position < y_coordinate:
            temp_y_position = y_coordinate
            y_coordinate = mouse_y_position
            mouse_y_position = temp_y_position
        create_rectangle(x_coordinate,y_coordinate,mouse_x_position,mouse_y_position, width=2, outline="#888888", fill= "#888888", alpha=0.4)

#deletes outline box, changes real_coordinate, imaginary_coordinate and zoom based on values determined by the box
#and reloads the set
def mouse_up(event):
    global x_mouse_up_value, y_mouse_up_value, x_mouse_down_value, y_mouse_down_value, zoom, real_coordinate, \
        imaginary_coordinate, mouse_is_down, outline, outline_fill
    if mouse_is_down == False:
        return
    mouse_is_down = False

    if event.x > 1000:
        return

    canvas.delete(outline)
    canvas.delete(outline_fill)
    x_mouse_up_value = event.x
    y_mouse_up_value = event.y
    if x_mouse_down_value == x_mouse_up_value and y_mouse_down_value == y_mouse_up_value:
        mouse_is_down = False
        return
    if x_mouse_down_value == x_mouse_up_value :
        x_mouse_up_value += 1
    if y_mouse_down_value == y_mouse_up_value:
        y_mouse_up_value += 1
    #calculating real and imaginary coordinates
    x_outline_midpoint = ((x_mouse_down_value + x_mouse_up_value) / 2)
    y_outline_midpoint = ((y_mouse_down_value + y_mouse_up_value) / 2)
    real_coordinate = ((x_outline_midpoint - 500) / (zoom * 300)) + real_coordinate
    imaginary_coordinate = ((y_outline_midpoint - 400) / (zoom * 300)) + imaginary_coordinate
    #calculating zoom
    x_zoom_multiple = abs(1000 / (x_mouse_down_value - x_mouse_up_value))
    y_zoom_multiple = abs(400 / (y_mouse_down_value - y_mouse_up_value))
    #maintaining aspect ratio of the image
    if x_zoom_multiple < y_zoom_multiple:
        zoom = (y_zoom_multiple * zoom)


    if x_zoom_multiple > y_zoom_multiple:
        zoom = (x_zoom_multiple * zoom)

    real_coordinate_field.delete(0, END)
    real_coordinate_field.insert(0, str(real_coordinate))
    imaginary_coordinate_field.delete(0, END)
    imaginary_coordinate_field.insert(0, str(imaginary_coordinate))
    zoom_field.delete(0, END)
    zoom_field.insert(0, str(zoom))
    generate()
def cancel(event=None):
    global mouse_is_down
    mouse_is_down = False
    canvas.delete(outline)
    canvas.delete(outline_fill)
#shuts down the program
def exit():
    stop()
    window.quit()
    sys.exit()

#binding the box commands to the mouse
window.bind("<Motion>", draw_outline_box)
window.bind("<Button-1>", mouse_down)
window.bind("<ButtonRelease>", mouse_up)
window.bind('<Escape>', cancel)



generation_button = Button(window, text='Generate', command=lambda: generate(), width=15, height=1, bg="#888888")
generation_button.place(x=1007, y=400)
resetting_button = Button(window, text='Reset', command=lambda: reset(), width=15, height=1, bg="#888888")
resetting_button.place(x=1007, y=440)
stop_button = Button(window, text='Stop', command=lambda: stop(), width=15, height=1, bg="#888888")
stop_button.place(x=1007, y=480)
exit_button = Button(window, text='Exit', command=lambda: exit(), width=15, height=1, bg="#888888")
exit_button.place(x=1007, y=640)


generate()
window.update()
window.mainloop()

