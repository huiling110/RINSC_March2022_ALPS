# Author: Thorben Quast, thorben.quast@cern.ch
# Date: 10 September 2021
import sys
sys.path.append('/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/plots/')

import common as cm
ROOT = cm.ROOT
ROOT.gROOT.SetBatch(True)
cm.setup_style()

import os
thisdir = os.path.dirname(os.path.realpath(__file__))
from copy import deepcopy
from common.util import *

#main draws the overlay of IV of different measurement with respect to the same channel

#export DATA_DIR=/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/data/
def main():
    # inputRootFolder = '/eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/rootFile/' 
    #input folder:  /eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/rootFile/ copyied frome /home/data/hgsensor_cv/RINSC_March2022_ALPS/ in plpcd15
    inputRootFolder = '/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/data/'
    plotsDir = 'output/' 

    #measurement specifics
    _measID = "8in_198ch_2019_N4790_21_4E15_neg40degC"
    CHANNEL = 101


    name = "annealing_IV_ch%s" %  CHANNEL
    #prepare the canvas
    canvas = ROOT.TCanvas("Canvas" + name, "canvas" + name, cm.default_canvas_width, cm.default_canvas_height)
    # I see, the commen module provides some ploting uniformity
    cm.setup_canvas(canvas, cm.default_canvas_width, cm.default_canvas_height)
    # ???setup_canvas function definition in __init__.py? this is a bit wield. should be in a .py file under commen
    canvas.Divide(1)
    pad = canvas.GetPad(1)
    cm.setup_pad(pad)
    pad.cd()
    #we are just using one pad in canvas, no need to go through all the hassle here
    #???plot has no title

    graphs = []
    legend1 = ROOT.TLegend(*cm.calc_legend_pos(1+1, x1=0.2, x2=0.5, y2=0.85))
    legend2 = ROOT.TLegend(*cm.calc_legend_pos(4, x1=0.6, x2=0.9, y2=0.34))
    cm.setup_legend(legend1)
    cm.setup_legend(legend2)
    #this seems no bad

    colors = [ROOT.kBlack, ROOT.kCyan+1, ROOT.kBlue+1, ROOT.kViolet+1, ROOT.kGreen-1, ROOT.kRed+1, ROOT.kTeal, ROOT.kAzure, ROOT.kMagenta, ROOT.kOrange]

    for drawindex, postfix in enumerate(["_1MOhm", "_10minAnnealing", "_20minAnnealing", "_30minAnnealing", "_40minAnnealing", "_50minAnnealing", "_60minAnnealing", "_85minAnnealing", "_95minAnnealing", "_110minAnnealing"]):
        measID = _measID+postfix
        label = "no additional annealing" if postfix=="" else postfix.replace("_", "").replace("minAnnealing", " min at 60^{#circ}C")
        # retrieve paths of processed files as input
        print(_measID)
        print(postfix)
        #Resuts folder: /eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_Winter2022_ALPS/
        # infile = ROOT.TFile(os.path.join( os.environ["DATA_DIR"], "iv/channelIV/%s/TGraphErrors.root" % (measID)), "READ")
        inFileName = inputRootFolder + 'iv/channelIV/{}/TGraphErrors.root'.format(measID)
        infile = ROOT.TFile( inFileName, "READ" )


        gr = deepcopy(infile.Get("IV_uncorrected_channel%i" % CHANNEL))
        infile.Close()

        #apply scale
        scale = 1.
        scale_graph(gr, 1.)

        cm.setup_graph(gr)
        cm.setup_x_axis(gr.GetXaxis(), pad, {"Title": "U_{bias} (V)"})
        cm.setup_y_axis(gr.GetYaxis(), pad, {"Title": "I_{pad %i, -40^{#circ}C} (#muA)" % CHANNEL})	

        gr.SetMarkerStyle({0: 20, 1: 25, 2: 22, 3: 23, 4: 24, 5: 25, 6: 26, 7: 27, 8: 29, 9: 30}[drawindex])
        gr.SetLineStyle(1+drawindex)
        gr.SetLineColor(colors[drawindex])
        gr.SetMarkerColor(colors[drawindex])

        if drawindex==0:
            gr.SetTitle(label + ", pad %i" % CHANNEL)
            gr.GetXaxis().SetLimits(0., 900.)
            gr.Draw("APL")
            gr.GetXaxis().SetLimits(0., 900.)
            gr.GetYaxis().SetRangeUser(0., 5.5)
        else:
            gr.Draw("PLSAME")
        
        if drawindex==0:
            legend1.AddEntry(gr, label, "pl")
        else:
            legend2.AddEntry(gr, label, "pl")

        graphs.append(gr)
        drawindex+=1

    legend1.Draw()
    legend2.Draw()

    canvas.cd()
    # cms label
    cms_labels = cm.create_cms_labels()
    cms_labels.Draw()

    # campaign label
    campaign_label = cm.create_campaign_label()
    campaign_label.Draw()

    _label_text = "rd. 5, LD, 200 #mum, ~4E15/cm^{2}"
    label = ROOT.TLatex(0.24, 0.82, _label_text)
    cm.setup_label(label, {"TextFont": 73})

    legend1.SetHeader(_label_text)
    #label.Draw()
    pad.SetGrid(True)
    
    
    #save pdf
    # canvas.Print(os.path.join(thisdir, "{}.pdf".format(name)))
    # canvas.Print(os.path.join(thisdir, "{}.png".format(name)))
    #??Print? SaveAs()
    canvas.Print( plotsDir + '{}.pdf'.format(name) )
    canvas.Print( plotsDir + '{}.png'.format(name) )


if __name__=='__main__':
    main()