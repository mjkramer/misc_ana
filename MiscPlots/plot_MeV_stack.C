//void plot_MeV_stack(int i=0){
{
    int i=2;
  //gStyle->
  //gStyle->SetPadTickX(0);
  //gStyle->SetPadTickY(0);
  gStyle->SetOptStat(000000);
    
    float livetime[3][8]={{186.786,186.786,187.191,0.,187.666,187.666,187.666,0.},{1349.834,1349.834,1353.601,1353.601,1351.874,1351.874,1351.874,1351.874},{0.,200.995,200.441,200.441,200.071,200.071,200.071,200.071}};
    float dmc_eff[3][8]={{0.9739,0.9742,0.9754,0.,0.9743,0.9740,0.9739,0.},{0.9745,0.9748,0.9759,0.9757,0.9762,0.9762,0.9760,0.9758},{1.,0.9751,0.9761,0.9759,0.9764,0.9763,0.9763,0.9760}};
    float muon_eff[3][8]={{0.82322,0.82048,0.85735,1.,0.98109,0.98108,0.98074,1.},{0.8265,0.8223,0.8575,0.8568,0.9831,0.9831,0.9829,0.9831},{1.,0.8218,0.8586,0.8567,0.9847,0.9847,0.9846,0.9847}};
    float mass[8]={19941,19966,19891,19945,19913,19991,19892,19931};
    
    //values from ./ShapeFit/Inputs files

  const Int_t Nstage = 3;
  const Int_t Ndet = 8;
      const Int_t Nhalls = 3;
    Char_t name[1024];
    Int_t EHnum[Ndet] = {0,0,1,1,2,2,2,2};
    
    /*
    TFile* pred_file=new TFile("../../outputs/prediction_official_rate_shape.root","READ");


    Int_t EHnum[Ndet] = {0,0,1,1,2,2,2,2};
    
    //load prediction
    TH1F* Pred_sum[Nhalls];
    
    for(int istage=0; istage<Nstage;++istage){
        for(int idet=0; idet<Ndet;++idet){
            sprintf(name,"h_nominal_stage%i_ad%i",istage+1,idet+1);
            TH1F* h_temp=(TH1F*) pred_file->Get(name);
            if(istage==0 && idet==0){
                for(int ihall=0; ihall<Nhalls; ++ihall){
                    Pred_sum[ihall]=(TH1F*)h_temp->Clone();
                    Pred_sum[ihall]->Reset();
                }
            }
            Pred_sum[EHnum[idet]]->Add(h_temp);
        }
    }
    for(int ihall=0; ihall<Nhalls; ++ihall){
        for(int ibin=0; ibin<Pred_sum[ihall]->GetNbinsX();++ibin){
            Pred_sum[ihall]->SetBinContent(ibin+1, Pred_sum[ihall]->GetBinContent(ibin+1) / Pred_sum[ihall]->GetBinWidth(ibin+1) );
            
        }
        Pred_sum[ihall]->Scale(0.947);
    }
    

*/
    

  TFile * f = new TFile("../../ShapeFit/fit_result_files/fit_shape_2d_2017Model_P17B_IHEP_BCWbin.root","READ");
 
  TString EHname[Ndet] = {"eh1","eh1","eh2","eh2","eh3","eh3","eh3","eh3"};
  TString ADname[Ndet] = {"ad1","ad2","ad1","ad2","ad1","ad2","ad3","ad4"};

  TH1F * Data[Nstage][Ndet];
  TH1F * Acc[Nstage][Ndet];
  TH1F * Li9[Nstage][Ndet];
  TH1F * Amc[Nstage][Ndet];
  TH1F * Fn[Nstage][Ndet];
  TH1F * Aln[Nstage][Ndet];

  for(Int_t istage=0; istage<Nstage;istage++){
    for(Int_t idet=0; idet<Ndet;idet++){
      //Data
      sprintf(name,"CorrIBDEvts_stage%i_AD%i",istage,idet+1);
      Data[istage][idet] = (TH1F*)f->Get(name);
        
        Data[istage][idet]->Scale(livetime[istage][idet]*muon_eff[istage][idet]*dmc_eff[istage][idet]*mass[idet]/mass[0]);
      
      sprintf(name,"CorrAccEvtsSpec_stage%i_AD%i",istage,idet+1);
      Acc[istage][idet] = (TH1F*)f->Get(name);

      sprintf(name,"CorrLi9EvtsSpec_stage%i_AD%i",istage,idet+1);
      Li9[istage][idet] = (TH1F*)f->Get(name);

      sprintf(name,"CorrAmcEvtsSpec_stage%i_AD%i",istage,idet+1);
      Amc[istage][idet] = (TH1F*)f->Get(name);

      sprintf(name,"CorrFnEvtsSpec_stage%i_AD%i",istage,idet+1);
      Fn[istage][idet] = (TH1F*)f->Get(name);

      sprintf(name,"CorrAlnEvtsSpec_stage%i_AD%i",istage,idet+1);
      Aln[istage][idet] = (TH1F*)f->Get(name);

    }
  }

  //Sum over 6AD and 8AD period for all AD within the same hall

  TH1F * Data_sum[Nhalls];
  TH1F * Data_sum_inpad[Nhalls];
  TH1F * Acc_sum[Nhalls];
  TH1F * Li9_sum[Nhalls];
  TH1F * Amc_sum[Nhalls];
  TH1F * Fn_sum[Nhalls];
  TH1F * Aln_sum[Nhalls];
 
  //Prepare histograms
  for (Int_t ihall=0; ihall<Nhalls; ihall++){
    Data_sum[ihall] = (TH1F*)Data[0][0]->Clone();
    Data_sum[ihall]->Reset();

    Acc_sum[ihall] = (TH1F*)Acc[0][0]->Clone();
    Acc_sum[ihall]->Reset();

    Li9_sum[ihall] = (TH1F*)Li9[0][0]->Clone();
    Li9_sum[ihall]->Reset();

    Amc_sum[ihall] = (TH1F*)Amc[0][0]->Clone();
    Amc_sum[ihall]->Reset();

    Fn_sum[ihall] = (TH1F*)Fn[0][0]->Clone();
    Fn_sum[ihall]->Reset();

    Aln_sum[ihall] = (TH1F*)Aln[0][0]->Clone();
    Aln_sum[ihall]->Reset();
    
  }

  //Int_t EHnum[Ndet] = {0,0,1,1,2,2,2,2};
 for(Int_t istage=0; istage<Nstage;istage++){
    for(Int_t idet=0; idet<Ndet;idet++){
      
      Data_sum[EHnum[idet]]->Add(Data[istage][idet]);
      Acc_sum[EHnum[idet]]->Add(Acc[istage][idet]);
      Li9_sum[EHnum[idet]]->Add(Li9[istage][idet]);
      Amc_sum[EHnum[idet]]->Add(Amc[istage][idet]);
      Fn_sum[EHnum[idet]]->Add(Fn[istage][idet]);
      Aln_sum[EHnum[idet]]->Add(Aln[istage][idet]);
      
    }
  }

 //Divide by bin width
 for(Int_t ihall=0; ihall<Nhalls;ihall++){
   
   Data_sum[ihall]->SetTitle(";Reconstructed Positron Energy [MeV];Events / MeV");
   Data_sum[ihall]->GetXaxis()->CenterTitle();
   Data_sum[ihall]->GetYaxis()->CenterTitle();
   
   //Data_sum[ihall]->SetMaximum(18);
   Data_sum[ihall]->SetMinimum(1);
   Data_sum[ihall]->SetTitleOffset(1.1,"Y");
   Data_sum[ihall]->SetTitleSize(0.05,"XY");
   Data_sum[ihall]->SetLabelSize(0.05,"XY");
   Data_sum[ihall]->GetXaxis()->SetRangeUser(0.7,12);
   
     
     if(i==0) Data_sum[ihall]->GetYaxis()->SetRangeUser(0.,5.2e5);
     if(i==1) Data_sum[ihall]->GetYaxis()->SetRangeUser(0.,4.8e5);
     if(i==2) Data_sum[ihall]->GetYaxis()->SetRangeUser(0.,1.4e5);
     
     
     
   //  Data_sum[ihall]->GetXaxis()->SetRangeUser(0.7,11.9);
   Data_sum[ihall]->SetMarkerStyle(20);
   Data_sum[ihall]->SetMarkerSize(0.9);
   Data_sum[ihall]->SetLineColor(1);
   Data_sum[ihall]->SetLineWidth(2);
  
   Acc_sum[ihall]->SetLineColor(4);
   Acc_sum[ihall]->SetLineWidth(2);
   Acc_sum[ihall]->SetFillColor(4);
   Acc_sum[ihall]->SetFillStyle(3001);
   
   Amc_sum[ihall]->SetLineColor(6);
   Amc_sum[ihall]->SetLineWidth(2);
   Amc_sum[ihall]->SetFillColor(6);
   Amc_sum[ihall]->SetFillStyle(3003);
  
   Li9_sum[ihall]->SetLineColor(41);
   Li9_sum[ihall]->SetLineWidth(2);
   Li9_sum[ihall]->SetFillColor(41);
   Li9_sum[ihall]->SetFillStyle(3002);
   
   Aln_sum[ihall]->SetLineColor(8);
   Aln_sum[ihall]->SetLineWidth(2);
   Aln_sum[ihall]->SetFillColor(8);
   Aln_sum[ihall]->SetFillStyle(3004);

   Fn_sum[ihall]->SetLineColor(17);
   Fn_sum[ihall]->SetLineWidth(2);
   Fn_sum[ihall]->SetFillColor(17);
   Fn_sum[ihall]->SetFillStyle(3005);

  for (Int_t ibin = 1; ibin <= 26; ibin++){
	Data_sum[ihall]->SetBinContent(ibin, Data_sum[ihall]->GetBinContent(ibin) / Data_sum[ihall]->GetBinWidth(ibin) );
      
      //cout<<Data_sum[ihall].GetBinContent(ibin) / Data_sum[ihall].GetBinWidth(ibin) <<endl;

	Acc_sum[ihall]->SetBinContent(ibin, Acc_sum[ihall]->GetBinContent(ibin) / Acc_sum[ihall]->GetBinWidth(ibin) );
	Li9_sum[ihall]->SetBinContent(ibin, Li9_sum[ihall]->GetBinContent(ibin) / Li9_sum[ihall]->GetBinWidth(ibin) );
	Amc_sum[ihall]->SetBinContent(ibin, Amc_sum[ihall]->GetBinContent(ibin) / Amc_sum[ihall]->GetBinWidth(ibin) );
	Fn_sum[ihall]->SetBinContent(ibin, Fn_sum[ihall]->GetBinContent(ibin) / Fn_sum[ihall]->GetBinWidth(ibin) );
	Aln_sum[ihall]->SetBinContent(ibin, Aln_sum[ihall]->GetBinContent(ibin) / Aln_sum[ihall]->GetBinWidth(ibin) );
      
      
      
    Data_sum[ihall]->SetBinContent(ibin,Data_sum[ihall]->GetBinContent(ibin)
                                   +Acc_sum[ihall]->GetBinContent(ibin)
                                   +Li9_sum[ihall]->GetBinContent(ibin)
                                   +Amc_sum[ihall]->GetBinContent(ibin)
                                   +Fn_sum[ihall]->GetBinContent(ibin)
                                   +Aln_sum[ihall]->GetBinContent(ibin)
                                   );
  }
    
  }


 THStack Stack[Nhalls];
    
     cout<<"here"<<endl;

 //Add stack
 for(Int_t ihall=0; ihall<Nhalls;ihall++){
   
   Stack[ihall].Add(Fn_sum[ihall]);
   Stack[ihall].Add(Aln_sum[ihall]);
   Stack[ihall].Add(Amc_sum[ihall]);
   Stack[ihall].Add(Li9_sum[ihall]);
   Stack[ihall].Add(Acc_sum[ihall]);
 }

 /*
  h_pred->SetLineColor(kRed+1);
  h_pred->SetLineStyle(1);
  h_pred->SetLineWidth(2);
  h_pred->SetFillStyle(0);
  h_pred_ratio->SetLineColor(kRed+1);
  h_pred_ratio->SetLineStyle(1);
  h_pred_ratio->SetLineWidth(2);
  h_pred_ratio->SetFillStyle(0);

  h_pred_e->SetLineColor(kRed+1);
  h_pred_e->SetLineWidth(2);
  h_pred_e->SetFillColor(kRed-7); 
  h_pred_ratio_e->SetLineColor(kRed+1);
  h_pred_ratio_e->SetLineWidth(2);
  h_pred_ratio_e->SetFillColor(kRed-7);
  
  TH1D * h_pred_null = f->Get(Form("h_final_pred_null_%s_mode3_0",stage.Data()));
  TH1D * h_pred_null_ratio = f->Get(Form("h_final_pred_null_ratio_%s_mode3_0",stage.Data()));
  h_pred_null->SetLineWidth(2);
  h_pred_null_ratio->SetLineWidth(2);
  */
  TCanvas * c1 = new TCanvas ("c1","c1",800,600);

  //TPad * c1_1 = new TPad("c1_1","c1_1",0.0,0.4,1.0,1.0);
  //  c1_1->SetTopMargin(0);
  c1->SetTopMargin(0.05);
  c1->SetBottomMargin(0.11);
  c1->SetRightMargin(0.03);
  c1->SetLeftMargin(0.12);
  //TPad * c1_2 = new TPad("c1_2","c1_2",0.0,0.0,1.0,0.4);
  //c1_2->SetTopMargin(0);
  //c1_2->SetRightMargin(0.02);
  //c1_2->SetLeftMargin(0.15);
  //c1_2->SetBottomMargin(0.16);

  c1->Draw();
    

    
  //c1_2->Draw();

  //c1->SetLogy(1);

  //Int_t i = 2;


  //TH1F * Amc_sum_2 = Amc_sum[ihall]->Clone();
  //Amc_sum_2->SetFillColor(3);
  //Amc_sum_2->SetFillStyle(3005);
  //Amc_sum_2->Draw("same F");

  /*
  h_ILL->SetMarkerStyle(20);
  h_ILL->SetMarkerSize(0.7);
  h_ILL->SetLineWidth(2);
  h_ILL->SetLineColor(4);
  h_ILL->Draw("same");

  h_AbInitio->SetMarkerStyle(20);
  h_AbInitio->SetMarkerSize(0.7);
  h_AbInitio->SetLineWidth(2);
  h_AbInitio->SetLineColor(2);
  h_AbInitio->Draw("same");
  */
  /*
   h_pred_null->Draw("hist same");
  h_pred_e->SetLineStyle(1);
  h_pred_e->Draw("e2 same");
  h_pred->Draw("hist same");
  */
  // h_pred2->SetFillStyle(0);
  // h_pred2->SetLineColor(4);
  // h_pred2->Draw("hist same");
     cout<<"here"<<endl;
  Data_sum[i]->Draw("p");
     cout<<"here"<<endl;
  Data_sum[i]->Draw("same");
  Stack[i]->Draw("same");
    c1->SetGridy();
    c1->SetGridx();
  c1->RedrawAxis();
    c1->SetTopMargin(0.1);
    
   // Pred_sum[i]->Draw("SAME");

  //TLegend * leg = new TLegend (0.715,0.6115,0.965,0.862);
    TLegend * leg = new TLegend (0.715,0.15,0.96,0.5);
    
    sprintf(name,"EH%d data",i+1);
    
  leg->AddEntry(Data_sum[i],name,"lp");
  leg->AddEntry(Acc_sum[i],"Accidental","f");
  leg->AddEntry(Amc_sum[i],"^{241}Am-^{13}C","f");
  leg->AddEntry(Li9_sum[i],"^{9}Li / ^{8}He","f");  
  leg->AddEntry(Aln_sum[i],"^{13}C(#alpha,n)^{16}O","f");
  leg->AddEntry(Fn_sum[i],"Fast neutrons","f");

  //leg->SetBorderSize(0);
  //leg->SetFillStyle(0);
  leg->SetFillColor(kWhite);
  leg->SetTextSize(0.04);
  leg->Draw();
    
    
    TH1F* Data_sum_copy[Nhalls];
    
    for(int ihall=0; ihall<Nhalls;++ihall){
        char name2[64];
        sprintf(name2,"Data_sum_copy_EH%d",ihall+1);
        Data_sum_copy[i]=(TH1F*)Data_sum[i]->Clone(name2);
        Data_sum_copy[i]->SetTitle(";;");
    }
    
    
    TPad* inpad=new TPad("inpad","inpad",0.5,0.51,1.,0.93);
    inpad->SetRightMargin(0.08);
    inpad->Draw("SAME");
    inpad->cd();
    inpad->SetLineColor(kBlack);
    inpad->SetLineWidth(4);
    inpad->SetLogy();
    inpad->SetGridx();
    inpad->SetGridy();
    Data_sum_copy[i]->Draw("p");
    Data_sum_copy[i]->SetMarkerSize(0.4);
    if(i==0) Data_sum_copy[i]->GetYaxis()->SetRangeUser(80.,650000);
    if(i==1) Data_sum_copy[i]->GetYaxis()->SetRangeUser(80.,650000);
    if(i==2) Data_sum_copy[i]->GetYaxis()->SetRangeUser(10.,200000);
    Data_sum_copy[i]->SetLineWidth(1);
    Stack[i]->Draw("same");
    inpad->SetBorderSize(1);
    inpad->SetFillStyle(0);
    inpad->Update();
    
    sprintf(name,"./EH%d_stack.pdf",i+1);
    c1->Print(name);
    
  /*
  c1_2->cd();
  
  Data_sum[2]_ratio->SetTitle(";Antineutrino Energy (MeV);Spectra / Spectra (Huber)");
  Data_sum[2]_ratio->GetXaxis()->SetRangeUser(1.8,10);
  //  Data_sum[2]_ratio->GetXaxis()->SetRangeUser(0.7,11.9);
  Data_sum[2]_ratio->SetTitleOffset(0.75,"Y");
  //  Data_sum[2]_ratio->SetTitleOffset(-0.2,"X");
  h_Huber_ratio->GetXaxis()->CenterTitle();
  h_Huber_ratio->GetYaxis()->CenterTitle();
  h_Huber_ratio->SetTitleSize(0.075,"X");
  h_Huber_ratio->SetTitleSize(0.075,"Y");
  h_Huber_ratio->SetLabelSize(0.075,"XY");
  h_Huber_ratio->SetMinimum(0.80);
  h_Huber_ratio->SetMaximum(1.1999);
  h_Huber_ratio->Draw();
  //h_Huber_ratio->Draw("hist same");
  //h_Huber_ratio->Draw("hist same");
  // h_pred2_ratio->SetFillStyle(0);
  // h_pred2_ratio->SetLineColor(4);
  // h_pred2_ratio->Draw("hist same");
  
  h_Huber_ratio->SetMarkerStyle(20);
  h_Huber_ratio->SetMarkerSize(0.7);
  h_Huber_ratio->SetLineWidth(2);
 
  h_ILL_ratio->SetMarkerStyle(20);
  h_ILL_ratio->SetMarkerSize(0.7);
  h_ILL_ratio->SetLineWidth(2);
  h_ILL_ratio->SetLineColor(4);
  h_ILL_ratio->Draw("same");
  */
/*
  h_AbInitio_ratio->SetMarkerStyle(20);
  h_AbInitio_ratio->SetMarkerSize(0.7);
  h_AbInitio_ratio->SetLineWidth(2);
  h_AbInitio_ratio->SetLineColor(2);
  h_AbInitio_ratio->Draw("same");

 //h_Huber_ratio->Draw("e0 same");
  c1_2->SetGridy();
  c1_2->RedrawAxis("g");

*/
  //h_Huber_ratio->Draw("same");

  // TCanvas * c2 = new TCanvas ("c2","c2",600,600);
  
  // TH2D * h_mcov_orig = f->Get("h_final_covmatrix_mode3");
  // Double_t bins[37];
  // bins[0] = 0.7;
  // for (Int_t i = 1; i < 37; i++){
  //   bins[i] = 1.0 + 0.2 *(i-1);
  // }
  // TH2D * h_mcov_new = new TH2D("h_mcov_new",";Prompt energy (MeV);Prompt energy (MeV)",36,bins,36,bins);
  // for (Int_t i = 0; i < 36; i++){
  //   for (Int_t j = 0; j < 36; j++){
  //     h_mcov_new->SetBinContent(i+1,j+1,h_mcov_orig->GetBinContent(i+1,j+1));
  //   }
  // }
  // h_mcov_new->Draw("zcol");

  
}
