from skimage import io, transform
import tensorflow as tf
import numpy as np
import os  # os 处理文件和目录的模块
import glob  # glob 文件通配符模块

# 此程序作用于进行简单的预测，取5个图片来进行预测，如果有多数据预测，按照cnn.py中，读取数据的方式即可

# 测试的数据集路径
# path = 'C:\\Users\\Lin\\Desktop\\testdata\\'
path = './sheep/testdata/animal'

# 模型路径
modelpath ='./sheep/model/fc_model.ckpt-8.meta'

# checkpoint路径
checkpointpath = './sheep/model/'

# 类别代表字典
flower_dict = {0: 'sheep', 1: 'dog'}

w = 100
h = 100
c = 3


# 读取图片+数据处理
def read_img(path):
    # os.listdir(path) 返回path指定的文件夹包含的文件或文件夹的名字的列表
    # os.path.isdir(path)判断path是否是目录
    # b = [x+x for x in list1 if x+x<15 ]  列表生成式,循环list1，当if为真时，将x+x加入列表b
    cate = [path + x for x in os.listdir(path) if os.path.isdir(path + x)]
    imgs = []

    for idx, folder in enumerate(cate):
        # glob.glob(s+'*.py') 从目录通配符搜索中生成文件列表
        for im in glob.glob(folder + '/*.jpg'):
            # 输出读取的图片的名称
            print('reading the images:%s' % (im))
            # io.imread(im)读取单张RGB图片 skimage.io.imread(fname,as_grey=True)读取单张灰度图片
            # 读取的图片
            img = io.imread(im)
            # skimage.transform.resize(image, output_shape)改变图片的尺寸
            img = transform.resize(img, (w, h))
            # 将读取的图片数据加载到imgs[]列表中
            imgs.append(img)
            # 将图片的label加载到labels[]中，与上方的imgs索引对应
    # 将读取的图片和labels信息，转化为numpy结构的ndarr(N维数组对象（矩阵）)数据信息
    return np.asarray(imgs, np.float32)


# 调用读取图片的函数，得到图片和labels的数据集
data = read_img(path)
with tf.Session() as sess:
    saver = tf.train.import_meta_graph(modelpath)
    saver.restore(sess, tf.train.latest_checkpoint(checkpointpath))
    # sess：表示当前会话，之前保存的结果将被加载入这个会话
    # 设置每次预测的个数
    graph = tf.get_default_graph()

    x = graph.get_tensor_by_name("x:0")

    feed_dict = {x: data}

    logits = graph.get_tensor_by_name("logits_eval:0")  # eval功能等同于sess(run)

    classification_result = sess.run(logits, feed_dict)

    # 打印出预测矩阵
    print(classification_result)

    # 打印出预测矩阵每一行最大值的索引
    print(tf.argmax(classification_result, 1).eval())

    # 根据索引通过字典进行分类
    output = []
    output = tf.argmax(classification_result, 1).eval()
    # print(output)
    for i in range(len(output)):
        print("第", i + 1, "张图预测:" + flower_dict[output[i]])
