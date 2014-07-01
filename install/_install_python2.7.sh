#!/bin/bash

CURR_DIR=`pwd`
SRCDIR="$CURR_DIR/src"
BUILDDIR="$CURR_DIR/build"

# Create Source Directories
if [ ! -d "$SRCDIR" ]
then
	mkdir -pv $SRCDIR
fi

if [ ! -d "BUILDDIR" ]
then
	mkdir -pv $BUILDDIR
fi


pybuild_remove() {
	echo Removing all set ENV Vars
	unset PREFIX CFLAGS CPPFLAGS LDFLAGS LD_RUN_PATH C_INCLUDE_PATH
	unset CPLUS_INCLUDE_PATH
}

pybuild_add() {
	echo Adding default ENV Vars
	export PREFIX="/opt/python-2.7.6"
	export C_INCLUDE_PATH="$PREFIX/include"
	export CPLUS_INCLUDE_PATH=$C_INCLUDE_PATH
	export LIBRARY_PATH="$PREFIX/lib"
	export LD_RUN_PATH="$PREFIX/lib"
}

pybuild_add_prepython() {
	echo Adding pre Python build includes
	export C_INCLUDE_PATH="$PREFIX/include/ncurses:$PREFIX/include/readline:$PREFIX/include/openssl:$C_INCLUDE_PATH"
	export CPLUS_INCLUDE_PATH="$C_INCLUDE_PATH"
}

build_cleanup() {
	echo cleaning up $BUILDDIR
	cd $BUILDDIR
	rm -rf $BUILDDIR/*
}

dl_if_none() {
	# takes 2 parameters
	# $1 - filename
	# $2 - url
	echo Downloading source file
	if [ -e "$SRCDIR/$1" ]
	then
		echo Source file $1 already exists
	else
		wget $2 -O "$SRCDIR/$1"
	fi
}

pybuild_sqlite3() {
	dl_if_none sqlite-autoconf-3071000.tar.gz http://www.sqlite.org/sqlite-autoconf-3071000.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/sqlite*
	cd $BUILDDIR/sqlite*
	pybuild_add
	./configure --prefix=$PREFIX
	make
	make install
	pybuild_remove
	build_cleanup
}


pybuild_bzip2() {
	dl_if_none bzip2-1.0.6.tar.gz http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/bzip2*
	cd $BUILDDIR/bzip2*
	pybuild_add
	make -f Makefile-*
	make install PREFIX=$PREFIX
	make
	make install PREFIX=$PREFIX
	pybuild_remove
	build_cleanup
}


pybuild_zlib() {
	dl_if_none zlib-1.2.8.tar.gz http://zlib.net/zlib-1.2.8.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/zlib*
	cd $BUILDDIR/zlib*
	pybuild_add
	./configure --prefix=$PREFIX
	make
	make install
	pybuild_remove
	build_cleanup
}


pybuild_openssl() {
	dl_if_none openssl-1.0.0g.tar.gz http://www.openssl.org/source/openssl-1.0.0g.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/openssl*
	cd $BUILDDIR/openssl*
	pybuild_add
	./config --prefix=$PREFIX -I$PREFIX/include -L$PREFIX/lib threads shared --openssldir=$PREFIX/openssl zlib
	make
	make install
	pybuild_remove
	build_cleanup
}

pybuild_ncurses() {
	dl_if_none ncurses-5.9.tar.gz http://ftp.gnu.org/pub/gnu/ncurses/ncurses-5.9.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/ncurses*
	cd $BUILDDIR/ncurses*
	pybuild_add
	./configure --with-normal --with-shared --prefix=$PREFIX --enable-rpath --enable-sp-funcs --enable-const --enable--ext-mouse
	make
	make install
	pybuild_remove
	build_cleanup
}

pybuild_readline() {
	dl_if_none readline-6.2.tar.gz ftp://ftp.gnu.org/gnu/readline/readline-6.2.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/readline*
	cd $BUILDDIR/readline*
	pybuild_add
	./configure --prefix=$PREFIX 
	make
	make install
	pybuild_remove
	build_cleanup
}

pybuild_gdbm() {
	dl_if_none gdbm-1.10.tar.gz ftp://ftp.gnu.org/gnu/gdbm/gdbm-1.10.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/gdbm*
	cd $BUILDDIR/gdbm*
	pybuild_add
	./configure --prefix=$PREFIX 
	make
	make install
	pybuild_remove
	build_cleanup
}

pybuild_bsdbm() {
	dl_if_none db-4.3.29.tar.gz http://download.oracle.com/berkeley-db/db-4.3.29.tar.gz
	tar -C $BUILDDIR -zxf $SRCDIR/db*
	cd $BUILDDIR/db-*/build_unix
	pybuild_add
	../dist/configure --prefix=$PREFIX
	make
	make install
	pybuild_remove
	build_cleanup
}

pybuild_python() {
	dl_if_none Python-2.7.6.tar.bz2 http://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz
	tar -C $BUILDDIR -xzf $SRCDIR/Python*
	cd $BUILDDIR/Python*
	pybuild_add
	pybuild_add_prepython
	./configure --enable-shared --prefix=$PREFIX --enable-ipv6  --with-dbmlib
order=gdbm:bdb --with-threads
	make
	make install
	pybuild_remove
	build_cleanup
}

build_python27() {
	pybuild_remove
	# pybuild_sqlite3
	# pybuild_bzip2
	# pybuild_zlib
	# pybuild_openssl
	pybuild_ncurses
	pybuild_readline
	pybuild_gdbm
	pybuild_bsdbm
	pybuild_python
}

build_python27
