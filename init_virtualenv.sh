#!/bin/bash

if [ ! -f bin/activate ]; then
    virtualenv ./
fi
source bin/activate
pip install -r requirements.txt

LIBS=( PyQt4 sip.so lxml )

PYTHON_VERSION=python$(python -c "import sys; print (str(sys.version_info[0])+'.'+str(sys.version_info[1]))")
VAR=( $(which -a $PYTHON_VERSION) )

GET_PYTHON_LIB_CMD="from distutils.sysconfig import get_python_lib; print (get_python_lib())"
LIB_VIRTUALENV_PATH=$(python -c "$GET_PYTHON_LIB_CMD")
LIB_SYSTEM_PATH=$(${VAR[-1]} -c "$GET_PYTHON_LIB_CMD")

[ -f $LIB_SYSTEM_PATH/${LIBS[0]} ] || \
LIB_SYSTEM_PATH=${LIB_SYSTEM_PATH/lib/lib64}



for LIB in ${LIBS[@]}
do
    if [ ! -h $LIB_VIRTUALENV_PATH/$LIB ]; then
	ln -s $LIB_SYSTEM_PATH/$LIB $LIB_VIRTUALENV_PATH/$LIB
    fi
done
