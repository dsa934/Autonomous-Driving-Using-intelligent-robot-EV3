import rpyc
import io
import os
import cv2
import google.cloud.vision
import Minerva_Func as mf


def Path_Finding(MyCar):

    # opencv 사용(카메라등록)
    cam = cv2.VideoCapture(0)

    # 사용할 이미지 파일 이름(고정된 명칭)
    image_file_name = './image.jpg'

    # 구글 클라우드 비전 사용(클라이언트 가져오기)
    vision_client = google.cloud.vision.ImageAnnotatorClient()
    
    MyCar.Stop_Motor()
    MyCar.Move_Forward()


    while(True):
        
        if ( MyCar.after_u_turn == True ):
            # U턴 백트레이싱 해서 다시 온 상태라면 장애물 체크하기

            if ( MyCar.Check_Distance(130) ):
                # U턴해서 되돌아올 때 또 다시 막혀있는 경우
                MyCar.Move_Right()

                part_back_tracing_index = MyCar.path_list_index - 1
                temp_list = MyCar.path_list[part_back_tracing_index]
                distance = temp_list[1]
                MyCar.Move_Forward_Distance(distance)

                # 2개를 삭제해야 됨 [forward, 거리], [left, 0]
                MyCar.path_list_index -= 1
                del MyCar.path_list[MyCar.path_list_index]
                MyCar.path_list_index -= 1
                del MyCar.path_list[MyCar.path_list_index]
            else:
                temp_list = ['Right', 0]
                MyCar.path_list_index += 1
                MyCar.path_list.append(temp_list)
                MyCar.Move_Forward()
                MyCar.after_u_turn == False

        
        # 주행 중 물체 인식
        if (MyCar.Check_Distance(120)):
            
            # 모터 B가 움직인 거리를 읽어서 임시거리 변수에 넣기
            distance = MyCar.Get_MotorB_Encoder()

            MyCar.Store_Current_Distance(distance)
            MyCar.Stop_Motor()

            # 사진 촬영(파이썬 파일이 저장된 곳에 자동저장)
            ret, img = cam.read()
            cv2.imwrite('image.jpg', img)

            # google cloud vision에 촬영한 이미지를 등록하는 과정
            with io.open(image_file_name, 'rb') as image_file:
                mycontent = image_file.read()

            # google cloud vision에 등록한 이미지 리턴 값
            myimage = google.cloud.vision.types.Image(content=mycontent)

            # 이미지 라벨링 값 받기
            image_response = vision_client.label_detection(image=myimage)

            # 자연어 처리 값 받기
            text_response = vision_client.text_detection(image=myimage)

            # 촬영한 사진에 자연어가 없다면 넘어가기 위한 인덱스 변수
            text_label_index = len(text_response.text_annotations)

            # 이미지 라벨링 값 판독
            for Labels in image_response.label_annotations:

                # 목적지(바다)를 본 경우
                if ( Labels.description == 'sea' ):

                    distance = MyCar.current_distance
                    temp_list = ['Forward', distance]
                    MyCar.path_list_index += 1
                    MyCar.path_list.append(temp_list)
                    MyCar.current_distance = 0

                    # 백트레이싱 준비를 위한 인덱스 변수 등록
                    MyCar.back_trace_list_length = len(MyCar.path_list)
                    MyCar.Move_U_Turn()
                    MyCar.destination = True
                    break

                # 벽 혹은 빌딩을 본 경우
                if ( Labels.description == 'white' or \
                     Labels.description == 'building' or Labels.description == 'window' ):

                    # 현재까지 온 주행거리를 저장
                    distance = MyCar.current_distance
                    temp_list = ['Forward', distance]
                    MyCar.path_list_index += 1
                    MyCar.path_list.append(temp_list)
                    MyCar.current_distance = 0

                    # 좌수법에 의해 왼쪽으로 돌고 리스트에 저장
                    MyCar.Move_Left()

                    if (MyCar.Check_Distance(120)):
                        # 왼쪽 길이 막혀있는 경우

                        MyCar.Move_U_Turn()

                        if (MyCar.Check_Distance(100)):
                            # 양 옆이 막혀있는 경우

                            MyCar.Move_Right()
                            
                            part_back_tracing_index = MyCar.path_list_index - 1
                            temp_list = MyCar.path_list[part_back_tracing_index]
                            distance = MyCar.path_list[part_back_tracing_index][1]

                            # 왔던 거리를 한번 되돌아가야 함
                            MyCar.Move_Forward_Distance(distance)
                            
                            MyCar.path_list_index -= 1
                            del MyCar.path_list[MyCar.path_list_index]
                            MyCar.path_list_index -= 1
                            del MyCar.path_list[MyCar.path_list_index]
                            MyCar.after_u_turn = True

                        else:
                            # 왼쪽 길이 막혀있지만 오른쪽은 뚫려 있는 경우
                            temp_list = ['Right', 0]
                            MyCar.path_list_index += 1
                            MyCar.path_list.append(temp_list)

                            MyCar.Move_Forward()

                    else:
                        # 왼쪽 길이 뚫려 있는 경우 Left를 경로 리스트에 저장
                        temp_list = ['Left', 0]
                        MyCar.path_list_index += 1
                        MyCar.path_list.append(temp_list)
                        MyCar.Move_Forward()
                        break

            if(text_label_index != 0 ):
                # 진행 중에 'PARKING' 텍스트 라벨이 있을 경우
                
                MyCar.Stop_Motor()
                
                if ('PARKING' in text_response.text_annotations[1].description):

                    # parking_list에 저장
                    for i in range(MyCar.path_list_index):
                        temp_list = MyCar.path_list[i]
                        MyCar.parking_list.append(temp_list)

                MyCar.Move_Forward()

            # 목적지에 도착했을 때 전체 while문을 탈출
            if ( MyCar.destination == True ):
                break


