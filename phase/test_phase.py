import unittest
from phase import Phase
from multiprocessing import Process, Queue
from multiprocessing import Manager

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
    # def test_phase_mp_1( self ):

    #     # key issue: how can we collect/test the output easily 
    #     frame_count = 100

    #     smm = Manager( )
    #     sl = smm.list( )

    #     x = Phase( )
    #     x.add( lambda x: x * 2 )
    #     y = Phase( )
    #     y.add( lambda x: x + 1 )
    #     x.next = y
    #     z = Phase( sl )
    #     z.add( lambda x: sl.append(x) ) # this would be incredible if this could work
    #     y.next = z

    #     q = Queue()
    #     x.start( q, frame_count )

    #     for i in range( 0, frame_count ):
    #         q.put( i )

    #     print( sl )


if __name__ == '__main__':
    unittest.main()
