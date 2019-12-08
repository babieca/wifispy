#!/bin/bash

MON=urtwn0
OPATH=/home/juan/scans/outputs
TOUT=/home/juan/.local/bin/timeout -t 8

clear

ifconfig $MON down

echo "`ifconfig $MON`"
echo "---------------------------------------"
echo ""
printf "Change interface $MON MAC address [y/N]?: "
read -r user_mac

if [[ $user_mac == 'y' ]]; then
	macrandr -c
	echo "$MON interface changed"
	echo "---------------------------------------"
	echo ""
	echo "`ifconfig $MON`"
	echo "---------------------------------------"
	echo ""
fi

printf "change interface $MON to monitor mode [y/N]?: "
read -r user_mon

if [[ $user_mon == 'y' ]]; then
	ifconfig $MON mediaopt monitor
	echo "Interface $MON configured in monitor mode"
	echo "---------------------------------------"
	echo ""
	echo "`ifconfig $MON`"
	echo "---------------------------------------"
fi


user_opt=""

printf "Listen channel(s): [<all>]: "
read -r user_chnl
if [[ $user_chnl != '' ]]; then
    user_opt="$user_opt --channel $user_chnl"
fi

printf "BSSID: [<none>]: "
read -r user_bssid
if [[ $user_bssid != '' ]]; then
    user_opt="$user_opt --bssid $user_bssid"
fi

while true
do
    NOW=$( date '+%F_%H:%M:%S' )
    OFILE="$OPATH/scan-$NOW"
    $TOUT airodump-ng $MON $user_opt -w $OFILE -o csv --uptime --manufacturer --showack &
	PID=$!
    sleep 30
    kill -INT $PID
done
