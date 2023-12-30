import multiprocessing

from task import Task, TaskStatus


class Constant:
    const_task_id = 0  # 进程id


class Scheduler:
    """
    调度器
    """

    def __init__(self, work_process_num: int = 1):
        # 调度队列
        self.queue = []
        # 进程池
        self.process_pool = []
        # 进程池中进程个数
        self.work_process_num = work_process_num

    def start(self, queue: multiprocessing.Queue) -> None:
        """
        开始调度,内部创建进程池，每个进程绑定执行run方法
        :return:
        """
        for i in range(self.work_process_num):
            # 创建进程
            process = multiprocessing.Process(target=run, args=(queue,))
            # 加入到进程池
            self.process_pool.append(process)
            # 运行进程
            process.start()
            print("创建进程成功")

    def get_runnable_task(self) -> Task or None:
        # 返回一个准备就绪的任务，调度算法为先来先服务
        for task in self.queue:
            if task.status is not TaskStatus.READY:
                # 未就绪状态，则继续向后遍历
                continue
            return task

        # 遍历完未找到准备就绪的任务
        return None

    def add_task(self, task) -> None:
        """
        添加任务
        :return:
        """
        self.queue.append(task)

    def update_task_by_id(self, id: int, parameters: dict) -> None:
        for i in range(len(self.queue)):
            if self.queue[i].id == id:
                self.queue[i].parameters = parameters
                break

    def delete_task_by_id(self, id) -> None:
        for i in range(len(self.queue)):
            if self.queue[i].id == id:
                del self.queue[i]
                break

    def query_task_by_id(self, id) -> Task:
        for i in range(len(self.queue)):
            if self.queue[i].id == id:
                return self.queue[i]

    def query_all_task(self) -> list:
        return self.queue

    def is_stop(self) -> bool:
        """
        调度是否结束，条件判断有待完善
        :return:
        """
        return len(self.queue) == 0

    def __str__(self):
        s = ""
        for i in self.queue:
            s += str(i) + "\n"
        return s


def run(queue: multiprocessing.Queue) -> None:
    """
    子进程内部，在任务队列中取任务执行
    :return:
    """

    while True:
        # 从调度器中获取任务并执行
        scheduler = queue.get()
        task = scheduler.get_runnable_task()

        if task is None:
            # 调度结束
            # 优化，当无任务执行时，进程应该处于idle状态
            queue.put(scheduler)
            break

        # 设置状态为运行态，在里边设显示不出来
        # 执行任务,等待任务执行完毕
        task.run()

        queue.put(scheduler)
        print(task)

    print('子进程执行完毕')
