
import win32gui
import configparser
from PyQt5 import  QtWidgets
from src.gui.window import Ui_MainWindow
import time
import threading
from src.modules.maple_function import maple_function as mf
from src.modules.modelfun import modelfun
from datetime import datetime
from PyQt5.QtCore import pyqtSignal
import pygame
from random import random
import os

import numpy as np

assets_path = os.path.join(os.path.dirname(os.path.abspath("main.py")), "assets")

class ui_setting_fun(QtWidgets.QMainWindow,Ui_MainWindow):


    #模型變數
    model = None
    #創建信號槽
    signal1_log_npc_xy = pyqtSignal(str)
    signal2_log_key = pyqtSignal(str)
    signal3_log_attack = pyqtSignal(str)
    signal4_log_error = pyqtSignal(str)

    
    #取得畫面
    gamepic = mf.qimgtocv2()    
    #按鍵設定
    jumpkey = None
    attackkey = None
    ropekey = None
    #角色轉向地圖邊界
    goright_x_num = None
    goleft_x_num = None

    #預設 上下左右鍵 無法改
    upkey= mf.KEY_MAP.get('up')
    downkey= mf.KEY_MAP.get('down')
    leftkey= mf.KEY_MAP.get('left')
    rightkey= mf.KEY_MAP.get('right')

    #線程 暫停/停止
    skillstopevent = threading.Event()
    skillstopevent.set()
    attackstopevent = threading.Event()
    attackstopevent.set()
    #線程鎖 防止同時使用技能    lock.acquire()鎖住    lock.release() 釋放

    lock = threading.Lock()

    # def __init__(self, gamepic):
    #     self.gamepic = gamepic
    def __init__(self,parent=None):
        super(ui_setting_fun, self).__init__(parent) # 調用父類把子類對象轉為父類對象

        self.setupUi(self)

        #連接log信號槽
        self.signal1_log_npc_xy.connect(self.log_npc_xy)
        self.signal2_log_key.connect(self.log_key)
        self.signal3_log_attack.connect(self.log_attack)
        self.signal4_log_error.connect(self.log_error)
        #預設>改成讀外部檔案
               
#-------------------------------------------------------------------------------------
        #尋找楓谷視窗按鈕
        self.pushButton.clicked.connect(self.getMapleStory_hwnd)
        
        #按下開始練等按鈕
        self.pushButton_2.clicked.connect(self.attackbtn)
        #啟動技能/buff 按鈕
        self.pushButton_3.clicked.connect(self.skillbtn)
        #測試自製script用
        self.pushButton_4.clicked.connect(lambda: self.self_script_functon(actiontext=self.lineEdit_25.text()))
        #關閉警報音樂
        self.pushButton_5.clicked.connect(self.closemp3)  
        #重新載入設定檔
        self.pushButton_6.clicked.connect(self.load_ini_file)              
        #儲存設定檔
        self.pushButton_7.clicked.connect(self.save_ini_file)         
        #開啟設定檔路徑
        self.pushButton_8.clicked.connect(self.openfilepath)
        #清除所有設定
        self.pushButton_9.clicked.connect(self.clearall)


