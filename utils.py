def clamp(value : float, min : float, max : float): 
    if value < min: return min
    elif value > max: return max
    return value 

def abs(value : float):
    if value < 0: return -value
    return value

def map(value, x1, x2, y1, y2):
    return (value - x1) / (x2 - x1) * (y2 - y1) + y1

def map_clamp(value, x1, x2, y1, y2, min, max):
    return clamp(map(value, x1, x2, y1, y2), min, max)