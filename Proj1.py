##### 2024 "TI Cup" Zhejiang Province University Students' Electronic Design Competition E Question Tictactoe OpenMV Control Code
# Topic: https://res.nuedc-training.com.cn/topic/2024/topic_113.html 
# Equipment: OpenMV4 H7 plus & OpenMV IDE 4.2.0
# Author: Gu Kaiser guiser@zju.edu.cn Q: 3023182701 Do not reproduce without authorization!
# Brief: Recognize the black and white pieces on the chessboard and make the next move decision, and transmit it to stm32 through the USART serial port to achieve the control of the homemade robotic arm.
# Algorithm: Minimax (suitable for game playing - completely zero-sum game type, decision tree + depth search)
# References: https://github.com/openmv && https://book.openmv.cc/ && https://pypi.org/ 
# Start: 2024.7.29
# Completion: 2024.8.1
# Acknowledgements: Thanks to Professor Ruan Bingtao for training guidance and ZJU-ISEE for venue support




######  Code Begin  ######

import sensor
import time
import math
import pyb
from pyb import UART
import json
import random

# 阈值库
thresholds = [
    (20, 30, -128, 127, -128, 127),  # generic_black_thresholds
    (95, 100, -128, 127, -128, 127),  # generic_white_thresholds
    # (30, 100, 15, 127, 15, 127), # generic_red_thresholds
]

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.HQVGA)  # 240X160
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must be turned off for color tracking
sensor.set_auto_whitebal(False)  # must be turned off for color tracking
sensor.set_framerate(2)
clock = time.clock()
# sensor.set_windowing(255,240)

# 初始化 UART
uart = UART(3, 9600)
uart.init(9600, bits=8, parity=None, stop=1)

black_points = []
white_points = []
# 定义颜色代码常量
# BLACK_CODE = 1
# WHITE_CODE = 2

### 对弈变量初始化 ###
centerpoint = (120,80) # 初定这个
Fake_Flag = 0 # 棋子有没有被人为动过
# 棋盘大小
BOARD_SIZE = 3
BOARD_WIDE = 27
BOARD_WIDE = BOARD_WIDE - 10

# 玩家标记
HUMAN = 'HU'
AI = 'AI'

# 空格标记
EMPTY = None

#棋盘数据
LastChessBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0]
CurrentChessBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0]

Current_Score = 0

def First_AI_Or_Human(signal):
    global First_Player
    if (signal==1):
        First_Player = HUMAN
    elif(signal==0):
        First_Player = AI
    else:
        First_Player = False


#通过得到的坐标与相对坐标得到棋子所在的方格序号.输入的location与centerpoint均为大小为2的数组，返回输出locationnumber方格序号
#黑色棋子
def Chess_Locate_black(location,centerpoint):
    Locationnumber=0
    if(math.sqrt((location[0] - centerpoint[0]) ** 2 + (location[1] - centerpoint[1]) ** 2) > 120):
        return 0
    if(location[0]<centerpoint[0]-BOARD_WIDE):
        if (location[1]<centerpoint[1]-BOARD_WIDE):
            Locationnumber = 9
        elif(location[1]>centerpoint[1]+BOARD_WIDE):
            Locationnumber = 3
        else:
            Locationnumber = 6
    elif(location[0]>centerpoint[0]+BOARD_WIDE):
        if(location[1]<centerpoint[1]-BOARD_WIDE):
            Locationnumber = 7
        elif(location[1]>centerpoint[1]+BOARD_WIDE):
            Locationnumber = 1
        else:
            Locationnumber = 4
    else:
        if(location[1]<centerpoint[1]-BOARD_WIDE):
            Locationnumber = 8
        elif(location[1]>centerpoint[1]+BOARD_WIDE):
            Locationnumber = 2
        else:
            Locationnumber = 5
    return Locationnumber

