import ROOT

def zoom(filename, axis, xmin, xmax):
    f = ROOT.TFile.Open(filename)
    if not f:
        raise IOError("No file %s!" % filename)
    c = f.GetListOfKeys().At(0).ReadObj()
    if not c or type(c) != ROOT.TCanvas:
        raise IOError("no canvas in file " + filename + "!")
    multigraph = c.GetListOfPrimitives().At(1)
    if not multigraph or type(multigraph) != ROOT.TMultiGraph:
        raise IOError("no multigraph in canvas in file " + filename + "!")

    if axis == 'x':
        multigraph.GetXaxis().SetLimits(xmin, xmax)
        newfilename = filename.replace(".root", "_%s-%s" % (xmin, xmax))
    elif axis == 'y':
        #multigraph.SetMinimum(xmin)
        multigraph.SetMinimum(-0.005)
        multigraph.SetMaximum(xmax)
        newfilename = filename.replace(".root", "_y%s-%s" % (xmin, xmax))

    c.SaveAs(newfilename+".png")
    c.SaveAs(newfilename+".eps")
    c.SaveAs(newfilename+".root")
    c.SaveAs(newfilename+".pdf")

if __name__ == '__main__':
    zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fits.root", 'x', 100, 200)
    #zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fraction.root", 'x', 100, 200)
    zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fits.root", 'y', 0, .1)
    #zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fraction.root", 'y', 0, .1)
    zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fits_100-200.root", 'y', 0, .1)
    #zoom("/afs/cern.ch/user/h/hroskes/www/VBF/Djet/fraction_100-200.root", 'y', 0, .1)
