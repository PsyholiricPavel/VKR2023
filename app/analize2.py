import numpy as np
import cv2
import threading
import time
import heapq
import os
import matplotlib.pyplot as plt
import sympy as sp
from pathlib import Path
from Db_manager import *
arrray=[]
THREADS=10
def getVideosName(date=""):
    videos=[]
    for root, dirs, files in os.walk("videos/"+date):
        for filename in files:
            videos.append(root+'/'+filename)
    #print(videos)
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
    arr.sort(key=lambda x: x[0],reverse=True) 
    heap = [(0, idx) for idx in range(num_chunks)]
    heapq.heapify(heap)
    sets = {}
    for i in range(num_chunks):
        sets[i] = []
    arr_idx = 0
    while arr_idx < len(arr):
        set_sum, set_idx = heapq.heappop(heap)
        sets[set_idx].append(arr[arr_idx])
        #print(set_sum)
        set_sum += arr[arr_idx][0]
        heapq.heappush(heap, (set_sum, set_idx))
        arr_idx += 1
    return sets.values()


def divederByDuration(arr,col):
    sets = divide_almost_equally(arr, col)
    #print(f"{arr.sort(key=lambda x: x[1],reverse=True)}   {sum(i[0] for i in arr)}\n")
    #print(sets)
    ret=[]
    for i in sets:
        #print(f"{[j[1] for j in i]}   {sum(j[0] for j in i)}")
        ret.append([[j[1],j[0]] for j in i])
    return ret

def video_analizator(videoName,duration,thrNumber):
    timeSt=time.time()
    i=0
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    threads = []
    cv2.startWindowThread()
    detections=0
    cap = cv2.VideoCapture(videoName)
    ret, frame = cap.read()

    if not ret:
            print("[Thread{0}]".format(thrNumber),"Can't receive frame of "+videoName+" Exiting")
            return

    i+=1
    print("[Thread{0}]".format(thrNumber),videoName,'analyse started video duration is',duration)
    while(True):
        ret, frame = cap.read()
        if not ret:
            #print("[Thread{0}]".format(thrNumber),videoName,"analysed sucsefull.",i,"frames.","Time:",time.time()-timeSt,"Detections:",detections)
            return detections
        i+=1
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )
        #print(len(boxes),i)
        detections+=len(boxes)
        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

        for (xA, yA, xB, yB) in boxes:
            cv2.rectangle(frame, (xA, yA), (xB, yB),
                            (0, 255, 0), 2)
        
        #cv2.imshow("Frame", frame)
        #if cv2.waitKey(5) & 0xFF == ord('q'):
        #    break
    cap.release()
    cv2.destroyAllWindows()

def lineAnalyse(thrNumber,videosNames):
    for i in videosNames:
        val=video_analizator(i[0], i[1],thrNumber)
        arrray.append([i[0], i[1],val])
        #print(val,arrray)
    
def toAnalize(files,thrs):
    if len(files)<thrs:
        thrs=len(files)
    #print(thrs)
    threads = []
    arr=divederByDuration(getVideosDuration(files), thrs)
    #print(arr)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    printer(arrray)
    #print(arrray)
def printer(data):
    x_values = [Path(item[0]).stem  for item in data]
    y_values = [item[2]/item[1] for item in data]
    plt.plot(x_values, y_values)
    plt.title('Проходимость')
    plt.xlabel('Видеофрагменты')
    plt.ylabel('Детекций в секунду')
    plt.tick_params(axis='x', rotation=90)
    timeSt=time.time()
    filename='img/graf'+str(time.time())+'.png'
    plt.savefig(filename,pad_inches=10)

def printer1(data):
    lol=0.999865903
    interval = np.arange(0, 1000000, 1)
    z_values = [ (lol/value+1-lol)**(-1) for value in interval]
    #print(z_values)
    plt.rcParams.update({'font.size': 30})
    x_values = [ 2**i for i in range(len(data))]
    print(x_values)
    y_values = [(str)(10000*(1-data[i]/data[0])//1/100)+'%' for i in range(len(data))]
    print(y_values)
    plt.figure(figsize = (25, 15))
    plt.grid()
    #plt.plot(x_values, y_values,marker="o")
    plt.plot(interval,z_values)
    #plt.addlabels(x_values, y_values)
    plt.title('Эффективность')
    plt.xlabel('Число потоков')
    plt.ylabel('Сокращение времени обработки')
    #plt.tick_params(axis='x', rotation=90)
    #plt.xticks(range(1,17))
    #plt.yticks(range(6))
    timeSt=time.time()
    filename='graf'+str(time.time())+'.png'
    plt.show()
    #plt.savefig(filename,pad_inches=10)

#videos=getVideosName('Tests/1')
#print(videos)
#video_analizator('videos/Tests/1/1 (1).webm',getVideosDuration(videos),1)

'''
tthr=2
print('------1------')
videos=getVideosName("Tests/32")
ar=[]
threads = []
for i in range(1000):
    #arr=divederByDuration(getVideosDuration(videos), tthr)
    #videos=getVideosName("Tests/32")
    timeSt=(time.time()*1000000000)
    a=getVideosDuration(videos)
    arr=divederByDuration(getVideosDuration(getVideosName("Tests/32")), tthr)

    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()

    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[999])
print(ar[998])
print(ar[997])

ar=[1616.562768,
1387.551317,
1168.416616,
890.1355238,
740.0951783]
printer1(ar)

print('------5------')
videos=getVideosName("Tests/5")
ar=[]
threads = []
for j in range(3):
    arr=divederByDuration(getVideosDuration(videos), tthr)
    timeSt=(time.time()*1000000000)
    #getVideosDuration(videos)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[2])
print(ar[1])
print(ar[0])
#exit()
print('------10------')
videos=getVideosName("Tests/10")
ar=[]
threads = []
for j in range(3):
    arr=divederByDuration(getVideosDuration(videos), tthr)
    timeSt=(time.time()*1000000000)
    #getVideosDuration(videos)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[2])
print(ar[1])
print(ar[0])
print('------20------')
videos=getVideosName("Tests/20")
ar=[]
threads = []
for j in range(3):
    arr=divederByDuration(getVideosDuration(videos), tthr)
    timeSt=(time.time()*1000000000)
    #getVideosDuration(videos)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[2])
print(ar[1])
print(ar[0])
print('------50------')
videos=getVideosName("Tests/50")
ar=[]
threads = []
for j in range(3):
    arr=divederByDuration(getVideosDuration(videos), tthr)
    timeSt=(time.time()*1000000000)
    #getVideosDuration(videos)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[2])
print(ar[1])
print(ar[0])
print('------100------')
videos=getVideosName("Tests/100")
ar=[]
threads = []
for j in range(3):
    arr=divederByDuration(getVideosDuration(videos), tthr)
    timeSt=(time.time()*1000000000)
    #getVideosDuration(videos)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[2])
print(ar[1])
print(ar[0])
print('------1000------')
videos=getVideosName("Tests/1000")
ar=[]
threads = []
for j in range(3):
    arr=divide_almost_equally(getVideosDuration(videos), tthr)
    timeSt=(time.time()*1000000000)
    #getVideosDuration(videos)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        threads.append(T)
        thrNumber+=1
    for x in threads:
        x.join()
    ar.append((time.time()*1000000000-timeSt)/1000000000)
#print(videos)
ar.sort()
print(ar[2])
print(ar[1])
print(ar[0])
print('------end------')
#toAnalize(videos,THREADS)
#printer(arrray)
'''