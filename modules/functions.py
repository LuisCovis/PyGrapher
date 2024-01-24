import re
import math
try:
    import readline
except:
    pass
import numpy as np
import modules.plotter as plot

# Functions.py is where the functions are evaluated and stored.
# Each UserDefinedFunction requires an expression upon creation, an 'expression' is just a
# string that defines a function, this string is passed through multiple REGEX substitutions
# to end up with an expression that can actually be parsed by python using the buitin eval() function.

class UserDefinedFunction:
    def __init__(self, expression,cfg):
        self.REGEX_SANITIZING_FILTER = "|\\".join(cfg.cfg["nmfilter"])
        self.REGEX_FUNCTIONS = "|".join(cfg.cfg["function_list"])
        self.cfg = cfg
        self.expression = re.sub(self.REGEX_SANITIZING_FILTER, "", expression)
        self.raw_expression = self.expression
        self.X_Axis = list()
        self.Y_Axis = list()
        self.title = "grafica"
        self.__findAbsoluteValues()
        self.__processSignals()
        self.__processFunctions()
        self.__processConstants()

    def __findAbsoluteValues(self):
        PATTERN = "(?<=\|).*?(?=\|)" # Fix BUG
        self.expression = re.sub(
            PATTERN, lambda match: f"abs({match[0]})", self.expression
        )
        self.expression = re.sub("\|", "", self.expression)
        return

    def __processFunctions(self):
        self.expression = re.sub(  # Catches sqrt, sin, cos, tan, asin, acos, atan and log
            self.REGEX_FUNCTIONS, lambda match: f"math.{match[0]}", self.expression
        )
        self.expression = re.sub(  # Only catches sen and converts it to the valid function sin
            "sen", "math.sin", self.expression
        )
        return

    def __processConstants(self):
        self.expression = re.sub("e", str(math.e), self.expression)
        self.expression = re.sub("pi", str(math.pi), self.expression)
        self.expression = re.sub("\^", "**", self.expression)
        return

    def __processSignals(self):
        EXPRESSION = "((?<=u\()|(?<=p\()|(?<=d\()).*?(?=\))"
        self.expression = re.sub(
            EXPRESSION, lambda match: f"'{match[0]}',i", self.expression
        )

    # Unitary step function
    def __unitStep(self,step_expression: int, index: int) -> int:  # Step function
        displacement = -eval(step_expression, {}, {"t": 0})
        t_isPositive = (eval(step_expression, {}, {"t": 1}) + displacement) > 0
        zero_index = self.__getZero_index()
        if t_isPositive:
            return 0 if index <= zero_index + displacement * self.cfg.cfg["XRes"] else 1
        return 1 if index <= zero_index + displacement * self.cfg.cfg["XRes"] else 0

    # Pulse function: "u(t-a)-u(t-b)" where a < b
    def __pulse(self,pulse_range: int, index: int, *args) -> int:  # Pulse signal
        limits = tuple(map(float, str(pulse_range).split(",")))
        zero_index = self.__getZero_index()
        return (
            1
            if zero_index + limits[0] * self.cfg.cfg["XRes"] <= index
            and index < zero_index + limits[1] * self.cfg.cfg["XRes"]
            else 0
        )

    # Impusle function
    def __dirac(self,dirac_expression: int, index: int) -> int:  # Dirac delta
        displacement = -eval(dirac_expression, {}, {"t": 0})
        zero_index = self.__getZero_index()
        return 0 if index != zero_index + displacement * self.cfg.cfg["XRes"] else self.cfg.cfg["XRes"]

    def __getZero_index(self):
        return -self.cfg.cfg["XPlotRange"][0] * self.cfg.cfg["XRes"]

    def getValues(self):
        ###cfg.updateRange()
        self.X_Axis = [
            i / self.cfg.cfg["XRes"]
            for i in range(self.cfg.cfg["XRes"] * self.cfg.cfg["XPlotRange"][0], self.cfg.cfg["XRes"] * self.cfg.cfg["XPlotRange"][1] + 1)

        ]
        self.Y_Axis = []
        c = 0
        for t in self.X_Axis:
            evaluation = (
                self.expression,
                {},
                {"i": c, "t": t, "math": math, "p": self.__pulse, "u": self.__unitStep, "d": self.__dirac, "np": np},
            )
            try:
                self.Y_Axis.append(eval(*evaluation))
            except ZeroDivisionError:
                self.Y_Axis.append(2**15)

            except ValueError:
                self.Y_Axis.append(0)

            except IndexError:
                self.Y_Axis.append(self.Y_Axis[-1])
            c += 1

        return np.array([self.X_Axis, self.Y_Axis])

    def show(self):
        plot.show(plot.setup(self.getValues(),self.title,"y",self.cfg)[0])

    def save(self):
        plot.save(*plot.setup(self.getValues(),self.title,"y",self.cfg),self.title,self.cfg)

    def set_title(self):
        new_title = self.readInput(self.title)
        if new_title == "":
            return False
        self.title = re.sub(self.REGEX_SANITIZING_FILTER, "", new_title)
        return True
    
    def readInput(self,prompt):
        if self.cfg.cfg["UNIX"]:
                
            readline.set_startup_hook(lambda: readline.insert_text(prompt))  # Set initial prompt
            try:
                return input()
            finally:
                readline.set_startup_hook()  # Reset prompt
        
        else:
            return input("~~>  ")

    def set_expression(self,predefined_expression=None):
        if predefined_expression:
            new_expression = predefined_expression
        else:
            new_expression = self.readInput(self.raw_expression)
            
        # Validate expression
        if new_expression == "":
            return True
        try:
            self.__init__(new_expression,self.cfg)
            self.getValues()
            return True
        except:
            return False

    def __str__(self):
        return f"La expresión inicial es {self.raw_expression}, que se convirtió a {self.expression}. actualmente el eje X tiene {len(self.X_Axis)} números, mientras que el eje Y tiene {len(self.Y_Axis)}"

