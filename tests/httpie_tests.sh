#!/bin/bash

printf ">> 'enter' to run command, any input to skip\n"

payload='{"parties": [{"email": "zo@localhost"}], "slots": []}'
user=ob
password=p
auth=$([ -n "$password" ] && echo "-a $user:$password")
addr=$([ -n "$host" ] && echo "$host:${port:-9000}/$pth" || echo :9000/)
printf "|$user |$password |$auth |$addr\n"

#while read -r -u 9 line; do
while read -u 9 line; do
    #echo "$line" | grep -E '^#|^\s*$' 2>&1 > /dev/null || \
    echo "$line" | grep -E '^#|^\s*$' > /dev/null || \
        #(
        {
        #printf "> '$line' ? " #\n"
        #printf "> '$line' ? " | envsubst #\n"
        #printf "> $line ? " #\n"
        #echo "$line" | envsubst '${payload_},${auth}'
        printf "> $(eval echo \"$line\") ? "
        #printf "|$user |$password |$auth |$addr\n"
        #printf "> '%s' ? " "$line" | envsubst #\n"
        read -re reply
        proceed="$(echo "$reply" | grep '^\s*$' 2>&1 > /dev/null; echo $?)"
        if [ "$proceed" == "0" ]; then
            printf "\n"
            #eval $line
            eval "$line"
        else
            printf "skipped\n"
        fi
        }
        #)
done 9< schedul_requests.txt 

