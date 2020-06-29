/**
 * Start
 *
 * Apr. 28, 2010  Created by ...
 */
#include "Start.h"

Start::Start(const std::string& name, ISvcLocator* pSvcLocator):
  GaudiAlgorithm(name, pSvcLocator)
{
}

Start::~Start()
{
}

StatusCode Start::initialize()
{
  StatusCode sc;
  sc = this->GaudiAlgorithm::initialize();

  return sc;
}

StatusCode Start::execute()
{
  info()<<"Start executing ... "<<endreq;

  return StatusCode::SUCCESS;
}

StatusCode Start::finalize()
{
  StatusCode sc;
  sc = this->GaudiAlgorithm::finalize();

  return sc;
}
