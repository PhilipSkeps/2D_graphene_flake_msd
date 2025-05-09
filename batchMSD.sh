#!/bin/bash

for FILE in *.xtc; 
do

[[ $FILE =~ ^.*_([0-9])\.xtc$ ]]
NUM=${BASH_REMATCH[1]}
[[ $FILE =~ ^(.*)trim.*$ ]]
FILEBASE=${BASH_REMATCH[1]}
TPR="$FILEBASE"_"$NUM".tpr
XVG_base=${FILE%%.*}
[[ $FILE =~ ^(.*)_prod.*$ ]]
GROROOT=${BASH_REMATCH[1]}
LINE=$(tail -2 "$GROROOT"_equ2_out_"$NUM".gro | head -1)
[[ $LINE =~ (^[0-9]*).* ]]
MAXRESNR=${BASH_REMATCH[1]}

echo MAXRESNR: $MAXRESNR >> ${LOG}

gmx -nobackup msd -f ${FILE} -s ${TPR} -o "${XVG_base}x.xvg" -type x << EOF &
resnr $MAXRESNR
resnr $((MAXRESNR-1))
EOF

gmx -nobackup msd -f ${FILE} -s ${TPR} -o "${XVG_base}y.xvg" -type y << EOF &
resnr $MAXRESNR
resnr $((MAXRESNR-1))
EOF

gmx -nobackup msd -f ${FILE} -s ${TPR} -o "${XVG_base}xy.xvg" -lateral z << EOF &
resnr $MAXRESNR
resnr $((MAXRESNR-1))
EOF

done

wait # wait for all jobs to finish
echo 'All Jobs are Complete'
