# DeepTPI

## 如何准备训练数据
1. 将bench格式的电路（保证为AIG：只有AND、NOT）保存在raw_data文件夹下
2. 运行prepare_benchmarks_circuits.py 处理bench电路，生成npz文件，默认输出位置为./data/train

## 如何准备测试数据
1. 将bench格式的电路（支持AND、NOT、OR、NOR、NAND、XOR、XNOR、BUFF）保存在./dataset/circuit2aig/bench文件夹下
2. 进入 ./dataset/circuit2aig
3. 运行top.py，将电路转换为AIG，生成benchmarks_circuits_graphs.npz 文件
4. 将生成的benchmarks_circuits_graphs.npz 复制到../branch_to_buff/input_npz下
5. 进入../branch_to_buff
6. 运行main.py，在电路分支上插入BUFF，作为TP候选位置但不改变电路功能，生成的npz文件会出现在output_npz下
7. 将npz文件复制到DeepTPI根目录下的 ./data/test 文件夹下

## 关于Atalanta
已经集成修改过的atalanta工具，见：./src/external