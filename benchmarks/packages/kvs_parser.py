from .parser import Parser
import json

class KVSParser(Parser):
    def __init__(self):
        super().__init__()
        self._add_kvs_arguments()
        
    def _add_kvs_arguments(self):
        self.parser.add_argument('--operation_size', type=int, required=True, help='Operation sizes for KVS benchmarks')
        self.parser.add_argument('--operation_type', required=True, help='Operation types for KVS benchmarks')
        self.parser.add_argument('--data_distribution_type', type=str, required=True, help='Data distribution types for KVS benchmarks')
        self.parser.add_argument("--operation_size_description", help="Description of operation sizes")
        self.parser.add_argument("--operation_type_description", help="Description of operation types")
        self.parser.add_argument("--data_distribution_type_description", help="Description of data distribution types")
        self.parser.add_argument("--metrics", nargs='+', help="Metrics to collect, e.g., latency, runtime, throughput")
        self.operation_type = json.loads(self.operation_type)


    def parse_arguments(self):
        return self.parser.parse_args()