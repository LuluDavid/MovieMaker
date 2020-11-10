#!/bin/sh
sudo docker system prune -a --volumes << EOF
y
EOF