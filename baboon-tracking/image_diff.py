class ImageDiffStrategy():
    def __init__(self, ):
        pass

    def generate_mask(self):
        pass

class VariableBackgroundSub_ImageDiffStrategy(ImageDiffStrategy):
    '''
    This is the strategy that we've been implementing, using hist of dissimilarity,
    freq of commonality, weights, etc
    '''
    def _intersect(self):
        pass

    def _union(self):
        pass

    def _get_weights(self):
        pass

    def _quantize_frame(self):
        '''
        Normalize pixel values from 0-255 to values from 0-10
        Returns quantized frame
        '''
    
    def generate_mask(self):
        pass

class SimpleBackroundSub_ImageDiffStrategy(ImageDiffStrategy):
    '''
    Using simple python background subtraction
    '''

    def generate_mask(self):
        pass


