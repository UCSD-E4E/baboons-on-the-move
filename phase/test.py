
from multiprocessing import Process, Queue
import os

def f(q, frame_count):
    i = 0
    
    os.system( "ps | grep 'python3 phase/test.py'" )

    while i < frame_count:
        if not q.empty():
            print( q.get() )
            i += 1

if __name__ == '__main__':
    frame_count = 100
    q = Queue()
    p = Process(target=f, args=(q, frame_count))
    p.start()

    for i in range( 0, frame_count ):
        q.put( [i, None, 'hello'] )

    p.join( )