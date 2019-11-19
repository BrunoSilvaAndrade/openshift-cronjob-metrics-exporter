CONTJOB_TEMPLATE = "cronjob-{}"
TIME_BETWEEN_ITERS = 5
API_PREFIX_NS = "api/v1/namespaces/viamais-sync/{}"
API_PREFIX_GET_PODS = API_PREFIX_NS.format("pods")
API_PREFIX_GET_ESPECIFIED_POD = API_PREFIX_NS.format("pods/{}")
API_POSTFIX_GET_LOGS = "{}/log?tailLines=0&follow=true"
REGEX_TEMPLATE_CAPT_METRCIS = "^.*{} METRICS: "