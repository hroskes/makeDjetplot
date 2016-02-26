import array
import collections
import makeDjetplot
import math
import os
import ROOT
import style

def gaus(x):
    math.exp(-x**2)

class AnalyticFunction(object):
    def __init__(self, name, evalstr, low, hi):
        self.evalstr = evalstr
        self.low = low
        self.hi = hi
        self.name = name
        self.channelname = "channel_"+name.replace("+", "")
        self.Cstr  = "if (channel == %(channelname)s)\n"
        self.Cstr += "{\n"
        if low is not None:
            self.Cstr += "if (m4l < %(low)f) m4l = %(low)f;\n" 
        if hi is not None:
            self.Cstr += "if (m4l > %(hi)f) m4l = %(hi)f;\n"
        self.Cstr += "return %(evalstr)s;\n"
        self.Cstr += "}\n"
        self.Cstr %= self.__dict__
        self.Cstr = self.Cstr.replace("gaus", "TMath::Gaus")

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

def weightedaverage(x, ex):
    num = sum(xi/exi**2 for xi, exi in zip(x, ex) if exi != 0)
    den = sum(1/exi**2 for exi in ex if exi != 0)
    return num/den

def getfunction(name, plots):

    plot = plots[name]
    if name == "ggZZ" or name == "ggH":
        plot = plots["ggH"]
    x = [xi for i, xi in zip(range(plot.GetN()), plot.GetX())]
    y = [yi for i, yi in zip(range(plot.GetN()), plot.GetY())]
    ex = [exi for i, exi in zip(range(plot.GetN()), plot.GetEX())]
    ey = [eyi for i, eyi in zip(range(plot.GetN()), plot.GetEY())]

    limits = graphxlimits(plot)

    if name == "ggZZ" or name == "ggH" or name == "Z+X":
        evalstr = "%e" % weightedaverage(y, ey)
        low = None
        hi = None
    if name == "qqZZ":  #from Ian's script
        evalstr = "%e - %e*m4l*gaus((m4l-%e)/%e)" % (6.54811139624252893e-03, 5.86652284998493653e-06, 2.43263229325644204e+02, 2.27247741344343623e+01)
        low = None
        hi = None
    if name == "ttH":
        low, hi = limits
        f = ROOT.TF1("f_ttH", "[0] + [1]*x + [2]*x*x", low, hi)
        f.SetParameters(1, 1, 1)
        plot.Fit(f, "W")
        evalstr = "%e + %e*m4l + %e*m4l*m4l" % tuple(f.GetParameter(a) for a in range(3))
    if name == "VBF":
        low, hi = limits
        f = ROOT.TF1("f_VBF", "[0] + [1]*x + [2]*x*x + [3]*x*x*x", low, hi)
        f.SetParameters(1, 1, 1, 1)
        plot.Fit(f, "W")
        evalstr = "%e + %e*m4l + %e*m4l*m4l + %e*m4l*m4l*m4l" % tuple(f.GetParameter(a) for a in range(4))
    if name == "ZH" or name == "WH":   #set to linear below 200 GeV, constant above/below
        low, hi = 110, 200
        f = ROOT.TF1("f_%s"%name, "[0] + [1]*x + [2]*x*x", low, hi)
        f.SetParameters(1, 1, -1)
        if name == "ZH":
            f.FixParameter(1, -0.000111909)
            f.FixParameter(0, 0.035839409)
            f.FixParameter(2, 0)
        plot.Fit(f, "W")

        evalstr = "%e + %e*m4l + %e*m4l*m4l" % tuple(f.GetParameter(a) for a in range(3))

    return AnalyticFunction(name, evalstr, low, hi)


def getplotsfromcanvas(canvas):
    legend = canvas.GetListOfPrimitives().At(2)
    plots = collections.OrderedDict((a, None) for a in ("ggH", "VBF", "WH", "ZH", "ttH", "qqZZ", "ggZZ", "Z+X"))
    for entry in legend.GetListOfPrimitives():
        graph = entry.GetObject()
        name = entry.GetLabel()
        assert name in plots
        plots[name] = graph
    return plots

def indent(string):
    bracelevel = 0
    lines = string.split("\n")
    for i, line in enumerate(lines):
        nopen, nclose = line.count("{"), line.count("}")
        if nopen and nclose and nopen != nclose:
            raise NotImplementedError
        if nopen != nclose:
            bracelevel -= line.count("}")
        lines[i] = " "*4*bracelevel + line
        if nopen != nclose:
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

    Cstring = ""

    Cstring += "#include <assert.h>\n"
    Cstring += '#include "TMath.h"\n\n'
    Cstring += "enum Channel {channel_" + ", channel_".join(name.replace("+", "") for name in plots) + "};\n\n"

    Cstring += "double Djetefficiency(double m4l, Channel channel)\n"
    Cstring += "{\n"
    for name in plots:
        function = getfunction(name, plots)
        Cstring += function.Cstr

    Cstring += "\n"
    Cstring += "assert(false);\n"
    Cstring += "}\n"

    c.SaveAs("/afs/cern.ch/user/h/hroskes/TEST/test.png")

    return indent(Cstring)

if __name__ == "__main__":
    Cstring = printCstr("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fraction.root")
    print Cstring
    with open("Djetefficiency.C", "w") as f:
        f.write(Cstring)
