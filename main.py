from telegram import Update
from telegram.ext import Application,MessageHandler,CommandHandler,filters,ContextTypes
import sqlite3
import ast
from datetime import datetime
import emoji
from dotenv import load_dotenv
import os
load_dotenv()
BOT_USERNAME=os.getenv("bot_username")
Token=os.getenv("token")
conn=sqlite3.connect("timetable.db")
c=conn.cursor()

def yap_fun(n):
    skull = emoji.emojize(":skull:", language='alias')
    tilted_rose = emoji.emojize(":wilted_rose:", language='alias')
    sob = emoji.emojize(":sob:",language="alias")
    coffin = emoji.emojize(":coffin:",language='alias')
    chair = emoji.emojize(":chair:",language='alias')
    melted_face=emoji.emojize(":melting_face:",language='alias')
    clown=emoji.emojize(":clown_face:",language='alias')
    if n>80 and n<=100:
        return f"damm bruhh your attendance is higher than teachers {skull} , Bro's not a student anymore, he's a piece of classroom furniture lol {chair}"
    elif n>60 and n<=80:
        return f"Bud thinks he's smart enough to stay near the borderline {clown} and could avoid paying fine lol , snap out of your delulu lil bro {melted_face}"
    else:
        return f"tf bro your attendance is on life support {sob}{tilted_rose} , just giveup you're cooked fr {coffin}"


def take_attendance_fun(n):
    day=n+1
    c.execute(f"SELECT * FROM timeeetable_db WHERE rowid={day}")
    periods=c.fetchall()
    return periods

def timetable_table(list):
    c.execute("""CREATE TABLE IF NOT EXISTS timeeetable_db(
              subject1 text,
              subject2 text,
              subject3 text,
              subject4 text,
              subject5 text,
              subject6 text,
              subject7 text,
              subject8 text,
              subject9 text,
              subject10 text)""")
    conn.commit()
    padded_subjects = [row + (None,) * (10 - len(row)) for row in list]
    c.executemany("INSERT INTO timeeetable_db values(?,?,?,?,?,?,?,?,?,?)",padded_subjects)
    conn.commit()
    c.execute("SELECT rowid,* FROM timeeetable_db")
    show=c.fetchall()
    conn.commit()
    return f"the timetable is as follows (here 1-monday,2-tuesday and so on..) : {show}"
    
def create_table(list):
    c.execute("""CREATE TABLE IF NOT EXISTS attendance_db(
          subject_name text,
          present_attendance INTEGER,
          total_attendance INTEGER)""")
    conn.commit()
    c.executemany("INSERT INTO attendance_db VALUES(?,?,?)",list)
    conn.commit()
    c.execute("SELECT rowid,* FROM attendance_db")
    status=c.fetchall()
    conn.commit()
    return f"the status is : {status}"
async def start_command(update: Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Happy to see you here :)...")
    
async def uploadAttendance_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "attendance"
    await update.message.reply_text("""enter your attendance history in form of a tuple inside of a list -->   [('subject_name',present_attendance,total_attendance)],[],[]....""")

async def create_table_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    message_type=update.message 
    text=update.message.text
    try:
        data = ast.literal_eval(text)
        if type(data)==list:
            if message_type=="group":
                if BOT_USERNAME in text:
                    response=create_table(data)
                else:
                    return 
            else:
                response=create_table(data)

            print("bot:",response)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("please re-enter your attendence history in correct format :)...")
    except Exception as e:
        await update.message.reply_text(f"error : {e}")



async def timetable_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "timetable"
    await update.message.reply_text("""please enter your timetable in the given order:[('subject1','subject2','subject3','subject4','subject5'),(),() ] the timetable of monday should be the first tuple then tuesday should be second tuple and so on.....""")
    
async def timetable_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    message_type=update.message
    text=update.message.text
    try:
        data= ast.literal_eval(text)
        if type(data)==list:
            if message_type=="group":
                if BOT_USERNAME in text:
                    response=timetable_table(data)
                else:
                    return 
            else:
                response=timetable_table(data)

            print("bot:",response)
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("please re-enter your timetable in correct format :)...")
    except Exception as e:
        await update.message.reply_text(f"error: {e} ")


