/** 
 * Start
 *
 * Apr 28, 2010  Created by ...
 */

#ifndef _START_H_
#define _START_H_

#include "GaudiAlg/GaudiAlgorithm.h"

class Start : public GaudiAlgorithm 
{

 public:
  
  Start(const std::string& name, ISvcLocator* pSvcLocator);
  virtual ~Start();
  
  virtual StatusCode initialize();
  virtual StatusCode execute();
  virtual StatusCode finalize();
  
 private:
  
};

#endif  // _START_H_
