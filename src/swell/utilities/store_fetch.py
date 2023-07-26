# (C) Copyright 2023 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

from r2d2 import R2D2Data
import r2d2.error as err

# --------------------------------------------------------------------------------------------------
def Fetch(data_stores, **fetch_kwargs):

    # Track whether a fetch was successful
    fetch_success = False

    # Gather error messages for each fetch attempt
    failure_messages = dict.fromkeys(data_stores)

    for data_store in data_stores:

        print("******", data_store, "*******")

        try:
            R2D2Data.fetch(data_store = data_store, **fetch_kwargs)

        except (err.RegistrationNotFound, err.RecordNotFound) as r2d2error:
            failure_messages[data_store] = str(r2d2error)
            pass
 
        else:
            fetch_success = True
            break
 
    if fetch_success is False:

        error_message = "Failed to fetch R2D2 data.\n"
        for k,v in failure_messages.items():
            error_message += k + ": " + v

        # Is there a more appropriate error than ValueError?
        raise ValueError(error_message)


# --------------------------------------------------------------------------------------------------
def Store(data_stores, limit_one = True, **store_kwargs):

    """Very similar to Fetch with an option to store into every data_store.
       This method also ignores r2d2.error.RecordNotFound as it is irrelevant to storing. 
    """

    # Track whether store is successful
    store_success = False

    # Gather error messages for each store attempt
    failure_messages = dict.fromkeys(data_stores)

    for data_store in data_stores:

        print("******", data_store, "*******")

        try:
            R2D2Data.store(data_store = data_store, **store_kwargs)

        except err.RegistrationNotFound as r2d2error:
            failure_messages[data_store] = str(r2d2error)
            pass

        else:
            store_success = True
            if limit_one is True:
                break

    if store_success is False:

        error_message = "Could not store data into any R2D2 data_store.\n"
        for k,v in failure_messages.items():
            error_message += k + ": " + v

        raise ValueError(error_message)



