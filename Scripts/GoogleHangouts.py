from SeeThru_Feeds.Model.Scripts.ScriptBase import ScriptBase
from SeeThru_Feeds.Model.Scripts.ScriptResult import ScriptResult
from SeeThru_Feeds.Model.Properties.Properties import FillableProperty, ResultProperty
from SeeThru_Feeds.Library.Components.Socket import PortOpen
from SeeThru_Feeds.Library.Components.HTTP import HTTPGet
import json

class GoogleHangouts(ScriptBase):
    HANGOUTS_ERROR = ResultProperty(name="hangouts_error", default=True)
    ERROR_MESSAGE = ResultProperty(name="error_message")
    IS_PORT_OPEN = ResultProperty(name="is_port_open")

    Script_Title="GoogleHangouts"
    Script_Description = "A script which tests google hangouts"
    Script_Author = "SeeThru Networks"
    Script_Owner = "SeeThru Networks"

    def port_open(self):
        is_port_open = PortOpen().SetProperty(PortOpen.TARGET_HOST, "hangouts.google.com").SetProperty(PortOpen.PORT, 443).Run().GetProperty(PortOpen.SUCCEEDED)
        self.SetProperty(self.IS_PORT_OPEN, is_port_open)
        return is_port_open

    # ------ Script Overrides ------
    def Script_Run(self): 
        # Checks if the port is open on the server
        if not self.port_open():
            return

        #Gets the google status page json
        try: page = HTTPGet().SetProperty(HTTPGet.URL, "https://www.google.com/appsstatus/json/en").Run()
        except: return

        try:
            #Converts the response to json, ommiting dashboard.jsonp
            response = json.loads(page.GetProperty(HTTPGet.RESPONSE_CONTENT)[16:-2])
            #Loops through all the messages and finds any google hangouts messages
            for i in range(len(response['messages'])-1, 0, -1):
                message = response['messages'][i]
                #The google hangouts id in the json response is 22
                if message['service'] == 22:
                    self.SetProperty(self.HANGOUTS_ERROR, not (message['type'] == 3 or message['type'] == 4))
                    self.SetProperty(self.ERROR_MESSAGE, message['message'])
                    return
        except:
            return

    def Script_Evaluate(self, result):
        result.SetStatus("green")
        result.SetMessage("")

        # Changes to red if the port is closed
        if not self.GetProperty(self.IS_PORT_OPEN):
            result.SetStatus("red")
            result.SetMessage("Could not connect to google hangouts.")
        
        #Checks if there is a hangouts error
        elif self.GetProperty(self.HANGOUTS_ERROR):
            result.SetStatus("red")
            message = "Google: \"{}\"".format(self.GetProperty(self.ERROR_MESSAGE))
            if len(message) > 256: message = "There is an issue with hangouts, please look at https://www.google.com/appsstatus"
            result.SetMessage(message)