
class BaseJobRescheduleException(Exception):
    def __init__(self, reschedule_delay_in_minutes, *args):
        super().__init__(*args)
        self.delay_in_minutes = reschedule_delay_in_minutes

class JobRescheduleConnectionTimeoutException(BaseJobRescheduleException):
    def __init__(self, reschedule_delay_in_minutes, *args):
        super().__init__(reschedule_delay_in_minutes, *args)

class JobRescheduleConnectionError(BaseJobRescheduleException):
    def __init__(self, reschedule_delay_in_minutes, *args):
        super().__init__(reschedule_delay_in_minutes, *args)