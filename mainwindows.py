import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLabel, \
    QPushButton, QDialog, QLineEdit, QTextEdit, QCheckBox
from pyqt5_plugins.examplebuttonplugin import QtGui
from PyQt5.QtCore import pyqtSignal, QThread

from scheduler import Task, TaskStatus, Scheduler, Constant
import main

import multiprocessing
import threading
from functools import partial


class TaskItemWidget(QWidget):
    """
    单个任务信息
    """

    def __init__(self, task: Task):
        super().__init__()

        # 复选框
        layout = QHBoxLayout()
        self.setLayout(layout)

        # self.task_checkbox = QCheckBox()
        self.id = task.id
        self.name = task.name
        self.status = task.status
        self.parameters = task.parameters

        # layout.addWidget(self.task_checkbox)  # 复选框
        layout.addWidget(QLabel(str(self.id)))  # 任务id
        layout.addWidget(QLabel(self.name))  # 任务名称
        # 任务状态
        status_label = QLabel(TaskStatus.get_str(self.status))
        status_label.setStyleSheet(TaskStatus.get_color(self.status))
        layout.addWidget(status_label)
        layout.addWidget(QLabel(str(self.parameters)))  # 参数列表


class AddTaskDialog(QDialog):
    # 定义信号
    add_task_dialog_closed = pyqtSignal(Task)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加任务")
        self.resize(660, 450)

        # 任务名称
        self.task_name_input = QLineEdit()

        # 解析参数，这里目前固定写，需要改成从yaml中加载
        # 学习率
        self.task_lr_input = QLineEdit()
        self.task_lr_input.setValidator(QtGui.QDoubleValidator())  # 设置只能输入double类型的数
        # batch size
        self.task_batch_size_input = QLineEdit()
        self.task_batch_size_input.setValidator(QtGui.QDoubleValidator())  # 设置只能输入double类型的数

        save_button = QPushButton("保存")

        # 保存按钮点击事件
        save_button.clicked.connect(self.save_task)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("任务名称:"))
        layout.addWidget(self.task_name_input)

        layout.addWidget(QLabel("lr:"))
        layout.addWidget(self.task_lr_input)

        layout.addWidget(QLabel("batch_size:"))
        layout.addWidget(self.task_batch_size_input)

        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_task(self):
        # 获取输入框中各个值
        # 任务id
        id = Constant.const_task_id
        Constant.const_task_id = Constant.const_task_id + 1

        name = self.task_name_input.text()

        # 从输入框中解析出信息，加入到参数列表中
        parameter = {
            "lr": float(self.task_lr_input.text()),
            "batch_size": float(self.task_batch_size_input.text())
        }

        # 运行函数先写死
        task = Task(id, name, parameter, main.test_func)

        # 发射信号
        self.add_task_dialog_closed.emit(task)

        # 值为空提示信息不能为空
        main_window.add_task_item(TaskItemWidget(task))
        self.close()


class RefreshThread(QThread):
    scheduler_received = pyqtSignal(object)

    def __init__(self, queue: multiprocessing.Queue):
        super().__init__()
        self.queue = queue

    def run(self) -> None:
        # while True:
        scheduler = self.queue.get()
        self.scheduler_received.emit(scheduler)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1360, 900)

        self.task_list_widget = QListWidget()
        self.add_button = QPushButton("添加任务")
        self.delete_button = QPushButton("删除任务")
        self.start_button = QPushButton("开始调度")
        self.refresh_button = QPushButton("刷新")
        self.stop_button = QPushButton("停止")
        self.close_button = QPushButton("关闭")

        # 连接信号
        self.add_button.clicked.connect(self.show_add_task_dialog)
        self.delete_button.clicked.connect(self.delete_selected_tasks)
        self.start_button.clicked.connect(self.start_scheduler_func)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.close_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.task_list_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        parameter = {
            "lr": 0.1,
            "batch_size": 32
        }
        # 值为空提示信息不能为空

        task_1 = Task(0, "name", parameter, main.test_func)
        task_2 = Task(1, "hello", parameter, main.test_func)
        task_3 = Task(2, "world", parameter, main.test_func)

        # 调度器
        self.scheduler = Scheduler(work_process_num=1)

        self.scheduler.add_task(task_1)
        self.scheduler.add_task(task_2)
        self.scheduler.add_task(task_3)

        self.add_task_item(TaskItemWidget(task_1))
        self.add_task_item(TaskItemWidget(task_2))
        self.add_task_item(TaskItemWidget(task_3))

        # 放入共享队列中
        manager = multiprocessing.Manager()
        self.queue = manager.Queue()

        self.queue.put(self.scheduler)
        # ---------------------------------------

        self.refresh_button.clicked.connect(self.start_refresh_thread)
        self.refresh_thread = RefreshThread(self.queue)
        self.refresh_thread.scheduler_received.connect(self.update_ui_with_scheduler)

    def start_scheduler_func(self):
        self.scheduler.start(self.queue)

    def start_refresh_thread(self):
        print("点击刷新按钮")
        self.refresh_thread.run()

    def update_ui_with_scheduler(self, scheduler):
        # 在主线程中更新界面的代码
        self.task_list_widget.clear()
        for item_task in scheduler.query_all_task():
            # print(item_task)
            item_widget = TaskItemWidget(item_task)
            self.add_task_item(item_widget)

        self.queue.put(scheduler)

    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        dialog.add_task_dialog_closed.connect(self.handle_dialog_closed)
        dialog.exec_()

    def handle_dialog_closed(self, task: Task):
        self.scheduler.add_task(task)
        print(self.scheduler)

    def add_task_item(self, item_widget):
        item = QListWidgetItem(self.task_list_widget)
        item.setSizeHint(item_widget.sizeHint())
        self.task_list_widget.addItem(item)
        self.task_list_widget.setItemWidget(item, item_widget)

    def delete_selected_tasks(self):
        # 获取选择的项
        selected_items = self.task_list_widget.selectedItems()
        for item in selected_items:
            row = self.task_list_widget.row(item)
            item_widget = self.task_list_widget.itemWidget(item)
            self.task_list_widget.takeItem(row)
            self.scheduler.delete_task_by_id(item_widget.id)

        print(self.scheduler)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowIcon(QIcon("./images/icon.png"))
    main_window.setWindowTitle("程序调度器")
    main_window.show()
    sys.exit(app.exec_())
