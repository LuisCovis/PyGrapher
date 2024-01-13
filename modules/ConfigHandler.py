import json
from matplotlib import ticker
import re

# ConfigHandler is the resposible for retrieving the configuration from the json file
# and any other modification to that file.

class MainConfig:
    def __init__(self, cfg):
        
        self.color =       dict(cfg["color_palette"])
        self.cfg   =       dict(cfg["global"])
        self.minorLn =     dict(cfg["grid_cfg"]["minor"])
        self.majorLn =     dict(cfg["grid_cfg"]["major"])
        self.axis_line =   dict(cfg["grid_cfg"]["axis_line"])
        self.locator =     cfg["grid_cfg"]["locator"]
        self.maj_locator = cfg["grid_cfg"]["maj_locator"]

    def reloadConfig(self,cfg_object):
        self.__init__(cfg_object)
    
    def saveConfig(self):
        cfg_file = open("config.json", "w")
        cfg_file.write(self.__toJSON())
        cfg_file.close()

    def translateLocator(self,key):

        locator = re.search(r"([A-Z])\w+",key)
        if locator:
            locator = locator.group()
        else:
            print("Error en la selección de locator")


        p = re.search(r"(?<=\().*?(?=\))",key).group()
        if p:
            p = list(map(float,p.split(",")))
        else:
            p = []


        loc_dictionary = {
                    "MultipleLocator": ticker.MultipleLocator(*p),
                    "AutoLocator": ticker.AutoLocator(),
                    "MaxNLocator": ticker.MaxNLocator(*p),
                    "LinearLocator": ticker.LinearLocator(*p),
                    "LogLocator": ticker.LogLocator(*p),
                    "NullLocator": ticker.NullLocator(),
                }
        return loc_dictionary[locator]

    def __toJSON(self):
        return json.dumps({"color_palette":self.color,
                "global": self.cfg,
                "grid_cfg": {
                    "minor":       self.minorLn,
                    "major":       self.majorLn,
                    "axis_line":   self.axis_line,
                    "locator":     self.locator,
                    "maj_locator": self.maj_locator
                    }
                }, indent=4)

    def __str__(self):
        return str(self.__toJSON)
