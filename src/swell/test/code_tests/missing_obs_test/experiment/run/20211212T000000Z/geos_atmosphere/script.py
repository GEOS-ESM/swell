
import netCDF4 as nc

# Create a NetCDF file
filename = "satwind.20211211T210000Z.nc4"
with nc.Dataset(filename, "w", format="NETCDF4") as ds:
    # Define the dimension
    ds.createDimension("Location", 1)  # 1 element in the "Location" dimension

    # Create a variable with the same name as the dimension
    location_var = ds.createVariable("Location", "i4")  # 'i4' represents 4-byte integer

    # Set the value of the variable to zero
    location_var[0] = 0
