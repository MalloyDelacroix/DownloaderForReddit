
def verify_run(method):
    """
    Decorator method that verifies that the containing class's continue_run variable is set to True before calling the
    supplied method.
    :param method: The method that should be called if the run condition is met.
    """
    def check(instance, *args, **kwargs):
        if instance.continue_run:
            return method(instance, *args, **kwargs)

    return check
