import unittest
import paramiko
import docker
import time

from bt4 import GlobalProperties
from bt4.utils.container_helper import ContainerHelper

""" 참고 자료: https://docker-py.readthedocs.io/en/stable/client.html """


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        self.hostname = '192.168.1.173'  # 원격 서버 IP 혹은 호스트네임
        self.username = 'ssel2'  # 원격 서버 사용자 이름
        self.password = 'dusrntlf512'  # 원격 서버 비밀번호


        self.init_paramiko()

        #####################################################################################

        self.init_default()
        self.init_remote()


    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        self.client_ssh.close()
        self.client_docker.close()

    def init_paramiko(self):
        # SSH 클라이언트 인스턴스 생성
        self.client_ssh = paramiko.SSHClient()

        # 서버 접속 정보 설정
        self.client_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 원격 서버에 연결
        self.client_ssh.start_websocket(self.hostname, username=self.username, password=self.password)

    def init_default(self):
        # 로컬 Docker 환경으로 연결
        self.client = docker.from_env()

    def init_remote(self):
        # 원격 Docker 서버의 주소 및 포트
        remote_docker_url = f'tcp://{GlobalProperties.CONTAINER_SERVER_1}:2375'

        # Docker 클라이언트 설정 (TLS 인증 없음)
        self.client_docker = docker.DockerClient(base_url=remote_docker_url)

    # @unittest.skip("Tested")
    def test_remote_docker_control(self):

        # Docker 컨테이너 실행 명령어
        command = 'docker run -d hello-world'  # 여기서 'your_docker_image'를 원하는 이미지로 대체

        # 명령어 실행
        stdin, stdout, stderr = self.client_ssh.exec_command(command)

        # 결과 출력
        print(stdout.read().decode())
        print(stderr.read().decode())

        # 연결 종료
        self.client_ssh.close()

    def test_remote_docker_control2(self):

        run_type = "bt"
        strategy_id = "0ab6a68d-ce6a-4eaa-9979-d0ce62f4854b"

        # 컨테이너 생성 및 실행
        container = self.client_docker.containers.run(image=f"{GlobalProperties.CONTAINER_IMAGE_NAME}",
                                          command= f"python {GlobalProperties.CONTAINER_PYTHON_FILE} {run_type} "
                                                   f"-tid {strategy_id}",
                                          detach=True,
                                          name=strategy_id,
                                          network=GlobalProperties.CONTAINER_NETWORK_NAME)

        # 컨테이너 상태 확인
        def check_container_status():
            cont = self.client_docker.containers.get(container.id)
            return cont.status

        # 이벤트 처리
        def handle_event():
            status = check_container_status()
            print(f"Container status: {status}")

        # # 컨테이너 목록 출력
        # for container in client.containers.list():
        #     print(container.attrs)

        # 메인 루프
        try:
            while True:
                handle_event()
                time.sleep(10)  # 10초마다 상태 확인

        except KeyboardInterrupt:
            print("Monitoring stopped.")

        # 컨테이너 정리
        container.stop()
        container.remove()

    def test_check_status(self):
        run_type = "backtestor"
        target_id = "19"
        isSuccess = ContainerHelper.instance().run_container(run_type, target_id)
        print(isSuccess)
        # ContainerHelper().run_container(run_type, strategy_id)

    def test_get_container(self):
        # 컨테이너 상태 확인
        def check_container_status(name):
            cont = self.client_docker.containers.get(name)
            return cont.status

        name = "a"
        print(check_container_status(name))

    def test_remote_docker_stop(self):

        container = self.client_docker.containers.run(image=f"{GlobalProperties.CONTAINER_IMAGE_NAME}",
                                                      command=f"python ./shutdown_hook.py",
                                                      detach=True,
                                                      name='shutdown_hook',
                                                      network=GlobalProperties.CONTAINER_NETWORK_NAME,
                                                      volumes={
                                                                '/home/ssel1/PycharmProjects/bt4_trader/spiketesting/_12_shutdown_hook/_01_shutdown_hook.py':
                                                                    {  # 호스트 시스템의 경로
                                                                        'bind': '/app/shutdown_hook.py',  # 컨테이너 내의 경로
                                                                        'mode': 'rw'  # 읽기/쓰기 모드, 읽기 전용으로 하려면 'ro' 사용
                                                                    }
                                                            }
                                                      )

        time.sleep(2)
        container.stop()
        print(container.logs())
        container.remove()



if __name__ == '__main__' :
    unittest.main()
