import socket
import time
import math
# import heapq

# User and Launcher Information
NICKNAME = 'GWANGJU01_GOSUNYOUNG'
HOST = '127.0.0.1'

# Static Value(Do not modify)
PORT = 1447
CODE_SEND = 9901
CODE_REQUEST = 9902
SIGNAL_ORDER = 9908
SIGNAL_CLOSE = 9909


# Predefined Variables(Do not modify)
TABLE_WIDTH = 254
TABLE_HEIGHT = 127
NUMBER_OF_BALLS = 6
HOLES = [[0, 0], [127, 0], [254, 0], [0, 127], [127, 127], [254, 127]]


class Conn:
    def __init__(self):
        self.sock = socket.socket()
        print('Trying to Connect: %s:%d' % (HOST, PORT))
        self.sock.connect((HOST, PORT))
        print('Connected: %s:%d' % (HOST, PORT))
        send_data = '%d/%s/' % (CODE_SEND, NICKNAME)
        self.sock.send(send_data.encode('utf-8'))
        print('Ready to play!\n--------------------')

    def request(self):
        self.sock.send('%d/%d' % (CODE_REQUEST, CODE_REQUEST).encode())
        print('Received Data has been currupted, Resend Requested.')

    def receive(self):
        recv_data = (self.sock.recv(1024)).decode()
        print('Data Received: %s' % recv_data)
        return recv_data

    def send(self, angle, power):
        if power <= 0:
            print('Power must be bigger than 0, Try again.')
            return False
        merged_data = '%f/%f/' % (angle, power)
        self.sock.send(merged_data.encode('utf-8'))
        print('Data Sent: %s' % merged_data)

    def close(self):
        self.sock.close()
        print('Connection Closed.\n--------------------')


class GameData:
    def __init__(self):
        self.order = 0
        self.reset()

    def reset(self):
        self.balls = [[0, 0] for i in range(NUMBER_OF_BALLS)]

    def read(self, conn):
        recv_data = conn.receive()
        split_data = recv_data.split('/')
        idx = 0
        try:
            for i in range(NUMBER_OF_BALLS):
                for j in range(2):
                    self.balls[i][j] = int(split_data[idx])
                    idx += 1
        except:
            self.reset()
            conn.request()
            self.read(conn)

    def arrange(self):
        self.order = self.balls[0][1]
        print('\n* You will be the %s player. *\n' %
              ('first' if self.order == 1 else 'second'))

    def show(self):
        print('====== Arrays ======')
        for i in range(NUMBER_OF_BALLS):
            print('Ball %d: %d, %d' % (i, self.balls[i][0], self.balls[i][1]))
        print('====================')


