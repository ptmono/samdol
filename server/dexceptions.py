
class NoContainerException(Exception):
    '''
    Each container deals each domain. This exception is raised when blocker
    couldn't found the container of the domain.
    '''
    pass