#------多線程-----------多線程---------------多線程---------------多線程------------------多線程--------------------
        #技能BUFF
        skillbtn = [self.checkBox,self.checkBox_2,self.checkBox_3,self.checkBox_4,self.checkBox_5,self.checkBox_6,self.checkBox_7,self.checkBox_8,self.checkBox_9,self.checkBox_10]
        skilkey = [self.lineEdit,self.lineEdit_3,self.lineEdit_5,self.lineEdit_7,self.lineEdit_9,self.lineEdit_11,self.lineEdit_13,self.lineEdit_15,self.lineEdit_17,self.lineEdit_19]
        skilltimelong = [self.lineEdit_2,self.lineEdit_4,self.lineEdit_6,self.lineEdit_8,self.lineEdit_10,self.lineEdit_12,self.lineEdit_14,self.lineEdit_16,self.lineEdit_18,self.lineEdit_20]
        skilllist = ["thread_skill1","thread_skill2","thread_skill3","thread_skill4","thread_skill5","thread_skill6","thread_skill7","thread_skill8","thread_skill9","thread_skill10"]       
        for i in range(0,10):
            
            skilllist[i] = threading.Thread(target=self.skill,args=(skillbtn[i],skilkey[i],skilltimelong[i]))
            skilllist[i].daemon = True 
            skilllist[i].start()

        #監聽測謊
        listen_polygraph_thread = threading.Thread(target=self.listen_polygraph)
        listen_polygraph_thread.daemon = True 
        listen_polygraph_thread.start()
        #練等
        attack_thread = threading.Thread(target=self.attack_right)
        attack_thread.daemon = True 
        attack_thread.start()
        #監測遊戲畫面 ,判斷角色位置
        listen_player_xy_thread = threading.Thread(target=self.listen_player_xy)
        listen_player_xy_thread.daemon = True 
        listen_player_xy_thread.start()
        # #判斷角色位置  與上述結合
        # gamepic_thread = threading.Thread(target=self.listen_player_xy)
        # gamepic_thread.daemon = True 
        # gamepic_thread.start() 
        #監測遊戲畫面 ,地圖輪
        listen_rune_xy_thread = threading.Thread(target=self.listen_rune_xy)
        listen_rune_xy_thread.daemon = True 
        listen_rune_xy_thread.start()
        #載入模型
        
        load_moudles_thead_thread = threading.Thread(target=self.load_moudles_thead)
        load_moudles_thead_thread.daemon = True 
        load_moudles_thead_thread.start()
        #載入ini檔
        load_ini_file_thread = threading.Thread(target=self.load_ini_file)
        load_ini_file_thread.daemon = True 
        load_ini_file_thread.start()
        
#------多線程-----------多線程---------------多線程---------------多線程------------------多線程--------------------


#-------------------------------------------------------------------------------------
    #尋找楓谷視窗按鈕
    def getMapleStory_hwnd(self):
        try:
            '''
            根据标题找句柄
            :param title: 标题
            :return:返回句柄所对应的ID
            '''
            title='MapleStory'
            jh = []
            hwnd_title = dict()

            def get_all_hwnd(hwnd, mouse):
                if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                    hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

            win32gui.EnumWindows(get_all_hwnd, 0)
            for h, t in hwnd_title.items():
                if t != "":
                    if title in t:
                        jh.append(h)

            if len(jh) == 0:
                self.lineEdit_21.setText('找不到楓之谷')
                self.signal4_log_error.emit('找不到楓之谷視窗')
            else:
                self.lineEdit_21.setText(str(jh[0]))
                self.signal2_log_key.emit('已獲取楓之谷句柄')
                
        except:
            self.lineEdit_21.setText('找楓之谷發生錯誤')
            self.signal4_log_error.emit('找楓之谷發生錯誤')
#-------------------------------------------------------------------------------------
    #放技能 or BUFF
    def skill(self,btn,key,timelong):

            while True:
                try:
                    if btn.isChecked() and not self.skillstopevent.is_set() and not self.attackstopevent.is_set() :
                        self.lock.acquire()
                        time.sleep(0.5)
                        self.signal2_log_key.emit('按鍵 '+str(key.text())+' 延遲'+str(timelong.text())+'秒')
                        # self.log('按鍵 '+str(key.text())+' 延遲'+str(timelong.text())+'秒')
                        #鎖
                        
                        #按 按鍵
                        mf.skillbuff_fun(key.text())
                        time.sleep(0.5)
                        #解鎖
                        self.lock.release()
                        time.sleep(int(timelong.text()))
                except Exception as e:
                    print(e)
                    print('skill function 有問題')
                    self.signal4_log_error.emit('skill function 有問題')                
                time.sleep(1)


