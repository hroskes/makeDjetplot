import array
import collections
import os
import ROOT
import style
import makeDjetplot

rootfile = ROOT.TFile.Open("fromUlascan/HZZ4l-DjetCutShapes.root")

class AnalyticFunction(object):
    def __init__(self, name, evalstr, low, hi):
        self.evalstr = evalstr
        self.low = low
        self.hi = hi
        self.name = name
        self.Cstr  = "if (channel == %(name)s)\n"
        self.Cstr += "{\n"
        if low is not None:
            self.Cstr += "if (m4l < %(low)f) m4l = %(low)f;\n" 
        if hi is not None:
            self.Cstr += "if (m4l > %(hi)f) m4l = %(hi)f;\n"
        self.Cstr += "return %(evalstr)s;\n"
        self.Cstr += "}\n"
        self.Cstr %= self.__dict__

def getfunction(name):

    fname = {
             "ggZZ": "MINLO_Djetcutshape",
             "H+jj": "MINLO_Djetcutshape",
             "qqZZ": "qqZZ_Djetcutshape",
             "VBF": "PhantomSig_Djetcutshape",
             "Z+X": "ZX_Djetcutshape",
            }
    try:
        f = rootfile.Get(fname[name])
        assert f
        return f
    except KeyError:
        return None

def getplotsfromcanvas(canvas):
    legend = canvas.GetListOfPrimitives().At(2)
    plots = {}
    for entry in legend.GetListOfPrimitives():
        graph = entry.GetObject()
        name = entry.GetLabel()
        plots[name] = graph
    return plots

def draw(filename):
    f = ROOT.TFile(filename)
    if not f:
        raise IOError("No file %s!" % filename)
    c = f.GetListOfKeys().At(0).ReadObj()
    if not c or type(c) != ROOT.TCanvas:
        raise IOError("no canvas in file " + filename + "!")

    plots = getplotsfromcanvas(c)
    functions = {}
    for name in plots:
        plot = plots[name]
        f = getfunction(name)
        if f is not None:
            functions[name] = f
            f.SetLineColor(plot.GetLineColor())
            f.SetLineWidth(3)
            f.Draw("same")

    functions["Z+X"] = getfunction("Z+X")
    functions["Z+X"].SetLineColor(7)
    functions["Z+X"].SetLineWidth(3)
    functions["Z+X"].Draw("same")


    c.SaveAs("/afs/cern.ch/user/h/hroskes/www/TEST/test.png")
    c.SaveAs("/afs/cern.ch/user/h/hroskes/www/TEST/test.pdf")

if __name__ == '__main__':
    draw("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fraction.root")
