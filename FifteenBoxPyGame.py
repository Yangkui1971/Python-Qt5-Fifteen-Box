import random, sys, pygame, time, math
from enum import Enum
from pygame.locals import *


# 定义方向枚举类型
class Direction(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"
    NONE = "NONE"


# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
SHADOW = (150, 150, 150)

# Constants
TILEROWS = 4
TILECOLS = 4
TILESIZE = 100
GAPSIZE = 2
FONTSIZEBIG = 48
FONTSIZENORMAL = 32
SHADOWWIDTH = 4  # 要是偶数

SCREENCOLOR = BLACK
TILECOLOR = GREY
TILEFONTCOLOR = RED

BUTTONCOLOR = GREEN
BUTTONTEXTSIZE = 20

TIMEPAUSE = 8.0  # 动画时间停顿 (ms)
ANIMATIONPIECE = 20  # 动画分段数 （越多越平滑）

pygame.init()  # 初始化

screenWidth = GAPSIZE * (TILECOLS + 1) + TILESIZE * TILECOLS + 200
screenHeight = GAPSIZE * (TILEROWS + 1) + TILESIZE * TILEROWS
screen = pygame.display.set_mode((screenWidth, screenHeight))  # 获取窗口对象
pygame.display.set_caption("十五子游戏")  # 窗口名字
pygame.draw.rect(screen, BLUE, (screenWidth - 200, 0, 200, screenHeight))

normalFontObj = pygame.font.Font('freesansbold.ttf', FONTSIZENORMAL)
bigFontObj = pygame.font.Font('freesansbold.ttf', FONTSIZEBIG)
buttonFontObj = pygame.font.Font('freesansbold.ttf', BUTTONTEXTSIZE)


class Board:
    def __init__(self):
        self.tiles = []
        self.emptyX = 0  # 空位的位置
        self.emptyY = 0
        self.shuffle()

    def shuffle(self):  # 洗牌, 利用random.shuffle函数
        self.tiles=[]
        cardList = [x for x in range(0, TILECOLS * TILEROWS)]
        random.shuffle(cardList)
        for i in range(0, TILEROWS):
            for j in range(0, TILECOLS):
                theNum = cardList[i * TILECOLS + j]
                if theNum == 0:
                    self.emptyX = j
                    self.emptyY = i
                theTile = Tile(j, i, theNum)
                self.tiles.append(theTile)

    def drawBoard(self):  # 画游戏子面板
        for i in range(0, TILECOLS * TILEROWS):
            self.tiles[i].drawTile()

    def isValidMouseClick(self, mouseWinX, mouseWinY):
        # 鼠标点击的位置是否在空盒的上下或左右，并返回 （是否可移动，需要移动的方向）
        def mouseLocToBoardLoc(mouseWinX, mouseWinY):
            # 把鼠标的坐标转换为盒子坐标， 如在外，返回False和原坐标
            bx = (mouseWinX - GAPSIZE) // (TILESIZE + GAPSIZE)
            by = (mouseWinY - GAPSIZE) // (TILESIZE + GAPSIZE)
            if bx < 0 or bx > TILECOLS - 1 or by < 0 or by > TILEROWS - 1:
                return False, mouseWinX, mouseWinY
            else:
                return True, bx, by

        # >>>>>>>>>>>>>>>>
        inside, bx, by = mouseLocToBoardLoc(mouseWinX, mouseWinY)
        if inside:
            if bx == self.emptyX and by == self.emptyY - 1:
                return True, Direction.DOWN  # 移动的方向相反
            elif bx == self.emptyX and by == self.emptyY + 1:
                return True, Direction.UP
            elif bx == self.emptyX - 1 and by == self.emptyY:
                return True, Direction.RIGHT
            elif bx == self.emptyX + 1 and by == self.emptyY:
                return True, Direction.LEFT
        return False, Direction.NONE

    def MakeChange(self, tDirection):
        # 根据方向键的内容，交换空值和盒子的位置，并动画显示
        def isValidMove(tDirection) -> tuple:  # (bool,int,int):
            # 判断移动是否有效， 并给出移动盒子x和y的增减值（先对于空值 有值盒子的位置）
            if tDirection == Direction.LEFT:
                if self.emptyX == TILECOLS - 1:
                    return False, 0, 0
                else:
                    return True, 1, 0
            elif tDirection == Direction.RIGHT:
                if self.emptyX == 0:
                    return False, 0, 0
                else:
                    return True, -1, 0
            elif tDirection == Direction.UP:
                if self.emptyY == TILEROWS - 1:
                    return False, 0, 0
                else:
                    return True, 0, 1
            elif tDirection == Direction.DOWN:
                if self.emptyY == 0:
                    return False, 0, 0
                else:
                    return True, 0, -1
            else:
                return False, 0, 0

        # >>>>>>>>>>>>>>>>>>>
        isMovable, deltabx, deltaby = isValidMove(tDirection)
        if isMovable:
            thebx = self.emptyX + deltabx
            theby = self.emptyY + deltaby
            theTile = self.tiles[thebx + theby * TILECOLS]
            theTile.moveTile(self.emptyX, self.emptyY)
            # print(theTile.bx, ' , ', theTile.by)
            # 交换存储位置
            self.tiles[thebx + theby * TILECOLS].bx = self.emptyX
            self.tiles[thebx + theby * TILECOLS].by = self.emptyY
            # self.tiles[thebx+theby*TILECOLS].num=0

            self.tiles[self.emptyX + self.emptyY * TILECOLS].bx = thebx
            self.tiles[self.emptyX + self.emptyY * TILECOLS].by = theby
            # self.tiles[self.emptyX+self.emptyY*TILECOLS].num=0

            self.tiles[thebx + theby * TILECOLS], self.tiles[self.emptyX + self.emptyY * TILECOLS] = \
                self.tiles[self.emptyX + self.emptyY * TILECOLS], self.tiles[thebx + theby * TILECOLS]
            self.emptyX = thebx
            self.emptyY = theby
            # self.TestDraw()

    def isSucessful(self):
        for i in range(TILECOLS * TILEROWS - 1):
            if self.tiles[i].num != i + 1:
                return False
        return True

    def TestDraw(self):
        for i in range(TILEROWS):
            for j in range(TILECOLS):
                print(str(self.tiles[j + i * TILECOLS].num), sep='  ', end='')
            print('\n')


class Tile:
    def __init__(self, boardX, boardY, num):
        self.bx = boardX
        self.by = boardY
        self.num = num

    # 盒子坐标变换成窗口坐标
    def bxToWinX(self, bx):
        return GAPSIZE * (bx + 1) + TILESIZE * bx

    # 盒子坐标变换成窗口坐标
    def byToWinY(self, by):
        return GAPSIZE * (by + 1) + TILESIZE * by

    # 画方块自己
    def drawTile(self):
        if self.num == 0:
            winX = int(self.bxToWinX(self.bx))
            winY = int(self.byToWinY(self.by))
            locAndSize = (winX, winY, TILESIZE, TILESIZE)
            # 画空盒子
            pygame.draw.rect(screen, SCREENCOLOR, locAndSize)    
            return
        self.drawTileInXY(self.bx, self.by)

    # 根据盒子坐标画方块，接受浮点数
    def drawTileInXY(self, thebx, theby):
        winX = int(self.bxToWinX(thebx))
        winY = int(self.byToWinY(theby))
        locAndSize = (winX, winY, TILESIZE, TILESIZE)
        # 画盒子
        pygame.draw.rect(screen, TILECOLOR, locAndSize)
        # 画空隙
        pygame.draw.rect(screen, SCREENCOLOR, (winX + TILESIZE, winY, GAPSIZE, TILESIZE))
        pygame.draw.rect(screen, SCREENCOLOR, (winX, winY + TILESIZE, TILESIZE + GAPSIZE, GAPSIZE))
        # Shadows , Widht-1 and Height-1 因为直线的线宽是偶数，缺乏中心位置
        pygame.draw.line(screen, WHITE, (winX, winY + SHADOWWIDTH // 2 - 1),
                         (winX + TILESIZE - 1 - SHADOWWIDTH, winY + SHADOWWIDTH // 2 - 1), SHADOWWIDTH)
        pygame.draw.line(screen, SHADOW, (winX + SHADOWWIDTH, winY + TILESIZE - 1 - SHADOWWIDTH // 2),
                         (winX + TILESIZE - 1, winY + TILESIZE - 1 - SHADOWWIDTH // 2), SHADOWWIDTH)
        pygame.draw.line(screen, WHITE, (winX + SHADOWWIDTH // 2 - 1, winY),
                         (winX + SHADOWWIDTH // 2 - 1, winY + TILESIZE - 1), SHADOWWIDTH)
        pygame.draw.line(screen, SHADOW, (winX + TILESIZE - SHADOWWIDTH // 2 - 1, winY),
                         (winX + TILESIZE - SHADOWWIDTH // 2 - 1, winY + TILESIZE - 1), SHADOWWIDTH)
        # Number    
        textSurfaceObj = normalFontObj.render(str(self.num), True, TILEFONTCOLOR, TILECOLOR)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (winX + TILESIZE // 2, winY + TILESIZE // 2)
        screen.blit(textSurfaceObj, textRectObj)

    # 移动方块
    def moveTile(self, newbx, newby):
        # 新位置和目前位置的差别
        delta: float = math.sqrt((newbx - self.bx) ** 2 + (newby - self.by) ** 2)
        px = self.bxToWinX(self.bx)
        py = self.byToWinY(self.by)
        for i in range(ANIMATIONPIECE):
            lamb: float = (i + 1) * 1.0 / ANIMATIONPIECE
            x = self.bx + (newbx - self.bx) * lamb
            y = self.by + (newby - self.by) * lamb
            # print(x,y)
            pygame.draw.rect(screen, SCREENCOLOR, (px, py, TILESIZE + GAPSIZE, TILESIZE + GAPSIZE))
            self.drawTileInXY(x, y)
            pygame.display.update()
            time.sleep(TIMEPAUSE / 1000.0)


class Button:
    def __init__(self, locX, locY, width, height, text, dofunc):
        self.locX = locX  # winX
        self.locY = locY  # winY
        self.width = width
        self.height = height
        self.text = text
        self.depression = False
        self.dofunc = dofunc
        # self.redraw()

    def redraw(self):
        def Darker(color):
            # 变暗
            red = color[0] - 100
            blue = color[1] - 100
            green = color[2] - 100
            return (red if red > 0 else 0,
                    blue if blue > 0 else 0,
                    green if green > 0 else 0)

        def Lighter(color):
            # 变亮
            red = color[0] + 100
            blue = color[1] + 100
            green = color[2] + 100
            return (red if red < 255 else 255,
                    blue if blue < 255 else 255,
                    green if green < 255 else 255)

        # >>>>>>>>>>>>>>>>
        if self.depression:
            shadowColor = Lighter(BUTTONCOLOR)
            reflectColor = Darker(BUTTONCOLOR)
        else:
            shadowColor = Darker(BUTTONCOLOR)
            reflectColor = Lighter(BUTTONCOLOR)
        # 通过文本长度核实按钮的长度    
        textSurfaceObj = buttonFontObj.render(str(self.text), True, TILEFONTCOLOR, BUTTONCOLOR)
        textRectObj = textSurfaceObj.get_rect()
        if (twidth := textRectObj.width) > self.width - 2 * SHADOWWIDTH - 4:
            self.width = twidth + 2 * SHADOWWIDTH + 4
        locAndSize = (self.locX, self.locY, self.width, self.height)
        # 画矩形
        pygame.draw.rect(screen, BUTTONCOLOR, locAndSize)

        # Shadows , Widht-1 and Height-1 因为直线的线宽是偶数，缺乏中心位置
        pygame.draw.line(screen, reflectColor, (self.locX, self.locY + SHADOWWIDTH // 2 - 1), \
                         (self.locX + self.width - 1, self.locY + SHADOWWIDTH // 2 - 1), SHADOWWIDTH)  # up --
        pygame.draw.line(screen, shadowColor, (self.locX, self.locY + self.height - SHADOWWIDTH // 2 - 1), \
                         (self.locX + self.width - 1, self.locY + self.height - SHADOWWIDTH // 2 - 1),
                         SHADOWWIDTH)  # down --
        pygame.draw.line(screen, reflectColor, (self.locX + self.width - SHADOWWIDTH // 2 - 1, self.locY + SHADOWWIDTH), \
                         (self.locX + self.width - SHADOWWIDTH // 2 - 1, self.locY + self.height - SHADOWWIDTH - 1),
                         SHADOWWIDTH)  # right |
        pygame.draw.line(screen, shadowColor, (self.locX + SHADOWWIDTH // 2 - 1, self.locY + SHADOWWIDTH), \
                         (self.locX + SHADOWWIDTH // 2 - 1, self.locY + self.height - SHADOWWIDTH - 1),
                         SHADOWWIDTH)  # left |
        # Number    
        if self.depression:
            textRectObj.center = (self.locX + self.width // 2 + 2, self.locY + self.height // 2 + 2)
        else:
            textRectObj.center = (self.locX + self.width // 2, self.locY + self.height // 2)
        screen.blit(textSurfaceObj, textRectObj)
        pygame.display.update()

    def isMouseIn(self, mouseWinX, mouseWinY) -> bool:
        if mouseWinX >= self.locX and mouseWinX <= self.locX + self.width - 1 and mouseWinY >= self.locY and mouseWinY <= self.locY + self.height - 1:
            return True
        else:
            return False

    def action(self):
        if self.dofunc:
            self.dofunc()


class ButtonCollection:
    def __init__(self):
        self.buttonList = []

    def addButton(self, theButton: Button):
        self.buttonList.append(theButton)

    def redrawButtons(self):
        for theBtn in self.buttonList:
            theBtn.redraw()

    def mouseButtonUp(self, mouseWinX, mouseWinY) -> bool:
        for theBtn in self.buttonList:
            if theBtn.isMouseIn(mouseWinX, mouseWinY):
                theBtn.depression = False
                theBtn.redraw()
                theBtn.action()
                return True
        return False

    def mouseButtonDown(self, mouseWinX, mouseWinY):
        for theBtn in self.buttonList:
            if theBtn.isMouseIn(mouseWinX, mouseWinY):
                theBtn.depression = True
                theBtn.redraw()

    def mouseMove(self, mouseWinX, mouseWinY):  # 要把按下的重画
        for theBtn in self.buttonList:
            if theBtn.isMouseIn(mouseWinX, mouseWinY):
                theBtn.depression = False
                theBtn.redraw()

def replay():
    theBoard.shuffle()
    theBoard.drawBoard()

def finish():
    pygame.quit()
    sys.exit()
# ============ 正式的程序开始（以前为常量定义和类定义）===================
# 创建面板
theBoard = Board()
theBoard.drawBoard()
# 生成按钮
theBtnCollection = ButtonCollection()
replayBtn = Button(GAPSIZE * (TILECOLS + 1) + TILESIZE * TILECOLS + 10, 100, 160, 60, "Reshuffle", replay)
theBtnCollection.addButton(replayBtn)
finishBtn = Button(GAPSIZE * (TILECOLS + 1) + TILESIZE * TILECOLS + 10, 200, 160, 60, "Finish", finish)
theBtnCollection.addButton(finishBtn)
theBtnCollection.redrawButtons()

# 定义按钮动作

while True:
    for event in pygame.event.get():
        # print(event.type)
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYUP:
            if event.key in (K_ESCAPE, K_q):
                pygame.quit()
                sys.exit()
            elif event.key in (K_a, K_LEFT):
                cDirection = Direction.LEFT
                # theBoard.tiles[1].moveTile(2,2)
            elif event.key in (K_d, K_RIGHT):
                cDirection = Direction.RIGHT
            elif event.key in (K_w, K_UP):
                cDirection = Direction.UP
            elif event.key in (K_s, K_DOWN):
                cDirection = Direction.DOWN
            # print(cDirection)
            theBoard.MakeChange(cDirection)
        elif event.type == MOUSEBUTTONDOWN:  # 鼠标处理
            theBtnCollection.mouseButtonDown(event.pos[0], event.pos[1])
        elif event.type == MOUSEBUTTONUP:
            if theBtnCollection.mouseButtonUp(event.pos[0], event.pos[1]):
                pass
            else:
                isOK, cDirection = theBoard.isValidMouseClick(event.pos[0], event.pos[1])
                if isOK:
                    theBoard.MakeChange(cDirection)
        elif event.type == MOUSEMOTION:
            theBtnCollection.mouseMove(event.pos[0], event.pos[1])
    # screen.fill(SCREENCOLOR)
    pygame.display.update()  # 更新
