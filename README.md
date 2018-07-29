## 安装方法
```bash
pip install git+https://github.com/zeroleo12345/myclog-python.git

# Debug
pip install -e .
```

## vs2015编写拓展python模块步骤
[使用VS2010编写Python的C扩展](http://blog.csdn.net/catalyst_zx/article/details/47333909  )
```
"# 新建"
新建项目 -> win32 项目 -> DLL
删除stdafx.h
删除targetver.h
删除dllmain.cpp
删除stdafx.cpp
 
"# 配置"
切换活动项目 -> Release     (Debug依赖python27_d.lib, Release依赖python27.lib)
切换编译选项为 x64     (因为依赖安装的python27.lib, 若py是64位, 则选择64, 若86, 则选择86)
 
配置属性 -> 常规 -> 目标文件拓展名 -> .pyd
配置属性 -> 常规 -> 目标文件名 -> cmylog    原配置为: $(ProjectName)
配置属性 -> 生成事件 -> 后期生成事件 -> xcopy $(SolutionDir)$(Platform)\$(Configuration)\myclog.pyd $(SolutionDir)

配置属性 -> VC++目录 -> 包含目录:       E:\Python27\include
配置属性 -> VC++目录 -> 库目录:        E:\Python27\libs
 
链接器 -> 输入 -> 添加依赖项 -> python27.lib
或者:
#ifdef _DEBUG 
#pragma comment(lib, "python27_d.lib")
#else
#pragma comment(lib, "python27.lib")
#endif
```
