# DataHQ Spec Store

[![Build Status](https://travis-ci.org/datahq/specstore.svg?branch=master)](https://travis-ci.org/datahq/specstore)

An API server for managing a Source Spec Registry

## Quick start

### Clone the repo and install

`make install`

### Run tests

`make test`

### Run server

`python server.py`

## Env Vars
- `DATABASE_URL`: A SQLAlchemy compatible database connection string (where registry is stored)
- `AUTH_SERVER`: The domain name for the authentication server
- `DPP_URL`: URL for the datapackage pipelines service (e.g. `http://host:post/`)

## API

### Status

`/source/{identifier}/status`

#### Method

`GET`

#### Response

```javascript=
{
   'state': 'LOADED/REGISTERED/INVALID/RUNNING/SUCCEEDED/FAILED',
   'logs': [
              'log-line',
              'log-line', // ...
           ],
   'modified': 'flowmanager-timestamp-of-pipeline-data
}
```

### Status

`/source/{identifier}/info`

#### Method

`GET`

#### Response

```javascript=
{
  "id": "./<pipeline-id>",

  "pipeline": <pipeline>,
  "source": <source>,

  "message": <short-message>,
  "error_log": [ <error-log-lines> ],
  "reason": <full-log>,

  "state": "LOADED/REGISTERED/INVALID/RUNNING/SUCCEEDED/FAILED",
  "success": <last-run-succeeded?>,
  "trigger": <dirty-task/scheduled>,

  "stats": {
      "bytes": <number>,
      "count_of_rows": <number>,
      "dataset_name": <string>,
      "hash": <datapackage-hash>
  },

  "cache_hash": "c69ee347c6019eeca4dbf66141001c55",
  "dirty": false,

  "queued": <numeric-timestamp>,
  "started": <numeric-timestamp>,
  "updated": <numeric-timestamp>,
  "last_success": <numeric-timestamp>,
  "ended": <numeric-timestamp>
}
```

state definition:

- `LOADED`: In the flowmanager, pipeline not created yet
- `REGISTERED`: Waiting to run
- `INVALID`: Problem with the source spec or the pipeline
- `RUNNING`: Currently running
- `SUCCEEDED`: Finished successfully
- `FAILED`: Failed to run

### Upload

`/source/upload`

#### Method

`POST`

#### Headers

* `Auth-Token` - permission token (received from conductor)
* Content-type - application/json

#### Body

A valid spec in JSON form. You can find example Flow-Spec in README of [planer API](https://github.com/datahq/planner/commit/d4dbc6bbd4d215ed1617969e3a502953b6b62910)

#### Response

```javascript=
{
  "success": true,
  "id": "<identifier>"
  "errors": [
      "<error-message>"
  ]
}
```

### Update

`/source/update`

#### Method

`POST`

#### Body

Payload in JSON form.

```javascript=
{
  "pipeline": "<pipeline-id>",
  "event": "queue/start/progress/finish",
  "success": true/false (when applicable),
  "errors": [list-of-errors, when applicable]
}
```

#### Response
```javascript=
{
  "success": success/pending/fail,
  "id": "<identifier>"
  "errors": [
      "<error-message>"
  ]
}
```
