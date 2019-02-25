import os

from wa import Instrument, Parameter, Executable
from wa.utils.types import list_or_string

class PIDGovernor(Instrument):
    name = 'pid_governor'
    description = """
    Runs a frequency PID controller
    """

    parameters = [
        Parameter('period', kind=float, default=0.5,
                    description='Maximun duration in seconds.'),
        Parameter('desired_temp', kind=float, default=70,
                    description='The desired temperature in celsius.'),
        Parameter('k', kind=float, default=100000,
                    description='K constant for pid'),
        Parameter('i', kind=float, default=150,
                    description='Ti constant for pid'),
        Parameter('Tzero', kind=float, default=70,
                    description='Tzero constant for PID'),
        Parameter('Fzero', kind=float, default=1421000,
                    description='Fzero constant for PID'),
        Parameter('Gain', kind=float, default=42000,
                    description='Gain for the frequency')
    ]

    def initialize(self, context):
        if not self.target.is_rooted:
            raise ConfigError('The device is not rooted, cannot run PIDGovernor as root.')

        self.binary_name = 'user_governor'
        self.binary_file = context.get_resource(Executable(self,
                                                self.target.abi,
                                                self.binary_name))
        self.device_binary = self.target.install(self.binary_file)
        self.log_pid = os.path.join(self.target.working_directory,
                                                "pid_log.txt")

        #user_governor -k 100000 -i 150 -s 0.5 -o 70 -f 1421000 -t 70 -g 42000
        self.command = '{} -k {} -i {} -s {} -o {} -f {} -t {} -g {} > {}'
        self.command = self.command.format(self.device_binary,
                                            self.k,
                                            self.i,
                                            self.period,
                                            self.desired_temp,
                                            self.Fzero,
                                            self.Tzero,
                                            self.Gain,
                                            self.log_pid)

    def start(self, context):
        self.target.kick_off(self.command, as_root=True)

    def stop(self, context):
        self.target.killall(self.binary_name, signal='TERM', as_root=True)

    def update_output(self, context):
        host_output_file = os.path.join(context.output_directory,'pid_log.txt')
        self.target.pull(self.log_pid, host_output_file)

    def teardown(self, context):
        self.target.remove(self.log_pid)

    def finalize(self, context):
        self.target.uninstall(self.binary_name)
