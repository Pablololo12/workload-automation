import os

from wa import Instrument, Parameter, Executable
from wa.utils.types import list_or_string

class PIDGovernor(Instrument):
    name = 'pid_governor'
    description = """
    Runs a frequency PID controller
    """

    parameters = [
        Parameter('period', kind=int, default=100, description='Maximun duration in seconds.'),
        Parameter('desired_temp', kind=int, default=70000, description='The desired temperature in millicelsius.'),
        Parameter('pid_params', kind=list_or_string, description='E F A B C parameters for the PID function')
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

        self.command = '{} {} {} {} > {}'
        self.command = self.command.format(self.device_binary,
                                        ' '.join(self.pid_params),
                                            self.period,
                                            self.desired_temp,
                                            self.log_pid)

    def start(self, context):
        self.target.kick_off(self.command, as_root=True)

    def stop(self, context):
        self.target.killall(self.binary_name, signal='TERM', as_root=True)

    def update_output(self, context):
        host_output_file = os.path.join(context.output_directory, 'pid_log.txt')
        self.target.pull(self.log_pid, host_output_file)

    def teardown(self, context):
        self.target.remove(self.log_pid)

    def finalize(self, context):
        self.target.uninstall(self.binary_name)
