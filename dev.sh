#!/bin/sh

ECHO="`which echo` -e"

[ x$1 = x ] && $ECHO "\
Small script for running developement tools. 

Usage: $0 <command>

Commands:

dev        Install developement envoronment
run	   Run the app in developement environment
pytest     Run pytest unittests
pylint     Do pylint
covhtml    Make branch coverage report with coverage in html format
covff      Genarate and open html coverage report in firefox
all        Do it all: pytest, coverage report in firefox and pylint
install    Build PyPI package form source and install it
" && exit 0

# Ensure ~/.local/bin in the PATH.
echo $PATH | grep /.local/bin > /dev/null \
	|| export PATH="$HOME/.local/bin:$PATH"

PIP=`which pipx`
[ x$PIP = x ] && PIP=`which pip`
[ x$PIP = x ] \
	&& $ECHO "This scripts uses pipx or pip to install poetry and the build." \
	&& exit 1
	
export DEVSH_PRIN=">>$DEVSH_PRIN"
export DEVSH_PROUT="<<$DEVSH_PROUT"

$ECHO "\033[32m$DEVSH_PRIN $0 $1 - started...\033[0m"

case $1 in

	install-poetry)
		[ -e $HOME/.local/bin/poetry ] \
		|| $PIP install poetry
		;;

	install-latest-build)
		$PIP install `ls dist/*.tar.gz -t -c -1 | head -1` \
		&& $ECHO "For uninstall please use '$PIP uninstall ...'"
		;;

	poetry-dev-deps)
		PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring \
		poetry install
		;;
	
	dev)
		$0 install-poetry \
		&& $0 poetry-dev-deps
		;;

	run)
		DEBUG=1 poetry run smplchat
		;;

	pytest)
		poetry run pytest -v
		;;

	pylint)
		poetry run pylint src/
		;;

	coverage)
		poetry run coverage run -m pytest -v
		;;

	covhtml)
		$0 coverage \
		&& poetry run coverage html
		;;

	covff)
		$0 covhtml \
		&& (firefox htmlcov/index.html || echo Cannot lauch browser.)
		;;

	all)	
		$0 covff \
		&& $0 pylint
		;;

	poetry-build)
		poetry build
		;;

	install)
		$0 install-poetry \
		&& $0 poetry-build \
		&& $0 install-latest-build
		;;

	*)	
		$ECHO "\033[31m$DEVSH_PROUT $0 $1 - unknown command.\033[0m"
		exit 1
		;;
esac

STATUS=$?

[ $STATUS != 0 ] \
	&& $ECHO "\033[31m$DEVSH_PROUT $0 $1 - exited with code $STATUS.\033[0m" \
	&& exit $STATUS
	
$ECHO "\033[32m$DEVSH_PROUT $0 $1 - done.\033[0m"
