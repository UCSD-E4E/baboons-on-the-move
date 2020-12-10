"""
Provides an algorithm for extracting baboons from drone footage.
"""
from baboon_tracking.preset_pipelines import preset_pipelines


class BaboonTracker:
    """
    An algorithm that attempts to extract baboons from drone footage.
    """

    def __init__(self, pipeline_name="default"):
        self._pipeline = preset_pipelines[pipeline_name]

    def run(self):
        """
        Runs the algorithm until it finishes.
        """

        while True:
            self._pipeline.before_execute()
            result = self._pipeline.execute()
            self._pipeline.after_execute()

            if not result.continue_pipeline:
                print("Average Runtime per stage:")
                self._pipeline.get_time().print_to_console()

                self._pipeline.on_destroy()

                return

    def flowchart(self):
        """
        Generates a chart representing the algorithm.
        """

        img, _, _, = self._pipeline.flowchart()
        return img
