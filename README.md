Openshift cronjob metrics exporter
============================================================


Features
--------

- Three default pod status in Gauge metric (process_is_running,process_is_locked,process_last_exec_with_error).
- Two types of Metric (Gauge,Counter).
- Create and capturing custom metrics by configuration.
- Configuring max wait,the proccess will wait for new metrics of log otherwise process_is_locked will be set to "True".
- Easy for configure.
- The proccess is based in log watch.
- The form of export follows the prometheus format.
- Multiple colectors and contexts.



HOW IT WORKS
---------------------------
The log parser is set by context.
```
{
    "openshift":
    {
        "namespace":"your-project",
        "endpoint":"https://your-openshift.endpoint",
	    "token":"your-service-account-token"
    },
    "colectors":
    [
        {
            "name":"your-cronjob",
            "maxWaitPerRecord": 10,
            "contexts":[{
                "regex_name":"your-metrics-logs-identification-1",
                "Gauge":["your-metric-key-1"],
                "Counter":[]
            },
            {
                "regex_name":"your-metrics-logs-identification-2",
                "Gauge":["your-metric-key-2"],
                "Counter":[]
            }]
        }
    ]
}

```
Logs must maintain a pattern to parse.

The regex that captures the line consists of 

```
    "^.*{} METRICS: ".format(regex_name)
```

This setting will capture the following log line.

```
    [some date dd/mm/yyyy][some info] your-metrics-logs-identification-1 METRICS: {"your-metric-key-1":200}
```

The json is captured from the line then the json decode attempt is made.


The metric value will be set when json will contain the metric key and the value is an instance of int or float.



Below is an example of the url and output from a request that passes the cronjob name to the server followed by /METRICS.

```
 http://your-endpoint/your-metrics-logs-identification-1/METRICS
```

    # Python client for prometheus.io
    # http://github.com/Lispython/pyprometheus
    # Generated at 2019-11-26T14:39:40.432401

    # HELP process_is_running Process (running/not running) status.If 0 not running, if 1 running
    # TYPE process_is_running gauge
    process_is_running{} 1.0 1574779180434
    # HELP process_is_locked Process (locked/unlocked) status.If 0 not locked, if 1 locked
    # TYPE process_is_locked gauge
    process_is_locked{} 0.0 1574779180434
    # HELP process_last_exec_with_error If 0 Last execution was successful, if 1 Last exection terminate wiht Error
    # TYPE process_last_exec_with_error gauge
    process_last_exec_with_error 0.0 1574779180434
    # HELP Metrics type Gauge of key your-metric-key-1
    # TYPE your-metric-key-1 gauge
    your-metric-key-1{} 200 1574779180434


CONTRIBUTE
----------

Fork https://github.com/BrunoSilvaAndrade/openshift-cronjob-metrics-exporter/ , create commit and pull request to ``develop``.