#-------------------------------------------------------------------------------------
    #gui記錄區 紀錄
    def log_key(self,text):
        self.textEdit.append(str(text)+'  '+datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'))
    def log_attack(self,text):    
        self.textEdit_2.append(str(text)+'  '+datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'))
    def log_npc_xy(self,text):    
        self.textEdit_5.append(str(text)+'  '+datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'))        
    def log_error(self,text):    
        self.textEdit_6.append(str(text)+'  '+datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'))  

#-------------------------------------------------------------------------------------
    #監測測謊 提醒
    def listen_polygraph(self):
        # global gamepic
        
            while True:
                try:
                    if self.checkBox_11.isChecked():

                        if mf.get_1(self.gamepic,assets_path+"/1.jpg") == True or mf.get_1(self.gamepic,assets_path+"/2.jpg") == True or mf.get_1(self.gamepic,assets_path+"/npctest.jpg") == True or mf.get_1(self.gamepic,assets_path+"/ohmygod.png") == True:
                            if not self.attackstopevent.is_set():
                                self.skillstopevent.set()
                                self.label_44.setText('被測謊已暫停打怪')
                            pygame.init()
                            pygame.mixer.music.load(assets_path+"/dangerw.mp3")
                            pygame.mixer.music.play()
                            time.sleep(60)
                except Exception as e:
                    print(e)
                    print('監聽測謊有問題')
                    self.signal4_log_error.emit('監聽測謊有問題')

                time.sleep(1.5)

#-------------------------------------------------------------------------------------
    def closemp3(self):
        pygame.init()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.load(assets_path+"/dangerw.mp3")       
            pygame.mixer.music.play()
#-------------------------------------------------------------------------------------
    #監測地圖輪 提醒
    def listen_rune_xy(self):
            while True:
                try:
                    time.sleep(1)
                    if self.checkBox_12.isChecked():

                        rune_xy = mf.get_rune_xy(self.gamepic)

                        if rune_xy == None:
                            rune_xy = '目前地圖上沒有輪'
                        else:
                            pygame.init()
                            pygame.mixer.music.load(assets_path+"/rune.mp3")
                            pygame.mixer.music.play()
                            self.signal2_log_key.emit('地圖輪已出現 ,自動停止練功 等待解輪 解輪後自行開始練功') 
                            rune_x = rune_xy[0]    
                            rune_y = rune_xy[1]        
                            
                            if not self.attackstopevent.is_set():
                                self.attackstopevent.set()
                                self.label_44.setText('已暫停打怪')
                                if self.checkBox_13.isChecked():
                                    
                                    self.signal2_log_key.emit('開始解地圖輪') 
                                    self.lock.acquire()
                                    self.runekeyfunction()
                                    self.lock.release()
                                    self.signal2_log_key.emit('解地圖輪完畢(失敗也會顯示)') 
                                    time.sleep(1)
                                    self.attackstopevent.clear()
                                    self.label_44.setText('攻擊中')
                                    time.sleep(540)
                    time.sleep(60)
                except Exception as e:
                    print(e)
                    print('監聽地圖輪有問題')
                    self.signal4_log_error.emit('監聽地圖輪有問題')
                            

                time.sleep(10)

#-------------------------------------------------------------------------------------
    #監測遊戲畫面 角色位置
    def listen_player_xy(self):
        i = 0

        while True:   
            try:
                time.sleep(0.7)

                gamepic_image = mf.get_game_pic()
                self.gamepic = mf.qimgtocv2(gamepic_image)
                try:
                    player_xy = mf.get_player_xy(self.gamepic)
                except:
                    print('角色位置貼牆了')
                    self.signal1_log_npc_xy.emit('角色位置可能貼牆了,請手動移動一下')

                if player_xy == None:
                    player_xy = '找不到角色位置'
                    self.signal1_log_npc_xy.emit(player_xy)
                else:
                    player_x = player_xy[0]
                    player_y = player_xy[1]
                    self.signal1_log_npc_xy.emit('人物位置 : (x:'+str(player_x)+', y:'+str(player_y)+')')

                if not self.attackstopevent.is_set() and self.checkBox_14.isChecked() :
                    #判斷人物位置 調整左右方向
                    if player_x <self.goright_x_num:
                        self.lock.acquire()
                        self.goright()
                        self.lock.release()
                        time.sleep(0.2)
                    elif player_x >self.goleft_x_num:  

                        self.lock.acquire() 
                        self.goleft()
                        self.lock.release()
                        time.sleep(0.2)
                                    
            except Exception as e:
                print(e)
                print('判斷角色位置 有問題')
                self.signal4_log_error.emit('判斷角色位置 有問題')             
      
#-------------------------------------------------------------------------------------
    #有CD技能 or BUFF技能 啟動/暫停按鈕
    def skillbtn(self):

        if self.skillstopevent.is_set():
            self.skillstopevent.clear()
            self.label_45.setText('已啟動')
        else:
            self.skillstopevent.set()
            self.label_45.setText('已暫停/關閉')
#-------------------------------------------------------------------------------------
    #練功 啟動 / 關閉
    def attackbtn(self):
        if self.attackstopevent.is_set():
            #切到遊戲畫面 或 改用gametop()
            time.sleep(0.5)
            mf.gametop()
            time.sleep(0)

            self.attackstopevent.clear()
            self.label_44.setText('開始練等中')
        else:
            self.attackstopevent.set()
            self.label_44.setText('已暫停/停止 練等')

    def load_moudles_thead(self):
            runemodelfun = modelfun()
            self.model = runemodelfun.load_model()
            self.label_52.setText('模型載入完成')
            print('模型載入完成')


#-------------------------------------------------------------------------------------
    #打怪流程 #X=46 Y=108  X=156  Y=108
    def attack_right(self):
        i=0
        
        while True:
            try:
                if not self.attackstopevent.is_set() :
                    if self.checkBox_15.isChecked() :
                        self.lock.acquire()
                        self.self_script_functon(self.lineEdit_25.text())
                        self.lock.release()
                    else:    
                        #主要攻擊過程
                        self.lock.acquire()
                        self.jumpattack()
                        self.lock.release()
                        self.jumpattackdelay()
                        #過程中觸發其他動作
                        i=i+1
                        if i > 30 :
                            i = 0
                            self.lock.acquire() 
                            time.sleep(0.3)
                            self.dumpjump()
                            time.sleep(0.2)
                            self.goright()
                            self.lock.release()    
            except Exception as e:
                print(e)
                print('attack function 有問題')
                self.signal4_log_error.emit('attack function 有問題')
                
            time.sleep(0.01)

#-------------------------------------------------------------------------------------
    def jumpattack(self):

        #跳
        sec = 0.02 +(0.05+random()/20)
        mf.keydownup(self.jumpkey,sec)
        self.log_attack('按下跳躍  時間'+str(round(sec,3))+'秒')
        #延遲
        sec = 0.1 +(random()/10)
        mf.keytimedelay(sec)
        self.log_attack('間隔延遲  時間'+str(round(sec,3))+'秒')
        #跳
        sec = 0.02 +(0.05+random()/20)
        mf.keydownup(self.jumpkey,sec)
        self.log_attack('按下跳躍  時間'+str(round(sec,3))+'秒') 
        #延遲
        sec = 0.01+(random()/40)
        mf.keytimedelay(sec)
        self.log_attack('間隔延遲  時間'+str(round(sec,3))+'秒')
        #打
        sec = 0.2 +(0.05+random()/20)
        mf.keydownup(self.attackkey,sec)
        self.log_attack('按下攻擊  時間'+str(round(sec,3))+'秒') 
#-------------------------------------------------------------------------------------        
    def jumpattackdelay(self):
        #延遲
        sec = 0.34+(random()/33)
        mf.keytimedelay(sec)
        self.log_attack('間隔延遲  時間'+str(round(sec,3))+'秒')
#-------------------------------------------------------------------------------------
    def dumpjump(self):
        mf.dumpjump(self.jumpkey)
        self.signal2_log_key.emit('向下跳躍')
        #跳後延遲 0.05~0.08

    def goright(self): 
        #0.1~0.15
        sec = 0.11 +(random()/20)
        mf.keydownup(self.rightkey,sec)
        self.signal2_log_key.emit('按下方向右鍵  時間'+str(round(sec,3))+'秒')    

    def goleft(self): 
        #0.1~0.15
        sec = 0.11 +(random()/20)
        mf.keydownup(self.leftkey,sec)
        self.signal2_log_key.emit('按下方向左鍵  時間'+str(round(sec,3))+'秒')       

    def jump_two(self):
        #跳
        sec = 0.02 +(0.05+random()/20)
        mf.keydownup(self.jumpkey,sec)
        self.log_attack('按下跳躍  時間'+str(round(sec,3))+'秒')
        #延遲
        sec = 0.11 +(random()/10)
        mf.keytimedelay(sec)
        self.log_attack('間隔延遲  時間'+str(round(sec,3))+'秒')
        #跳
        sec = 0.02 +(0.05+random()/20)
        mf.keydownup(self.jumpkey,sec)
        self.log_attack('按下跳躍  時間'+str(round(sec,3))+'秒')                  
#-------------------------------------------------------------------------------------
    #自製script function
    def self_script_functon(self,actiontext:str):

        #腳本文法錯誤
        try:
            
            actiontext = actiontext.split('/')
            for keyword in actiontext:
                keyword = keyword.split(',')
                if keyword[0] == "按鍵-按壓時間":
                    mf.keydownup(mf.KEY_MAP.get(keyword[1]),int(keyword[2])+(random()/20))
                elif keyword[0] == "間隔延遲":
                    mf.keytimedelay(int(keyword[1])+(random()/20))
                elif keyword[0] == "二段跳":
                    self.jump_two()
                elif keyword[0] == "連接鍵動作":
                    mf.connect_actions(mf.KEY_MAP.get(keyword[1]),mf.KEY_MAP.get(keyword[2]))           
                elif keyword[0] == "下跳":
                    mf.dumpjump(self.jumpkey)

        except Exception as e:
            self.signal4_log_error.emit('自製script 文法錯誤')
            print(e)


#-------------------------------------------------------------------------------------
# ;內鍵預設動作 "下跳","二段跳","連接鍵動作","間隔延遲","單鍵-按多久"
# ;"下跳"         >   mf.dumpjump(jumpkey)
# ;"二段跳"       >   self.jump_two()
# ;"連接鍵動作"   >   mf.connect_actions(key1,key2)
# ;"間隔延遲"     >   mf.keytimedelay(sec)
# ;"按鍵-按壓時間"  >   mf.keydownup(num,sec) 單位 秒
# 例 : 按鍵-按壓時間,f,100/間隔延遲,50/按鍵-按壓時間,f,100/二段跳/連接鍵動作,g,y/下跳
#-------------------------------------------------------------------------------------    
    #解輪的function     
    def mainfun(self):
        t = time.time()
        time.sleep(0.1)
        frame = np.array(self.gamepic)
        time.sleep(0.1)

        time.sleep(0.05)
        a= time.time() - t
        arrows = self.runemodelfun.merge_detection(self.model, frame)
        self.signal2_log_key.emit('解輪所花時間 : ' + str(round((time.time() - t),3)))
        print(arrows)
        return arrows
    #自動走到輪的點並解輪
    def runekeyfunction(self):
        # self.lock.acquire()
        self.goto_rune()
        try:

            time.sleep(0.3)
            mf.keydownup(0x20,0.05)     #按空白鍵
            time.sleep(2)
            testkey = self.mainfun() #判斷上下左右 回傳
            time.sleep(0.3)
            # 按鍵 上下左右
            mf.keydownup(mf.KEY_MAP.get(testkey[0]),0.08)

            mf.keydownup(mf.KEY_MAP.get(testkey[1]),0.08)

            mf.keydownup(mf.KEY_MAP.get(testkey[2]),0.08)

            mf.keydownup(mf.KEY_MAP.get(testkey[3]),0.08)    

 
            self.signal2_log_key.emit('解輪成功')    
        except:   
            self.signal2_log_key.emit('解輪失敗,請暫停打怪 手動解輪')
        # self.lock.release()
  

    def goto_rune(self):

        rune_xy = mf.get_rune_xy(self.gamepic)
        player_xy = mf.get_player_xy(self.gamepic)
        rune_x,rune_y = rune_xy[0],rune_xy[1]
        player_x,player_y = player_xy[0],player_xy[1]

        print(f'輪的位置  x :{rune_x} y : {rune_y} ')
        print(f'角色的位置  x :{player_x} y : {player_y} ')
        time.sleep(1)

        x_axis = (abs(player_x - rune_x)<5) #abs 絕對值
        y_axis = (abs(player_y - rune_y) <5) #abs 絕對值
        time.sleep(0.5)
        #先處理 x軸
        while x_axis == False:

            # if player_x - rune_x > 27:
            #     #向左攻擊跳
            #     mf.keydownup(mf.KEY_MAP.get('left'),0.05) 
            #     self.jumpattack()  
            # elif rune_x - player_x > 27:
            #     #向右攻擊跳
            #     mf.keydownup(mf.KEY_MAP.get('right'),0.05) 
            #     self.jumpattack()
            try:
                if player_x > rune_x:
                    #向左走
                    sec = int(player_x - rune_x)/13
                    mf.keydownup(mf.KEY_MAP.get('left'),sec)   
                elif player_x < rune_x:
                    #向右
                    sec = int(rune_x - player_x)/13
                    mf.keydownup(mf.KEY_MAP.get('right'),sec)  

                #再抓一次角色位置
                time.sleep(1.1)
                player_xy = mf.get_player_xy(self.gamepic)
                player_x,player_y = player_xy[0],player_xy[1]

                time.sleep(0.1)
                print(f'角色的位置  x :{player_x} y : {player_y} ')

                x_axis = (abs(player_x - rune_x)<5)
            except:
                print('X軸失敗')    
            time.sleep(1)

        print('x軸已到位')

        while y_axis == False:
            #再處理Y軸
            try:
                if abs(player_y - rune_y)<5:
                    None
                elif  player_y > rune_y:
                    #向上跳
                    mf.keydownup(self.ropekey,sec)  
                    print('向上跳')
                    time.sleep(0.1)
                    #五轉牽繩
                elif player_y < rune_y:
                    #向下跳
                    self.dumpjump(self.jumpkey)
                    print('向下跳')

                time.sleep(1)

                #再抓一次角色位置
                time.sleep(1.1)
                player_xy = mf.get_player_xy(self.gamepic)
                player_x,player_y = player_xy[0],player_xy[1]
                time.sleep(0.1)
                print(f'角色的位置  x :{player_x} y : {player_y} ')
                y_axis = (abs(player_y - rune_y) <5)
            except:
                print('Y軸失敗')
            time.sleep(1)

        print('已移動到輪的位置')
        self.signal2_log_key.emit('已移動到輪的位置')
        time.sleep(1)

    def load_ini_file(self):
        self.label_53.setText('重新載入中')

        config = configparser.ConfigParser()
        try:
            if self.lineEdit_28.text() =="":
                filename = os.path.join(os.path.dirname(os.path.abspath("main.py")), "config.ini")     
            else:    
                filename = os.path.join(os.path.dirname(os.path.abspath("main.py")), self.lineEdit_28.text())
        except:
            filename = os.path.join(os.path.dirname(os.path.abspath("main.py")), "config.ini")     
        config.read(filename,encoding='utf-8-sig')


        keys = ["skillkey1", "skillkey2", "skillkey3", "skillkey4", "skillkey5", "skillkey6", "skillkey7", "skillkey8", "skillkey9", "skillkey10"]
        keys_CD = ["skillkey_CD_key1","skillkey_CD_key2","skillkey_CD_key3","skillkey_CD_key4","skillkey_CD_key5","skillkey_CD_key6","skillkey_CD_key7","skillkey_CD_key8","skillkey_CD_key9","skillkey_CD_key10"]
        keys_Checked = ["skillkey_Checked_key1","skillkey_Checked_key2","skillkey_Checked_key3","skillkey_Checked_key4","skillkey_Checked_key5","skillkey_Checked_key6","skillkey_Checked_key7","skillkey_Checked_key8","skillkey_Checked_key9","skillkey_Checked_key10"]
        lineedit_list =[self.lineEdit,self.lineEdit_3,self.lineEdit_5,self.lineEdit_7,self.lineEdit_9,self.lineEdit_11,self.lineEdit_13,self.lineEdit_15,self.lineEdit_17,self.lineEdit_19]
        lineedit_list_cd = [self.lineEdit_2,self.lineEdit_4,self.lineEdit_6,self.lineEdit_8,self.lineEdit_10,self.lineEdit_12,self.lineEdit_14,self.lineEdit_16,self.lineEdit_18,self.lineEdit_20]
        lineedit_list_Checked = [self.checkBox,self.checkBox_2,self.checkBox_3,self.checkBox_4,self.checkBox_5,self.checkBox_6,self.checkBox_7,self.checkBox_8,self.checkBox_9,self.checkBox_10]
        for i in range(0,10):
            try:
                lineedit_list[i].setText(config.get("key_time", keys[i]))
                lineedit_list_cd[i].setText(config.get("key_time", keys_CD[i]))
                lineedit_list_Checked[i].setChecked(config.get("key_time", keys_Checked[i]) == 'True')
            except configparser.NoOptionError:
                self.signal4_log_error.emit('讀檔錯誤')
                print(f"No option '{keys[i]}' in section 'SETTINGS'")
                print(f"No option '{keys_CD[i]}' in section 'SETTINGS'")

        self.jumpkey = mf.KEY_MAP.get(config.get("key", 'jumpkey'))
        self.lineEdit_22.setText(config.get("key", 'jumpkey'))
        self.attackkey = mf.KEY_MAP.get(config.get("key", 'attackkey'))
        self.lineEdit_23.setText(config.get("key", 'attackkey'))
        self.ropekey = mf.KEY_MAP.get(config.get("key", 'ropekey'))
        self.lineEdit_24.setText(config.get("key", 'ropekey'))

        self.goright_x_num = int(config.get("key", 'goright_x_num'))
        self.lineEdit_26.setText(config.get("key", 'goright_x_num'))
        self.goleft_x_num = int(config.get("key", 'goleft_x_num'))
        self.lineEdit_27.setText(config.get("key", 'goleft_x_num'))

        self.checkBox_11.setChecked(config.get("checkbox", "listen_polygraph") == 'True')
        self.checkBox_12.setChecked(config.get("checkbox", "listen_rune_xy") == 'True')
        self.checkBox_13.setChecked(config.get("checkbox", "listen_auto_rune") == 'True')
        self.checkBox_14.setChecked(config.get("checkbox", "listen_auto_npc_right_or_left") == 'True')

        self.checkBox_15.setChecked(config.get("self_made_script", "self_script_checkbox") == 'True')
        self.lineEdit_25.setText(config.get("self_made_script", 'self_script'))

        self.signal2_log_key.emit('重新載入成功')
        self.label_53.setText('重新載入完成')

    def save_ini_file(self):
        self.label_59.setText('存檔中,請稍後')
        # Writing Data
        config = configparser.ConfigParser()
        try:
            
            filename = os.path.join(os.path.dirname(os.path.abspath("main.py")),self.lineEdit_28.text())
            config.read(filename,encoding='utf-8-sig')
            config.add_section('key')
            config.add_section('key_time')
            config.add_section('checkbox')
            config.add_section('self_made_script')
        except configparser.NoOptionError:
            self.signal4_log_error.emit('存檔錯誤')



        # try:
            # config.add_section("SETTINGS")
        # except configparser.DuplicateSectionError:
        #     pass
        keys = ["skillkey1", "skillkey2", "skillkey3", "skillkey4", "skillkey5", "skillkey6", "skillkey7", "skillkey8", "skillkey9", "skillkey10"]
        keys_CD = ["skillkey_CD_key1","skillkey_CD_key2","skillkey_CD_key3","skillkey_CD_key4","skillkey_CD_key5","skillkey_CD_key6","skillkey_CD_key7","skillkey_CD_key8","skillkey_CD_key9","skillkey_CD_key10"]
        keys_Checked = ["skillkey_Checked_key1","skillkey_Checked_key2","skillkey_Checked_key3","skillkey_Checked_key4","skillkey_Checked_key5","skillkey_Checked_key6","skillkey_Checked_key7","skillkey_Checked_key8","skillkey_Checked_key9","skillkey_Checked_key10"]
        lineedit_list =[self.lineEdit,self.lineEdit_3,self.lineEdit_5,self.lineEdit_7,self.lineEdit_9,self.lineEdit_11,self.lineEdit_13,self.lineEdit_15,self.lineEdit_17,self.lineEdit_19]
        lineedit_list_cd = [self.lineEdit_2,self.lineEdit_4,self.lineEdit_6,self.lineEdit_8,self.lineEdit_10,self.lineEdit_12,self.lineEdit_14,self.lineEdit_16,self.lineEdit_18,self.lineEdit_20]
        lineedit_list_Checked = [self.checkBox,self.checkBox_2,self.checkBox_3,self.checkBox_4,self.checkBox_5,self.checkBox_6,self.checkBox_7,self.checkBox_8,self.checkBox_9,self.checkBox_10]
        for i in range(0,10):
            try:
                config.set('key_time', keys[i], lineedit_list[i].text())
                config.set('key_time', keys_CD[i], lineedit_list_cd[i].text())
                config.set('key_time', keys_Checked[i], str(lineedit_list_Checked[i].isChecked()))
            except configparser.NoOptionError:
                self.signal4_log_error.emit('存檔錯誤')
                print(f"No option '{keys[i]}' in section 'SETTINGS'")
                print(f"No option '{keys_CD[i]}' in section 'SETTINGS'")
        try:
            config.set("key", "jumpkey", self.lineEdit_22.text())
            config.set("key", "attackkey", self.lineEdit_23.text())
            config.set("key", "ropekey", self.lineEdit_24.text())
            config.set("key", "goright_x_num", self.lineEdit_26.text())
            config.set("key", "goleft_x_num", self.lineEdit_27.text())
            config.set('checkbox', "listen_polygraph", str(self.checkBox_11.isChecked()))
            config.set('checkbox', "listen_rune_xy", str(self.checkBox_12.isChecked()))
            config.set('checkbox', "listen_auto_rune", str(self.checkBox_13.isChecked()))
            config.set('checkbox', "listen_auto_npc_right_or_left", str(self.checkBox_14.isChecked()))
            config.set('self_made_script', "self_script", self.lineEdit_25.text())
            config.set('self_made_script', "self_script_checkbox", str(self.checkBox_15.isChecked()))

        except configparser.NoOptionError:
            self.signal4_log_error.emit('存檔錯誤')
            print('存檔錯誤')
        #儲存檔案
        with open(filename, "w") as config_file:
            config.write(config_file)
        self.label_59.setText('存檔成功')
        self.signal2_log_key.emit('存檔成功')
        time.sleep(0.5)
        self.load_ini_file()
        

    def openfilepath(self):
        try:
            filePath , filterType = QtWidgets.QFileDialog.getOpenFileNames()  # 選擇檔案對話視窗
            print(filePath , filterType)
            fileName = filePath[0][filePath[0].rfind('/')+1:]
            # filePath = filePath[0][:filePath[0].rfind('/')+1]+fileName
            self.lineEdit_28.setText(fileName)
        except:
            None    



    def clearall(self):
        self.checkBox.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.checkBox_4.setChecked(False)
        self.checkBox_5.setChecked(False)
        self.checkBox_6.setChecked(False)
        self.checkBox_7.setChecked(False)
        self.checkBox_8.setChecked(False)
        self.checkBox_9.setChecked(False)
        self.checkBox_10.setChecked(False)
        self.checkBox_11.setChecked(False)
        self.checkBox_12.setChecked(False)
        self.checkBox_13.setChecked(False)
        self.checkBox_14.setChecked(False)
        self.checkBox_15.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.lineEdit_3.setText('')
        self.lineEdit_4.setText('')
        self.lineEdit_5.setText('')
        self.lineEdit_6.setText('')
        self.lineEdit_7.setText('')
        self.lineEdit_8.setText('')
        self.lineEdit_9.setText('')
        self.lineEdit_10.setText('')
        self.lineEdit_11.setText('')
        self.lineEdit_12.setText('')
        self.lineEdit_13.setText('')
        self.lineEdit_14.setText('')
        self.lineEdit_15.setText('')
        self.lineEdit_16.setText('')
        self.lineEdit_17.setText('')
        self.lineEdit_18.setText('')
        self.lineEdit_19.setText('')
        self.lineEdit_20.setText('')
        self.lineEdit_21.setText('')
        self.lineEdit_22.setText('')
        self.lineEdit_23.setText('')
        self.lineEdit_24.setText('')
        self.lineEdit_25.setText('')
        self.lineEdit_26.setText('')
        self.lineEdit_27.setText('')
        self.lineEdit_28.setText('')

# thread_a = QThread()   # 建立 Thread()
# thread_a.run = ui_setting_fun.skill()      # 設定該執行緒執行 a()
# thread_a.start()       # 啟動執行緒