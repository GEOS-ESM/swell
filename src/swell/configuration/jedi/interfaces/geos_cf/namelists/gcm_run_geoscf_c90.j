#!/bin/csh -f

#######################################################################
#                     Batch Parameters for Run Job
#######################################################################
#SBATCH --time=00:40:00
#SBATCH --nodes=8 --ntasks-per-node=108
#SBATCH --job-name=CFv2rc1t13
#SBATCH --output=CFv2_gcm_%j
#SBATCH --constraint=mil
#SBATCH --account=s2127


#######################################################################
#                         System Settings
#######################################################################

umask 022

limit stacksize unlimited

#######################################################################
#           Architecture Specific Environment Variables
#######################################################################

setenv ARCH `uname`

setenv SITE             NCCS
#setenv GEOSDIR          /discover/nobackup/projects/gmao/geos-cf-v2/CFv2_code/GEOSgcm_rc1_t15/install_mil
#setenv GEOSBIN          /discover/nobackup/projects/gmao/geos-cf-v2/CFv2_code/GEOSgcm_rc1_t15/install_mil/bin
#setenv GEOSETC          /discover/nobackup/projects/gmao/geos-cf-v2/CFv2_code/GEOSgcm_rc1_t15/install_mil/etc
#setenv GEOSUTIL         /discover/nobackup/projects/gmao/geos-cf-v2/CFv2_code/GEOSgcm_rc1_t15/install_mil

#setenv GEOSDIR          /discover/nobackup/mabdiosk/GEOS-mil/GEOSgcm/install
setenv GEOSDIR          /discover/nobackup/mabdiosk/GEOS-mil/GEOSgcm/install
#setenv GEOSDIR          /discover/nobackup/vshah5/cf2/CFv2_code/GEOSgcm_rc1_t15/build_mil
setenv GEOSBIN          $GEOSDIR/bin
setenv GEOSETC          $GEOSDIR/etc
setenv GEOSUTIL         $GEOSDIR

source $GEOSBIN/g5_modules # super important, all the libs to run geos.exe, will do module purge 
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:${BASEDIR}/${ARCH}/lib:${GEOSDIR}/lib

setenv RUN_CMD "$GEOSBIN/esma_mpirun -np "

setenv GCMVER `cat $GEOSETC/.AGCM_VERSION`
echo   VERSION: $GCMVER

#######################################################################
#             Experiment Specific Environment Variables
#######################################################################


setenv  EXPID   GCv14.0_GCMv1.17_c90
setenv  EXPDIR  /discover/nobackup/mabdiosk/rundir/GCv14.0_GCMv1.17_c90_Skylab 
# EXPDIR and EXPID have to be the same 
setenv  HOMDIR  $EXPDIR

# Run GSI?
set RUN_GSI = 0

#######################################################################
#                 Create Experiment Sub-Directories
#######################################################################
echo "  Create Experiment Sub-Directories "
setenv CYCLEDIR /discover/nobackup/mabdiosk/SwellExperiments/swell-3dvar_cf_cycle/run/20230810T000000Z/geos_cf/scratch # current_cycle


#if (! -e $CYCLEDIR/restarts   ) mkdir -p $CYCLEDIR/restarts
#if (! -e $CYCLEDIR/holding    ) mkdir -p $CYCLEDIR/holding

setenv  SCRDIR  $CYCLEDIR
# Remove the directory if it exists
#if ( -d $SCRDIR ) then
#    rm -rf $SCRDIR
#endif

# Create the directory
#mkdir -p $SCRDIR

#######################################################################
#                   Set Experiment Run Parameters
#######################################################################
# read things from AGCM.rc, change only changing the res/config
# nx ny has to be the same as number of requested cpus.
# prepfc copies AGCM.rc from skylab/models/geos_cf/namelists to CYCLEDIR

echo "Set Experiment Run Parameters"
set       NX  = `grep '^\s*NX:'             $CYCLEDIR/AGCM.rc | cut -d: -f2`
set       NY  = `grep '^\s*NY:'             $CYCLEDIR/AGCM.rc | cut -d: -f2`
set  AGCM_IM  = `grep '^\s*AGCM_IM:'        $CYCLEDIR/AGCM.rc | cut -d: -f2`
set  AGCM_JM  = `grep '^\s*AGCM_JM:'        $CYCLEDIR/AGCM.rc | cut -d: -f2`
set  AGCM_LM  = `grep '^\s*AGCM_LM:'        $CYCLEDIR/AGCM.rc | cut -d: -f2`
set  OGCM_IM  = `grep '^\s*OGCM\.IM_WORLD:' $CYCLEDIR/AGCM.rc | cut -d: -f2`
set  OGCM_JM  = `grep '^\s*OGCM\.JM_WORLD:' $CYCLEDIR/AGCM.rc | cut -d: -f2`


