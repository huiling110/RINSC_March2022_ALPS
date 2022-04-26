# Author: Thorben Quast, thorben.quast@cern.ch
# Date: 10 September 2021
import sys
sys.path.append('/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/plots/')

import common as cm
ROOT = cm.ROOT
ROOT.gROOT.SetBatch(True)
cm.setup_style()

import os
from copy import deepcopy
from common.util import *

def drawMultipleChannls( ):
    # channelList = [15, 25, 35, 45, 55, 67, 77, 87, 97, 105, 115, 123, 133, 145, 157, 167, 177, 187]
    channelList = [ 
                   1, 
                   #12, 13, 14, 15, 16, 17, 18, 196, 197, 198, 199, 
                   100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
    for ichannel in channelList:
        main( ichannel )


#main draws the overlay of IV of different measurement with respect to the same channel
#export DATA_DIR=/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/data/
def main(
    
    CHANNEL = 101
    ):
    
    # inputRootFolder = '/eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/rootFile/' 
    #input folder:  /eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/rootFile/ copyied frome /home/data/hgsensor_cv/RINSC_March2022_ALPS/ in plpcd15
    # inputRootFolder = '/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/data/'
    inputRootFolder = '/eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/rootFile/channelIV/'
    plotsDir = 'output/' 

    #measurement specifics
    # _measID = "8in_198ch_2019_N4790_21_4E15_neg40degC"
    # repeatedMeasureNames = ["_1MOhm", "_10minAnnealing", "_20minAnnealing", "_30minAnnealing", "_40minAnnealing", "_50minAnnealing", "_60minAnnealing", "_85minAnnealing", "_95minAnnealing", "_110minAnnealing"]
    _measID = '8in_198ch_2019_N4790_21_4E15'
    repeatedMeasureNames = [ '_neg37degC_tscan', '_neg38degC_tscan','_neg39degC_tscan', '_neg40degC_tscan', '_neg41degC_tscan', '_neg42degC_tscan' ]
    
    
    # name = "annealing_IV_ch%s" %  CHANNEL
    name = 'tempareture_effect_{}'.format( CHANNEL )
    
    
    
    
    
    
    
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

    for drawindex, postfix in enumerate( repeatedMeasureNames ):
        measID = _measID+postfix
        label = "no additional annealing" if postfix=="" else postfix.replace("_", "").replace("minAnnealing", " min at 60^{#circ}C")
        # retrieve paths of processed files as input
        print(_measID)
        print(postfix)
        #Resuts folder: /eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_Winter2022_ALPS/
        # inFileName = inputRootFolder + 'iv/channelIV/{}/TGraphErrors.root'.format(measID)
        inFileName = inputRootFolder + '{}/TGraphErrors.root'.format(measID)
        infile = ROOT.TFile( inFileName, "READ" )


        if ( not infile.Get("IV_uncorrected_channel%i" % CHANNEL) ):
            print( 'channel not measured: ', CHANNEL )
            # break
            continue
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
    #??Print? SaveAs()
    canvas.Print( plotsDir + '{}_{}.pdf'.format( _measID, name) )
    canvas.Print( plotsDir + '{}_{}.png'.format( _measID, name) )


if __name__=='__main__':
    # main()
    drawMultipleChannls()