from .parser import Parser


class E2EParser(Parser):
    def __init__(self):
        super().__init__()
        self._add_e2e_arguments()

    def _add_e2e_arguments(self):
        self.parser.add_argument('--e2e_scale_factors', type=str, required=True, help='Scale factors for E2E benchmarks')
        self.parser.add_argument('--e2e_query', type=str, required=True, help='Query for E2E benchmarks')
        self.parser.add_argument('--e2e_execution_mode', type=str, required=True, help='Execution mode for E2E benchmarks')

    def parse_arguments(self):
        return self.parser.parse_args()