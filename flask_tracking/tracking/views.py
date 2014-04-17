from flask import abort, Blueprint, flash, jsonify, Markup, redirect, render_template, request, url_for
from flask.ext.login import current_user, login_required

from .forms import PunchInForm, VisitForm

from .models import Site, Entry
from ..users.models import User

from flask_tracking.data import query_to_list
import datetime

tracking = Blueprint("tracking", __name__)


@tracking.route("/")
def index():
    if not current_user.is_anonymous():
        return redirect(url_for(".view_sites"))
    return render_template("index.html")


@tracking.route("/sites/<int:site_id>")
@login_required
def view_site_visits(site_id=None):
    site = Site.get_or_404(site_id)
    if not site.user_id == current_user.id:
        abort(401)

    query = Visit.query.filter(Visit.site_id == site_id)
    data = query_to_list(query)
    return render_template("tracking/site.html", visits=data, site=site)

def prettyEntries(e):
    l = []
    for t in e:
        g = []
        for cell in t:
            if type(cell) is str or type(cell) is unicode or  len(g) == 0:
                g.append(cell)
            elif cell is None:
                g.append("")
            else:
                if (cell.year == 1):
                    g.append("In Progress")
                else:
                    g.append(cell.strftime('%Y-%m-%d %H:%M'))
        l.append(g)
    return l


@tracking.route("/timecards/<int:user_id>")
def listTimecards(user_id = None):
    timecards = Entry.query.filter(Entry.user_id == user_id).with_entities(Entry.id, Entry.punchIn, Entry.punchOut,Entry.punchOutComment).all()
    l = prettyEntries(timecards)
    return render_template("tracking/entries.html", entries=l, user_id=user_id)

@tracking.route("/timecards/all")
def allTimecards():
    timecards = User.query.all()
    return render_template("tracking/all.html", users=timecards)


@tracking.route("/timecards/<int:user_id>/punchIn")
def punch_in(user_id=None):
    entry = Entry.create(user_id=user_id)
    timecards = Entry.query.filter(Entry.user_id == user_id).with_entities(Entry.id, Entry.punchIn, Entry.punchOut,Entry.punchOutComment).all()
    l = prettyEntries(timecards)

    return render_template("tracking/entries.html", entries=l, user_id=user_id)

@tracking.route("/timecards/<int:user_id>/<int:entry_id>/punchOut")
def punch_out(user_id, entry_id):    
    e = Entry.query.filter(Entry.id == entry_id).one()
    if e.punchOut == datetime.datetime.min:
        e.punch_out()
        return e.punchOut.strftime('%Y-%m-%d %H:%M'),200
    return '',400

    #return render_template("tracking/entries.html", entries=l, user_id=user_id)

@tracking.route("/timecards/<int:user_id>/<int:entry_id>/updateComment", methods=["POST", "GET"])
def updateComment(user_id, entry_id):    
    comment = request.values.get("comment")
    entry = Entry.query.filter(Entry.id == entry_id).one()
    entry.updateComment(comment);


    return '',200

@tracking.route("/timecards/<int:user_id>/<int:entry_id>/deleteEntry", methods=["GET"])
def deleteEntry(user_id, entry_id):    
    entry = Entry.query.filter(Entry.id == entry_id).one()
    entry.delete();

    return '',200




@tracking.route("/sites", methods=("GET", "POST"))
@login_required
def view_sites():
    form = PunchInForm()

    if form.validate_on_submit():
        Entry.create(owner=current_user, **form.data)
        flash("Punched In")
        return redirect(url_for(".punchOut"))

    query = Entry.query.filter(Entry.user_id == current_user.id)
    data = query_to_list(query)
    results = []

    try:
  
        results = [next(data)]
        for row in data:
            row = [_make_link(cell) if i == 0 else cell
                   for i, cell in enumerate(row)]
            results.append(row)
    except StopIteration:

        pass

    return render_template("tracking/entries.html", entries=results, form=form)


_LINK = Markup('<a href="{url}">{name}</a>')


def _make_link(site_id):
    url = url_for(".view_site_visits", site_id=site_id)
    return _LINK.format(url=url, name=site_id)
