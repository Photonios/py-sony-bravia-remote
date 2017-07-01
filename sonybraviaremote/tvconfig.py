class TVConfig:
    """Collection of configuration details
    for a TV.

    This for example includes the IP address
    of the TV.
    """

    def __init__(self, host: str, device_name: str):
        """Initializes a new instance of :see:TVConfig.

        Arguments:
            host:
                The hostname or IP address
                of the TV.

            device_name:
                The name under which to register
                this controller.
        """

        self.host = host
        self.device_name = device_name
