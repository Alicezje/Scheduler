class TaskStatus:
    """
    任务
    """
    READY = 0  # 未运行(准备就绪)
    EXEC = 1  # 正在运行
    TERM = 2  # 运行结束
    EXCEPT = 3  # 异常结束

    # 依赖于上边定义的值
    list_status_str = ["READY", "EXEC", "TERM", "EXCEPT"]
    list_status_color = ["color: black;", "color: blue;", "color: green;", "color: red;"]

    def get_str(status) -> str:
        return TaskStatus.list_status_str[status]

    def get_color(status) -> str:
        return TaskStatus.list_status_color[status]


class Task:
    """
    任务
    """

    def __init__(self, id: int, name: str, parameters: dict, run_func: None or callable,
                 status: TaskStatus = TaskStatus.READY):
        # 任务id
        self.id = id
        # 任务名称
        self.name = name
        # 任务状态
        self.status: TaskStatus = status
        # 执行函数
        self.run_func = run_func
        # 参数列表
        self.parameters = parameters

    def run(self):
        self.status = TaskStatus.EXEC
        self.run_func(self.parameters)
        self.status = TaskStatus.TERM

    def __str__(self):
        return "[id:" + str(self.id) \
            + " name: " + str(self.name) \
            + " status: " + TaskStatus.get_str(self.status) \
            + "]"
