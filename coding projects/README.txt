There are three different programs in this folder.

red_river_application_code.py is the solution to the programming challenge given by Red River Software, which can be found at https://gist.github.com/sedders123/cf425ab35e5406c5e2af25aa51b858a2

online_chat_GUI.py is the GUI portion of an online chatting program I've been working on with my friend, this section of the code was written by me alone, which is why I've decided to send it. 

In the fractal generator folder, Fractal_generator_V_C3.py is the main code for the fractal generator program, 
generating a fractal requires constant iteration of a given value which leads the program to run incredibly slowly in base python, as such I wrote the more resource intensive sections in cython, a python module that
allows you to write and run C code in python, the uncompiled cython code is stored in cy_fractal_static.pyx.
if the cython code won't run correctly, I've also included an older version of the program, fractal_generator_v2 which doesn't use cython, however this is significantly slower than the cython version

Currently the fractal generator doesn't work outside of an IDE, I'm not entirely sure why this is (I assume it's because I don't have the necessary libraries outside of my IDE) but I apologise for the inconvenience. 

 