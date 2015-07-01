////////////////////////////////////////////////////////////////////////////////
//
//  Copyright (C) 2012-2013 Eric Conte, Benjamin Fuks
//  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
//
//  This file is part of MadAnalysis 5.
//  Official website: <https://launchpad.net/madanalysis5>
//
//  MadAnalysis 5 is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  MadAnalysis 5 is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with MadAnalysis 5. If not, see <http://www.gnu.org/licenses/>
//
////////////////////////////////////////////////////////////////////////////////

#ifndef ISOLATIONCALORIMETER_SERVICE_h
#define ISOLATIONCALORIMETER_SERVICE_h

// STL headers

// SampleAnalyzer headers
#include "SampleAnalyzer/Commons/Service/IsolationBase.h"


namespace MA5
{

class IsolationCalorimeter : IsolationBase
{
  // -------------------------------------------------------------
  //                       data members
  // -------------------------------------------------------------
  private:


  public:

    /// Constructor
    IsolationCalorimeter() {}

    /// Destructor
    virtual ~IsolationCalorimeter() {}

    // -------------------------------------------------------------
    //                Isolation of one particle
    // -------------------------------------------------------------

    virtual Double_t relIsolation(const RecLeptonFormat& part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    { return relIsolation(&part, event, DR, PTmin); }

    virtual Double_t relIsolation(const RecLeptonFormat* part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    {
      if (part==0) return 0;
      if (event==0) return 0;
      if (part->pt()<1e-9) return 999.;
      return sumIsolation(part,event,DR,PTmin)/part->pt();
    }

    virtual Double_t sumIsolation(const RecLeptonFormat& part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    { return sumIsolation(&part, event, DR, PTmin); }

    virtual Double_t sumIsolation(const RecLeptonFormat* part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    {
      if (part==0) return 0;
      if (event==0) return 0;
      Double_t sum=0.;
      sum += sumPT(part,event->towers(),DR,PTmin);
      return sum;
    }

    virtual Double_t relIsolation(const RecPhotonFormat& part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    { return relIsolation(&part, event, DR, PTmin); }

    virtual Double_t relIsolation(const RecPhotonFormat* part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    {
      if (part==0) return 0;
      if (event==0) return 0;
      if (part->pt()<1e-9) return 999.;
      return sumIsolation(part,event,DR,PTmin)/part->pt();
    }

    virtual Double_t sumIsolation(const RecPhotonFormat& part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    { return sumIsolation(&part, event, DR, PTmin); }

    virtual Double_t sumIsolation(const RecPhotonFormat* part, const RecEventFormat* event, const double& DR, double PTmin=0.5) const
    {
      if (part==0) return 0;
      if (event==0) return 0;
      Double_t sum=0.;
      sum += sumPT(part,event->towers(),DR,PTmin);
      return sum;
    }

    // -------------------------------------------------------------
    //                Isolation of one collection
    // -------------------------------------------------------------

    virtual std::vector<const RecLeptonFormat*> getRelIsolated(const std::vector<RecLeptonFormat>& leptons, 
                                                               const RecEventFormat* event, 
                                                               const double& threshold, const double& DR, double PTmin=0.5) const
    {
      std::vector<const RecLeptonFormat*> isolated(leptons.size());
      for (unsigned int i=0;i<leptons.size();i++) isolated[i]=&(leptons[i]);
      return getRelIsolated(isolated, event, threshold, DR, PTmin);
    }

    virtual std::vector<const RecLeptonFormat*> getRelIsolated(const std::vector<const RecLeptonFormat*>& leptons, 
                                                               const RecEventFormat* event, 
                                                               const double& threshold, const double& DR, double PTmin=0.5) const
    {
      std::vector<const RecLeptonFormat*> isolated;
      for (unsigned int i=0;i<leptons.size();i++)
      {
        if (relIsolation(leptons[i],event,DR,PTmin)>threshold) continue;
        isolated.push_back(leptons[i]);
      }
      return isolated;
    }


    virtual std::vector<const RecPhotonFormat*> getRelIsolated(const std::vector<RecPhotonFormat>& photons, 
                                                               const RecEventFormat* event, 
                                                               const double& threshold, const double& DR, double PTmin=0.5) const
    {
      std::vector<const RecPhotonFormat*> isolated(photons.size());
      for (unsigned int i=0;i<photons.size();i++) isolated[i]=&(photons[i]);
      return getRelIsolated(isolated, event, threshold, DR, PTmin);
    }

    virtual std::vector<const RecPhotonFormat*> getRelIsolated(const std::vector<const RecPhotonFormat*>& photons, 
                                                               const RecEventFormat* event, 
                                                               const double& threshold, const double& DR, double PTmin=0.5) const
    {
      std::vector<const RecPhotonFormat*> isolated;
      for (unsigned int i=0;i<photons.size();i++)
      {
        if (relIsolation(photons[i],event,DR,PTmin)>threshold) continue;
        isolated.push_back(photons[i]);
      }
      return isolated;
    }




};

}

#endif
