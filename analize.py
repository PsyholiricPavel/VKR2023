# import the necessary packages
import numpy as np
import cv2
import threading
import time
import heapq
import os

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

def divide_almost_equally(arr, num_chunks):
    arr.sort(key=lambda x: x[0],reverse=True) #= sorted(arr, reverse=True)
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
    # initialize the HOG descriptor/person detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    cv2.startWindowThread()
    detections=0
    # open video stream
    cap = cv2.VideoCapture(videoName)
    ret, frame = cap.read()
        # if frame is read correctly ret is True
    if not ret:
            print("[Thread{0}]".format(thrNumber),"Can't receive frame of "+videoName+" Exiting")
            exit()
        # Our operations on the frame come here
    i+=1
    print("[Thread{0}]".format(thrNumber),videoName,'analyse started video duration is',duration)
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("[Thread{0}]".format(thrNumber),videoName,"analysed sucsefull.",i,"frames.","Time:",time.time()-timeSt,"Detections:",detections)
            return detections
        i+=1
        # resizing for faster detection
        frame = cv2.resize(frame, (640, 480))
        # using a greyscale picture, also for faster detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # detect people in the image
        # returns the bounding boxes for the detected objects
        boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )
        #print(len(boxes),i)
        detections+=len(boxes)
        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

        for (xA, yA, xB, yB) in boxes:
            # display the detected boxes in the colour picture
            cv2.rectangle(frame, (xA, yA), (xB, yB),
                            (0, 255, 0), 2)
        
        #cv2.imshow("Frame", frame)
        #if cv2.waitKey(5) & 0xFF == ord('q'):
        #    break
    # When everything done, release the capture
    cap.release()
    # and release the output
    #out.release()
    # finally, close the window
    cv2.destroyAllWindows()
def lineAnalyse(thrNumber,videosNames):
    for i in videosNames:
        video_analizator(i[0], i[1],thrNumber)

def toAnalize(files,thrs):
    if len(files)<thrs:
        thrs=len(files)
    print(thrs)
    arr=divederByDuration(getVideosDuration(files), thrs)
    print(arr)
    thrNumber=0
    for i in arr:
        #print(([i],thrNumber))
        T = threading.Thread( target =lineAnalyse, args =(thrNumber,i)) 
        T.start()
        thrNumber+=1


  
#for i in range(100):
#    video_analizator("1.webm",i)
#video_analizator("videos/1/1.webm",1,time.time())
#video_analizator("1.webm",2)
#2043 2970
#['3.webm', '1.webm', '1.webm', '3.webm', '3.webm', '1.webm', '1.webm', '1.webm', '3.webm', '3.webm', '1.webm', '1.webm', '3.webm', '3.webm', '1.webm', '3.webm', '1.webm', '3.webm', '1.webm', '1.webm', '1.webm', '1.webm', '1.webm', '1.webm', '3.webm', '1.webm', '1.webm', '3.webm', '1.webm', '3.webm', '1.webm', '1.webm', '3.webm', '3.webm', '3.webm', '3.webm', '3.webm', '1.webm', '1.webm', '3.webm', '1.webm', '1.webm', '1.webm', '1.webm', '3.webm', '1.webm', '3.webm', '3.webm', '1.webm', '3.webm', '3.webm', '3.webm', '1.webm', '1.webm', '3.webm', '3.webm', '3.webm', '1.webm', '1.webm', '3.webm', '3.webm', '3.webm', '1.webm', '3.webm', '3.webm', '1.webm', '1.webm', '1.webm', '1.webm', '3.webm', '1.webm', '3.webm', '3.webm', '3.webm', '1.webm', '1.webm', '1.webm', '3.webm', '3.webm', '3.webm', '1.webm', '1.webm', '1.webm', '1.webm', '3.webm', '3.webm', '3.webm', '1.webm', '1.webm', '3.webm', '3.webm', '1.webm', '1.webm', '1.webm', '3.webm', '1.webm', '1.webm', '3.webm', '1.webm', '1.webm']