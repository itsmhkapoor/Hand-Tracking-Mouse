import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
 
wCam, hCam = 640, 480
frameR = 100 # Frame Reduction to avoid incorrect detection of hands at camera edges
smoothening = 7

 
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
 
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
 
while True:
    # Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    
    # Get the tip of the index finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:] # tip of index finger
    
    # Check which fingers are up
    fingers = detector.fingersUp()
    
    # Draw finger movement box
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
    
    # Only Index Finger : Moving Mode
    if fingers[1] == 1 and fingers[2] == 0:
        # Convert Coordinates to screen coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        # Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening # Smoothening mouse movement can also be done by autopy.mouse.smooth_move
        clocY = plocY + (y3 - plocY) / smoothening
        # Move Mouse
        autopy.mouse.move(wScr - clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY
        
    # Both Index and middle fingers are up : Clicking Mode
    if fingers[1] == 1 and fingers[2] == 1:
        # Find distance between fingers
        length, img, lineInfo = detector.findDistance(8, 12, img)
        # Click is distance is short
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
            15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()
    
    # For displaying Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