# Calculate number of cores/nodes for IOSERVER
# --------------------------------------------

set USE_IOSERVER   = 0
set AGCM_IOS_NODES = `grep '^\s*IOSERVER_NODES:' $CYCLEDIR/AGCM.rc | cut -d: -f2`

if ($USE_IOSERVER == 0) then
   set IOS_NODES = 0
else
   set IOS_NODES = $AGCM_IOS_NODES
endif

# Check for Over-Specification of CPU Resources
# ---------------------------------------------
if ($?SLURM_NTASKS) then
   set  NCPUS = $SLURM_NTASKS
else if ($?PBS_NODEFILE) then
   set  NCPUS = `cat $PBS_NODEFILE | wc -l`
else
   set  NCPUS = NULL
endif

@ MODEL_NPES = $NX * $NY

if ( $NCPUS != NULL ) then

   if ( $USE_IOSERVER == 1 ) then

      set NCPUS_PER_NODE = 40

      @ NODES  = `echo "( ($MODEL_NPES + $NCPUS_PER_NODE) + ($AGCM_IOS_NODES * $NCPUS_PER_NODE) - 1)/$NCPUS_PER_NODE" | bc`
      @ NPES   = $NODES * $NCPUS_PER_NODE

      if( $NPES > $NCPUS ) then
         echo "CPU Resources are Over-Specified"
         echo "--------------------------------"
         echo "Allotted  NCPUs: $NCPUS"
         echo "Requested NCPUs: $NPES"
         echo ""
         echo "Specified NX: $NX"
         echo "Specified NY: $NY"
         echo ""
         echo "Specified IOSERVER_NODES: $AGCM_IOS_NODES"
         echo "Specified cores per node: $NCPUS_PER_NODE"
         echo "Exit with  NPES > NCPUS 1"
         exit
      endif

   else

      @ NPES = $MODEL_NPES

      if( $NPES > $NCPUS ) then
         echo "CPU Resources are Over-Specified"
         echo "--------------------------------"
         echo "Allotted  NCPUs: $NCPUS"
         echo "Requested NCPUs: $NPES"
         echo ""
         echo "Specified NX: $NX"
         echo "Specified NY: $NY"
         echo "Exit with  NPES > NCPUS 2"
         exit
      endif

   endif

else
   # This is for the desktop path

   @ NPES = $MODEL_NPES

endif

# submit GSI standalone run, will run in parallel 
if ( $RUN_GSI == 1 ) then
   # make sure EXPID is correct
   /bin/mv gsi_sa.j gsi_sa.tmp
   cat gsi_sa.tmp | sed -e "s?setenv EXPID.*?setenv EXPID $EXPID?g" > gsi_sa.j
   /bin/rm gsi_sa.tmp
   echo "submitting gsi job to run in parallel..."
   sbatch gsi_sa.j
endif

echo "finish Set Experiment Run Parameters"
#######################################################################
#   Move to Scratch Directory and Copy RC Files from Home Directory
#######################################################################
echo " Move to Scratch Directory and Copy RC Files from Home Directory "
cd $SCRDIR  # SCRDIR=$CYCLEDIR/scratch

# done in prep_forecast
#cp -rf  $CYCLEDIR/RC/* . #moved/edited in prepForecast
#cp      $CYCLEDIR/cap_restart . 
#cp -rf  $CYCLEDIR/*.rc .
##cp -rf  $HOMDIR/*.nml .
#cp -rf  $CYCLEDIR/*.yaml .
cp     $GEOSBIN/bundleParser.py .

cat fvcore_layout.rc >> input.nml

set END_DATE  = `grep '^\s*END_DATE:'     CAP.rc | cut -d: -f2`
set NUM_SGMT  = `grep '^\s*NUM_SGMT:'     CAP.rc | cut -d: -f2`
set FSEGMENT  = `grep '^\s*FCST_SEGMENT:' CAP.rc | cut -d: -f2`
set USE_SHMEM = `grep '^\s*USE_SHMEM:'    CAP.rc | cut -d: -f2`

