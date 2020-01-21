echo minediamonds | sudo -S su
cd minecraftdir
sudo screen -dmS screen_session_name bash -c "sudo java -Xmx1024M -Xms1024M -jar $1 nogui; exec bash"
