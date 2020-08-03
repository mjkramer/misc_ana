#include <TFile.h>
#include <TH1F.h>
#include <TTree.h>

// Branches of "results" tree
int br_site;
int br_detector;
float br_livetime_s;
float br_accDaily;
float br_li9Daily;
float br_vetoEff;
float br_dmcEff;

void init_tree(TTree* results)
{
  results->SetBranchAddress("site", &br_site);
  results->SetBranchAddress("detector", &br_detector);
  results->SetBranchAddress("livetime_s", &br_livetime_s);
  results->SetBranchAddress("accDaily", &br_accDaily);
  results->SetBranchAddress("li9Daily", &br_li9Daily);
  results->SetBranchAddress("vetoEff", &br_vetoEff);
  results->SetBranchAddress("dmcEff", &br_dmcEff);

  // To ensure that br_site is specified:
  results->GetEntry(0);
}

// Get the total count of a given type of background event. We pass a *pointer*
// to the daily rate in case it's a tree branch that updates every time we call
// GetEntry.
float total_of(TTree* results, int detector, float* dailyRate_ptr)
{
  float total = 0;

  for (int i = 0; i < results->GetEntries(); ++i) {
    results->GetEntry(i);

    if (br_detector != detector)
      continue;

    // The daily rates are "ideal", i.e., what we would measure if we had
    // "perfect" cuts (efficiency of 1). To get what we actually measure,
    // we must scale down the ideal rates according to the efficiencies of the
    // muon veto and "decoupled multiplicity cut" (DMC).
    float eff = br_vetoEff * br_dmcEff;
    total += *dailyRate_ptr * eff * br_livetime_s / (60*60*24);
  }

  return total;
}

float total_acc(TTree* results, int detector)
{
  return total_of(results, detector, &br_accDaily);
}

float total_li9(TTree* results, int detector)
{
  // Note: li9 rate is actually the same every day
  return total_of(results, detector, &br_li9Daily);
}

// Hardcoded values for *nominal* IBD selection (i.e. Ep < 12 MeV)
// (see ~mkramer/mywork/ThesisAnalysis/IbdSel/code/fit_prep/hardcoded.py)
float fastn_daily_nominal(int site)
{
  if (site == 1) return 0.843;
  if (site == 2) return 0.638;
  else return 0.053;
}

float total_fastn(TTree* results, int detector, TH1F* spectrum)
{
#define B(x) spectrum->FindBin(x)
  float scale_factor =
    spectrum->Integral(B(0.7), B(17)-1) / spectrum->Integral(B(0.7), B(12)-1);
  float daily = scale_factor * fastn_daily_nominal(br_site);
  return total_of(results, detector, &daily);
#undef B
}

TH1F* norm_acc_spec(TH1F* h_single)
{
  TH1F* h = (TH1F*) h_single->Clone();

  // The singles spectrum goes beyond 17 MeV while the IBD spectrum has a hard
  // cutoff there. Thus we must clear the bins above 17 MeV.
  for (int ibin = 1; ibin <= h->GetNbinsX(); ++ibin) {
    if (h->GetBinLowEdge(ibin) >= 17) {
      h->SetBinContent(ibin, 0);
    }
  }

  // The singles spectrum is more finely binned than the IBD spectrum
  h->Rebin(5);

  // Normalize
  h->Scale(1/h->Integral());

  return h;
}

TH1F* ibd_spec_subtracted(TFile* file, int detector)
{
  TTree* results = (TTree*) file->Get("results");
  init_tree(results);

  TH1F* h_single = (TH1F*) file->Get(Form("h_single_AD%d", detector));
  TH1F* h_acc = norm_acc_spec(h_single);

  TFile* f_li9 = new TFile("li9.root");
  TH1F* h_li9 = (TH1F*) f_li9->Get("h_li9");

  TFile* f_fastn = new TFile("fastn.root");
  auto hname_fastn = Form("h_fastn_eh%d_ad%d", br_site, detector);
  TH1F* h_fastn = (TH1F*) f_fastn->Get(hname_fastn);

  file->cd();                   // otherwise we'll end up in fastn.root

  float tot_acc = total_acc(results, detector);
  float tot_li9 = total_li9(results, detector);
  float tot_fastn = total_fastn(results, detector, h_fastn);

  TH1F* h_ibd = (TH1F*) file->Get(Form("h_ibd_AD%d", detector));
  TH1F* h_ibd_sub = (TH1F*) h_ibd->Clone(Form("%s_sub", h_ibd->GetName()));

  h_ibd_sub->Add(h_acc, -tot_acc);
  h_ibd_sub->Add(h_li9, -tot_li9);
  h_ibd_sub->Add(h_fastn, -tot_fastn);

  return h_ibd_sub;
}
