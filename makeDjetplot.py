import array
import CJLSTfiles
import collections
import loadlib
import os
import ROOT
import style

class Plot(object):
    maindir = "root://eoscms//eos/cms/store/user/covarell/2l2qTrees/160625/"
    basename = "ZZ2l2qAnalysis_{}.root"
    min = 0.
    max = 1.
    bins = 100
    units = ""

    def __init__(self, title, color, *CJLSTdirs, **kwargs):
        for kw, kwarg in kwargs.iteritems():
            if kw == "maindir":
                self.maindir = kwarg
            elif kw == "basename":
                self.basename = kwarg
            elif kw == "match":
                CJLSTdirs = list(CJLSTdirs) + CJLSTfiles.listfolders(self.maindir, kwarg)
                CJLSTdirs = list(set(CJLSTdirs))
            else:
                raise TypeError("Unknown kwarg: %s=%s" % (kw, kwarg))
        self.filenames = []
        for dir in CJLSTdirs:
            maindir = self.maindir
            if not CJLSTfiles.exists(maindir, dir):
                raise ValueError("{} does not exist in {}".format(dir, self.maindir))
            self.filenames.append(os.path.join(maindir, dir, self.basename))
        self.title = title
        self.color = color
        self._h = None

    def __hash__(self):
        return hash((tuple(self.filenames), self.title, self.color))
    def __str__(self):
        return self.title

    def addtolegend(self, tlegend, option = "l"):
        tlegend.AddEntry(self.h(), self.title, option)

class TreePlot(Plot):
    def __init__(self, title, color, *CJLSTdirs, **kwargs):
        Plot.__init__(self, title, color, *CJLSTdirs, **kwargs)

    def h(self, bins = None, normalize = True):
        if self._h is not None and bins is None:
            return self._h
        if bins is None:
            bins = [Bin(-1, float("inf"))]
        t = ROOT.TChain("ZZTree/candTree")
        for filename in self.filenames:
            for i in range(22):
                t.Add(filename.format(i))
        print t.GetEntries()

        h = {}
        sumofweights = {}
        for bin in bins:
            h[bin] = ROOT.TH1F("h"+self.title+str(bin), "D_{jet}", self.bins, self.min, self.max)
            h[bin].SetLineColor(self.color)
            h[bin].SetMarkerColor(self.color)
            h[bin].SetLineWidth(3)
            h[bin].Sumw2()
            sumofweights[bin] = 0

        length = t.GetEntries()

        for i, entry in enumerate(t):
            t.GetEntry(i)

            wt = entry.genHEPMCweight * entry.PUWeight

            for cand, pvbf, phjj, m4l in zip(entry.ZZCandType, entry.pvbf_VAJHU_highestPTJets, entry.phjj_VAJHU_highestPTJets, entry.ZZMass):
                if cand == 2 and resolved or cand == 1 and not resolved and 2 not in entry.ZZCandType:
                    try:
                        Djet = (pvbf / (pvbf + 0.06 * phjj))
                    except ZeroDivisionError:
                        pass
                    for bin in bins:
                        if bin.min <= m4l < bin.max:
                            if pvbf >= 0 and phjj >= 0 and not (pvbf == phjj == 0):
                                h[bin].Fill(Djet, wt)
                            else:
                                h[bin].Fill(-1, wt)

                            sumofweights[bin] += wt

            if (i+1) % 10000 == 0 or i+1 == length:
                print (i+1), "/", length

        h[bin].Print("all")
        if normalize:
            for bin in bins:
                try:
                    h[bin].Scale(1.0/sumofweights[bin])
                except ZeroDivisionError:
                    pass

        if len(h) == 1:
            self._h = h.values()[0]
        else:
            self._h = h
        return self._h

