NAME=$(shell cat samdolc.spec |grep Name |sed -n '1p' |gawk '{print $$2}')
MAINVER=$(shell cat samdolc.spec |grep mainver |sed -n '1p' |gawk '{print $$3}')
RELEASE=$(shell cat samdolc.spec |grep Release |sed -n '1p' |gawk '{print $$2}')
EXT_VER=0.1
EXT_RELEASE=1
TARBALL_NAME=${NAME}-${MAINVER}.tar.gz
BUILD_DIRR=$(shell pwd)/tmp
BUILD_DIRF=$(shell pwd)/build

RPM_NAME=${NAME}-${MAINVER}-${RELEASE}.noarch.rpm
EXE_NAME=${NAME}-${MAINVER}-${RELEASE}-installer.exe

#EXT_NAME=${NAME}-${EXT_VER}-${EXT_RELEASE}.crx
EXT_NAME=${NAME}.crx #More convenient to use the static name
EXT_EXTERNAL_JSON=onpobpkjhjihnhmjpjemcedjebllieoi.json
EXT_EXTERNAL_PATH=~/myscript/tmp/chrome-linux/extensions

NSI_PY2EXE_SAMPLE_NAME=samdolc_py2exe.nsi
NSI_PY2EXE_NAME=${NAME}-${MAINVER}.nsi

#Fixme: We need any method to get current_path on windows. chrome.exe
#doesn't understand posix directory
SYS := $(shell gcc -dumpmachine)
ifneq (, $(findstring linux, $(SYS)))
CHROME_CMD=chrome-cvs
CURRENT_PATH=$(shell pwd)
else ifneq(, $(findstring mingw, $(SYS)))
NSIS_CMD="$(PROGRAMFILES)/NSIS/makensis.exe"
CHROME_CMD="$(USERPROFILE)/Local Settings/Application Data/Google/Chrome/Application/chrome.exe"
CURRENT_PATH="c:\emacsd\cygwin\home\ptmono\works_xp\samdol"
else ifneq(, $(findstring cygwin, $(SYS)))
NSIS_CMD="$(PROGRAMFILES(x86))/NSIS/makensis.exe"
CHROME_CMD="$(USERPROFILE)/Local Settings/Application Data/Google/Chrome/Application/chrome.exe"
CURRENT_PATH="c:\emacsd\cygwin\home\ptmono\works_xp\samdol"
endif



create-chrome-package:
	if [ -f ${EXT_NAME} ]; then rm ${EXT_NAME}; fi
	${CHROME_CMD} --pack-extension=${CURRENT_PATH}/chrome_extension --pack-extension-key=${CURRENT_PATH}/chrome_extension.pem
	mv chrome_extension.crx ${BUILD_DIRF}/${EXT_NAME}

install-chrome-package:
	cp ${EXT_EXTERNAL_JSON} ${EXT_EXTERNAL_PATH}

remove-chrome-package:
	rm ${EXT_EXTERNAL_PATH}/${EXT_EXTERNAL_JSON}

prepare-exe-nsi:
	sed -e 's/__OUT_FILENAME/${EXE_NAME}/g' -e 's/__CRX_VERSION/${EXT_VER}-${EXT_RELEASE}/g' -e 's/__CRX_NAME/${EXT_NAME}'${NSI_PY2EXE_SAMPLE_NAME} > ${NSI_PY2EXE_NAME}


prepare-exe: clean-tmp zip-exe prepare-exe-nsi
	if [ ! -d tmp/build_exe ]; then mkdir -p tmp/build_exe; fi
	tar zxvf ${TARBALL_NAME} -C tmp/build_exe

remove-build-exe:
	if [ -d tmp/build_exe ]; then rm -rf tmp/build_exe; fi

exe: prepare-exe
	${NSIS_CMD} ${NAME}.nsi
	mv ${NAME}.exe ${BUILD_DIRF}/${EXE_NAME}
	rm -rf tmp/build_exe

exe-py2exe: clean-tmp py2exe crx
	mkdir -p tmp/build_exe
	mv server/dist tmp/build_exe/server
	cp -r server/tools tmp/build_exe/server
	cp -r server/medias tmp/build_exe/server
	cp -r tools tmp/build_exe
	cp ${EXT_NAME} tmp/build_exe
	${NSIS_CMD} ${NSI_PY2EXE_NAME}
	rm -rf tmp/build_exe
	rm ${NSI_PY2EXE_NAME}
	mv ${EXE_NAME} ${BUILD_DIRF}/${EXE_NAME}

crx: create-chrome-package

py2exe:
	$(MAKE) -C server py2exe

zip: crx
	tar cvzf ${TARBALL_NAME} -l `cat docs/file_list`

zip-rpm: crx
	tar cvzf ${TARBALL_NAME} -l `cat docs/file_list_on_rpm`

zip-exe: crx
	tar cvzf ${TARBALL_NAME} -l `cat docs/file_list_on_windows`

rpm: build-rpm-pre
	rpmbuild -bb --sign --define="_buildshell /bin/bash" --define="_topdir ${BUILD_DIRR}" --define="_sourcedir `pwd`/" samdolc.spec
	mv ${BUILD_DIRR}/RPMS/noarch/${RPM_NAME} ${BUILD_DIRF}

ddinstall: rpm
	sudo rpm -Uvh --force --nodeps ${RPM_NAME}

build-rpm-pre: zip-rpm
	mkdir -p ${BUILD_DIRR}/{BUILDROOT,BUILD,RPMS,SOURCES,SPECS,SRPMS}

clean: clean-all

clean-all: clean-build-dir clean-exe clean-crx clean-tmp

clean-build-dir:
	rm -rf ${BUILD_DIRR}/{BUILDROOT,BUILD,RPMS,SOURCES,SPECS,SRPMS}

clean-exe:
	if [ -f ${EXE_NAME} ]; then rm ${EXE_NAME}; fi

clean-crx:
	if [ -f ${NAME}.crx ]; then rm ${NAME}.crx; fi

clean-rpm:
	if [ -f ${NAME}.rpm ]; then rm ${NAME}.rpm; fi

clean-tmp:
	rm -rf tmp

clean-zip:
	if [ -f ${TARBALL_NAME} ]; then rm ${TARBALL_NAME}; fi

clean-py2exe:
	rm -rf dist

clean-virtualenv:
	rm -rf bin
	rm -rf build
	rm -rf include
	rm -rf lib
	rm lib64

test2:
	${NSIS_CMD} ttt2.nsi
