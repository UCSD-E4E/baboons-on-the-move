"""
Implements a treeviewer based Pipeline Viewer
"""

# import tkinter as tk
# from tkinter import ttk
# from pipeline.parent_stage import ParentStage

# from pipeline.pipeline import Pipeline
# from pipeline.serial import Serial
# from pipeline.parallel import Parallel
# from pipeline.stage import Stage


class PipelineViewer:
    """
    Implements a treeviewer based Pipeline Viewer
    """

    def __init__(self, pipeline: Pipeline):
        self._pipeline = pipeline

    def run(self):
        """
        Displays the pipeline viewer.
        """

        title = type(self._pipeline).__name__

        root = tk.Tk()
        root.title(title)

        tree = ttk.Treeview(root)
        tree.pack(fill=tk.BOTH, expand=True)

        self._add_stage(tree, "", self._pipeline.stage)

        root.mainloop()

    def _add_stage(self, tree: ttk.Treeview, parent: str, stage: Stage):
        name = type(stage).__name__

        if isinstance(stage, ParentStage):
            name = stage.name

            if isinstance(stage, Serial):
                name += " (Serial)"

            if isinstance(stage, Parallel):
                name += " (Parallel)"

        parent = tree.insert(parent, index="end", iid=name, text=name)

        if isinstance(stage, ParentStage):
            for child in stage.stages:
                self._add_stage(tree, parent, child)
