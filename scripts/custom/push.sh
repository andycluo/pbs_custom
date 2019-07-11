#!/bin/bash
    
cdate=`date +"%Y%m%d%H%M%S"`
./build_fe.sh greentown $cdate greentown
ansible 
