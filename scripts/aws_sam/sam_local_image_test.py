import json
import subprocess

EXPECTED_RESP = {
    "hints": [
        {
            "word": "request",
            "start_position": 15,
            "end_position": 22,
            "ranking": 1395,
            "definition": "the verbal act of requesting",
            "part_of_speech": "NN",
        }
    ]
}

EVENT_PATHS = [
    "scripts/aws_sam/sam_local_invoke_event_v1.json",
    "scripts/aws_sam/sam_local_invoke_event_latest.json",
]

ENV_VARS_PATH = "scripts/aws_sam/test_env_vars.json"


def get_sam_local_invoke_output(event_path):
    sam_invoke_cmd = f"sam local invoke SmartWordHintsFunction -e {event_path} --env-vars {ENV_VARS_PATH}"
    process = subprocess.Popen(sam_invoke_cmd.split(), stdout=subprocess.PIPE)
    output, _ = process.communicate()
    return output


if __name__ == "__main__":
    for event_path in EVENT_PATHS:
        assert (
            json.loads(json.loads(get_sam_local_invoke_output(event_path))["body"])
            == EXPECTED_RESP
        )
