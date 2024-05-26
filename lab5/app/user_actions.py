import csv
from io import BytesIO
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from app import db_connector
from math import ceil
from flask_login import current_user

bp = Blueprint('user_actions', __name__, url_prefix='/user_actions')
MAX_PER_PAGE = 10


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    user_id = current_user.id if current_user.is_authenticated else None
    if current_user.is_admin():
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT last_name, first_name, middle_name, "
                     "path, user_actions.created_at AS created_at "
                     "FROM user_actions LEFT JOIN users ON user_actions.user_id = users.id "
                     "ORDER BY user_actions.created_at DESC "
                     f"LIMIT {MAX_PER_PAGE} OFFSET {(page - 1) * MAX_PER_PAGE}")
            cursor.execute(query)
            user_actions = cursor.fetchall()

            query = "SELECT COUNT(*) as count FROM user_actions"
            cursor.execute(query)
            record_count = cursor.fetchone().count
            page_count = ceil(record_count / MAX_PER_PAGE)
            pages = range(max(1, page - 3), min(page_count, page + 3) + 1)
    else:
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT last_name, first_name, middle_name, "
                     "path, user_actions.created_at AS created_at "
                     "FROM user_actions LEFT JOIN users ON user_actions.user_id = users.id "
                     "WHERE users.id = %s "
                     "ORDER BY user_actions.created_at DESC "
                     f"LIMIT {MAX_PER_PAGE} OFFSET {(page - 1) * MAX_PER_PAGE}")
            cursor.execute(query, (user_id,))
            user_actions = cursor.fetchall()

            query = ("SELECT COUNT(*) as count FROM user_actions "
                     "WHERE user_id = %s")
            cursor.execute(query, (user_id,))
            record_count = cursor.fetchone().count
            page_count = ceil(record_count / MAX_PER_PAGE)
            pages = range(max(1, page - 3), min(page_count, page + 3) + 1)
    return render_template("user_actions/index.html", user_actions=user_actions,
                           page=page, pages=pages, page_count=page_count)


@bp.route('/users_stats')
def users_stats():
    if current_user.is_admin():
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT user_id, last_name, first_name, middle_name, "
                     "COUNT(*) AS entries_counter "
                     "FROM user_actions LEFT JOIN users ON user_actions.user_id = users.id "
                     "GROUP BY user_id ")
            cursor.execute(query)
            print(cursor.statement)
            users_stats = cursor.fetchall()
        return render_template("user_actions/users_stats.html", users_stats=users_stats)
    else:
        flash('Недостаточно прав для доступа к этой странице', 'warning')
        return redirect(url_for('user_actions.index'))


@bp.route('/pages_stats')
def pages_stats():
    if current_user.is_admin():
        page = request.args.get('page', 1, type=int)
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT path, COUNT(*) AS visits_count "
                     "FROM user_actions "
                     "GROUP BY path "
                     "ORDER BY visits_count DESC "
                     f"LIMIT {MAX_PER_PAGE} OFFSET {(page - 1) * MAX_PER_PAGE}")
            cursor.execute(query)
            pages_stats = cursor.fetchall()

            query = ("SELECT COUNT(*) AS count "
                     "FROM ( "
                     "SELECT path, COUNT(*) AS visits_count "
                     "FROM user_actions "
                     "GROUP BY path "
                     "ORDER BY visits_count DESC "
                     ") AS subquery")
            cursor.execute(query)
            record_count = cursor.fetchone().count
            page_count = ceil(record_count / MAX_PER_PAGE)
            pages = range(max(1, page - 3), min(page_count, page + 3) + 1)
        return render_template("user_actions/pages_stats.html", pages_stats=pages_stats,
                               page=page, pages=pages, page_count=page_count)
    else:
        flash('Недостаточно прав для доступа к этой странице', 'warning')
        return redirect(url_for('user_actions.index'))


@bp.route('/page_export.csv')
def page_export():
    if current_user.is_admin():
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT path, COUNT(*) AS visits_count "
                     "FROM user_actions "
                     "GROUP BY path "
                     "ORDER BY visits_count DESC")
            cursor.execute(query)
            pages_stats = cursor.fetchall()
            result = ''
            fields = ['path', 'visits_count']
            result += ','.join(fields) + '\n'
            for record in pages_stats:
                result += ','.join([str(getattr(record, field)) for field in fields]) + '\n'
        return send_file(BytesIO(result.encode()), as_attachment=True, mimetype='text/csv',
                         download_name='page_export.csv')
    else:
        flash('Недостаточно прав для доступа к этой странице', 'warning')
        return redirect(url_for('user_actions.index'))


@bp.route('user_export.csv')
def user_export():
    if current_user.is_admin():
        with db_connector.connect().cursor(named_tuple=True) as cursor:
            query = ("SELECT user_id, last_name, first_name, middle_name, "
                     "COUNT(*) AS entries_counter "
                     "FROM user_actions LEFT JOIN users ON user_actions.user_id = users.id "
                     "GROUP BY user_id ")
            cursor.execute(query)
            print(cursor.statement)
            users_stats = cursor.fetchall()
            result = ''
            fields = ['last_name', 'first_name', 'middle_name', 'entries_counter']
            none_values = ['не', 'авторизованный', 'пользователь']
            result += ','.join(fields) + '\n'
            for record in users_stats:
                if record.user_id is None:
                    result += ','.join(none_values) + ',' + str(record.entries_counter) + '\n'
                    continue
                result += ','.join([str(getattr(record, field)) for field in fields]) + '\n'
        return send_file(BytesIO(result.encode()), as_attachment=True, mimetype='text/csv',
                         download_name='user_export.csv')
    else:
        flash('Недостаточно прав для доступа к этой странице', 'warning')
        return redirect(url_for('user_actions.index'))


@bp.route('paths_stats')
def paths_stats():
    return render_template("user_actions/paths_stats.html")
