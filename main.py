import subprocess, json, os
# Change directory to the root of the project
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Run setup
subprocess.call(["python", "./modules/setup.py"])
from modules.functions import UserDefinedFunction
from modules.UIHandler import UIManager
from modules.dataHandler import SavedData
from modules.configHandler import MainConfig


def getMenus():
    menu_file = open("./modules/menu-definition.json")
    obj = json.load(menu_file)
    menu_file.close()
    return obj


def populateMenus(handler, menu_obj):
    for uid in menu_obj["static"]:
        handler.createMenu(int(uid), menu_obj["static"][uid])
    for uid in menu_obj["dynamic"]:
        handler.createMenu(int(uid), menu_obj["dynamic"][uid], dynamic=True)
    for uid in menu_obj["selection"]:
        handler.createMenu(int(uid), menu_obj["selection"][uid], selection=True)

if __name__ == "__main__":

    # Initialization of handlers
    cfg = MainConfig()
    dh = SavedData()
    user_function = UserDefinedFunction("sen(t)",cfg)
    user_function.set_title_hardcoded("Ejemplo")
    UI_Handler = UIManager(user_function,cfg,dh)
    populateMenus(UI_Handler, getMenus())
    # Main loop 
    while True:
        UI_Handler.mainLoop()
