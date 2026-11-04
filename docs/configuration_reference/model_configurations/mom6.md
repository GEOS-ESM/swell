# MOM6 Settings for GEOS/SOCA Setup (GEOSgcm v11.6.0)


## History Outputs (`diag_table`)

>In SWELL, history outputs are utilized to obtain the aggregated variables in desired output frequencies. See more details about [history outputs](history_outputs.md).

`diag_table` for SOCA is defined as below, which are the prognostic and diagnostic ocean fields required for SOCA applications to work. This particular setup spits out 3-hourly history outputs but users can experiment with different values.

```fortran
ocean_da
1970 1 1 0 0 0

##############################################
 "his%4yr%2mo%2dy%2hr",      3,  "hours", 1, "hours", "time", 3, "hours", "1901 1 1 0 0 0"
##############################################

# "module_name","field_name","output_name","file_name","time_sampling","reduction_method","regional_section",  packing
#===============================================
 "ocean_model", "geolon",      "geolon",      "his%4yr%2mo%2dy%2hr", "all", "none", "none", 2
 "ocean_model", "geolat",      "geolat",      "his%4yr%2mo%2dy%2hr", "all", "none", "none", 2
#===============================================
 "ocean_model", "SSH",       "ave_ssh",      "his%4yr%2mo%2dy%2hr","all", "none","none",2
 "ocean_model", "MLD_0125",  "MLD",      "his%4yr%2mo%2dy%2hr","all",none,"none",2
#===============================================
 "ocean_model","u","u"            ,"his%4yr%2mo%2dy%2hr","all",.false.,"none",2
 "ocean_model","v","v"            ,"his%4yr%2mo%2dy%2hr","all",.false.,"none",2
 "ocean_model","salt","Salt"      ,"his%4yr%2mo%2dy%2hr","all",.false.,"none",2
 "ocean_model","temp","Temp"      ,"his%4yr%2mo%2dy%2hr","all",.false.,"none",2
 "ocean_model","h","h"            ,"his%4yr%2mo%2dy%2hr","all",.false.,"none",2
#===============================================
```

## Incremental Analysis Update (IAU) with `MOM_oda_incupd`

`MOM_oda_incupd` is a module that stands for Ocean Data Assimilation (DA) incremental update. This is similar to other
modules that are located in `MOM_input` and currently handled as an extra file in the experiment directory. It divides increment files into smaller, linear segments. For example, if the model step is 900 seconds and `ODA_INCUPD_NHOURS` is set to 3 hours, the increments will be divided by 12 and applied to the state over 12 time steps.

In GEOS and SWELL context it needs to be included in the GEOS experiment folder. For it to be active,  `ODA_INCUPD` should ne set as `True`. `ODA_INCUPD_FILE` name shouldn't be changed as that is also used in SWELL. `ODA_INCUPD_UV` is set to false for
now until horizontal surface current fields are assimilated. In terms of `ODA_INCUPD_NHOURS`, there is no set rule but we aim
for half DA window length. Nonetheless, this can be changed using the `experiment.yaml` config key with the same name.

```fortran
! === module MOM_oda_incupd ===
ODA_INCUPD = True               ! [Boolean] default = False
                                ! If true, oda incremental updates will be applied
                                ! everywhere in the domain.
ODA_INCUPD_FILE = "mom6_increment.nc"   ! The name of the file with the T,S,h increments.

ODA_TEMPINC_VAR = "Temp"        ! default = "ptemp_inc"
                                ! The name of the potential temperature inc. variable in
				      	        ! ODA_INCUPD_FILE.
ODA_SALTINC_VAR = "Salt"        ! default = "sal_inc"
                                ! The name of the salinity inc. variable in
                                ! ODA_INCUPD_FILE.
ODA_THK_VAR = "h"               ! default = "h"
                                ! The name of the int. depth inc. variable in
                                ! ODA_INCUPD_FILE.
ODA_INCUPD_UV = false           !
ODA_UINC_VAR = "u"              ! default = "u_inc"
                                ! The name of the zonal vel. inc. variable in
                                ! ODA_INCUPD_UV_FILE.
ODA_VINC_VAR = "v"              ! default = "v_inc"
                                ! The name of the meridional vel. inc. variable in
                                ! ODA_INCUPD_UV_FILE.
ODA_INCUPD_NHOURS = 3.0         ! default=3.0
```