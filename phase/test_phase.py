import unittest
import os
from phase import Phase
from pipeline import Pipeline

class TestPhase( unittest.TestCase ):

    # Square every number in an integer sequence using Phase
    def test_apply_1( self ):

        x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = []

        pipeline = Phase()
        pipeline.add( lambda x: x**2 ) 

        for i in x:
            y.append( pipeline.apply(i) )
        
        for i in range(0, len(x) ):
            self.assertEqual(x[i] ** 2, y[i])

    # Square every number in an integer sequence using nested Phases
    def test_nested_phase_apply_1( self ):

        x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = []

        pipeline = Phase()
        sub_phase = Phase( )
        sub_phase.add( lambda x: x**2 )
        pipeline.add( sub_phase ) 

        for i in x:
            y.append( pipeline.apply( i ) )
        
        for i in range(0, len(x) ):
            self.assertEqual(x[i] ** 2, y[i])

    # # test the phase object when applying 3 phases each in its own process
    def test_pipeline_length( self ):

        frame_count = 100

        # build up the phase seperately from the pipeline
        x = Phase( )
        x.add( lambda x: x * 2 )
        y = Phase( )
        y.add( lambda x: x + 1 )
        
        # open question, where can I collect the input
        # create a multiprocess pipeline
        pipeline = Pipeline( ) 
        pipeline.add_phase( x )
        pipeline.add_phase( y )

        assert( len( pipeline ) == 2 )

    # test the phase object when applying 3 phases each in its own process
    def test_pipeline_execute_1( self ):

        frame_count = 10

        # build up the phase seperately from the pipeline
        x = Phase( )
        x.add( lambda x: x * 2 )
        y = Phase( )
        y.add( lambda x: x + 1 )
        z = Phase( )
        z.add( test )

        # open question, where can I collect the input
        pipeline = Pipeline( )
        pipeline.add_phase( x )
        pipeline.add_phase( y )
        pipeline.add_phase( z )
        pipeline.start( frame_count )
        for i in range(0, frame_count ):
            pipeline.schedule( i )
        
def test( x ):
    # the most naive way to see the output
    print( x ) 
    return x

if __name__ == '__main__':
    unittest.main()
