## Requests from App Engine Cron/Task Queues fail to reach App Engine when ingress is set to internal-and-cloud-load-balancing

## Steps to Reproduce

Create an App Engine App which uses Cron or Task Queues.

Set the Ingress policy to internal-and-cloud-load-balancing

**Expected results:**

Request specified in Cron configuration or Task Queue enqueue call is executed.

**Actual results:**

Calling system reports failure. No logs appear, not even for failures, in log records.

**Note:**
The task queue system, and cron which is built on top of it, are by very definition 'internal' and should not be blocked by this ingress setting.

## A concrete app with repro steps.

The files in the 'app' directory comprise a simple app which has a no-op cron/push queue responder and a way to enqueue tasks.

Repro can thus be done as follows:

- Create (or re-use) an App Engine app in the Google Cloud Console.
- Deploy this app to it with `gcloud app deploy`. Note the target url and version deployed.
- Deploy the cron schedule with `gcloud app deploy cron.yaml`.

### Verify Cron

Visit https://console.cloud.google.com/appengine/cronjobs and see that a cron job
is set up with a somewhat absurd schedule; the schedule does not have impact on the bug.

Click 'run now' to execute the task.

Verify that the result on the 'cronjobs' page is Succeded, and an entry present in the logs using the console by clicking the 'logs' link.

The log entry will contain all the environment variables, including the following entries

```
'REMOTE_ADDR': '0.1.0.1'
'HTTP_X_APPENGINE_COUNTRY': 'ZZ',
'HTTP_X_APPENGINE_CRON': 'true',
'HTTP_X_APPENGINE_QUEUENAME': '__cron',
```

### Verify Task Queue

Run `curl -d v=${target version} https://${target url}/enqueue/` .

You should get 'Enqueued' as a response.

Visit https://console.cloud.google.com/cloudtasks , the entry may be visible or it may have run.

Visit https://console.cloud.google.com/logs/viewer to verify that it has run /crontest?queue=1.

This time the env vars in the log should include

```
'HTTP_X_APPENGINE_QUEUENAME': 'default',
'REMOTE_ADDR': '0.1.0.2',
```

Run `curl -d "v=${target version}&delay=300" https://${target url}/enqueue/` .

You should again get 'Enqueued' as a response. Visit https://console.cloud.google.com/cloudtasks
to view it there.

### Disable 'public' ingress.

Run `gcloud app services update default --ingress internal-and-cloud-load-balancing`

Note that at this point you can try to view any page from the app in your browser and curl and it should fail with a 403. This is expected.

Now test the cron and task queue.

Visit https://console.cloud.google.com/appengine/cronjobs page and click 'run now'.

Note that the status will be :warning: `Failed`: `The job's latest run failed.`

Visit https://console.cloud.google.com/logs/viewer and note that :warning: no entries are found.

Visit https://console.cloud.google.com/cloudtasks . The task you enqueued a moment ago should not yet have run.
Wait for it to attempt to run, or click 'run now'. Note that the :warning: Retries will go up (with some exponential decay).
Again, note that there are :warning: no associated logs in the log viewer.

### Re-enable 'public' ingress

`gcloud app services update default --ingress all`

Then re-visit the https://console.cloud.google.com/appengine/cronjobs page and click 'run now'.

It should succeed and appear in the logs.

Visit https://console.cloud.google.com/cloudtasks and click 'run now'

It should succeed (disapear) and appear in the logs.

### Additional comment

The 'ingress' configuration does not appear to be visible in the Cloud Console, which may makes this bug harder to analyze and debug.
