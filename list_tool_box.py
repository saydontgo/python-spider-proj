def exist_in_list(item,your_list:list):
    """
    判断一个元素是否在list中
    :param your_list:
    :return: bool
    """
    for i in your_list:
        if i==item:
            return True
    return False

def list2set(your_list:list):
    """
    将list去重而不改变源list的元素顺序
    :param your_list:
    :return:
    """
    res=[]
    for i in your_list:
        if exist_in_list(i,res):continue
        res.append(i)
    return res