def play(conn, gameData):
    angle = 0.0
    power = 0.0

    ##############################
    # Begining of Your Code
    # Put your code here to set angle and power values.
    # angle(float) must be between 0.0 and 360.0
    # power(float) must be between 1.0 and 100.0
    target = [[1, 3], [2, 4]]
    if gameData.order == 1: s = 0
    else: s = 1
    
    white_x = gameData.balls[0][0]
    white_y = gameData.balls[0][1]

    # 목적구가 모두 당구대 위에 온전히 있을 때
    if gameData.balls[target[s][0]][0] != -1 and gameData.balls[target[s][1]][0] != -1:
        # 1번 공이 3번 공보다 흰공에 비해 멀거나 같다면
        if (gameData.balls[target[s][0]][0] - white_x)**2 + (gameData.balls[target[s][0]][1] - white_x)**2 >= (gameData.balls[target[s][1]][0] - white_x)**2 + (gameData.balls[target[s][1]][1] - white_x)**2:
            targetBall_x = gameData.balls[target[s][1]][0]
            targetBall_y = gameData.balls[target[s][1]][1]
        # 1번 공이 3번 공보다 가깝다면
        elif (gameData.balls[target[s][0]][0] - white_x)**2 + (gameData.balls[target[s][0]][1] - white_x)**2 < (gameData.balls[target[s][1]][0] - white_x)**2 + (gameData.balls[target[s][1]][1] - white_x)**2:
            targetBall_x = gameData.balls[target[s][0]][0]
            targetBall_y = gameData.balls[target[s][0]][1]
    
    # 첫번째 상황의 경우, 3번 공이 나가리
    elif gameData.balls[target[s][0]][0] != -1 and gameData.balls[target[s][1]][0] == -1:
        targetBall_x = gameData.balls[target[s][0]][0]
        targetBall_y = gameData.balls[target[s][0]][1]
    # 첫번째 상황의 경우, 1번 공이 나가리
    elif gameData.balls[target[s][0]][0] != -1 and gameData.balls[target[s][1]][0] == -1:
        targetBall_x = gameData.balls[target[s][1]][0]
        targetBall_y = gameData.balls[target[s][1]][1]
    # 모두 나가리 => 8번 공이 목적구가 됨
    elif gameData.balls[target[s][0]][0] == -1 and gameData.balls[target[s][1]][0] == -1:
        targetBall_x = gameData.balls[5][0]
        targetBall_y = gameData.balls[5][1]
    
    width = abs(targetBall_x - white_x)
    height = abs(targetBall_y - white_y)

    # 흰 공을 원점이라 가정했을 때 직교 좌표계에서 target_Ball이 축과 4개의 사분면에 놓이는 8가지 경우
    if white_y < targetBall_y:
        radian = math.atan(width / height)
        if white_x < targetBall_x:
            angle = 180 / math.pi * radian
        elif white_x > targetBall_x:
            angle = 360 - 180 / math.pi * radian
        else: 0

    elif white_y > targetBall_y:
        radian = math.atan(height / width)
        if white_x < targetBall_x:
            angle = (180 / math.pi * radian) + 90
        elif white_x > targetBall_x:
            angle = 270 - (180 / math.pi * radian)
        else: 180
    
    else:
        if white_x < targetBall_x: angle = 90
        elif white_x > targetBall_x: angle = 270

    distance = math.sqrt(width**2 + height**2)
    # angle_hole = (hole_angle_trace(angle, targetBall_x, targetBall_y)/180)*math.pi
    # if (24<targetBall_x<230) and (24<targetBall_y<103):
    #     angle -= (180/math.pi)*math.atan(5.72*math.sin(angle_hole)/distance-5.72*math.cos(angle_hole))

    angle = (angle+360.0)% 360 # angle을 0~360으로 맞추기
    power = distance
    # You can clear Stage 1 with the pre-written code above.
    # Those will help you to figure out how to clear other Stages.
    # Good luck!!
    # End of Your Code
    ##############################
    conn.send(angle, power)


# def hole_angle_trace(angle,tx,ty):
#     """
#     targetball의 위치를 받아서, 넣기 편한 구멍의 방향쪽으로 튕길 수 있는 각도를 제시한다.
#     """
#     angle_between_target_holes = [0,0,0,0,0,0]
#     for i in range(6):
#         hx = HOLES[i][0]
#         hy = HOLES[i][1]
#         width = abs(tx-hx)
#         height = abs(ty-hy)
#         if (ty < hy):
#             radian = math.atan(width / height)
#             if tx < hx:
#                 angle_bth = (180 / math.pi) * radian
#             elif tx > hx:
#                 angle_bth = 360 - (180 / math.pi) * radian
#             else: angle = 0
#         elif (ty > hy):
#             radian = math.atan(height / width)
#             if tx < hx:
#                 angle_bth = (((180 / math.pi)) * radian) + 90
#             elif tx > hx:
#                 angle_bth = 270 - (((180 / math.pi)) * radian)
#             else: angle_bth = 180
#         else:
#             if tx < hx:
#                 angle_bth = 90
#             elif tx > hx:
#                 angle_bth = 270
        
#         angle_between_target_holes[i] = angle_bth - angle  
#     heapq.heapify(angle_between_target_holes)
#     return heapq.heappop(angle_between_target_holes)


def main():
    conn = Conn()
    gameData = GameData()
    while True:
        gameData.read(conn)
        if gameData.balls[0][0] == SIGNAL_ORDER:
            gameData.arrange()
            continue
        elif gameData.balls[0][0] == SIGNAL_CLOSE:
            break
        gameData.show()
        play(conn, gameData)
    conn.close()


if __name__ == '__main__':
    main()
