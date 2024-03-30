from customtkinter import *
from tkinterdnd2 import TkinterDnD, DND_ALL
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as polynom
import os

#prebuiltSettings
matplotlib.use('TkAgg')
set_appearance_mode("system")
set_default_color_theme("blue")
os.chdir('C:/buffer')
#mainClass
class windowApp(CTk, TkinterDnD.DnDWrapper):
    def __init__(self, size:str, *args,**kwargs)  -> CTk:
        super().__init__(*args,**kwargs)
        #sharedData
        
        self.file = open('text.txt', 'r', encoding='utf-8')
        self.dataVar = self.file.read()
        self.file.close()
        self.points = [] 
        self.values = []

        #WindowOptions
        self.Tkdndversion = TkinterDnD._require(self)
        self.title("Interpolation program")
        self.geometry(size)
        for i in range(3):
            self.rowconfigure(i, weight= 1)
            self.columnconfigure(i, weight= 1)
        self.rowconfigure(3, weight=1)

        #QuitScenario
        self.protocol("WM_DELETE_WINDOW", quit)

        #Start
        self.createWidgets()
        self.showInput()
        self.mainloop()
    #Widgets
    def createButtons(self) -> None:
        self.upbutton = CTkButton(self, text= "load file", command= self.loadfile, width = 600, height= 150)
        self.filebutton = CTkButton(self, text= "or open file dialog", command= self.filedialog, width = 600, height= 150)
        self.inputButton = CTkButton(self, text= "select other file", command= self.showInput, width = 100, height= 100)
        self.drawButton = CTkButton(self, text="draw graph", command=self.draw, width=100, height=100)
        self.clearButton = CTkButton(self, text = 'clear', command=self.clear, width=100, height=100)
    
    def createWidgets(self) -> None:
        self.check_var1 = StringVar(value=0)
        self.check_var2 = StringVar(value=0)

        #Buttons
        self.createButtons()

        #Labels
        self.label = CTkLabel(self, text= "Drop or choose a file", width= 600, height= 100)

        self.label.drop_target_register(DND_ALL)
        self.label.dnd_bind('<<Drop>>', self.uploadfile)
        #CheckBoxes
        self.LagrangeCheck = CTkCheckBox(self,text="draw Lagrange polynoms", variable=self.check_var1, onvalue=1, offvalue=0, width = 100, height=100 )
        self.SplineCheck = CTkCheckBox(self,text="draw Splines polynoms", variable=self.check_var2, onvalue=1, offvalue=0, width=100, height=100)

        #Frames
        self.frame = dataFrame(master=self)
        self.spec = CTkFrame(master= self, height=400,width=400)
        self.inter = Interpolation(self.spec, [],[])
        self.inter.get_tk_widget().pack()

        
        #inputmethods
    def showInput(self) -> None:
        try:
            self.hideData()
        except:
            pass
        self.label.grid(sticky = 'nsew', columnspan = 3)
        self.upbutton.grid(sticky = 'nsew', columnspan = 3)
        self.filebutton.grid(sticky = 'nsew', columnspan = 3)

    def hideInput(self) -> None:
        self.label.grid_remove()
        self.upbutton.grid_remove()
        self.filebutton.grid_remove()


    def uploadfile(self, event) -> None:
        self.dataVar = event.data
        self.label.configure(text= str(self.dataVar).split('/')[-1]+' click to read')

    def filedialog(self) -> None:
        self.dataVar = filedialog.askopenfilename()
        self.label.configure(text= str(self.dataVar).split('/')[-1]+' click to read')

    def loadfile(self) -> None:
        self.file = open('text.txt', 'w',encoding='utf-8')
        self.file.seek(0)
        self.file.write(str(self.dataVar))
        self.file.close()
        print('Записано')
        try:
            data = pd.read_csv(self.dataVar, sep= ';', dtype= np.double)
            self.points, self.values = np.round(data.to_numpy().transpose(),6)
            self.hideInput()
            self.showData()
        except:
            self.label.configure(text= 'no proper file is present')


    #dataMethods
    def showData(self) -> None:  

        #Data
        self.frame = dataFrame(array =[self.points, self.values],master = self, height = 300, width=100)
        self.inter.get_tk_widget().pack_forget()
        self.inter = Interpolation(master = self.spec,points= self.points,values= self.values)

        self.frame.grid(sticky = 'nsew', rowspan=3, column = 0, row = 0)
        self.inter.get_tk_widget().pack()
        self.spec.grid(sticky='nsew',column=1,row=0, rowspan=4)

        self.inter.config()

        self.inputButton.grid(sticky = 'nsew', row=3)
        self.LagrangeCheck.grid(sticky = 'nsew', column=2, row=0)
        self.SplineCheck.grid(sticky = 'nsew', column = 2, row=1)
        self.drawButton.grid(sticky = 'nsew',column = 2, row=2)
        self.clearButton.grid(sticky = 'nsew', column=2, row=3)

    def hideData(self) -> None:
        self.frame.grid_remove()
        self.spec.grid_remove()
        self.inputButton.grid_remove()
        self.LagrangeCheck.grid_remove()
        self.SplineCheck.grid_remove()
        self.drawButton.grid_remove()
        self.clearButton.grid_remove()


    #graphicsMethods
    def draw(self) -> None:
        count = counter(self.points, self.values)
        if self.check_var1.get() == '1':
            self.inter.addGraph(count.eval_Lag_poly(),color='blue', label='Интерполяция многочленами Лагранжа')
        if self.check_var2.get() == '1':
            self.inter.addGraph(count.eval_cubic_spl(), color='orange', label ='Интерполяция кубическими сплайнами')
        else:
            self.inter.draw()
    def clear(self) -> None:
        try:
            self.inter.clear()
        except:
            pass


