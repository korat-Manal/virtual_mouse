import cv2
import numpy as np
import handtracking as htm
import time
import autopy
import tkinter as tk

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################

def start_tracking():
    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = htm.handDetector(maxHands=1)
    wScr, hScr = autopy.screen.size()

    while True:
        # 1.Find the hand landmarks
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        # 2. get the tip of the index middle finger
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            x3, y3 = lmList[4][1:]
            x4, y4 = lmList[16][1:]
            x5, y5 = lmList[20][1:]
            # 3.check which fingers are up
            fingers = detector.fingersUp()
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
            # 4.only index finger:Moving mode
            if fingers[1] == 1 and fingers[2] == 0:
                # 5.convert Coordinates
                x6 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y6 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                # 6.smoothen values
                clocX = plocX + (x6 - plocX) / smoothening
                clocY = plocY + (y6 - plocY) / smoothening
                # 7.Move mouse
                autopy.mouse.move(wScr - clocX, clocY)
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

            # 8.both index and middle fingers are up:clicking mode
            if fingers[1] == 1 and fingers[2] == 1:
                # 9.find distance between fingers
                length, img, lineInfo = detector.findDistance(8, 12, img)
                # 10.click mouse if distance short
                if length < 30:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click()
            elif fingers[1] == 1 and fingers[0] == 1:
                # 9.find distance between fingers
                length, img, lineInfo = detector.findDistance(4, 8, img)
                if length < 30:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)
            elif fingers[1] == 1 and fingers[4] == 1:
                length, img, lineInfo = detector.findDistance(8, 20, img)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)

            # 11.frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        # 12.display
        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord('q'):
            break


# Create Tkinter window
root = tk.Tk()
root.title("Hand Tracking")
root.geometry("300x200")


# Function to start tracking when the button is clicked
start_button = tk.Button(root, text="Start Tracking", fg="white", bg='green', font='Helvetica 12 bold italic ',
                         command=start_tracking)
start_button.pack()

root.mainloop()
