#!/usr/bin/env bash
SVCFILE="/etc/systemd/system/alexacast.service"
cat > $SVCFILE << EOM
[Unit]
Description=Alexa YouTube Chromecast integration

[Service]
ExecStart=$PWD/alexa-chromecast-yt.py

[Install]
WantedBy=multi-user.target
EOM
chmod 664 "$SVCFILE" && \
systemctl enable alexacast.service
