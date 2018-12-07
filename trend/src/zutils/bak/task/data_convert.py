class DefaultConvert:
    def __init__(self, client_config=None, server_config=None):
        self.client_config = client_config
        self.server_config = server_config

    def client_convert(self, input):
        return input

    def server_convert(self, input):
        return input
