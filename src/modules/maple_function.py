import keyboard
import time 
import win32gui , win32con ,win32api ,win32ui
from ctypes import windll
from PIL import Image, ImageQt
import numpy as np
import cv2
import ctypes
from random import random
import os

pic_path = os.path.join(os.path.dirname(os.path.abspath("main.py")), "assets")

class maple_function():
#---------------------------------------------------------------------------        
        
    MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA
    #放指定技能 跟延遲
    def skillbuff_fun(key):
        time.sleep(0.1)
        keyboard.send(str(key))


#---------------------------------------------------------------------------
    #擷取楓谷畫面 
    def get_game_pic():
        #擷取楓谷畫面 
        try:
            hwnd = win32gui.FindWindow(None,'MapleStory')
            # hwnd = get_jb_id()
            # 如果使用高 DPI 显示器（或 > 100% 缩放尺寸），添加下面一行，否则注释掉
            windll.user32.SetProcessDPIAware()

            # Change the line below depending on whether you want the whole window
            # or just the client area.
            # 根据您是想要整个窗口还是只需要 client area 来更改下面的行。
            left, top, right, bot = win32gui.GetClientRect(hwnd)
            # left, top, right, bot = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bot - top

            hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
            saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC

            saveBitMap = win32ui.CreateBitmap()  # 创建bitmap准备保存图片
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间

            saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap中

            # 选择合适的 window number，如0，1，2，3，直到截图从黑色变为正常画面
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if result == 1:
                # PrintWindow Succeeded
                qimage = ImageQt.ImageQt(im)
                return qimage  # 返回图片
            else:
                print("獲取遊戲圖片失敗")
        except Exception as e:  
            print (e)  
            print('抓取遊戲畫面失敗')    
#---------------------------------------------------------------------------
      #楓之谷視窗移到最上層
    def gametop():
        try:
            hwnd = win32gui.FindWindow(None,'MapleStory')
            time.sleep(0.5)
                #楓之谷視窗    # 若最小化，则将其显示
            if win32gui.IsIconic(hwnd):
                time.sleep(0.2)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
                time.sleep(0.2)
            
                win32gui.SetForegroundWindow(hwnd)
            else:
                time.sleep(0.2)
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
                time.sleep(0.2)

                win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            print(e)            
#---------------------------------------------------------------------------            
    #img檔 轉cv2 圖檔 為了使用get_1()
    def qimgtocv2(qimg=get_game_pic()):
        try:
            # qimg=(maple_function.get_game_pic(hwnd))
            temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
            temp_shape += (4,)
            ptr = qimg.bits()
            ptr.setsize(qimg.byteCount())
            result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
            result = result[..., :3]

            return result
        except Exception as e:  
            print (e)  
            print('抓取遊戲畫面失敗')  
#---------------------------------------------------------------------------            
  
    #遊戲視窗起始位置
    def getGame_X_Y():
        hwnd = win32gui.FindWindow(None,'MapleStory')
        # hwnd =await get_jb_id()
        x1,y1,x2,y2 = win32gui.GetWindowRect(hwnd)

        #x軸+3  軸+26 去除標題的位移
        return x1+3,y1+26,x2,y2
#---------------------------------------------------------------------------            
    #滑鼠左鍵點擊
    # def mouseclick(x,y):
    #     win32api.SetCursorPos((x+( getGame_X_Y())[0], y+( getGame_X_Y())[1]))
    #     time.sleep(0.05)
    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    #     win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0) 
#---------------------------------------------------------------------------            
    #比較圖片(遊戲,尋找的圖)
    def get_1(pic,pic2):
        img_rgb = pic  

        time.sleep(0.1)

        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)


        pic1 = cv2.imread(pic2,0)
        w, h = pic1.shape[::-1]


        res = cv2.matchTemplate(img_gray,pic1,cv2.TM_CCOEFF_NORMED)

        threshold = 0.85

        loc = np.where(res >= threshold)
        x=loc[1]
        y=loc[0]

        if len(x) and len(y):
            return True
        else :
            return False               
#---------------------------------------------------------------------------            
    MapVirtualKey = ctypes.windll.user32.MapVirtualKeyA
    #底層按鍵方法(上下左右) #keydownup(KEY_MAP.get('left'),sec) 
    def keydownup(key,sec):
        #按下
        win32api.keybd_event(key, maple_function.MapVirtualKey(key, 0), 0, 0)
        #持續時間
        time.sleep(sec)
        #彈起
        win32api.keybd_event(key, maple_function.MapVirtualKey(key, 0), win32con.KEYEVENTF_KEYUP, 0)
#---------------------------------------------------------------------------            
    #按鍵延遲
    def keytimedelay(sec):
        time.sleep(sec)
