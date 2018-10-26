## 准备环境

- CentOS
``` bash
yum install python36-devel
```


## Cygwin 版本编译:
``` bash
#!/usr/bin/sh
if [[ "`uname -a`" =~ "Cygwin" || "`uname -a`" =~ "Msys" ]];then
    rm -rf build; python.exe setup.py install
else
    rm -rf build; python setup.py install
fi
find ./build -name "myclog*.pyd" | xargs -I{} -t sh -c "cp {} ~/code/mybase/myclog.pyd"
find ./build -name "myclog*.so" | xargs -I{} -t sh -c "cp {} ~/code/mybase/myclog.so"
```


## Python 3 版本编译:
``` bash
rm -rf build; python3 setup.py install
```


## Python 2 版本编译:
``` bash
rm -rf build; python2 setup.py install
```
