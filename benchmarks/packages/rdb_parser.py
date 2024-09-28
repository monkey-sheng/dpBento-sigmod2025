from .parser import Parser


class RDBParser(Parser):
    def __init__(self):
        super().__init__()
        self._add_rdb_arguments()

    def _add_rdb_arguments(self):
        self.parser.add_argument('--scale_factors', type=str, required=True, help='Scale factors for RDB benchmarks')
        self.parser.add_argument('--query', type=str, required=True, help='Query for RDB benchmarks')
        self.parser.add_argument('--execution_mode', type=str, required=True, help='Execution mode for RDB benchmarks')

    def parse_arguments(self):
        return self.parser.parse_args()