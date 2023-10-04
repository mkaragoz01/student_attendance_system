from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pirc522 import RFID
import signal
import RPi.GPIO as GPIO
from time import sleep
from buzzer_lib import ses
from blink import led
from ledRed import led2
from time import sleep
import sys
import sqlite3


class YoklamaSistemi(QWidget):
    def __init__(self,parent = None):
        super(YoklamaSistemi,self).__init__(parent)
        
        grid = QGridLayout()
        
        logo = QLabel()
        logo.setPixmap(QPixmap("/home/pi/Downloads/ybs.jpeg"))
        self.name = QLabel()
        self.name.setText("<center><font size='10'>Ders Başlamadı...</center></font>")
        self.no = QLabel(f"<center><font size='10'>      </center></font>")
        self.katilim = QLabel("<font size='10'>      <center></font></center>")
        self.foto = QLabel("              ")
        
        grid.addWidget(logo,0,0,1,1)
        grid.addWidget(QLabel("<font size='25' color='brown'><b>Dokuz Eylül YBS Yoklama Sistemi</font></b>"),0,1,1,2)
        grid.addWidget(QLabel("<font size='10'><b>Ad-Soyad: </font></b>"),1,0,1,1)
        grid.addWidget(self.name,1,1,1,1)
        grid.addWidget(QLabel("<font size='10'><b>Öğrenci No: </font></b>"),2,0,1,1)
        grid.addWidget(self.no,2,1,1,1)
        grid.addWidget(self.foto,1,2,3,3)
        grid.addWidget(QLabel("<font size='10'><b>Derse Katılımı: </font></b>"),3,0,1,1)
        grid.addWidget(self.katilim,3,1,1,1)
        
        self.setWindowTitle("Yoklama Sistemi")
        self.setLayout(grid)
        self.move(50,200)
        
        self.start = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.yoklama)
        self.timer.start(1000)
      
    def yoklama(self):
        GPIO.cleanup()
        baglanti=sqlite3.connect("ogrenciler.db")
        isaretci=baglanti.cursor()
        self.rdr = RFID()
        self.util = self.rdr.util()
        counter = 0
        while counter < 1:    
            
            ogrenci = isaretci.execute('''SELECT id FROM ogrenciler''')
            
            self.kart_uid = ""
            self.util.debug = True
            print("Kart bekleniyor...")
            self.rdr.wait_for_tag()
            (error, data) = self.rdr.request()

            if not error:
                print("Kart Algilandi!")
                counter += 1
                
                (error, uid) = self.rdr.anticoll()
                if not error:
                    self.kart_uid = str(uid[0])+" "+str(uid[1])+" "+str(uid[2])+" "+str(uid[3])+" "+str(uid[4])
                    print(self.kart_uid)

                if self.start:
                    if self.kart_uid in ogrenci:
                        self.read_student()
                    elif self.kart_uid == "131 115 128 244 132":
                        self.teacher_stop()
                    else:
                        self.undefined_card()
                else:
                    if self.kart_uid == "131 115 128 244 132":
                        self.teacher_start()
                    else:
                        led2(),ses()
                baglanti.commit()
        baglanti.close()
    
    def read_student(self):
        led(),ses()
        ogrenci = isaretci.execute(f'''SELECT * FROM ogrenciler WHERE id={self.kart_uid}''')
        gelme = [j[2] for j in ogrenci]
        isaretci.execute(f'''UPDATE ogrenciler set derseKatilim ={int(gelme[0])+1} WHERE id={self.kart_uid}''')
        ogrenci = isaretci.execute(f'''SELECT * FROM ogrenciler WHERE id={self.kart_uid}''')
        # i[0] == id, i[1] == name, i[2] == attend, i[3] == number
        for i in ogrenci:
            self.name.setText(f"<center><font size='10'>{i[1]}</center></font>")
            self.katilim.setText(f"<center><font size='10'>{str(i[2])}</center></font>")
            self.no.setText(f"<center><font size='10'>{i[3]}</center></font>")
            self.foto.setPixmap(QPixmap(f"/home/pi/Downloads/{i[0]}.jpeg"))
    
    def teacher_stop(self):
        led(),ses()
        self.name.setText(f"<center><font size='10'>Vahap Tecim</center></font>")
        self.katilim.setText(f"<center><font size='10'></center></font>")
        self.no.setText(f"<center><font size='10'>Ders Bitti.</center></font>")
        self.foto.setPixmap(QPixmap("/home/pi/Downloads/vt.jpeg"))
        self.start = False  
    
    def teacher_start(self):
        led(),ses()
        self.name.setText(f"<center><font size='10'>Vahap Tecim</center></font>")
        self.katilim.setText(f"<center><font size='10'>      </center></font>")
        self.no.setText(f"<center><font size='10'>Ders Başladı!!!</center></font>")
        self.foto.setPixmap(QPixmap("/home/pi/Downloads/vt.jpeg"))
        self.start = True
    
    def undefined_card(self):
        led2(),ses()
        self.name.setText(f"<center><font size='10'>Tanımsız!!!</center></font>")
        self.katilim.setText(f"<center><font size='10'>xx</center></font>")
        self.no.setText(f"<center><font size='10'>xxxxxxxxxx</center></font>")
        self.foto.setPixmap(QPixmap("/home/pi/Downloads/tanimsiz.jpeg"))           

        
app = QApplication(sys.argv)
pen = YoklamaSistemi()
pen.resize(500,500)
pen.show()
sys.exit(app.exec_())