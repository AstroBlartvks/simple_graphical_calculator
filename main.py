import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from Form import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import ast
import copy
import math
from math import sin,cos,tan,hypot


def convertExpr2Expression(Expr):
        Expr.lineno = 0
        Expr.col_offset = 0
        result = ast.Expression(Expr.value, lineno=0, col_offset = 0)
        return result

def exec_with_return(code):
    code_ast = ast.parse(code)
    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]
    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]
    exec(compile(init_ast, "<ast>", "exec"), globals())
    if type(last_ast.body[0]) == ast.Expr:
        return eval(compile(convertExpr2Expression(last_ast.body[0]), "<ast>", "eval"),globals())
    else:
        exec(compile(last_ast, "<ast>", "exec"),globals())

exec_with_return("from math import sin,cos,tan,hypot,sqrt")

class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None
    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            xdata = event.xdata
            ydata = event.ydata
            if event.button == 'down':
                scale_factor = base_scale
            elif event.button == 'up':
                scale_factor = 1/base_scale
            else:
                scale_factor = 1
            try:
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
                relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
                rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])
                ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
                ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
                ax.figure.canvas.draw()
            except:
                pass
        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', zoom)
        return zoom
    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press
        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()
        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)
            ax.figure.canvas.draw()
        fig = ax.get_figure()
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)
        return onMotion
    

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        zp = ZoomPan()
        figZoom = zp.zoom_factory(self.axes, base_scale = 1.2)
        figPan = zp.pan_factory(self.axes)
        self.graphs = []
        self.axes.grid(True)
        super(MplCanvas, self).__init__(fig)
    def ToDraw(self,x,y,color="r",name="1"):
        self.axes.plot(x,y,c=color,label=name)


