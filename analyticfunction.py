import array
import collections
import os
import ROOT
import style
import makeDjetplot

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

def graphxlimits(graph):
    x = graph.GetX()
    ex = graph.GetEX()
    y = graph.GetY()
    ey = graph.GetEY()

    xex = [(x[i], ex[i]) for i in range(graph.GetN())]

    low = min(xex, key = sum)
    low = low[0] - low[1]
    hi = max(xex, key = sum)
    hi = hi[0] - hi[1]

    return (low, hi)

def getfunction(name, plots):

    plot = plots[name]
    x = plot.GetX()
    y = plot.GetY()

    limits = graphxlimits(plot)

    if name == "ggZZ":
        plot = plots["H+jj"]
        x = plot.GetX()
        y = plot.GetY()
        evalstr = "%f" % (sum(y[i] for i in range(plot.GetN()))/plot.GetN())
        low = None
        hi = None
    if name == "H+jj" or name == "qqZZ":
        evalstr = "%f" % (sum(y[i] for i in range(plot.GetN()))/plot.GetN())
        low = None
        hi = None
    if name == "ttH":
        low, hi = limits
        f = ROOT.TF1("f_ttH", "[0] + [1]*x + [2]*x*x", low, hi)
        f.SetParameters(1, 1, 1)
        plot.Fit(f)
        evalstr = "%f + %f*m4l + %f*m4l*m4l" % tuple(f.GetParameter(a) for a in range(3))
    if name == "VBF":
        low, hi = limits
        f = ROOT.TF1("f_VBF", "[0] + [1]*x + [2]*x*x", low, hi)
        f.SetParameters(1, 1, 1)
        plot.Fit(f)
        evalstr = "%f + %f*m4l + %f*m4l*m4l" % tuple(f.GetParameter(a) for a in range(3))
    if name == "ZH" or name == "WH":   #set to linear below 200 GeV, constant above/below
        low, hi = 100, 200
        f = ROOT.TF1("f_%s"%name, "[0] + [1]*x", low, hi)
        f.SetParameters(1, -1)
        plot.Fit(f)
        evalstr = "%f + %f*m4l" % tuple(f.GetParameter(a) for a in range(2))

    return AnalyticFunction(name, evalstr, low, hi)


def getplotsfromcanvas(canvas):
    legend = canvas.GetListOfPrimitives().At(2)
    plots = {}
    for entry in legend.GetListOfPrimitives():
        graph = entry.GetObject()
        name = entry.GetLabel()
        plots[name] = graph
    return plots

def indent(string):
    bracelevel = 0
    lines = string.split("\n")
    for i, line in enumerate(lines):
        bracelevel -= line.count("}")
        lines[i] = " "*4*bracelevel + line
        bracelevel += line.count("{")

    return "\n".join(lines)

def printCstr(filename):
    f = ROOT.TFile(filename)
    if not f:
        raise IOError("No file %s!" % filename)
    c = f.GetListOfKeys().At(0).ReadObj()
    if not c or type(c) != ROOT.TCanvas:
        raise IOError("no canvas in file " + filename + "!")

    plots = getplotsfromcanvas(c)

    Cstring = "enum {" + ", ".join(name for name in plots) + "};\n\n"

    Cstring += "double Djetefficiency(double m4l)\n"
    Cstring += "{\n"
    for name in plots:
        function = getfunction(name, plots)
        Cstring += function.Cstr

    Cstring += "}\n"

    c.SaveAs("test.png")

    return indent(Cstring)

if __name__ == "__main__":
    print printCstr("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fraction.root")
