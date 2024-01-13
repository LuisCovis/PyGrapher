import os
import sqlite3
import json
import time
import re
from configHandler import MainConfig
# setup ensures the application will run without problems since the first launch.
# Upon launch, setup.py:
#   Updates the UNIX and EXPORT_PATH parameters within config.json
#   Checks if matplotlib and numpy are installed
#   Checks if the database already exists, if it doesn't, creates the file and the needed tables

def getConfig():
    cfg_file = open("config.json") # usar PATH absoluto
    obj = json.load(cfg_file)
    cfg_file.close()
    return obj
cfg_obj = MainConfig(getConfig())
cfg = cfg_obj.cfg

print("Detectando ambiente de ejecución")
if type(cfg["UNIX"]!=bool):
    cfg["UNIX"] = True if os.name != "nt" else False
    print("os detectado como ", os.name)
else:
    print("Ya se conoce")

print("Creando carpeta de salida.")
if cfg["EXPORT_PATH"]=="null":
    if re.match(r"/data/data/com\.termux/.",os.getcwd()):
        cfg["EXPORT_PATH"] = "/data/data/com.termux/files/home/storage/dcim/Graficas/"
        os.system(f"mkdir {cfg['EXPORT_PATH']}")
        print("Creada una carpeta para termux en DCIM")
    else:
        cfg["EXPORT_PATH"] = os.getcwd()+"/Graficas/" if cfg["UNIX"] else os.getcwd()+"\\Graficas\\"
        os.system(f"mkdir {cfg['EXPORT_PATH']}")
        print("Creada una carpeta de salida exitosamente")
else:
    print("Ya existe una carpeta")

try:
    import matplotlib
    import numpy
except:
    print("No se encontraron algunas dependencias, asegúrese de instalar numpy y matplotlib")
    input()
    exit()

print("Verificando base de datos")
if not os.path.exists("./modules/vault.db"):
    print("Creando nueva base de datos...")
    con = sqlite3.connect("./modules/vault.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE history(expr)")
    cur.execute("CREATE TABLE vault(expr)")
    con.close()
    print("Base de datos creada.")
cfg_obj.saveConfig()
