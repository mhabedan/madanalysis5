################################################################################
#  
#  Copyright (C) 2012-2019 Eric Conte, Benjamin Fuks
#  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
#  
#  This file is part of MadAnalysis 5.
#  Official website: <https://launchpad.net/madanalysis5>
#  
#  MadAnalysis 5 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  MadAnalysis 5 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with MadAnalysis 5. If not, see <http://www.gnu.org/licenses/>
#  
################################################################################

import madanalysis.observable.observable_list as obs_list

class JobSmearerMain:

    ## Initialization
    def __init__(self, fastsim):
        self.fastsim = fastsim


    ## Writing NewTagger.h
    def WriteNewSmearerSource(self, file):
        # header
        file.write('#include "SampleAnalyzer/User/Analyzer/newsmearer.h"\n')
        file.write('#include "SampleAnalyzer/User/Analyzer/sigmas.h"\n')
        file.write('#include "SampleAnalyzer/Commons/Service/RandomService.h"\n')
        file.write('using namespace MA5;\n')
        file.write('\n')
        file.write('void NewSmearer::Execute(SampleFormat& sample, ' +\
            'EventFormat& event)\n{\n')
        # MET, Meff, TET & THT
        file.write('  // New Lorentz Vector for recalculating the missing energy after smearing\n')
        file.write('  MALorentzVector pTmiss;\n')
        file.write('  // shortcut for Meff, TET & THT\n')
        file.write('  MAfloat64 & TET  = event.rec()->TET();\n')
        file.write('  MAfloat64 & THT  = event.rec()->THT();\n')
        file.write('  MAfloat64 & Meff = event.rec()->Meff();\n')
        file.write('  TET = 0.; THT = 0.; Meff = 0.;\n\n')
        # Jet Smearing
        file.write('  // Jet smearing\n')
        file.write('  for (MAuint32 i=0; i<event.rec()->jets().size(); i++)\n')
        file.write('  {\n')
        self.PrintSmearer(['21', 'j'], ['PT','ETA','PHI','E','PX','PY','PZ'],file,'(&event.rec()->jets()[i])')
        file.write('    pTmiss -= event.rec()->jets()[i].momentum();\n')
        file.write('    THT    += event.rec()->jets()[i].pt();\n')
        file.write('    TET    += event.rec()->jets()[i].pt();\n')
        file.write('    Meff   += event.rec()->jets()[i].pt();\n')
        file.write('  }\n\n')
        file.write('  (&event.rec()->MHT().momentum())->SetPxPyPzE(pTmiss.Px(), pTmiss.Py(), 0., pTmiss.E());\n')
        # Electron smearing
        file.write('  // Electron smearing \n')
        file.write('  for (MAuint32 i=0; i<event.rec()->electrons().size(); i++)\n')
        file.write('  {\n')
        self.PrintSmearer(['11', 'e'], ['PT','ETA','PHI','E','PX','PY','PZ'],file,'(&event.rec()->electrons()[i])')
        file.write('    pTmiss -= event.rec()->electrons()[i].momentum();\n')
        file.write('    TET    += event.rec()->electrons()[i].pt();\n')
        file.write('  }\n\n')
        # Muon smearing
        file.write('  // Muon smearing \n')
        file.write('  for (MAuint32 i=0; i<event.rec()->muons().size(); i++)\n')
        file.write('  {\n')
        self.PrintSmearer(['13', 'mu'], ['PT','ETA','PHI','E','PX','PY','PZ'],file,'(&event.rec()->muons()[i])')
        file.write('    pTmiss -= event.rec()->muons()[i].momentum();\n')
        file.write('    TET    += event.rec()->muons()[i].pt();\n')
        file.write('  }\n\n')
        # Tau smearing
        file.write('  // Tau smearing\n')
        file.write('  for (MAuint32 i=0; i<event.rec()->taus().size(); i++)\n')
        file.write('  {\n')
        self.PrintSmearer(['15', 'ta'], ['PT','ETA','PHI','E','PX','PY','PZ'],file,'(&event.rec()->taus()[i])')
        file.write('    pTmiss -= event.rec()->taus()[i].momentum();\n')
        file.write('    TET    += event.rec()->taus()[i].pt();\n')
        file.write('  }\n\n')
        # Photon smearing
        file.write('  // Photon smearing\n')
        file.write('  for (MAuint32 i=0; i<event.rec()->photons().size(); i++)\n')
        file.write('  {\n')
        self.PrintSmearer(['22', 'a'], ['PT','ETA', 'PHI', 'E','PX','PY','PZ'],file,'(&event.rec()->photons()[i])')
        file.write('    pTmiss -= event.rec()->photons()[i].momentum();\n')
        file.write('    TET    += event.rec()->photons()[i].pt();\n')
        file.write('  }\n')
        # Set missing transverse energy
        file.write('  // New MET\n')
        file.write('  (&event.rec()->MET().momentum())->SetPxPyPzE(pTmiss.Px(), pTmiss.Py(), 0., pTmiss.E());\n')
        file.write('  Meff += event.rec()->MET().pt();\n')
        file.write('}\n\n')

        # Gaussian
        file.write('MAdouble64 NewSmearer::Gaussian(MAdouble64 sigma, MAdouble64 object)\n{\n')
        file.write('  MAdouble64 PI = 3.141592653589793;\n')
        file.write('  MAdouble64 N  = 1.0 / (sigma * sqrt(2.0 * PI));\n')
        file.write('  if (N > 1e20)\n') ## N can become infinity
        file.write('  {\n')
        file.write('    WARNING << "Infinite normalization found in a smearing function" << endmsg;\n')
        file.write('    WARNING << "Smearing ignored." << endmsg;\n')
        file.write('    return object;\n')
        file.write('  }\n')
        file.write('  MAdouble64 gaussian = N * exp( -pow( object / sigma, 2.0) * 0.5 );\n')
        file.write('  MAdouble64 r        = RANDOM->flat();\n')
        file.write('  MAdouble64 sign     = (r >= 0.5) * 1.0 + (r < 0.5) * (-1.0);\n')
        file.write('  return object + sign * RANDOM->flat() * gaussian/2.;\n')
        file.write('}\n\n')


    def PrintSmearer(self, true_list, list_obs, file, obj):
        import madanalysis.observable.observable_list as observable_list
        check_initializer = 0
        for key, val in self.fastsim.smearer.rules.items():
            if val['id_true'] in true_list and val['obs'] in list_obs:
                eff_str = []
                initializer = 'MAdouble64 '
                if check_initializer > 0:
                    initializer = ''
                for eff_key, eff_val in val['efficiencies'].items():
                    my_eff_str = eff_val['bounds'].tocpp_call(obj,\
                      'bnd_'+str(val['id_true'])+'_'+str(val['obs'])+'_'+str(eff_key))
                    my_eff_str +=' * '
                    my_eff_str += eff_val['function'].tocpp_call(obj,\
                      'eff_'+str(val['id_true'])+'_'+str(val['obs'])+'_'+str(eff_key))
                    eff_str.append(my_eff_str)
                if check_initializer > 0:
                    file.write('    sigma = 0.;\n')
                file.write('        '+initializer+'sigma = ' + ' + '.join(eff_str) +';\n')
                file.write('        if ( sigma != 0. )\n        {\n')
                file.write('        MAdouble64 smeared_object = Gaussian(sigma,'+obj+'->'+\
                               observable_list.__dict__[val['obs']].code_reco+');\n')
                # we dont want momentum and energy to be negative
                if val['obs'] == 'PT':
                    file.write('        if (smeared_object < 0.) smeared_object = 0.;\n')
                    file.write('        '+obj+'->momentum().SetPtEtaPhiM(smeared_object, '+\
                               obj+'->eta(), '+obj+'->phi(), '+\
                               obj+'->m());\n')
                elif val['obs'] == 'ETA':
                    file.write('        '+obj+\
                               '->momentum().SetPtEtaPhiM('+obj+'->pt(), '+\
                               'smeared_object, '+obj+'->phi(), '+ obj+'->m());\n')
                elif val['obs'] == 'PHI':
                    file.write('        '+obj+\
                               '->momentum().SetPtEtaPhiM('+obj+'->pt(), '+\
                               +obj+'->eta(), smeared_object, '+ obj+'->m());\n')
                elif val['obs'] == 'PX':
                    file.write('        if (smeared_object < 0.) smeared_object = 0.;\n')
                    file.write('        '+obj+\
                               '->momentum().SetPxPyPzE(smeared_object,'+\
                               obj+'->py(), '+obj+'->pz(), '+obj+'->e());\n')
                elif val['obs'] == 'PY':
                    file.write('        if (smeared_object < 0.) smeared_object = 0.;\n')
                    file.write('        '+obj+\
                               '->momentum().SetPxPyPzE('+obj+'->px(),'+\
                               'smeared_object, '+obj+'->pz(), '+obj+'->e());\n')
                elif val['obs'] == 'PZ':
                    file.write('        if (smeared_object < 0.) smeared_object = 0.;\n')
                    file.write('        '+obj+\
                               '->momentum().SetPxPyPzE('+obj+'->px(),'+\
                               obj+'->py(), smeared_object, '+obj+'->e());\n')
                elif val['obs'] == 'E':
                    file.write('        if (smeared_object < 0.) smeared_object = 0.;\n')
                    file.write('        '+obj+\
                               '->momentum().SetPtEtaPhiE('+obj+'->pt(), '+\
                               obj+'->eta(), '+obj+'->phi(), '+\
                               'smeared_object);\n')
                file.write('        }\n')
                check_initializer+=1
