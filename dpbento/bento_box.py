from enum import IntEnum

class HWPlatform(IntEnum):
    HOST = 1
    BF2 = 2
    BF3 = 3
    UNDEFINED_LAST = 4  # keep this last

class BentoBox:
    """
    This is the base class for all boxes (tests). This provides an interface for the main runner to invoke
    each test.


    """
    def __init__(self, hw_platform = HWPlatform.HOST) -> None:
            '''
            The arguments are passed in here, and should all be kwargs.

            Args:
                hw_platform: The hardware platform to run on. Defaults to HWPlatform.HOST.
            '''
            raise NotImplementedError

    def init(self) -> None:
        '''
        This is called to setup the test environment by the master runner.
        Called once before the test is run.
        '''
        raise NotImplementedError

    def run(self) -> None:
        '''
        Actually running the test.
        Should probably call _parse_results() at the end,
        where results would be generated and parsed and stored to somewhere.
        '''
        raise NotImplementedError

    def _parse_results(self) -> None:
        '''
        Parse the results of the test. Should be called at the end of run().
        '''
        raise NotImplementedError

    def plot(self) -> None:
        '''
        Plot the results of the test, probably reading the parsed results.
        '''
        raise NotImplementedError

    

