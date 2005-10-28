#!/bin/bash
#
# Build PySNMP MIB/managed objects from MIB text files
#

destDir=.
libsmi2pysnmp=/usr/local/bin/libsmi2pysnmp

[ ! -x $libsmi2pysnmp ] && {
  echo "$libsmi2pysnmp not found";
  exit
}

for origFile in [A-Z]*.py
do
  mibName=${origFile/.py/}
  mibPath=$(find /usr/local/share/mibs -name $mibName)
  [ -z $mibPath ] && {
      mibPath=$(find /usr/local/share/mibs -name $mibName.txt)
  }
  [ -z $mibPath ] && { echo "Missing MIB source for $origFile"; exit; }

  pyMibPath=$destDir/$mibName.py
  oldMib='no'
  egrep 'FROM *RFC' $mibPath > /dev/null && { oldMib='yes'; }
  [ $oldMib = 'yes' ] && { # pysnmp SMI is SMIv2
    myMibPath=/tmp/buildmibs.$$
    smidump -f smiv2 $mibPath > $myMibPath 2> /dev/null || {
      [ -f $myMibPath ] && rm -f $myMibPath;
      echo "smidump -f smiv2 $mibPath fails";
      exit ;
    }
    smidump -f python $myMibPath 2> /dev/null | $libsmi2pysnmp > $pyMibPath || {
      [ -f $myMibPath ] && rm -f $myMibPath;
      echo "smidump -f python $mibPath fails";
      exit
    }
    echo $mibPath $pyMibPath
    rm -f $myMibPath
  }
  [ $oldMib != 'yes' ] && {
    smidump -f python $mibPath 2> /dev/null | $libsmi2pysnmp > $pyMibPath || {
    echo "smidump -f python $mibPath fails";
    exit
    }
  }
  echo "$mibPath --> $pyMibPath"
done