#######################################################################
#              Create HISTORY Collection Directories
#######################################################################
## all diag is written in colelction and then moved to holding outside scratch
#echo "  Create HISTORY Collection Directories "
#set collections = ''
#foreach line ("`cat HISTORY.rc`")
#   set firstword  = `echo $line | awk '{print $1}'`
#   set firstchar  = `echo $firstword | cut -c1`
#   set secondword = `echo $line | awk '{print $2}'`
#
#   if ( $firstword == "::" ) goto done
#
#   if ( $firstchar != "#" ) then
#      set collection  = `echo $firstword | sed -e "s/'//g"`
#      set collections = `echo $collections $collection`
#      if ( $secondword == :: ) goto done
#   endif
#
#   if ( $firstword == COLLECTIONS: ) then
#      set collections = `echo $secondword | sed -e "s/'//g"`
#   endif
#end
#
#done:
#   foreach collection ( $collections )
#      echo "checking if $CYCLEDIR/$collection exists"
#      if (! -e $CYCLEDIR/$collection )         mkdir $CYCLEDIR/$collection
#      echo "checking if $CYCLEDIR/holding/$collection exists"
#      if (! -e $CYCLEDIR/holding/$collection ) mkdir $CYCLEDIR/holding/$collection
#   end

#######################################################################
#                        Link Boundary Datasets
#######################################################################
echo " Link Boundary Datasets"
setenv BCSDIR    /discover/nobackup/ltakacs/bcs/Icarus-NLv3/Icarus-NLv3_Reynolds
setenv SSTDIR    /discover/nobackup/projects/gmao/share/gmao_ops/fvInput/g5gcm/bcs/realtime/OSTIA_REYNOLDS/2880x1440/
setenv CHMDIR    /discover/nobackup/projects/gmao/share/gmao_ops/fvInput_nc3
setenv BCRSLV    CF0090x6C_DE0360xPE0180
setenv DATELINE  DC
setenv EMISSIONS OPS_EMISSIONS

setenv BCTAG `basename $BCSDIR`

set             FILE = linkbcs
/bin/rm -f     $FILE
cat << _EOF_ > $FILE
#!/bin/csh -f

/bin/mkdir -p            ExtData
/bin/ln    -sf $CHMDIR/* ExtData


# Precip correction
#/bin/ln -s /discover/nobackup/projects/gmao/share/gmao_ops/fvInput/merra_land/precip_CPCUexcludeAfrica-CMAP_corrected_MERRA/GEOSdas-2_1_4 ExtData/PCP

 /bin/ln -sf $BCSDIR/$BCRSLV/${BCRSLV}-Pfafstetter.til  tile.data
 if(     -e  $BCSDIR/$BCRSLV/${BCRSLV}-Pfafstetter.TIL) then
 /bin/ln -sf $BCSDIR/$BCRSLV/${BCRSLV}-Pfafstetter.TIL  tile.bin
 endif

# DAS or REPLAY Mode (AGCM.rc:  pchem_clim_years = 1-Year Climatology)
# --------------------------------------------------------------------
#/bin/ln -sf $BCSDIR/Shared/pchem.species.Clim_Prod_Loss.z_721x72.nc4 species.data

# CMIP-5 Ozone Data (AGCM.rc:  pchem_clim_years = 228-Years)
# ----------------------------------------------------------
/bin/ln -sf $BCSDIR/Shared/pchem.species.CMIP-5.1870-2097.z_91x72.nc4 species.data

# S2S pre-industrial with prod/loss of stratospheric water vapor
# (AGCM.rc:  pchem_clim_years = 3-Years,  and  H2O_ProdLoss: 1 )
# --------------------------------------------------------------
#/bin/ln -sf $BCSDIR/Shared/pchem.species.CMIP-6.wH2OandPL.1850s.z_91x72.nc4 species.data

# MERRA-2 Ozone Data (AGCM.rc:  pchem_clim_years = 39-Years)
# ----------------------------------------------------------
#/bin/ln -sf $BCSDIR/Shared/pchem.species.CMIP-5.MERRA2OX.197902-201706.z_91x72.nc4 species.data

/bin/ln -sf $BCSDIR/Shared/*bin .
/bin/ln -sf $BCSDIR/Shared/*c2l*.nc4 .

/bin/ln -sf $BCSDIR/$BCRSLV/visdf_${AGCM_IM}x${AGCM_JM}.dat visdf.dat
/bin/ln -sf $BCSDIR/$BCRSLV/nirdf_${AGCM_IM}x${AGCM_JM}.dat nirdf.dat
/bin/ln -sf $BCSDIR/$BCRSLV/vegdyn_${AGCM_IM}x${AGCM_JM}.dat vegdyn.data
/bin/ln -sf $BCSDIR/$BCRSLV/lai_clim_${AGCM_IM}x${AGCM_JM}.data lai.data
/bin/ln -sf $BCSDIR/$BCRSLV/green_clim_${AGCM_IM}x${AGCM_JM}.data green.data
/bin/ln -sf $BCSDIR/$BCRSLV/ndvi_clim_${AGCM_IM}x${AGCM_JM}.data ndvi.data



/bin/ln -sf $BCSDIR/$BCRSLV/topo_DYN_ave_${AGCM_IM}x${AGCM_JM}.data topo_dynave.data
/bin/ln -sf $BCSDIR/$BCRSLV/topo_GWD_var_${AGCM_IM}x${AGCM_JM}.data topo_gwdvar.data
/bin/ln -sf $BCSDIR/$BCRSLV/topo_TRB_var_${AGCM_IM}x${AGCM_JM}.data topo_trbvar.data


if(     -e  $BCSDIR/$BCRSLV/Gnomonic_$BCRSLV.dat ) then
/bin/ln -sf $BCSDIR/$BCRSLV/Gnomonic_$BCRSLV.dat .
endif


_EOF_


 echo "/bin/ln -sf $SSTDIR/dataoceanfile_OSTIA_REYNOLDS_SST.2880x1440.2023.data sst.data" >> $FILE
 echo "/bin/ln -sf $SSTDIR/dataoceanfile_OSTIA_REYNOLDS_ICE.2880x1440.2023.data fraci.data" >> $FILE
 echo "/bin/ln -sf $SSTDIR/SEAWIFS_KPAR_mon_clim.2880x1440 SEAWIFS_KPAR_mon_clim.data" >> $FILE

chmod +x linkbcs
cp  linkbcs $CYCLEDIR

#######################################################################
#                    Get Executable and RESTARTS
#######################################################################
echo " Get Executable and RESTARTS"
cp $GEOSBIN/GEOSgcm.x .

set rst_files      = `grep "RESTART_FILE"    AGCM.rc | grep -v VEGDYN | grep -v "#" | cut -d ":" -f1 | cut -d "_" -f1-2`
set rst_file_names = `grep "RESTART_FILE"    AGCM.rc | grep -v VEGDYN | grep -v "#" | cut -d ":" -f2`

set chk_files      = `grep "CHECKPOINT_FILE" AGCM.rc | grep -v "#" | cut -d ":" -f1 | cut -d "_" -f1-2`
set chk_file_names = `grep "CHECKPOINT_FILE" AGCM.rc | grep -v "#" | cut -d ":" -f2`

set monthly_chk_names = `cat $CYCLEDIR/HISTORY.rc | grep -v '^[\t ]*#' | sed -n 's/\([^\t ]\+\).monthly:[\t ]*1.*/\1/p' | sed 's/$/_rst/' `

