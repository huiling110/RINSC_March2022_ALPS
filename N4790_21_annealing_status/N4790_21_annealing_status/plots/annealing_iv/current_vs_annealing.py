# Author: Thorben Quast, thorben.quast@cern.ch
# Date: 10 September 2021

import sys
sys.path.append('/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/N4790_21_annealing_status/N4790_21_annealing_status/plots/')
import pandas as pd
import numpy as np

import common as cm
ROOT = cm.ROOT
ROOT.gROOT.SetBatch(True)
cm.setup_style()

import os
thisdir = os.path.dirname(os.path.realpath(__file__))

from copy import deepcopy
from common.util import *


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--EVALVOLTAGE", type=int, help="", default=600, required=False)
args = parser.parse_args()
EVALVOLTAGE = args.EVALVOLTAGE

def main():
    inputRootFolder = '/eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/rootFile/channelIV/'
    HEXPLOT_DIR = '/afs/cern.ch/work/h/hhua/HGCal_sensorTest/Hexplot/HGCAL_sensor_analysis/'
    # plotsDir = 'output/'
    plotsDir = '/afs/cern.ch/work/h/hhua/HGCal_sensorTest/RINSC_March2022_ALPS/slides/plots/' 
    #measurement specifics
    # _measID = "8in_198ch_2019_N4790_21_4E15_neg40degC"
    _measID = '8in_198ch_2019_N4790_09_4E15_neg40degC'
    
    
    
    # true_additional_annealing = {
    #     0: 0,
    #     10: 10.9,
    #     20: 22.4,
    #     30: 34.1,
    #     40: 45.5,
    #     50: 55.1,
    #     60: 66.6,
    #     85: 86.5,
    #     95: 97.9,
    #     110: 115.1
    # }
    #???true additional_annealing
    #/eos/user/h/hgsensor/HGCAL_test_results/Results/RINSC_March2022_ALPS/HPK_8in_198ch_2019_N4790_09_neg40degC_30minAnnealing/Annealing/annealing_4790_09_0_to_30min.csv
    true_additional_annealing = {#for N4790_09
        0:0,
       30:28,
       60:59.7 
    }


    name = "annealing_current"
    if EVALVOLTAGE == -1:
        name += "_atUdep"
    hexplot_geo_file_path = HEXPLOT_DIR + 'geo/' + 'hex_positions_HPK_198ch_8inch_edge_ring_testcap.txt' 
    #???it seems we just need this txt file from the HEXPLOT package
    #load geometry mapping
    geo_mapping = pd.DataFrame(np.genfromtxt(open(hexplot_geo_file_path, "r"), skip_header=7, usecols=(0, 1, 2, 3), dtype=[("channel", "i4"), ("x", "f8"), ("y", "f8"), ("type", "i4")]))#???to learn
    
    #prepare the canvas
    canvas = ROOT.TCanvas("Canvas" + name, "canvas" + name, cm.default_canvas_width, cm.default_canvas_height)
    cm.setup_canvas(canvas, cm.default_canvas_width, cm.default_canvas_height)
    canvas.Divide(1)
    pad = canvas.GetPad(1)
    cm.setup_pad(pad)
    pad.cd()


    # determine per-channel leakage current at common voltage (EVALVOLTAGE)
    tmp_data = []

    # for annealing in [0, 10, 20, 30, 40, 50, 60, 85, 95, 110]:
    for annealing in [0, 30, 60]:

        measID = _measID
        if annealing > 0:
            postfix = "_%iminAnnealing" % annealing
        else:
            # postfix = "_1MOhm"
            postfix = ""
        measID = measID+postfix

        # retrieve paths of processed files as input
        inFileName = inputRootFolder + '{}/TGraphErrors.root'.format(measID)
        infile = ROOT.TFile( inFileName, "READ" )

        for CHANNEL in range(1, 199):
            geotype = np.array(geo_mapping.type[geo_mapping.channel==CHANNEL])[0]
            if geotype!=0:  #not a full cell
                continue            
            try:
                gr = infile.Get("IV_uncorrected_channel%i" % CHANNEL)
                gr.GetXaxis().SetTitle(
                    "Effective bias voltage (HV resistance-corrected) [V]")
            except:
                continue

            _EVALVOLTAGE = EVALVOLTAGE

            lfti = ROOT.TF1("pol1", "pol1", _EVALVOLTAGE-120., _EVALVOLTAGE+120.)

            gr.Fit(lfti, "RQ")

            # compute ratios and save as file
            lcurr = lfti.Eval(_EVALVOLTAGE)

            # position not really useful because coordinate system center not quite in center
            tmp_data.append((annealing, CHANNEL, EVALVOLTAGE, lcurr))

    _df = pd.DataFrame(tmp_data, columns=["annealingMin", "channel", "U", "I"])

    legend1 = ROOT.TLegend(*cm.calc_legend_pos(5+1, x1=0.2, x2=0.9, y2=0.92))
    cm.setup_legend(legend1)
    legend1.SetNColumns(4)

    #create the graphs
    graphs = {}
    for draw_index, _channel in enumerate(_df.channel.unique()):
        if (draw_index % 8) != 3:
            continue

        channel_data = _df[_df.channel==_channel]
        annealingMin = np.array(channel_data.annealingMin)
        I = np.array(channel_data.I)
        I = I/I[0]*100.
        graphs[_channel] = ROOT.TGraph()
        NGraphs = len([key for key in graphs])
        for i in range(len(channel_data)):
            graphs[_channel].SetPoint(graphs[_channel].GetN(), true_additional_annealing[annealingMin[i]], I[i]*1.)
        
        cm.setup_graph(graphs[_channel])
        graphs[_channel].SetMarkerStyle(19+NGraphs%11)
        graphs[_channel].SetMarkerColor((NGraphs-1)%9+1)
        graphs[_channel].SetLineColor((NGraphs-1)%9+1)


        graphs[_channel].GetYaxis().SetRangeUser(85., 108.)
        xaxis_title = "t = Addtional annealing at +60^{#circ} C (min)"
        cm.setup_x_axis(graphs[_channel].GetXaxis(), pad, {"Title": xaxis_title, "TitleOffset": 0.90*graphs[_channel].GetXaxis().GetTitleOffset()})
        if EVALVOLTAGE == -1:
            yaxis_title = "I_{pad, -40^{#circ}C}(t, U_{dep})/I_{pad, -40^{#circ}C}(t=0, U_{dep}) [%]"
        else:
            yaxis_title = "I_{pad, -40^{#circ}C}(t, %i V)/I_{pad, -40^{#circ}C}(t=0, %i V)" % (EVALVOLTAGE, EVALVOLTAGE)+"[%]"

        cm.setup_y_axis(graphs[_channel].GetYaxis(), pad, {"Title": yaxis_title})
            
        if NGraphs==1:
            graphs[_channel].Draw("APL")
        else:
            graphs[_channel].Draw("PLSAME")
        
        legend1.AddEntry(graphs[_channel], "pad %i" % _channel)

        if NGraphs == 20:
            break
        

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

    legend1.Draw()

    pad.SetGrid(True)
    #save pdf
    canvas.Print( plotsDir + '{}_{}_{}.pdf'.format( _measID, name, EVALVOLTAGE) )
    canvas.Print( plotsDir + '{}_{}_{}.png'.format( _measID, name, EVALVOLTAGE) )


if __name__=='__main__':
    main()
