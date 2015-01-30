#!/bin/bash

output=$(python depmat.py $1)
keys=$(echo "$output" | grep "'" | sed "s/ //g;s/\[//g;s/\]//g;s/[',]//g")
size=$(echo "$keys" | wc -l)
matrix=$(echo "$output" | tail -n$size)

max=1
for key in $keys; do
    len=${#key}
    [ $len -gt $max ] && max=$len
done

padding=$(echo $matrix | grep -o '[0-9]*' | sort -ug | head -n1)
[ $padding -gt 9 ] && padding=2 || padding=1

for ((i=$max-1; i>=0; i--)); do
    for ((m=0; m<$max+1; m++)); do
        echo -n " "
    done
    echo "$keys" | while read key; do
        char="${key:$i:1}"
        for ((p=0; p<$padding+1; p++)); do
            echo -n " "
        done
        echo -n "${char:- }"
    done
    echo
done

for ((i=1; i<=$size; i++)); do
    key=$(echo "$keys" | head -n$i | tail -n1)
    row=$(echo "$matrix" | head -n$i | tail -n1)
    printf "%*s %s\n" $max "$key" "$row"
done
