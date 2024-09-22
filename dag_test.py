"""DAG for test task."""

from datetime import datetime, timezone

from airflow.decorators import dag, task
from airflow.models import TaskInstance, Variable
from airflow.operators.python import get_current_context
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes import client

from tools import DEFAULT_IMAGE_PULL_POLICY, IMAGE_ENVS, STARTUP_TIMEOUT, CreatorDAG, EnvironmentName


class TestCreator(CreatorDAG):
    """Test Creator."""

    def __init__(self, environment: EnvironmentName):
        """Initialize the creator.

        Args:
            environment (EnvironmentName): The environment name
        """
        super().__init__(environment)
        self.tags = ["test"]
        self.dag_id = "test-prod" if self.environment == EnvironmentName.PROD else "test-dev"
        self.description = "The test workflow"

    def create(self):
        """Create DAG for the test workflow."""
        @dag(
            dag_id=self.dag_id,
            description=self.description,
            schedule=None,
            start_date=datetime(year=2024, month=9, day=22, tzinfo=timezone.utc),
            catchup=False,
            default_args={
                "owner": "airflow",
                "retries": 0,
            },
            tags=self.tags,
        )
        def test_dag_generator(
            image: str = Variable.get(
                "test_image_prod" if self.environment == EnvironmentName.PROD else "test_image_dev"
            ),
            input_param: str = "example",
        ):
            """Generate a DAG for test workflow.

            Args:
                image (str): The image to be used for the KubernetesPodOperator.
                input_param (str): The input parameter.
            """
            test_operator = KubernetesPodOperator(
                task_id="test-task",
                image=image,
                namespace="airflow",
                name="test-pod-prod" if self.environment == EnvironmentName.PROD else "test-pod-dev",
                env_vars=IMAGE_ENVS,
                cmds=[
                    "python",
                    "main.py",
                    "--input_param",
                    "{{ params.input_param }}",
                ],
                in_cluster=True,
                is_delete_operator_pod=True,
                get_logs=True,
                startup_timeout_seconds=STARTUP_TIMEOUT,
                image_pull_policy=DEFAULT_IMAGE_PULL_POLICY,
                do_xcom_push=True,
                pool="PROD" if self.environment == EnvironmentName.PROD else "DEV",
                container_resources=client.V1ResourceRequirements(
                    requests={"cpu": "1000m", "memory": "2G"},
                    limits={"cpu": "2000m", "memory": "8G"},
                ),
            )

            @task(task_id="print-task")
            def print_result(task_id: str) -> None:
                """Print result."""
                context = get_current_context()
                ti: TaskInstance = context["ti"]
                result = ti.xcom_pull(task_ids=task_id, key="return_value")
                print(f"Result: {result}")

            print_result_operator = print_result("test-task")

            test_operator >> print_result_operator

        return test_dag_generator()

# create DAGs for each environment
test_prod_dag = TestCreator(
    environment=EnvironmentName.PROD,
).create()

test_dev_dag = TestCreator(
    environment=EnvironmentName.DEV,
).create()
