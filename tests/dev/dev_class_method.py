import inspect


def method_called():
    frame = inspect.currentframe().f_back
    # print(dir(frame))
    if "self" in frame.f_locals:
        self_obj = frame.f_locals["self"]
        print(type(self_obj).__name__)

    # _stack = inspect.stack(0)
    # print("cls:", _stack[0].f_locals["self"].__class__.__name__, "func:", _stack[3])


class CallingClass:
    def __init__(self):
        pass

    def calling_method(self):
        method_called()

    @staticmethod
    def calling_static():
        method_called()


# ############################################################################
# #### Stand alone program #######
# ################################

if __name__ == "__main__":
    clscall = CallingClass()

    # from method
    print("From class method")
    clscall.calling_method()

    # from static
    print("From class static method")
    clscall.calling_static()
