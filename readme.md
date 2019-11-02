# Stay point identification based on the correlation coefficient


## 前提：
快递员在妥投快递后，需要通过手持PDA确认妥投，PDA会上传当前坐标及妥投标识。

通过快递员手持PDA记录的GPS位置与时间，通过算法得到快递员在揽派过程中停留较久区域的位置。再根据快递订单信息，查询用户填写的下单地址与坐标。对比停留点与下单地址，可做以下几点应用：


  1. 判断快递员有没有虚假妥投。有的快递员会在统一妥投后再一并上传信息。通过停留点和确认妥投信息上传的比较可以判断快递员有没有按照规范上传。

  2. 此外，可根据挖掘出的停留点信息，结合对用户填写的下单地址进行文本识别、相似性判断，对下单地址的妥投点归类，节约快递员时间。

  3. 后续还可根据停留点位置挖掘更多有关地理位置或小区区域的有效信息。

## 实行步骤：

１. 提取２０１８－１１－１２日全国各地八个快递员全天的PDA上传数据。数据属性有快递员ｉｄ、日期与时间（精确到秒）、纬度、经度（经纬度坐标为WGS84格式）

２.	处理格式，删除多余内容，用制表符或者逗号分隔

３.	使用字典分ｉｄ保存快递员的信息，列表保存快递员点集，元组保存记录的单个点的时间与经纬度

４.	将2018-11-12 H:M:S　格式转换为时间戳，并将每个快递员中的点集按时间顺序排序保存

５.	计算当前时间戳与上一时间戳距离查得出，平均速度分布不均，存在大量噪点（下图为当日某快递员平均速度的时间序列）
![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p1.png 'p1')

于地图上绘制：

![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p2.png 'p2')

因此，无法使用当前数据分析停留点，因此需要数据清洗。

６. 清洗数据
   1. 对字典内每个快递员按时间戳排序的列表点集处理，如果当前点与时间戳前一点的距离超过时间阈值，则将这两点分开保存，否则将此两点放在同一个列表中保存。通过此方法，将一个时间戳排列的列表分割成多个按距离再次分割的列表集合。

2. 对分割后的列表集合进行处理，找到其中的噪音点。新建一个列表，将每一个分隔的子列表进行处理。将子列表中的第一个点放入新列表，随后遍历子列表。如果当前点与新列表中最后一个点的距离小于距离阈值及速度阈值，则判断该点不是噪点，将点放入新列表。如果是噪点，则遍历下一个点，舍弃此点。如果新列表总点数不超过点数阈值，则将此列表舍弃。最终将整合的多个新列表统一保存在一个总列表里，将总列表保存再字典中。默认时间阈值为６００秒，距离阈值２０００米，速度阈值为２０米／秒，点数阈值为５。

3. 对按时间阈值分开的新列表再次分隔，以时间与距离为单位。若当前点与上一点距离大于距离阈值，或时间大于时间阈值，则将分隔。距离阈值５００米，时间阈值２４００秒。

数据清洗后，绘制路线图，可看出多段有序沿道路行进的路径。

![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p3.png 'p3')

７.	数据清洗后，选择相关算法计算停留点。
阅读论文《基于相关系数的轨迹停留点识别算法》，发现场景较为合适。

比较传统的方法是根据轨迹停留点的距离和时间特征，基于距离和时间阈值的识别算法。在停留点研究中，轨迹点的速度属性也被分离出来。在很多文献中，会把速度较低的轨迹点称为静止点，把在静止点持续的时间作为识别停留点的一个重要依据。
轨迹停留点分析还有一个研究方向，就是基于密度的方法对轨迹停留点进行识别。这类动态方法建立在已有的经典聚类方法（ｋ－中值算法等）的基础上。

基于相关系数的轨迹停留点识别算法：通过计算轨迹中每一个点都可以根据相邻点的坐标计算出相关系数，相关系数的绝对值越小，在相邻点附近的行进方向变化则相对较大。
- 通过轨迹坐标依次计算轨迹点相关系数的绝对值；

- 对轨迹点进行过滤，如果轨迹点相关系数的绝对值小于闽值，则认定该点为关键点；

- 把这些关键点按照时间顺序依次排列形成关键点序列。

- 一般情况下，轨迹点中的点进行依次关键点过滤后只留下与相邻点相比方向变化较大的点，但是数量仍然较多，并且在转弯附近的点很可能被保留下来，影响停留点的进一步判断，所以有必要对关键点序列进行再次过滤。第二次过滤的过程中，我们以第一次识别的关键点序列为原轨迹序列，仍然根据相关点的相关系数进行过
滤，把生成的点按照时间顺序排列形成二次关键点序列。

![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p4.png 'p4')

可以看出途中有两种类型的点。浅蓝色为去除噪点后的路线轨迹点集合。深蓝色点为关键点。关键点即为方向变化较大的点，通过对关键点及周边点的处理可以得到停留点。
在计算过程中，ｘ与ｙ值分别是纬度与经度值。

８. 将相邻的关键点进行划分，如果距离超过阈值，则在这两个点处对关键点序列进行分割。

９.	停留点识别
1. 计算出该关键点区域的最小包围圆，阅读文献《离散点集最小包围圆算法分析与改进》，尝试相关算法。
2. 分别沿着关键点区域时间下限和上限方向寻找该圆内和附近的相关点，找出该关键点相关区域的轨迹时间上限和下限；
3. 提取出所识别时间下限和上限之间的点，形成关键点相关区域。


停留点的提取主要分为两个阶段：关键点区域划分、停留点识别。实验中根据对轨迹中轨迹数据的分析，相关系数（皮尔逊系数）阈值设置为０.５５，关键点划分阈值设为75米，停留点识别的轨迹长度与区域半径比值设为１，停留时间至少为120秒。下图为示例轨迹的识别结果。

![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p5.png 'p5')

（新添的红色点即为停留点）

# 实验统计

上周采用平均速度计算停留点的方法，停留点数量随阈值变化基本呈正比例关系
![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p6.png 'p6')

使用相关系数法计算停留区域，将多个点聚合与一个区域中。

 ![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p7.png 'p7')

当半径与距离总和比例高于2以后，无法计算出停留点区域。上图三条线分别为快递员在得到停留点后的逗留阈值，分别为30秒，60秒和120秒。

![X轴 时间戳 单位：秒，Y轴 平均速度 单位：米/秒](p8.png 'p8')

当相关系数阈值超过0.65后（即要求相关性较高时），得到的停留点陡升。