class ZXPlot(Plot):
    def __init__(self, color):
        Plot.__init__(self, "Z+X", color, "AllData")

    def h(self, bins = None, normalize = True):
        if self._h is not None and bins is None:
            return self._h
        if bins is None:
            bins = [Bin(-1, float("inf"))]
        t = ROOT.TChain("CRZLLTree/candTree")
        for filename in self.filenames:
            t.Add(filename)

        h = {}
        sumofweights = {}
        for bin in bins:
            h[bin] = ROOT.TH1F("h"+self.title+str(bin), "D_{jet}", self.bins, self.min, self.max)
            h[bin].SetLineColor(self.color)
            h[bin].SetMarkerColor(self.color)
            h[bin].SetLineWidth(3)
            h[bin].Sumw2()
            sumofweights[bin] = 0

        length = t.GetEntries()

        for i, entry in enumerate(t):
            wt = ROOT.fakeRate13TeV(entry.LepPt.at(2),entry.LepEta.at(2),entry.LepLepId.at(2)) * ROOT.fakeRate13TeV(entry.LepPt.at(3),entry.LepEta.at(3),entry.LepLepId.at(3))

            try:
                Djet = (entry.pvbf_VAJHU_old / (entry.pvbf_VAJHU_old + entry.phjj_VAJHU_old))
            except ZeroDivisionError:
                pass

            for bin in bins:
                if bin.min <= entry.ZZMass < bin.max:
                    if entry.pvbf_VAJHU_old >= 0 and entry.phjj_VAJHU_old >= 0 and not (entry.pvbf_VAJHU_old == entry.phjj_VAJHU_old == 0):
                        h[bin].Fill(Djet, wt)
                    else:
                        h[bin].Fill(-1, wt)

                    sumofweights[bin] += wt

            if (i+1) % 10000 == 0 or i+1 == length:
                print (i+1), "/", length

        if normalize:
            for bin in bins:
                try:
                    h[bin].Scale(1.0/sumofweights[bin])
                except ZeroDivisionError:
                    pass

        if len(h) == 1:
            self._h = h.values()[0]
        else:
            self._h = h
        return self._h

def makeDjetplots(*plots):
    print "ABC"
    c1 = ROOT.TCanvas()
    legend = ROOT.TLegend(0.6, 0.5, 0.9, 0.9)
    legend.SetLineStyle(0)
    legend.SetLineColor(0)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    hstack = ROOT.THStack("hstack", "D_{jet}")
    max, min, bins, units = None, None, None, None
    for plot in plots:
        print plot
        hstack.Add(plot.h())
        plot.addtolegend(legend)
        if max is None:
            max, min, bins, units = plot.max, plot.min, plot.bins, plot.units
        assert (max, min, bins, units) == (plot.max, plot.min, plot.bins, plot.units)
    hstack.Draw("nostackhist")
    hstack.GetXaxis().SetTitle("D_{jet}")
    hstack.GetYaxis().SetTitle("fraction of events / %s%s" % ((max-min)/bins, " "+units if units else ""))
    legend.Draw()
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/Djet.png".format("resolved" if resolved else "merged"))
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/Djet.eps".format("resolved" if resolved else "merged"))
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/Djet.root".format("resolved" if resolved else "merged"))
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/Djet.pdf".format("resolved" if resolved else "merged"))

class Bin(object):
    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.center = (max+min)*.5
        self.error = (max-min)*.5
    def __str__(self):
        return "%s-%s GeV" % (self.min, self.max)

