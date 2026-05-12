from math import sqrt

def take_third_point(x1, y1, x2, y2): 
    return x1 + (x2-x1)/2 + (sqrt(3)/2)*(y2-y1), y1+(y2-y1)/2-(sqrt(3)/2)*(x2-x1)
