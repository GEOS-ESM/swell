# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os

from abc import ABC, abstractmethod

from swell.tasks.base.task_base import taskBase

# --------------------------------------------------------------------------------------------------


class GeosTasksRunExecutableBase(taskBase):

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self):
        # This class does not execute, it provides helper function for the children
        # ------------------------------------------------------------------------
        pass

    # ----------------------------------------------------------------------------------------------

    def rc_to_bool(self, rcdict):

        # .rc files have switch values in .TRUE. or .FALSE. format.
        # This method converts it to python boolean and assumes only two types
        # of input. It can also accept faulty formats (i.e., .True. , .False) 
        # ----------------------------------------------------------------------

        for key, value in rcdict.items():
            if rcdict[key].strip('.').lower() == 'true':
                rcdict[key] = True
            elif rcdict[key].strip('.').lower() == 'false':
                rcdict[key] = False
            else:
                continue

        return rcdict
        # for key, value in rcdict.items():
        #     rcdict[key] = rcdict[key] == '.TRUE.'
        
        # exit()
        # return rcdict

    # ----------------------------------------------------------------------------------------------

    def geos_chem_rename(self, rcdict):

        # Some files are renamed according to bool. swithfes in GEOS_ChemGridComp.rc 
        # -------------------------------------------------------------------------

        # Convert rc bool.s to python 
        # ---------------------------
        rcdict = self.rc_to_bool(rcdict)

        self.cycle_dir = self.config_get('cycle_dir')

        # GEOS Chem filenames, shares same keys as rcdict
        # -----------------------------------------------
        chem_files = {
            'ENABLE_STRATCHEM' : 'StratChem_ExtData.rc',
            'ENABLE_GMICHEM' : 'GMI_ExtData.rc',
            'ENABLE_GEOSCHEM' : 'GEOSCHEMchem_ExtData.rc',
            'ENABLE_CARMA' : 'CARMAchem_GridComp_ExtData.rc',
            'ENABLE_DNA' : 'DNA_ExtData.rc',
            'ENABLE_ACHEM' : 'GEOSachem_ExtData.rc',
            'ENABLE_GOCART_DATA' : 'GOCARTdata_ExtData.rc',
        }

        for key, value in chem_files.items():
            fname = os.path.join(self.cycle_dir, value)
            
            if not rcdict[key] and os.path.isfile(fname):
                self.logger.info(' Renaming file: '+fname)
                os.system('rename .rc .rc.NOT_USED ' + fname)

    # ----------------------------------------------------------------------------------------------

    def parse_rc(self, rcfile, getkey=None, singlekey=None):

        # Parse AGCM.rc & CAP.rc line by line and create a dictionary or obtain 
        # single key-value pair. It ignores comments and commented out lines.
        # Some values involve multiple ":" characters which required some extra 
        # steps to handle them as dictionary values.

        # Also possible (notyet) to return a single key-value pair using getkey and 
        # singlekey options
        # ----------------------------------------------------------------------

        with open(rcfile, 'r') as file:
            lines = file.readlines()

        rcdict = {}

        for line in lines:
            # Strip any leading or trailing whitespace from the line
            # ------------------------------------------------------
            line = line.strip()

            # Skip if the line is a comment (i.e., starts with #)
            # ------------------------------------------------------
            if line.startswith("#"):
                continue

            # Split the line into key-value pair and ignore any comment after #
            # -------------------------------------------------------------------
            parts = line.split('#', 1)
            line = parts[0]

            # Split the line into key and value using the first occurrence of ":" as the delimiter
            # ------------------------------------------------------------------------------------
            split_line = line.split(":", 1)
            if len(split_line) == 2:
                key, value = split_line
                # Re-join any remaining parts of the value with ":" again
                # -------------------------------------------------------
                value = value.split(":")
                value = ":".join(value)

                # Strip any whitespace from the key and value
                # --------------------------------------------
                key = key.strip()
                value = value.strip()
                rcdict[key] = value

        return rcdict
#                 # Check if the key matches the string we're looking for
#                 # -----------------------------------------------------
#                 print(key)
#                 print(singlekey)
#                 if getkey and key == singlekey:
#                     # Store the value and return
#                     # --------------------------
# ]                    print(value)
#                     rcdict[singlekey] = value

# --------------------------------------------------------------------------------------------------
