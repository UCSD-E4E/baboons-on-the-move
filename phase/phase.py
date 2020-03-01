from multiprocessing import Process, Queue
import random
import time

class Phase:
    '''
    A base unit of multipipelining in Phase, that can compose function pointers and 
    subphases to be executed be executed in one more or processes.
    '''
    def __init__( self, sm_output_list = None ):
        super().__init__()

        self.on             = True  
        self.collect_time   = False
        self.duration       = None
        self.steps          = []

        self.launched_next = False
        self.next = None

    def on_proc_start( self ):
        '''
        Callback that is called when a new process starts executing this Phase.
        '''
        pass 

    def on_proc_complete( self ):
        '''
        Callback that is called when the process finished the process running this phase has completed
        all scheduled work.
        '''
        pass

    def on_start( self, obj ):
        if self.collect_time:
            duration = time.perf_counter()

    def on_complete( self, obj ):
        # somewhat naive, only keeps time from the last execution
        if self.collect_time:
            self.duration = time.perf_counter() - duration
    
    def add( self, t ):
        self.steps.append( t )
       
    def _apply_new_process(self, input_queue, time_to_live, output_queue):
        
        # we will only process time_to_live frames
        self.on_proc_start() 

        i = 0
        while i < time_to_live:
            # if there is input waiting to be processed
            if not input_queue.empty():
                n_item  = input_queue.get()
                res     = self.apply( n_item )
                output_queue.put( res )
                
                i += 1
            else:
                # maybe some kind of optional sleep for queue balancing happens here
                continue

        self.on_proc_complete() 
        
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