def Back_Tracing(MyCar):

    # 백트레이싱에 사용할 인덱스 변수
    back_trace_for_minus = 1
    
    while(True):

        MyCar.Stop_Motor()

        if ( back_trace_for_minus == MyCar.back_trace_list_length + 1 ):
            break

        # 길이고정 - back_trace_for_minus(증가시키는길이)
        temp_list = MyCar.path_list[MyCar.back_trace_list_length - back_trace_for_minus]

        if ( temp_list[0] == 'Left' ):
            MyCar.Move_Right()
                
        elif ( temp_list[0] == 'Forward' ) :
            distance = temp_list[1]
            MyCar.Move_Forward_Distance(distance)

        elif ( temp_list[0] == 'Right' ):
            MyCar.Move_Left()
            
        back_trace_for_minus += 1


def Parking(MyCar):

    # opencv 사용(카메라등록)
    cam = cv2.VideoCapture(0)

    # 구글 클라우드 비전 사용(클라이언트 가져오기)
    vision_client = google.cloud.vision.ImageAnnotatorClient()
    image_file_name = './image.jpg'

    # 사용할 이미지 파일 이름(고정된 명칭)
    parking_length = len(MyCar.parking_list)

    MyCar.Move_U_Turn()
    
    while(True):

        MyCar.Stop_Motor()
    
        for i in range(parking_length):
            temp_list = MyCar.parking_list[i]

            if ( temp_list[0] == 'Left' ):
                MyCar.Move_Left()

            elif ( temp_list[0] == 'Forward' ):
                distance = temp_list[1]
                MyCar.Move_Forward_Distance(distance)

            elif ( temp_list[0] == 'Right' ):
                MyCar.Move_Right()
                
        break

    # 사진 촬영(Parking left, Parking right 판단)
    ret, img = cam.read()
    cv2.imwrite('image.jpg', img)

    with io.open(image_file_name, 'rb') as image_file:
        mycontent = image_file.read()

    myimage = google.cloud.vision.types.Image(content=mycontent)

    text_response = vision_client.text_detection(image=myimage)

    if ('right' in text_response.text_annotations[2].description):
        MyCar.Move_Left()
        MyCar.Move_Backward()

    if ('left' in text_response.text_annotations[2].description):
        MyCar.Move_Right()
        MyCar.Move_Backward()

# 메인 정의
def Main():
    MyCar = mf.Minerva()

    Path_Finding(MyCar)
    Back_Tracing(MyCar)
    Parking(MyCar)

# 실행 
Main()

