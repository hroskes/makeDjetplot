import array
import os
import ROOT
import style

class Plot:
    maindir = "root://lxcms03://data3/Higgs/160111_ggZZincomplete/"
    basename = "ZZ4lAnalysis.root"
    min = 0.
    max = 1.
    bins = 100
    units = ""
    normalizationincludesfailedevents = True

    def __init__(self, title, color, *CJLSTdirs):
        self.filenames = [os.path.join(self.maindir, dir, self.basename) for dir in CJLSTdirs]
        self.title = title
        self.color = color
        self.__h = None

    def h(self):
        if self.__h is not None:
            return self.__h
        print self.title
        t = ROOT.TChain("ZZTree/candTree")
        for filename in self.filenames:
            print filename, t.GetEntries()
            t.Add(filename)
        pvbf = array.array('f', [0])
        phjj = array.array('f', [0])
        MC_weight = array.array('f', [1])
        t.SetBranchAddress("pvbf_VAJHU_old", pvbf)
        t.SetBranchAddress("phjj_VAJHU_old", phjj)

        h = ROOT.TH1F("h"+self.title, "D_{jet}", self.bins, self.min, self.max)

        length = t.GetEntries()
        sumofweights = 0
        for i in range(length):
            t.GetEntry(i)

            wt = MC_weight[0]

            if pvbf[0] >= 0 and phjj[0] >= 0 and not (pvbf[0] == phjj[0] == 0):

                try:
                    Djet = (pvbf[0] / (pvbf[0] + phjj[0]))
                except ZeroDivisionError:
                    t.Show(i)
                    raise

                h.Fill(Djet, wt)
                sumofweights += wt

            elif self.normalizationincludesfailedevents:
                sumofweights += wt

            if (i+1) % 10000 == 0 or i+1 == length:
                print (i+1), "/", length

        h.SetLineColor(self.color)
        h.SetLineWidth(3)
        h.Scale(1.0/sumofweights)

        self.__h = h
        return h

    def addtolegend(self, tlegend):
        tlegend.AddEntry(self.h(), self.title, "l")

def makeDjetplots(*plots):
    c1 = ROOT.TCanvas()
    legend = ROOT.TLegend(0.6, 0.7, 0.9, 0.9)
    drawoption = ""
    hstack = ROOT.THStack("hstack", "D_{jet}")
    max, min, bins, units = None, None, None, None
    for plot in plots:
        hstack.Add(plot.h())
        plot.addtolegend(legend)
        if max is None:
            max, min, bins, units = plot.max, plot.min, plot.bins, plot.units
        assert (max, min, bins, units) == (plot.max, plot.min, plot.bins, plot.units)
    hstack.Draw("nostack")
    hstack.GetXaxis().SetTitle("D_{jet}")
    hstack.GetYaxis().SetTitle("fraction of events / %s%s" % ((max-min)/bins, " "+units if units else ""))
    legend.Draw()
    c1.SaveAs("~/www/TEST/test.png")

if __name__ == "__main__":
    plots = (
             Plot("VBF",  1,              "VBFH125"),
             Plot("H+jj", 2,              "ggH125"),
             Plot("ZH",   ROOT.kGreen-6,  "ZH125"),
             Plot("WH",   3,              "WplusH125", "WminusH125"),
             Plot("ttH",  4,              "ttH125"),
             #Plot("qqZZ", 6,              "???"),
             Plot("ggZZ", ROOT.kViolet-1, "ggZZ2e2mu", "ggZZ2e2tau", "ggZZ2mu2tau", "ggZZ4e", "ggZZ4mu", "ggZZ4tau"),
            )
    makeDjetplots(*plots)
