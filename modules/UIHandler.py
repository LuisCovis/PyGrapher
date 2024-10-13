import os
from modules.configHandler import MainConfig
try:
    import readline
except:
    pass
import json

# UIHandler: manages both the application flow and the UI.
# UIManager is the core of the application, There are three types of menu
#   MenuObject: Its main purpose is tho allow navigation and give info.
#   EditScreen: It prints some info but expect some input to take over the flow.
#   SelectionMenu: Similar to MenuObject, however its contents are dynamic and perform actions
#       upon selecting an option.
# All the menus are written in a json file, each with an Unique ID and separated by type of menu.


class UIManager:
    class MenuObject:
        def __init__(self, handler, title, info, keys, opt={}):
            self.handler = handler
            self.title = title
            self.info = info
            self.keys = keys
            self.keys["Q"] = ["Volver", "BCK"]
            self.optional = opt

        def green(self, string):
            return f"\033[32m{string}\033[39m"

        def manageExtraInfo(self):
            if not self.optional:
                return
            extra_text = list(self.optional.keys())[0]
            print(
                extra_text.format(
                    *list(map(self.green, (map(eval, self.optional[extra_text]))))
                )
            )

        def show(self):
            self.handler.titleBox(self.title)
            print(self.info)
            self.handler.printSuccess()
            print(self.handler.lastErr)
            self.manageExtraInfo()
            print("")
            for key in self.keys:
                print(f"[{key}] {self.keys[key][0]}")
            print("")
            return input("Opción:  ")

    class EditScreen:
        def __init__(self, handler, title, info, aux, prompt, args):
            self.handler = handler
            self.title = title
            self.info = info
            self.aux = aux
            self.prompt = prompt
            self.args = args

        def show(self):
            self.handler.titleBox(self.title)
            print(self.info)
            print(self.aux.format(*list(map(eval, self.args))))
            print(self.handler.lastErr)
            print("")
            return "Q"

    class SelectionMenu:
        def __init__(self, handler, title, specialAction):
            self.handler = handler
            self.maxPages = 0
            self.maxLen = 0
            self.page = 0
            self.title = title
            self.desc = "Introduce el numero correspondiente para la expresion deseada"
            self.keys = dict()
            self.max = 5
            self.specialAction = specialAction
            self.__update()

        def __update(self):
            if int(self.specialAction) % 2 == 0:
                self.iterable = self.handler.dh.getHistory()
                self.iterable.reverse()
            else:
                vault = self.handler.dh.getVault()
                vault.reverse()
                self.maxPages = len(vault) - 1
                self.iterable = vault[self.page]

        def __populateKeys(self):
            self.__update()
            self.keys = {}
            for i, element in enumerate(self.iterable):
                self.keys.update(
                    {str(i): [element, f"AS{self.specialAction}:{i}"]}
                )
            if self.paginated:
                self.keys.update({"S": ["Siguiente pagina", "AC9"]})
                self.keys.update({"A": ["Pagina Anterior", "AC10"]})
            self.keys.update({"Q": ["Volver", "BCK"]})

        def nextPage(self):
            if self.page == self.maxPages:
                self.handler.Error("Ya se encuentra en la última página.")
                return
            self.page += 1

        def prevPage(self):
            if self.page == 0:
                self.handler.Error("Ya se encuentra en la primera página.")
                return
            self.page -= 1

        def show(self):
            self.paginated = eval("self.maxPages != 0")

            self.handler.titleBox(self.title)
            print(self.desc)
            if self.paginated:
                print(f"Página {self.page+1} de {self.maxPages+1}")
            print(self.handler.lastErr)
            self.__populateKeys()
            for key in self.keys:
                if key.isnumeric():
                    print(f"[{key}] ({self.keys[key][0][1]}) {self.keys[key][0][0]}")
                else:
                    print(f"[{key}] {self.keys[key][0]}")
            print("")
            return input("Opción:  ")

    def __init__(self, user_function,cfg,dh):
        self.cfg = cfg.cfg
        self.debug = self.cfg["DEBUG_MODE"]
        self.unix = self.cfg["UNIX"]
        self.dh = dh
        self.function = user_function
        self.current_action = 0
        self.lastErr = ""
        self.menus = dict()
        self.pointer = 0
        self.stack = [0]
        self.infoQueue = list()
        self.successQueue = list()

    def __clearError(self):
        self.lastErr = ""

    def __exitAction(self, clear_last_error=True):
        if clear_last_error:
            self.lastErr = ""
        self.current_action = 0
        self.decode("BCK")

    def titleBox(self, title):
        title_len = len(title)
        margin = 5
        corner = "+"
        horizontal = "-"
        vertical = "|"
        print(corner + horizontal * (title_len + 2 * margin) + corner)
        print(vertical + " " * margin + title + " " * margin + vertical)
        print(corner + horizontal * (title_len + 2 * margin) + corner)

    def clear(self):
        if self.unix:
            os.system("clear")
        else:
            os.system("cls")

    def success(self, msg):
        self.successQueue.append(msg)

    def printSuccess(self):
        try:
            msg = self.successQueue.pop()
        except:
            return
        print(f"\033[32m[!] {msg}\033[39m")

    def Info(self, msg, desc):
        self.infoQueue.append(f"{msg} <~~ {desc}")

    def printInfo(self):
        if self.debug:
            for msg in self.infoQueue:
                print(f"\033[33m[!] {msg}\033[39m")
            self.infoQueue = []

    def Error(self, msg):
        self.lastErr = f"\033[31m[⚠] {msg}\033[39m"

    def createMenu(self, UID, dataList, dynamic=False, selection=False):
        if dynamic:
            newUI = UIManager.EditScreen(self,*dataList)

        elif selection:
            newUI = UIManager.SelectionMenu(self,*dataList)

        else:
            newUI = UIManager.MenuObject(self,*dataList)
            if UID == 0:
                newUI.keys["Q"] = ["\033[31mSalir\033[39m", "EXT"]
        self.menus[UID] = newUI

    def selectMenu(self, ptr):
        self.stack.append(ptr)

    # The navigation is based on codes, each action or valid key returns a code:
    #   EXT: Exit code, closes database and exits the program
    #   BCK: Back code, pops a pointer from the stack, so the cursor will be set to the previous ID
    #   Jxx: Jump code, navigates to the menu with the ID specified in the end of the code.
    #       JM0:  Normal jump: jumps to MenuObject with ID 0
    #       JE10: Edit jump: jumps to the EditScreen with ID 10
    #   Axx: Action code, executes an action specified at the end of the code
    #       AC1: Normal action: executes the action() number 1
    #       AS3:0: Special action: executes the specialAction() number 3 with an ID parameter 0
    #       Special actions are related to data handling and SelectMenus
    def decode(self, code):
        if code == "EXT":
            self.dh.exit()
            exit()
        elif code == "BCK":
            self.stack.pop()
        elif code[0] == "J":
            self.selectMenu(int(code[2:]))
            if code[1] == "E":
                return code[2:]
        elif code[0] == "A":
            if code[1] == "S":
                parsedCode = code.split(":")
                self.specialAction(parsedCode[0][2:], parsedCode[1])
                return 0
            self.action(int(code[2:]))
        else:
            self.Error("Esa funcionalidad aún no está implementada.")
        return 0

    def readInput(self, prompt):
        if self.unix:
            readline.set_startup_hook(
                lambda: readline.insert_text(prompt)
            )  # Set initial prompt
            try:
                return input()
            finally:
                readline.set_startup_hook()  # Reset prompt
        else:
            return input("~~>  ")

    def changeRange(self, rangeConfig):
        try:
            old_xRange = ",".join(map(str, self.cfg[rangeConfig]))
            new_xRange = self.readInput(old_xRange)
            new_xRange = new_xRange.split(",")
            if new_xRange == "":
                return True
            elif len(new_xRange) != 2:
                raise Exception("Se deben proporcionar exactamente 2 elementos.")
            else:
                self.cfg[rangeConfig] = list(map(int, new_xRange))
                return True
        except Exception as e:
            self.Error(
                f"Hubo un error asignando el nuevo rango. Intenta de nuevo o deja vacío para salir sin guardar  {e}"
            )
            return False

    def specialAction(self, action_code, selectedID):
        current_menu = self.menus[self.pointer]
        items = current_menu.iterable
        if action_code == "1":  # Select expression from vault
            if not self.function.set_expression(items[int(selectedID)][0]):
                self.Error(
                    "Ocurrió un error al seleccionar la expresión, puede que sea inválida."
                )
            else:
                self.lastErr = ""
            self.function.set_title_hardcoded(items[int(selectedID)][1])
            self.__exitAction(False)
            return
        if action_code == "2":  # Select expression from history
            if not self.function.set_expression(items[int(selectedID)][0]):
                self.Error(
                    "Ocurrió un error al seleccionar la expresión, puede que sea inválida."
                )
            else:
                self.lastErr = ""
            self.function.set_title_hardcoded(items[int(selectedID)][1])
            self.__exitAction(False)
            return
        if action_code == "3":  # Delete vault expression
            self.dh.deleteVaultEntry(items[int(selectedID)][0])
            self.__exitAction()
            return
        if action_code == "4":  # Save history expression to vault
            self.dh.addToVaultFromHistory(items[int(selectedID)])
            self.__exitAction()
            return

    def action(self, action_number):
        if action_number == 1: # Plot Show
            self.function.show()
            return

        if action_number == 2: # Confirm and save
            self.function.save()
            self.success(
                f"Gráfica guardada en {self.cfg['EXPORT_PATH']} satisfactoriamente."
            )
            return

        if action_number == 3: # Save to database
            self.dh.addToVault(self.function.raw_expression,self.function.title)
            return

        if action_number == 4: # Edit title
            sw = True
            while sw:
                self.reDraw()
                title_operation = self.function.set_title()
                sw = not title_operation[0]
                newTitle = title_operation[1]
                if sw:
                    self.Error("Introduce un título válido.")
            self.dh.updateColumn("history",self.function.raw_expression,"name",newTitle)
            self.__exitAction()
            return

        if action_number == 5: # XRange config
            isChanged = False
            while not isChanged:
                self.reDraw()
                isChanged = self.changeRange("XPlotRange")
            self.function.getValues()
            self.__exitAction()
            return

        if action_number == 6: # YRange config
            isChanged = False
            while not isChanged:
                self.reDraw()
                isChanged = self.changeRange("YPlotRange")
            self.__exitAction()
            return

        if action_number == 7: # Edit function
            lastExpr = self.function.raw_expression
            isNotChanged = True
            while isNotChanged:
                self.reDraw()
                isNotChanged = not self.function.set_expression()
                if isNotChanged:
                    self.Error(
                        "Hubo un error con la función introducida. Intenta nuevamente o deja vacío para salir"
                    )
                else:
                    if self.function.raw_expression != lastExpr:
                        self.dh.updateHistory(self.function.raw_expression,self.function.title)
            self.__exitAction()
            return

        if action_number == 8: # Edit sample rate
            sw = True
            old_XRes = self.cfg["XRes"]
            while sw:
                self.reDraw()
                try:
                    new_xRes = self.readInput(old_XRes)
                    if new_xRes == "":
                        sw = False
                    else:
                        self.cfg["XRes"] = int(new_xRes)
                        sw = False
                except Exception as e:
                    self.Error(
                        f"Hubo un error asignando el nuevo sample rate. Intenta de nuevo o deja vacío para salir sin guardar  {e}"
                    )
            self.__exitAction()
            return

        if action_number == 9: # Next page of the SelectionMenu
            current_menu = self.menus[self.pointer]
            current_menu.nextPage(self)
            return

        if action_number == 10: # Previous page of the SelectionMenu
            current_menu = self.menus[self.pointer]
            current_menu.prevPage(self)
            return

        # Default option
        self.Error("Acción no reconocida.")

    def reDraw(self):
        self.clear()
        current_menu = self.menus[self.pointer]
        current_menu.show()
        print(self.menus[self.pointer].prompt)

    def mainLoop(self):
        if self.debug:
            input("continue")
        self.clear()
        self.pointer = self.stack[-1]  # Update pointer
        current_menu = self.menus[self.pointer]  # Select menu to display
        value = current_menu.show()  # Display menu and store the value (Code)

        if self.current_action:
            self.action(int(self.current_action))
            # self.decode("BCK")
            return
        self.__clearError()

        if value.upper() not in current_menu.keys:
            self.Error("Por favor, selecciona una opción de la lista.")
        else:
            self.current_action = self.decode(current_menu.keys[value.upper()][1])

