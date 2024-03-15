from flask import Flask, make_response, Response, request
from ultralytics import YOLO
import json, os, cv2, requests, time
from dotenv import load_dotenv
import numpy as np
import search, ocr
from PIL import Image
# import time
from datetime import datetime
import io, base64
from PIL import Image

load_dotenv('.env')

app = Flask(__name__)  
model = YOLO("best.pt")

@app.route('/', methods=['GET'])
def pred():
    plate = request.args.get('plt')
    loc = request.args.get('loc')
    timee = request.args.get('time')
    start_time, stop_time = timee, timee
    start_time = timee[:13] + str(int(timee[13:15])-1) + ':00'
    stop_time = timee[:13] + str(int(timee[13:15])+1) + ':59'
    start_time = datetime.strptime(start_time,r"%d/%m/%Y%H:%M:%S")
    stop_time = datetime.strptime(stop_time,r"%d/%m/%Y%H:%M:%S")
    print(start_time,stop_time)
    inc = request.args.get('inc')

    msgs = []
    found = False
    global limits
    global limits_old

    if int(inc) == 0:
        print('assinging fresh limits')
        limits = [1,1,1,1]
        limits_old = [-1,-1,-1,-1]
    # else:                              #remove b4 deployment
    #     limits = [1,1,1,1]
    #     limits_old = [-1,-1,-1,-1]

    # Find location of camera
    top, right, bottom, left, limits = search.cams(int(loc), int(inc), limits)
    print('search for cam results = ', top, right, bottom, left, limits)
    # Check limits & add msgs if any
    if limits == [0,0,0,0]:
        limits_old = limits
        msgs.append('Full map checked\n')
    else:
        if limits[0] == 0 and limits_old[0]:
            msgs.append('Top of map reached\n')
        if limits[1] == 0 and limits_old[1]:
            msgs.append('Right of map reached\n')
        if limits[2] == 0 and limits_old[2]:
            msgs.append('Bottom of map reached\n')
        if limits[3] == 0 and limits_old[3]:
            msgs.append('Left of map reached\n')
        limits_old = limits

        # Narrow results to cams to check
        cams_to_check = np.concatenate((top, right, bottom, left))
        cams_to_check = np.delete(cams_to_check, np.where(cams_to_check == 0))
        print('cams to check = ', cams_to_check)
        if cams_to_check.size > 0:

            # Loop through surrounding cams, otherwise say no cams
            cam_results = {}
            for i in cams_to_check:
                # Ask server with time (correctly formatted)
                url = 'http://10.5.11.123:5000/?'
                argss = f'cam={i}&start_time={start_time.strftime("%Y%m%d%H%M%S")}&end_time={stop_time.strftime("%Y%m%d%H%M%S")}'
                print('args', argss)
                footage = requests.get(url+argss)
                print(f'Footage for camera {i} recieved')
                footage = json.loads(footage.text)
                imgs = footage['frames']
                names = footage['names']

                for x in range(0, len(names)):
                    pic = imgs[x]
                    name = names[x]

                    # Format img
                    img = Image.open(io.BytesIO(base64.decodebytes(bytes(pic))))
                    img.save('img.jpg')
                    print('Image saved')

                    # Run through custom model 
                    results = model('img.jpg')
                    print(f'Processed by model')
                    if len(results) > 0: # Check if there are any predictions
                        for result in results:
                            result = result.cpu().boxes.numpy()
                            if len(result.cls) > 0:  # If detected
                                # print(result)
                                [x1,y1,x2,y2] = result.xyxy[0]
                                og_shape = result.orig_shape

                                #Cropping to send to API for OCR
                                img = cv2.imread('img.jpeg')
                                cropped_image = img[int(y1):int(y2), int(x1):int(x2)]    # Crop the image to the rectangle
                                cv2.imwrite("cropped.jpeg", cropped_image)    # Save in    
                                print('cropped version saved')   

                                # Use API to read plate
                                # plates = ocr.detect()
                                plates = requests.get(f'http://10.5.11.123:5000/ocr?img={pic}')
                                print(plates)
                                # Check if any of the results plates match reqd plate
                                for j in plates:
                                    if plate in j:
                                        found = True
                                        msgs.append(f'Target found in camera {i} at {name}: \n')
                                        msgs.append(pic)
                            if found:
                                break
                    if found:
                        break
                if found:
                    break
        else:
            msgs.append('No nearby cameras found\n')

    # Send result
    # Create a JSON response and set custom header
    d = {'msgs': msgs}
    response = json.dumps(d)
    response = Response(response, status=200, content_type='application/json')
    response.headers['X-My-Header'] = 'foo'
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
    # print(model.names)

# results = model(r'C:\Users\anush\Projects\Emirates_Robotics\venv\data\test\trash.mp4', show=True)
