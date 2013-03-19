NAME=$(shell cat samdolc.spec |grep Name |sed -n '1p' |awk '{print $$2}')
MAINVER=$(shell cat samdolc.spec |grep mainver |sed -n '1p' |awk '{print $$3}')
RELEASE=$(shell cat samdolc.spec |grep Release |sed -n '1p' |awk '{print $$2}')
RPM_NAME=${NAME}-${MAINVER}-${RELEASE}.noarch.rpm
TARBALL_NAME=${NAME}-${MAINVER}.tar.gz
BUILD_DIRR=$(shell pwd)/tmp
EXE_NAME=${NAME}_installer.exe

SYS := $(shell gcc -dumpmachine)
ifneq (, $(findstring linux, $(SYS)))
CHROME_CMD=chrome-cvs
else ifneq(, $(findstring mingw, $(SYS)))
NSIS_CMD="C:/Program Files (x86)/NSIS/makensis.exe"
CHROME_CMD="$(USERPROFILE)/Local Settings/Application Data/Google/Chrome/Application/chrome.exe"
else ifneq(, $(findstring cygwin, $(SYS)))
NSIS_CMD="C:/Program Files (x86)/NSIS/makensis.exe"
CHROME_CMD="$(USERPROFILE)/Local Settings/Application Data/Google/Chrome/Application/chrome.exe"
endif

CURRENT_PATH=$(shell pwd)


CHROME_PACKAGE=samdolc.crx
CHROME_EXTERNAL_JSON=onpobpkjhjihnhmjpjemcedjebllieoi.json
CHROME_EXTERNAL_PATH=~/myscript/tmp/chrome-linux/extensions

create-chrome-package:
	if [ -f ${CHROME_PACKAGE} ]; then rm ${CHROME_PACKAGE}; fi
	${CHROME_CMD} --pack-extension=${CURRENT_PATH}/chrome_extension --pack-extension-key=${CURRENT_PATH}/chrome_extension.pem
	mv chrome_extension.crx ${NAME}.crx

install-chrome-package:
	cp ${CHROME_EXTERNAL_JSON} ${CHROME_EXTERNAL_PATH}

remove-chrome-package:
	rm ${CHROME_EXTERNAL_PATH}/${CHROME_EXTERNAL_JSON}


prepare-exe: clean-tmp zip-exe
	if [ ! -d tmp/build_exe ]; then mkdir -p tmp/build_exe; fi
	tar zxvf ${TARBALL_NAME} -C tmp/build_exe

remove-build-exe:
	if [ -d tmp/build_exe ]; then rm -rf tmp/build_exe; fi

exe: prepare-exe
	${NSIS_CMD} ${NAME}.nsi
	mv ${NAME}.exe ${EXE_NAME}
	rm -rf tmp/build_exe

exe-py2exe: clean-tmp py2exe crx
	mkdir -p tmp/build_exe
	mv server/dist tmp/build_exe/server
	cp -r server/tools tmp/build_exe/server
	cp -r server/medias tmp/build_exe/server
	cp -r tools tmp/build_exe
	cp ${CHROME_PACKAGE} tmp/build_exe
	${NSIS_CMD} ${NAME}_py2exe.nsi
	rm -rf tmp/build_exe

crx: create-chrome-package

py2exe:
	$(MAKE) -C server py2exe

zip: crx
	tar cvzf ${TARBALL_NAME} -l `cat file_list`

zip-rpm: crx
	tar cvzf ${TARBALL_NAME} -l `cat file_list_on_rpm`

zip-exe: crx
	tar cvzf ${TARBALL_NAME} -l `cat file_list_on_windows`

rpm: build-rpm-pre
	rpmbuild -bb --sign --define="_buildshell /bin/bash" --define="_topdir ${BUILD_DIRR}" --define="_sourcedir `pwd`/" samdolc.spec
	mv ${BUILD_DIRR}/RPMS/noarch/${RPM_NAME} ./

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

test:
	${NSIS_CMD} ttt2.nsi
