import subprocess
import json
import time
import asyncio
import datetime

from loguru import logger


IMAGE_NAME = "mahjong-client-v2"


class Client:
    def __init__(self, player_id: int, zip_file_path: str):
        self.player_id = player_id
        self.zip_file_path = zip_file_path
        self.proc = self.init_container_process()

    def init_container_process(self):
        cmd = [
            "docker",
            "run",
            "-d",
            "--rm",
            "--memory", "4G",
            "--cpus", "4",
            "--network", "none",
            "--name", f"player{self.player_id}",
            IMAGE_NAME,
            "sleep",
            "infinity",
        ]
        proc = subprocess.Popen(
            cmd,
            bufsize=0,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        proc.wait()

        # /workspace にファイルを転送して bot.zip として保存する
        proc_copy = subprocess.Popen(
            [
                "docker",
                "cp",
                self.zip_file_path,
                f"player{self.player_id}:/workspace/bot.zip",
            ],
            bufsize=0,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            outs, errs = proc_copy.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc_extract.kill()

        # bot.zip を展開する
        proc_extract = subprocess.Popen(
            [
                "docker",
                "exec",
                f"player{self.player_id}",
                "unzip",
                "bot.zip",
            ],
            bufsize=0,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            outs, errs = proc_extract.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc_extract.kill()

        # bot.zip を削除する
        proc_extract = subprocess.Popen(
            [
                "docker",
                "exec",
                f"player{self.player_id}",
                "rm",
                "-f",
                "bot.zip",
            ],
            bufsize=0,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            outs, errs = proc_extract.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc_extract.kill()

        # bot.py を実行する
        proc_main = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                f"player{self.player_id}",
                "/workspace/.pyenv/shims/python",
                "-u",
                "bot.py",
                f"{self.player_id}",
            ],
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        return proc_main

    def react(self, events: str) -> str:
        self.proc.stdin.write((events + "\n").encode("utf8"))
        self.proc.stdin.flush()
        resp = self.proc.stdout.readline()
        return resp.decode("utf8").strip()


async def verify_bot(zipfile_path, timeout) -> str:
    logger.info("Step1")

    # start_game に対して none を返す
    try:
        loop = asyncio.get_running_loop()
        res = await asyncio.wait_for(
            loop.run_in_executor(None, do_test_1, zipfile_path), timeout=timeout
        )
        if res is not True:
            return '{"status":2,"msg":"Validation failed in test case1."}'
    except asyncio.TimeoutError:
        return '{"status":2,"msg":"Timeout in test case1."}'

    logger.info("Step2")  # player_id=0 として dahai を選択できる
    try:
        loop = asyncio.get_running_loop()
        res = await asyncio.wait_for(
            loop.run_in_executor(None, do_test_2, zipfile_path), timeout=timeout
        )
        if res is not True:
            return '{"status":3,"msg":"Validation failed in test case2."}'
    except asyncio.TimeoutError:
        return '{"status":3,"msg":"Timeout in test case2."}'

    logger.info("Step4")  # player_id=1 として pon or none を選択できる
    try:
        loop = asyncio.get_running_loop()
        res = await asyncio.wait_for(
            loop.run_in_executor(None, do_test_4, zipfile_path), timeout=timeout
        )
        if res is not True:
            return '{"status":4,"msg":"Validation failed in test case3."}'
    except asyncio.TimeoutError:
        return '{"status":4,"msg":"Timeout in test case3."}'


def do_test_1(zipfile_path):
    try:
        target_client = Client(0, zipfile_path)
        resp = target_client.react('[{"type":"start_game","id":0}]')
        resp = json.loads(resp)
        clean_containers()
        return (resp["type"] == "none")
    except Exception:
        return False


def do_test_2(zipfile_path):
    try:
        target_client = Client(0, zipfile_path)
        resp = target_client.react('[{"type":"start_game","id":0}]')
        resp = json.loads(resp)
        assert resp["type"] == "none"
        resp = target_client.react('[{"type":"start_kyoku","bakaze":"E","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"dora_marker":"7s","scores":[2500,2500,2500,2500],"tehais":[["3m","4m","3p","5pr","7p","9p","4s","4s","5sr","7s","7s","W","N"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":0,"pai":"3m"}]')
        resp = json.loads(resp)
        assert resp["type"] == "dahai"
        assert resp["actor"] == 0
        assert resp["pai"] in ["3m", "4m", "3p", "5pr", "7p", "9p", "4s", "5sr", "7s", "W", "N"]
        clean_containers()

        return True
    except Exception:
        return False


def do_test_4(zipfile_path):
    try:
        target_client = Client(1, zipfile_path)
        resp = target_client.react('[{"type":"start_game","id":1}]')
        resp = json.loads(resp)
        assert resp["type"] == "none"
        resp = target_client.react('[{"type":"start_kyoku","bakaze":"E","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"dora_marker":"7s","scores":[2500,2500,2500,2500],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["3m","4m","3p","5pr","7p","9p","4s","4s","5sr","7s","7s","W","N"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":0,"pai":"?"},{"type":"dahai","actor":0,"pai":"7s","tsumogiri":false}]')
        # ポンするか選択する
        assert len(resp) > 8
        resp = json.loads(resp)
        assert resp["type"] in ["none", "pon"]
        clean_containers()
        return True
    except Exception:
        return False


def clean_containers():
    proc_main = subprocess.Popen(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"ancestor={IMAGE_NAME}",
            "--format",
            "{{.ID}}",
        ],
        bufsize=0,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    instance_ids = [id_ for id_ in proc_main.stdout.read().decode("utf8").split("\n") if len(id_) == 12]
    logger.info(f"{str(instance_ids)}")
    proc_main.wait()

    for instance_id in instance_ids:
        proc_main = subprocess.Popen(
            [
                "docker",
                "rm",
                "-f",
                instance_id,
            ],
            bufsize=0,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        proc_main.wait()


def main():
    zipfile_path = "./your_bot.zip"

    logger.info("Clean containers: start of validation")
    clean_containers()
    resp = asyncio.run(verify_bot(zipfile_path, 20))
    logger.info(f"Response: {str(resp)}")

    logger.info("Clean containers: end of validation")
    clean_containers()


if __name__ == "__main__":
    main()
