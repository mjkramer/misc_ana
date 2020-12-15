#include "MysterySel.hh"
#include "MultCut.hh"
#include "MuonAlg.hh"

#include "Framework/Assert.hh"
#include "Framework/ConfigTool.hh"

#include <TH2F.h>
#include <TH3F.h>

#include <cmath>
#include <iostream>             // XXX

MysterySel::MysterySel(Det det) :
  SelectorBase(det, MuonAlg::Purpose::ForSingles)
{
  auto hname = Form("h2_rz_AD%d", int(det));
  h2_rz = new TH2F(hname, hname, 400, -10, 10, 400, -10, 10);

  hname = Form("h2_r2z_AD%d", int(det));
  h2_r2z = new TH2F(hname, hname, 400, -100, 100, 400, -10, 10);

  hname = Form("h2_xy_AD%d", int(det));
  h2_xy = new TH2F(hname, hname, 400, -10, 10, 400, -10, 10);

  hname = Form("h3_xyz_AD%d", int(det));
  h3_xyz = new TH3F(hname, hname,
                    400, -10, 10,
                    400, -10, 10,
                    400, -10, 10);
}

void MysterySel::initCuts(const Config *config)
{
  EMIN = config->get<float>("mysteryEmin", 6);
  EMAX = config->get<float>("mysteryEmax", 7.75);
}

void MysterySel::finalize(Pipeline& _p)
{
  h2_rz->Write();
  h2_r2z->Write();
  h2_xy->Write();
  h3_xyz->Write();
}

void MysterySel::select(Iter it)
{
  if (EMIN < it->energy && it->energy < EMAX &&
      not muonAlg->isVetoed(it->time(), det) &&
      multCut->singleDmcOk(it, det)) {

    double x = it->x / 1000;
    double y = it->y / 1000;
    double z = it->z / 1000;

    double r2 = x*x + y*y;
    double r = sqrt(r2);

    std::cout << x << " " << y << " " << z << std::endl;

    h2_rz->Fill(r, z);
    h2_r2z->Fill(r2, z);
    h2_xy->Fill(x, y);
    h3_xyz->Fill(x, y, z);
  }
}