#---------------------------------------------------------------------------            
    #下跳       
    def dumpjump(jumpkey):
        #按下 下
        win32api.keybd_event(0x28, maple_function.MapVirtualKey(0x28, 0), 0, 0)
        #持續時間
        sec = 0.07 +(random()/25)
        time.sleep(sec)
        #按下 跳
        win32api.keybd_event(jumpkey, maple_function.MapVirtualKey(0x44, 0), 0, 0)
        
        #持續時間
        sec = 0.1 +(random()/40)
        time.sleep(sec)
        #彈起 跳
        win32api.keybd_event(jumpkey, maple_function.MapVirtualKey(0x44, 0), win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(sec)
        #彈起 下
        win32api.keybd_event(0x28, maple_function.MapVirtualKey(0x28, 0), win32con.KEYEVENTF_KEYUP, 0)
#---------------------------------------------------------------------------            
    #連接動作       
    def connect_actions(key1,key2):
        #按下 下
        win32api.keybd_event(key1, maple_function.MapVirtualKey(0x28, 0), 0, 0)
        #持續時間
        sec = 0.07 +(random()/25)
        time.sleep(sec)
        #按下 跳
        win32api.keybd_event(key2, maple_function.MapVirtualKey(0x44, 0), 0, 0)
        
        #持續時間
        sec = 0.1 +(random()/40)
        time.sleep(sec)
        #彈起 跳
        win32api.keybd_event(key2, maple_function.MapVirtualKey(0x44, 0), win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(sec)
        #彈起 下
        win32api.keybd_event(key1, maple_function.MapVirtualKey(0x28, 0), win32con.KEYEVENTF_KEYUP, 0)        
#--------------------------------------------------------------------------- 
    #獲取角色位置xy      
    def get_player_xy(img_rgb=qimgtocv2()):
        try:
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

            template = cv2.imread(os.path.join(pic_path,'player2_template.png'),0)

            res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)

            threshold = 0.85

            loc = np.where(res >= threshold)
            x=loc[1]
            y=loc[0]

            if len(x) and len(y):
                return (int(x),int(y))
            else:
                return None    
        except Exception as e:
            print('找不到人物黃點')
            print(e)
#---------------------------------------------------------------------------      
    #獲取地圖輪的位置  
    def get_rune_xy(img_rgb=qimgtocv2()):

        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        template = cv2.imread(os.path.join(pic_path,'rune_template.png'),0)

        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)

        threshold = 0.85

        loc = np.where(res >= threshold)
        x=loc[1]
        y=loc[0]

        if len(x) and len(y):
            return (int(x),int(y))
        else:
            return None 
#---------------------------------------------------------------------------            
#---------------------------------------------------------------------------            
 
            










    #---------------------------------------------------------------------------            
    #按鍵碼
    KEY_MAP = {
        'left': 0x25,   # Arrow keys
        'up': 0x26,
        'right': 0x27,
        'down': 0x28,

        'backspace': 0x08,      # Special keys
        'tab': 0x09,
        'enter': 0x0D,
        'shift': 0x10,
        'ctrl': 0x11,
        'alt': 0x12,
        'caps lock': 0x14,
        'esc': 0x1B,
        'space': 0x20,
        'page up': 0x21,
        'page down': 0x22,
        'end': 0x23,
        'home': 0x24,
        'insert': 0x2D,
        'delete': 0x2E,

        '0': 0x30,      # Numbers
        '1': 0x31,
        '2': 0x32,
        '3': 0x33,
        '4': 0x34,
        '5': 0x35,
        '6': 0x36,
        '7': 0x37,
        '8': 0x38,
        '9': 0x39,

        'a': 0x41,      # Letters
        'b': 0x42,
        'c': 0x43,
        'd': 0x44,
        'e': 0x45,
        'f': 0x46,
        'g': 0x47,
        'h': 0x48,
        'i': 0x49,
        'j': 0x4A,
        'k': 0x4B,
        'l': 0x4C,
        'm': 0x4D,
        'n': 0x4E,
        'o': 0x4F,
        'p': 0x50,
        'q': 0x51,
        'r': 0x52,
        's': 0x53,
        't': 0x54,
        'u': 0x55,
        'v': 0x56,
        'w': 0x57,
        'x': 0x58,
        'y': 0x59,
        'z': 0x5A,

        'f1': 0x70,     # Functional keys
        'f2': 0x71,
        'f3': 0x72,
        'f4': 0x73,
        'f5': 0x74,
        'f6': 0x75,
        'f7': 0x76,
        'f8': 0x77,
        'f9': 0x78,
        'f10': 0x79,
        'f11': 0x7A,
        'f12': 0x7B,
        'num lock': 0x90,
        'scroll lock': 0x91,

        ';': 0xBA,      # Special characters
        '=': 0xBB,
        ',': 0xBC,
        '-': 0xBD,
        '.': 0xBE,
        '/': 0xBF,
        '`': 0xC0,
        '[': 0xDB,
        '\\': 0xDC,
        ']': 0xDD,
        "'": 0xDE
    }