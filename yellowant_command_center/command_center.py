"""
Command Center to define which functions has to be done when.
"""
from yellowant.messageformat import MessageClass
from yellowant_api.models import UserIntegration
from .commands_by_invoke_name import commands_by_invoke_name


class CommandCenter:
    """Class Command Center."""
    def __init__(self, yellowant_integration_id, command_name, args):
        self.yellowant_integration_id = yellowant_integration_id
        self.command_name = command_name
        self.args = args

        try:
            self.user_integration = UserIntegration.objects.get(
                yellowant_integration_id=self.yellowant_integration_id)
        except UserIntegration.DoesNotExist:
            self.user_integration = None
        self.command = commands_by_invoke_name.get(self.command_name)
    def parse(self):
        """Function for parsing."""
        message = MessageClass()
        if self.yellowant_integration_id is None:
            message.message_text = "Sorry! I could not find your integration."
            return message
        elif self.command is None:
            message.message_text = "Sorry! I could not find that command."
            return message
        # build YA message object
        message = self.command(self.args, self.user_integration)
        # use inbuilt sdk method to_json to return message in a json format accepted by YA
        return message.to_json()
