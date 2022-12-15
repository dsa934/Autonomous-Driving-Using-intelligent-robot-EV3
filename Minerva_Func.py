import rpyc
import io
import os
import cv2
import google.cloud.vision

class Minerva():

    # 생성자
    def __init__(self):
        # RPYC 연결
        self.conn = rpyc.classic.connect('192.168.0.24')

        # ev3 모듈을 rpyc로 가져오기 
        self.ev3 = self.conn.modules['ev3dev.ev3']

        # 모터 B, C와 UltraSonic 설정
        self.MotorB = self.ev3.LargeMotor('outB')
        self.MotorC = self.ev3.LargeMotor('outC')

        self.ultrasonic = self.ev3.UltrasonicSensor()
        assert self.ultrasonic.connected, "Connect a single US sensor to any sensor port"
        self.ultrasonic.mode = 'US-DIST-CM'

        # 목적지에 도달했는지 확인
        self.destination = False

        # U턴 했다 라는 상태를 알리는 변수
        self.after_u_turn = False

        # 백 트레이싱에 사용할 리스트 길이
        self.back_trace_list_length = 0

        # Forward의 거리 저장하는 변수 
        self.current_distance = 0

        # 경로를 저장하는 path list
        self.parking_list = []
        self.path_list = []
        self.path_list_index = 0


    def Move_Forward(self, speed_B = 100, speed_C = 180):
        self.MotorB.run_forever(speed_sp = speed_B)
        self.MotorC.run_forever(speed_sp = speed_C)
        self.Sleep_Motor(0) # 돌기 보정을위해 
        self.MotorC.run_forever(speed_sp = speed_B)

    # 백 트레이싱에선 거리로 전진해야 함 
    def Move_Forward_Distance(self, position, speed_B = 100, speed_C = 100):
        self.Reset_Encoder()
        self.MotorB.run_to_rel_pos(position_sp = position + 10, speed_sp = speed_B)
        self.MotorC.run_to_rel_pos(position_sp = position, speed_sp = speed_C)
        self.MotorC.run_to_rel_pos(position_sp = position, speed_sp = speed_B)
        self.MotorB.wait_until_not_moving()

    
    def Move_Left(self):
        pi = 3.14
        left_distance = 21.0 * pi / 4

        self.Reset_Encoder()
        self.MotorB.run_to_rel_pos(position_sp = 0, speed_sp = 0)
        self.MotorC.run_to_rel_pos(position_sp = self.CM_To_Encoder(left_distance), speed_sp = 200)
        self.MotorC.wait_until_not_moving()
     


    def Move_Right(self):
        pi = 3.14
        right_distance = 20.0 * pi / 4

        self.Reset_Encoder()
        self.MotorC.run_to_rel_pos(position_sp = 0, speed_sp = 0) 
        self.MotorB.run_to_rel_pos(position_sp = self.CM_To_Encoder(right_distance), speed_sp = 200)
        self.MotorB.wait_until_not_moving()
        self.Reset_Encoder()


    def Move_Backward(self):
        position = 450
    
        self.MotorC.run_to_rel_pos(position_sp = -position, speed_sp = -100)
        self.MotorB.run_to_rel_pos(position_sp = -position, speed_sp = -100)
        self.MotorC.wait_until_not_moving()


    def Move_U_Turn(self, speed_B = -100, speed_C = 100):
        pi = 3.14
        u_distance = 11.5 * pi / 2
        self.Reset_Encoder()
        self.MotorB.run_to_rel_pos(position_sp = -self.CM_To_Encoder(u_distance), speed_sp = speed_B)
        self.MotorC.run_to_rel_pos(position_sp = self.CM_To_Encoder(u_distance), speed_sp = speed_C)
        self.MotorB.wait_until_not_moving()
        
        
    def Stop_Motor(self):
        self.MotorB.command = self.MotorB.COMMAND_RESET
        self.MotorC.command = self.MotorC.COMMAND_RESET

    # 일정시간 동안 디버거 멈추기(단위 : 초)
    def Sleep_Motor(self, second = 3):
        self.ev3.time.sleep(second)

    # 매개변수와 UltraSonic의 거리 비교 
    def Check_Distance(self, input_distance):
        ev3_distance = self.ultrasonic.value()

        if ( ev3_distance < input_distance ):
            return True
        else:
            return False

    def Get_MotorB_Encoder(self):
        return self.MotorB.position

    def Get_MotorC_Encoder(self):
        return self.MotorC.position

    def Store_Current_Distance(self, input_distance):
        self.current_distance += input_distance

    # Output 전용 ( Ev3 → User)
    def Encoder_To_CM(self, encoder):
        pi = 3.141592
        distance = 5.6 * pi * encoder / 360
        return distance

    # Input 전용 ( User → Ev3)
    def CM_To_Encoder(self, distance):
        pi = 3.141592
        encoder = distance * 360 / 5.6 / pi
        return encoder

    # Encoder를 0으로 초기화 
    def Reset_Encoder(self):
        self.MotorB.position = 0
        self.MotorC.position = 0
