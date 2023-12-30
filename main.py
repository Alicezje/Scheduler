import time


def test_func(args):
    print('子进程开始')
    print(args["lr"])
    print(args["batch_size"])

    for i in range(3):
        print('epoch: ', i)
        # 模拟训练过程
        time.sleep(1)

    print('子进程结束')
