# -*- coding: utf-8 -*-
'''
-----------------
BitmapFont Server 
-----------------

Created on Mon Apr  4 19:44:19 2022

@author: ghosty
'''
import cv2
import numpy as np
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from PIL import ImageFont, ImageDraw, Image
import threading
import time

hostName = 'localhost'
serverPort = 8080

isServerRunning = False

def showBitmap():
    print('*** showBitmap()')
    global img, webServer
    while (isServerRunning):          
        if (img.shape[0]>0 and img.shape[1]>0):
            cv2.imshow('Bitmap',img)
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q') or key==27: 
                break
        else:
            break
        time.sleep(0.1)   
    cv2.destroyAllWindows()
    print('*** stop showBitmap()')    
    webServer.shutdown()
    
def getTextWidth(text):
    width = 0
    for _char in text:
        if not '\u4e00' <= _char <= '\u9fa5':
            width += 1
        else:
            width += 2
    return width

class MyServer(BaseHTTPRequestHandler):
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('<html><head><title>Bitmap Font Server</title></head>', 'utf-8'))
        self.wfile.write(bytes('<font face="monospace">', 'utf-8'))
        #print('*** path=',self.path)
        query = parse.urlparse(self.path).query
        if (len(query)==0):
            print('*** No query')
            return
        try:
            print('*** query=',query)
            query_components = dict(qc.split('=') for qc in query.split('&'))
            print('*** query_components=',query_components)
        except:
            return    
        
        #font
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        #size
        try:
            size = int(query_components['size'])
        except:
            size = 16   
        print('*** size=',size)
        #text
        try:
            text = query_components['text']
            print('*** text=',text)           
        except:
            print('*** No text')
            text = ''
        text = parse.unquote(text) 
        # show bitmap
        global img
        if len(text)>0:            
            #
            height = size
            width = (int)(getTextWidth(text)*size/2)            
            self.wfile.write(bytes('%d,%d<br>'%(width,height), 'utf-8'))
            print('*** height=',height,', width=',width)
            img = np.zeros((height,width,3), np.uint8)
                
            ## Use simsum.ttc to write Chinese.
            fontpath = './mingliu.ttc' #"simsun.ttc"     
            font = ImageFont.truetype(fontpath, size)
            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((0, 0),  text, font = font, fill = (255, 255, 255, 255))
            img = np.array(img_pil)    

            for y in range(height):
                for x in range(width):          
                    if (img[y][x][0]>0):
                        #bit=1
                        bit='<font color="red">1</font>'
                    else: 
                        #bit=0
                        bit='0'
                    #self.wfile.write(bytes('%d' % bit, 'utf-8'))
                    self.wfile.write(bytes('%s' % bit, 'utf-8'))
                self.wfile.write(bytes('<br>', 'utf-8')) #end of line
                
        #end of body        
        self.wfile.write(bytes('</font>', 'utf-8'))
        self.wfile.write(bytes('<body>', 'utf-8'))
        self.wfile.write(bytes('</body></html>', 'utf-8'))

if __name__ == '__main__':     
    # show bitmap    
    img = np.zeros((16,16,3), np.uint8)
    t = threading.Thread(target = showBitmap)
    isServerRunning = True
    t.start()
    
    # start web server
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print('Server started http://%s:%s' % (hostName, serverPort))
    try:
        print('*** server is running')
        webServer.serve_forever(1) #check running state every 1 second
            
    except KeyboardInterrupt:
        pass

    isServerRunning = False
    webServer.server_close()
    print('*** Server is stopped.')   
    
    