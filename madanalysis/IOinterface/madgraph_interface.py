################################################################################
#
#  Copyright (C) 2012-2016 Eric Conte, Benjamin Fuks
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

import itertools
import logging
import os

class MadGraphInterface():

    def __init__(self):
        self.logger = logging.getLogger('MA5')
        self.model = ''
        self.multiparticles={}
        self.card=[]
        self.invisible_particles = []

    class InvalidCard(Exception):
        pass
    class MultiParts(Exception):
        pass


    def generate_card(self, MG5history, ProcessesDefinitions, ProcessesLists, card_type='parton'):
        """ Main routine allowing for the creation of ma5 cards.
            ProcessesDefinitions is a list of blocks, one block for each generate or add process command;
            ProcessesLists is a more detailed list"""

        ## Initialization
        self.logger.info('Creating an MA5 card for the mode: ' + card_type)
        self.card=[]

        self.logger.info('Getting the UFO model:')
        self.model = ProcessesLists[0][0].get('model')
        self.logger.debug('  >> ' + self.model.get('name'))
        self.get_invisible()

        self.logger.info('Getting the multiparticle definitions')
        for line in MG5history:
            if 'define' in line:
                myline = line.split()
                self.logger.debug('pdgs = '+str(myline[3:]))
                mypdgs= [self.get_pdg_code(prt) for prt in myline[3:]]
                self.multiparticles[myline[1]]=sorted(sum([e if isinstance(e,list) else [e] for e in mypdgs],[]))
        self.logger.debug('  >> ' + str(self.multiparticles))
        self.logger.debug('  >> invisible: ' + str(self.invisible_particles))
        self.write_multiparticles(card=(card_type=='parton'))

        if card_type=='hadron':
            return self.generate_hadron_card(ProcessesDefinitions, ProcessesLists)
        elif card_type=='parton':
            return self.generate_parton_card(ProcessesDefinitions, ProcessesLists)
        else:
            self.logger.error('  ** Unknown card type')
            raise self.InvalidCard('Unknown card type')


    def generate_parton_card(self, ProcessesDefinitions, ProcessesLists):

        # event fiile
        self.card.append('@MG5aMC inputs = *.lhe')

        # global observables
        self.card.append('# Global event variables')
        self.card.append('plot THT   40 0 500 [logY]')
        self.card.append('plot MET   40 0 500 [logY]')
        self.card.append('plot SQRTS 40 0 500 [logY]')

        # processes is a list of ProcessDefinitions
        self.logger.info('Decoding the considered process')
        for myprocdef in ProcessesDefinitions:
            self.generate_parton_card_for_procdef(myprocdef, interstate=[], finalstate=[])

        # output
        return '\n'.join(self.card)


    def generate_hadron_card(self, ProcessesDefinitions, ProcessesLists):
        self.card.append('# Reconstruction using FastJet')
        self.card.append('@MG5aMC reconstruction_name = BasicReco')
        self.card.append('@MG5aMC inputs = *.hepmc, *.hep, *.stdhep')
        self.card.append('set main.fastsim.package = fastjet')
        self.card.append('set main.fastsim.algorithm = antikt')
        self.card.append('set main.fastsim.radius = 0.4')
        self.card.append('set main.fastsim.ptmin = 5.0')
        self.card.append('# b-tagging')
        self.card.append('set main.fastsim.bjet_id.matching_dr = 0.4')
        self.card.append('set main.fastsim.bjet_id.efficiency = 1.0')
        self.card.append('set main.fastsim.bjet_id.misid_cjet = 0.0')
        self.card.append('set main.fastsim.bjet_id.misid_ljet = 0.0')
        self.card.append('# tau-tagging')
        self.card.append('set main.fastsim.tau_id.efficiency = 1.0')
        self.card.append('set main.fastsim.tau_id.misid_ljet = 0.0')

        self.card.append('\n# Reconstruction using Delphes')
        self.card.append('@MG5aMC reconstruction_name = CMSReco')
        self.card.append('@MG5aMC inputs = *.hepmc, *.hep, *.stdhep')
        self.card.append('set main.fastsim.package  = delphes')
        self.card.append('set main.fastsim.detector = cms-ma5tune')

        self.card.append('\n# Analysis using both reco')
        self.card.append('@MG5aMC analysis_name = analysis1')
        self.card.append('@MG5aMC inputs = *.lhe, *.root')
        self.card.append('@MG5aMC set_reconstructions = [\'BasicReco\', \'CMSReco\']')
        self.card.append('# object definition')
        self.card.append('select (j)  PT > 20')
        self.card.append('select (b)  PT > 20')
        self.card.append('select (e)  PT > 10')
        self.card.append('select (mu) PT > 10')
        self.card.append('select (j)  ABSETA < 2.5')
        self.card.append('select (b)  ABSETA < 2.5')
        self.card.append('select (e)  ABSETA < 2.5')
        self.card.append('select (mu) ABSETA < 2.5')

        self.card.append('# Basic plots')
        self.card.append('plot MET 40 0 500')
        self.card.append('plot THT 40 0 500')

        ## Getting the number of expected jets, electrons, etc...
        nj, nb, ntau, nmu, ne, na = 0,0,0,0,0,0
        for myprocdef in ProcessesDefinitions:
            mynj, mynb, myntau, mynmu, myne, myna = 0,0,0,0,0,0
            myfinal = self.get_finalstate_particles(myprocdef)
            for x in myfinal:
                mynj  += self.get_Npart(x, [4,3,2,1,-1,-2,-3,-4,21])
                mynb  += self.get_Npart(x, [5,-5])
                myna  += self.get_Npart(x, [22])
                myne  += self.get_Npart(x, [11,-11])
                mynmu += self.get_Npart(x, [13,-13])
                myntau+= self.get_Npart(x, [15,-15])
            if nj < mynj:
                nj=mynj
            if nb < mynb:
                nb=mynb
            if ne < myne:
                ne=myne
            if nmu< mynmu:
                nmu=mynmu
            if ntau < myntau:
                ntau=myntau
            if na < myna:
                na=myna

        # plots
        all_particles=[]
        self.card.append('# basic properties of the non-b-tagged jets')
        for i in range(1,max(2,nj)+1):
            self.card.append('plot PT(j['+str(i)+']) 40 0 500 [logY]')
            self.card.append('plot ETA(j['+str(i)+']) 40 -10 10 [logY]')
            self.card.append('plot MT_MET(j[' + str(i)+ ']) 40 0 500 [logY]')
            all_particles.append('j['+str(i)+']')
        if nb!=0:
            self.card.append('# basic properties of the b-tagged jets')
            for i in range(1,nb+1):
                self.card.append('plot PT(b['+str(i)+']) 40 0 500 [logY]')
                self.card.append('plot ETA(b['+str(i)+']) 40 -10 10 [logY]')
                self.card.append('plot MT_MET(b[' + str(i)+ ']) 40 0 500 [logY]')
                all_particles.append('b['+str(i)+']')

        self.card.append('# basic properties of the leptons')
        for i in range(1,ne+1):
            self.card.append('plot PT(e['+str(i)+']) 40 0 500 [logY]')
            self.card.append('plot ETA(e['+str(i)+']) 40 -10 10 [logY]')
            self.card.append('plot MT_MET(e[' + str(i)+ ']) 40 0 500 [logY]')
            all_particles.append('e['+str(i)+']')
        for i in range(1,nmu+1):
            self.card.append('plot PT(mu['+str(i)+']) 40 0 500 [logY]')
            self.card.append('plot ETA(mu['+str(i)+']) 40 -10 10 [logY]')
            self.card.append('plot MT_MET(mu[' + str(i)+ ']) 40 0 500 [logY]')
            all_particles.append('mu['+str(i)+']')
        for i in range(1,ntau+1):
            self.card.append('plot PT(ta['+str(i)+']) 40 0 500 [logY]')
            self.card.append('plot ETA(ta['+str(i)+']) 40 -10 10 [logY]')
            self.card.append('plot MT_MET(ta[' + str(i)+ ']) 40 0 500 [logY]')
            all_particles.append('ta['+str(i)+']')

        self.card.append('# basic properties of the photons')
        for i in range(1,na+1):
            self.card.append('plot PT(a['+str(i)+']) 40 0 500 [logY]')
            self.card.append('plot ETA(a['+str(i)+']) 40 -10 10 [logY]')
            self.card.append('plot MT_MET(a[' + str(i)+ ']) 40 0 500 [logY]')
            all_particles.append('a['+str(i)+']')

        permlist = [c for i in range(1,len(all_particles)) for c in itertools.combinations(all_particles, i+1)]
        permlist.sort()
        permlist=list(permlist for permlist,_ in itertools.groupby(permlist))
        if len(permlist)>0:
            self.card.append('# Invariant-mass distributions')
            for perm in permlist:
                if len(perm)==2:
                    self.card.append('plot M('+' '.join(perm)+') 40 0  500 [logY]')
            self.card.append('# Angular distance distributions')
            for perm in permlist:
                if len(perm)==2:
                    self.card.append('plot DELTAR('+','.join(perm)+') 40 0 10 [logY]')

        # output
        return '\n'.join(self.card)

    def get_Npart(self, prt, pdglist):
        if isinstance(prt, list):
            for x in prt:
                if x in pdglist:
                    return 1
            return 0
        else:
            return int(prt in pdglist)


    def generate_parton_card_for_procdef(self, process, interstate=[], finalstate=[], invisstate=[]):
        """ Main routine for decoding the parton-level process"""

        # init
        if interstate==[] and finalstate==[]:
            self.logger.debug('  >> new process')

        # getting the list of particles and creating the plots
        if interstate==[] and finalstate==[]:
            dummy, interstate,finalstate,invisstate = self.particles_in_process(process)
        self.logger.debug('    >> visible inter state particles: ' + str(interstate))
        self.logger.debug('    >> visible final state particles: ' + str(finalstate))
        self.logger.debug('    >> invisible final state particles: ' + str(invisstate))
        # Hard process before decay
        self.generate_plots(interstate,finalstate,invisstate)
        # Hard process after decay
        if interstate !=[]:
            interstate, finalstate, invisstate = \
               self.decay(process.get('decay_chains'),interstate,finalstate,invisstate)
            self.logger.debug('    >> visible final state particles after decay: ' + str(finalstate))
            self.logger.debug('    >> invisible final state particles after decay: ' + str(invisstate))
            self.generate_plots(interstate,finalstate,invisstate)

    def decay(self,chains,old_int,old_fin,old_inv):
        new_int, new_fin, new_inv = old_int, old_fin, old_inv
        for mydecay in chains:
            dec_init,dec_inter,dec_final,dec_inv = self.particles_in_process(mydecay)
            for x in dec_init:
                if x in new_int:
                    new_int.remove(x)
                new_inv+=dec_inv
                new_fin+=dec_final
                new_int+=dec_inter
            if new_int!=[]:
                new_int, newfin, new_inv = self.decay(mydecay.get('decay_chains'),new_int,new_fin,new_inv)
        return new_int,new_fin,new_inv

    def particles_in_process(self,process):
         # init
        initstate = []
        intstate = []
        finstate = []
        decaying_particles=[]

        # decay properties
        for mydecay in process.get('decay_chains'):
            decaying_particles.append(mydecay.get('legs')[0].get('ids'))

        for myleg in process.get('legs'):
            prts = sorted(myleg.get('ids'))
            if not myleg.get('state'):
                initstate.append(self.get_name(prts))
            elif prts in decaying_particles:
                intstate.append(self.get_name(prts))
            else:
                finstate.append(self.get_name(prts))
        invstate   = [ x for x in finstate if x in self.invisible_particles ]
        finstate = [ x for x in finstate if not x in invstate ]
        return initstate,intstate,finstate,invstate



    def generate_plots(self,interstate,finalstate,invisible):
        # Formatting the inputs (tally)
        new_inter = []
        new_final = []
        for x,num in [[x,interstate.count(x)] for x in set(interstate)]:
            for i in range(num):
                new_inter.append(x+'['+str(i+1)+']')
        for x,num in [[x,finalstate.count(x)] for x in set(finalstate)]:
            for i in range(num):
                new_final.append(x+'['+str(i+1)+']')

        # properties of the final state particles
        self.card.append('# PT and ETA distributions of all particles')
        for part in new_inter:
            self.card.append('plot  PT(' + part + ') 40 0  500 [logY interstate]')
            self.card.append('plot ETA(' + part + ') 40 -10 10 [logY interstate]')
        for part in new_final:
            self.card.append('plot  PT(' + part + ') 40 0  500 [logY]')
            self.card.append('plot ETA(' + part + ') 40 -10 10 [logY]')

        # invariant mass ditributions
        tagstate = 'allstate'
        if len(interstate)==0:
            tagstate=''
        allstate = new_inter+new_final
        permlist = [c for i in range(1,len(allstate)) for c in itertools.combinations(allstate, i+1)]
        permlist.sort()
        permlist=list(permlist for permlist,_ in itertools.groupby(permlist))
        if len(permlist)>0:
            self.card.append('# Invariant-mass distributions')
        for perm in permlist:
            self.card.append('plot M('+' '.join(perm)+') 40 0  500 [logY '+tagstate+']')

        # delta R of between two particles
        if len(permlist)>0:
            self.card.append('# Angular distance distributions')
        for perm in permlist:
            if len(perm)==2:
                self.card.append('plot DELTAR('+','.join(perm)+') 40 0 10 [logY '+tagstate+']')

        # MET
        if len(invisible)>0:
            self.card.append('# Invisible')
            for part in new_inter:
                self.card.append('plot MT_MET(' + part + ') 40 0  500 [logY interstate]')
            for part in new_final:
                self.card.append('plot MT_MET(' + part + ') 40 0  500 [logY]')

    # from pdf list to name
    def get_name(self,pdg):
        if len(pdg)==1:
            myprt =self.model.get('particle_dict')[pdg[0]]
            if myprt['is_part']:
                return myprt['name']
            else:
                return myprt['antiname']
        else:
            for key, value in self.multiparticles.iteritems():
                self.logger.debug('new multiparticles ' + key + ' = ' + str(value))
                if value==pdg:
                    return key
        self.logger.error('  ** Cannot find the name associated with the pdg code list' + str(pdg))
        raise self.MultiParts("  ** Problem with the multiparticle definitions")


    # from pdg code to name
    def get_pdg_code(self,prt):
        for key, value in self.model.get('particle_dict').iteritems():
            if value['antiname']==prt and not value['is_part']:
                return key
            elif value['name']==prt and value['is_part']:
                return key
        if prt in self.multiparticles.keys():
            return self.multiparticles[prt]
        else:
            self.logger.error("  ** Problem with the multiparticle definitions")
            raise self.MultiParts("  ** Problem with the multiparticle definitions")

    # adding the particle definitions
    def get_invisible(self):
        # Do we have MET?
        for key, value in self.model.get('particle_dict').iteritems():
            if value['width'] == 'ZERO' and value['color']==1 and value['charge']==0 and not value['name']=='a':
                self.invisible_particles.append(value['name'])
                self.invisible_particles.append(value['antiname'])
        self.invisible_particles=list(set(self.invisible_particles))
        if len(self.invisible_particles)>0:
            self.card.append('# Multiparticle definition')
            self.card.append('define invisible = ' + ' '.join(self.invisible_particles))

    def write_multiparticles(self, card=True):
        for key, value in self.multiparticles.iteritems():
            if len([ x for x in value if x in [self.get_pdg_code(y) for y in self.invisible_particles] ])==len(value):
                self.invisible_particles.append(key)
            if card:
                self.card.append('define ' + key + ' = ' + ' '.join([str(x) for x in value]))

    def get_finalstate_particles(self, process):
        dummy, interstate,finalstate,invisstate = self.particles_in_process(process)
        if interstate !=[]:
            interstate, finalstate, invisstate = \
               self.decay(process.get('decay_chains'),interstate,finalstate,invisstate)
        return [self.get_pdg_code(x) for x in finalstate]
