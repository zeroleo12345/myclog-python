#!/usr/bin/sh
if [[ "`uname -a`" =~ "Cygwin" || "`uname -a`" =~ "Msys" ]];then
    rm -rf build; python.exe setup.py install
else
    rm -rf build; python setup.py install
fi
find ./build -name "myclog*.pyd" | xargs -I{} -t sh -c "cp {} ~/code/mybase/myclog.pyd"
find ./build -name "myclog*.so" | xargs -I{} -t sh -c "cp {} ~/code/mybase/myclog.so"

# Python3版本编译:
# yum install python36-devel
# rm -rf build; python3.6 setup.py install
