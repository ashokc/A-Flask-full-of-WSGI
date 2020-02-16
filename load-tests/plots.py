import pandas, json, sys
import matplotlib.pyplot as plt
from os import path
from datetime import datetime

from matplotlib.legend import Legend

def getSecondsFromEpoch(dateTimeString):
    a = datetime.strptime(dateTimeString,"%Y-%m-%dT%H:%M:%S")
    return a.timestamp()

args = sys.argv
if (len(args) < 2):
    print ("Need 1 arg... run folder")
    sys.exit(0)
else:
    folder = args[1]

plt.rcParams.update({'figure.autolayout': True})

#"Type","Name","Timestamp","# requests","# failures","Requests/s","Requests Failed/s","Median response time","Average response time","Min response time","Max response time","Average Content Size","50%","66%","75%","80%","90%","95%","98%","99%","99.9%","99.99%","99.999","100%"

locust = {}
cmonitor = {}
for method in ['direct', 'nginx']:
    locust[method] = {}
    cmonitor[method] = {}
    for wsgi in ['gunicorn', 'uwsgi', 'uwsgi-http', 'werkzeug']:
        startingTime = 0
        cmonitor_result_file = folder + '/' + method + '_' + wsgi + '.json'
        locust_result_file = folder + '/' + method + '_' + wsgi + '_stats_history.csv'
        print ('Reading in files...', cmonitor_result_file, locust_result_file)

        if path.exists(locust_result_file):
            locust[method][wsgi] = pandas.read_csv(locust_result_file)
            startingTime = locust[method][wsgi]['Timestamp'][0]
            locust[method][wsgi]['Timestamp'] = locust[method][wsgi]['Timestamp'] - startingTime

        if path.exists(cmonitor_result_file):
            with open (cmonitor_result_file) as fh:
                cmonitor[method][wsgi] = json.loads(fh.read())
                if (startingTime == 0):
                    startingTime = getSecondsFromEpoch(cmonitor[method][wsgi]['samples'][0]['timestamp']['datetime'])

                cmonitor[method][wsgi]['Timestamp'] = [getSecondsFromEpoch(cmonitor[method][wsgi]['samples'][k]['timestamp']['datetime']) for k in range(len(cmonitor[method][wsgi]['samples']))]
                cmonitor[method][wsgi]['Timestamp'] = [a - startingTime for a in cmonitor[method][wsgi]['Timestamp']]
                cmonitor[method][wsgi]['load_avg_1min'] = [cmonitor[method][wsgi]['samples'][k]['proc_loadavg']['load_avg_1min'] for k in range(len(cmonitor[method][wsgi]['samples']))]
                cmonitor[method][wsgi]['load_avg_5min'] = [cmonitor[method][wsgi]['samples'][k]['proc_loadavg']['load_avg_5min'] for k in range(len(cmonitor[method][wsgi]['samples']))]
                cmonitor[method][wsgi]['MemFree'] = [cmonitor[method][wsgi]['samples'][k]['proc_meminfo']['MemFree']/1.0e9 for k in range(len(cmonitor[method][wsgi]['samples']))]


colors = {'gunicorn' : 'r', 'uwsgi' : 'g', 'uwsgi-http' : 'b' , 'werkzeug' : 'k' }
linestyles = {'direct' : ':', 'nginx' : '-'}

def plotLines (dataSource, feature, loc1, loc2, filename):
    fig = plt.figure(figsize=(6,6),dpi=720)
    requests_plot = fig.add_subplot(1, 1, 1)
    lines, legends = [], []
    for method in ['direct', 'nginx']:
        if dataSource == 'locust':
            df0 = locust[method]
        if dataSource == 'cmonitor':
            df0 = cmonitor[method]
        for wsgi in ['gunicorn', 'uwsgi', 'uwsgi-http', 'werkzeug']:
            if wsgi in df0.keys():
                df = df0[wsgi]
                legends.append(wsgi)
                lines += requests_plot.plot (df['Timestamp'], df[feature], linestyle=linestyles[method], color=colors[wsgi])

    requests_plot.legend(lines[0:3], legends[0:3], loc=loc1, prop={'size': 10}, frameon=True)
    leg = Legend(requests_plot, lines[3:7], legends[3:7], loc=loc2, prop={'size': 10}, frameon=True)
    requests_plot.add_artist(leg);
    fig.savefig(folder + '/' + filename + '.png', format='png', dpi=720)
    plt.close(fig)

plotLines ('cmonitor', 'load_avg_1min', 'upper left', 'upper right', 'load_avg_1_min')
plotLines ('cmonitor', 'load_avg_5min', 'upper left', 'upper right', 'load_avg_5_min')
plotLines ('cmonitor', 'MemFree', 'upper center', 'lower left', 'MemFree')
plotLines ('locust', '# failures', 'center left', 'center right', 'failures')
plotLines ('locust', '# requests', 'upper left', 'lower right', 'requests')
plotLines ('locust', 'Median response time', 'upper left', 'lower right', 'median_response_time')
plotLines ('locust', 'Average response time', 'upper left', 'lower right', 'average_response_time')
plotLines ('locust', '90%', 'upper left', 'lower right', '90_response_time')

