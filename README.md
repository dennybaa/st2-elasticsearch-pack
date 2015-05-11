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
**host** | Specifies Elasticsearch host to connect to (**required**). | `none`
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
**exclude** | A comma separated list of patterns specifying indices or snapshots to exclude.

### Indices selection only

Parameter | Description | Details
------------ | ------------ | ------------
**index** | Comma separated string of index names to be included into the operation. | Indices added with this option **will not** be filtered by any of the other index selection parameters.
**all_indices** | Set to `true` to operate on all indices in a cluster. | This option overrides other filtering parameters except **exclude**.

### Snapshot selection only

Parameter | Description | Details
------------ | ------------ | ------------
**snapshot** | Comma separated string of snapshot names to be included into the operation. | Snapshots added with this option **will not** be filtered by any of the other snapshot selection parameters.
**all_snapshots** | Set to `true` to operate on all snapshots in a cluster. | This option overrides other filtering parameters except **exclude**.
**repository** | Provides the repository name for snapshot operations (**required**).

## Search actions

Search actions perform a specified query in Elasticsearch. There are two search actions available: **search.q** and **search.body**. The first one takes a query string (given in lucene syntax), while the former allows to perform more sophisticated searches using Elasticsearch query DSL.

Both search actions use the same *common parameters* as curator based actions.

### search.q specific parameters

This action is enhanced with *index selection* parameters to simplify indices matching.

Parameter | Description
------------ | ------------
**q** | Query in the Lucene query string syntax (**required**).
**df** | The default field to use when no field prefix is defined within the query.
**default_operator** | The default operator to be used, can be AND or OR. Defaults to OR.
**from** | The starting from index of the hits to return. Defaults to 0.
**size** | The number of hits to return. Defaults to 10.
**pretty** | Set to `true` to pretty print JSON response.

### search.body specific parameters

Parameter | Description 
------------ | ------------
**body** | The search definition using the Query DSL (**required**). 
**indices** | A comma-separated list of index names to search. Defaults to `"_all"`.
**from** | The starting from index of the hits to return. Defaults to 0.
**size** | The number of hits to return. Defaults to 10.
**pretty** | Set to `true` to pretty print JSON response.

## Usage and examples

Performing *curator operations* on indices or snapshots **at least one** filtering parameter must be specified. That's a generic rule applied to all of curator actions except *show*,  *show* will act on all indices or snapshots if there aren't any other filtering options.

Now let's have at a few invocation examples.

### Show and deleting indices

* Show indices older than 2 days:
```
st2 run elastic.show.indices host=elk older_than=2 timestring=%Y.%m.%d
```
Shows this on my node:
```json
{
    "result": null, 
    "exit_code": 0, 
    "stderr": "", 
    "stdout": "logstash-2015.05.02
logstash-2015.05.04
"
}
```
* Delete all indices matching *^logstash.\**:

```
st2 run elastic.delete.indices host=elk prefix=logstash
```

### Snapshot operations

* Create a snapshot of indices  based on time range criteria:
```
st2 run elastic.snapshot host=elk repository=my_backup newer_than=20 older_than=10 timestring=%Y.%m.%d
```

This command will create a snapshot of indices newer than 20 days and older than 10 days. Notice that filtering parameters of snapshot command *apply to indices* not to snapshots. That's why it's important not to mess it up. For example, the timestring parameter when created by curator with default options has a different time scheme.

* Delete specific snapshots:
```
st2 run elastic.delete.snapshots host=elk repository=my_backup snapshot=curator-20150506155615,curator-20150506155619
```
* Delete all snapshots:
```
st2 run elastic.delete.snapshots host=elk repository=my_backup all_indices=true
```

### Querying Elasticsearch

On successful search (*total hits > 0*) query actions exit with *return code* == 0, if no documents have been found *return code* == 1. In all other case such as execution exceptions *return code* is 99.

Let's look at a few examples:

* Run query using DSL syntax:
```
st2 run elastic.search.body host=elk body='{"query":{"match_all":{}}}' pretty=true
```

* Run query using URI syntax where **q** is a Lucene string:
```
st2 run elastic.search.q host=elk q='message:my_log_event' prefix=logstash
```


## License and Authors

* Author:: StackStorm (st2-dev) (<info@stackstorm.com>)
* Author:: Denis Baryshev (<dennybaa@gmail.com>)
