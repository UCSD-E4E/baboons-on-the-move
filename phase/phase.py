from multiprocessing import Process, Queue
import random
import time

# Basic unit of multipipelining 
class Phase:
    
    def __init__( self, sm_output_list = None ):
        super().__init__()

        self.on             = True  
        self.collect_time   = False
        self.duration       = None
        self.steps          = []

        self.launched_next = False
        self.next = None

    def start( self, source, time_to_live ):
        self.p = Process( target=self._new_process, args=(source, time_to_live) )
        self.p.start()
        
    def apply( self, obj ):

        if not self.on:
            return obj

        self.on_start( obj )

        res = obj
        for f in self.steps:
            if isinstance( f, Phase ):
                res = f.apply( res )
            else:
                res = f( res )

        self.on_complete( obj )

        return res

    def on_start( self, obj ):
        if self.collect_time:
            duration = time.perf_counter()

    def on_complete( self, obj ):
        # somewhat naive, only keeps time from the last execution
        if self.collect_time:
            self.duration = time.perf_counter() - duration
    
    def add( self, t ):
        self.steps.append( t )

    def show( self ):
        pass

    def _new_process(self, source, time_to_live):

        if not self.launched_next:
            q = Queue()
            
        i = 0
        while i < time_to_live:
            if not source.empty():
                n_item  = source.get()
                res     = self.apply( n_item )

                if not self.launched_next and self.next is not None:
                    self.next.start( q, time_to_live )
                    self.launched_next = True
                    q.put( res )
                elif self.launched_next:
                    q.put( res )
                
                i += 1