#白色棋子，一模一样，函数名用于区分
def Chess_Locate_white(location,centerpoint):
    Locationnumber=0
    if(math.sqrt((location[0] - centerpoint[0]) ** 2 + (location[1] - centerpoint[1]) ** 2)>120):
        return 0
    if(location[0]<centerpoint[0]-BOARD_WIDE):
        if (location[1]<centerpoint[1]-BOARD_WIDE):
            Locationnumber = 9
        elif(location[1]>centerpoint[1]+BOARD_WIDE):
            Locationnumber = 3
        else:
            Locationnumber = 6
    elif(location[0]>centerpoint[0]+BOARD_WIDE):
        if(location[1]<centerpoint[1]-BOARD_WIDE):
            Locationnumber = 7
        elif(location[1]>centerpoint[1]+BOARD_WIDE):
            Locationnumber = 1
        else:
            Locationnumber = 4
    else:
        if(location[1]<centerpoint[1]-BOARD_WIDE):
            Locationnumber = 8
        elif(location[1]>centerpoint[1]+BOARD_WIDE):
            Locationnumber = 2
        else:
            Locationnumber = 5
    return Locationnumber

#更新现在棋盘状态，更改上一次棋盘状态.输入LastChessBoard与CurrentChessBoard均为大小为9的数组，locationnumber即为通过坐标分析出的方格序号用于存储, Player用于区分黑棋还是白旗.
def UpdateBoard(LastChessBoard, CurrentChessBoard, LocationNumber, Player):
    if CurrentChessBoard[LocationNumber-1] != 0:  # 0 表示空位
        return 0
    # 根据玩家放置相应的棋子
    if Player == 1:  # 黑棋
        CurrentChessBoard[LocationNumber-1] = 1
    elif Player == 2:  # 白棋
        CurrentChessBoard[LocationNumber-1] = 2
    return 1


#找到新的棋子位置或者改变位置的棋子，返回一个location数组（位置即为方格序号）。location[0]为模式选择，若为1则返回location[1]新棋子位置，若为2则返回location[1],location[2],
#其中location[1]被改动棋子现在所在的位置，location[2]为原来的位置
def Find_New(LastChessBoard, CurrentChessBoard):
    location = [0,0,0]
    count=0
    Mode =0
    global Human_Color
    global Ai_color

    if (First_Player == HUMAN):
        Human_Color = 1
        Ai_Color = 2
    elif(First_Player == AI):
        Ai_Color = 1
        Human_Color = 2
    if(LastChessBoard.count(Human_Color)==CurrentChessBoard.count(Human_Color) and (CurrentChessBoard.count(Human_Color)+CurrentChessBoard.count(Ai_Color))%2 == Human_Color-1):
        Mode = 2
        location[0]=2
    else:
        Mode = 1
        location[0]=1
    if (Mode==2):
        for i in range(0,9):
            if (CurrentChessBoard[i]!= LastChessBoard[i]):
                count = count+1
                if(CurrentChessBoard[i]==Ai_Color):
                    location[1]=i
                else:
                    location[2]=i
        if(count<2):
            Mode=0
            location[0]=0
    if(Mode==1):
         for i in range(0,9):
            if (CurrentChessBoard[i]!= LastChessBoard[i]):
                if(CurrentChessBoard[i]==Human_Color):
                    location[1]=i
    print("模式是",Mode)
    return location

# 胜利条件
WINNING_COMBOS = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)]
]

# 评估函数，用于Minimax算法
def evaluate(board, player):
    # 检查棋盘上是否有获胜者
    for combo in WINNING_COMBOS:
        for pos in combo:
            if board[pos[0]][pos[1]] != player:
                break
        else:
            return 1 if player == AI else -1
    # 如果棋盘上没有获胜者，检查是否平局
    if all(board[row][col] != EMPTY for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)):
        return 0.5  # 平局
    return 0  # 游戏继续

Ai_move =[]
# Minimax算法 + alpha&beta剪枝
def minimax(board, depth, is_maximizing, alpha, beta, player):
    # 基础情况：游戏结束或达到最大深度
    score = evaluate(board, player)
    if score != 0 or depth == 0:
        return score

    if is_maximizing:
        max_eval = -math.inf
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == EMPTY:
                    board[i][j] = player
                    eval = minimax(board, depth - 1, False, alpha, beta, HUMAN if player == AI else AI)
                    board[i][j] = EMPTY  # 回溯
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = math.inf
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == EMPTY:
                    board[i][j] = HUMAN if player == AI else AI
                    eval = minimax(board, depth - 1, True, alpha, beta, player)
                    board[i][j] = EMPTY  # 回溯
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval

