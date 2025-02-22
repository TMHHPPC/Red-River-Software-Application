from math import log, floor, sin, pi, e, ceil
cimport cython

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)

cpdef iterate(long double x, long double y, long int maximum_generation, long double colour_sensitivity):
    cdef long double y0 = y
    cdef long double x0 = x
    cdef long double xtemp = 0
    cdef long int i
    for i in range(0, maximum_generation):
        if (x*x) + (y*y) > 256:
            return colour_scheme(i, x, y, colour_sensitivity)  # sends any escaping value to the colour scheme
        xtemp = x*x - y*y + x0
        y = 2*x*y + y0
        x = xtemp # actual formula for the set
    return 0, 0, 0  # returns black if value didn't escape

cpdef colour_scheme(long int generation_number, long double x, long double y, long double colour_sensitivity):
    # smooth colouring code
    cdef long double smooth_colouring_value = log((log(((x*x) + (y*y)), e) / 2) / log(2, e), e) / log(2, e)
    cdef long double colour_value = (generation_number + 1 - smooth_colouring_value)
    if colour_value < 2.8:
        colour_value = 2.8
    # formulae for the colour scheme
    colour_value = log(colour_value, e) / colour_sensitivity  # logarithmic colouring + applying the colour sensitivity
    # calculations for rgb values
    #potential future optimisation here: replace pi/3 and pi/6 with precalculated values, would have to be really high
    #accuracy values though to avoid colour desyncs at higher zooms
    cdef int r = floor(170 * abs(sin(colour_value - (pi / 3))))
    cdef int g = floor(170 * abs(sin(colour_value - (pi / 6))))
    cdef int b = floor(170 * abs(sin(colour_value)))
    return r, g, b

    