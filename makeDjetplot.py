import array
import os
import ROOT
import style

class Plot:
    maindir = "root://lxcms03://data3/Higgs/160111_ggZZincomplete/"
    basename = "ZZ4lAnalysis.root"

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
        t.SetBranchAddress("pvbf_VAJHU_old", pvbf)
        t.SetBranchAddress("phjj_VAJHU_old", phjj)

        h = ROOT.TH1F("h"+self.title, "D_{jet}", 100, 0, 1)

        length = t.GetEntries()
        for i in range(length):
            t.GetEntry(i)
            if pvbf[0] >= 0 and phjj[0] >= 0 and not (pvbf[0] == phjj[0] == 0):
                try:
                    Djet = (pvbf[0] / (pvbf[0] + phjj[0]))
                except ZeroDivisionError:
                    t.Show(i)
                    raise
                h.Fill(Djet)
            if (i+1) % 10000 == 0 or i+1 == length:
                print (i+1), "/", length

        h.SetLineColor(self.color)

        self.__h = h
        return h

    def addtolegend(self, tlegend):
        tlegend.AddEntry(self.h(), self.title, "l")

def makeDjetplots(*plots):
    c1 = ROOT.TCanvas()
    legend = ROOT.TLegend(0.6, 0.7, 0.9, 0.9)
    drawoption = ""
    for plot in plots:
        plot.h().Draw(drawoption)
        if "same" not in drawoption: drawoption += "same"
        plot.addtolegend(legend)
    legend.Draw()
    c1.SaveAs("test.png")

if __name__ == "__main__":
    plots = (
             Plot("VBF",  1,              "VBFH125"),
             Plot("H+jj", 2,              "ggH125"),
             Plot("ZH",   ROOT.kGreen-6,  "ZH125"),
             Plot("WH",   3,              "WplusH125", "WminusH125"),
             Plot("ttH",  4,              "ttH125"),
             #Plot("qqZZ", 6,              "VBF125"),
             Plot("ggZZ", ROOT.kViolet-1, "ggZZ2e2mu", "ggZZ2e2tau", "ggZZ2mu2tau", "ggZZ4e", "ggZZ4mu", "ggZZ4tau"),
            )
    makeDjetplots(*plots)
