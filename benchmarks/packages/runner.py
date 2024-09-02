import os

class Runner:
    def __init__(self, args):
        self.args = args
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.dirname(current_dir)
        self.output_dir = os.path.join(parent_dir, 'output')
        self.create_directory(self.output_dir)
        

    def create_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
