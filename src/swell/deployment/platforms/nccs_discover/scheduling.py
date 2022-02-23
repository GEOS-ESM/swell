# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


# Dictionary containing the tasks per node for each platform/constraint
ntasks_per_node_dict = {
  'nccs_discover': {'hasw': 28,
                    'sky': 40,
                    'cas': 48
                    }
}


# --------------------------------------------------------------------------------------------------


def get_tasks_per_node(platform, constraint):

    return ntasks_per_node_dict[platform][constraint]


# --------------------------------------------------------------------------------------------------
