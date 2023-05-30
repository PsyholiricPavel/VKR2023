import json
from pymongo import MongoClient
import bson.json_util as json_util
from bson import ObjectId
import os
#MONGOTIMEOUT=5
client = MongoClient("mongodb://localhost:27017/")
#client = MongoClient("mongodb://mongo:27017")#,serverSelectionTimeoutMS=MONGOTIMEOUT)

db = client["Data"] 
dbUsers = db["Users"]
dbVideos = db["Videos"]
def Authorization(data):
    cursor =dbUsers.find_one({'UserName': data['login']})
    if not isRegistredAlready(data['login']):
        return [None,"Not registred"]
    if "Password" not in data or not data['Password']:
        return [None,"No Password"]
    if cursor['Password']== data['Password']:
        return [cursor,"OK"]
    else:
        return [None,"Wrong Password"]
def isRegistredAlready(userN):
    return GetUser(userN)!=None
def NewUser(data):
    NUser={}
    NUser['UserName']=data['UserName']
    NUser['Password']=data['Password']
    NUser['Videos']=[]
    a=dbUsers.insert_one(NUser)
    NUser['_id']=a.inserted_id
    return NUser
def NewVideo(data,user):
    NVideo={}
    NVideo['Name']=data['Name']
    NVideo['Path']=data['Path']
    NVideo['Duration']=data['Duration']
    NVideo['Analized']=False
    NVideo['Detections']=-1
    a=dbVideos.insert_one(NVideo)
    NVideo['_id']=a.inserted_id
    user['Videos'].append(NVideo['_id'])
    dbUsers.update_one({"UserName":user["UserName"]},{'$addToSet':{'Videos': NVideo['_id']}})
    print(NVideo)
    return NVideo
def UpdateVideoData(data):
    dbVideos.update_one({'_id':data['_id']}, {'$set':{'Analized': True, 'Detections' : data['Detections']}})
    return
def UpdateNONVideoData(data):
    dbVideos.update_one({'_id':data['_id']}, {'$set':{'Analized': False, 'Detections' : -1}})
    return
def GetVideosOfUserDB(userN):
    cursor =dbUsers.find_one({'UserName': userN})
    return cursor['Videos']   
def GetVideosForChoice(userN):
    ids=GetVideosOfUserDB(userN)
    arr=[]
    for i in ids:
        video_i=dbVideos.find_one({'_id': i})
        if video_i!=None:
            arr.append(video_i)
    #print(arr)
    return arr
def GetVideo(id):
    cursor =dbVideos.find_one({'_id': ObjectId(id)})
    #print(cursor)
    return cursor
def getVideosFromDB(ids):
    arr=[]
    for i in ids:
        el=GetVideo(i)
        #print(i)
        if el!=None:
            arr.append(el)
    #print(arr)
    return(arr)
def GetUser(userN):
    cursor =dbUsers.find_one({'UserName': userN})
    #print(cursor)
    return cursor
def DeleteVideo(id,user):
    dbUsers.update_one({'Videos':ObjectId(id), 'UserName':user['UserName']},{'$pull':{'Videos':ObjectId(id)}})
    if len(list(dbUsers.find({'Videos':ObjectId(id)})))==0:
        video=dbVideos.find_one({'_id': ObjectId(id)})
        os.remove(video['Path']+'/'+video['Name'])
        dbVideos.delete_one({'_id':ObjectId(id)})
    return
def DeleteAllUserVideo(user):
    arr=GetVideosOfUserDB(user['UserName'])
    for i in arr:
        DeleteVideo(i, user)
def DeleteIMG():
    folder = 'app/img'

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if filename.endswith('.png') and os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Не удалось удалить %s. Причина: %s' % (file_path, e))
dat={'UserName':"PsyholiricPavel",
     'Password':"123",
     'Videos':[]
     }
dat1={
    'Name':"aaa",
    'Path':"aaa",
    'Duration':"aaa"
}
#a=NewVideo(dat1, dat)
#DeleteAllUserVideo(dat)
#DeleteVideo('64753817aa117631ff3e6541', dat)
#DeleteVideo(a['_id'], dat)
#a=['64734ff18f42d16c63b4e4c6', '6474c3cb8ec02f0c58005730', '6474c3e08ec02f0c58005731', '6474c3e88ec02f0c58005732', '6474c40e8ec02f0c58005733', '6474c4168ec02f0c58005734', '6474c4238ec02f0c58005735']
#print(getVideosFromDB(a))
#GetVideosForChoice('Pavel')
