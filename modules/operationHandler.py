import uuid
import modules.plotter as plot
from modules.functions import UserDefinedFunction
from modules.configHandler import MainConfig
import numpy as np

try:
    import readline
except:
    pass

class CompoundFunction:
    def __init__(self, cfg, *functions: UserDefinedFunction):
        self.type = "COMPOUND"
        self.cfg = cfg
        self.functions = functions
        self.X_Axis = list()
        self.Y_Axis = list()
        self.result_Y_Axis = list()
        self.expr = str()
        self.operand = "&"
        self.updateExpr()
        self.__getIndividualValues()

    def __getIndividualValues(self):
        self.X_Axis = []
        self.Y_Axis = []
        for function in self.functions:
            values = function.getValues()
            self.Y_Axis.append(*values[:-1])
            self.X_Axis = values[-1]

    def executeOperation(self,operation):
        if operation == 0: # Clear, just show two graphs
            self.operand = "&"
            self.result_Y_Axis = []
            self.Y_Axis.pop(0)

        elif operation == 1: # Sum, add the two functions
            self.operand = "+"
            self.result_Y_Axis = []
            for i in range(len(self.Y_Axis[0])):
                self.result_Y_Axis.append(self.Y_Axis[0][i]+self.Y_Axis[1][i])
            self.Y_Axis.insert(0,self.result_Y_Axis)

        elif operation == 2: # Substract
            self.operand = "-"
            self.result_Y_Axis = []
            for i in range(len(self.Y_Axis[0])):
                self.result_Y_Axis.append(self.Y_Axis[0][i]-self.Y_Axis[1][i])
            self.Y_Axis.insert(0,self.result_Y_Axis)

        elif operation == 3: # Product, multiply both functions
            self.operand = "×"
            self.result_Y_Axis = []
            for i in range(len(self.Y_Axis[0])):
                self.result_Y_Axis.append(self.Y_Axis[0][i]*self.Y_Axis[1][i])
            self.Y_Axis.insert(0,self.result_Y_Axis)

        else:              # Convolute, "same" convolution between both functions
            self.operand = "*"
            self.result_Y_Axis = []
            self.result_Y_Axis = np.convolve(self.Y_Axis[0], self.Y_Axis[1], mode="same") / self.cfg.cfg["XRes"]
            self.Y_Axis.insert(0,self.result_Y_Axis)

        self.updateExpr()


    def updateExpr(self):
        title_list = list()
        for func in self.functions:
            if type(func) == 'CompoundFunction':
                title_list.append(f"({func.title})")
            else:
                title_list.append(func.title)
        self.expr = f" {self.operand} ".join(title_list)
        self.title = self.expr
        self.raw_expression = self.expr

    def getValues(self):
        self.__getIndividualValues()
        if self.operand != "&":
            return np.array([self.result_Y_Axis, self.X_Axis])
        return (*self.Y_Axis,self.X_Axis)

    def show(self):
        plot.show(plot.setup((*self.Y_Axis,self.X_Axis),self.title,"y",self.cfg,labels=[self.functions[0].raw_expression,self.functions[1].raw_expression])[0])

    def readInput(self,prompt):
        if self.cfg.cfg["UNIX"]:
                
            readline.set_startup_hook(lambda: readline.insert_text(prompt))  # Set initial prompt
            try:
                return input()
            finally:
                readline.set_startup_hook()  # Reset prompt
        
        else:
            return input("~~>  ")

    def set_title(self):
        new_title = self.readInput(self.title)
        if new_title == "":
            return False
        self.title = re.sub(self.REGEX_SANITIZING_FILTER, "", new_title)
        return (True,new_title)

    def __str__(self):
        return f"Se tiene un total de {len(self.functions)} expresiones juntas, las cuales son:\n {' y '.join([x.raw_expression for x in self.functions])}\nLa operación a ejecutar es {self.operand}"

if __name__=="__main__":
    cfg = MainConfig()
    funcion1 = UserDefinedFunction("e^-t*u(t)",cfg)
    funcion1.set_title_hardcoded("Exponencial")
    funcion2 = UserDefinedFunction("sen(10*t)",cfg)
    funcion2.set_title_hardcoded("Seno de 10t")

    mix = CompoundFunction(cfg,funcion1,funcion2)
    mix.executeOperation(3)
    mix.show()
    # funcion3 = UserDefinedFunction("p(-1,1)",cfg)
    # funcion3.set_title_hardcoded("Pulso de -1 a 1")
    # mixedMix = CompoundFunction(cfg,mix,funcion3)
    # mixedMix.executeOperation(1)
    # mixedMix.show()
    mix.executeOperation(0)
    mix.show()