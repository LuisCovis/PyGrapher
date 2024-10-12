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
    cfg
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

    ## Manage multiple plots
    for graphID, graph in enumerate(data[:-1]):
        ax.plot(graph, data[-1], color=cfg.color["plot_line"][graphID])

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