#classToCalculateInterpolationCoefficient
class counter():
    def __init__(self, points:np.array, values:np.array):
        self.points = points
        self.values = values
        self.n = len(points)


    #LagrangePolynomCalculation
    def Lag_poly_basis(self) -> list[polynom.Polynomial]:
        points = self.points.tolist()
        l = []
        for i in range(self.n):
            l.append(polynom.Polynomial.fromroots(points[:i:]+points[i+1:self.n:]))
            for j in range(self.n):
                if i == j:
                    continue
                l[i]= l[i] // polynom.Polynomial(np.round(points[i]-points[j],9))
        return l
    def Lag_poly(self) -> polynom.Polynomial:
        return np.sum(np.fromiter((self.values[i] * self.Lag_poly_basis()[i] for i in range(self.n)),dtype=polynom.Polynomial))
    def eval_Lag_poly(self) -> tuple[np.array,np.array]:
        x = self.points
        pln = self.Lag_poly()
        xx, yy = pln.linspace(1000, [min(x),max(x)])
        return (xx, yy)
    

    #CubicSplinesCalculation
    def calc_cubic_spl(self) -> tuple[np.array,np.array,np.array]:
        n = self.n-1
        h = np.diff(self.points)
        df = np.diff(self.values) / h
        A = np.zeros((n+1, n+1))
        B = np.zeros(n+1)
        A[0, 0] = 1
        A[n, n] = 1
        for i in range(1, n):
            A[i, i-1] = h[i-1]
            A[i, i] = 2 * (h[i-1] + h[i])
            A[i, i+1] = h[i]
            B[i] = 3 * (df[i] - df[i-1])
        c = np.linalg.solve(A, B)
        d = np.diff(c) / (3 * h)
        b = df - h * (2 * c[:-1] + c[1:]) / 3
        return b, c[:-1], d
    def eval_cubic_spl(self) -> tuple[np.array,np.array]:
        x, y = self.points, self.values
        b, c, d = self.calc_cubic_spl()
        n = len(x) - 1
        xx = np.linspace(x[0], x[-1], 1000)
        yy = np.piecewise(xx, [((x[i] <= xx) & (xx <= x[i+1])) for i in range(n)],
                        [lambda xx, i=i: y[i] + b[i] * (xx - x[i]) + c[i] * (xx - x[i])**2 + d[i] * (xx - x[i])**3 for i in range(n)])
        return (xx, yy)



#WindowSubclassForBetterTable
class dataFrame(CTkScrollableFrame):
    def __init__(self, array:list[np.array] = [], *args, **kwargs) -> CTkScrollableFrame:
        super().__init__(*args, **kwargs)
        for j, x in enumerate(array):
              for i, proc in enumerate(x):
                self.app_frame = CTkFrame(
                    master=self,
                    width=50,
                    height=50,
                    corner_radius=3,
                    border_width=0,
                    
                )
                self.app_name_label = CTkLabel(
                    self.app_frame,
                    text=proc,
                )
                self.app_frame.grid(row=i, column=j, pady=2) 
                self.app_name_label.place(y=25, x=20)

    

#PlotClass
class Interpolation(FigureCanvasTkAgg):
        
    def __init__(self, master:CTk ,points:np.array, values:np.array, *args,**kwargs) -> FigureCanvasTkAgg:
        #SharedData
        self.fig = plt.Figure(figsize=(15, 15))
        self.points = points
        self.values = values
        super().__init__(self.fig, master)
        #self._tkcanvas.configure(*args, **kwargs)
        #self.nav = NavigationToolbar2Tk(self, self)
        #BasicPlot
        self.ax = self.fig.add_subplot()
        self.ax.plot(points,values,'o',label = 'точки',color = 'red')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.fig.tight_layout()

    #drawMethodToUpdatePlot
    def draw(self) -> None:
        self.config()
        self.fig.legend()
        super().draw()

    #UsefulMethod
    def config(self) -> None:
        minv = min(self.values)
        maxv = max(self.values)
        minp = min(self.points)
        maxp = max(self.points)
        self.ax.set_ylim(minv-0.1*abs(minv), maxv+0.1*abs(maxv))
        self.ax.set_xlim(minp-0.1*abs(minp), maxp+0.1*abs(maxp))
        self.ax.set_xticks(np.linspace(int(minp),int(maxp),20))
        self.ax.set_yticks(np.linspace(int(minv),int(maxv),20))

    #GraphDrawerMethod
    def addGraph(self, dots:tuple[np.array,np.array], color:str, label:str) -> None:
        xx,yy =dots
        self.ax.plot(xx, yy, label= label,color= color)
        self.config()
        self.draw()
    #CleanerMethod
    def clear(self) -> None:
        self.ax.cla()
        self.ax.plot(self.points,self.values,'o',label = 'точки',color='red')
        self.draw()


if __name__ == '__main__':
    wind = windowApp("600x400")