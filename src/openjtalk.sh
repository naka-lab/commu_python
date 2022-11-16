OPENJTALK_DIR=/home/root/openjtalk
VOICE=$OPENJTALK_DIR/MMDAgent_Example-1.4/Voice/mei/mei_normal.htsvoice
DIC=$OPENJTALK_DIR/open_jtalk_dic_utf_8-1.08
echo $1 | open_jtalk \
-m  $VOICE \
-x  $DIC \
-ow $2