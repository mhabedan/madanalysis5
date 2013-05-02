////////////////////////////////////////////////////////////////////////////////
//  
//  Copyright (C) 2012 Eric Conte, Benjamin Fuks, Guillaume Serret
//  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
//  
//  This file is part of MadAnalysis 5.
//  Official website: <http://madanalysis.irmp.ucl.ac.be>
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


#ifndef ProgressBar_h
#define ProgressBar_h

// STL headers
#include <iostream>
#include <string>
#include <iomanip>
#include <vector>
#include <sstream>

// ROOT headers
#include <Rtypes.h> 

// SampleAnalyzer headers
#include "SampleAnalyzer/Service/LogService.h"


namespace MA5
{


  class ProgressBar
  {

  // -------------------------------------------------------------
  //                        class SpySreamBuffer
  // -------------------------------------------------------------
  protected:

    class SpyStreamBuffer : public std::streambuf 
    {
    public:

      /// Constructor
      SpyStreamBuffer(std::streambuf* buf) : buf(buf)
      {
        last_chars.resize(7,traits_type::eof());
        // no buffering, overflow on every char
        setp(0, 0);
      }

      /// Getting last character
      const std::vector<char>& get_last_chars() const 
      { return last_chars; }

      /// Overflow method
      virtual int_type overflow(int_type c)
      {
        buf->sputc(c);
        for (unsigned int i=(last_chars.size()-1);i>0;i--) 
           last_chars[i]=last_chars[i-1];
        last_chars[0] = c;
        return c;
      }
    private:

      std::streambuf* buf;
      std::vector<char> last_chars;
    };

  // -------------------------------------------------------------
  //                        data members
  // -------------------------------------------------------------
  protected:

    /// Start point of the progress bar
    Long64_t MinValue_;

    /// End point of the progress bar
    Long64_t MaxValue_;

    /// Number of steps
    UInt_t Nstep_;

    /// Progress indicator
    UInt_t Indicator_;

    /// Mute if bad initialization
    Bool_t MuteInit_;

    /// Mute if the progress bar reachs the end bound
    Bool_t MuteEnd_;

    /// First time
    Bool_t FirstTime_;

    /// Thresholds
    std::vector<Long64_t> Thresholds_;

    /// Pointer to the new stream buffer
    SpyStreamBuffer* newstreambuf_;

    /// Pointer to the old stream buffer
    std::streambuf* oldstreambuf_;

    static const std::string header;

  // -------------------------------------------------------------
  //                       method members
  // -------------------------------------------------------------
 public:

    /// Constructor without argument
    ProgressBar()
    {
      newstreambuf_=0;
      oldstreambuf_=0;
      Reset(); 
    }

    /// Destructor 
    ~ProgressBar() 
    { if (newstreambuf_!=0) delete newstreambuf_; }

    /// Reset
    void Reset()
    {
      MinValue_=0; MaxValue_=0; Nstep_=0; Indicator_=0; 
      MuteInit_=false; MuteEnd_=false; FirstTime_=true;
      Thresholds_.clear();
    }

    /// Initializing the progress bar
    void Initialize(UInt_t Nstep, 
                    Long64_t MinValue, Long64_t MaxValue);

    /// Updating the display of the progress bar
    void Update(Long64_t value);

    /// Finalizing the progress bar
    void Finalize();

    /// Displaying the progress bar
    void Display(UInt_t ind);
  };
}

#endif