# Remove possible bootstrap parameters (+/-)
# ------------------------------------------
set dummy = `echo $rst_file_names`
set rst_file_names = ''
foreach rst ( $dummy )
  set length  = `echo $rst | awk '{print length($0)}'`
  set    bit  = `echo $rst | cut -c1`
  if(  "$bit" == "+" | \
       "$bit" == "-" ) set rst = `echo $rst | cut -c2-$length`
  set rst_file_names = `echo $rst_file_names $rst`
end

# Copy Restarts to Scratch Directory
# ----------------------------------
# Rsts moved to CYCLEDIR/scratch by getRSTGEOSCF
#foreach rst ( $rst_file_names $monthly_chk_names )
#  if(-e $CYCLEDIR/$rst ) cp $CYCLEDIR/$rst . &
#end
#wait

# If any restart is binary, set NUM_READERS to 1 so that
# +-style bootstrapping of missing files can occur in
# MAPL. pbinary cannot do this, but pnc4 can.
# ------------------------------------------------------
# maybe delete
set found_binary = 0

foreach rst ( $rst_file_names )
   if (-e $rst) then
      set rst_type = `/usr/bin/file -Lb --mime-type $rst`
      if ( $rst_type =~ "application/octet-stream" ) then
         set found_binary = 1
      endif
   endif
end

if ($found_binary == 1) then
   /bin/mv AGCM.rc AGCM.tmp
   cat AGCM.tmp | sed -e "/^NUM_READERS/ s/\([0-9]\+\)/1/g" > AGCM.rc
   /bin/rm AGCM.tmp
endif

##################################################################
######
######         Perform multiple iterations of Model Run
######
##################################################################

@ counter    = 1
while ( $counter <= ${NUM_SGMT} )

/bin/rm -f  EGRESS

cp -f $CYCLEDIR/CAP.rc .

/bin/mv CAP.rc CAP.rc.orig
awk '{$1=$1};1' < CAP.rc.orig > CAP.rc

# Set Time Variables for Current_(c), Ending_(e), and Segment_(s) dates
# ---------------------------------------------------------------------
set nymdc = `awk '{print $1}' cap_restart`
set nhmsc = `awk '{print $2}' cap_restart`
set nymde = `grep '^\s*END_DATE:' CAP.rc | cut -d: -f2 | awk '{print $1}'`
set nhmse = `grep '^\s*END_DATE:' CAP.rc | cut -d: -f2 | awk '{print $2}'`
set nymds = `grep '^\s*JOB_SGMT:' CAP.rc | cut -d: -f2 | awk '{print $1}'`
set nhmss = `grep '^\s*JOB_SGMT:' CAP.rc | cut -d: -f2 | awk '{print $2}'`

