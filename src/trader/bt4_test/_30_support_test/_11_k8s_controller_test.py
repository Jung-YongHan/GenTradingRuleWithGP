import unittest
import paramiko
import docker
import time

from bt4 import GlobalProperties
from bt4.utils.container_helper import ContainerHelper
from kubernetes import client, config
# from __future__ import print_function
import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
""" 참고 자료: https://github.com/kubernetes-client/python """


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        config.load_kube_config()

        # self.init_default()
        # self.init_remote()

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """

    def test_doSomthing(self):
        self.init_default()

    def init_default(self):
        config.load_kube_config()

        self.v1 = client.CoreV1Api()
        print("Listing pods with their IPs:")
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def init_remote(self):
        print("init_remote")
        pass

    def test_get_pod_list(self):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        namespace = "default"
        pods = v1.list_namespaced_pod(namespace)
        for pod in pods.items:
            print(pod.metadata.name)
        # v1.close()

    def test_delete_pod(self):

        # 쿠버네티스 API에 접근하기 위한 설정을 로드합니다
        config.load_kube_config()

        # CoreV1Api 인스턴스를 생성합니다
        v1 = client.CoreV1Api()

        # 삭제할 파드의 이름과 네임스페이스를 지정합니다
        # pod_name = "your-pod-name"
        namespace = "default"

        # 지정된 네임스페이스의 파드 목록을 가져옵니다.
        pods = v1.list_namespaced_pod(namespace)

        # 파드 이름을 출력합니다.
        for pod in pods.items:
            print(pod.metadata.name)
            # 파드를 삭제합니다
            v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)

            print(f"Pod {pod.metadata.name} in namespace {namespace} deleted")

    # @unittest.skip("Tested")
    def test_check_status(self):
        v1 = client.BatchV1Api()

        pass

    def test_get_resource(self):
        configuration = kubernetes.client.Configuration()
        # Configure API key authorization: BearerToken
        configuration.api_key['authorization'] = 'YOUR_API_KEY'
        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.host = "http://localhost"

        # Enter a context with an instance of the API kubernetes.client
        with kubernetes.client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = kubernetes.client.BatchV1Api(api_client)

            try:
                api_response = api_instance.get_api_resources()
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling BatchV1Api->get_api_resources: %s\n" % e)

    def test_run_pod(self):
        # config.load_kube_config()

        run_type = "backtestor"
        target_id = "121"

        # 쿠버네티스 API 클라이언트 생성
        v1 = client.BatchV1Api()

        # 잡 정의
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name="k8s-test-container4"),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=target_id,
                                image=GlobalProperties.CONTAINER_IMAGE_NAME,
                                command=["python", GlobalProperties.CONTAINER_PYTHON_FILE, run_type, "-bt_id", target_id]
                            )
                        ],
                        image_pull_secrets=[client.V1LocalObjectReference(name="jg-docker-hub-secret")],
                        restart_policy="Never"
                    )
                )
            )
        )

        # 잡 생성
        response = v1.create_namespaced_job(
            body=job,
            namespace="default"
        )

        print("Job created. status='%s'" % str(response.status))
        pass

    def create_mysql_pod(api_instance, pod_name, namespace='default'):
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name
            },
            "spec": {
                "containers": [{
                    "name": "mysql",
                    "image": "mysql:5.7",
                    "env": [
                        {"name": "MYSQL_ROOT_PASSWORD", "value": "yourpassword"}
                    ]
                }]
            }
        }

        api_instance.create_namespaced_pod(namespace=namespace, body=pod_manifest)
        print(f"Pod {pod_name} created")


    def run_replicaset(self):
        pass


if __name__ == '__main__' :
    unittest.main()
