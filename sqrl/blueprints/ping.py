"""Endpoints for reporting service status and health."""
from flask import Blueprint

bp = Blueprint('ping', __name__, url_prefix='/ping')


@bp.route('/')
def index():
    """Report if the Sqrl server is up and running.

    It does not report the health of the service, just whether it is
    reachable (i.e. running).  The return value of this endpoint can be
    anything as long as the response has a status code of 200.
    """
    return 'pong'
