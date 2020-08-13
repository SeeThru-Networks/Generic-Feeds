from SeeThru_Feeds.Model.Scripts.ScriptBase import ScriptBase
from SeeThru_Feeds.Model.Scripts.ScriptResult import ScriptResult
from SeeThru_Feeds.Model.Properties.Properties import FillableProperty, ResultProperty
from SeeThru_Feeds.Library.Components.Socket import PortOpen
from SeeThru_Feeds.Library.Components.HTTP import HTTPGet
import json


class GoogleHangouts(ScriptBase):
    HANGOUTS_ERROR = ResultProperty(name="hangouts_error", default=False)
    ERROR_MESSAGE = ResultProperty(name="error_message")
    IS_PORT_OPEN = ResultProperty(name="is_port_open")

    Script_Title = "GoogleHangouts"
    Script_Description = "A script which tests google hangouts"
    Script_Author = "SeeThru Networks"
    Script_Owner = "SeeThru Networks"

    def port_open(self):
        is_port_open = PortOpen().set_property(PortOpen.TARGET_HOST, "hangouts.google.com")\
            .set_property(PortOpen.PORT,443).run().get_property(PortOpen.SUCCEEDED)
        self.set_property(self.IS_PORT_OPEN, is_port_open)
        return is_port_open

    # ------ Script Overrides ------
    def script_run(self):
        # Checks if the port is open on the server
        if not self.port_open():
            return

        # Gets the google status page json
        try:
            page = HTTPGet().set_property(HTTPGet.URL, "https://www.google.com/appsstatus/json/en").run()
        except:
            return

        try:
            # Converts the response to json, ommiting dashboard.jsonp
            response = json.loads(page.get_property(HTTPGet.RESPONSE_CONTENT)[16:-2])
            # Loops through all the messages and finds any google hangouts messages
            for i in range(len(response['messages']) - 1, 0, -1):
                message = response['messages'][i]
                # The google hangouts id in the json response is 22
                if message['service'] == 22:
                    self.set_property(self.HANGOUTS_ERROR, not (message['type'] == 3 or message['type'] == 4))
                    self.set_property(self.ERROR_MESSAGE, message['message'])
                    return
        except:
            return

    def script_evaluate(self, result):
        result.set_status("green")
        result.set_message("")

        # Changes to red if the port is closed
        if not self.get_property(self.IS_PORT_OPEN):
            result.set_status("red")
            result.set_message("Could not connect to google hangouts.")

        # Checks if there is a hangouts error
        elif self.get_property(self.HANGOUTS_ERROR):
            result.set_status("red")
            message = "Google: \"{}\"".format(self.get_property(self.ERROR_MESSAGE))
            if len(message) > 256:
                message = "There is an issue with hangouts, please look at https://www.google.com/appsstatus"
            result.set_message(message)
