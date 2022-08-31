# (C) Copyright 2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod


# --------------------------------------------------------------------------------------------------


class PrepUsingBase(ABC):

    # ----------------------------------------------------------------------------------------------

    def __init__(self, logger):

        self.logger = logger

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def execute(self, input_dictionary, experiment_dictionary):
        pass


# --------------------------------------------------------------------------------------------------
