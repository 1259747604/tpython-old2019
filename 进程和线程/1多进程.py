# windows个辣鸡用不了
import os

""" print('Process (%s) start...' % os.getpid())
# Only works on Unix/Linux/Mac:
pid = os.fork()
if pid == 0:
    print('I am child process (%s) and my parent is %s.' % (os.getpid(), os.getppid()))
else:
    print('I (%s) just created a child process (%s).' % (os.getpid(), pid)) """

# multiprocessing
# 由于Python是跨平台的，自然也应该提供一个跨平台的多进程支持。multiprocessing模块就是跨平台版本的多进程模块
# 创建子进程时，只需要传入一个执行函数和函数的参数，创建一个Process实例，用start()方法启动，这样创建进程比fork()还要简单。
# join()方法可以等待子进程结束后再继续往下运行，通常用于进程间的同步。

from multiprocessing import Process
import os

# 子进程要执行的代码
""" def run_proc(name):
  print('Run child process %s (%s)...' % (name, os.getpid()))

if __name__=='__main__':
  print('Parent process %s.' % os.getpid())
  p = Process(target=run_proc, args=('test',))
  print('Child process will start.')
  p.start()
  p.join()
  print('Child process end.') """

# Pool
# 如果要启动大量的子进程，可以用进程池的方式批量创建子进程

# 代码解读：

# 对Pool对象调用join()方法会等待所有子进程执行完毕，调用join()之前必须先调用close()，调用close()之后就不能继续添加新的Process了。

# 请注意输出的结果，task 0，1，2，3是立刻执行的，而task 4要等待前面某个task完成后才执行，这是因为Pool的默认大小在我的电脑上是4，
# 因此，最多同时执行4个进程。这是Pool有意设计的限制，并不是操作系统的限制。如果改成：p = Pool(5)就可以同时跑5个进程
# 由于Pool的默认大小是CPU的核数，如果你不幸拥有8核CPU，你要提交至少9个子进程才能看到上面的等待效果
""" from multiprocessing import Pool
import os, time, random
def long_time_task(name):
  print('Run task %s (%s)...' % (name, os.getpid()))
  start = time.time()
  time.sleep(random.random() * 3)
  end = time.time()
  print('Task %s runs %0.2f seconds.' % (name, (end - start)))

if __name__=='__main__':
  print('Parent process %s.' % os.getpid())
  p = Pool(4)
  for i in range(5):
    p.apply_async(long_time_task, args=(i,))
  print('Waiting for all subprocesses done...')
  p.close()
  p.join()
  print('All subprocesses done.') """

# 子进程
# 很多时候，子进程并不是自身，而是一个外部进程。我们创建了子进程后，还需要控制子进程的输入和输出。

# subprocess模块可以让我们非常方便地启动一个子进程，然后控制其输入和输出。

# 下面的例子演示了如何在Python代码中运行命令nslookup www.python.org，这和命令行直接运行的效果是一样的
""" import subprocess
print('$ nslookup')
r = subprocess.call(['nslookup', 'www.python.org'])
print('Exit code:', r) """

# 如果子进程还需要输入，则可以通过communicate()方法输入：
""" import subprocess

print('$ nslookup')
p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, err = p.communicate(b'set q=mx\npython.org\nexit\n')
print(output.decode('utf-8', errors='ignore'))
print('Exit code:', p.returncode) """


# 进程通信
# Process之间肯定是需要通信的，操作系统提供了很多机制来实现进程间的通信。
# Python的multiprocessing模块包装了底层的机制，提供了Queue、Pipes等多种方式来交换数据。
# 我们以Queue为例，在父进程中创建两个子进程，一个往Queue里写数据，一个从Queue里读数据：

from multiprocessing import Process, Queue
import os, time, random

# 写数据进程执行的代码:
def write(q):
  print('Process to write: %s' % os.getpid())
  for value in ['A', 'B', 'C']:
    print('Put %s to queue...' % value)
    q.put(value)
    time.sleep(random.random())

# 读数据进程执行的代码:
def read(q):
  print('Process to read: %s' % os.getpid())
  while True:
    value = q.get(True)
    print('Get %s from queue.' % value)

if __name__=='__main__':
  # 父进程创建Queue，并传给各个子进程：
  q = Queue()
  pw = Process(target=write, args=(q,))
  pr = Process(target=read, args=(q,))
  # 启动子进程pw，写入:
  pw.start()
  # 启动子进程pr，读取:
  pr.start()
  # 等待pw结束:
  pw.join()
  # pr进程里是死循环，无法等待其结束，只能强行终止:
  pr.terminate()