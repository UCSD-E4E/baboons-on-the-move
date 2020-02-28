from multiprocessing import Process, Queue
from phase import Phase

class Pipeline():

    def __init__(self):
        super().__init__()

        # TODO manager makes some kind of shared dictionary ? 
        self.head:Phase = None
        self.tail:Phase = None
        self.len    = 0

    def add_phase( self, phase ):

        # TODO make each stage know about the shasred memory 
        # can I do this?
        # is this good practice 
        # does sharing with many processes make it slower 
        if self.head is None:
            self.head = phase
            self.tail = phase
            self.tail.next = None
        else:
            self.tail.next = phase
            self.tail = self.tail.next

        self.len += 1

    def start( self, input_count ):
        if self.head is not None:
            self.input_queue:Queue = Queue( )
            self.head.mp_apply( self.input_queue, input_count )

    def schedule( self, val ):
        self.input_queue.put( val )

    def __len__( self ):
        return self.len
    


