import os

from wa import Workload, Parameter, Executable

results_matrix_bench = 'results_matrix_bench.csv'

class matrixbench(Workload):

    name = 'matrixbench'
    description = """
    A multiplication matrix benchmark

    """
    parameters = [
        # Workload parameters go here e.g.
        Parameter('num_threads', kind=int, default=1, description='Number of threads.'),
        Parameter('matrix_size', kind=int, default=256, description='Matrix size.'),
        Parameter('duration', kind=int, default=3600, description='Maximun duration in seconds.'),
        Parameter('which_cpus', kind=str, default='all', description='Select on which cpu the benchmark should be execute.'),
        Parameter('num_iter', kind=int, default=10, description='Select the number of iterations to perform'),
        Parameter('num_loop', kind=int, default=10, description='Select the number of loops to perform')
    ]

    def setup(self, context):
        super(matrixbench, self).setup(context)
        self.binary_name = 'benchmark'
        self.command = '{} -t {} -m {} -c {} -i {} -l {}> {}'

        host_binary = context.resolver.get(Executable(self, self.target.abi,
                                                            self.binary_name))
        self.device_binary = self.target.install(host_binary)
        self.hackbench_result = os.path.join(self.target.working_directory,
                                                'results_matrix_bench')

        self.command = self.command.format(self.device_binary, self.num_threads,
                                            self.matrix_size, self.which_cpus,
                                            self.num_iter, self.num_loop,
                                            self.hackbench_result)

    def run(self, context):
        self.target.execute(self.command, timeout=self.duration+200)

    def update_output(self, context):
        self.target.pull(self.hackbench_result, context.output_directory)

        with open(os.path.join(context.output_directory, 'results_matrix_bench')) as hackbench_file:
            for line in hackbench_file:
                context.add_metric("mean_time", float(line),
                "milliseconds", lower_is_better=True)

    def teardown(self, context):
        self.target.uninstall(self.binary_name)
        self.target.remove(self.hackbench_result)

