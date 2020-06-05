from SeeThru_Feeds.Model.Scripts.ScriptBase import ScriptBase
from SeeThru_Feeds.Model.Scripts.ScriptResult import ScriptResult
from SeeThru_Feeds.Model.Properties.Properties import FillableProperty, ResultProperty
from SeeThru_Feeds.Library.Components.Socket import PortOpen
from SeeThru_Feeds.Library.Components.HTTP import HTTPGet
import json

class Zoom(ScriptBase):
    ALL_OPERATIONAL = ResultProperty(name="all_operational", default=False)
    ZOOM_INDICATOR = ResultProperty(name="zoom_indicator")
    ZOOM_DESCRIPTION = ResultProperty(name="zoom_description")
    VALID_JSON = ResultProperty(name="valid_json", default=True)
    IS_PORT_OPEN = ResultProperty(name="is_port_open")

    Script_Title="Zoom"
    Script_Description = "A script which tests zoom"
    Script_Author = "SeeThru Networks"
    Script_Owner = "SeeThru Networks"

    def port_open(self):
        is_port_open = PortOpen().SetProperty(PortOpen.TARGET_HOST, "zoom.us").SetProperty(PortOpen.PORT, 443).Run().GetProperty(PortOpen.SUCCEEDED)
        self.SetProperty(self.IS_PORT_OPEN, is_port_open)
        return is_port_open

    # ------ Script Overrides ------
    def Script_Run(self): 
        # Checks if the port is open on the server
        if not self.port_open():
            return

        #Gets the google status page json
        try: page = HTTPGet().SetProperty(HTTPGet.URL, "https://14qjgk812kgk.statuspage.io/api/v2/status.json").Run()
        except: return

        try:
            #Gets the contents of the response
            contents = json.loads(page.GetProperty(HTTPGet.RESPONSE_CONTENT))

            self.SetProperty(self.ALL_OPERATIONAL, contents['status']['description'] == "All Systems Operational")
            self.SetProperty(self.ZOOM_INDICATOR, contents['status']['indicator'])
            self.SetProperty(self.ZOOM_DESCRIPTION, contents['status']['description'])
        except:
            self.SetProperty(self.VALID_JSON, False)

    def Script_Evaluate(self, result):
        result.SetStatus("green")
        result.SetMessage("")

        # Changes to red if the port is closed
        if not self.GetProperty(self.IS_PORT_OPEN):
            result.SetStatus("red")
            result.SetMessage("Could not connect to zoom.")
        
        #Changes to red if the status page couldn't be accessed
        elif not self.GetProperty(self.VALID_JSON):
            result.SetStatus("red")
            result.SetMessage("Could not load statistics")
        
        #Changes to amber if not all the zoom systems are operational
        elif not self.GetProperty(self.ALL_OPERATIONAL):
            result.SetStatus("amber")
            message = "There is a {} issue with zoom: '{}'".format(self.GetProperty(self.ZOOM_INDICATOR), self.GetProperty(self.ZOOM_DESCRIPTION))
            if len(message) > 256: message = "Not all systems are operational, head to status.zoom.us"
            result.SetMessage(message)