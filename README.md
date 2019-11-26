Openshift Cronjob metrics exporter
============================================================


Features
--------

- Three default Gauge metrics (process_is_running,process_is_locked,process_last_exec_with_error)
- 2 Metric types(Gauge,Counter)
- Create and capture custom metrics by configuration.
- Configure max waiting for capture new metric or process_last_exec_with_error is seted with "True"
- Simple Configuration
- The proccess is based is log watch
- Export type prometheus
- Multiple colectors and contexts



THE OPERATION OF THE SYSTEM
---------------------------
The log parser is set by context.
    {
    "regex_name":"your-metrics-logs-identification-1",
    "Gauge":["your-metric-key-1"],
    "Counter":[]
    }

Logs must maintain a pattern to parse.

The regex that captures the line consists of "^.*{} METRICS: ".format(regex_name)

This setting will capture the following log line.
    [some date dd/mm/yyyy][some info] your-metrics-logs-identification-1 METRICS: {"your-metric-key-1":200}

The json is removed from the line then the json parse attempt is made.

Then the existence of the Metrica key inside the Object is verified, if key exist and value is instance of int or float, the metric is seted.

Follow output metrics in call http endpoint-> http://your-endpoint/your-metrics-logs-identification-1/METRICS

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