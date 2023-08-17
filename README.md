<p align="center">
  <a href="https://github.com/certainstar/little-Python-software/tree/%E7%89%88%E6%9C%AC%E6%9B%B4%E6%96%B0/%E7%9B%91%E5%90%AC%E8%84%9A%E6%9C%AC%E5%8F%AF%E6%89%A7%E8%A1%8C%E6%96%87%E4%BB%B6(.exe)">
    <img src="img/2.ico" width="200" height="200" alt="监听脚本">
  </a>
</p>

<div align="center">

# 监听脚本

_基于 [Mirai](https://github.com/mamoe/mirai) , [MiraiGo](https://github.com/Mrs4s/MiraiGo) 的 [OneBot](https://github.com/howmanybots/onebot/blob/master/README.md) Go语言(易语言)实现的框架,部分java代码实现的签名服务器_

_主要框架为[Mrs4s](https://github.com/Mrs4s/go-cqhttp/)大佬的go-cqhttp机器人框架_

_签名服务器为[fuqiuluo](https://github.com/fuqiuluo/unidbg-fetch-qsign)大佬的服务器部署_

_脚本程序为Python语言编写,可在仓库中找到[各个版本的Python源代码]()，可自取。**请在合法条件下使用或修改源程序！**若没有Python编译器，可去[Python官网](https://github.com/search?q=Python&type=repositories)下载，或直接使用已经编译好的[exe文件](https://github.com/certainstar/little-Python-software/tree/%E7%89%88%E6%9C%AC%E6%9B%B4%E6%96%B0/%E7%9B%91%E5%90%AC%E8%84%9A%E6%9C%AC%E5%8F%AF%E6%89%A7%E8%A1%8C%E6%96%87%E4%BB%B6(.exe))_

</div>

<p align="center">
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="img/license.jpg" width="65" height="10" alt="license:Apache License 2.0">
  </a>
  <a href="https://github.com/certainstar/little-Python-software/releases/tag/v1.2.1">
    <img src="img/release.jpg" width="65" height="10" alt="release:v1.2.1">
  </a>
</p>

<p align="center">
  <a href="https://github.com/certainstar/little-Python-software/releases/tag/v1.2.1">下载</a>
</p>

# 使用教程

## 前置配置

1. 对go-cqhttp进行配置
  - 可进入[Mrs4s](https://github.com/Mrs4s/go-cqhttp/)大佬的go-cqhttp项目库，自行配置，其中[教学文档](https://docs.go-cqhttp.org)有[引导部分](https://docs.go-cqhttp.org/guide/#go-cqhttp)，可供学习参考。
  - 若不会配置可跟随下方步骤进行配置：
    - [x] ①首先下载适合自己系统的最新的go-cqhttp.exe文件，_[最新下载地址](https://github.com/Mrs4s/go-cqhttp/releases)_，或者直接导入[本库中的go-cqhttp.exe文件](https://github.com/certainstar/little-Python-software/blob/%E7%89%88%E6%9C%AC%E6%9B%B4%E6%96%B0/go-cqhttp/go-cqhttp.exe)，_`注意：本库中的go-cqhttp为_amd64版本_`_
    - [x] ②下载后，点击go-cqhttp.exe后，会弹窗（如图配置go-cq步骤1），直接一路确认然后会在此目录下生成一个go-cqhttp.bat，点击bat文件。
      <p align="center">
        <img src="img/配置go-cq步骤1.png" alt="配置go-cq步骤1">
        <span>配置go-cq步骤1</span>
      </p>
      此时会生成一个如下图所示的弹窗，可以按照自身需求输入0~3
      <p align="center">
        <img src="img/配置go-cq步骤2.png" alt="配置go-cq步骤2">
        <span>配置go-cq步骤2</span>
      </p>
      ③
      ④
2. 对签名服务器进行配置
_为什么要用签名服务器？为减少风控，减少`code45`风控报错_
  
  - 可进入[fuqiuluo](https://github.com/fuqiuluo/unidbg-fetch-qsign)大佬的签名服务器项目，并进行部署。
  - 若不会配置可跟随下方步骤进行配置：
