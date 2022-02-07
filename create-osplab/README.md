############PYTHON SCRIPT RUN ON VIRTUAL ENV.##################


WHY WE NEED VIRTUAL ENVIORNMENT ?
virtualenv is used to manage Python packages for different projects. Using virtualenv allows you to avoid installing Python packages globally which could break system tools or other projects. You can install virtualenv using pip.


HOW TO MAKE VIRTUAL ENVIORNMENT AND RUN SCRIPT ON THIS ?
virtual env. wiil be make to as follow:-

apt install python3
python3 --version
apt install python3-pip
pip3 --version
apt install python3.8-venv
python3 -m venv myenv
source myenv/bin/activate
chmod +x demo.py
./demo.py


Note: If there is no DHCP server in the environment. The VM console login might take up to 2-5 minutes to appear for login. Adjust the timeout accordingly