# Compute Time Variables at the Finish_(f) of current segment
# -----------------------------------------------------------
set nyear   = `echo $nymds | cut -c1-4`
set nmonth  = `echo $nymds | cut -c5-6`
set nday    = `echo $nymds | cut -c7-8`
set nhour   = `echo $nhmss | cut -c1-2`
set nminute = `echo $nhmss | cut -c3-4`
set nsec    = `echo $nhmss | cut -c5-6`
       @ dt = $nsec + 60 * $nminute + 3600 * $nhour + 86400 * $nday

set nymdf = $nymdc
set nhmsf = $nhmsc
set date  = `$GEOSBIN/tick $nymdf $nhmsf $dt`
set nymdf =  $date[1]
set nhmsf =  $date[2]
set year  = `echo $nymdf | cut -c1-4`
set month = `echo $nymdf | cut -c5-6`
set day   = `echo $nymdf | cut -c7-8`

     @  month = $month + $nmonth
while( $month > 12 )
     @  month = $month - 12
     @  year  = $year  + 1
end
     @  year  = $year  + $nyear
     @ nymdf  = $year * 10000 + $month * 100 + $day

if( $nymdf >  $nymde )    set nymdf = $nymde
if( $nymdf == $nymde )    then
    if( $nhmsf > $nhmse ) set nhmsf = $nhmse
endif

set yearc = `echo $nymdc | cut -c1-4`
set yearf = `echo $nymdf | cut -c1-4`

# For Non-Reynolds SST, Modify local CAP.rc Ending date if Finish time exceeds Current year boundary
# --------------------------------------------------------------------------------------------------
if( DE0360xPE0180 != DE0360xPE0180 ) then
    if( $yearf > $yearc ) then
       @ yearf = $yearc + 1
       @ nymdf = $yearf * 10000 + 0101
        set oldstring = `grep '^\s*END_DATE:' CAP.rc`
        set newstring = "END_DATE: $nymdf $nhmsf"
        /bin/mv CAP.rc CAP.tmp
        cat CAP.tmp | sed -e "s?$oldstring?$newstring?g" > CAP.rc
    endif
endif

# Which ExtData are we using
set  EXTDATA2G_TRUE = `grep -i '^\s*USE_EXTDATA2G:\s*\.TRUE\.'    CAP.rc | wc -l`

# Rename big ExtData files that are not needed
# --------------------------------------------
set            SC_TRUE = `grep -i '^\s*ENABLE_STRATCHEM:\s*\.TRUE\.'     GEOS_ChemGridComp.rc | wc -l`
if (          $SC_TRUE == 0 && -e StratChem_ExtData.rc          ) /bin/mv          StratChem_ExtData.rc          StratChem_ExtData.rc.NOT_USED
set           GMI_TRUE = `grep -i '^\s*ENABLE_GMICHEM:\s*\.TRUE\.'       GEOS_ChemGridComp.rc | wc -l`
if (         $GMI_TRUE == 0 && -e GMI_ExtData.rc                ) /bin/mv                GMI_ExtData.rc                GMI_ExtData.rc.NOT_USED
set           GCC_TRUE = `grep -i '^\s*ENABLE_GEOSCHEM:\s*\.TRUE\.'      GEOS_ChemGridComp.rc | wc -l`
if (         $GCC_TRUE == 0 && -e GEOSCHEMchem_ExtData.rc       ) /bin/mv       GEOSCHEMchem_ExtData.rc       GEOSCHEMchem_ExtData.rc.NOT_USED
set         CARMA_TRUE = `grep -i '^\s*ENABLE_CARMA:\s*\.TRUE\.'         GEOS_ChemGridComp.rc | wc -l`
if (       $CARMA_TRUE == 0 && -e CARMAchem_GridComp_ExtData.rc ) /bin/mv CARMAchem_GridComp_ExtData.rc CARMAchem_GridComp_ExtData.rc.NOT_USED
set           DNA_TRUE = `grep -i '^\s*ENABLE_DNA:\s*\.TRUE\.'           GEOS_ChemGridComp.rc | wc -l`
if (         $DNA_TRUE == 0 && -e DNA_ExtData.rc                ) /bin/mv                DNA_ExtData.rc                DNA_ExtData.rc.NOT_USED
set         ACHEM_TRUE = `grep -i '^\s*ENABLE_ACHEM:\s*\.TRUE\.'         GEOS_ChemGridComp.rc | wc -l`
if (       $ACHEM_TRUE == 0 && -e GEOSachem_ExtData.rc          ) /bin/mv          GEOSachem_ExtData.rc          GEOSachem_ExtData.rc.NOT_USED
set   GOCART_DATA_TRUE = `grep -i '^\s*ENABLE_GOCART_DATA:\s*\.TRUE\.'   GEOS_ChemGridComp.rc | wc -l`
if ( $GOCART_DATA_TRUE == 0 && -e GOCARTdata_ExtData.rc         ) /bin/mv         GOCARTdata_ExtData.rc         GOCARTdata_ExtData.rc.NOT_USED

