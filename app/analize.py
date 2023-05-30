import numpy as np
import cv2
import threading
import time
import heapq
import os
import matplotlib
matplotlib.use('Agg')
import sympy as sp
import matplotlib.pyplot as plt
from pathlib import Path
from Db_manager import *
from pprint import pprint
arrray=[]
THREADS=10
def getVideosName(date=""):
    videos=[]
    for root, dirs, files in os.walk("videos/"+date):
        for filename in files:
            videos.append(root+'/'+filename)
    return videos
def getVideosDuration(videosNames):
    arr=[]
    for i in videosNames:
        cap = cv2.VideoCapture(i)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        cap.release()
        arr.append([duration,i])
    return arr
def getOneVideoDuration(videosNames):
    cap = cv2.VideoCapture(i)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    return duration
def divide_almost_equally(arr, num_chunks):
    arr.sort(key=lambda x: x['Duration'],reverse=True) 
    heap = [(0, idx) for idx in range(num_chunks)]
    heapq.heapify(heap)
    sets = {}
    for i in range(num_chunks):
        sets[i] = []
    arr_idx = 0
    while arr_idx < len(arr):
        set_sum, set_idx = heapq.heappop(heap)
        sets[set_idx].append(arr[arr_idx])
        set_sum += arr[arr_idx]['Duration']
        heapq.heappush(heap, (set_sum, set_idx))
        arr_idx += 1
    return sets.values()
def divederByDuration(ids,col):
    arr=ids
    sets = divide_almost_equally(arr, col)
    ret=[]
    for i in sets:
        ret.append([j for j in i])
    return ret
def video_analizator(video,thrNumber):
    timeSt=time.time()
    i=0
    videoName=video['Path']+'/'+video['Name']
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    threads = []
    cv2.startWindowThread()
    video['Detections']=0
    cap = cv2.VideoCapture(videoName)
    ret, frame = cap.read()

    if not ret:
            print("[Thread{0}]".format(thrNumber),"Can't receive frame of "+videoName+" Exiting")
            return

    i+=1
    print("[Thread{0}]".format(thrNumber),videoName,'analyse started video duration is',video['Duration'])
    while(True):
        ret, frame = cap.read()
        if not ret:
            print("[Thread{0}]".format(thrNumber),videoName,"analysed sucsefull.",i,"frames.","Time:",time.time()-timeSt,"Detections:",video['Detections'])
            UpdateVideoData(video)
            return video['Detections']
        i+=1
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )
        video['Detections']+=len(boxes)
        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

        for (xA, yA, xB, yB) in boxes:
            cv2.rectangle(frame, (xA, yA), (xB, yB),
                            (0, 255, 0), 2)
    cap.release()
    cv2.destroyAllWindows()
def lineAnalyse(thrNumber,videos):
    for i in videos:
        val=video_analizator(i,thrNumber)
def toAnalize(ids,thrs):
    if len(ids)<thrs:
        thrs=len(ids)
    threads = []
    arr=divederByDuration(ids, thrs)
    thrNumber=0
    for i in arr:
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
def printerGraf(ids):
    data=getVideosFromDB(ids)
    data.sort(key=lambda x: x['Name'],reverse=False)
    plt.clf()
    x_values = [item['Name'].split('.')[0] for item in data]
    y_values = [item['Detections']/item['Duration'] for item in data]
    plt.plot(x_values, y_values)
    plt.title('Проходимость')
    plt.xlabel('Видеофрагменты')
    plt.ylabel('Детекций в секунду')
    plt.tick_params(axis='x', rotation=90)
    timeSt=time.time()
    filename="graf"+str(time.time())+'.png'
    #plt.show()
    plt.savefig(os.path.join(os.getcwd(), 'app', 'img', filename),bbox_inches='tight')
    return filename