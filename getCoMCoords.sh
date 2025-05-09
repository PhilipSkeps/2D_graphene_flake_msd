#!/bin/bash

# $1 is a pattern match containing the files you would like to process

for FILE in *.xtc
do

[[ $FILE =~ ^.*_([0-9])\.xtc$ ]]
NUM=${BASH_REMATCH[1]}
[[ $FILE =~ ^(.*)trim.*$ ]]
FILEBASE=${BASH_REMATCH[1]}
TPR="$FILEBASE"_"$NUM".tpr
XVG_base=${FILE%%.*}
NDX="$FILEBASE"_"$NUM".ndx
[[ $FILE =~ ^(.*)_prod.*$ ]]
GRO=${BASH_REMATCH[1]}"_equ2_out_"$NUM".gro"
LINE=$(tail -2 "$GRO" | head -1)
[[ $LINE =~ (^[0-9]*).* ]]
MAXRESNR=${BASH_REMATCH[1]}

gmx -nobackup make_ndx -f $GRO -o $NDX << EOF 
ri $MAXRESNR
ri $((MAXRESNR-1))
q
EOF

gmx -nobackup traj -com -nojump -f $FILE -s $TPR -n $NDX -ox "CoM"$XVG_base"_"$MAXRESNR".xvg" << EOF &
r_$MAXRESNR
EOF

gmx -nobackup traj -com -nojump -f $FILE -s $TPR -n $NDX -ox "CoM"$XVG_base"_"$((MAXRESNR-1))".xvg" << EOF &
r_$((MAXRESNR-1))
EOF

done

wait
echo 'All Jobs are Complete'