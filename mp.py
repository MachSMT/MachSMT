import time
import timeout_decorator

@timeout_decorator.timeout(5)
def mytest():
    it = 0
    while it < 10 ** 10 ** 10:
        it +=1
    return it

if __name__ == '__main__':
    ret = mytest()
    print(ret)