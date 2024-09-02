import os

class Runner:
    def __init__(self, args):
        self.args = args
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        self.create_directory(self.output_dir)
        
        self.log_file_path = os.path.join(self.output_dir, "result.csv")
        self.log_file = open(self.log_file_path, 'a')

    def create_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    
    def close_log_file(self):
        self.log_file.close()