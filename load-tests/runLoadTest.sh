#!/bin/bash

clients=$1
hatch_rate=$2
length_of_time=$3

sleep_time=30

results_dir="./runs/all_"$clients"_"$hatch_rate"_"$length_of_time
mkdir -p $results_dir
if [ $? -ne 0 ]; then
	echo "Could not create directory... exiting"
	exit 1
fi

for dir in direct nginx; do
	for file in ./$dir/*.py; do
		echo "Staring the run for $dir $file"
		base=$(basename $file .py)
		sleep $sleep_time
		csv_outfile=$results_dir"/"$dir"_"$base
		perf_outfile=$results_dir"/"$dir"_"$base".json"
		echo "Starting the monitor $perf_outfile sleeping for $sleep_time seconds"
		/usr/bin/cmonitor_collector --sampling-interval=3 --output-filename=$perf_outfile
		sleep $sleep_time
		echo "pipenv run locust -f $file --host localhost --csv $csv_outfile -c $clients -r $hatch_rate -t $length_of_time -L INFO --only-summary --no-web"
		pipenv run locust -f $file --host localhost --csv $csv_outfile -c $clients -r $hatch_rate -t $length_of_time"m" -L INFO --only-summary --no-web
		sleep $sleep_time
		pid=$(ps -ef | grep 'cmonitor_collector' | grep -v 'grep' | awk '{ print $2 }')
		echo "Terminating the collector for:$perf_outfile sleeping for $sleep_time seconds"
		echo ""
		echo ""
		kill -15 $pid
		sleep $sleep_time
	done
done

pipenv run python ./plots.py $results_dir
pipenv run python ./plots2.py