class Programm:
    def __init__(self):
        pass
    def FRange(self,start = 0.0, end=0.0, step=1.0):
        i = start
        tolist = []
        while i <= end:
            tolist.append(i)
            i += step
        return tolist
    def ReadVars(self,text):
        try:
            text=text.replace(" ","")
        except:
            pass
        try:
            text=text.replace("  ","")
        except:
            pass
        lines = text.split("\n")
        mainVar = {}
        for i in range(0,len(lines)):
            if len(lines[i]) < 4:
                print("Error, line V "+str(i)+" less than 4s")
                continue
            if "main" in lines[i]:
                line = lines[i]
                div = line.split("=")
                MV = (div[0].replace(":","-"))
                right = div[1]
                right=right.replace("[","")
                right=right.replace("]","")
                variablesS = right.split(",")
                variablesI = []
                for var in variablesS:
                    try:
                        variablesI.append(float(var))
                    except:
                        if "range" in var:
                            try:
                                Args = (((var).split("("))[1]).replace(")","")
                                Args = Args.split(">")
                                if len(Args) > 4 or len(Args) < 2:
                                    break
                                elif len(Args) == 2:
                                    StartPos = Args[0]
                                    EndPos = Args[1]
                                    Herz = 1
                                elif len(Args) == 3:
                                    StartPos = Args[0]
                                    EndPos = Args[1]
                                    Herz = Args[2]
                                List = self.FRange(float(StartPos),float(EndPos),float(Herz))
                                variablesI = List
                                break
                            except Exception as exp:
                                print(exp)
                        elif ("sin" in var) or ("cos" in var) or ("tan" in var) or ("abs" in var) or ("hypot" in var):
                            if "to-" in var:
                                PreR = (((var).split("("))[1]).replace(")","")
                                name_to = (PreR.split('-'))[1]
                                PartBefore = "to-" + name_to
                                variablesI.append(var.replace(PartBefore,str(mainVar[name_to])))
                            else:
                                variablesI.append(str(var))
                        elif "to-" in var:
                            try:
                                rPre = var
                                name_to = (rPre.split('-'))[1]
                                variablesI.append(mainVar[name_to])
                            except:
                                variablesI.append(0.0)
                        else:
                            variablesI.append(0.0)
                mainVar[MV] = variablesI
            elif "var" in lines[i]:
                line = lines[i]
                div = line.split("=")
                MV = (div[0].split(":"))[1]
                try:
                    right = float(div[1])
                except:
                    if ("sin" in div[1]) or ("cos" in div[1]) or ("tan" in div[1]) or ("abs" in div[1]) or ("hypot" in div[1]):
                        if "to-" in div[1]:
                            PreR = (((div[1]).split("("))[1]).replace(")","")
                            name_to = (PreR.split('-'))[1]
                            PartBefore = "to-" + name_to
                            right = div[1].replace(PartBefore,str(mainVar[name_to]))
                        else:
                            right = str(div[1])
                    elif "to-" in div[1]:
                        try:
                            rPre = div[1]
                            name_to = (rPre.split('-'))[1]
                            right = mainVar[name_to]
                        except:
                            right = 0.0
                    elif "addres" in div[1]:
                        try:
                            rPre = div[1]
                            name_to = (rPre.split('>'))[1]
                            if "upper" in name_to:
                                name_to = name_to.replace('upper',"main")
                                #name_to = name_to.replace(((name_to.split("-"))[1]),((name_to.split("-"))[1]).lower())
                            value = (rPre.split('>'))[2]
                            right = mainVar[name_to]
                            right = right[int(value)]
                        except Exception as exp:
                            print(exp)
                            right = 0.0
                    else:
                        right = 0.0
                mainVar[MV] = right
            else:
                continue
        return mainVar
    def ReadCode(self,text):
        text=text.strip()
        try:
            text=text.replace(" ","")
        except:
            pass
        try:
            text=text.replace("  ","")
        except:
            pass
        lines = text.split("\n")
        mainCodes = []
        for i in range(0,len(lines)):
            if len(lines[i]) < 4:
                print("Error, line C "+str(i)+" less than 4s")
                continue
            elif "name" in lines[i]:
                line = (lines[i].split(":"))[2]
                line = line.replace("{","")
                line = line.replace("}","")
                mainCodes.append(line)
            else:
                continue
        return mainCodes
    def Interpretat(self,lines,variables):
        anwser = {}
        for var in variables:
            if "main" in var:
                continue
            else:
                for l in range(0,len(lines)):
                    try:
                        lines[l] = lines[l].replace(var,str(variables[var]))
                    except Exception as exp:
                        print("We cant replace "+var+" in "+str(l)+" line")
                        print(exp)
        return lines
    def Compilater(self,code,mainVars):
        positions = {}
        prepositions = {}
        for i in range(0,len(code)):
            for Var in mainVars:
                if "main" in Var:
                    variable = Var.replace("main-","")
                    allResults = mainVars[Var]
                    lines = []
                    for l in range(0,len(allResults)):
                        line = code[i]
                        line = line.replace(variable,str(allResults[l]))
                        othercode = line+"\ny"
                        try:
                                lines.append([str(allResults[l]),str(exec_with_return(othercode))])
                        except:
                                lines.append([str(allResults[l]),str(0.0)])
                    positions[str(i+1)] = lines
        return positions
    def Drawler(self,positions):
        args = []
        allbones = []
        allcolors = ["lawngreen", "aqua", "springgreen","magenta",'grey','fuchsia','green',"red","orange","olive","yellow"]
        for Graph in positions:
            pos = positions[Graph]
            xlist = []
            ylist = []
            for x in range(0,len(pos)):
                xlist.append(float(pos[x][0]))
            for y in range(0,len(pos)):
                ylist.append(float(pos[y][1]))
            allbones.append([xlist,ylist])
        for i in range(0,len(allbones)):
            args.append([allbones[i][0],allbones[i][1],allcolors[i%11],str(i+1)])
        return args
    

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.Interpreter = Programm()
        self.GRAPH = MplCanvas(self, width=1, height=1, dpi=100)
        #self.GRAPH.ToDraw([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0], [0.0, 1.0, 4.0, 9.0, 16.0, 25.0, 36.0, 49.0, 64.0, 81.0, 100.0, 121.0, 144.0, 169.0, 196.0, 225.0], 'lawngreen', '1')
        #[[-1.0, -2.0, -3.0, 0.0, 1.0, 2.0, 3.0], [-2.0, -4.0, -6.0, 0.0, 2.0, 4.0, 6.0], 'lawngreen', '1']
        self.ui.forgraph = QtWidgets.QVBoxLayout(self.ui.Graph)
        self.ui.forgraph.setGeometry(QtCore.QRect(0, 0, 1161, 751))
        self.ui.forgraph.setObjectName("forgraph")
        self.ui.forgraph.addWidget(self.GRAPH)
        self.ui.pushButton.clicked.connect(self.DrawGraphs)
    def DrawGraphs(self):
        self.ui.forgraph.removeWidget(self.GRAPH)
        self.GRAPH.deleteLater()
        self.GRAPH.hide()
        self.GRAPH = MplCanvas(self, width=1, height=1, dpi=100)
        text = self.ui.textEdit_2.toPlainText()
        Variables = self.Interpreter.ReadVars(text)
        text =self.ui.textEdit.toPlainText()
        Lines = self.Interpreter.ReadCode(text)
        Codes = self.Interpreter.Interpretat(Lines,Variables)
        Positions = self.Interpreter.Compilater(Codes,Variables)
        LastArgs = self.Interpreter.Drawler(Positions)
        for i in range(0,len(LastArgs)):
            self.GRAPH.ToDraw(LastArgs[i][0],LastArgs[i][1],LastArgs[i][2],LastArgs[i][3])
        #self.GRAPH.ToDraw([-1.0, -2.0, -3.0, 0.0, 1.0, 2.0, 3.0], [-2.0, -4.0, -6.0, 0.0, 2.0, 4.0, 6.0], 'lawngreen', '1')
        self.ui.forgraph.addWidget(self.GRAPH)

def main():
        app = QtWidgets.QApplication([])
        application = mywindow()
        application.show()
         
        sys.exit(app.exec())

if __name__ == "__main__":
        main()
