import os
import sys
import time
import math
import random

# Real-time Pong for Windows CMD / PowerShell (Python standard library only)
if os.name != "nt":
    import tty, termios, select
else:
    import msvcrt
    os.system("")

CSI="\x1b["
def pos(x,y): return f"{CSI}{y};{x}H"
def color(s,c): return f"{CSI}{c}m{s}{CSI}0m"

WIDTH, HEIGHT = 64, 20
PADDLE_H = 5
WIN_SCORE = 7
FPS = 30

class Game:
    def __init__(self):
        self.score=[0,0]
        self.player=HEIGHT//2
        self.ai=HEIGHT//2
        self.reset_ball(random.choice([-1,1]))
        self.state="menu"
        self.msg="Press ENTER to start | W/S move | Q quit"

    def reset_ball(self, direction):
        self.x,self.y=WIDTH//2,HEIGHT//2
        self.vx=direction*22.0
        self.vy=random.choice([-1,1])*random.uniform(7,11)

    def keys(self):
        out=[]
        if os.name=="nt":
            while msvcrt.kbhit():
                k=msvcrt.getch()
                if k in (b"\xe0",b"\x00"):
                    k=msvcrt.getch()
                    out.append({"H":"up","P":"down"}.get(k.decode(errors="ignore"),""))
                else:
                    out.append(k.decode(errors="ignore").lower())
        else:
            while select.select([sys.stdin],[],[],0)[0]:
                k=sys.stdin.read(1)
                if k=="\x1b":
                    seq=sys.stdin.read(2)
                    out.append({"[A":"up","[B":"down"}.get(seq,""))
                else: out.append(k.lower())
        return out

    def paddle(self, direction, dt):
        self.player=max(PADDLE_H/2,min(HEIGHT-1-PADDLE_H/2,self.player+direction*30*dt))

    def update(self,dt):
        if self.state!="play": return
        # AI follows the ball with limited speed
        diff=self.y-self.ai
        self.ai += max(-25*dt,min(25*dt,diff))
        self.ai=max(PADDLE_H/2,min(HEIGHT-1-PADDLE_H/2,self.ai))

        # substeps ensure paddle collisions are not skipped
        steps=max(1,int(abs(self.vx*dt)/0.35)+1)
        for _ in range(steps):
            self.x += self.vx*dt/steps
            self.y += self.vy*dt/steps
            if self.y<=1:
                self.y=1; self.vy=abs(self.vy)
            if self.y>=HEIGHT-2:
                self.y=HEIGHT-2; self.vy=-abs(self.vy)

            if self.vx<0 and self.x<=4 and abs(self.y-self.player)<=PADDLE_H/2:
                self.x=4; self.hit(self.player,1)
            elif self.vx>0 and self.x>=WIDTH-5 and abs(self.y-self.ai)<=PADDLE_H/2:
                self.x=WIDTH-5; self.hit(self.ai,-1)

        if self.x<1:
            self.score[1]+=1; self.point(-1)
        elif self.x>WIDTH-2:
            self.score[0]+=1; self.point(1)
        if max(self.score)>=WIN_SCORE:
            self.state="over"

    def hit(self,center,direction):
        offset=max(-1,min(1,(self.y-center)/(PADDLE_H/2)))
        speed=min(38,math.hypot(self.vx,self.vy)*1.06+0.4)
        angle=offset*0.9
        self.vx=direction*speed*math.cos(angle)
        self.vy=speed*math.sin(angle)

    def point(self,direction):
        self.state="point"
        self.deadline=time.monotonic()+0.7
        self.direction=direction

    def render(self):
        # One fixed-size canvas; cursor goes to top-left once per frame.
        canvas=[[" "]*WIDTH for _ in range(HEIGHT)]
        for x in range(WIDTH):
            canvas[0][x]="-"; canvas[-1][x]="-"
        for y in range(HEIGHT):
            canvas[y][0]="|"; canvas[y][-1]="|"
        canvas[0][0]=canvas[0][-1]=canvas[-1][0]=canvas[-1][-1]="+"
        for y in range(2,HEIGHT-1,2): canvas[y][WIDTH//2]=":"
        for y in range(round(self.player-PADDLE_H/2),round(self.player+PADDLE_H/2)+1):
            if 1<=y<HEIGHT-1: canvas[y][3]="#"
        for y in range(round(self.ai-PADDLE_H/2),round(self.ai+PADDLE_H/2)+1):
            if 1<=y<HEIGHT-1: canvas[y][WIDTH-4]="#"
        bx,by=round(self.x),round(self.y)
        if 1<=bx<WIDTH-1 and 1<=by<HEIGHT-1: canvas[by][bx]="O"

        lines=["+"+"-"*(WIDTH-2)+"+"]
        lines += ["|"+"".join(r[1:-1])+"|" for r in canvas[1:-1]]
        lines += ["+"+"-"*(WIDTH-2)+"+"]
        header=f" YOU {self.score[0]}    PONG CLI    CPU {self.score[1]} "
        header=header.center(WIDTH)
        if self.state=="menu": footer="ENTER start | W/S or arrows move | Q quit"
        elif self.state=="paused": footer="PAUSED — SPACE to resume"
        elif self.state=="point": footer="POINT! Serving..."
        elif self.state=="over": footer=("YOU WIN!" if self.score[0]>self.score[1] else "CPU WINS!")+" — ENTER rematch | Q quit"
        else: footer="W/S or arrows move | SPACE pause | Q quit | First to 7"
        # Clear and redraw entire terminal frame with explicit line breaks.
        frame=CSI+"H"+CSI+"2J"+color(header,"1;97;44")+"\n"+"\n".join(lines)+"\n"+footer+"\n"
        sys.stdout.write(frame); sys.stdout.flush()

    def run(self):
        old=None
        if os.name!="nt":
            old=termios.tcgetattr(sys.stdin); tty.setcbreak(sys.stdin.fileno())
        sys.stdout.write(CSI+"?25l"); sys.stdout.flush()
        try:
            while True:
                start=time.monotonic()
                dt=min(0.05,start-getattr(self,"last",start))
                self.last=start
                for k in self.keys():
                    if k in ("q","\x1b"): return
                    if k in ("w","up"): self.paddle(-1,0.045)
                    if k in ("s","down"): self.paddle(1,0.045)
                    if k==" ":
                        if self.state=="play": self.state="paused"
                        elif self.state=="paused": self.state="play"
                    if k in ("\r","\n"):
                        if self.state in ("menu","point"): self.state="play"; self.reset_ball(getattr(self,"direction",random.choice([-1,1])))
                        elif self.state=="over":
                            self.score=[0,0]; self.state="menu"; self.player=self.ai=HEIGHT//2
                if self.state=="point" and time.monotonic()>=self.deadline:
                    self.state="play"; self.reset_ball(self.direction)
                self.update(dt)
                self.render()
                time.sleep(max(0,1/FPS-(time.monotonic()-start)))
        finally:
            sys.stdout.write(CSI+"?25h"+CSI+"2J"+CSI+"H"); sys.stdout.flush()
            if old is not None: termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old)

if __name__=="__main__":
    try: Game().run()
    except KeyboardInterrupt: pass
