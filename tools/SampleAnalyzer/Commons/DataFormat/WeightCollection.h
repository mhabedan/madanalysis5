////////////////////////////////////////////////////////////////////////////////
//
//  Copyright (C) 2012-2023 Jack Araz, Eric Conte & Benjamin Fuks
//  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
//
//  This file is part of MadAnalysis 5.
//  Official website: <https://github.com/MadAnalysis/madanalysis5>
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

#ifndef WEIGHT_COLLECTION_H
#define WEIGHT_COLLECTION_H

// STL headers
#include <map>
#include <iostream>
#include <vector>
#include <cmath>
#include <sstream>
#include <algorithm>

// SampleAnalyzer headers
#include "SampleAnalyzer/Commons/Service/LogService.h"
#include "SampleAnalyzer/Commons/Service/ExceptionService.h"

namespace MA5
{

    class WeightCollection
    {

        // -------------------------------------------------------------
        //                        data members
        // -------------------------------------------------------------
    private:
        std::map<MAuint32, MAfloat64> weights_;
        static const MAfloat64 emptyvalue_;

        // -------------------------------------------------------------
        //                      method members
        // -------------------------------------------------------------
    public:
        /// Constructor withtout arguments
        WeightCollection() {}

        // copy constructor
        WeightCollection(const WeightCollection &rhs)
        {
            weights_.clear();
            for (auto &id_weights : rhs.weights_)
                Add(id_weights.first, id_weights.second);
        }

        /// @brief Initialise weights with a certain size and default value
        /// @param size number of weights
        /// @param default_value default value for each weight
        WeightCollection(const MAint32 &size, MAdouble64 default_value = 0.0)
        {
            for (MAuint32 i = 0; i < size; i++)
                weights_[i] = default_value;
        }

        /// Destructor
        ~WeightCollection() {}

        /// Clear all the content
        void Reset() { weights_.clear(); }
        void clear() { Reset(); }

        /// Size
        MAuint32 size() const { return weights_.size(); }

        /// Size
        MAuint32 size() { return weights_.size(); }

        /// Add a new weight group
        MAbool Add(MAuint32 id, MAfloat64 value)
        {
            // Try to add the item
            std::pair<std::map<MAuint32, MAfloat64>::iterator, bool> ret;
            ret = weights_.insert(std::pair<MAuint32, MAfloat64>(id, value));

            // Is it added?
            try
            {
                if (!ret.second)
                {
                    std::stringstream str;
                    str << id;
                    std::string idname;
                    str >> idname;
                    throw EXCEPTION_WARNING("The Weight '" + idname +
                                                "' is defined at twice. Redundant values are skipped.",
                                            "", 0);
                }
            }
            catch (const std::exception &e)
            {
                MANAGE_EXCEPTION(e);
                return false;
            }

            return true;
        }

        /// Get all the Weight Collection
        const std::map<MAuint32, MAfloat64> &GetWeights() const { return weights_; }

        /// Get a weight
        const MAfloat64 &Get(MAuint32 id) const
        {
            // Try to get the item
            std::map<MAuint32, MAfloat64>::const_iterator it = weights_.find(id);
            try
            {
                if (it == weights_.end())
                {
                    std::stringstream str;
                    str << id;
                    std::string idname;
                    str >> idname;
                    throw EXCEPTION_ERROR("The Weight '" + idname +
                                              "' is not defined. Return null value.",
                                          "", 0);
                }
            }
            catch (const std::exception &e)
            {
                MANAGE_EXCEPTION(e);
                return emptyvalue_;
            }

            return it->second;
        }

        /// Get a weight
        const MAfloat64 &operator[](MAuint32 id) const { return Get(id); }

        /// Add a new weight group
        void Print() const
        {
            if (weights_.empty())
                return;

            // Loop over weights for getting max
            MAuint32 maxi = 0;
            for (std::map<MAuint32, MAfloat64>::const_iterator
                     it = weights_.begin();
                 it != weights_.end(); it++)
            {
                if (it->first > maxi)
                    maxi = it->first;
            }

            // Loop over weights
            for (auto &w : weights_)
                INFO << "ID=" << w.first << " : " << w.second << endmsg;
        }

        /// @brief add weight to specific location
        /// @param idx location
        /// @param weight weight value
        void add_weight_to(MAint32 idx, MAdouble64 weight) { weights_[idx] += weight; }

        /// @brief multiply operator
        /// @param multiple
        WeightCollection &operator*=(const MAfloat64 multiple)
        {
            for (auto &id_value : weights_)
                id_value.second *= multiple;
            return *this;
        }

        /// @brief add operator
        /// @param input
        WeightCollection &operator+=(const MAfloat64 input)
        {
            for (auto &id_value : weights_)
                id_value.second += input;
            return *this;
        }

        /// @brief add operator
        /// @param input
        WeightCollection &operator+=(const WeightCollection input)
        {
            for (auto &id_value : weights_)
                id_value.second += input.Get(id_value.first);
            return *this;
        }

        /// @brief subtract operator
        /// @param input
        WeightCollection &operator-=(const MAfloat64 input)
        {
            for (auto &id_value : weights_)
                id_value.second -= input;
            return *this;
        }

        /// @brief divide operator
        /// @param input
        WeightCollection &operator/=(const MAfloat64 input)
        {
            for (auto &id_value : weights_)
                id_value.second /= input;
            return *this;
        }

        /// @brief assignment operator
        /// @param input
        WeightCollection &operator=(const MAfloat64 input)
        {
            for (auto &id_value : weights_)
                id_value.second = input;
            return *this;
        }

        /// @brief assignment operator
        /// @param input
        WeightCollection &operator=(const WeightCollection input)
        {
            for (auto &id_value : weights_)
                id_value.second = input.Get(id_value.first);
            return *this;
        }
    };

}

#endif
