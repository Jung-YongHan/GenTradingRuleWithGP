from bt4 import GlobalProperties
from bt4.utils.mylog import init_log
from abc import ABC, abstractmethod
import docker
import time

log = init_log()


class SingletonInstane:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance


class ContainerHelper(SingletonInstane):
    def __init__(self):
        if GlobalProperties.CONTAINER_TYPE == "k8s":
            self.helper = K8sController().instance()

        elif GlobalProperties.CONTAINER_TYPE == "docker":
            self.helper = DockerController().instance()

    def run_backtesting(self, target_id):
        run_type = "bt"
        return self.helper.run_container(run_type, target_id)

    def check_backtesting_status(self, target_id) -> str:
        run_type = "bt"
        return self.helper.check_status(run_type, target_id)

    def run_live_trading(self, target_id):
        run_type = "live_trading"  # todo 명칭 변경 필요
        return self.helper.run_container(run_type, target_id)

    def check_live_trading(self, target_id) -> str:
        run_type = "live_trading"  # todo 명칭 변경 필요
        return self.helper.check_status(run_type, target_id)

    def run_forwardtesting(self, target_id):
        run_type = "forward_testing"  # todo 명칭 변경 필요
        return self.helper.run_container(run_type, target_id)

    def check_forwardtesting(self, target_id) -> str:
        run_type = "forward_testing"  # todo 명칭 변경 필요
        return self.helper.check_status(run_type, target_id)

    def check_status(self, run_type, target_id) -> str:
        return self.helper.check_status(run_type, target_id)

    def run_container(self, run_type, target_id) -> bool:
        return self.helper.run_container(run_type, target_id)


class DockerController(SingletonInstane):
    
    def __init__(self):
        self.set_server(GlobalProperties.CONTAINER_SERVER_1)
        # 원격 Docker 서버의 주소 및 포트
        remote_docker_url = f'tcp://{self.ip}:2375'

        # Docker 클라이언트 설정 (TLS 인증 없음)
        self.client = docker.DockerClient(base_url=remote_docker_url)

    def set_server(self, server_ip: str) -> None:

        if server_ip == GlobalProperties.CONTAINER_SERVER_2:
            self.ip = GlobalProperties.CONTAINER_SERVER_2
            self.id = GlobalProperties.CONTAINER_SERVER_2_USERNAME

        elif server_ip == GlobalProperties.CONTAINER_SERVER_3:
            self.ip = GlobalProperties.CONTAINER_SERVER_3
            self.id = GlobalProperties.CONTAINER_SERVER_3_USERNAME

        else:
            if server_ip != GlobalProperties.CONTAINER_SERVER_1:
                log.warning("잘못된 값이 입력되어 초기값으로 서버를 세팅합니다.")

            self.ip = GlobalProperties.CONTAINER_SERVER_1
            self.id = GlobalProperties.CONTAINER_SERVER_1_USERNAME

    # def run_container(self, run_type, target_id):
    #     client = paramiko.SSHClient()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #
    #     client.connect(self.ip, username=self.id, password=GlobalProperties.CONTAINER_SERVER_PASSWORD)
    #     command = (f"docker run --network {GlobalProperties.CONTAINER_NETWORK_NAME} -d "
    #                f"--name {target_id} "
    #                f"{GlobalProperties.CONTAINER_IMAGE_NAME} "
    #                f"python {GlobalProperties.CONTAINER_PYTHON_FILE} "
    #                f"{run_type} -stgy_id {target_id}")
    #
    #     print(command)
    #     stdin, stdout, stderr = client.exec_command(command)
    #     # 결과 출력
    #     print(stdout.read().decode())
    #     print(stderr.read().decode())
    #
    #     stdin, stdout, stderr = client.exec_command(f"docker ps | grep {target_id}")
    #
    #     print(stdout.read().decode())
    #     print(stderr.read().decode())
    #
    #     # 연결 종료
    #     client.close()

    def get_all_container_list(self) -> list:
        return self.client.containers.list()

    # 컨테이너 상태 확인
    def check_status(self, run_type, target_id) -> str:
        try:
            container = self.client.containers.get(run_type, target_id)
            return container.status
        except Exception as e:
            print(e)
            return None

    def run_container(self, run_type, target_id) -> bool:
        # 컨테이너 생성 및 실행
        try:
            container = self.client.containers.run(image=f"{GlobalProperties.CONTAINER_IMAGE_NAME}",
                                                   command=f"python {GlobalProperties.CONTAINER_PYTHON_FILE} {run_type} "
                                                           f"-tid {target_id}",
                                                   detach=True,
                                                   name=f"{run_type}_{target_id}",
                                                   network=GlobalProperties.CONTAINER_NETWORK_NAME,
                                                   auto_remove=True)

            if (container.status == "running") or (container.status == "created"):
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return False

    def stop_container(self, run_type, target_id) -> None:
        container= self.client.containers.get(f"{run_type}_{target_id}")
        container.stop()

    def remove_container(self, run_type, target_id) -> None:
        container= self.client.containers.get(f"{run_type}_{target_id}")
        container.remove()


class K8sController(SingletonInstane):
    def __init__(self):
        self.config = '/path/to/config'

    def run_container(self, run_type, target_id):
        print("k8s - run_container")
        pass

    def check_status(self, run_type, target_id):
        print("k8s - check_status")
        pass

