from multiprocessing import Process, Queue, Manager 
from phase import Phase
from phase_exceptions import NoPhasesException

class Pipeline():

    ## 
    # Create a new master process to manage a pipeline of worker processes
    # and handle data interchange between the groups.
    def __init__(self):
        super().__init__()

        # all transitions of state are going to pass through the manager process
        self._manager:Manager       = Manager()

        # there is a defined order to the way these phases should run
        self.head:Phase             = None
        self.tail:Phase             = None

        # default to lenth 0
        self.len                    = 0
        
        self._input_queue:Queue     = self._manager.Queue( )
        self._buffer_queues:list    = []
        self._processes             = []

    ##
    # Add a new phase to this Pipeline, which will be delegated to a worker process,
    # managed by this pipeline's master process when the user calls start.
    #
    # Note that creation of the Pipeline automatically creates a master process.
    def add_phase( self, phase ):

        # Allows this function to accept Phase objects and function pointers 
        if not isinstance( phase, Phase ):
            function = phase
            phase = Phase( )
            phase.add( function )

        # this is the first phase that has been added to this pipeline
        if self.head is None:
            self.head = phase
            self.tail = phase
            self.tail.next = None
        else:
            self.tail.next = phase
            self.tail = self.tail.next

        self.len += 1

    def start( self, input_count ):

        # return if we have no work to do
        if self.head is None:
            raise NoPhasesException()

        # initialize structures for linked list queue configuration
        curr            = self.head 
        input_queue     = self._input_queue
        output_queue    = None
        
        # for each pipeline stage we need to:
        while curr is not None:
            output_queue    = self._manager.Queue( )

            p = Process( target=curr._apply_new_process, args=( input_queue, input_count, output_queue ) )
            self._processes.append( p )
            p.start()

            curr            = curr.next            
            input_queue     = output_queue
            self._buffer_queues.append( output_queue )

        # make the entire thing output at this queue
        self._output_queue = output_queue

    def schedule_input( self, val ):
        self._input_queue.put( val )

    def has_output( self ):
        return not self._output_queue.empty()

    def next_output( self ):
        return self._output_queue.get()

    def __len__( self ):
        return self.len
    


