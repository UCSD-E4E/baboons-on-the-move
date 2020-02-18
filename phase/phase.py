import random
import time

# Basic unit of multipipelining 
class Phase:
    
    def __init__( self ):
        super().__init__()

        self.on             = True  
        self.collect_time   = False
        self.duration       = None
        self.steps          = []

    def apply( self, obj ):

        if not self.on:
            return obj

        self.on_start( obj )

        if self.collect_time:
            duration = time.perf_counter()

        res = obj
        for f in self.steps:
            if isinstance( f, Phase ):
                res = f.apply( res )
            else:
                res = f( res )

        # somewhat naive, only keeps time from the last execution
        if self.collect_time:
            self.duration = time.perf_counter() - duration

        self.on_complete( obj )

        return res

    def on_start( self, obj ):
        pass 

    def on_complete(self, obj):
        pass
    
    def add( self, t ):
        self.steps.append( t )

    def show( self ):
        pass