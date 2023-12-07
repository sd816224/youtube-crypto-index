import subprocess
import os
import time

current_dir = os.path.dirname(os.path.realpath(__file__))
compose_path = os.path.join(current_dir, "docker-compose-dev.yaml")

subprocess.run(
    ['docker', 'compose', '-f', compose_path, 'up','-d'], check=False
)

def within_dev_postgres(func):
    try:
        max_attempts = 5
        for _ in range(max_attempts):
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "local-dev-postgres",
                    "pg_isready",
                    "-h",
                    "localhost",
                    "-U",
                    "testdb",
                ],
                stdout=subprocess.PIPE,
                check=False,
            )
            if result.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise TimeoutError(
                """PostgreSQL container is not responding,
                cancelling fixture setup."""
            )
        func()
    finally:
        subprocess.run(
            ['docker', 'compose', '-f', compose_path, 'down'], check=False
        )

@within_dev_postgres
def say_hello():
    time.sleep(0.1)
    print('hello')


say_hello()