# 1MOM and GFDL microphysics do not use WSUB_NATURE
# -------------------------------------------------
if ($EXTDATA2G_TRUE == 0 ) then
   /bin/mv WSUB_ExtData.rc WSUB_ExtData.tmp
   cat WSUB_ExtData.tmp | sed -e '/^WSUB_NATURE/ s#ExtData.*#/dev/null#' > WSUB_ExtData.rc
else
   /bin/mv WSUB_ExtData.yaml WSUB_ExtData.tmp
   cat WSUB_ExtData.tmp | sed -e '/collection:/ s#WSUB_Wvar_positive_05hrdeg.*#/dev/null#' > WSUB_ExtData.yaml
endif
/bin/rm WSUB_ExtData.tmp



# Generate the complete ExtData.rc
# --------------------------------
if(-e ExtData.rc )    /bin/rm -f   ExtData.rc
set  extdata_files = `/bin/ls -1 *_ExtData.rc`

# Switch to MODIS v6.1 data after Nov 2021
if( $EXTDATA2G_TRUE == 0 ) then
   set MODIS_Transition_Date = 20211101
   if ( ${EMISSIONS} == OPS_EMISSIONS && ${MODIS_Transition_Date} <= $nymdc ) then
       cat $extdata_files | sed 's|\(qfed2.emis_.*\).006.|\1.061.|g' > ExtData.rc
   else
   cat $extdata_files > ExtData.rc
   endif
endif

if( $EXTDATA2G_TRUE == 1 ) then

  $GEOSBIN/construct_extdata_yaml_list.py GEOS_ChemGridComp.rc
  touch ExtData.rc

endif

# Move GOCART to use RRTMGP Bands
# -------------------------------
# UNCOMMENT THE LINES BELOW IF RUNNING RRTMGP
#
#set instance_files = `/bin/ls -1 *_instance*.rc`
#foreach instance ($instance_files)
#   /bin/mv $instance $instance.tmp
#   cat $instance.tmp | sed -e '/RRTMG/ s#RRTMG#RRTMGP#' > $instance
#   /bin/rm $instance.tmp
#end

# Link Boundary Conditions for Appropriate Date
# ---------------------------------------------
setenv YEAR 2023 #$yearc
./linkbcs

if (! -e tile.bin) then
$GEOSBIN/binarytile.x tile.data tile.bin
endif

# If running in dual ocean mode, link sst and fraci data here
#set yy  = `cat cap_restart | cut -c1-4`
#echo $yy
#ln -sf $SSTDIR/dataoceanfile_MERRA2_SST.${OGCM_IM}x${OGCM_JM}.${yy}.data sst.data
#ln -sf $SSTDIR/dataoceanfile_MERRA2_ICE.${OGCM_IM}x${OGCM_JM}.${yy}.data fraci.data

#######################################################################
#                Split Saltwater Restart if detected
#######################################################################

if ( (-e $SCRDIR/openwater_internal_rst) && (-e $SCRDIR/seaicethermo_internal_rst)) then
  echo "Saltwater internal state is already split, good to go!"