# 选择最佳移动
def find_best_move(board, player):
    best_score = -math.inf
    best_move = None
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == EMPTY:
                board[i][j] = player
                score = minimax(board, 4, False, -math.inf, math.inf, player)
                board[i][j] = EMPTY  # 回溯
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    return best_move

# 棋盘从检测端到算法端转译
def board_change(board,CurrentChessBoard,First_Player):
    #print(CurrentChessBoard)
    print(First_Player)
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if CurrentChessBoard[i*BOARD_SIZE+j] == 1:  #黑棋
                if First_Player == HUMAN:  # HUMAN先手
                    board[i][j] = HUMAN
                elif First_Player == AI:  # AI先手
                    board[i][j] = AI
            elif CurrentChessBoard[i*BOARD_SIZE+j] == 2:  #白旗
                if First_Player == HUMAN:
                    board[i][j] = AI
                elif First_Player == AI:
                    board[i][j] = HUMAN
    return 0

#主游戏进程
def play_game():
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    #if First == 1:
    #    current_player = HUMAN
    #elif First == 2:
    #    current_player = AI

    board_change(board,CurrentChessBoard,First_Player)
    if(First_Player==AI):
        if((CurrentChessBoard.count(1)+CurrentChessBoard.count(2)) % 2== 1):
            return 0
        else:
            move = find_best_move(board, AI)
    if(First_Player==HUMAN):
        if((CurrentChessBoard.count(1)+CurrentChessBoard.count(2)) % 2== 0):
            return 0
        else:
            move = find_best_move(board, AI)
    #print(board)
    Ai_move.append(move)  # 将AI的移动添加到列表中
    # print("AI should move to:", move)  # 打印AI的移动坐标
    board[move[0]][move[1]] = AI
    Current_Score = evaluate(board, AI)
    print(board)
    # judge_Win_Draw(board,First)
    return move

def judge_Win_Draw(board,First):
    # current_player = HUMAN
    if First == 1:
        current_player = HUMAN
    elif First == 2:
        current_player = AI
    score = evaluate(board, AI if current_player == HUMAN else HUMAN)
    if score != 0:
        uart.write('D')
        #if score == 1:
                #uart.write('W')   # 中断示例（判断结束了）
        #elif score == -1:
                #uart.write('L')   # 中断示例（判断结束了）
        #else:
                #uart.write('Z')   # 中断示例（判断结束了）
    # 检查棋盘是否已满
    if all(board[row][col] != EMPTY for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)):
        uart.write('D')   # 中断示例（判断结束了）
        #print("It's a draw!")

def Trans_Board(Locationnumber):
    if Locationnumber == 1:
        return (0,0)
    elif Locationnumber == 2:
        return (0,1)
    elif Locationnumber == 3:
        return (0,2)
    elif Locationnumber == 4:
        return (1,0)
    elif Locationnumber == 5:
        return (1,1)
    elif Locationnumber == 6:
        return (1,2)
    elif Locationnumber == 7:
        return (2,0)
    elif Locationnumber == 8:
        return (2,1)
    elif Locationnumber == 9:
        return (2,2)



def find_max_rect(rects):
    global max_rect
    rect_max = 0
    for rect in rects:
        if rect.w() > rect_max:
            max_rect = rect
            rect_max = rect.w()
    return max_rect

def Find_Corner():
    img = sensor.snapshot()
    rects = find_max_rect(img.find_rects(threshold=3000))
    img.draw_cross(rects.corners()[0],color =(255,0,255))
    img.draw_cross(rects.corners()[1],color =(255,0,255))
    img.draw_cross(rects.corners()[2],color =(255,0,255))
    img.draw_cross(rects.corners()[3],color=(255,0,255))

