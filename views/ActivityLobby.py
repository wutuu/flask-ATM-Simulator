from flask import render_template,request, flash,session
from flask import Blueprint
from datetime import datetime

from ATMflask import db
from ATMflask.sql import User, Activity, Club

actlb = Blueprint('actlb',__name__)

def parseDate(date_str):
    if date_str:
        return datetime.strptime(date_str, '%Y-%m-%d')
    return None

@actlb.route('/ActivityLobby',methods = ['GET','POST'])  # 用装饰器定义路由的对应关系
def activityLobby():
    user_id = session.get('id')
    username = None
    Act = None
    selected_acts = None
    clubNames = {}

    nowTime = datetime.now().strftime('%Y-%m-%d')

    if user_id:
        user = User.query.get(user_id)
        username = user.username

        ActId = db.session.query(Activity.activity_id).all()
        if ActId == []:
            flash("No activities have been created yet.")
        else:
            ActIdLst = [activity_id[0] for activity_id in ActId]  # 把列表嵌套元组改为列表
            Act = Activity.query.filter(Activity.activity_id.in_(ActIdLst)).all()

            for act in Act:
                ClubId = act.club_id
                clubName = db.session.query(Club.club_name).filter_by(club_id=ClubId).scalar()
                clubNames[act.activity_id] = clubName

        if request.method == 'POST':
            action = request.form.get('action')
            print(f"Action received: {action}")
            print("Form data received:", request.form)
            # 筛选
            if action == 'apply':
                type = request.form.get('type')
                status = request.form.get('status')
                signup_start = request.form.get('signup_start')
                signup_end = request.form.get('signup_end')
                start_time = request.form.get('start_time')
                end_time = request.form.get('end_time')

                signup_start = parseDate(signup_start)
                signup_end = parseDate(signup_end).replace(hour=23, minute=59, second=59)

                start_time = parseDate(start_time)
                end_time = parseDate(end_time).replace(hour=23, minute=59, second=59)

                query = Activity.query
                if type:
                    query = query.filter(Activity.type == type)
                if status:
                    query = query.filter(Activity.status == status)
                if signup_start:
                    query = query.filter(Activity.signup_start >= signup_start)
                if signup_end:
                    query = query.filter(Activity.signup_end <= signup_end)
                if start_time:
                    query = query.filter(Activity.start_time >= start_time)
                if end_time:
                    query = query.filter(Activity.end_time <= end_time)

                selected_acts = query.all()
                print(f"Searching for : {type} and {status} time: {signup_start} and {end_time}")
                print(f"Found activities: {selected_acts}")
                if not selected_acts:
                    flash("No matching activities were found yet.")

            # 搜索
            elif action == 'search':
                search_word = request.form.get('search-input')
                print(f"Searching for activities: {search_word}")
                if search_word:
                    selected_acts = Activity.query.filter(Activity.activity_name.ilike(f"%{search_word}%")).all()
                    if not selected_acts:
                        flash("No matching activities were found yet.")
                else:
                    selected_acts = Act
                print(f"Found activities: {selected_acts}")

            # 清除
            elif action == 'clear':
                print("Clear all activities.")
                selected_acts = Act


        return render_template('ActivityLobby.html', username=username, nowTime=nowTime,Act=Act,selected_acts=selected_acts,clubNames=clubNames)


    if request.method == 'GET':
        return render_template('ActivityLobby.html',username=username,nowTime=nowTime,Act=Act,selected_acts=selected_acts,clubNames=clubNames)





