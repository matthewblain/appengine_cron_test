import logging
import os
import pprint
from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class CronTestPage(webapp.RequestHandler):
    def get(self):
        env = pprint.pformat(dict(os.environ))
        logging.info(env)
        self.response.out.write("Done.")


class EnqueuePage(webapp.RequestHandler):
    def post(self):
        """Enqueues a task in the future.

        For 'security' purposes, this requires a POST and also that the
        post param 'v' matches the major version of the app.

        Optionally, a 'delay' param can be passed in which will enqueue
        the task to run that many seconds into the future.
        """

        env = pprint.pformat(dict(os.environ))
        logging.info(env)

        version = os.environ.get("CURRENT_VERSION_ID", "0.0")
        major_version = version.split(".")[0]

        v = self.request.get("v")
        delay = self.request.get("delay")
        if delay:
            delay = int(delay)
        else:
            delay = None
        if v == major_version:
            t = taskqueue.add(url="/crontest?queue=1", method="GET", countdown=delay)
            self.response.out.write("Enqueued: %s" % t)
            logging.info("Enqueued: %s", t)
        else:
            self.response.out.write("Ignored.")
            logging.info("Ignored.")


# Register the URL with the responsible classes
application = webapp.WSGIApplication(
    [
        ("/crontest", CronTestPage),
        ("/enqueue", EnqueuePage),
    ],
    debug=True,
)

# Register the wsgi application to run


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