def makeDjettable(massbins, *plots):
    print massbins
    bins = [Bin(massbins[i], massbins[i+1]) for i in range(len(massbins)-1)]
    for a in bins: print a

    fraction = collections.OrderedDict()
    x = {}
    y = {}
    ex = {}
    ey = {}
    nbins = {}
    g = {}
    mg = ROOT.TMultiGraph()
    legend = ROOT.TLegend(0.6, 0.4, 0.9, 0.8)
    legend.SetLineStyle(0)
    legend.SetLineColor(0)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    for plot in plots:
        x[plot] = array.array("d")
        y[plot] = array.array("d")
        ex[plot] = array.array("d")
        ey[plot] = array.array("d")
        nbins[plot] = 0
        fraction[plot] = collections.OrderedDict()

        h = plot.h(bins)
        for bin in bins:
            integralerror = array.array("d", [0])
            fraction[plot][bin] = h[bin].IntegralAndError(51, 100, integralerror)
            if plot.title == "ttH" and bin.min >= 500: continue
            nbins[plot] += 1
            x[plot].append(bin.center)
            y[plot].append(fraction[plot][bin])
            ex[plot].append(bin.error)
            ey[plot].append(integralerror[0])
        g[plot] = ROOT.TGraphErrors(nbins[plot], x[plot], y[plot], ex[plot], ey[plot])
        mg.Add(g[plot])
        g[plot].SetLineColor(plot.color)
        g[plot].SetMarkerColor(plot.color)
        legend.AddEntry(g[plot], plot.title, "lp")

    c1 = ROOT.TCanvas()
    mg.Draw("AP")
    mg.GetXaxis().SetTitle("m_{4l}")
    mg.GetYaxis().SetTitle("fraction of events with D_{jet}>0.5")
    mg.SetMinimum(0)
    legend.Draw()
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/fraction.png".format("resolved" if resolved else "merged"))
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/fraction.eps".format("resolved" if resolved else "merged"))
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/fraction.root".format("resolved" if resolved else "merged"))
    c1.SaveAs("~/www/VBF/Djet/2016_2l2q/{}/fraction.pdf".format("resolved" if resolved else "merged"))

    print r"\begin{center}"
    print r"\begin{tabular}{ |%s| }" % ("|".join("c" * (len(plots)+1)))

    #http://stackoverflow.com/a/9536084
    header_format = " & ".join(["{:>15}"] * (len(plots) + 1)) + r" \\"
    row_format = " & ".join(["{:>15}"] + [r"{:14.2f}\%"] * (len(plots))) + r"\\"
    print r"\hline"
    print header_format.format("", *plots)
    for bin in bins:
        print r"\hline"
        print row_format.format(bin, *(fraction[plot][bin]*100 for plot in plots))
    print r"\hline"
    print r"\end{tabular}"
    print r"\end{center}"

def printdebug(massbins, *plots):
    print massbins
    bins = [Bin(massbins[i], massbins[i+1]) for i in range(len(massbins)-1)]
    for a in bins: print a

    fraction = collections.OrderedDict()
    passcut = collections.OrderedDict()
    failcut = collections.OrderedDict()
    notdijet = collections.OrderedDict()

    for plot in plots:
        passcut[plot] = collections.OrderedDict()
        failcut[plot] = collections.OrderedDict()
        notdijet[plot] = collections.OrderedDict()

        h = plot.h(bins, normalize = False)
        print "ABC"
        for bin in bins:
            integralerror = array.array("d", [0])
            passcut[plot][bin] = h[bin].IntegralAndError(51, 100, integralerror)
            failcut[plot][bin] = h[bin].IntegralAndError(1, 50, integralerror)
            notdijet[plot][bin] = h[bin].GetBinContent(0)

    header_format = "  ".join(["{:>15}"] + ["{:>14}"] * (3*len(plots)))
    row_format = "  ".join(["{:>15}"] + [r"{:14.2f}"] * (3*len(plots)))
    print header_format.format("", *sum((["", plot, ""] for plot in plots), []))
    print header_format.format("", *(["pass", "fail", "<2 jets"]*len(plots)))
    for bin in bins:
        print row_format.format(bin, *sum(([passcut[plot][bin], failcut[plot][bin], notdijet[plot][bin]] for plot in plots), []))


if __name__ == "__main__":
    forplot = False
    fortable = True
    fordebug = False
    resolved = False
    if forplot:
        plots = (
                 TreePlot("VBF",  1,              "VBFHiggs1000"),
                 TreePlot("ggH",  2,              "ggHiggs1000"),
                )
        makeDjetplots(*plots)
    if fortable:
        plots = (
                 TreePlot("VBF",  1,              match="VBFHiggs[0-9]*"),
                 TreePlot("ggH",  2,              match="ggHiggs[0-9]*"),
                )
        makeDjettable([300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000], *plots)
    if fordebug:
        plots = (
                 TreePlot("new", 1,              "VBFH125"),
                 TreePlot("old", 2,              "VBF125", maindir="root://lxcms03://data3/Higgs/160121/"),
                )
        printdebug([100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 300, 400, 500, 600, 700, 800, 900, 1000], *plots)