async def take_attendance_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "take"
    await update.message.reply_text(f"""enter 1 if you were present in that lecture,enter 0 if you were not inside of a typle:(1,0,1,1)[this means present in first,third and fourth lecture and absent in second] say 'ok' to proceed""")
async def take_attendance_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    today_num = datetime.today().weekday()
    lectures=take_attendance_fun(today_num)
    if text.lower()=="ok":
        await update.message.reply_text(f"will be taking attendence for the following timetable : {lectures} enter attendance in the correct format")
        return
    if len(lectures)==0:
        await update.message.reply_text("no lecturs are there today")
        return
    message_type=update.message 
    try:
        if message_type=="group":
            if BOT_USERNAME in text:
                new_message=text.replace(BOT_USERNAME," ").strip()
                data=ast.literal_eval(new_message)
                if type(data)==tuple:
                    for i in range(len(lectures[0])):
                        subject = lectures[0][i]
                        if subject is None:
                            continue
                        c.execute("""UPDATE attendance_db SET present_attendance=present_attendance + ?,
                                 total_attendance=total_attendance +1
                                    WHERE subject_name=?""",(data[i],lectures[0][i]))
                    conn.commit()
                    c.execute("SELECT rowid,* FROM attendance_db")
                    updated=c.fetchall()
                    await update.message.reply_text(f"the updated timetable is : {updated}")
            else:
                return
        else:
            data=ast.literal_eval(text)
            if type(data)==tuple:
                    for i in range(len(lectures[0])):
                        subject = lectures[0][i]
                        if subject is None:
                            continue
                        c.execute("""UPDATE attendance_db SET present_attendance=present_attendance + ?,
                                total_attendance= total_attendance + 1
                                    WHERE subject_name=?""",(data[i],lectures[0][i]))
                    conn.commit()
                    c.execute("SELECT rowid,* FROM attendance_db")
                    updated=c.fetchall()
                    await update.message.reply_text(f"the updated timetable is : {updated}")
    except Exception as e:
        await update.message.reply_text(f"error {e}")

async def report_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await report_handler(update,context)
    
async def report_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    c.execute("SELECT * FROM attendance_db")
    final=c.fetchall()
    total,present=0,0
    for values in final:
        total+=values[2]
        present+=values[1]
    attendance_percentage=(present/total)*100
    yap=yap_fun(attendance_percentage)
    await update.message.reply_text(f"your final attendance percentage is : {attendance_percentage}% , {yap}")


async def drop_attendance_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await drop_attendance_handler(update,context)
    
async def drop_attendance_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    c.execute("DROP TABLE attendance_db")
    conn.commit()
    await update.message.reply_text("your attendance data has been dropped!")


async def drop_timetable_command(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await drop_timetable_handler(update,context)
    
async def drop_timetable_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    c.execute("DROP TABLE timeeetable_db")
    conn.commit()
    await update.message.reply_text("your timetable has been dropped!")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode == "attendance":
        await create_table_handler(update, context)

    elif mode == "timetable":
        await timetable_handler(update, context)

    elif mode == "take":
        await take_attendance_handler(update, context)
    
    else:
        await update.message.reply_text("Please first use /attendance, /timetable,/take,/report,/dropa or /dropt")



async def error(update:Update,context:ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__=="__main__":
    print("Starting...")
    app=Application.builder().token(Token).build()

    app.add_handler(CommandHandler("start",start_command))
    app.add_handler(CommandHandler("attendance",uploadAttendance_command))
    app.add_handler(CommandHandler("timetable",timetable_command))
    app.add_handler(CommandHandler("take",take_attendance_command))
    app.add_handler(CommandHandler("report",report_command))
    app.add_handler(CommandHandler("dropt",drop_timetable_command))
    app.add_handler(CommandHandler("dropa",drop_attendance_command))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))
    app.add_error_handler(error)
    # c.execute("DROP TABLE timeeetable_db")
    # conn.commit()
    # conn.close()
    # c.execute("DROP TABLE attendance_db")
    # conn.commit()
    # conn.close()
    print("polling...")
    app.run_polling(poll_interval=3)
    conn.close()
























