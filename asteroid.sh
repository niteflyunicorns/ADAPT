#!/bin/bash
#SBATCH --job-name=adapt  #the name of your job

#change to your NAUID
#SBATCH --output=/scratch/sjc497/adapt-isoforest-timing100New2.out #this is the file for stdout 
#SBATCH --error=/scratch/sjc497/adapt-isoforest-timing100New2.err #this is the file for stderr

#SBATCH --time=00:10:00
#SBATCH --mem=8GB
#SBATCH --cpus-per-task=1

# VARIABLES ---------------------------------------
# required variables:
maxIn=1
offset=1000
# fromFileFlg=False
# file="/home/sjc497/ADAPT/astNames.csv"
# attrs=['elong', 'mag18omag8', 'H', 'rb']

fltrType='isoforest'
# ^ fltrType can be one of:
# 'anomaly', 'dbscan', 'isoforest', 'mix'
fltrLvl=2

plots=True
exportFlg=True

# optional variables:
fileType=2 # default 2 (.csv)
fileName="/scratch/sjc497/ADAPT/data/" # default ""
astName=2156 # default 0
featFltr=n # default n
lB=0 # default 0
uB=0 # default 0



# PRE-RUN STUFF
# remove output files from previous run
# rm -f /scratch/sjc497/astMat.*
# load conda in case it's not loaded already
# module load anaconda3
# conda activate astroEnv


# PROFILING ---------------------------------------
# assumes there is no plots or output
# time kernprof -lv runADAPT.py "$maxIn" "$offset" "$fltrType" "$fltrLvl" "$plots" "$exportFlg"


# RUNNING -----------------------------------------
# No export, multiple asteroids
if [ $exportFlg == "False" ]; then
	if [ $maxIn -gt 1 ]; then
		# No export, multiple asteroids
		time python runADAPT.py "$maxIn" "$offset" "$fltrType" "$fltrLvl" "$plots" "$exportFlg" "$fromFileFlg"
	else
	   # No export, single asteroid
	   time python runADAPT.py "$maxIn" "$offset" "$fltrType" "$fltrLvl" "$plots" "$exportFlg" "$astName" "$featFltr" "$lB" "$uB"
   fi
else
	if [ $maxIn -gt 1 ]; then
		# Export, multiple asteroids
		time python runADAPT.py "$maxIn" "$offset" "$fltrType" "$fltrLvl" "$plots" "$exportFlg" "$fileType" "$fileName"
	else
		# Export, single asteroid
		time python runADAPT.py "$maxIn" "$offset" "$fltrType" "$fltrLvl" "$plots" "$exportFlg" "$fileType" "$fileName" "$astName" "$featFltr" "$lB" "$uB"
    fi
fi



# if [ $fromFileFlg == "True" ]; then
# time python runADAPT.py "$maxIn" "$offset" "$fltrType" "$fltrLvl" "$plots" "$exportFlg" "$fromFileFlg" "$fileType" "$fileName" "$file"

# if [$(maxIn) == -1]; then
# fi

# if [$(maxIn) == 1]; then
# 	echo -n "file type: "
# 	read fileType
# 	echo -n "file name: "
# 	read fileName
# fi

# if [$(exportFlg) == 'n']; then
# fi

   # New Program Variables / Args

   # number of asteroids
   # if only one:
   # 	  get name
   # 	  feature to filter by
   # 	  lower bound
   # 	  upper bound

   # export results flag
   # if yes:
   # 	  file type
   # 	  file name
		 
   # starting position
	  
   # filter type
   # filter value
