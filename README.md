# Elasticsearch integration pack

Pack provides many operations helping to manage your Elasticsearch indices. Current functionality is mostly based on [curator](http://www.elastic.co/guide/en/elasticsearch/client/curator/current/).

## Features

Pack provides a set of actions based on curator.

## Curator based actions

Action | Description
------ | -----------
**alias** | Add indices to or remove them from aliases.
**allocation** | Set routing allocation based on tags.
**bloom** | Disable the bloom filter cache for indices.
**close** | Close indices.
**delete.indices** | Delete indices.
**delete.snapshots** | Delete snapshots.
**open** | Open indices.
**optimize** | Optimize indices.
**replicas** | Set replica count per shard.
**show.indices** | Show indices.
**show.snapshots** | Show snapshots.
**snapshot** | Capture snapshot of indices.

Actions invocation parameters will be described further. But for more detailed description what each action actually does please also refer to the [curator docs](http://www.elastic.co/guide/en/elasticsearch/client/curator/current/), it is more in-depth.

### Common parameters

These parameters include general options such as elasticsearch host, port etc.

Parameter | Description | Default
------------ | ------------ | ------------
**host** | Specifies Elasticsearch host to connect to (**required**). | `host_or_ip` | `none`
**url_prefix** | Specifies Elasticsearch http url prefix. | `/`
**port** | Specifies port remote Elasticsearch instance is running on. | `9200`
**use_ssl** | Set to `true` to connect to Elasticsearch through SSL. | `false`
**http_auth** | Colon separated string specifying HTTP Basic Authentication. | `none`
**master_only** | Set to `true` enable operation only on elected master. If connected to a node other than master operation will fail. | `false`
**timeout** | Specifies Elasticsearch operation timeout in seconds. | `600`
**log_level** | Specifies log level \[critical\|error\|warning\|info\|debug\]. | `warn`
**dry_run** | Set to `true` to enable *dry run* mode not performing any changes. | `false`

### Indices/snapshots selection parameters

These parameters filter indices or snapshots when a command is being applied. 

Parameter | Description | Details
------------ | ------------ | ------------
**newer_than** | Filter indices or snapshots which are newer than n time_units. | integer value >= 0
**older_than** | Filter indices or snapshots which are older than n time_units.  | integer value >= 0
**prefix** | Prefix that indices or snapshots must match.
**suffix** | Suffix that indices or snapshots must match.
**time_unit** | Specifies the time interval between indices or snapshots \[hours\|days\|weeks\|months\]. | (default: `days`)
**timestring** | Timestring is the pattern used for matching the dates in indices and snapshots. | ex. `%Y.%m.%d`, see. [python strftime formatting](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior)
**regex** | Include only indices or snapshots matching the provided pattern.
**exclude** | A comma separated list of patterns specifying indices or snapshots to exclude. | **NOT READY**
