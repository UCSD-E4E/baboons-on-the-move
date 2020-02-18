import unittest
from phase import Phase

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

if __name__ == '__main__':
    unittest.main()