# 主循环
while True:
    #clock.tick()
    judge=uart.read()
    if(judge!=None):
        if(judge[0]==1 or judge[0]==0):
            First_AI_Or_Human(judge[0])
            print("FirstPlayer")
        else:
            clock.tick()
            img = sensor.snapshot()   # 拍照并获取图像
        # 识别圆形
            circles = img.find_circles(roi=(72,38,95,85),threshold = 2500, x_margin = 10, y_margin = 10, r_margin = 10, r_min = 2, r_max = 12, r_step = 2)

        # 识别颜色
            for c in circles:
                area = (c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r())
                statistics = img.get_statistics(roi=area) #像素颜色统计
            # 进行多颜色识别

                img.draw_cross(c.x(), c.y(),color=(0,255,0))  # 标出色块中心点
                x = c.x()            # 根据颜色代码添加坐标点
                y = c.y()
            # 颜色辨析
                pyb.delay(300)
                if 2<statistics.l_mode()<40 and -45<statistics.a_mode()<22 and -42<statistics.b_mode()<79:
                    black_points.append([x, y])
                    img.draw_rectangle(x,y,10,10,color=(0,255,0))  # 框出识别到的色块
            #elif 69<statistics.l_mode()<100 and -34<statistics.a_mode()<29 and -19<statistics.b_mode()<26:
                else:
                    white_points.append([x, y])
                    img.draw_rectangle(x,y,10,10,color=(0,0,255))  # 框出识别到的色块
            # pyb.delay(1000)
            print(black_points)
            print(white_points)
            print("先手是",First_Player)


        #### 统计过程 ####
            for i in range(0,9):
                    LastChessBoard[i]=CurrentChessBoard[i]
            for i in range(0,9):
                CurrentChessBoard[i]=0
            for black_point in black_points:
                location = Chess_Locate_black(black_point,centerpoint)
                print("黑色棋子",location)
                UpdateBoard(LastChessBoard,CurrentChessBoard,location,1)
            for white_point in white_points:
                location = Chess_Locate_white(white_point,centerpoint)
                print("白色棋子",location)
                UpdateBoard(LastChessBoard,CurrentChessBoard,location,2)
            new_location = Find_New(LastChessBoard, CurrentChessBoard)
            print("上一次棋盘",LastChessBoard)
            print("当前棋盘",CurrentChessBoard)
            if new_location[0] == 1:   ## 没有被偷动过
                print("False")
                should_move = play_game()
                #uart.write(str(should_move[0]))
                # uart.write(str(3))
                if (should_move != 0):
                    print(should_move)
                    uart.write(str(should_move[0]))
                    print(should_move[0])
                    uart.write(" ")
                    uart.write(str(should_move[1]))
                    print(should_move[1])
                    uart.write(" ")
                    uart.write("B")
                    print("Finish")
            elif(new_location[0]==2):
                print("True")
                if new_location != None:
                    print("现在位置",Trans_Board(new_location[1]+1))
                    print("原来位置",Trans_Board(new_location[2]+1))
                    temp = CurrentChessBoard[new_location[2]]
                    CurrentChessBoard[new_location[2]]=CurrentChessBoard[new_location[1]]
                    CurrentChessBoard[new_location[1]]=temp
                    should_move_To = Trans_Board(new_location[2]+1)
                    #print(should_move_To)
                    should_move_From = Trans_Board(new_location[1]+1)
                    #print(should_move_From)
                    uart.write(str(should_move_To[0]))
                    uart.write(" ")
                    uart.write(str(should_move_To[1]))
                    uart.write(" ")
                    uart.write(str(should_move_From[0]))
                    uart.write(" ")
                    uart.write(str(should_move_From[1]))
                    uart.write(" ")
                    uart.write("B")
            if(Current_Score!=0):
                uart.write('D')
                print(2)

            #print("Black Points:", black_points)
            #print("White Points:", white_points)
            ###########
            # uart_stop = bytearray(0xFF)
            # 发送结束标记


            print(clock.fps())

            # 清空列表，释放内存
            black_points.clear()
            white_points.clear()
            pyb.delay(1000)
