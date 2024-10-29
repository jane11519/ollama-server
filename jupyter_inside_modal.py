# ---
# args: ["--timeout", 10]
# ---

# ## Overview
#
# Quick snippet showing how to connect to a Jupyter notebook server running inside a Modal container,
# especially useful for exploring the contents of Modal Volumes.
# This uses [Modal Tunnels](https://modal.com/docs/guide/tunnels#tunnels-beta)
# to create a tunnel between the running Jupyter instance and the internet.
#
# If you want to your Jupyter notebook to run _locally_ and execute remote Modal Functions in certain cells, see the `basic.ipynb` example :)

import os
import subprocess
import time

import modal

app = modal.App(
    image=modal.Image.debian_slim().pip_install(
        "jupyter"
    ).apt_install(
        "git"
    )
)
volume = modal.Volume.from_name(
    "GGUF-volume", create_if_missing=True
)

GGUF_DIR = "/GGUF"
JUPYTER_TOKEN = "12345678"  # Change me to something non-guessable!


@app.function(volumes={GGUF_DIR: volume})
def seed_volume():
    doneload_url = "https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF/resolve/main/Qwen2.5-14B-Instruct-Q4_K_M.gguf"
    file_name = doneload_url.split("/")[-1] # Qwen2.5-14B-Instruct-Q4_K_M.gguf
    if not os.path.isfile(os.path.join(GGUF_DIR, file_name)):
        subprocess.run(["cd", GGUF_DIR])
        subprocess.run(["curl", "-o", os.path.join(GGUF_DIR, file_name), "-L", doneload_url])
    
    content = """FROM /GGUF/Qwen2.5-14B-Instruct-Q4_K_M.gguf
    TEMPLATE "{{ if .System }}<|im_start|>system
    {{ .System }}<|im_end|>
    {{ end }}{{ if .Prompt }}<|im_start|>user
    {{ .Prompt }}<|im_end|>
    {{ end }}<|im_start|>assistant
    {{ .Response }}<|im_end|>"
    PARAMETER num_ctx 8192
    PARAMETER stop "<|im_end|>"
    PARAMETER stop "<|im_start|>"
    """
    # Write the content to the file
    modelfile_name = 'Modelfile'
    with open(os.path.join(GGUF_DIR, modelfile_name), 'w') as file:
        file.write(content)
    
    subprocess.run(["cd", GGUF_DIR])
    subprocess.run(["git", "clone", "https://github.com/jane11519/ollama-server.git"])

    volume.commit()


# This is all that's needed to create a long-lived Jupyter server process in Modal
# that you can access in your Browser through a secure network tunnel.
# This can be useful when you want to interactively engage with Volume contents
# without having to download it to your host computer.


@app.function(concurrency_limit=1, volumes={GGUF_DIR: volume}, timeout=1_500)
def run_jupyter(timeout: int):
    jupyter_port = 8888
    subprocess.run(["cd", GGUF_DIR])
    with modal.forward(jupyter_port) as tunnel:
        jupyter_process = subprocess.Popen(
            [
                "jupyter",
                "notebook",
                "./",
                "--no-browser",
                "--allow-root",
                "--ip=0.0.0.0",
                f"--port={jupyter_port}",
                "--NotebookApp.allow_origin='*'",
                "--NotebookApp.allow_remote_access=1",
            ],
            env={**os.environ, "JUPYTER_TOKEN": JUPYTER_TOKEN},
        )

        print(f"Jupyter available at => {tunnel.url}")

        try:
            end_time = time.time() + timeout
            while time.time() < end_time:
                time.sleep(5)
            print(f"Reached end of {timeout} second timeout period. Exiting...")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            jupyter_process.kill()


@app.local_entrypoint()
def main(timeout: int = 10_000):
    # Write some images to a volume, for demonstration purposes.
    seed_volume.remote()
    # Run the Jupyter Notebook server
    run_jupyter.remote(timeout=timeout)


# Doing `modal run jupyter_inside_modal.py` will run a Modal app which starts
# the Juypter server at an address like https://u35iiiyqp5klbs.r3.modal.host.
# Visit this address in your browser, and enter the security token
# you set for `JUPYTER_TOKEN`.