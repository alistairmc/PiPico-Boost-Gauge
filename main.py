# WaceShare Library code
# Alistair Mcgranaghan 24/09/2022
from machine import Pin,SPI,PWM
import framebuf
import utime
import os
import math

# ============ Start of Drive Code ================

BL = 13  # Pins used for display screen
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

class LCD_1inch3(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 240
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,100000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0 # Pre-defined colours
        self.green =   0x001f # Probably easier to use colour(r,g,b) defined below
        self.blue  =   0xf800
        self.white =   0xffff
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)  

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
        
    # def taken from https://github.com/dhargopala/pico-custom-font/blob/main/lcd_lib.py    
    def write_text(self,text,x,y,size,color):
        ''' Method to write Text on OLED/LCD Displays
            with a variable font size
            Args:
                text: the string of chars to be displayed
                x: x co-ordinate of starting position
                y: y co-ordinate of starting position
                size: font size of text
                color: color of text to be displayed
        '''
        background = self.pixel(x,y)
        info = []
        
        # Creating reference charaters to read their values
        self.text(text,x,y,color)
        for i in range(x,x+(8*len(text))):
            for j in range(y,y+8):
                # Fetching amd saving details of pixels, such as
                # x co-ordinate, y co-ordinate, and color of the pixel
                px_color = self.pixel(i,j)
                info.append((i,j,px_color)) if px_color == color else None
                
        # Clearing the reference characters from the screen
        self.text(text,x,y,background)
        
        # Writing the custom-sized font characters on screen
        for px_info in info:
            self.fill_rect(size*px_info[0] - (size-1)*x , size*px_info[1] - (size-1)*y, size, size, px_info[2])
              
# ========= End of Driver ===========


# Global values
boost = 0
boost_current = 0
boost_max = 0
boost_sensor = machine.ADC(2)
boost_input_min = 0
boost_input_max = 30.17
boost_array = [0, 0, 0, 0, 0]
temp_array = [0, 0, 0, 0, 0]
startup_loop = 1
boost_loop = 0
current_atms = 14.7
brightness = 65535
temp_sensor = machine.ADC(4)
temp_conversion_factor = 3.3 / (65535)
tmp_current = 0
pwm = PWM(Pin(BL)) # Screen Brightness
pwm.freq(1000)
pwm.duty_u16(brightness) # max 65535 - mid value
LCD = LCD_1inch3()
back_col = 0

def rgb_color(R,G,B):
# Get RED value
    rp = int(R*31/255) # range 0 to 31
    if rp < 0: rp = 0
    r = rp *8

# Get Green value - more complicated!
    gp = int(G*63/255) # range 0 - 63
    if gp < 0: gp = 0
    g = 0
    if gp & 1:  g = g + 8192
    if gp & 2:  g = g + 16384
    if gp & 4:  g = g + 32768
    if gp & 8:  g = g + 1
    if gp & 16: g = g + 2
    if gp & 32: g = g + 4
    
# Get BLUE value
    bp =int(B*31/255) # range 0 - 31
    if bp < 0: bp = 0
    b = bp *256
    rgb_color = r+g+b
    return rgb_color
    
def ring(cx,cy,r,cc):   # Draws a circle - with centre (x,y), radius, color 
    for angle in range(91):  # 0 to 90 degrees in 2s
        y3=int(r*math.sin(math.radians(angle)))
        x3=int(r*math.cos(math.radians(angle)))
        LCD.pixel(cx-x3,cy+y3,cc)  # 4 quadrants
        LCD.pixel(cx-x3,cy-y3,cc)
        LCD.pixel(cx+x3,cy+y3,cc)
        LCD.pixel(cx+x3,cy-y3,cc) 
    

def boostColour(boostValue): # Returns the colour of the boost text based on boost value.
    boostCol = rgb_color(128,128,128)
    print(boostValue)
    if(boostValue <= 6):
        boostCol = rgb_color(64,0,128)
        
    if( boostValue > 6 and boostValue <= 8 ):
        boostCol = rgb_color(0,0,255)
        
    if( boostValue > 8 and boostValue <= 10 ):
        boostCol = rgb_color(0,255,0)
    
    if( boostValue > 10 and boostValue <= 12 ):
        boostCol = rgb_color(255,255,0)

    if( boostValue > 12 and boostValue <= 14 ):
        boostCol = rgb_color(255,128,0)
    
    if( boostValue > 14 ):
        boostCol = rgb_color(255,0,0)
        
    return boostCol
        