else
 if ( ( ( -e $SCRDIR/saltwater_internal_rst ) || ( -e $EXPDIR/saltwater_internal_rst) ) && ( $counter == 1 ) ) then

   echo "Found Saltwater internal state. Splitting..."

   # If saltwater_internal_rst is in EXPDIR move to SCRDIR
   # -----------------------------------------------------
   if ( -e $EXPDIR/saltwater_internal_rst ) /bin/mv $EXPDIR/saltwater_internal_rst $SCRDIR

   # The splitter script requires an OutData directory
   # -------------------------------------------------
   if (! -d OutData ) mkdir -p OutData

   # Run the script
   # --------------
   $RUN_CMD 1 $GEOSBIN/SaltIntSplitter tile.data $SCRDIR/saltwater_internal_rst

   # Move restarts
   # -------------
   /bin/mv OutData/openwater_internal_rst OutData/seaicethermo_internal_rst .

   # Remove OutData
   # --------------
   /bin/rmdir OutData

   # Make decorated copies for restarts tarball
   # ------------------------------------------
   cp openwater_internal_rst    $EXPID.openwater_internal_rst.${edate}.${GCMVER}.${BCTAG}_${BCRSLV}
   cp seaicethermo_internal_rst $EXPID.seaicethermo_internal_rst.${edate}.${GCMVER}.${BCTAG}_${BCRSLV}

   # Inject decorated copies into restarts tarball
   # ---------------------------------------------
   tar rf $CYCLEDIR/restarts/restarts.${edate}.tar $EXPID.*.${edate}.${GCMVER}.${BCTAG}_${BCRSLV}

   # Remove the decorated restarts
   # -----------------------------
   /bin/rm $EXPID.*.${edate}.${GCMVER}.${BCTAG}_${BCRSLV}

   # Remove the saltwater internal restart
   # -------------------------------------
   /bin/rm $SCRDIR/saltwater_internal_rst
 else
   echo "Neither saltwater_internal_rst, nor openwater_internal_rst and seaicethermo_internal_rst were found. Abort!"
   exit 6
 endif
endif

# Test Openwater Restart for Number of tiles correctness
# ------------------------------------------------------

if ( -x $GEOSBIN/rs_numtiles.x ) then
 
   set N_OPENW_TILES_EXPECTED = `grep '^\s*0' tile.data | wc -l`
   set N_OPENW_TILES_FOUND = `$RUN_CMD 1 $GEOSBIN/rs_numtiles.x openwater_internal_rst | grep Total | awk '{print $NF}'`

   echo $N_OPENW_TILES_EXPECTED
   echo $N_OPENW_TILES_FOUND

   if ( $N_OPENW_TILES_EXPECTED != $N_OPENW_TILES_FOUND ) then
      echo "Error! Found $N_OPENW_TILES_FOUND tiles in openwater. Expect to find $N_OPENW_TILES_EXPECTED tiles."
      echo "Your restarts are probably for a different ocean."
      exit 7
   endif

endif

# Check for MERRA2OX Consistency
# ------------------------------

# The MERRA2OX pchem file is only valid until 201706, so this is a first
# attempt at a check to make sure you aren't using it and are past the date

# Check for MERRA2OX by looking at AGCM.rc
set PCHEM_CLIM_YEARS = `awk '/pchem_clim_years/ {print $2}' AGCM.rc`

# If it is 39, we are using MERRA2OX
if ( $PCHEM_CLIM_YEARS == 39 ) then

   # Grab the date from cap_restart
   set YEARMON = `cat cap_restart | cut -c1-6`

   # Set a magic date
   set MERRA2OX_END_DATE = "201706"

   # String comparison seems to work here...
   if ( $YEARMON > $MERRA2OX_END_DATE ) then
      echo "You seem to be using MERRA2OX pchem species file, but your simulation date [${YEARMON}] is after 201706. This file is only valid until this time."
      exit 2
   endif
endif

# Environment variables for MPI, etc
# ----------------------------------
# potential ewok problem... 
setenv I_MPI_ADJUST_ALLREDUCE 12
setenv I_MPI_ADJUST_GATHERV 3

# This flag prints out the Intel MPI state. Uncomment if needed
#setenv I_MPI_DEBUG 9
setenv I_MPI_SHM_HEAP_VSIZE 512
setenv PSM2_MEMORY large
setenv I_MPI_EXTRA_FILESYSTEM 1
setenv I_MPI_EXTRA_FILESYSTEM_FORCE gpfs


# Run bundleParser.py
#---------------------
python bundleParser.py

# If REPLAY, link necessary forcing files
# ---------------------------------------
set  REPLAY_MODE = `grep '^\s*REPLAY_MODE:' AGCM.rc | cut -d: -f2`
if( $REPLAY_MODE == 'Exact' | $REPLAY_MODE == 'Regular' ) then

     set ANA_EXPID    = `grep '^\s*REPLAY_ANA_EXPID:'    AGCM.rc | cut -d: -f2`
     set ANA_LOCATION = `grep '^\s*REPLAY_ANA_LOCATION:' AGCM.rc | cut -d: -f2`

     set REPLAY_FILE        = `grep '^\s*REPLAY_FILE:'   AGCM.rc | cut -d: -f2`
     set REPLAY_FILE09      = `grep '^\s*REPLAY_FILE09:' AGCM.rc | cut -d: -f2`
     set REPLAY_FILE_TYPE   = `echo $REPLAY_FILE           | cut -d"/" -f1 | grep -v %`
     set REPLAY_FILE09_TYPE = `echo $REPLAY_FILE09         | cut -d"/" -f1 | grep -v %`

     # Modify GAAS_GridComp.rc and Link REPLAY files
     # ---------------------------------------------
     /bin/mv -f GAAS_GridComp.rc GAAS_GridComp.tmp
     cat GAAS_GridComp.tmp | sed -e "s?aod/Y%y4/M%m2/${ANA_EXPID}.?aod/Y%y4/M%m2/${ANA_EXPID}.?g" > GAAS_GridComp.rc

     /bin/ln -sf ${ANA_LOCATION}/aod .
     /bin/ln -sf ${ANA_LOCATION}/${REPLAY_FILE_TYPE} .
     /bin/ln -sf ${ANA_LOCATION}/${REPLAY_FILE09_TYPE} .

     #link the actual FP files that were move to workdir
     #temp changes as we will remove that .j script with jedi
     /bin/ln -sf ${ANA_LOCATION}/${ANA_EXPID}.ana.eta.*.nc4 .


