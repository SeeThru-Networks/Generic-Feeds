from SeeThru_Feeds.Model.Scripts.ScriptBase import ScriptBase
from SeeThru_Feeds.Model.Scripts.ScriptResult import ScriptResult
from SeeThru_Feeds.Model.Properties.Properties import FillableProperty, ResultProperty
from SeeThru_Feeds.Library.Components.Socket import PortOpen
from SeeThru_Feeds.Library.Components.HTTP import HTTPGet
import json

from SeeThru_Feeds.Model.Scripts.ScriptState import DefaultStates, State


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
        is_port_open = PortOpen().set_property(PortOpen.TARGET_HOST, "zoom.us").set_property(PortOpen.PORT, 443).run().get_property(PortOpen.SUCCEEDED)
        self.set_property(self.IS_PORT_OPEN, is_port_open)
        return is_port_open

    # ------ Script Overrides ------
    def script_run(self): 
        # Checks if the port is open on the server
        if not self.port_open():
            return

        #Gets the google status page json
        try: page = HTTPGet().set_property(HTTPGet.URL, "https://14qjgk812kgk.statuspage.io/api/v2/status.json").run()
        except: return

        try:
            #Gets the contents of the response
            contents = json.loads(page.get_property(HTTPGet.RESPONSE_CONTENT))

            self.set_property(self.ALL_OPERATIONAL, contents['status']['description'] == "All Systems Operational")
            self.set_property(self.ZOOM_INDICATOR, contents['status']['indicator'])
            self.set_property(self.ZOOM_DESCRIPTION, contents['status']['description'])
        except:
            self.set_property(self.VALID_JSON, False)

    def script_evaluate(self, result):
        result.set_status("green")
        result.set_message("")

        # Changes to red if the port is closed
        if not self.get_property(self.IS_PORT_OPEN):
            result.set_status("red")
            result.set_message("Could not connect to zoom.")
        
        #Changes to red if the status page couldn't be accessed
        elif not self.get_property(self.VALID_JSON):
            result.set_status("red")
            result.set_message("Could not load statistics")
        
        #Changes to amber if not all the zoom systems are operational
        elif not self.get_property(self.ALL_OPERATIONAL):
            result.set_status("amber")
            message = "There is a {} issue with zoom: '{}'".format(self.get_property(self.ZOOM_INDICATOR), self.get_property(self.ZOOM_DESCRIPTION))
            if len(message) > 256: message = "Not all systems are operational, head to status.zoom.us"
            result.set_message(message)
