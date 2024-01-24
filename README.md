# PyGrapher
El proyecto PyGrapher consta de una aplicación que sirva de interfaz entre el usuario y la librería MatPlotLIb con el propósito de graficar funciones polinómicas y trigonométricas en el dominio R²
La aplicación cuenta con una interfaz híbrida entre CLI y GUI donde la información se muestra en pantalla de manera dinámica y la navegación se realiza a través de comandos de un solo caracter también mostrados en pantalla. 
También se cuenta con una base de datos para hacer más fácil ver y editar funciones introducidas anteriormente.

## Features
* Compatibilidad con Windows y Linux
* Posibilidad de graficar:
  *   Polinomios
  *   Operadores trigonométricos
  *   Valor absoluto
  *   Escalón unitario (uso: u(t-t0)
  *   Pulso (u(t-t0)-u(t-t1) donde t1>t0, uso: p(t0,t1)
* Interfaz Gráfica.
* Colores dentro de la terminal.
* Edición natural dentro de la función builtin input(), lo que permite hacer uso de las flechas en el teclado, copiar y pegar.
* Archivo de configuración comprensible en formato JSON que puede ser editado manualmente o mediante la aplicación de forma temporal.
* Permanencia de las funciones en una base de datos
  *   Historial que guarda hasta 5 funciones
  *   "Vault" sin límite de funciones para un guardado más permanente y proximamente para realizar operaciones entre funciones.
 
## TO-DO List
* Permitir más de un valor absoluto en las funciones
* ~~Asegurar compatibilidad con Windows~~ DONE
* Agregar la opción de comparar 2 funciones en un mismo gráfico
* Agregar la opción de operar 2 funciones
  * Suma
  * Resta
  * Multiplicación
  * Convolución

# Documentación
El proyecto está dividido en distintos módulos, cada uno con su función específica
## setup.py
Script encargado de configurar el ambiente de ejecución de la app, manteniendo la configuración acorde con el sistema operativo y creando la base de datos junto con las tablas necesarias

## configHandler.py
Contiene la clase <MainConfig> la cual maneja todos los cambios y solicitudes al archivo config.json ubicado en la carpeta raíz
### MainConfig(cfg: dict) --> configHandler.MainConfig Object
Para iniciar el config handler, es necesario crear una instancia nueva y pasar como parámetro el diccionario obtenido al procesar config.json.
Utilizando el modulo builtin "json" de python, se puede obtener este diccionario de la siguiente manera
``` python
def getConfig():
    cfg_file = open("config.json") # usar PATH absoluto
    obj = json.load(cfg_file)
    cfg_file.close()
    return obj
```

### MainConfig.reloadConfig(cfg_object) --> None
Vuelve a ejecutar __init__ para actualizar la instancia con la nueva configuración ubicada en config.json

### MainConfig.saveConfig() --> None
Sobreescribe la configuración temporal actual al archivo config.json

### MainConfig.translateLocator(key: str) --> matplotlib.ticker object
config.json contiene información necesaria para las gráficas de matplotlib, esta función hace el cambio de un string guardado en la configuración al objeto ticker de matplotlib que se encarga de las divisiones y sub divisiones de los ejes.

## DataHandler.py
Es la interfaz entre la aplicación y la base de datos sqlite3. Al tratarse de un proyecto pequeño, las bases de datos de prototipado SQLite3 son suficientes.
Este archivo define el objeto SavedData, utilizado para obtener y escribir datos en la base de datos ubicada en el directorio 'modules'

### SavedData() --> dataHandler.SavedData Object
No requiere parámetros para crear una nueva instancia. Este objeto se conecta a la base de datos al ser iniciado.

### SavedData.slicePages(_list: list) --> list
Limita la cantidad de información que se muestra en las entradas del vault a 5 elementos por página. Retorna una lista con las listas de longitud igual o menor a 5 sobre la cual se puede iterar para mostrar los distintos elementos de cada página. La cantidad de elementos por página se encuentra en el atributo SavedData.objects_per_page

### SavedData.getHistory() --> list
Realiza un query a la base de datos para retornar todos los elementos de la tabla 'history'

### SavedData.getVault() --> list
Realiza un query a la base de datos para retornar todos los elementos de la tabla 'vault' y a su vez retorna la lista anidada con las páginas

### SavedData.updateHistory(entry: str) --> None
Guarda la expresión 'entry' en el historial y mantiene la cantidad de objetos guardados igual al atributo SavedData.historyLenght

### SavedData.addToVault(entry: str) --> None
Agrega la expresión 'entry' al Vault

### SavedData.deleteVaultEntry(entry: str) --> None
Busca la expresión 'entry' en la base de datos y la elimina

### SavedData.printTables() --> None
Imprime todas las tablas presentes en la base de datos, para propósitos de testing.

### SavedData.exit() --> None
Cierra la conexión a la base de datos de forma segura

## functions.py
El objeto UserDefinedFunction es donde se guarda, evalúa y obtienen los valores de toda las funciones que se van a graficar.

### UserDefinedFunction(expression: str, cfg: MainConfig object):
Se debe iniciar con una expresión. Al momento de declarar el objeto, no se evalúa la expresión, sino que se modifica la expresión para que pueda ser evaluada por python.
Por ejemplo, la expresión <b>cos(pi\*t) + |t| - 1</b> NO puede ser evaluada por python directamente, sin embargo, esa expresión es entendible para el usuario y para mostrarla como información, se guarda en el atributo UserDefinedFunction.raw_expression. Sin embargo, el atributo UserDefinedFunction.expression toma raw_expression y a través de filtros Regex, se puede convertir en una expresión válida para python:</br>
<b>UserDefinedFunction.raw_expression:  </b> cos(pi\*t) + |t| - 1 </br>
<b>UserDefinedFunction.expression:  </b> math.cos(3.141592653589793*t) + abs(t) - 1 </br>

### UserDefinedFunction.getValues() --> numpy.array Object
Primero genera un array para los valores horizontales con valores espaciados uniformemente ubicados en el rango especificado en la configuración, luego itera sobre este array para crear un segundo array para los valores de las ordenadas. La función builtin eval() permite pasar referencias a funciones y variables que no están en el scope del eval para que la expresión se evalúe correctamente, es así como se toma 't' como variable independiente y las funciones personalizadas del pulso, escalón e impulso son tomadas como válidas.

### UserDefinedFunction.show() --> None
Llamada a plotter para mostrar la función de forma gráfica con la utilidad que brinda matplotlib. Si se cuenta con interfaz gráfica, este método permite hacer zoom y desplazar la gráfica para un mejor análisis.

### UserDefinedFunction.save() --> None
Llamada a plotter para guardar la gráfica en un pdf dentro del directorio 'Graficas'. Se guarda en un pdf debido a que la gráfica no será rasterizada sino vectorial, de esta forma no se pierde detalle alguno al hacer zoom.

### UserDefinedFunction.readInput(prompt: str) --> class 'builtin_function_or_method'
Este método es el responsable de dar una función mejorada a la función builtin input() utilizando el módulo también incluído con python, readline.
El método readInput en realidad retorna la función input() la cual luego retorna el string introducido.

### UserDefinedFunction.set_title() --> None
Llama el método readInput para establecer un nuevo título que será visible tanto en el pdf de la gráfica como en el nombre del archivo.

### UserDefinedFunction.set_expression() --> bool
A través del método readInput intenta establecer una nueva expresión para el objeto UserDefinedFunction, Si el cambio es exitoso retorna True, de lo contrario False.

## plotter.py
Este módulo se encarga de manipular matplotlib y configurar las gráficas a partir de la configuracion

### setup(data: np.array, title: str, y_title: str, cfg: MainConfig object) --> tuple
Esta función configura la gráfica a mostrar/guardar. Retorna una tupla con las instancias de plot y figure pre configuradas.

### save(plt: module, fig: matplotlib.figure.Figure, title: str, cfg: configHandler.MainConfig) --> None
Guarda la gráfica en un archivo PDF ubicado en el directorio /Graficas

### show(plt: module) --> None
Muestra la gráfica.

