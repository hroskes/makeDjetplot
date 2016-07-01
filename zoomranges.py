import ROOT

def zoom(filename, axis, xmin, xmax, axis2=None, xmin2=None, xmax2=None):
    f = ROOT.TFile.Open(filename)
    if not f:
        raise IOError("No file %s!" % filename)
    c = f.GetListOfKeys().At(0).ReadObj()
    if not c or type(c) != ROOT.TCanvas:
        raise IOError("no canvas in file " + filename + "!")
    multigraph = c.GetListOfPrimitives().At(1)
    if not multigraph or type(multigraph) != ROOT.TMultiGraph:
        raise IOError("no multigraph in canvas in file " + filename + "!")

    if axis2 != 'y' and axis2 is not None: assert False

    if axis == 'x':
        multigraph.GetXaxis().SetLimits(xmin, xmax)
        newfilename = filename.replace(".root", "_%s-%s" % (xmin, xmax))
    elif axis == 'y':
        #multigraph.SetMinimum(xmin)
        multigraph.SetMinimum(-0.005)
        multigraph.SetMaximum(xmax)
        newfilename = filename.replace(".root", "_y%s-%s" % (xmin, xmax))
    else:
        assert False
    if axis2 == 'y':
        multigraph.SetMinimum(-0.005)
        multigraph.SetMaximum(xmax2)

    c.SaveAs(newfilename+".png")
    c.SaveAs(newfilename+".eps")
    c.SaveAs(newfilename+".root")
    c.SaveAs(newfilename+".pdf")

def dozoom():
    zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/2016_2l2q/resolved/fraction.root", 'x', 300, 1500, 'y', 0, 0.5)

if __name__ == "__main__":
    dozoom()
