import unittest
import os
import time
from phase import Phase
from pipeline import Pipeline
from phase_exceptions import NoPhasesException 

class TestPhase( unittest.TestCase ):

    # Square every number in an integer sequence using Phase
    def test_single_apply( self ):
        x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        pipeline = Phase()
        pipeline.add( lambda x: x**2 ) 
        for i in x:
            self.assertEqual(x[i] ** 2, pipeline.apply(i))

    # Square every number in an integer sequence using nested Phases
    def test_nested_apply( self ):
        x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        pipeline = Phase()
        sub_phase = Phase( )
        sub_phase.add( lambda x: x**2 )
        pipeline.add( sub_phase ) 
        for i in x:
            self.assertEqual(x[i] ** 2, pipeline.apply( i ) )

    # test the phase object when applying 3 phases each in its own process
    def test_multiprocess_length( self ):
        frame_count = 100
        pipeline = Pipeline( ) 
        pipeline.add_phase( lambda x: x * 2 )
        pipeline.add_phase( lambda x: x + 1 )
        assert( len( pipeline ) == 2 )

    def test_no_phases( self ):
        frame_count = 100
        pipeline = Pipeline( ) 
        assert( len( pipeline ) == 0 )
        with self.assertRaises(NoPhasesException): 
            pipeline.start( frame_count )

    # test the phase object when applying 3 phases each in its own process
    def test_single_phase( self ):

        frames = 450

        # create a pipeline and shared memeory manager
        pipeline = Pipeline( )
        pipeline.add_phase( lambda x: 2 * x )
        assert( len( pipeline ) == 1 )

        # begin multiprocessing
        pipeline.start( frames )
        for i in range(0, frames ):
            pipeline.schedule_input( i )

        # collect the output in the main function
        i = 0
        while i < frames:
            if not pipeline._output_queue.empty():
                output = pipeline._output_queue.get()
                assert( 2 * i == output )
                i += 1

    # test the phase object when applying 3 phases each in its own process
    def test_multiple_phases( self ):

        frames = 1800

        # create a pipeline and shared memeory manager
        pipeline = Pipeline( )
        pipeline.add_phase( lambda x: 2 * x )
        pipeline.add_phase( lambda x: 1 + x )
        pipeline.add_phase( lambda x: 1 + x )

        assert( len( pipeline ) == 3 )
        
        # start multiprocessing and configure IPC queues   
        pipeline.start( frames )
        for i in range(0, frames ):
            pipeline.schedule_input( i )

        i = 0
        while i < frames:
            if pipeline.has_output():
                output = pipeline.next_output()
                assert( 2 + 2 * i == output )
                i += 1
                
if __name__ == '__main__':
    unittest.main()