def updateBoost(): # Updates the boost value on screen and stores the old value.
    global boost_current
    global boost
    boost_positive = "Boost +Psi"
    boost_negative = "Boost -Psi"
    boost_text = boost_positive
    xpos = 0
    tmp_boost = boost
        
    if tmp_boost < 0:
        tmp_boost = tmp_boost * -1
        boost_text = boost_negative
        
    if tmp_boost < 10: xpos = 60
    
    LCD.fill_rect(0,0,240,190,back_col)
    boost_current = boost
    LCD.write_text(str(tmp_boost), xpos, 70, 15, boostColour(boost))
    LCD.write_text(boost_text, 0, 30, 3, rgb_color(255,255,255))

def readBoost(): # Reads the boost value from the AD pin and return boost value in psi
    global current_atms
    tmp_boost = 0
    tmp_boost = boost_sensor.read_u16()
    boost_voltage = boost_sensor.read_u16() * temp_conversion_factor
    display_boost = int(((tmp_boost - 0) / (65535 - 0)) * (boost_input_max - boost_input_min) + boost_input_min)
    display_boost = display_boost - current_atms # Adjust for atmospheric pressure to get a + or - psi value
    return display_boost

def readTemp(): # Reads temp and returns the value
    temp_reading = 27 - ((temp_sensor.read_u16() * temp_conversion_factor) - 0.706)/0.001721
    return temp_reading

def updateTemp(): # Updates the temprature display with current temp.
    LCD.fill_rect(0,190,240,240,back_col)
    LCD.write_text("Temp:"+str(round(temp_reading, 1))+"C", 0, 200, 3, rgb_color(255,255,255))

def startupDisplay(loop_count): # Draw startup screen
    LCD.fill(0)
    for r in range(loop_count * 4):
        ring(120,120,60+r*3,rgb_color(0,255-8*r,0))
    LCD.text("Calibrating", 75, 115, rgb_color(255,255,255))
    LCD.show()
    
# =========== Main ============

# Background color - black
LCD.fill(rgb_color(0,0,0))
LCD.show()

# Define pins for buttons and Joystick
keyA = Pin(15,Pin.IN,Pin.PULL_UP) # Normally 1 but 0 if pressed
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19,Pin.IN,Pin.PULL_UP)
keyY= Pin(21,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

LCD.show()

running = True # Loop control

# =========== Main loop ===============
while(running):
    #if (keyA.value() == 0):
        #print("A")   
        
    #if (keyB.value() == 0):
        #print("B") 
                   
    #if (keyX.value() == 0):
        #print("X") 
        
    #if (keyY.value() == 0):
        #print("Y")
       
    if (up.value() == 0):
        #print("UP")
        #print("brightness up")
        tmp_brightness = brightness + 2048
        if(tmp_brightness >= 65535):
            tmp_brightness = 65535
        brightness = tmp_brightness
        pwm.duty_u16(brightness)
        
    if (down.value() == 0):
        #print("DOWN")
        #print("brightness down")
        tmp_brightness = brightness - 2048
        if(tmp_brightness <= 4096):
            tmp_brightness = 4096
        brightness = tmp_brightness
        pwm.duty_u16(brightness)
     
    #if (left.value() == 0):
        #print("LEFT")
    
    #if (right.value() == 0):
        #print("RIGHT")
    
    #if (ctrl.value() == 0):
        #print("CTRL")
     
     
    boost_array[boost_loop] = readBoost()
    temp_array[boost_loop] = readTemp()
    boost_loop+=1

    if (startup_loop == 1):
        startupDisplay(boost_loop)
    
    if (boost_loop == 5 and startup_loop == 1 ):
        boost_loop = 0
        startup_loop = 0
        current_atms = (boost_array[0] + boost_array[1] + boost_array[2] + boost_array[3] + boost_array[4]) // 5
    
    if (boost_loop == 5 and startup_loop == 0 ):
        boost_loop = 0
        boost = (boost_array[0] + boost_array[1] + boost_array[2] + boost_array[3] + boost_array[4]) // 5
        temp_reading = (temp_array[0] + temp_array[1] + temp_array[2] + temp_array[3] + temp_array[4]) // 5
        updateBoost()
        updateTemp()
        LCD.show()
    
    
    if (keyA.value() == 0) and (keyY.value() == 0): # Halt looping?
        running = False
        
    utime.sleep_us(200) # Debounce delay 
    
# Finish
LCD.fill(0)
for r in range(10):
    ring(120,120,60+r,rgb_color(255,255,0))
LCD.text("Halted", 95, 115, rgb_color(255,0,0))
LCD.show()

# Tidy up
utime.sleep(3)
LCD.fill(0)
LCD.show()





