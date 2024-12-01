import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

# plotSetup :: List[Float[]], Str, Str -> Tuple
# Takes a list of XY values and outputs the plot and figure objects
# Aditionally takes text data for the title and axis label
def setup(
    data,
    title,
    y_title,
    cfg,
    labels=None
):
    _xlim = cfg.cfg["XPlotRange"]
    _ylim = cfg.cfg["YPlotRange"]
    ## Plot call and trimming
    fig, ax = plt.subplots()
    ax.set_xlim(*_xlim)
    ax.set_ylim(*_ylim)

    ## Main colors
    fig.set_facecolor(cfg.color["background"])
    ax.set_facecolor(cfg.color["foreground"])

    ## Discrete functions
    is_discrete = True if cfg.cfg["XRes"] == 1 else False
    def quantizeTime(x,y,colorID=0):
        if is_discrete:
            ax.stem(x,y, linefmt=cfg.color["plot_line"][colorID])

    ## Manage multiple plots
    if len(data[:-1]) < 3:
        for graphID, graph in enumerate(data[:-1]):
            ax.plot(data[-1], graph, linestyle='solid'*(not is_discrete), color=cfg.color["plot_line"][graphID])
            quantizeTime(data[-1],graph,colorID=graphID)
    else:
        for graphID, graph in enumerate(data[1:-1]):
            ax.plot(data[-1], graph, linestyle='dashed', linewidth=0.5, color=cfg.color["plot_line"][graphID+1])
        ax.plot(data[-1], data[0], linestyle='solid'*(not is_discrete),color=cfg.color["plot_line"][0])
        quantizeTime(data[-1],data[0])
        ax.legend([labels[0],labels[1],"Resultado"])

    ## Grid, axes and locators
    ax.grid(**cfg.minorLn)
    ax.grid(**cfg.majorLn)
    ax.axvline(**cfg.axis_line)
    ax.axhline(**cfg.axis_line)
    ax.xaxis.set_minor_locator(cfg.translateLocator(cfg.locator))
    ax.xaxis.set_major_locator(cfg.translateLocator(cfg.maj_locator))
    ax.yaxis.set_minor_locator(cfg.translateLocator(cfg.locator))
    ax.tick_params(axis='x', colors=cfg.color["text_color"])    
    ax.tick_params(axis='y', colors=cfg.color["text_color"])  
    ax.spines['left'].set_color(cfg.color["text_color"])        
    ax.spines['bottom'].set_color(cfg.color["text_color"]) 

    ## Labels
    ax.set_title(title, size=18, color=cfg.color["text_color"])
    ax.set_xlabel("t", loc="right", weight="bold", color=cfg.color["text_color"])
    ax.set_ylabel(y_title, loc="top", rotation="horizontal", weight="bold", color=cfg.color["text_color"])
    return (plt,fig)

def save(plt,fig,title,cfg):
    fig.savefig(f'{cfg.cfg["EXPORT_PATH"]}{title}.pdf')

def show(plt):
    plt.show()
