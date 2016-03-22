__author__ = 'hdthdt'
M_MAX = 0.9921875
M_MIN = 0.5
M_MAX_DEC = 0b1111111
M_MIN_DEC = 0b1000000

def standardizeM(m):
    '''Scale a float in (0.5,1) to a 7-bit binary form'''
    tmp = []
    while len(tmp) < 7:
        tmp.append(int(m*2))
        m = m*2 - tmp[-1]
    m_bin = ''.join([str(i) for i in tmp])
    if int(m_bin, 2) <= 0:
        raise Exception('[SizeError] Too small') 
    return m_bin
    
def standardizeE(e):
    '''Cast a int to a 7-bit binary form'''
    if e > 127:
        raise Exception('[SizeError] Too small or too big')
    e_bin = bin(e)[2:]
    while len(e_bin) < 7:
        e_bin = '0' + e_bin
    return e_bin
   
def parseFloat(originfloat):
    '''Cast a float type in python to 16-bit MyFloat in binary string'''
    originabs = abs(originfloat)
    if not isinstance(originfloat, float) :
        raise Exception('[TypeError] Only float is supported, float the integer first')
    if originabs == 0:
        raise Exception('[ZeroError] Zero is not supported')
    if originfloat < 0 :
        sm = 1
    else :
        sm = 0 
        assert originfloat > 0 
    if originabs < M_MIN:
        se = 1
        e = 0
        while originabs < M_MIN:
            originabs *= 2
            e += 1
        m = originabs
    elif originabs > M_MAX:
        se = 0
        e = 0
        while originabs > M_MAX:
            originabs /= 2
            e += 1
        m = originabs
    else :
        se = 0 
        e = 0
        m = originabs
    return (str(se), standardizeE(e), str(sm), standardizeM(m))

def scale(tmp_m, tmp_e):
    '''construct a standard 16-bit float from a signed mantissa and a signed exponent'''
    if tmp_m == 0:
        raise Exception('[ZeroError] Mantissa is 0')
    result = MyFloat()
    if tmp_m < 0:
        result.sm = '1'
    else:
        result.sm = '0'
    tmp_m = abs(tmp_m)
    if tmp_m < M_MIN_DEC:
        while tmp_m < M_MIN_DEC:
            tmp_m *= 2
            tmp_e -= 1
    elif tmp_m > M_MAX_DEC:
        while tmp_m > M_MAX_DEC:
            tmp_m /= 2
            tmp_e += 1
    tmp_m = bin(tmp_m)[2:]
    while len(tmp_m) < 7:
        tmp_m = '0' + tmp_m
    result.m = tmp_m
    if tmp_e > 0:
        result.se = 0
    else:
        result.se = 1
    result.e = standardizeE(abs(tmp_e))
    return result

class MyFloat(object):
    '''The main 16-bit float class, default value is 1.0'''
    def __init__(self, origin_float=1.0):
        tmpResult = parseFloat(origin_float)
        self.se = tmpResult[0]
        self.e = tmpResult[1]
        self.sm =tmpResult[2]
        self.m = tmpResult[3]

    def __repr__(self):
        return '%s_%s_%s_%s' % (self.se, self.e, self.sm, self.m)

    def __add__(self, other):
        if (self.ev() < other.ev()):
            x = self
            y = other
        else:
            x = other
            y = self
        ex = x.ev()
        ey = y.ev()
        mx = x.mv()
        my = y.mv()
        tmp_e = ey
        tmp_m = (mx >> (ey - ex)) + my
        return scale(tmp_m, tmp_e)
        
    def __sub__(self, other):
        new = MyFloat()
        new.se = other.se
        new.e = other.e
        new.sm = str(1 - int(other.sm))
        new.m = other.m
        return self + new
        
    def __mul__(self, other):
        ex = self.ev()
        ey = other.ev()
        mx = self.mv()
        my = other.mv()
        tmp_m = mx * my
        tmp_e = ex + ey
        tmp_m = int(bin(tmp_m)[:-8] + str(int(bin(tmp_m)[-8]) | int(bin(tmp_m)[-7])), 2)
        
        return scale(tmp_m, tmp_e)
        
    def __div__(self, other):
        ex = self.ev()
        ey = other.ev()
        mx = self.mv()
        my = other.mv()
        tmp_m = 0
        tmp_e = ex - ey
        for i in xrange(7):
            tmp_m += (mx / my) << (7 - i)
            mx %= my 
            mx <<= 1
        return scale(tmp_m, tmp_e)
        
    def mv(self):
        '''return the signed mantissa of MyFloat'''
        return (-1)**int(self.sm) * int(self.m, 2)
        
    def ev(self):
        '''return the signed exponent of MyFloat'''
        return (-1)**int(self.se) * int(self.e, 2)

    def decode(self):
        '''Test the result of MyFloat Calculation'''
        e = self.ev()
        m = self.mv()/128.0
        return 2**e*m

def fmtPrint(c, res):
    '''print the calculation result in a pre-defined format'''
    template = "%s,%f,%f,%f"
    print  template % (c, c.decode(), res, abs((res - c.decode()) / res))
    
def main(x, y):
    '''Calculate four arithmetic operation between x and y, and compare the result'''
    a = MyFloat(x)
    b = MyFloat(y)
    c = a + b
    fmtPrint(c, x + y)
    c = a - b
    fmtPrint(c, x - y)
    c = a * b
    fmtPrint(c, x * y)
    c = a / b
    fmtPrint(c, x / y)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print 'Usage:\npython ' + sys.argv[0] + ' float1 float2'
        sys.exit(1)
    
    main(float(sys.argv[1]), float(sys.argv[2]))
