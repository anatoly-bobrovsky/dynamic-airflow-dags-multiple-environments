"""Environment variables for images."""

from airflow.models import Variable

IMAGE_ENVS = {
    "ENV_EXAMPLE": Variable.get("env_example"),
}
