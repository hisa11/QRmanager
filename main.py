import subprocess
import threading

def run_script(script_path):
  try:
    subprocess.run(["python", script_path], check=True)
  except subprocess.CalledProcessError as e:
    print(f"Error running {script_path}: {e}")

if __name__ == "__main__":
  thread1 = threading.Thread(target=run_script, args=("pyfile/app.py",))
  thread2 = threading.Thread(target=run_script, args=("pyfile/main.py",))

  thread1.start()
  thread2.start()

  thread1.join()
  thread2.join()