endif

# Establish safe default number of OpenMP threads
# -----------------------------------------------
setenv OMP_NUM_THREADS 1

# Run GEOSgcm.x
# -------------
if( $USE_SHMEM == 1 ) $GEOSBIN/RmShmKeys_sshmpi.csh >& /dev/null

if( $USE_IOSERVER == 1 ) then
   set IOSERVER_OPTIONS = "--npes_model $MODEL_NPES --nodes_output_server $IOS_NODES"

   # Per SI Team, the multigroup server should always be used
   # The ideal number of backend PEs is based on the number of HISTORY
   # collections and number of IO nodes

   # First we figure out the number of collections in the HISTORY.rc (this is not perfect, but is close to right)
   set NUM_HIST_COLS = `cat HISTORY.rc | sed -n '/^COLLECTIONS:/,/^ *::$/{p;/^ *::$/q}' | grep -v '^ *#' | wc -l`

   # Protect against divide by zero
   if ($IOS_NODES == 0) then
      echo "Something is wrong. IOSERVER asked for, but zero IO nodes provided"
      exit 3
   endif

   # Now we divide that number of collections by the ioserver nodes
   echo "NUM_BACKEND_PES = $NUM_BACKEND_PES"
   set NUM_BACKEND_PES = `echo "scale=1;(($NUM_HIST_COLS - 1) / $IOS_NODES)" | bc | awk '{print int($1 + 0.5)}'`

   # Finally multigroup requires at least two backend pes
   if ($NUM_BACKEND_PES < 2) set NUM_BACKEND_PES = 2

   echo "IOSERVER_EXTRA = $IOSERVER_EXTRA"
   set IOSERVER_EXTRA = "--oserver_type multigroup --npes_backend_pernode $NUM_BACKEND_PES"
else
   set IOSERVER_OPTIONS = ""
   set IOSERVER_EXTRA = ""
endif
 
 #set +e
 #$RUN_CMD $NPES ./GEOSgcm.x $IOSERVER_OPTIONS $IOSERVER_EXTRA --logging_config 'logging.yaml'
 $RUN_CMD $NPES ./GEOSgcm.x --logging_config 'logging.yaml'
 #exit_code=$?
 #set -e

if( $USE_SHMEM == 1 ) $GEOSBIN/RmShmKeys_sshmpi.csh >& /dev/null

# if something goes wrong EGRESS File wouldn't exist and rc will be -1
if( -e EGRESS ) then
   set rc = 0
else
   set rc = -1
endif
echo GEOSgcm Run Status: $rc
if ( $rc == -1 ) exit -1

# write geos complete file (this tells the GSI run to stop)
if ( $RUN_GSI == 1 ) then
   set geos_done = "geos_run.done"
   touch ${geos_done}
   echo "written geos checkpoint file: ${geos_done}"
endif

#######################################################################
#   Rename Final Checkpoints => Restarts for Next Segment and Archive
#        Note: cap_restart contains the current NYMD and NHMS
#######################################################################

# saveRstGEOSCF task in ewok saves checkpoints as rst to R2D2 for next cycle

#######################################################################
#               Move HISTORY Files to Holding Directory
#######################################################################

# Move current files to /holding
# ------------------------------
#echo "Move current files to /holding"
#cd $SCRDIR
#foreach collection ( $collections )
#   echo "Moving  $collection"
#   /bin/mv `/bin/ls -1 *.${collection}.*` $CYCLEDIR/holding/$collection
#end

#######################################################################
#                         Update Iteration Counter
#######################################################################

set enddate = `echo  $END_DATE | cut -c1-8`
set capdate = `cat cap_restart | cut -c1-8`

if ( $capdate < $enddate ) then
@ counter = $counter    + 1
else
@ counter = ${NUM_SGMT} + 1
endif

end   # end of segment loop; remain in $SCRDIR
